import unittest
import numpy as np

from spatial.types import CSIRecord
from spatial.features import extract_link_features, fuse_features
from spatial.inference import SpatialBaseline
from spatial.tracker import PersonTracker
from spatial.window import MultiLinkWindow


class TestSpatial(unittest.TestCase):

    def make_records(self):
        records = []
        for rx in ["RX1", "RX2"]:
            for tx in ["TX1", "TX2", "TX3", "TX4"]:
                records.append(
                    CSIRecord(
                        timestamp=100.0,
                        receiver_id=rx,
                        source_mac="SIM",
                        rssi=-60.0,
                        amplitudes=[60.0 for _ in range(64)],
                        rate_hz=20.0,
                        tx_id=tx
                    )
                )
        return records

    def test_8_links(self):
        # 3 samples per link so extract_link_features has enough data
        records = []
        for t in [100.0, 100.05, 100.1]:
            for r in self.make_records():
                r_copy = CSIRecord(
                    timestamp=t,
                    receiver_id=r.receiver_id,
                    source_mac=r.source_mac,
                    rssi=r.rssi,
                    amplitudes=r.amplitudes,
                    rate_hz=r.rate_hz,
                    tx_id=r.tx_id
                )
                records.append(r_copy)

        features = extract_link_features(records)
        vector, active = fuse_features(features)

        self.assertEqual(active, 8)
        self.assertEqual(vector.shape[0], 48)

    def test_signal_gate(self):
        model = SpatialBaseline()
        state = model.predict([], 0, False)
        self.assertFalse(state["signal_ok"])
        self.assertEqual(state["reason"], "SIGNAL_UNSTABLE")

    def test_tracker_id_persistence(self):
        tracker = PersonTracker()
        
        # Frame 1: 2 people in Z1 and Z2
        frame1 = tracker.update([{"zone": "Z1"}, {"zone": "Z2"}])
        self.assertEqual(len(frame1), 2)
        id_z1 = frame1[0]["id"]
        id_z2 = frame1[1]["id"]
        
        # Frame 2: Same zones -> Should retain exact same IDs
        frame2 = tracker.update([{"zone": "Z1"}, {"zone": "Z2"}])
        self.assertEqual(frame2[0]["id"], id_z1)
        self.assertEqual(frame2[1]["id"], id_z2)

    def test_multi_link_window(self):
        win = MultiLinkWindow(seconds=2.0, step=0.5)
        # Adding record at t=1.0 emits initial window
        r1 = CSIRecord(1.0, "RX1", "MAC1", -60, [10]*64, 20, "TX1")
        w1 = win.add(r1)
        self.assertIsNotNone(w1)
        
        # Adding record at t=1.2 (less than 0.5 step) does not emit
        r2 = CSIRecord(1.2, "RX1", "MAC1", -60, [10]*64, 20, "TX1")
        w2 = win.add(r2)
        self.assertIsNone(w2)
        
        # Adding record at t=1.6 (>= 0.5 step) emits window
        r3 = CSIRecord(1.6, "RX1", "MAC1", -60, [10]*64, 20, "TX1")
        w3 = win.add(r3)
        self.assertIsNotNone(w3)
        self.assertEqual(len(w3), 3)


if __name__ == "__main__":
    unittest.main()
