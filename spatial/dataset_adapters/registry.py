# ==============================================================================
# WiMotion 2.0: Public Dataset Registry & Provenance Manager
# Tracks licenses, citations, and supported dataset adapters.
# ==============================================================================
from typing import Dict, Any, List
from .esp_fi_adapter import ESPFiHARAdapter
from .rf_esp32_adapter import RFESP32Adapter
from .wical_adapter import WiCALAdapter


DATASET_REGISTRY = {
    "ESP_FI_HAR": {
        "name": "ESP-Fi HAR (AutoSmartGroup)",
        "url": "https://github.com/AutoSmartGroup/ESP-Fi-HAR",
        "license": "Academic / MIT",
        "hardware": "ESP32 CSI HT20 (Single-Link & 3-Antenna)",
        "adapter_class": ESPFiHARAdapter,
        "supported_tasks": ["Activity Recognition", "Binary Presence Gating"]
    },
    "RF_ESP32": {
        "name": "RF_ESP32 Indoor Propagation Dataset",
        "url": "https://github.com/Mohammed-Baqir/RF_ESP32_Dataset",
        "license": "Open Academic Research",
        "hardware": "ESP32 802.11n CSI",
        "adapter_class": RFESP32Adapter,
        "supported_tasks": ["Indoor RF Propagation", "Presence Detection"]
    },
    "WICAL": {
        "name": "WiCAL WiFi CSI Calibration & Localization",
        "url": "https://github.com/fuhaiwang/WiCAL",
        "license": "Academic Research",
        "hardware": "Multi-AP Distributed WiFi CSI",
        "adapter_class": WiCALAdapter,
        "supported_tasks": ["Spatial Sector Localization", "Calibration"]
    }
}


def get_adapter(dataset_id: str):
    info = DATASET_REGISTRY.get(dataset_id.upper())
    if not info:
        return None
    cls = info["adapter_class"]
    return cls()


def list_registered_datasets() -> List[Dict[str, Any]]:
    return [
        {
            "id": k,
            "name": v["name"],
            "url": v["url"],
            "license": v["license"],
            "hardware": v["hardware"],
            "tasks": v["supported_tasks"]
        }
        for k, v in DATASET_REGISTRY.items()
    ]
