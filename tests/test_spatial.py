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
        if not recs:
            self.skipTest("No recordings found in data/raw")
        benchmark = recs[0]
        self.assertIn("session_id", benchmark)
        self.assertIn("format", benchmark)
        
        frames_data = load_recording_frames(benchmark["session_id"])
        self.assertIsNotNone(frames_data)
        self.assertIn("frames", frames_data)
        self.assertGreater(len(frames_data["frames"]), 0)
        self.assertIn("model_zone", frames_data["frames"][0])

    def test_server_mode_isolation_and_simulation(self):
        import spatial.server as server
        from unittest.mock import MagicMock

        original_mode = server.CURRENT_MODE
        original_engine = server.engine_instance
        try:
            # 1. Verify default or setting to LIVE
            server.set_mode({"mode": "LIVE"})
            self.assertEqual(server.get_mode()["mode"], "LIVE")

            # 2. Mock a live engine that returns an identifiable state
            mock_engine = MagicMock()
            mock_engine.get_state.return_value = {
                "source": "LIVE_HARDWARE",
                "zone": "Z1",
                "rate_hz": 99.0
            }
            server.engine_instance = mock_engine

            live_res = server.get_spatial()
            self.assertEqual(live_res["source"], "LIVE")
            self.assertEqual(live_res["zone"], "Z1")

            # 3. Switch to SIMULATION mode: Must strictly isolate and return SIMULATION state
            server.set_mode({"mode": "SIMULATION"})
            self.assertEqual(server.get_mode()["mode"], "SIMULATION")

            sim_res = server.get_spatial()
            self.assertEqual(sim_res["source"], "SIMULATION")
            self.assertEqual(sim_res["authoritative_mode"], "SIMULATION")
            self.assertNotEqual(sim_res["rate_hz"], 99.0)

            # 4. Inject synthetic state
            server.update_simulate({
                "zone": "Z3",
                "active_zone_count": 1,
                "people": [{"id": 1, "zone": "Z3", "score": 21.66}]
            })
            sim_injected = server.get_spatial()
            self.assertEqual(sim_injected["zone"], "Z3")
            self.assertEqual(sim_injected["active_zone_count"], 1)

            # 5. Switch back to LIVE: Stale simulation state must be cleared
            server.set_mode({"mode": "LIVE"})
            self.assertEqual(server.get_mode()["mode"], "LIVE")
            self.assertEqual(server.SIMULATION_STATE["zone"], "CLEAR")
            self.assertEqual(server.SIMULATION_STATE["active_zone_count"], 0)

        finally:
            server.CURRENT_MODE = original_mode
            server.engine_instance = original_engine

    def test_stale_engine_reports_unknown_zone(self):
        from spatial.live import LiveSpatialEngine
        import time

        engine = LiveSpatialEngine("config/nodes.json")
        # Simulate last packet received 10 seconds ago (exceeding 3.0s timeout)
        engine.last_packet_time = time.time() - 10.0
        
        state = engine.get_state()
        self.assertFalse(state["signal_ok"])
        self.assertEqual(state["zone"], "UNKNOWN")
        self.assertEqual(state["inference_status"], "UNAVAILABLE")
        self.assertEqual(state["active_zone_count"], 0)

    def test_inference_active_zone_count_and_status(self):
        model = SpatialBaseline()
        
        # Test 1: Clean features (baseline noise)
        features = [
            {"receiver": "RX1", "tx": "TX1", "csi_variance": 1.5, "rssi": -60.0},
            {"receiver": "RX1", "tx": "TX2", "csi_variance": 2.0, "rssi": -60.0}
        ]
        state_clean = model.predict(features, 8, True)
        self.assertEqual(state_clean["zone"], "CLEAR")
        self.assertEqual(state_clean["count"], 0)
        self.assertEqual(state_clean["active_zone_count"], 0)
        self.assertEqual(state_clean["inference_status"], "BASELINE_CLEAR")

        # Test 2: Perturbed link exceeding threshold 8.0
        features_perturbed = [
            {"receiver": "RX1", "tx": "TX3", "csi_variance": 19.5, "rssi": -55.0}
        ]
        state_perturbed = model.predict(features_perturbed, 8, True)
        self.assertEqual(state_perturbed["zone"], "Z3")
        self.assertEqual(state_perturbed["count"], 1)
        self.assertEqual(state_perturbed["active_zone_count"], 1)
        self.assertEqual(state_perturbed["inference_status"], "ACTIVE_PERTURBATION")

    def test_replay_loader_rate_quality_gate(self):
        from spatial.replay_loader import evaluate_window_frame

        # Only 2 records with rate = 1.0 Hz (below minimum 4.0 Hz rate gate)
        records = [
            CSIRecord(1.0, "RX1", "MAC1", -60, [10]*64, 1.0, "TX1"),
            CSIRecord(1.5, "RX1", "MAC1", -60, [10]*64, 1.0, "TX1")
        ]
        frame = evaluate_window_frame(
            window_records=records,
            window_seconds=2.0,
            total_duration=10.0,
            current_offset=0.5,
            window_end=1.5,
            latest_gt_count=1,
            latest_gt_zone="Z1",
            latest_motion="MOTION"
        )
        self.assertEqual(frame["eval_status"], "INSUFFICIENT_DATA")
        self.assertEqual(frame["model_zone"], "UNKNOWN")

    def test_replay_loader_missing_session_404(self):
        from spatial.replay_loader import load_recording_frames
        from fastapi import HTTPException
        import spatial.server as server

        res = load_recording_frames("non_existent_dummy_session_12345")
        self.assertIsNone(res)

        with self.assertRaises(HTTPException) as ctx:
            server.get_recording_data("non_existent_dummy_session_12345")
        self.assertEqual(ctx.exception.status_code, 404)

    def test_serial_manager_startup_failure_state(self):
        from spatial.serial_manager import SerialReceiverWorker

        # Instantiate a worker with an invalid port name that cannot connect
        worker = SerialReceiverWorker(
            receiver_id="RX1",
            port="INVALID_PORT_XYZ",
            baud=921600,
            mac_map={},
            on_record_callback=lambda r: None
        )
        worker.start()
        import time
        time.sleep(0.1)
        worker.stop()

        self.assertFalse(worker.running)
        self.assertIsNotNone(worker.last_error)
        self.assertIsNotNone(worker.last_error)


if __name__ == "__main__":
    unittest.main()

