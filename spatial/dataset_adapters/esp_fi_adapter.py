# ==============================================================================
# WiMotion 2.0: ESP-Fi-HAR Public Dataset Adapter
# Dataset Reference: AutoSmartGroup/ESP-Fi-HAR (ESP32 CSI 3-antenna / 52 subcarriers)
# Paper/Source: "ESP-Fi: Low-Cost and Ubiquitous Human Activity Recognition"
# ==============================================================================
from typing import Dict, Any, List, Optional
import numpy as np
from pathlib import Path


ESP_FI_ACTIVITY_MAP = {
    "0": "empty_room",
    "1": "walking",
    "2": "running",
    "3": "falling",
    "4": "sitting",
    "5": "standing"
}

ESP_FI_PRESENCE_MAP = {
    "0": "empty_room",
    "1": "human_present",
    "2": "human_present",
    "3": "human_present",
    "4": "human_present",
    "5": "human_present"
}


class ESPFiHARAdapter:
    """
    Adapter for the ESP-Fi-HAR benchmark dataset.
    Converts 52/56-subcarrier ESP32 CSI records into standard 64-subcarrier
    WiMotion representation with zero-padding on guard/DC carriers.
    """

    DATASET_ID = "ESP_FI_HAR"
    CITATION = "AutoSmartGroup/ESP-Fi-HAR, GitHub / IEEE IoT Journal"
    LICENSE = "MIT / Academic Research"
    SAMPLING_RATE_HZ = 100.0  # ESP-Fi original capture rate

    def __init__(self):
        self.subcarriers_in = 52
        self.subcarriers_out = 64

    def parse_csi_line(self, raw_line: str) -> Optional[Dict[str, Any]]:
        """Parses a comma-separated or space-separated ESP-Fi CSI string."""
        parts = [p.strip() for p in raw_line.strip().split(",") if p.strip()]
        if len(parts) < 52:
            parts = [p.strip() for p in raw_line.strip().split() if p.strip()]
        if len(parts) < 52:
            return None

        try:
            # First elements might be timestamp/label or directly CSI amplitudes
            # Robust heuristic: check if first element is float or int label
            if len(parts) > 52:
                label_code = parts[0]
                raw_amps = [float(x) for x in parts[1:53]]
            else:
                label_code = "1"
                raw_amps = [float(x) for x in parts[:52]]

            # Map 52 active carriers into 64 carriers (pad guard subcarriers 0..5 and 59..63, DC 32)
            padded_64 = np.zeros(64, dtype=float)
            active_indices = [i for i in range(6, 32)] + [i for i in range(33, 59)]
            for src_idx, dst_idx in enumerate(active_indices[:len(raw_amps)]):
                padded_64[dst_idx] = raw_amps[src_idx]

            return {
                "amplitudes_64": padded_64.tolist(),
                "activity_label": ESP_FI_ACTIVITY_MAP.get(label_code, "walking"),
                "presence_label": ESP_FI_PRESENCE_MAP.get(label_code, "human_present"),
                "dataset_source": self.DATASET_ID,
                "sampling_rate_hz": self.SAMPLING_RATE_HZ
            }
        except Exception:
            return None
