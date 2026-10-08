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

        features.append({
            "receiver": rx,
            "tx": tx,
            "sample_count": len(x),
            "mean_amp": mean_val,
            "std_amp": std_val,
            "mean_delta": mean_delta,
            "rms_delta": rms_delta,
            "p95_delta": p95_delta,
            "energy": energy
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
        if feature is None:
            vector.extend([0.0] * 6)
            mask.append(0.0)
            continue

        active_links += 1
        mask.append(1.0)
        vector.extend([
            feature["mean_amp"],
            feature["std_amp"],
            feature["mean_delta"],
            feature["rms_delta"],
            feature["p95_delta"],
            feature["energy"]
        ])

    if include_validity_mask:
        vector.extend(mask)

    return np.asarray(vector, dtype=np.float32), active_links
