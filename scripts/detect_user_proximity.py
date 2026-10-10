#!/usr/bin/env python3
"""
WiMotion 2.0 — Dual-Receiver Real-Time Spatial Proximity & Sector Localizer
Listens simultaneously to RX1 (COM8) and RX2 (COM9), analyzes the 8-link
CSI subcarrier amplitude flutter and variance across all 4 TX nodes,
and determines which transmitter the user is closest to.
"""
import sys
import time
import json
import threading
from pathlib import Path
from collections import defaultdict
import numpy as np
import serial

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from spatial.parser import parse_line
from spatial.config import load_config, build_mac_map


def main():
    config = load_config()
    mac_map = build_mac_map(config)
    
    rx_ports = {
        rx_id: cfg["port"]
        for rx_id, cfg in config.receivers.items()
        if cfg["port"] and not cfg["port"].upper().startswith("COM_OFFLINE")
    }

    print("=" * 75)
    print("      WiMotion 2.0 — Dual-Receiver 8-Link Spatial Proximity Radar")
    print(f"      Monitoring Ports: {rx_ports}")
    print(f"      Target Transmitters: {list(config.transmitters.keys())}")
    print("=" * 75)

    link_records = defaultdict(list)
    lock = threading.Lock()
    running = True

    def reader(rx_id, port):
        nonlocal running
        try:
            s = serial.Serial()
            s.port = port
            s.baudrate = 921600
            s.timeout = 0.5
            s.dtr = False
            s.rts = False
            s.open()
            print(f"[+] {rx_id} ({port}): Serial port opened successfully.")
            
            while running:
                line_bytes = s.readline()
                if not line_bytes:
                    continue
                line = line_bytes.decode("ascii", errors="ignore").strip()
                record = parse_line(line, rx_id)
                if record:
                    tx_id = mac_map.get(record.source_mac, "UNKNOWN")
                    if tx_id != "UNKNOWN":
                        record.tx_id = tx_id
                        with lock:
                            link = f"{rx_id}-{tx_id}"
                            link_records[link].append(record)
            s.close()
        except Exception as e:
            print(f"[!] {rx_id} ({port}) error: {e}")

    threads = [threading.Thread(target=reader, args=(rx, port), daemon=True) for rx, port in rx_ports.items()]
    for t in threads:
        t.start()

    scan_duration = 6.0
    print(f"\n[*] Scanning live multi-link RF field for {scan_duration:.0f} seconds...")
    t0 = time.time()
    for sec in range(int(scan_duration), 0, -1):
        time.sleep(1.0)
        sys.stdout.write(f"\r    [SCANNING] {sec} seconds remaining... ")
        sys.stdout.flush()

    running = False
    time.sleep(0.4)
    print("\n\n" + "=" * 75)
    print("                      8-LINK TELEMETRY & SPECTRUM AUDIT")
    print("=" * 75)

    tx_variances = defaultdict(list)
    tx_rssi = defaultdict(list)

    for rx_id in sorted(rx_ports.keys()):
        print(f"\n--- {rx_id} Receiver Stream ---")
        for tx_id in sorted(config.transmitters.keys()):
            link = f"{rx_id}-{tx_id}"
            records = link_records[link]
            count = len(records)
            rate = count / scan_duration

            if count >= 10:
                # Build (N, 64) amplitude matrix
                amps_matrix = np.array([r.amplitudes[:64] for r in records])
                rssi_list = [r.rssi for r in records if r.rssi is not None]
                avg_rssi = np.mean(rssi_list) if rssi_list else -99.0

                # Spatial Metric: Mean temporal variance across active subcarriers (excluding nulls)
                # Subcarriers with dynamic multipath have high temporal variance
                subcarrier_vars = np.var(amps_matrix, axis=0)
                # Ignore zeroed/pilot subcarriers
                active_vars = subcarrier_vars[subcarrier_vars > 1e-4]
                mean_var = float(np.mean(active_vars)) if len(active_vars) > 0 else 0.0

                tx_variances[tx_id].append(mean_var)
                tx_rssi[tx_id].append(avg_rssi)

                print(f"  {link:<8} | {count:>4} pkts ({rate:4.1f} Hz) | RSSI: {avg_rssi:5.1f} dBm | CSI Variance: {mean_var:7.2f}")
            else:
                print(f"  {link:<8} | {count:>4} pkts ({rate:4.1f} Hz) | [LOW PACKETS / WEAK SIGNAL]")

    print("\n" + "=" * 75)
    print("             TRANSMITTER PERTURBATION & PROXIMITY RANKING")
    print("=" * 75)

    ranked = []
    for tx_id in sorted(config.transmitters.keys()):
        v_list = tx_variances.get(tx_id, [])
        r_list = tx_rssi.get(tx_id, [])
        # Combined disturbance score across both receivers
        combined_var = float(np.sum(v_list)) if v_list else 0.0
        avg_rssi = float(np.mean(r_list)) if r_list else -99.0
        ranked.append({
            "tx": tx_id,
            "variance": combined_var,
            "rssi": avg_rssi,
            "rx_count": len(v_list)
        })

    # Sort descending by variance (human body in Fresnel zone maximizes CSI variance)
    ranked.sort(key=lambda x: x["variance"], reverse=True)

    max_var = max((x["variance"] for x in ranked), default=1.0)
    for rank, item in enumerate(ranked, 1):
        bar_len = int(35 * (item["variance"] / max(max_var, 0.001)))
        bar = "#" * max(1, bar_len)
        print(f"  #{rank}  {item['tx']:<4} | Combined Flutter: {item['variance']:7.2f} | RSSI: {item['rssi']:5.1f} dBm | {bar}")

    print("=" * 75)
    if ranked:
        leader = ranked[0]
        runner_up = ranked[1] if len(ranked) > 1 else None
        
        print(f"\n  [>>>] TARGET LOCATION DETECTED:")
        print(f"     => Tu abhi **{leader['tx']}** ke sabse zyada paas hai!")
        if runner_up:
            delta_ratio = leader['variance'] / max(runner_up['variance'], 0.001)
            print(f"     => Perturbation Margin: {delta_ratio:.1f}x higher than #{runner_up['tx']}")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    main()
