# ==============================================================================
# WiMotion 2.0: Original WiMotion Model Adapter (v2.4 Contract)
# Preserves exact 217-feature temporal-spectral feature pipeline for
# HistGradientBoosting / ExtraTrees presence detection over multi-link windows.
# ==============================================================================
import os
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

ROOT = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------------------
# Feature Pipeline Configuration (Exact Match with Original WiMotion v2.4)
# ------------------------------------------------------------------------------
NUM_SUBCARRIERS = 64
GUARD_SUBCARRIERS = [0, 1, 2, 3, 4, 5, 59, 60, 61, 62, 63]
DC_SUBCARRIER = [32]
ACTIVE_SUBCARRIERS = [i for i in range(NUM_SUBCARRIERS) if i not in (GUARD_SUBCARRIERS + DC_SUBCARRIER)]
SMOOTHING_WINDOW = 3
TARGET_RESAMPLE_FS = 20.0
NOMINAL_SAMPLING_RATE_HZ = 20.0
MOTION_FREQ_BINS = 12
EXPECTED_FEATURE_COUNT = 217


def resample_to_uniform_grid(
    window_arr: np.ndarray,
    timestamps: Optional[np.ndarray] = None,
    target_fs: float = TARGET_RESAMPLE_FS
) -> np.ndarray:
    """Interpolates irregular arrival time series onto an exact uniform temporal grid."""
    n_frames = window_arr.shape[0]
    if timestamps is None or len(timestamps) != n_frames or len(timestamps) < 3:
        return window_arr

    ts = np.asarray(timestamps, dtype=float)
    t_start, t_end = ts[0], ts[-1]
    duration = t_end - t_start

    if duration < 0.2:
        return window_arr

    n_target = max(10, int(round(duration * target_fs)))
    t_uniform = np.linspace(t_start, t_end, n_target)

    try:
        f_interp = interp1d(ts, window_arr, axis=0, kind="linear", fill_value="extrapolate")
        return f_interp(t_uniform)
    except Exception:
        return window_arr


def smooth_window(arr: np.ndarray) -> np.ndarray:
    """Causal temporal moving-average smoothing across CSI frames using pure NumPy."""
    n = len(arr)
    if n <= 1:
        return arr.copy()
    if n == 2:
        out = np.empty_like(arr)
        out[0] = arr[0]
        out[1] = (arr[0] + arr[1]) / 2.0
        return out
    cs = np.cumsum(arr, axis=0)
    out = np.empty_like(arr)
    out[0] = arr[0]
    out[1] = (arr[0] + arr[1]) / 2.0
    out[2:] = (cs[2:] - np.vstack([np.zeros((1, arr.shape[1])), cs[:-3]])) / 3.0
    return out


def compute_temporal_motion_power_spectrum(normalized_arr: np.ndarray) -> np.ndarray:
    """Computes normalized Doppler / multipath motion power spectrum across active subcarriers."""
    n_frames = normalized_arr.shape[0]
    active_arr = normalized_arr[:, ACTIVE_SUBCARRIERS]
    arr_detrended = active_arr - active_arr.mean(axis=0, keepdims=True)
    hanning = np.hanning(n_frames).reshape(-1, 1)
    windowed = arr_detrended * hanning

    fft_result = np.fft.rfft(windowed, axis=0)
    power_spectrum = np.abs(fft_result) ** 2
    motion_power_full = power_spectrum.sum(axis=1)

    n_keep = min(MOTION_FREQ_BINS, max(1, (n_frames // 2)))
    motion_power_spectrum = motion_power_full[1:1 + n_keep]

    if len(motion_power_spectrum) < MOTION_FREQ_BINS:
        motion_power_spectrum = np.pad(motion_power_spectrum, (0, MOTION_FREQ_BINS - len(motion_power_spectrum)))

    return motion_power_spectrum


def compute_cross_subcarrier_coherence(normalized_arr: np.ndarray) -> np.ndarray:
    """SVD Spatial Subcarrier Coherence Analysis on active OFDM carriers."""
    active_norm = normalized_arr[:, ACTIVE_SUBCARRIERS]
    try:
        _, s, _ = np.linalg.svd(active_norm - active_norm.mean(axis=0, keepdims=True), full_matrices=False)
        s_var = s ** 2
        total_s_var = float(np.sum(s_var))
        if total_s_var > 1e-6:
            pc1_ratio = float(s_var[0] / total_s_var)
            pc2_ratio = float(s_var[1] / total_s_var) if len(s) > 1 else 0.0
            p = (s_var / total_s_var) + 1e-12
            spatial_entropy = float(-np.sum(p * np.log(p)))
        else:
            pc1_ratio, pc2_ratio, spatial_entropy = 0.0, 0.0, 0.0
    except Exception:
        pc1_ratio, pc2_ratio, spatial_entropy = 0.0, 0.0, 0.0

    return np.array([pc1_ratio, pc2_ratio, spatial_entropy])


def extract_v1_features(
    window_arr: np.ndarray,
    timestamps: Optional[np.ndarray] = None,
    fs: float = NOMINAL_SAMPLING_RATE_HZ,
    target_fs: float = TARGET_RESAMPLE_FS
) -> np.ndarray:
    """
    Extracts the authoritative 217-element baseline-invariant feature vector
    from a window of 64 subcarriers amplitudes.
    """
    inactive = [i for i in range(NUM_SUBCARRIERS) if i not in ACTIVE_SUBCARRIERS]

    if timestamps is not None and len(timestamps) == len(window_arr):
        arr_grid = resample_to_uniform_grid(window_arr, timestamps, target_fs=target_fs)
        effective_fs = target_fs
    else:
        arr_grid = window_arr
        effective_fs = fs

    arr_grid = np.maximum(arr_grid, 0.0)
    arr_grid[:, inactive] = 0.0
    arr = smooth_window(arr_grid)
    n_frames = arr.shape[0]

    baseline = np.median(arr, axis=0, keepdims=True)
    baseline[:, inactive] = 0.0
    scale = np.maximum(np.median(np.abs(arr), axis=0, keepdims=True), 1.0)

    normalized = (arr - baseline) / scale
    normalized[:, inactive] = 0.0

    temporal_std = normalized.std(axis=0)
    temporal_range = np.ptp(normalized, axis=0)
    temporal_diff = np.abs(np.diff(normalized, axis=0)).mean(axis=0) if n_frames > 1 else np.zeros(NUM_SUBCARRIERS)

    # Active carriers for global stats
    active_norm = normalized[:, ACTIVE_SUBCARRIERS]
    global_mean_std = float(active_norm.std(axis=0).mean())
    global_max_std = float(active_norm.std(axis=0).max())
    global_std_of_std = float(active_norm.std(axis=0).std())
    global_mean_range = float(np.ptp(active_norm, axis=0).mean())
    global_max_range = float(np.ptp(active_norm, axis=0).max())
    global_total_energy = float((active_norm ** 2).mean())

    global_features = np.array([
        global_mean_std, global_max_std, global_std_of_std,
        global_mean_range, global_max_range, global_total_energy
    ])

    motion_power_spectrum = compute_temporal_motion_power_spectrum(normalized)
    peak_bin_idx = int(np.argmax(motion_power_spectrum)) + 1

    freqs_hz = np.arange(1, len(motion_power_spectrum) + 1) * effective_fs / max(1, n_frames)
    peak_frequency_hz = (peak_bin_idx * effective_fs) / max(1, n_frames)
    total_motion_power = float(motion_power_spectrum.sum())

    if total_motion_power > 1e-6:
        motion_centroid_hz = float((freqs_hz * motion_power_spectrum).sum() / total_motion_power)
        diff_sq = (freqs_hz - motion_centroid_hz) ** 2
        motion_spread_hz = float(np.sqrt((diff_sq * motion_power_spectrum).sum() / total_motion_power))
    else:
        motion_centroid_hz = 0.0
        motion_spread_hz = 0.0

    motion_summary = np.array([
        peak_frequency_hz, total_motion_power, motion_centroid_hz, motion_spread_hz
    ])

    coherence_features = compute_cross_subcarrier_coherence(normalized)

    feature_vector = np.concatenate([
        temporal_std, temporal_range, temporal_diff,
        global_features,
        motion_power_spectrum, motion_summary,
        coherence_features
    ])

    return np.nan_to_num(feature_vector, nan=0.0, posinf=0.0, neginf=0.0)


class CompatUnpickler(pickle.Unpickler):
    """
    Robust unpickler supporting cross-NumPy version unpickling (NumPy 1.x <-> 2.x).
    Resolves numpy._core.multiarray <-> numpy.core.multiarray transparently.
    """
    def find_class(self, module, name):
        if module.startswith("numpy._core"):
            try:
                return super().find_class(module, name)
            except ModuleNotFoundError:
                alt_module = module.replace("numpy._core", "numpy.core")
                return super().find_class(alt_module, name)
        elif module.startswith("numpy.core"):
            try:
                return super().find_class(module, name)
            except ModuleNotFoundError:
                alt_module = module.replace("numpy.core", "numpy._core")
                return super().find_class(alt_module, name)
        return super().find_class(module, name)


# ------------------------------------------------------------------------------
# V1 Model Adapter Class
# ------------------------------------------------------------------------------
class V1PresenceModelAdapter:
    """
    Adapter that loads and executes original WiMotion presence models (v2.4)
    over multi-link window captures by grouping per receiver-transmitter link.
    """

    def __init__(self, model_filename: str = "presence_model.pkl"):
        self.model = None
        self.classes = []
        self.feature_count = EXPECTED_FEATURE_COUNT
        self.metadata = {}
        self.loaded = False
        self.load_error = None

        candidate_paths = [
            ROOT / "models" / model_filename,
            ROOT.parent / "wimotion" / "models" / model_filename,
            Path("models") / model_filename
        ]

        for p in candidate_paths:
            if p.exists():
                try:
                    with open(p, "rb") as f:
                        data = CompatUnpickler(f).load()
                    if isinstance(data, dict):
                        self.model = data.get("model")
                        self.classes = [str(c) for c in data.get("classes", [])]
                        self.metadata = data
                    else:
                        self.model = data
                        self.classes = ["empty_room", "human_present"]
                    self.loaded = True
                    break
                except Exception as e:
                    self.load_error = f"{type(e).__name__}: {str(e)}"

        if not self.loaded and not self.load_error:
            self.load_error = f"Model file '{model_filename}' not found in candidate paths."

    def is_available(self) -> bool:
        return self.loaded and self.model is not None

    def predict_link_stream(
        self,
        amplitudes_matrix: np.ndarray,
        timestamps: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Runs the exact 217-feature extraction and model inference for a single link.
        """
        if not self.is_available():
            return {
                "available": False,
                "error": self.load_error,
                "prediction": "UNKNOWN",
                "presence_probability": 0.0
            }

        if len(amplitudes_matrix) < 5:
            return {
                "available": True,
                "prediction": "INSUFFICIENT_FRAMES",
                "presence_probability": 0.0,
                "frame_count": len(amplitudes_matrix)
            }

        feats = extract_v1_features(amplitudes_matrix, timestamps=timestamps)
        feats_2d = feats.reshape(1, -1)

        try:
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(feats_2d)[0]
                if "human_present" in self.classes:
                    idx = self.classes.index("human_present")
                    p_present = float(probs[idx])
                else:
                    p_present = float(probs[-1])
                pred_class = self.classes[int(np.argmax(probs))] if (hasattr(self, "classes") and self.classes) else ("human_present" if p_present >= 0.5 else "empty_room")
            else:
                pred_class = self.model.predict(feats_2d)[0]
                p_present = 1.0 if pred_class == "human_present" else 0.0

            return {
                "available": True,
                "prediction": str(pred_class),
                "presence_probability": round(p_present, 4),
                "frame_count": len(amplitudes_matrix)
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "prediction": "INFERENCE_ERROR",
                "presence_probability": 0.0
            }

    def evaluate_multilink_window(self, window_records: List[Any]) -> Dict[str, Any]:
        """
        Groups multi-link CSI records by (receiver, tx), runs v1 feature extraction
        and inference per link, and computes aggregated presence telemetry.
        """
        if not self.is_available():
            return {
                "model_available": False,
                "error": self.load_error,
                "global_presence": "UNKNOWN",
                "confidence": None,
                "per_link_results": {}
            }

        records_by_link = {}
        for rec in window_records:
            rx = getattr(rec, "receiver_id", "RX1")
            tx = getattr(rec, "tx_id", "TX1")
            key = f"{rx}-{tx}"
            if key not in records_by_link:
                records_by_link[key] = []
            records_by_link[key].append(rec)

        per_link_results = {}
        presence_probs = []

        for link_key, recs in records_by_link.items():
            if len(recs) < 5:
                per_link_results[link_key] = {
                    "status": "INSUFFICIENT_DATA",
                    "frame_count": len(recs),
                    "presence_probability": 0.0
                }
                continue

            amps = np.array([r.amplitudes for r in recs], dtype=float)
            ts = np.array([r.timestamp for r in recs], dtype=float)
            res = self.predict_link_stream(amps, ts)
            per_link_results[link_key] = res
            if res.get("available") and res.get("prediction") != "INSUFFICIENT_FRAMES":
                presence_probs.append(res.get("presence_probability", 0.0))

        if presence_probs:
            max_p = float(np.max(presence_probs))
            mean_p = float(np.mean(presence_probs))
            is_present = max_p >= 0.50
            global_presence = "human_present" if is_present else "empty_room"
            confidence = round(max_p, 4)
        else:
            global_presence = "insufficient_data"
            confidence = None

        return {
            "model_available": True,
            "global_presence": global_presence,
            "confidence": confidence,
            "active_links_evaluated": len(presence_probs),
            "per_link_results": per_link_results
        }


_V1_SINGLETON: Optional[V1PresenceModelAdapter] = None


def get_v1_adapter() -> V1PresenceModelAdapter:
    """Returns a process-wide singleton instance of the V1PresenceModelAdapter to avoid re-pickling."""
    global _V1_SINGLETON
    if _V1_SINGLETON is None:
        _V1_SINGLETON = V1PresenceModelAdapter()
    return _V1_SINGLETON
