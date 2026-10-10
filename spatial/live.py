import time
import threading
from typing import Dict, Any, List, Optional
from pathlib import Path

from .types import CSIRecord, SpatialState
from .config import load_config, NodeConfig
from .window import MultiLinkWindow
from .features import extract_link_features, fuse_features
from .inference import SpatialBaseline
from .tracker import PersonTracker
from .serial_manager import MultiSerialManager


class LiveSpatialEngine:
    def __init__(self, config_path: str = "config/nodes.json"):
        self.config = load_config(config_path)
        self.window = MultiLinkWindow(
            seconds=self.config.sampling.window_seconds,
            step=self.config.sampling.step_seconds
        )
        self.model = SpatialBaseline()
        self.tracker = PersonTracker()
        self.serial_manager = MultiSerialManager(self.config, self._on_record)

        self.latest_state = {
            "timestamp": time.time(),
            "signal_ok": False,
            "count": 0,
            "people": [],
            "zone": "CLEAR",
            "active_links": 0,
            "link_count": 8,
            "confidence": 0.0,
            "reason": "INITIALIZING"
        }
        self.lock = threading.Lock()
        self.running = False
        self.last_record_receipt_time = 0.0

    def _on_record(self, record: CSIRecord):
        self.last_record_receipt_time = time.time()
        emitted_window = self.window.add(record)
        if emitted_window is not None:
            self._process_window(emitted_window)

    def _process_window(self, records: List[CSIRecord]):
        self.last_record_receipt_time = time.time()
        health = self.serial_manager.get_health()
        # Signal Quality Gate across active receivers (supports degraded single-receiver mode)
        all_rates = [
            h.get("aggregate_rate_hz", h.get("rate_hz", 0.0))
            for h in health.values()
            if h.get("running", False)
        ]
        signal_ok = len(all_rates) > 0 and any(r >= self.config.sampling.minimum_hz for r in all_rates)

        features = extract_link_features(records)
        vector, active = fuse_features(features)

        pred = self.model.predict(features, active, signal_ok)
        tracked = self.tracker.update(pred["people"])

        with self.lock:
            self.latest_state = {
                "timestamp": time.time(),
                "signal_ok": pred["signal_ok"],
                "count": pred["count"],
                "people": tracked,
                "zone": pred["zone"],
                "active_links": active,
                "link_count": 8,
                "confidence": None,  # Non-probabilistic; uncalibrated heuristic
                "reason": pred.get("reason", "OK"),
                "receiver_health": health
            }

    def start(self):
        self.running = True
        self.serial_manager.start_all()
        print("[+] LiveSpatialEngine started.")

    def stop(self):
        self.running = False
        self.serial_manager.stop_all()
        print("[*] LiveSpatialEngine stopped.")

    def get_state(self) -> Dict[str, Any]:
        with self.lock:
            st = dict(self.latest_state)
            now = time.time()
            time_since_pkt = now - self.last_record_receipt_time if self.last_record_receipt_time > 0 else 999.0

            health = st.get("receiver_health", {})
            active_rx = sum(1 for h in health.values() if h.get("running") and h.get("aggregate_rate_hz", 0) >= 1.0)

            if time_since_pkt > 3.0:
                st["hardware_connected"] = False
                st["signal_ok"] = False
                st["mode"] = "HARDWARE OFFLINE (NO RECENT PACKETS)"
                st["reason"] = "AWAITING_SERIAL_STREAM"
                st["count"] = 0
                st["zone"] = "CLEAR"
                st["people"] = []
            elif active_rx >= 2:
                st["hardware_connected"] = True
                st["mode"] = "LIVE HARDWARE (DUAL-RX 8-LINK)"
            elif active_rx == 1:
                st["hardware_connected"] = True
                st["mode"] = "LIVE HARDWARE (DEGRADED SINGLE-RX)"
            else:
                st["hardware_connected"] = False
                st["signal_ok"] = False
                st["mode"] = "HARDWARE STANDBY"

            return st
