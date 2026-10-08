"""WiMotion 2.0 ESP32 Firmware Management & Flashing Utility.

Enables cloning and flashing of ESP32-WROOM-32 boards without needing
manual compilation or complex IDF configuration.

Features:
1. Dual Toolchain Detection:
   - Native ESP-IDF v4.3.4 (at E:\\Espressif with esptool v3.3.2-dev)
   - Python 3.10 esptool (v5.5.0)
2. Dump Golden Images: Reads full 4MB flash from pre-flashed working boards
   (TX / active_sta, RX / active_ap) preserving exact ESP-IDF v4.3.4 compilation bit-for-bit.
3. Clone & Flash: Flashes blank boards with verified golden images in ~15 seconds.
4. Hardware MAC Identification: Automatically queries and registers the unique
   factory eFuse MAC address of every connected board.
5. Auto-update nodes.json: Registers discovered TX MACs into WiMotion 2.0 config.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

try:
    import serial.tools.list_ports
except ImportError:
    serial = None

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
FIRMWARE_DIR = WORKSPACE_ROOT / "firmware"
CONFIG_FILE = WORKSPACE_ROOT / "config" / "nodes.json"
TX_IMAGE = FIRMWARE_DIR / "golden_tx_sta.bin"
RX_IMAGE = FIRMWARE_DIR / "golden_rx_ap.bin"
DEFAULT_BAUD = "921600"
FLASH_SIZE = "0x400000"  # 4MB standard for ESP32-WROOM-32

# Check for native ESP-IDF v4.3 installation
IDF_DIR = Path(r"E:\Espressif")
IDF_PYTHON = IDF_DIR / "python_env" / "idf4.3_py3.8_env" / "Scripts" / "python.exe"
IDF_ESPTOOL_SCRIPT = IDF_DIR / "frameworks" / "esp-idf-v4.3.4" / "components" / "esptool_py" / "esptool" / "esptool.py"

USE_IDF_ESPTOOL = False
if IDF_PYTHON.exists() and IDF_ESPTOOL_SCRIPT.exists():
    HAS_IDF_ENV = True
else:
    HAS_IDF_ENV = False


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


def get_esptool_base_cmd() -> List[str]:
    global USE_IDF_ESPTOOL
    if USE_IDF_ESPTOOL and HAS_IDF_ENV:
        return [str(IDF_PYTHON), str(IDF_ESPTOOL_SCRIPT)]
    return [sys.executable, "-m", "esptool"]


def run_esptool_cmd(args: List[str]) -> tuple[int, str]:
    base_cmd = get_esptool_base_cmd()
    cmd = base_cmd + args
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
    print(f"   DUMPING {role_name.upper()} GOLDEN FIRMWARE (4MB Flash)")
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
        size_mb = target_file.stat().st_size / (1024 * 1024)
        print(f"\n[SUCCESS] Successfully dumped {role_name} firmware: {size_mb:.2f} MB")
        return True
    else:
        print(f"\n[FAILED] Dump failed for port {port}. Please check connection or BOOT button.")
        return False


def flash_firmware(port: str, source_file: Path, role_name: str) -> bool:
    if not source_file.exists():
        print(f"[!] Source image not found: {source_file}")
        print(f"    Please dump or provide the {role_name} golden image first.")
        return False

    print(f"\n" + "=" * 60)
    print(f"   FLASHING BLANK ESP32 AS {role_name.upper()}")
    print(f"   Port: {port} | Image: {source_file}")
    print("=" * 60)

    # 1. Read MAC before flashing
    mac = read_mac_address(port)
    if mac:
        print(f"[*] Target Board Silicon MAC: {mac}")

    # 2. Flash image
    ret, _ = run_esptool_cmd([
        "--port", port,
        "--baud", DEFAULT_BAUD,
        "write_flash",
        "--flash_mode", "dio",
        "--flash_freq", "40m",
        "--flash_size", "detect",
        "0x0", str(source_file)
    ])

    if ret == 0:
        print(f"\n[SUCCESS] Successfully flashed ESP32 as {role_name}!")
        if mac and role_name.lower() == "tx":
            print(f"[*] Node Silicon MAC is: {mac}")
            update_nodes_config(mac)
        return True
    else:
        print(f"\n[FAILED] Flashing failed on port {port}.")
        print("    Tip: If connection fails, press and hold the 'BOOT' button on ESP32 while connecting.")
        return False


def update_nodes_config(new_mac: str) -> None:
    if not CONFIG_FILE.exists():
        return
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        tx_nodes = cfg.get("tx_nodes", [])
        known_macs = [node.get("mac") for node in tx_nodes]
        if new_mac not in known_macs:
            for node in tx_nodes:
                if node.get("mac") == "PENDING_DISCOVERY":
                    node["mac"] = new_mac
                    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                        json.dump(cfg, f, indent=2)
                    print(f"[*] Registered new MAC {new_mac} to node {node.get('id')} in config/nodes.json")
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
        if HAS_IDF_ENV:
            print(f"  Detected IDF Path: E:\\Espressif\\frameworks\\esp-idf-v4.3.4")
        tx_status = "READY" if TX_IMAGE.exists() else "MISSING (Needs dump)"
        rx_status = "READY" if RX_IMAGE.exists() else "MISSING (Needs dump)"
        print(f"  Golden TX Image: {tx_status} ({TX_IMAGE.name})")
        print(f"  Golden RX Image: {rx_status} ({RX_IMAGE.name})")
        print("-" * 65)
        print("  [1] Dump/Backup WORKING Transmitter board (AP/STA golden image)")
        print("  [2] Dump/Backup WORKING Receiver board (CSI-RX golden image)")
        print("  [3] Flash BLANK board as Transmitter (TX)")
        print("  [4] Flash BLANK board as Receiver (RX)")
        print("  [5] Identify connected ESP32 (Read MAC & Chip Info)")
        print("  [6] Scan active COM ports")
        if HAS_IDF_ENV:
            toggle_label = "Switch to Python 3.10 esptool" if USE_IDF_ESPTOOL else "Switch to Native IDF v4.3 esptool"
            print(f"  [7] {toggle_label}")
            print("  [8] Exit")
        else:
            print("  [7] Exit")
        print("=" * 65)
        
        choice = input("Select an option: ").strip()
        if choice == "1":
            port = select_com_port("Select COM port of WORKING TX board")
            if port:
                dump_firmware(port, TX_IMAGE, "TX")
        elif choice == "2":
            port = select_com_port("Select COM port of WORKING RX board")
            if port:
                dump_firmware(port, RX_IMAGE, "RX")
        elif choice == "3":
            port = select_com_port("Select COM port of BLANK board to flash as TX")
            if port:
                flash_firmware(port, TX_IMAGE, "TX")
        elif choice == "4":
            port = select_com_port("Select COM port of BLANK board to flash as RX")
            if port:
                flash_firmware(port, RX_IMAGE, "RX")
        elif choice == "5":
            port = select_com_port("Select COM port of ESP32 board to inspect")
            if port:
                run_esptool_cmd(["--port", port, "chip_id"])
                mac = read_mac_address(port)
                if mac:
                    print(f"\n[+] Chip MAC Address: {mac}")
        elif choice == "6":
            ports = list_com_ports()
            print(f"\n[*] Active COM ports: {ports if ports else 'None detected'}")
        elif choice == "7" and HAS_IDF_ENV:
            USE_IDF_ESPTOOL = not USE_IDF_ESPTOOL
            print(f"[*] Toolchain toggled to: {'IDF v4.3.4' if USE_IDF_ESPTOOL else 'Python 3.10'}")
        elif (choice == "7" and not HAS_IDF_ENV) or (choice == "8" and HAS_IDF_ENV):
            break
        else:
            print("[!] Invalid option.")


def main() -> None:
    parser = argparse.ArgumentParser(description="WiMotion 2.0 ESP32 Firmware Utility")
    parser.add_argument("--dump-tx", help="COM port to dump working TX board from")
    parser.add_argument("--dump-rx", help="COM port to dump working RX board from")
    parser.add_argument("--flash-tx", help="COM port to flash blank board as TX")
    parser.add_argument("--flash-rx", help="COM port to flash blank board as RX")
    parser.add_argument("--info", help="COM port to read MAC and chip info from")
    parser.add_argument("--use-idf", action="store_true", help="Force using native ESP-IDF v4.3 esptool")
    args = parser.parse_args()

    global USE_IDF_ESPTOOL
    if args.use_idf and HAS_IDF_ENV:
        USE_IDF_ESPTOOL = True

    ensure_firmware_dir()

    if args.dump_tx:
        dump_firmware(args.dump_tx, TX_IMAGE, "TX")
    elif args.dump_rx:
        dump_firmware(args.dump_rx, RX_IMAGE, "RX")
    elif args.flash_tx:
        flash_firmware(args.flash_tx, TX_IMAGE, "TX")
    elif args.flash_rx:
        flash_firmware(args.flash_rx, RX_IMAGE, "RX")
    elif args.info:
        run_esptool_cmd(["--port", args.info, "chip_id"])
        mac = read_mac_address(args.info)
        if mac:
            print(f"[+] Chip MAC Address: {mac}")
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
