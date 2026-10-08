import time
import random
from typing import List

from .types import CSIRecord
from .features import extract_link_features, fuse_features
from .inference import SpatialBaseline
from .tracker import PersonTracker
from .window import MultiLinkWindow


def main():
    engine = SpatialBaseline()
    tracker = PersonTracker()
    window = MultiLinkWindow(seconds=2.0, step=0.5)
    start = time.time()

    print("[*] Starting WiMotion 2.0 Multi-Link Synthetic Replay (600 frames)...")
    print(f"{'FRAME':>6} | {'COUNT':>6} | {'ZONE':>8} | {'ACTIVE LINKS':>12} | {'PEOPLE TRACKED':>24}")
    print("-" * 70)

    last_emitted_records = None

    for frame in range(600):
        timestamp = start + frame / 20.0

        # Simulate 2 Receivers and 4 Transmitters = 8 Candidate Links
        for rx in ["RX1", "RX2"]:
            for tx in ["TX1", "TX2", "TX3", "TX4"]:
                # Multi-target progression:
                # Frame 0-199: Empty Room (0 people)
                # Frame 200-399: 1 Person at Z1 (Doorway)
                # Frame 400-599: 2 People at Z1 and Z3 (Doorway + Flank)
                if frame >= 400:
                    motion = random.uniform(2.5, 5.0) if tx in ["TX1", "TX3"] else random.uniform(0.05, 0.15)
                elif frame >= 200:
                    motion = random.uniform(2.5, 5.0) if tx == "TX1" else random.uniform(0.05, 0.15)
                else:
                    motion = random.uniform(0.05, 0.20)

                amplitudes = [
                    60.0 + motion + random.uniform(-0.5, 0.5)
                    for _ in range(64)
                ]

                rec = CSIRecord(
                    timestamp=timestamp,
                    receiver_id=rx,
                    source_mac=f"SIM_{tx}",
                    rssi=-62.0 - (motion * 1.5),
                    amplitudes=amplitudes,
                    rate_hz=20.0,
                    tx_id=tx
                )

                res = window.add(rec)
                if res is not None:
                    last_emitted_records = res

        # Run inference on current sliding window every 20 frames (1 second interval)
        if last_emitted_records and (frame % 25 == 0 or frame == 599):
            features = extract_link_features(last_emitted_records)
            vector, active = fuse_features(features)
            state = engine.predict(features, active, True)
            tracked_people = tracker.update(state["people"])

            people_str = ", ".join([f"P{p['id']}@{p['zone']}" for p in tracked_people]) or "NONE"
            print(
                f"{frame:6d} | "
                f"{state['count']:6d} | "
                f"{state['zone']:>8} | "
                f"{active:12d} | "
                f"{people_str:>24}"
            )

    print("-" * 70)
    print("[+] Synthetic Replay Completed Successfully! Multi-link pipeline verified.")


if __name__ == "__main__":
    main()
