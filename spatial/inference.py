import numpy as np
from typing import List, Dict, Any


class SpatialBaseline:
    def __init__(self):
        self.zones = [
            "Z1",
            "Z2",
            "Z3",
            "Z4"
        ]
        self.tx_zone_map = {
            "TX1": "Z1",
            "TX2": "Z2",
            "TX3": "Z3",
            "TX4": "Z4"
        }

    def predict(
        self,
        features: List[Dict[str, Any]],
        active_links: int,
        signal_ok: bool
    ) -> Dict[str, Any]:

        if not signal_ok:
            return {
                "signal_ok": False,
                "count": 0,
                "zone": "UNKNOWN",
                "people": [],
                "active_links": active_links,
                "reason": "SIGNAL_UNSTABLE"
            }

        if active_links == 0:
            return {
                "signal_ok": False,
                "count": 0,
                "zone": "UNKNOWN",
                "people": [],
                "active_links": 0,
                "reason": "NO_VALID_LINKS"
            }

        # ----------------------------------------------------
        # Multi-Link Sector Perturbation Detection (Wi-CaL)
        # ----------------------------------------------------
        # Identify which transmitters have active link perturbation
        # Threshold: mean_delta > 0.75 or energy > 0.5 indicates human motion across that link
        active_tx_scores = {}
        for f in features:
            tx = f.get("tx")
            score = f.get("mean_delta", 0.0)
            if tx:
                active_tx_scores[tx] = max(active_tx_scores.get(tx, 0.0), score)

        # Count how many distinct spatial zones exceed perturbation threshold
        active_zones = []
        for tx, score in active_tx_scores.items():
            if score >= 0.75:
                zone_name = self.tx_zone_map.get(tx, "Z1")
                if zone_name not in active_zones:
                    active_zones.append(zone_name)

        count = len(active_zones)
        primary_zone = active_zones[0] if active_zones else "CLEAR"

        people = [
            {
                "id": i + 1,
                "zone": zone
            }
            for i, zone in enumerate(active_zones)
        ]

        return {
            "signal_ok": True,
            "count": count,
            "zone": primary_zone,
            "people": people,
            "active_links": active_links,
            "reason": "BASELINE_OK"
        }
