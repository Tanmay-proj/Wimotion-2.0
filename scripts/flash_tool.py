#!/usr/bin/env python3
"""
WiMotion 2.0 — Automated ESP32 Firmware Management & Flashing Utility
======================================================================
Provides interactive flashing and backups for:
  - Transmitter (STA mode)          -> firmware/tx/active_sta.bin
  - Master Receiver (AP mode)       -> firmware/rx/active_ap.bin
  - Passive Sniffer (Promiscuous)   -> firmware/rx_sniffer/passive.bin
  - Golden WiMotion v1 Backups      -> firmware/golden_*.bin
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import List, Optional

try:
    import serial.tools.list_ports
except ImportError:
    serial = None

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
FIRMWARE_DIR = WORKSPACE_ROOT / "firmware"
CONFIG_FILE = WORKSPACE_ROOT / "config" / "nodes.json"

TX_IMAGE = FIRMWARE_DIR / "tx" / "active_sta.bin"
RX_AP_IMAGE = FIRMWARE_DIR / "rx" / "active_ap.bin"
RX_SNIFFER_IMAGE = FIRMWARE_DIR / "rx_sniffer" / "passive.bin"
GOLDEN_TX_IMAGE = FIRMWARE_DIR / "golden_tx_sta.bin"
GOLDEN_RX_IMAGE = FIRMWARE_DIR / "golden_rx_ap.bin"

DEFAULT_BAUD = "460800"
FLASH_SIZE = "0x6A000"

# Check for native ESP-IDF v4.3 installation
IDF_DIR = Path(r"E:\Espressif")
IDF_PYTHON = IDF_DIR / "python_env" / "idf4.3_py3.8_env" / "Scripts" / "python.exe"
IDF_ESPTOOL_SCRIPT = IDF_DIR / "frameworks" / "esp-idf-v4.3.4" / "components" / "esptool_py" / "esptool" / "esptool.py"

USE_IDF_ESPTOOL = False
HAS_IDF_ENV = IDF_PYTHON.exists() and IDF_ESPTOOL_SCRIPT.exists()


def ensure_firmware_dir() -> None:
    FIRMWARE_DIR.mkdir(parents=True, exist_ok=True)


def list_com_ports() -> List[str]:
    if serial is None:
        return []
    ports = [p.device for p in serial.tools.list_ports.comports()]
    return sorted(ports)


def select_com_port(prompt_msg: str = "Select COM Port") -> Optional[str]:
    ports = list_com_ports()
    if not ports:
        print("[!] No active COM ports detected. Please connect your ESP32 via USB.")
        return None
    if len(ports) == 1:
        print(f"[*] Detected 1 active COM port: {ports[0]}")
        return ports[0]
    
    print(f"\n[*] Available COM Ports:")
    for idx, port in enumerate(ports, 1):
        print(f"    [{idx}] {port}")
    
    choice = input(f"{prompt_msg} [1-{len(ports)}]: ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(ports):
            return ports[idx]
    except ValueError:
        pass
    print("[!] Invalid selection.")
    return None


def run_esptool_cmd(args: List[str]) -> tuple[int, str]:
    if USE_IDF_ESPTOOL and HAS_IDF_ENV:
        cmd = [str(IDF_PYTHON), str(IDF_ESPTOOL_SCRIPT)] + args
    else:
        cmd = [sys.executable, "-m", "esptool"] + args
        
    print(f"\n[*] Executing: {' '.join(cmd)}")
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False
        )
        print(proc.stdout)
        return proc.returncode, proc.stdout
    except Exception as exc:
        print(f"[!] Subprocess execution error: {exc}")
        return -1, str(exc)


def read_mac_address(port: str) -> Optional[str]:
    ret, out = run_esptool_cmd(["--port", port, "read_mac"])
    if ret != 0:
        return None
    for line in out.splitlines():
        if "MAC:" in line:
            parts = line.split("MAC:")
            if len(parts) > 1:
                mac = parts[1].strip().upper()
                return mac
    return None


def dump_firmware(port: str, target_file: Path, role_name: str) -> bool:
    ensure_firmware_dir()
    print(f"\n" + "=" * 60)
    print(f"   DUMPING {role_name.upper()} FIRMWARE")
    print(f"   Port: {port} | Target: {target_file}")
    print("=" * 60)
    
    mac = read_mac_address(port)
    if mac:
        print(f"[*] Detected Node Hardware MAC: {mac}")
    
    ret, _ = run_esptool_cmd([
        "--port", port,
        "--baud", DEFAULT_BAUD,
        "read_flash", "0x0", FLASH_SIZE, str(target_file)
    ])
    
    if ret == 0 and target_file.exists():
        size_kb = target_file.stat().st_size / 1024
        print(f"\n[SUCCESS] Successfully dumped {role_name} firmware: {size_kb:.1f} KB")
        return True
    else:
        print(f"\n[FAILED] Dump failed for port {port}.")
        return False


def flash_firmware(port: str, source_file: Path, role_name: str, offset: str = "0x10000") -> bool:
    if not source_file.exists():
        print(f"[!] Source image not found: {source_file}")
        return False

    print(f"\n" + "=" * 60)
    print(f"   FLASHING ESP32 AS {role_name.upper()}")
    print(f"   Port: {port} | Image: {source_file}")
    print("=" * 60)

    mac = read_mac_address(port)
    if mac:
        print(f"[*] Target Board Silicon MAC: {mac}")

    # Determine bootloader and partition table if flashing sub-component
    sub_dir = source_file.parent
    bl = sub_dir / "bootloader.bin"
    pt = sub_dir / "partition-table.bin"
    
    if bl.exists() and pt.exists():
        flash_args = [
            "--port", port,
            "--baud", DEFAULT_BAUD,
            "write_flash",
            "--flash_mode", "dio",
            "--flash_freq", "40m",
            "--flash_size", "detect",
            "0x1000", str(bl),
            "0x8000", str(pt),
            "0x10000", str(source_file)
        ]
    else:
        flash_args = [
            "--port", port,
            "--baud", DEFAULT_BAUD,
            "write_flash",
            "--flash_mode", "dio",
            "--flash_freq", "40m",
            "--flash_size", "detect",
            offset, str(source_file)
        ]

    ret, _ = run_esptool_cmd(flash_args)

    if ret == 0:
        print(f"\n[SUCCESS] Successfully flashed ESP32 as {role_name}!")
        if mac and "tx" in role_name.lower():
            update_nodes_config(mac)
        return True
    else:
        print(f"\n[FAILED] Flashing failed on port {port}.")
        return False


def update_nodes_config(new_mac: str) -> None:
    if not CONFIG_FILE.exists():
        return
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        transmitters = cfg.get("transmitters", {})
        known_macs = [t.get("mac") for t in transmitters.values()]
        if new_mac not in known_macs:
            for tx_id, t_info in transmitters.items():
                if t_info.get("mac") in ["PENDING_DISCOVERY", ""]:
                    t_info["mac"] = new_mac
                    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                        json.dump(cfg, f, indent=2)
                    print(f"[*] Registered new MAC {new_mac} to {tx_id} in config/nodes.json")
                    break
    except Exception as exc:
        print(f"[!] Could not update config/nodes.json: {exc}")


def interactive_menu() -> None:
    global USE_IDF_ESPTOOL
    ensure_firmware_dir()
    while True:
        print("\n" + "=" * 65)
        print("        WiMotion 2.0 — ESP32 Automated Firmware Tool")
        print("=" * 65)
        active_tool = "Native ESP-IDF v4.3.4 (esptool v3.3)" if USE_IDF_ESPTOOL else "Python 3.10 (esptool v5.5)"
        print(f"  Active Toolchain: {active_tool}")
        print("-" * 65)
        print("  --- WiMotion 2.0 Fleet Flashing ---")
        print(f"  [1] Flash Transmitter STA           ({TX_IMAGE.name})")
        print(f"  [2] Flash Master AP Receiver (RX1)  ({RX_AP_IMAGE.name})")
        print(f"  [3] Flash Passive Sniffer (RX2)     ({RX_SNIFFER_IMAGE.name})")
        print("  --- Hardware Diagnostics & Tools ---")
        print("  [4] Identify connected ESP32 (Read MAC & Chip Info)")
        print("  [5] Scan active COM ports")
        print("  --- WiMotion v1 Golden Restores ---")
        print(f"  [6] Flash Golden v1 Transmitter     ({GOLDEN_TX_IMAGE.name})")
        print(f"  [7] Flash Golden v1 Receiver        ({GOLDEN_RX_IMAGE.name})")
        print("  [8] Exit")
        print("=" * 65)
        
        choice = input("Select an option [1-8]: ").strip()
        if choice == "1":
            port = select_com_port("Select COM port for Transmitter")
            if port: flash_firmware(port, TX_IMAGE, "TX (STA)")
        elif choice == "2":
            port = select_com_port("Select COM port for Master AP (RX1)")
            if port: flash_firmware(port, RX_AP_IMAGE, "RX1 (Master AP)")
        elif choice == "3":
            port = select_com_port("Select COM port for Passive Sniffer (RX2)")
            if port: flash_firmware(port, RX_SNIFFER_IMAGE, "RX2 (Passive Sniffer)")
        elif choice == "4":
            port = select_com_port("Select COM port to read")
            if port:
                mac = read_mac_address(port)
                if mac: print(f"\n[+] Silicon MAC: {mac}")
        elif choice == "5":
            ports = list_com_ports()
            print(f"\n[*] Active Ports: {ports if ports else 'None'}")
        elif choice == "6":
            port = select_com_port("Select COM port for Golden TX")
            if port: flash_firmware(port, GOLDEN_TX_IMAGE, "Golden TX", offset="0x0")
        elif choice == "7":
            port = select_com_port("Select COM port for Golden RX")
            if port: flash_firmware(port, GOLDEN_RX_IMAGE, "Golden RX", offset="0x0")
        elif choice == "8":
            break


if __name__ == "__main__":
    interactive_menu()
