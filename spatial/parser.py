import json
import time
import numpy as np
from typing import Optional

from .types import CSIRecord


def parse_line(line: str, receiver_id: str) -> Optional[CSIRecord]:
    """
    Parses a single stream line from either:
    1. JSON formatted simulation/test line
    2. Real ESP32-CSI-Tool raw serial output: CSI_DATA,type,mac,rssi,...[I0 Q0 I1 Q1 ...]
    """
    if not line:
        return None

    line = line.strip()
    if not line:
        return None

    # ----------------------------------------------------
    # Mode 1: JSON format (Simulation / Replay / IPC)
    # ----------------------------------------------------
    if line.startswith("{"):
        try:
            data = json.loads(line)
            return CSIRecord(
                timestamp=float(data.get("timestamp", time.time())),
                receiver_id=receiver_id,
                source_mac=str(data["source_mac"]).upper(),
                rssi=float(data["rssi"]) if data.get("rssi") is not None else None,
                amplitudes=[float(x) for x in data["amplitudes"]],
                rate_hz=float(data["rate_hz"]) if data.get("rate_hz") is not None else None,
                tx_id=data.get("tx_id"),
                monotonic_time=float(data.get("monotonic_time", time.monotonic()))
            )
        except Exception:
            return None

    # ----------------------------------------------------
    # Mode 2: Real ESP32-CSI-Tool Hardware Output
    # Format: CSI_DATA,STA,MAC,RSSI,rate,sig_mode,...[I0 Q0 I1 Q1 ...]
    # ----------------------------------------------------
    if line.startswith("CSI_DATA"):
        try:
            bracket_start = line.index("[")
            bracket_end = line.index("]")
        except ValueError:
            return None

        metadata_part = line[:bracket_start].rstrip(",")
        csi_part = line[bracket_start + 1:bracket_end].strip()

        meta_fields = [f.strip() for f in metadata_part.split(",")]
        if len(meta_fields) < 25 or meta_fields[0] != "CSI_DATA":
            return None

        # Field 2: Source MAC address
        source_mac = meta_fields[2].upper() if len(meta_fields) > 2 else "UNKNOWN"
        # Field 3: RSSI
        try:
            rssi_val = float(meta_fields[3]) if len(meta_fields) > 3 and meta_fields[3] else None
        except ValueError:
            rssi_val = None

        # Unified host arrival timestamp ensures cross-receiver clock synchronization
        ts = time.time()
        mono_ts = time.monotonic()

        try:
            csi_raw = [int(x) for x in csi_part.split() if x.strip()]
        except ValueError:
            return None

        # Need at least 128 integers for 64 complex subcarriers
        if len(csi_raw) < 128:
            return None

        # Compute subcarrier amplitudes: sqrt(I^2 + Q^2)
        amplitudes = []
        for i in range(0, min(128, len(csi_raw)), 2):
            I = csi_raw[i]
            Q = csi_raw[i + 1]
            amp = float(np.sqrt(I**2 + Q**2))
            amplitudes.append(round(amp, 4))

        return CSIRecord(
            timestamp=ts,
            receiver_id=receiver_id,
            source_mac=source_mac,
            rssi=rssi_val,
            amplitudes=amplitudes,
            rate_hz=None,
            tx_id=None,
            monotonic_time=mono_ts
        )

    return None
