#!/usr/bin/env python3
"""
WiMotion 2.0 — Multi-Link Raw CSI Session Recorder
Records simultaneous streams across all active RX ports and TX links,
saving organized CSV datasets along with comprehensive research metadata.
"""
import sys
import time
import json
import argparse
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from spatial.config import load_config
from spatial.serial_manager import MultiSerialManager
from spatial.types import CSIRecord


def main():
    parser = argparse.ArgumentParser(description="WiMotion 2.0 Multi-Link Dataset Recorder")
    parser.add_argument("--session", type=str, default="session_001", help="Session ID (e.g. session_001)")
    parser.add_argument("--room-id", type=str, default="ROOM_LAB_A", help="Room or Environment Identifier")
    parser.add_argument("--operator-id", type=str, default="OC_TANMAY", help="Operator or Cadet ID")
    parser.add_argument("--zone", type=str, default="Z1", choices=["Z1", "Z2", "Z3", "Z4", "CLEAR"], help="Ground truth zone")
    parser.add_argument("--count", type=int, default=1, help="Ground truth person count (0, 1, 2, 3)")
    parser.add_argument("--motion-state", type=str, default="DYNAMIC", choices=["DYNAMIC", "STATIC", "TRANSIT", "EMPTY"], help="Subject motion state")
    parser.add_argument("--duration", type=float, default=20.0, help="Recording duration in seconds")
    parser.add_argument("--notes", type=str, default="", help="Experimental observation notes")
    args = parser.parse_args()

    config = load_config()
    out_dir = ROOT / "data" / "raw" / args.session
    out_dir.mkdir(parents=True, exist_ok=True)

    session_log_file = out_dir / f"multilink_data_{args.zone}_{args.count}P_{args.motion_state.lower()}.csv"
    meta_log_file = out_dir / f"metadata_{args.zone}_{args.count}P.json"

    print(f"\n[*] Starting Multi-Link Session Recording:")
    print(f"    Session ID:       {args.session}")
    print(f"    Room / Env:       {args.room_id}")
    print(f"    Operator:         {args.operator_id}")
    print(f"    Ground Truth:     {args.count} Person(s) in Zone {args.zone} ({args.motion_state})")
    print(f"    Duration:         {args.duration} seconds")
    print(f"    Output CSV:       {session_log_file}")

    fieldnames = [
        "timestamp", "receiver", "tx", "source_mac", "rssi", 
        "rate_hz", "ground_truth_count", "ground_truth_zone", "motion_state", "room_id"
    ] + [f"sub_{i}" for i in range(64)]

    csv_file = open(session_log_file, "w", newline="", encoding="utf-8")
    writer = csv.writer(csv_file)
    writer.writerow(fieldnames)

    total_records = 0
    start_time = time.time()

    def on_record(record: CSIRecord):
        nonlocal total_records
        row = [
            f"{record.timestamp:.4f}",
            record.receiver_id,
            record.tx_id or "UNKNOWN",
            record.source_mac,
            record.rssi if record.rssi is not None else "",
            f"{record.rate_hz:.1f}" if record.rate_hz is not None else "",
            args.count,
            args.zone,
            args.motion_state,
            args.room_id
        ] + [f"{a:.2f}" for a in record.amplitudes[:64]]
        writer.writerow(row)
        total_records += 1

    manager = MultiSerialManager(config, on_record)
    manager.start_all()

    try:
        while time.time() - start_time < args.duration:
            elapsed = time.time() - start_time
            remain = max(0.0, args.duration - elapsed)
            health = manager.get_health()
            rates_str = " | ".join([f"{rx}: {h['aggregate_rate_hz']}Hz" for rx, h in health.items()])
            print(f"\r    [RECORDING] {elapsed:4.1f}s / {args.duration:4.1f}s | {total_records} frames | {rates_str} ", end="", flush=True)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user.")
    finally:
        manager.stop_all()
        csv_file.close()

    # Save scientific metadata companion JSON
    metadata_payload = {
        "session_id": args.session,
        "room_id": args.room_id,
        "operator_id": args.operator_id,
        "ground_truth_count": args.count,
        "ground_truth_zone": args.zone,
        "motion_state": args.motion_state,
        "duration_seconds": args.duration,
        "total_records_captured": total_records,
        "timestamp_start": start_time,
        "timestamp_end": time.time(),
        "notes": args.notes,
        "csv_filename": session_log_file.name
    }
    meta_log_file.write_text(json.dumps(metadata_payload, indent=2), encoding="utf-8")

    print(f"\n[+] Completed! Recorded {total_records} multi-link CSI frames to {session_log_file.name}")
    print(f"[+] Provenance metadata written to {meta_log_file.name}\n")


if __name__ == "__main__":
    main()
