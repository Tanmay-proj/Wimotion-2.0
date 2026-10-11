# ==============================================================================
# WiMotion 2.0: RF_ESP32 Dataset Adapter
# Dataset Reference: Mohammed-Baqir/RF_ESP32_Dataset
# ==============================================================================
from typing import Dict, Any, Optional
import numpy as np


class RFESP32Adapter:
    """
    Adapter for RF_ESP32 Dataset (ESP32 CSI indoor radio propagation).
    Maps raw CSI records into standard WiMotion schema.
    """

    DATASET_ID = "RF_ESP32"
    CITATION = "Mohammed-Baqir/RF_ESP32_Dataset, GitHub"
    LICENSE = "Open Academic Research"
    SAMPLING_RATE_HZ = 50.0

    def parse_csi_line(self, line: str) -> Optional[Dict[str, Any]]:
        parts = [p.strip() for p in line.strip().split(",") if p.strip()]
        if len(parts) < 64:
            return None
        try:
            # Amplitudes across 64 subcarriers
            amps = [float(x) for x in parts[-64:]]
            rssi = float(parts[0]) if len(parts) > 64 else -55.0
            return {
                "amplitudes_64": amps,
                "rssi": rssi,
                "dataset_source": self.DATASET_ID,
                "sampling_rate_hz": self.SAMPLING_RATE_HZ,
                "presence_label": "human_present"
            }
        except Exception:
            return None
