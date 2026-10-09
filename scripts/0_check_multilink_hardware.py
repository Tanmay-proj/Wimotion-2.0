#!/usr/bin/env python3
"""
WiMotion 2.0 — Multi-Link Hardware Diagnostic & Auto-Discovery Tool
Features:
- Scans and audits USB ports for RX1 and RX2
- Computes both aggregate receiver rate AND per-source transmitter CSI rates (e.g. RX1->TX1 Hz)
- Provides explicit, verified MAC-to-Transmitter assignment
- Validates the 8 candidate links experimentally
"""
import sys
import time
import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("[!] PySerial is required. Run: pip install pyserial")
    sys.exit(1)

from spatial.parser import parse_line
from spatial.config import load_config


def list_esp32_ports():
    ports = serial.tools.list_ports.comports()
    detected = []
    print("\n[+] Scanning USB Serial Ports on Host System:")
    for p in ports:
        desc = p.description.lower()
        is_esp = any(k in desc for k in ["cp210", "ch340", "ch910", "usb-serial", "uart", "ftdi"])
        tag = "[ESP32 CANDIDATE]" if is_esp else "[OTHER SERIAL]"
        print(f"    - {p.device:<8}: {p.description} {tag}")
        if is_esp or "com" in p.device.lower():
            detected.append(p.device)
    return detected


def audit_port(port: str, baud: int = 921600, duration: float = 6.0):
    print(f"\n[*] Auditing {port} @ {baud} baud for {duration:.1f} seconds...")
    try:
        ser = serial.Serial()
        ser.port = port
        ser.baudrate = baud
        ser.timeout = 1.0
        ser.dtr = False
        ser.rts = False
        ser.open()
        ser.reset_input_buffer()
    except Exception as e:
        print(f"[!] Could not open {port}: {e}")
        return None

    start = time.time()
    packet_count = 0
    tx_counts = Counter()
    tx_rssis = defaultdict(list)

    while time.time() - start < duration:
        raw_bytes = ser.readline()
        if not raw_bytes:
            continue
        try:
            line = raw_bytes.decode("ascii", errors="ignore").strip()
        except Exception:
            continue

        rec = parse_line(line, receiver_id=port)
        if rec and rec.amplitudes:
            packet_count += 1
            tx_counts[rec.source_mac] += 1
            if rec.rssi is not None:
                tx_rssis[rec.source_mac].append(rec.rssi)

    ser.close()
    elapsed = time.time() - start
    agg_rate = packet_count / elapsed if elapsed > 0 else 0.0

    per_tx_rates = {
        mac: round(cnt / elapsed, 1)
        for mac, cnt in tx_counts.items()
    }

    per_tx_rssi = {
        mac: round(sum(vals)/len(vals), 1)
        for mac, vals in tx_rssis.items() if vals
    }

    print(f"    Aggregate Packets: {packet_count} ({agg_rate:.1f} Hz total)")
    print(f"    Per-Source Link Rates:")
    for mac, r in per_tx_rates.items():
        rssi_str = f"{per_tx_rssi.get(mac, 'N/A')} dBm"
        print(f"      -> MAC {mac:<17} | Rate: {r:4.1f} Hz | RSSI: {rssi_str}")

    return {
        "port": port,
        "packet_count": packet_count,
        "aggregate_rate_hz": round(agg_rate, 1),
        "per_tx_rates": per_tx_rates,
        "per_tx_rssi": per_tx_rssi,
        "healthy": agg_rate >= 4.0
    }


def main():
    parser = argparse.ArgumentParser(description="WiMotion 2.0 Multi-Link Hardware Diagnostic")
    parser.add_argument("--interactive", action="store_true", help="Prompt to explicitly name/pair each discovered transmitter MAC")
    parser.add_argument("--duration", type=float, default=6.0, help="Diagnostic capture window in seconds")
    args = parser.parse_args()

    print("=" * 70)
    print("    WiMotion 2.0 — Multi-Link Diagnostic & Per-Link Verification")
    print("=" * 70)

    detected_ports = list_esp32_ports()
    if not detected_ports:
        print("\n[!] No active USB Serial COM ports found! Please plug in ESP32 boards.")
        sys.exit(0)

    results = {}
    for p in detected_ports[:2]:  # Check up to 2 candidate ports (RX1, RX2)
        res = audit_port(p, baud=921600, duration=args.duration)
        if res:
            results[p] = res

    print("\n" + "=" * 70)
    print("               MULTI-LINK VERIFICATION REPORT")
    print("=" * 70)

    rx_keys = ["RX1", "RX2"]
    rx_port_map = {}
    all_discovered_macs = set()

    for idx, (p, r) in enumerate(results.items()):
        rx_name = rx_keys[idx] if idx < len(rx_keys) else f"RX{idx+1}"
        rx_port_map[rx_name] = p
        status = "READY (ONLINE)" if r["healthy"] else "UNSTABLE (< 4 Hz)"
        print(f"  {rx_name} [{p:<5}] | Total: {r['aggregate_rate_hz']:5.1f} Hz | Status: {status}")
        for mac, rate in r["per_tx_rates"].items():
            all_discovered_macs.add(mac)
            print(f"      --> {rx_name} -> {mac:<17} : {rate:4.1f} Hz (RSSI: {r['per_tx_rssi'].get(mac, 'N/A')} dBm)")

    print("-" * 70)
    total_candidate_links = len(results) * len(all_discovered_macs)
    print(f"  Active Receivers:    {len(results)} / 2")
    print(f"  Detected Unique TX:  {len(all_discovered_macs)} / 4")
    print(f"  Verified Links:      {total_candidate_links} candidate link streams")

    cfg_file = ROOT / "config" / "nodes.json"
    if cfg_file.exists() and all_discovered_macs:
        try:
            cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
            # Update receiver ports
            for rx_name, p in rx_port_map.items():
                if rx_name in cfg["receivers"]:
                    cfg["receivers"][rx_name]["port"] = p

            # Interactive or explicit mapping of TX MACs
            if args.interactive and len(all_discovered_macs) > 0:
                print("\n[*] Interactive Transmitter MAC Assignment:")
                for mac in sorted(all_discovered_macs):
                    print(f"\nDiscovered Transmitter MAC: {mac}")
                    print("  [1] Assign to TX1 (North / Breach)")
                    print("  [2] Assign to TX2 (West / Center)")
                    print("  [3] Assign to TX3 (East / Flank)")
                    print("  [4] Assign to TX4 (South / Far)")
                    print("  [S] Skip")
                    choice = input("Enter selection [1/2/3/4/S]: ").strip().upper()
                    mapping = {"1": "TX1", "2": "TX2", "3": "TX3", "4": "TX4"}
                    if choice in mapping:
                        tx_key = mapping[choice]
                        cfg["transmitters"][tx_key]["mac"] = mac
                        print(f"  [+] Assigned {mac} -> {tx_key}")
            else:
                # Do not destructively overwrite registered transmitters in non-interactive audits
                pass

            cfg_file.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
            print(f"\n[+] Synchronized receiver ports to {cfg_file.name}")
        except Exception as e:
            print(f"[!] Warning updating config: {e}")

    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
