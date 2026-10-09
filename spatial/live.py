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

    def _on_record(self, record: CSIRecord):
        emitted_window = self.window.add(record)
        if emitted_window is not None:
            self._process_window(emitted_window)

    def _process_window(self, records: List[CSIRecord]):
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
            return dict(self.latest_state)
