"""
WiMotion 2.0 - Final Pre-Demo 6-Point Verification Script
Tests all 6 criteria from the colleague audit report and reports pass/fail with exact evidence.
"""

import sys
import unittest
from pathlib import Path

# Ensure workspace root is in python path
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from spatial.types import CSIRecord
from spatial.replay_loader import evaluate_window_frame, load_recording_frames
from spatial.features import extract_link_features
import spatial.server as server
from fastapi import HTTPException


def run_check_1():
    print("[1/6] Testing: Replay session with single RX (RX1 only) must NEVER mark RX2 active...")
    records = [
        CSIRecord(1.0 + i*0.1, "RX1", "MAC1", -60, [10]*64, 10.0, "TX1") for i in range(10)
    ]
    frame = evaluate_window_frame(
        window_records=records,
        window_seconds=2.0,
        total_duration=5.0,
        current_offset=1.0,
        window_end=2.0,
        latest_gt_count=0,
        latest_gt_zone="CLEAR",
        latest_motion="EMPTY"
    )
    assert frame["link_details"]["RX1-TX1"]["rate"] > 0, "RX1 link must have positive rate"
    for link, det in frame["link_details"].items():
        if link.startswith("RX2-"):
            assert det["rate"] == 0.0, f"{link} rate must be 0"
            assert det["status"] == "IDLE", f"{link} status must be IDLE"
    print("      -> PASS: RX2 links remain strictly IDLE with 0.0 Hz.")


def run_check_2():
    print("[2/6] Testing: High variance with 0 valid samples in window must remain IDLE (not active)...")
    from unittest.mock import patch
    fake_features = [{
        "receiver": "RX1",
        "tx": "TX1",
        "csi_variance": 45.2,
        "sample_count": 0,
        "rssi": -60.0
    }]
    with patch("spatial.replay_loader.extract_link_features", return_value=fake_features):
        frame = evaluate_window_frame(
            window_records=[],
            window_seconds=2.0,
            total_duration=5.0,
            current_offset=0.0,
            window_end=1.0,
            latest_gt_count=0,
            latest_gt_zone="CLEAR",
            latest_motion="EMPTY"
        )
        det = frame["link_details"]["RX1-TX1"]
        assert det["rate"] == 0.0, "Rate must be 0"
        assert det["status"] == "IDLE", f"Status was '{det['status']}' instead of IDLE"
        assert frame["active_links"] == 0, "Active links count must be 0"
    print("      -> PASS: Zero-sample link remained IDLE despite variance 45.2.")


def run_check_3():
    print("[3/6] Testing: Transactional mode switching and error rejection rollback...")
    server.set_mode({"mode": "LIVE"})
    assert server.get_mode()["mode"] == "LIVE"
    try:
        server.set_mode({"mode": "NON_EXISTENT_MODE"})
        assert False, "Should have raised HTTPException 400"
    except HTTPException as e:
        assert e.status_code == 400
    assert server.get_mode()["mode"] == "LIVE", "Mode must remain unchanged on error"
    print("      -> PASS: Invalid mode rejected with HTTP 400; state remained LIVE.")


def run_check_4():
    print("[4/6] Testing: Mode isolation lifecycle (LIVE -> REPLAY -> SIMULATION -> LIVE)...")
    server.set_mode({"mode": "LIVE"})
    assert server.get_spatial()["source"] in ["LIVE", "LIVE_STANDBY"]
    
    server.set_mode({"mode": "REPLAY"})
    assert server.get_spatial()["source"] == "REPLAY"

    server.set_mode({"mode": "SIMULATION"})
    server.update_simulate({"zone": "Z3", "count": 2})
    assert server.get_spatial()["zone"] == "Z3"

    server.set_mode({"mode": "LIVE"})
    st = server.get_spatial()
    assert st["source"] in ["LIVE", "LIVE_STANDBY"]
    assert st["zone"] != "Z3", "Simulated Z3 must not leak into LIVE mode"
    assert server.SIMULATION_STATE["zone"] == "CLEAR", "Simulation state reset on mode exit"
    print("      -> PASS: Clean state transitions without cross-mode state leakage.")


def run_check_5():
    print("[5/6] Testing: Replay aggregate rate formula (Sum of per-link rates == Aggregate rate)...")
    records = (
        [CSIRecord(1.0 + i*0.1, "RX1", "MAC1", -60, [10]*64, 5.0, "TX1") for i in range(10)] +
        [CSIRecord(1.0 + i*0.1, "RX1", "MAC2", -60, [10]*64, 3.0, "TX2") for i in range(6)]
    )
    frame = evaluate_window_frame(
        window_records=records,
        window_seconds=2.0,
        total_duration=5.0,
        current_offset=1.0,
        window_end=2.0,
        latest_gt_count=1,
        latest_gt_zone="Z1",
        latest_motion="MOTION"
    )
    sum_link_rates = sum(d["rate"] for d in frame["link_details"].values())
    assert abs(sum_link_rates - frame["rate_hz"]) < 0.01, f"Sum {sum_link_rates} != Total {frame['rate_hz']}"
    assert frame["rate_hz"] == 8.0, f"Expected 8.0 Hz, got {frame['rate_hz']}"
    print(f"      -> PASS: Sum of link rates ({sum_link_rates:.1f} Hz) == Aggregate rate ({frame['rate_hz']:.1f} Hz).")


def run_check_6():
    print("[6/6] Testing: Empty, missing, or sparse recording triggers UNKNOWN/UNAVAILABLE quality gate...")
    # Missing session
    missing = load_recording_frames("non_existent_session_12345")
    assert missing is None, "Missing session must return None"

    # Sparse data (< 4.0 Hz quality gate)
    sparse_records = [
        CSIRecord(1.0, "RX1", "MAC1", -60, [10]*64, 1.0, "TX1")
    ]
    frame = evaluate_window_frame(
        window_records=sparse_records,
        window_seconds=2.0,
        total_duration=5.0,
        current_offset=1.0,
        window_end=2.0,
        latest_gt_count=0,
        latest_gt_zone="CLEAR",
        latest_motion="EMPTY"
    )
    assert frame["eval_status"] == "INSUFFICIENT_DATA", "Must trigger INSUFFICIENT_DATA"
    assert frame["model_zone"] == "UNKNOWN", "Must report UNKNOWN zone"
    print("      -> PASS: Sparse / invalid sessions correctly gated as INSUFFICIENT_DATA / UNKNOWN.")


def main():
    print("==============================================================================")
    print("   WiMotion 2.0 — Colleague Audit 6-Point Verification Suite")
    print("==============================================================================")
    try:
        run_check_1()
        run_check_2()
        run_check_3()
        run_check_4()
        run_check_5()
        run_check_6()
        print("==============================================================================")
        print("   ALL 6/6 PRE-DEMO VERIFICATION CHECKS PASSED SUCCESSFULLY (100%)")
        print("==============================================================================")
        return 0
    except AssertionError as e:
        print(f"\n[FAIL] Assertion failed: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
