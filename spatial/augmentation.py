# ==============================================================================
# WiMotion 2.0: Controlled Synthetic CSI Data Augmentation Utility
# Physics-informed transformations for training robustness:
#   - Bounded Gaussian noise on active OFDM carriers
#   - Subtle physical RF gain fluctuation (+-3% to +-5%)
#   - Strict parent session provenance tracking (source_type: synthetic_augmented)
# ==============================================================================
from typing import Dict, Any, List, Optional
import numpy as np
from pathlib import Path


GUARD_SUBCARRIERS = [0, 1, 2, 3, 4, 5, 59, 60, 61, 62, 63]
DC_SUBCARRIER = [32]
ACTIVE_SUBCARRIERS = [i for i in range(64) if i not in (GUARD_SUBCARRIERS + DC_SUBCARRIER)]


def augment_csi_frame(
    amplitudes: List[float],
    gain_scale: float = 1.0,
    noise_std: float = 0.03,
    rng: Optional[np.random.RandomState] = None
) -> List[float]:
    """Applies physics-informed augmentation to a single 64-subcarrier CSI frame."""
    if rng is None:
        rng = np.random.RandomState(42)

    arr = np.array(amplitudes, dtype=float)
    # Apply gain fluctuation
    arr = arr * gain_scale

    # Add Gaussian perturbation to active carriers only
    noise = rng.normal(0.0, noise_std, size=arr.shape)
    arr[ACTIVE_SUBCARRIERS] += noise[ACTIVE_SUBCARRIERS]

    # Mask guard and DC carriers to 0.0
    inactive = [i for i in range(64) if i not in ACTIVE_SUBCARRIERS]
    arr[inactive] = 0.0

    return np.maximum(arr, 0.0).tolist()


def create_augmented_session(
    input_csv_path: Path,
    output_dir: Path,
    parent_session_id: str,
    output_session_id: str,
    display_name: str,
    gain_variation: float = 0.04,
    noise_std: float = 0.03,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Reads an existing genuine hardware recording CSV, applies controlled augmentation,
    and writes out a new session with complete metadata documenting exact parent provenance.
    """
    import csv
    import json

    output_dir.mkdir(parents=True, exist_ok=True)
    out_csv = output_dir / f"{output_session_id}.csv"
    out_meta = output_dir / "metadata.json"

    rng = np.random.RandomState(seed)

    rows_written = 0
    duration = 0.0
    first_ts = None
    last_ts = None

    with open(input_csv_path, "r", encoding="utf-8") as fin, open(out_csv, "w", newline="", encoding="utf-8") as fout:
        reader = csv.reader(fin)
        writer = csv.writer(fout)
        header = next(reader, None)
        if not header:
            raise ValueError(f"Input file {input_csv_path} is empty.")
        writer.writerow(header)

        for row in reader:
            if len(row) < 74:
                continue
            ts = float(row[0])
            if first_ts is None:
                first_ts = ts
            last_ts = ts

            # Perturb gain within bounds
            gain = 1.0 + rng.uniform(-gain_variation, gain_variation)
            raw_amps = [float(x) for x in row[10:74]]
            aug_amps = augment_csi_frame(raw_amps, gain_scale=gain, noise_std=noise_std, rng=rng)

            # Reconstruct row
            aug_row = row[:10] + [f"{a:.2f}" for a in aug_amps]
            writer.writerow(aug_row)
            rows_written += 1

    if first_ts is not None and last_ts is not None:
        duration = round(max(0.1, last_ts - first_ts), 2)

    metadata = {
        "session_id": output_session_id,
        "display_name": display_name,
        "source_type": "synthetic_augmented",
        "provenance": "synthetic_augmented",
        "parent_session_id": parent_session_id,
        "augmentation_parameters": {
            "gain_variation": gain_variation,
            "noise_std": noise_std,
            "seed": seed,
            "method": "bounded_rf_gain_and_gaussian_multipath"
        },
        "total_records": rows_written,
        "duration_seconds": duration,
        "description": f"Controlled synthetic augmentation derived from genuine parent session '{parent_session_id}'. Used for training diversity only; never counted as real hardware data.",
        "created_at": "2026-10-11 07:00:00"
    }

    out_meta.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata
