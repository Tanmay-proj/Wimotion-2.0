import numpy as np
from typing import List, Dict, Any


class SpatialBaseline:
    def __init__(self, variance_threshold: float = 8.0):
        self.zones = [
            "Z1",  # NE Quadrant (TX1)
            "Z2",  # NW Quadrant (TX2)
            "Z3",  # SW Quadrant (TX3)
            "Z4"   # SE Quadrant (TX4)
        ]
        self.tx_zone_map = {
            "TX1": "Z1",
            "TX2": "Z2",
            "TX3": "Z3",
            "TX4": "Z4"
        }
        self.variance_threshold = variance_threshold

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
                "active_zone_count": 0,
                "zone": "UNKNOWN",
                "inference_status": "SIGNAL_UNSTABLE",
                "people": [],
                "active_links": active_links,
                "confidence": None,
                "reason": "SIGNAL_UNSTABLE"
            }

        if active_links == 0:
            return {
                "signal_ok": False,
                "count": 0,
                "active_zone_count": 0,
                "zone": "UNKNOWN",
                "inference_status": "NO_VALID_LINKS",
                "people": [],
                "active_links": 0,
                "confidence": None,
                "reason": "NO_VALID_LINKS"
            }

        # ----------------------------------------------------
        # Multi-Link Sector Perturbation Detection (Wi-CaL)
        # Aggregates subcarrier temporal variance across links for each TX
        # ----------------------------------------------------
        tx_scores = {}
        for f in features:
            tx = f.get("tx")
            if not tx:
                continue
            # Primary metric: csi_variance; fallback to delta-energy if synthetic
            var_score = f.get("csi_variance", 0.0)
            alt_score = f.get("mean_delta", 0.0) * 4.0 if var_score == 0.0 else 0.0
            score = max(var_score, alt_score)
            tx_scores[tx] = tx_scores.get(tx, 0.0) + score

        # Separate mapped transmitters from unmapped/rogue transmitters
        mapped_tx = [(tx, score) for tx, score in tx_scores.items() if tx in self.tx_zone_map]
        unmapped_tx = [(tx, score) for tx, score in tx_scores.items() if tx not in self.tx_zone_map]

        # Sort mapped transmitters by perturbation score (highest to lowest)
        ranked_mapped = sorted(mapped_tx, key=lambda x: x[1], reverse=True)
        ranked_unmapped = sorted(unmapped_tx, key=lambda x: x[1], reverse=True)

        # Select only mapped transmitters exceeding the calibrated noise floor cutoff
        active_zones = []
        people = []
        for rank, (tx, score) in enumerate(ranked_mapped, 1):
            if score >= self.variance_threshold:
                zone_name = self.tx_zone_map[tx]
                if zone_name not in active_zones:
                    active_zones.append(zone_name)
                    people.append({
                        "id": rank,
                        "zone": zone_name,
                        "tx": tx,
                        "score": round(score, 2)
                    })

        # Strongest Perturbation Selection:
        # A valid mapped transmitter exceeding threshold takes precedence.
        # An unmapped rogue transmitter CANNOT suppress a valid mapped transmitter.
        if ranked_mapped and ranked_mapped[0][1] >= self.variance_threshold:
            primary_zone = self.tx_zone_map[ranked_mapped[0][0]]
        elif ranked_unmapped and ranked_unmapped[0][1] >= self.variance_threshold:
            # Only unmapped transmitter(s) exceeded the threshold -> isolated to UNKNOWN
            primary_zone = "UNKNOWN"
        else:
            primary_zone = "CLEAR"

        # Note: active_zones reflects distinct RF sectors with variance >= threshold,
        # not physically calibrated multi-person counting.
        active_zone_count = len(active_zones)

        return {
            "signal_ok": True,
            "count": active_zone_count,
            "active_zone_count": active_zone_count,
            "zone": primary_zone,
            "inference_status": "ACTIVE_PERTURBATION" if primary_zone != "CLEAR" else "BASELINE_CLEAR",
            "people": people,
            "active_links": active_links,
            "confidence": None,
            "reason": "ZONE_PERTURBATION_DETECTED" if primary_zone != "CLEAR" else "BASELINE_OK"
        }
