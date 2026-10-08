#!/usr/bin/env python3
"""
WiMotion 2.0 — Multi-Link Hardware Diagnostic & Auto-Discovery Tool
Scans all connected COM ports, listens for raw CSI streams from RX1 & RX2,
identifies active transmitter MAC addresses, measures line rates,
and optionally updates config/nodes.json automatically!
"""
import sys
import time
import json
from pathlib import Path
from collections import defaultdict, Counter

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
    print(f"\n[*] Auditing {port} @ {baud} baud for {duration} seconds...")
    try:
        ser = serial.Serial(port, baud, timeout=1.0)
        ser.reset_input_buffer()
    except Exception as e:
        print(f"[!] Could not open {port}: {e}")
        return None

    start = time.time()
    packet_count = 0
    tx_macs = Counter()
    rssis = []

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
            tx_macs[rec.source_mac] += 1
            if rec.rssi is not None:
                rssis.append(rec.rssi)

    ser.close()
    elapsed = time.time() - start
    rate = packet_count / elapsed if elapsed > 0 else 0.0

    print(f"    Total CSI Packets: {packet_count}")
    print(f"    Measured Rate:     {rate:.1f} Hz (Min Quality Gate: 4.0 Hz)")
    print(f"    Average RSSI:      {sum(rssis)/len(rssis):.1f} dBm" if rssis else "    Average RSSI:      N/A")
    print(f"    Detected TX MACs:  {dict(tx_macs)}")

    return {
        "port": port,
        "packet_count": packet_count,
        "rate_hz": round(rate, 1),
        "tx_macs": list(tx_macs.keys()),
        "healthy": rate >= 4.0
    }


def main():
    print("=" * 65)
    print("    WiMotion 2.0 — Multi-Link Hardware Diagnostic & Discovery")
    print("=" * 65)

    detected_ports = list_esp32_ports()
    if not detected_ports:
        print("\n[!] No active USB Serial COM ports found! Please plug in ESP32 boards.")
        sys.exit(0)

    results = {}
    for p in detected_ports[:2]:  # Check first 2 candidate ports (RX1, RX2)
        res = audit_port(p, baud=921600, duration=5.0)
        if res:
            results[p] = res

    print("\n" + "=" * 65)
    print("               SUMMARY DIAGNOSTIC AUDIT REPORT")
    print("=" * 65)
    all_healthy = True
    discovered_macs = set()

    for p, r in results.items():
        status = "READY (ONLINE)" if r["healthy"] else "UNSTABLE (< 4 Hz)"
        print(f"  Port {p:<8} | Rate: {r['rate_hz']:5.1f} Hz | Status: {status}")
        for mac in r["tx_macs"]:
            discovered_macs.add(mac)
            print(f"    -> Heard Transmitter MAC: {mac}")
        if not r["healthy"]:
            all_healthy = False

    print("-" * 65)
    if all_healthy and len(results) >= 2:
        print("[+] SUCCESS: Dual-Receiver hardware link is fully OPERATIONAL!")
    elif all_healthy and len(results) == 1:
        print("[*] NOTICE: 1 Receiver is operational. Plug in 2nd Receiver for Dual-Link.")
    else:
        print("[!] WARNING: Some ports are not receiving steady 20 Hz CSI.")

    # Auto-update config/nodes.json if requested
    cfg_file = ROOT / "config" / "nodes.json"
    if cfg_file.exists() and len(results) >= 1:
        print(f"\n[*] Discovered {len(discovered_macs)} unique transmitter MAC addresses.")
        ports_list = list(results.keys())
        try:
            cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
            if len(ports_list) >= 1:
                cfg["receivers"]["RX1"]["port"] = ports_list[0]
            if len(ports_list) >= 2:
                cfg["receivers"]["RX2"]["port"] = ports_list[1]

            macs_list = list(discovered_macs)
            for idx, tx_key in enumerate(["TX1", "TX2", "TX3", "TX4"]):
                if idx < len(macs_list):
                    cfg["transmitters"][tx_key]["mac"] = macs_list[idx]

            cfg_file.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
            print(f"[+] Automatically updated {cfg_file.name} with discovered hardware ports & MACs!")
        except Exception as e:
            print(f"[!] Could not auto-update config: {e}")

    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
