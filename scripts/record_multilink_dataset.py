#!/usr/bin/env python3
"""
WiMotion 2.0 — Multi-Link Raw CSI Session Recorder
Records simultaneous streams across all active RX ports and TX links.
Supports live prototype auto-detection: whatever the user does, the prototype
computes real-time spatial predictions (zone & count) on the fly and records them!
"""
import sys
import time
import json
import argparse
import threading
from pathlib import Path
from collections import deque, Counter
import csv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from spatial.config import load_config
from spatial.serial_manager import MultiSerialManager
from spatial.types import CSIRecord
from spatial.features import extract_link_features
from spatial.inference import SpatialBaseline
from spatial.replay_loader import invalidate_recordings_cache


def main():
    parser = argparse.ArgumentParser(description="WiMotion 2.0 Multi-Link Dataset Recorder")
    parser.add_argument("--session", type=str, default="session_001", help="Session ID (e.g. session_001)")
    parser.add_argument("--duration", type=float, default=20.0, help="Recording duration in seconds")
    parser.add_argument("--zone", type=str, default=None, choices=["Z1", "Z2", "Z3", "Z4", "CLEAR"], help="Optional single zone override")
    parser.add_argument("--zones", type=str, default=None, help="Optional multi-zone ground truth (e.g. 'Z1,Z3' for multi-person)")
    parser.add_argument("--count", type=int, default=None, help="Optional manual person count override")
    parser.add_argument("--motion-state", type=str, default=None, help="Optional manual motion state override")
    parser.add_argument("--room-id", type=str, default="ROOM_LAB_A", help="Room or Environment Identifier")
    parser.add_argument("--operator-id", type=str, default="OC_TANMAY", help="Operator or Cadet ID")
    parser.add_argument("--notes", type=str, default="", help="Experimental observation notes")
    args = parser.parse_args()

    session_clean = args.session.replace(".csv", "").strip()
    config = load_config()
    out_dir = ROOT / "data" / "raw" / session_clean
    out_dir.mkdir(parents=True, exist_ok=True)

    session_log_file = out_dir / f"multilink_data_{session_clean}.csv"
    meta_log_file = out_dir / f"metadata_{session_clean}.json"

    is_auto = (args.zone is None and args.zones is None and args.count is None)

    print(f"\n==============================================================================")
    print(f"             WiMotion 2.0 — Live Hardware Session Recorder")
    print(f"==============================================================================")
    print(f"    Session Name:     {session_clean}")
    print(f"    Duration:         {args.duration:.1f} seconds")
    mode_str = 'LIVE PROTOTYPE AUTO-DETECTION (Autonomous - Unverified GT)' if is_auto else f'Manual Ground Truth ({args.count or (len(args.zones.split(",")) if args.zones else 1)}P in {args.zones or args.zone})'
    print(f"    Operating Mode:   {mode_str}")
    if is_auto:
        print(f"    [!] SCIENTIFIC WARNING: No --zone provided! Recorded CSV labels are live heuristic guesses.")
        print(f"    [!] For supervised training, pass: --zone [CLEAR, Z1..Z4] --count [0, 1] --motion-state [WALKING...]")
    print(f"    Output CSV:       {session_log_file.name}")
    print(f"==============================================================================\n")

    fieldnames = [
        "timestamp", "receiver", "tx", "source_mac", "rssi", 
        "rate_hz", "ground_truth_count", "ground_truth_zone", "ground_truth_zones", "motion_state", "room_id"
    ] + [f"sub_{i}" for i in range(64)]

    csv_file = open(session_log_file, "w", newline="", encoding="utf-8")
    writer = csv.writer(csv_file)
    writer.writerow(fieldnames)

    # Thread safety lock for concurrent RX1 and RX2 streaming
    write_lock = threading.Lock()

    # Live Prototype Detection Pipeline
    model = SpatialBaseline(variance_threshold=8.0)
    window_buffer = deque(maxlen=80)  # ~2-second rolling buffer
    current_detected_zone = "CLEAR"
    current_detected_count = 0
    current_detected_motion = "EMPTY_ROOM"
    current_score = 0.0
    detected_history = []

    total_records = 0
    start_time = time.time()

    def on_record(record: CSIRecord):
        nonlocal total_records
        with write_lock:
            window_buffer.append(record)

            # Dynamic Prototype Decision vs Manual Override
            if args.zones is not None:
                active_zones = args.zones
                active_zone = args.zone if args.zone is not None else (args.zones.split(',')[0] if ',' in args.zones else args.zones)
                active_count = args.count if args.count is not None else len([z.strip() for z in args.zones.split(',') if z.strip()])
            else:
                active_zone = args.zone if args.zone is not None else current_detected_zone
                active_zones = active_zone
                active_count = args.count if args.count is not None else current_detected_count

            active_motion = args.motion_state if args.motion_state is not None else current_detected_motion

            row = [
                f"{record.timestamp:.4f}",
                record.receiver_id,
                record.tx_id or "UNKNOWN",
                record.source_mac,
                record.rssi if record.rssi is not None else "",
                f"{record.rate_hz:.1f}" if record.rate_hz is not None else "",
                active_count,
                active_zone,
                active_zones,
                active_motion,
                args.room_id
            ] + [f"{a:.2f}" for a in record.amplitudes[:64]]
            writer.writerow(row)
            total_records += 1

    manager = MultiSerialManager(config, on_record)
    manager.start_all()

    try:
        while time.time() - start_time < args.duration:
            elapsed = time.time() - start_time

            # Update live prototype detection from recent multi-link packet snapshot
            snapshot = list(window_buffer)
            if len(snapshot) >= 8:
                feats = extract_link_features(snapshot)
                pred = model.predict(feats, len(feats), signal_ok=True)
                current_detected_zone = pred.get("zone", "CLEAR")
                current_detected_count = pred.get("count", 0)
                current_detected_motion = "DYNAMIC" if current_detected_count > 0 else "EMPTY_ROOM"
                scores = [f.get("csi_variance", 0.0) for f in feats]
                current_score = round(max(scores) if scores else 0.0, 1)
                detected_history.append((current_detected_zone, current_detected_count))

            health = manager.get_health()
            rates_str = " | ".join([f"{rx}: {h['aggregate_rate_hz']}Hz" for rx, h in health.items()])
            status_text = f"PROTOTYPE: {current_detected_count} Person(s) in {current_detected_zone} (var: {current_score})"
            print(f"\r    [RECORDING {elapsed:4.1f}s / {args.duration:4.1f}s] {status_text} | {total_records} frames | {rates_str} ", end="", flush=True)
            time.sleep(0.35)
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user.")
    finally:
        manager.stop_all()
        csv_file.close()

    # Determine dominant detected zone & count for session metadata
    actual_duration = round(time.time() - start_time, 2)
    if detected_history:
        dominant_zone = Counter([h[0] for h in detected_history]).most_common(1)[0][0]
        dominant_count = Counter([h[1] for h in detected_history]).most_common(1)[0][0]
    else:
        dominant_zone = "CLEAR"
        dominant_count = 0
    final_zone = args.zone if args.zone is not None else (args.zones.split(',')[0] if args.zones else dominant_zone)
    final_count = args.count if args.count is not None else (len(args.zones.split(',')) if args.zones else dominant_count)
    final_motion = args.motion_state if args.motion_state is not None else ("DYNAMIC" if final_count > 0 else "EMPTY_ROOM")
    final_zones = args.zones if args.zones is not None else final_zone

    metadata_payload = {
        "session_id": session_clean,
        "display_name": session_clean,
        "source_type": "hardware_recorded_multilink",
        "provenance": "hardware_recorded_multilink",
        "format": "CSV_RAW_CSI_64",
        "room_id": args.room_id,
        "operator_id": args.operator_id,
        "ground_truth_count": final_count,
        "ground_truth_zone": final_zone,
        "ground_truth_zones": final_zones,
        "motion_state": final_motion,
        "duration_seconds": actual_duration,
        "total_records_captured": total_records,
        "auto_detected": is_auto,
        "is_manual_ground_truth": not is_auto,
        "provenance_note": "Verified manual ground truth" if not is_auto else "Live prototype autonomous heuristic estimation (unverified ground truth)",
        "timestamp_start": start_time,
        "timestamp_end": time.time(),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "notes": args.notes,
        "csv_filename": session_log_file.name,
        "description": f"Live hardware multi-link CSI capture. {'Manual GT' if not is_auto else 'Prototype detected'} {final_count} person(s) in {final_zone}, {actual_duration}s duration."
    }
    meta_log_file.write_text(json.dumps(metadata_payload, indent=2), encoding="utf-8")
    invalidate_recordings_cache()

    print(f"\n\n[+] Completed Successfully!")
    print(f"    - Captured:  {total_records} frames in {actual_duration}s")
    print(f"    - Detection: Dominant {final_count} Person(s) in Zone {final_zone}")
    print(f"    - Saved CSV: {session_log_file.name}")
    print(f"    - Metadata:  {meta_log_file.name}")
    print(f"[+] Added directly to WiMotion 2.0 Recorded Replay list! Ready for instant playback.\n")


if __name__ == "__main__":
    main()

