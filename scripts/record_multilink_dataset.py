#!/usr/bin/env python3
"""
WiMotion 2.0 — Multi-Link Raw CSI Session Recorder
Records simultaneous streams across all active RX ports and TX links,
saving organized CSV datasets for model training & evaluation.
"""
import sys
import time
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
    parser.add_argument("--zone", type=str, default="Z1", choices=["Z1", "Z2", "Z3", "Z4", "CLEAR"], help="Ground truth zone")
    parser.add_argument("--count", type=int, default=1, help="Ground truth person count (0, 1, 2, 3)")
    parser.add_argument("--duration", type=float, default=20.0, help="Recording duration in seconds")
    args = parser.parse_args()

    config = load_config()
    out_dir = ROOT / "data" / "raw" / args.session
    out_dir.mkdir(parents=True, exist_ok=True)

    session_log_file = out_dir / f"multilink_data_{args.zone}_{args.count}P.csv"
    print(f"\n[*] Starting Multi-Link Session Recording:")
    print(f"    Session ID:       {args.session}")
    print(f"    Ground Truth:     {args.count} Person(s) in Zone {args.zone}")
    print(f"    Duration:         {args.duration} seconds")
    print(f"    Output File:      {session_log_file}")

    fieldnames = [
        "timestamp", "receiver", "tx", "source_mac", "rssi", 
        "rate_hz", "ground_truth_count", "ground_truth_zone"
    ] + [f"sub_{i}" for i in range(64)]

    csv_file = open(session_log_file, "w", newline="", encoding="utf-8")
    writer = csv.writer(csv_file)
    writer.writerow(fieldnames)

    total_records = 0

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
            args.zone
        ] + [f"{a:.2f}" for a in record.amplitudes[:64]]
        writer.writerow(row)
        total_records += 1

    manager = MultiSerialManager(config, on_record)
    manager.start_all()

    start_t = time.time()
    try:
        while time.time() - start_t < args.duration:
            elapsed = time.time() - start_t
            remain = max(0.0, args.duration - elapsed)
            health = manager.get_health()
            rates_str = " | ".join([f"{rx}: {h['rate_hz']}Hz" for rx, h in health.items()])
            print(f"\r    [RECORDING] {elapsed:4.1f}s / {args.duration:4.1f}s | {total_records} frames | {rates_str} ", end="", flush=True)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user.")
    finally:
        manager.stop_all()
        csv_file.close()

    print(f"\n[+] Completed! Recorded {total_records} multi-link CSI frames to {session_log_file.name}\n")


if __name__ == "__main__":
    main()
