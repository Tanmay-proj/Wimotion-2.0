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

    def test_replay_single_rx_only_records(self):
        from spatial.replay_loader import evaluate_window_frame

        # Only RX1 records present (no RX2 packets at all)
        records = [
            CSIRecord(1.0 + i*0.1, "RX1", "MAC1", -60, [10]*64, 10.0, "TX1") for i in range(10)
        ] + [
            CSIRecord(1.0 + i*0.1, "RX1", "MAC2", -60, [10]*64, 10.0, "TX2") for i in range(10)
        ]

        frame = evaluate_window_frame(
            window_records=records,
            window_seconds=2.0,
            total_duration=10.0,
            current_offset=1.0,
            window_end=2.0,
            latest_gt_count=1,
            latest_gt_zone="Z1",
            latest_motion="MOTION"
        )

        # RX1 links should have positive rates
        self.assertGreater(frame["link_details"]["RX1-TX1"]["rate"], 0)
        self.assertGreater(frame["link_details"]["RX1-TX2"]["rate"], 0)

        # RX2 links must have 0 rate and be IDLE
        for link_name, det in frame["link_details"].items():
            if link_name.startswith("RX2-"):
                self.assertEqual(det["rate"], 0.0)
                self.assertEqual(det["status"], "IDLE")

        # Active links count must strictly reflect only links with valid samples (2 links)
        self.assertEqual(frame["active_links"], 2)

    def test_replay_link_variance_without_samples_is_not_active(self):
        from spatial.replay_loader import evaluate_window_frame
        from unittest.mock import patch

        # Mock feature extractor returning a link with high variance but 0 sample_count
        fake_features = [
            {
                "receiver": "RX1",
                "tx": "TX1",
                "csi_variance": 22.5,  # high variance
                "sample_count": 0,     # NO valid samples in window
                "rssi": -60.0
            }
        ]

        with patch("spatial.replay_loader.extract_link_features", return_value=fake_features):
            frame = evaluate_window_frame(
                window_records=[CSIRecord(1.0, "RX1", "MAC1", -60, [10]*64, 0.0, "TX1")],
                window_seconds=2.0,
                total_duration=10.0,
                current_offset=0.0,
                window_end=1.0,
                latest_gt_count=0,
                latest_gt_zone="CLEAR",
                latest_motion="EMPTY"
            )

            # Link with 0 samples must remain IDLE despite high variance
            det = frame["link_details"]["RX1-TX1"]
            self.assertEqual(det["rate"], 0.0)
            self.assertEqual(det["status"], "IDLE")
            self.assertNotEqual(det["status"], "PERTURBED")
            self.assertNotEqual(det["status"], "ACTIVE")
            self.assertEqual(frame["active_links"], 0)

    def test_mode_switching_transactional_error_handling(self):
        import spatial.server as server
        from fastapi import HTTPException

        server.set_mode({"mode": "LIVE"})
        self.assertEqual(server.get_mode()["mode"], "LIVE")

        # Reject invalid mode with HTTP 400
        with self.assertRaises(HTTPException) as ctx:
            server.set_mode({"mode": "INVALID_CORRUPTED_MODE"})
        self.assertEqual(ctx.exception.status_code, 400)

        # Verify mode remains unchanged (transactional integrity)
        self.assertEqual(server.get_mode()["mode"], "LIVE")

    def test_cycle_modes_no_leakage(self):
        import spatial.server as server

        original_mode = server.CURRENT_MODE
        try:
            # 1. LIVE
            server.set_mode({"mode": "LIVE"})
            st_live = server.get_spatial()
            self.assertIn(st_live["source"], ["LIVE", "LIVE_STANDBY"])

            # 2. REPLAY
            server.set_mode({"mode": "REPLAY"})
            st_replay = server.get_spatial()
            self.assertEqual(st_replay["source"], "REPLAY")

            # 3. SIMULATION with injection
            server.set_mode({"mode": "SIMULATION"})
            server.update_simulate({"zone": "Z4", "active_zone_count": 1})
            st_sim = server.get_spatial()
            self.assertEqual(st_sim["source"], "SIMULATION")
            self.assertEqual(st_sim["zone"], "Z4")

            # 4. Return to LIVE -> Simulation state cleared
            server.set_mode({"mode": "LIVE"})
            st_live_again = server.get_spatial()
            self.assertIn(st_live_again["source"], ["LIVE", "LIVE_STANDBY"])
            self.assertNotEqual(st_live_again["zone"], "Z4")
            self.assertEqual(server.SIMULATION_STATE["zone"], "CLEAR")
            self.assertEqual(server.SIMULATION_STATE["active_zone_count"], 0)
        finally:
            server.set_mode({"mode": original_mode})

    def test_replay_aggregate_rate_formula_and_units(self):
        from spatial.replay_loader import evaluate_window_frame

        # Window duration: 2.0s
        # 10 records for RX1-TX1 -> 5.0 Hz
        # 6 records for RX1-TX2 -> 3.0 Hz
        # Total records = 16 -> Total aggregate rate = 8.0 Hz
        records = [
            CSIRecord(1.0 + i*0.1, "RX1", "MAC1", -60, [10]*64, 5.0, "TX1") for i in range(10)
        ] + [
            CSIRecord(1.0 + i*0.1, "RX1", "MAC2", -60, [10]*64, 3.0, "TX2") for i in range(6)
        ]

        frame = evaluate_window_frame(
            window_records=records,
            window_seconds=2.0,
            total_duration=10.0,
            current_offset=1.0,
            window_end=2.0,
            latest_gt_count=1,
            latest_gt_zone="Z1",
            latest_motion="MOTION"
        )

        self.assertEqual(frame["rate_hz"], 8.0)
        self.assertEqual(frame["link_details"]["RX1-TX1"]["rate"], 5.0)
        self.assertEqual(frame["link_details"]["RX1-TX2"]["rate"], 3.0)
        
        # Verify sum of per-link rates equals aggregate rate
        sum_link_rates = sum(d["rate"] for d in frame["link_details"].values())
        self.assertAlmostEqual(sum_link_rates, frame["rate_hz"], places=1)

    def test_bisect_window_slicing_equivalence(self):
        import bisect
        from spatial.types import CSIRecord

        # Generate 200 synthetic records with strictly monotonic timestamps
        records_by_time = []
        timestamps = []
        for i in range(200):
            t = 100.0 + i * 0.05
            r = CSIRecord(t, "RX1", "MAC1", -60, [10]*64, 20.0, "TX1")
            records_by_time.append((t, r, 0, "CLEAR", "EMPTY"))
            timestamps.append(t)

        # Test 10 arbitrary window intervals
        window_seconds = 2.0
        for offset in [0.0, 0.5, 1.25, 2.5, 4.0, 5.5, 7.0, 8.2]:
            window_end = 100.0 + offset
            window_start = window_end - window_seconds

            # Method A: Linear scan (original baseline)
            linear_records = [
                item[1]
                for item in records_by_time
                if window_start <= item[0] <= window_end
            ]

            # Method B: O(log N) Bisect search (optimized)
            idx_start = bisect.bisect_left(timestamps, window_start)
            idx_end = bisect.bisect_right(timestamps, window_end)
            bisect_records = [item[1] for item in records_by_time[idx_start:idx_end]]

            # Must be 100% equivalent in length and contents
            self.assertEqual(len(linear_records), len(bisect_records))
            self.assertEqual([r.timestamp for r in linear_records], [r.timestamp for r in bisect_records])

    def test_auto_browser_opener_when_server_ready(self):
        from unittest.mock import patch, MagicMock
        from spatial.server import _launch_browser_when_ready

        # 1. Success case: server returns HTTP 200 on /health -> browser opens
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__.return_value = mock_resp

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen, \
             patch("webbrowser.open") as mock_browser_open:
            t = _launch_browser_when_ready(url="http://127.0.0.1:8000", max_retries=5, delay=0.01)
            t.join(timeout=1.0)
            mock_browser_open.assert_called_once_with("http://127.0.0.1:8000")

        # 2. Timeout case: server unreachable -> browser must NOT open
        with patch("urllib.request.urlopen", side_effect=Exception("Connection refused")), \
             patch("webbrowser.open") as mock_browser_open_fail:
            t = _launch_browser_when_ready(url="http://127.0.0.1:8000", max_retries=2, delay=0.01)
            t.join(timeout=1.0)
            mock_browser_open_fail.assert_not_called()


    def test_demo_session_in_session_library(self):
        from spatial.replay_loader import list_recordings

        recordings = list_recordings()
        demo_rec = next((r for r in recordings if r["session_id"] == "demo_session"), None)
        self.assertIsNotNone(demo_rec, "demo_session must be present in list_recordings()")
        self.assertTrue(demo_rec["is_demo"])
        self.assertEqual(demo_rec["format"], "DEMO_SCENARIO_SCRIPTED")
        self.assertEqual(demo_rec["scenario_name"], "4-Zone People Movement Demo")
        self.assertEqual(demo_rec["duration_seconds"], 95.0)

    def test_demo_session_exact_95s_timeline_and_occupancy_sequence(self):
        from spatial.replay_loader import load_recording_frames

        data = load_recording_frames("demo_session")
        self.assertIsNotNone(data)
        self.assertEqual(data["total_duration"], 95.0)
        self.assertEqual(data["total_frames"], 191)  # 0.0 to 95.0 @ 0.5s step

        frames = data["frames"]
        self.assertEqual(len(frames), 191)

        # 1. 00-15s: Occupancy = 0, no person markers
        for f in frames:
            if f["time_offset"] < 15.0:
                self.assertEqual(f["occupancy"], 0)
                self.assertEqual(len(f["people"]), 0)

        # 2. 15-30s: Occupancy = 1, P1 in Zone 1
        for f in frames:
            if 15.0 <= f["time_offset"] < 30.0:
                self.assertEqual(f["occupancy"], 1)
                self.assertEqual(len(f["people"]), 1)
                self.assertEqual(f["people"][0]["id"], "P1")
                self.assertEqual(f["people"][0]["zone"], "Z1")

        # 3. 30-45s: Occupancy = 1, P1 moves to Zone 3
        for f in frames:
            if 30.0 <= f["time_offset"] < 45.0:
                self.assertEqual(f["occupancy"], 1)
                self.assertEqual(len(f["people"]), 1)
                self.assertEqual(f["people"][0]["id"], "P1")
                if f["time_offset"] >= 34.0:
                    self.assertEqual(f["people"][0]["zone"], "Z3")

        # 4. 45-55s: Occupancy = 0, markers disappear (settling)
        for f in frames:
            if 45.0 <= f["time_offset"] < 55.0:
                self.assertEqual(f["occupancy"], 0)
                self.assertEqual(len(f["people"]), 0)

        # 5. 55-70s: Occupancy = 2, P1 in Zone 2 and P2 in Zone 4
        for f in frames:
            if 55.0 <= f["time_offset"] < 70.0:
                self.assertEqual(f["occupancy"], 2)
                self.assertEqual(len(f["people"]), 2)
                ids = {p["id"] for p in f["people"]}
                self.assertEqual(ids, {"P1", "P2"})
                zones = {p["id"]: p["zone"] for p in f["people"]}
                self.assertEqual(zones["P1"], "Z2")
                self.assertEqual(zones["P2"], "Z4")

        # 6. 70-85s: Occupancy = 2, both P1 and P2 in Zone 1
        for f in frames:
            if 70.0 <= f["time_offset"] < 85.0:
                self.assertEqual(f["occupancy"], 2)
                self.assertEqual(len(f["people"]), 2)
                ids = {p["id"] for p in f["people"]}
                self.assertEqual(ids, {"P1", "P2"})
                if f["time_offset"] >= 74.0:
                    self.assertEqual(f["people"][0]["zone"], "Z1")
                    self.assertEqual(f["people"][1]["zone"], "Z1")

        # 7. 85-95s: Occupancy = 0, markers disappear (settling/final)
        for f in frames:
            if 85.0 <= f["time_offset"] <= 95.0:
                self.assertEqual(f["occupancy"], 0)
                self.assertEqual(len(f["people"]), 0)

        # Final frame (t=95.0s) must be strictly empty
        last_frame = frames[-1]
        self.assertEqual(last_frame["time_offset"], 95.0)
        self.assertEqual(last_frame["occupancy"], 0)
        self.assertEqual(len(last_frame["people"]), 0)

    def test_demo_session_persistent_marker_ids_and_transitions(self):
        from spatial.replay_loader import load_recording_frames

        data = load_recording_frames("demo_session")
        frames = data["frames"]

        # Track IDs across phases: P1, P2 only (no P3)
        p1_frames = [f for f in frames if any(p["id"] == "P1" for p in f["people"])]
        p2_frames = [f for f in frames if any(p["id"] == "P2" for p in f["people"])]
        p3_frames = [f for f in frames if any(p["id"] == "P3" for p in f["people"])]

        # P3 must not exist at all
        self.assertEqual(len(p3_frames), 0)

        # P1 exists in 15s-45s (solo) and 55s-85s (with P2)
        self.assertTrue(all((15.0 <= f["time_offset"] < 45.0) or (55.0 <= f["time_offset"] < 85.0) for f in p1_frames))

        # P2 exists only in 55s-85s
        self.assertTrue(all(55.0 <= f["time_offset"] < 85.0 for f in p2_frames))

        # Verify markers are strictly placed in their discrete zones without floating between zones
        for f in frames:
            if 15.0 <= f["time_offset"] < 30.0:
                self.assertEqual(f["people"][0]["zone"], "Z1")
                self.assertEqual((f["people"][0]["x"], f["people"][0]["y"]), (285.0, 125.0))
            elif 30.0 <= f["time_offset"] < 45.0:
                self.assertEqual(f["people"][0]["zone"], "Z3")
                self.assertEqual((f["people"][0]["x"], f["people"][0]["y"]), (125.0, 275.0))
            elif 55.0 <= f["time_offset"] < 70.0:
                self.assertEqual(f["people"][0]["zone"], "Z2")
                self.assertEqual(f["people"][1]["zone"], "Z4")
            elif 70.0 <= f["time_offset"] < 85.0:
                self.assertEqual(f["people"][0]["zone"], "Z1")
                self.assertEqual(f["people"][1]["zone"], "Z1")
                self.assertEqual((f["people"][0]["x"], f["people"][0]["y"]), (270.0, 115.0))
                self.assertEqual((f["people"][1]["x"], f["people"][1]["y"]), (295.0, 135.0))


    def test_provenance_and_session_discovery(self):
        from spatial.replay_loader import list_recordings

        recordings = list_recordings()
        self.assertGreaterEqual(len(recordings), 2)

        source_types = {r["session_id"]: r.get("source_type") for r in recordings}
        self.assertEqual(source_types.get("demo_session"), "scripted_presentation")
        self.assertEqual(source_types.get("benchmark_session_01"), "synthetic_generated_benchmark")
        self.assertEqual(source_types.get("synthetic_session_01"), "synthetic_augmented")
        self.assertEqual(source_types.get("public_esp_fi_01"), "unverified_import")
        self.assertEqual(source_types.get("held_out_empty_01"), "hardware_recorded_single_link")

        # Verify display names are present and natural
        for r in recordings:
            self.assertIn("display_name", r)
            self.assertIn("source_type", r)
            self.assertTrue(len(r["display_name"]) > 0)

    def test_genuine_vs_scripted_replay_isolation(self):
        from spatial.replay_loader import load_recording_frames

        # 1. Non-existent session must return None and NEVER fall back to demo_session
        missing = load_recording_frames("non_existent_fake_session_12345")
        self.assertIsNone(missing)

        # 2. Benchmark session must return real records and honest synthetic benchmark provenance
        benchmark_data = load_recording_frames("benchmark_session_01")
        self.assertIsNotNone(benchmark_data)
        self.assertEqual(benchmark_data["source_type"], "synthetic_generated_benchmark")
        self.assertFalse(benchmark_data["is_demo"])
        self.assertIn("malformed_rows", benchmark_data)

        # 3. Genuine held-out session must return genuine hardware provenance
        genuine_ho = load_recording_frames("held_out_empty_01")
        self.assertIsNotNone(genuine_ho)
        self.assertEqual(genuine_ho["source_type"], "hardware_recorded_single_link")

        # 3. Scripted demo session must return scripted provenance
        scripted = load_recording_frames("demo_session")
        self.assertIsNotNone(scripted)
        self.assertEqual(scripted["source_type"], "scripted_presentation")
        self.assertTrue(scripted["is_demo"])

    def test_v1_model_adapter_217_features_and_inference(self):
        from spatial.v1_adapter import V1PresenceModelAdapter, extract_v1_features

        adapter = V1PresenceModelAdapter()
        self.assertTrue(adapter.is_available(), f"Model failed to load: {adapter.load_error}")

        # Exact 217-feature dimension contract
        dummy_window = np.ones((20, 64), dtype=float) * 60.0
        feats = extract_v1_features(dummy_window)
        self.assertEqual(feats.shape, (217,))
        self.assertFalse(np.isnan(feats).any())

        # Predict quiet link stream -> empty_room
        res = adapter.predict_link_stream(dummy_window)
        self.assertTrue(res["available"])
        self.assertEqual(res["prediction"], "empty_room")
        self.assertLess(res["presence_probability"], 0.20)

    def test_v1_model_adapter_edge_cases_and_missing_model(self):
        from spatial.v1_adapter import V1PresenceModelAdapter

        adapter = V1PresenceModelAdapter()

        # 1. Insufficient frames (< 5 frames)
        tiny_window = np.ones((3, 64), dtype=float) * 55.0
        tiny_res = adapter.predict_link_stream(tiny_window)
        self.assertTrue(tiny_res["available"])
        self.assertEqual(tiny_res["prediction"], "INSUFFICIENT_FRAMES")
        self.assertEqual(tiny_res["presence_probability"], 0.0)

        # 2. Empty multi-link window
        empty_multi = adapter.evaluate_multilink_window([])
        self.assertEqual(empty_multi["global_presence"], "insufficient_data")
        self.assertIsNone(empty_multi["confidence"])

        # 3. Model load failure / missing model file
        missing_adapter = V1PresenceModelAdapter(model_filename="non_existent_model_file_xyz.pkl")
        self.assertFalse(missing_adapter.is_available())
        missing_res = missing_adapter.predict_link_stream(np.ones((20, 64), dtype=float))
        self.assertFalse(missing_res["available"])
        self.assertEqual(missing_res["prediction"], "UNKNOWN")

        missing_multi = missing_adapter.evaluate_multilink_window([])
        self.assertFalse(missing_multi["model_available"])
        self.assertEqual(missing_multi["global_presence"], "UNKNOWN")

    def test_compat_unpickler_cross_numpy_support(self):
        from spatial.v1_adapter import CompatUnpickler, ROOT

        model_path = ROOT / "models" / "presence_model.pkl"
        self.assertTrue(model_path.exists())
        with open(model_path, "rb") as f:
            obj = CompatUnpickler(f).load()
        self.assertIsInstance(obj, dict)
        self.assertIn("model", obj)
        self.assertEqual(obj.get("classifier_name"), "HistGradientBoosting")

    def test_benchmark_generator_honest_metadata_contract(self):
        from spatial.v1_adapter import ROOT
        import json

        script_path = ROOT / "scripts" / "create_benchmark_session.py"
        self.assertTrue(script_path.exists())

        # Verify generator source code enforces honest metadata and does not claim verified physical trial
        script_content = script_path.read_text(encoding="utf-8")
        self.assertNotIn("reconstructing verified South-West", script_content)
        self.assertIn('"source_type": "synthetic_generated_benchmark"', script_content)

        # Verify metadata file on disk has matching provenance and software-generated description
        meta_file = ROOT / "data" / "raw" / "benchmark_session_01" / "metadata_Z3_1P.json"
        self.assertTrue(meta_file.exists())
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        self.assertEqual(meta.get("source_type"), "synthetic_generated_benchmark")
        self.assertEqual(meta.get("provenance"), "synthetic_generated_benchmark")
        self.assertNotIn("verified", meta.get("description", "").lower())
        self.assertIn("software-generated", meta.get("description", "").lower())

    def test_unknown_transmitter_handling(self):
        model = SpatialBaseline(variance_threshold=8.0)

        # Scenario 1: Unknown TX only -> UNKNOWN, never false Z1/Z2/Z3/Z4
        feats_unknown_only = [{
            "receiver": "RX1",
            "tx": "TX_ROGUE_UNKNOWN",
            "csi_variance": 45.0,
            "sample_count": 20,
            "rssi": -55.0
        }]
        st1 = model.predict(feats_unknown_only, active_links=1, signal_ok=True)
        self.assertNotEqual(st1["zone"], "Z1")
        self.assertEqual(st1["zone"], "UNKNOWN")
        self.assertEqual(st1["active_zone_count"], 0)
        self.assertEqual(st1["people"], [])

        # Scenario 2: Rogue TX with high score (50.0) + Known TX1 above threshold (20.0)
        # Rogue TX must NEVER suppress the valid mapped TX1
        feats_rogue_and_valid = [
            {"receiver": "RX1", "tx": "TX_ROGUE_UNKNOWN", "csi_variance": 50.0, "sample_count": 20},
            {"receiver": "RX1", "tx": "TX1", "csi_variance": 20.0, "sample_count": 20}
        ]
        st2 = model.predict(feats_rogue_and_valid, active_links=2, signal_ok=True)
        self.assertEqual(st2["zone"], "Z1")
        self.assertEqual(st2["active_zone_count"], 1)
        self.assertEqual(len(st2["people"]), 1)
        self.assertEqual(st2["people"][0]["tx"], "TX1")
        self.assertEqual(st2["people"][0]["zone"], "Z1")

        # Scenario 3: Known TX below calibrated threshold (5.0 < 8.0) -> CLEAR
        feats_subthreshold = [
            {"receiver": "RX1", "tx": "TX1", "csi_variance": 5.0, "sample_count": 20}
        ]
        st3 = model.predict(feats_subthreshold, active_links=1, signal_ok=True)
        self.assertEqual(st3["zone"], "CLEAR")
        self.assertEqual(st3["active_zone_count"], 0)
        self.assertEqual(st3["people"], [])

        # Scenario 4: Multiple known active TXs (TX1=25.0, TX3=18.0)
        feats_multiple = [
            {"receiver": "RX1", "tx": "TX1", "csi_variance": 25.0, "sample_count": 20},
            {"receiver": "RX1", "tx": "TX3", "csi_variance": 18.0, "sample_count": 20}
        ]
        st4 = model.predict(feats_multiple, active_links=2, signal_ok=True)
        self.assertEqual(st4["zone"], "Z1")  # strongest perturbation
        self.assertEqual(st4["active_zone_count"], 2)
        self.assertEqual(len(st4["people"]), 2)
        self.assertEqual([p["zone"] for p in st4["people"]], ["Z1", "Z3"])

        # Scenario 5: No valid links (active_links=0)
        st5 = model.predict([], active_links=0, signal_ok=True)
        self.assertFalse(st5["signal_ok"])
        self.assertEqual(st5["zone"], "UNKNOWN")
        self.assertEqual(st5["reason"], "NO_VALID_LINKS")
        self.assertEqual(st5["active_zone_count"], 0)

        # Scenario 6: Unstable signal (signal_ok=False)
        st6 = model.predict(feats_multiple, active_links=2, signal_ok=False)
        self.assertFalse(st6["signal_ok"])
        self.assertEqual(st6["zone"], "UNKNOWN")
        self.assertEqual(st6["reason"], "SIGNAL_UNSTABLE")
        self.assertEqual(st6["active_zone_count"], 0)

        # Scenario 7: Single-receiver operation (only RX1 active with TX2)
        feats_single_rx = [
            {"receiver": "RX1", "tx": "TX2", "csi_variance": 22.0, "sample_count": 20}
        ]
        st7 = model.predict(feats_single_rx, active_links=1, signal_ok=True)
        self.assertTrue(st7["signal_ok"])
        self.assertEqual(st7["zone"], "Z2")
        self.assertEqual(st7["active_zone_count"], 1)

    def test_provenance_enforcement_and_isolation(self):
        from spatial.replay_loader import list_recordings, load_recording_frames
        from scripts.evaluate_models import evaluate_session

        # 1. Missing provenance in metadata must default to unknown_unverified, NEVER hardware_recorded
        # Test loading a mocked session directory without source_type
        import tempfile
        import shutil
        import json
        from pathlib import Path
        import spatial.replay_loader as loader

        temp_dir = tempfile.mkdtemp(prefix="wimotion_prov_test_")
        try:
            p = Path(temp_dir)
            meta_path = p / "metadata.json"
            meta_path.write_text(json.dumps({"description": "Test session with missing provenance"}), encoding="utf-8")
            csv_path = p / "data.csv"
            # Write minimal valid header
            header = ["timestamp", "rx", "tx", "mac", "rssi", "rate", "gt_count", "gt_zone", "motion_state", "channel"] + [f"sub_{i}" for i in range(64)]
            csv_path.write_text(",".join(header) + "\n", encoding="utf-8")

            # Patch DATA_RAW temporarily
            orig_data_raw = loader.DATA_RAW
            loader.DATA_RAW = p.parent
            try:
                recs = loader.list_recordings()
                target = next((r for r in recs if r["session_id"] == p.name), None)
                self.assertIsNotNone(target)
                self.assertEqual(target["source_type"], "unknown_unverified")
                self.assertNotEqual(target["source_type"], "hardware_recorded")
            finally:
                loader.DATA_RAW = orig_data_raw
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        # 2. Verify synthetic sessions cannot claim genuine hardware
        bench = load_recording_frames("benchmark_session_01")
        self.assertIsNotNone(bench)
        self.assertEqual(bench["source_type"], "synthetic_generated_benchmark")
        self.assertFalse(bench["source_type"].startswith("hardware_recorded"))

        # 3. Verify public dataset without independent upstream verification is unverified_import
        pub = load_recording_frames("public_esp_fi_01")
        self.assertIsNotNone(pub)
        self.assertEqual(pub["source_type"], "unverified_import")
        self.assertFalse(pub["source_type"].startswith("hardware_recorded"))

    def test_synthetic_augmentation_reproducibility(self):
        from spatial.augmentation import augment_csi_frame, GUARD_SUBCARRIERS, DC_SUBCARRIER

        raw_amps = [60.0] * 64
        rng1 = np.random.RandomState(42)
        aug1 = augment_csi_frame(raw_amps, gain_scale=1.04, noise_std=0.03, rng=rng1)

        rng2 = np.random.RandomState(42)
        aug2 = augment_csi_frame(raw_amps, gain_scale=1.04, noise_std=0.03, rng=rng2)

        # Exact reproducibility with same seed
        self.assertEqual(aug1, aug2)

        # Guard and DC subcarriers must be strictly 0.0
        for idx in GUARD_SUBCARRIERS + DC_SUBCARRIER:
            self.assertEqual(aug1[idx], 0.0)

    def test_public_dataset_adapter(self):
        from spatial.dataset_adapters.esp_fi_adapter import ESPFiHARAdapter

        adapter = ESPFiHARAdapter()
        # Mock 52 comma-separated numbers (label '1' for walking + 52 values)
        line = "1," + ",".join(["62.5"] * 52)
        parsed = adapter.parse_csi_line(line)

        self.assertIsNotNone(parsed)
        self.assertEqual(len(parsed["amplitudes_64"]), 64)
        self.assertEqual(parsed["activity_label"], "walking")
        self.assertEqual(parsed["presence_label"], "human_present")

    def test_evaluation_zero_denominator_and_invalid_handling(self):
        from scripts.evaluate_models import compute_metrics

        # 1. Pure empty room (0 actual positives): Recall must be None (Undefined), NOT 1.0 or 100%
        empty_res = compute_metrics(tp=0, fp=18, tn=19, fn=0, invalid_windows=7)
        self.assertIsNone(empty_res["recall_pct"])
        self.assertEqual(empty_res["precision_pct"], 0.0)
        self.assertEqual(empty_res["specificity_pct"], 51.35)
        self.assertEqual(empty_res["valid_windows"], 37)
        self.assertEqual(empty_res["invalid_windows"], 7)
        self.assertEqual(empty_res["total_windows"], 44)

        # 2. Pure walking session (0 actual negatives): Specificity must be None (Undefined)
        walk_res = compute_metrics(tp=59, fp=0, tn=0, fn=0, invalid_windows=6)
        self.assertIsNone(walk_res["specificity_pct"])
        self.assertEqual(walk_res["recall_pct"], 100.0)
        self.assertEqual(walk_res["precision_pct"], 100.0)
        self.assertEqual(walk_res["valid_windows"], 59)
        self.assertEqual(walk_res["invalid_windows"], 6)

        # 3. No positive predictions made: Precision must be None (Undefined)
        no_pos_res = compute_metrics(tp=0, fp=0, tn=20, fn=10)
        self.assertIsNone(no_pos_res["precision_pct"])

    def test_held_out_session_counts_and_separation(self):
        from spatial.replay_loader import load_recording_frames

        # Session 1: Held-out empty room
        empty_data = load_recording_frames("held_out_empty_01")
        self.assertIsNotNone(empty_data)
        self.assertEqual(empty_data["total_frames"], 44)
        self.assertTrue(empty_data["metadata"].get("is_held_out"))
        self.assertTrue(all(f["gt_count"] == 0 for f in empty_data["frames"]))

        # Session 2: Held-out walking presence
        walk_data = load_recording_frames("held_out_walking_01")
        self.assertIsNotNone(walk_data)
        self.assertEqual(walk_data["total_frames"], 65)
        self.assertTrue(walk_data["metadata"].get("is_held_out"))
        self.assertTrue(all(f["gt_count"] > 0 for f in walk_data["frames"]))

        # Combined count must be exactly 109
        self.assertEqual(empty_data["total_frames"] + walk_data["total_frames"], 109)

    def test_scripted_demo_ml_evaluation_rejected_gracefully(self):
        from scripts.evaluate_models import evaluate_session
        from spatial.v1_adapter import V1PresenceModelAdapter

        adapter = V1PresenceModelAdapter()
        res = evaluate_session("demo_session", adapter)
        self.assertIsNotNone(res)

        # Scripted demo frames lack physical multi-link packet stream for ML features
        # Evaluation suite must track all 191 windows as invalid rather than silently converting to empty_room
        ml_m = res["v1_ml_model"]
        self.assertEqual(ml_m["invalid_windows"], 191)
        self.assertEqual(ml_m["valid_windows"], 0)
        self.assertIsNone(ml_m["valid_accuracy_pct"])
        self.assertEqual(ml_m["all_window_accuracy_pct"], 0.0)
        self.assertIsNone(ml_m["recall_pct"])


if __name__ == "__main__":
    unittest.main()




