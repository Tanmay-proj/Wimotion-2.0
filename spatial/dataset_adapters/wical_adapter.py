# ==============================================================================
# WiMotion 2.0: WiCAL Multi-AP Spatial Localization Dataset Adapter
# Dataset Reference: fuhaiwang/WiCAL (Multi-AP CSI for Calibration & Localization)
# ==============================================================================
from typing import Dict, Any, Optional
import numpy as np


class WiCALAdapter:
    """
    Adapter for WiCAL Localization Dataset.
    Focuses on multi-link calibration coordinates and spatial subcarrier features.
    """

    DATASET_ID = "WICAL"
    CITATION = "fuhaiwang/WiCAL: WiFi CSI Calibration & Localization"
    LICENSE = "Academic Research License"

    def __init__(self):
        self.subcarriers = 64

    def parse_record(self, raw_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Parses a structured dictionary from WiCAL raw JSON/HDF5/CSV."""
        return {
            "ap_id": raw_dict.get("ap_id", "AP1"),
            "location_x": float(raw_dict.get("x", 0.0)),
            "location_y": float(raw_dict.get("y", 0.0)),
            "subcarrier_amplitudes": raw_dict.get("amplitudes", [0.0] * 64),
            "dataset_source": self.DATASET_ID,
            "status": "CALIBRATION_FRAME"
        }
