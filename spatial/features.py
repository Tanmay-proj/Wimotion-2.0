import numpy as np
from collections import defaultdict
from typing import List, Dict, Any, Tuple
from .types import CSIRecord

LINKS = [
    ("RX1", "TX1"),
    ("RX1", "TX2"),
    ("RX1", "TX3"),
    ("RX1", "TX4"),
    ("RX2", "TX1"),
    ("RX2", "TX2"),
    ("RX2", "TX3"),
    ("RX2", "TX4")
]


def clean_amplitudes(values):
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    x = x[(x >= 0) & (x < 10000)]
    return x


def extract_link_features(records: List[CSIRecord]) -> List[Dict[str, Any]]:
    groups = defaultdict(list)

    for record in records:
        if not record.tx_id:
            continue
        key = (record.receiver_id, record.tx_id)
        groups[key].append(record)

    features = []

    for (rx, tx), group in groups.items():
        amplitudes = []
        for record in group:
            a = clean_amplitudes(record.amplitudes)
            if len(a):
                amplitudes.append(float(np.mean(a)))

        if len(amplitudes) < 3:
            continue

        x = np.asarray(amplitudes, dtype=float)
        delta = np.diff(x)

        mean_val = float(np.mean(x))
        std_val = float(np.std(x))
        mean_delta = float(np.mean(np.abs(delta)))
        rms_delta = float(np.sqrt(np.mean(delta ** 2)))
        p95_delta = float(np.percentile(np.abs(delta), 95))
        energy = float(np.mean((x - mean_val) ** 2))

        # Multi-subcarrier temporal variance (WiMotion 2.0 Proximity Metric)
        matrix_rows = [clean_amplitudes(record.amplitudes)[:64] for record in group]
        valid_rows = [r for r in matrix_rows if len(r) == 64]
        if len(valid_rows) >= 3:
            matrix = np.asarray(valid_rows, dtype=float)
            sub_vars = np.var(matrix, axis=0)
            active_vars = sub_vars[sub_vars > 1e-4]
            csi_var = float(np.mean(active_vars)) if len(active_vars) > 0 else 0.0
        else:
            csi_var = 0.0

        rssi_vals = [record.rssi for record in group if record.rssi is not None]
        rssi_mean = float(np.mean(rssi_vals)) if rssi_vals else None

        features.append({
            "receiver": rx,
            "tx": tx,
            "sample_count": len(x),
            "mean_amp": mean_val,
            "std_amp": std_val,
            "mean_delta": mean_delta,
            "rms_delta": rms_delta,
            "p95_delta": p95_delta,
            "energy": energy,
            "csi_variance": csi_var,
            "rssi": rssi_mean
        })

    return features


def fuse_features(features: List[Dict[str, Any]], include_validity_mask: bool = True) -> Tuple[np.ndarray, int]:
    """
    Fuses 8 candidate links into a structured vector:
    - 48 continuous features (6 features per link)
    - 8 link-validity flags (1.0 = link active, 0.0 = link disconnected)
    Total dimensions: 56
    """
    lookup = {
        (f["receiver"], f["tx"]): f
        for f in features
    }

    vector = []
    mask = []
    active_links = 0

    for link in LINKS:
        feature = lookup.get(link)
        if feature is None or feature.get("sample_count", 1) <= 0:
            vector.extend([0.0] * 6)
            mask.append(0.0)
            continue

        active_links += 1
        mask.append(1.0)
        vector.extend([
            float(feature.get("mean_amp", 0.0)),
            float(feature.get("std_amp", 0.0)),
            float(feature.get("mean_delta", 0.0)),
            float(feature.get("rms_delta", 0.0)),
            float(feature.get("p95_delta", 0.0)),
            float(feature.get("energy", feature.get("csi_variance", 0.0)))
        ])

    if include_validity_mask:
        vector.extend(mask)

    return np.asarray(vector, dtype=np.float32), active_links


def extract_window_feature_vector(records: List[CSIRecord], include_validity_mask: bool = True) -> Tuple[np.ndarray, int, List[Dict[str, Any]]]:
    """
    Canonical single-source-of-truth function for multi-link feature extraction.
    Used identically in live inference, replay evaluation, and training pipelines to guarantee zero train-serving skew.
    
    Returns:
        (fused_56_dim_vector, active_link_count, raw_link_features)
    """
    features = extract_link_features(records)
    vector, active = fuse_features(features, include_validity_mask=include_validity_mask)
    return vector, active, features


FEATURE_SCHEMA_VERSION = "2.0.0-canonical-56dim"


def get_feature_names() -> List[str]:
    """Returns canonical names for all 56 feature dimensions in exact fused order."""
    names = []
    metric_names = ["mean_amp", "std_amp", "mean_delta", "rms_delta", "p95_delta", "energy"]
    for rx, tx in LINKS:
        for m in metric_names:
            names.append(f"{rx}_{tx}_{m}")
    for rx, tx in LINKS:
        names.append(f"valid_{rx}_{tx}")
    return names

