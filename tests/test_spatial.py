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
        self.assertEqual(vector.shape[0], 56)
        self.assertEqual(sum(vector[48:]), 8.0)  # All 8 links active in mask

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

    def test_live_engine_health_schema(self):
        from spatial.live import LiveSpatialEngine
        engine = LiveSpatialEngine("config/nodes.json")
        # Mock serial manager health dictionary output
        engine.serial_manager.get_health = lambda: {
            "RX1": {
                "port": "COM8",
                "running": True,
                "aggregate_rate_hz": 40.0,
                "rate_hz": 40.0,
                "status": "HEALTHY",
                "healthy": True
            }
        }
        # Verify _process_window doesn't crash with KeyError
        records = [
            CSIRecord(1.0, "RX1", "MAC1", -60, [10]*64, 20, "TX1"),
            CSIRecord(1.1, "RX1", "MAC1", -60, [10]*64, 20, "TX1"),
            CSIRecord(1.2, "RX1", "MAC1", -60, [12]*64, 20, "TX1"),
        ]
        engine._process_window(records)
        state = engine.get_state()
        self.assertTrue(state["signal_ok"])
        self.assertIsNone(state["confidence"])

    def test_parse_raw_hardware_csi_line(self):
        from spatial.parser import parse_line
        raw_iq = " ".join(["10", "-5"] * 64)
        sample_line = f"CSI_DATA,AP,BC:DD:C2:CC:49:F4,-55,11,0,0,0,0,0,0,0,0,0,-90,0,6,0,1234567,0,28,0,128,1,128,[{raw_iq}]"
        
        record = parse_line(sample_line, "RX1")
        self.assertIsNotNone(record)
        self.assertEqual(record.receiver_id, "RX1")
        self.assertEqual(record.source_mac, "BC:DD:C2:CC:49:F4")
        self.assertEqual(record.rssi, -55.0)
        self.assertEqual(len(record.amplitudes), 64)
        # Ensure timestamp is valid host epoch (> 1.7e9) and not corrupted by first_word_invalid
        self.assertGreater(record.timestamp, 1700000000.0)


    def test_replay_loader_benchmark(self):
        from spatial.replay_loader import list_recordings, load_recording_frames
        recs = list_recordings()
        self.assertGreater(len(recs), 0)
        benchmark = recs[0]
        self.assertIn("session_id", benchmark)
        self.assertIn("format", benchmark)
        
        frames_data = load_recording_frames(benchmark["session_id"])
        self.assertIsNotNone(frames_data)
        self.assertIn("frames", frames_data)
        self.assertGreater(len(frames_data["frames"]), 0)
        self.assertIn("model_zone", frames_data["frames"][0])


if __name__ == "__main__":
    unittest.main()

