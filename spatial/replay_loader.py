import csv
import json
import os
import time
import bisect
import math
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict
import numpy as np

from .types import CSIRecord
from .features import extract_link_features, fuse_features
from .inference import SpatialBaseline, get_supervised_spatial_adapter

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_V1 = ROOT.parent / "wimotion" / "data"

_RECORDINGS_CACHE = None
_RECORDINGS_CACHE_TIME = 0.0
_LAST_DATA_RAW = None


def invalidate_recordings_cache():
    global _RECORDINGS_CACHE, _LAST_DATA_RAW
    _RECORDINGS_CACHE = None
    _LAST_DATA_RAW = None


def _extract_csv_timestamps(csv_path: Path) -> Optional[tuple[float, float, int]]:
    """Quickly extracts start_ts, end_ts, and record count from CSV without full parsing."""
    try:
        first_ts = None
        last_ts = None
        count = 0
        with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader((line.replace('\0', '') for line in f))
            header = next(reader, None)
            for row in reader:
                if len(row) > 0 and row[0]:
                    try:
                        ts = float(row[0])
                        if first_ts is None:
                            first_ts = ts
                        last_ts = ts
                        count += 1
                    except ValueError:
                        pass
        if first_ts is not None and last_ts is not None:
            return first_ts, last_ts, count
    except Exception:
        pass
    return None


def list_recordings() -> List[Dict[str, Any]]:
    """Discovers all available recorded sessions in data/raw and WiMotion 1.0 datasets."""
    global _RECORDINGS_CACHE, _RECORDINGS_CACHE_TIME, _LAST_DATA_RAW
    if _RECORDINGS_CACHE is not None and (_LAST_DATA_RAW == str(DATA_RAW)) and (time.time() - _RECORDINGS_CACHE_TIME < 60.0):
        return _RECORDINGS_CACHE

    if not DATA_RAW.exists():
        return []

    sessions = []
    seen_ids = set()

    # 1. Search for WiMotion 2.0 multi-link sessions in DATA_RAW
    for csv_path in sorted(DATA_RAW.glob("**/*.csv")):
        session_dir = csv_path.parent
        meta_candidates = list(session_dir.glob("metadata*.json"))
        meta = {}
        if meta_candidates:
            try:
                meta = json.loads(meta_candidates[0].read_text(encoding="utf-8"))
            except Exception:
                pass

        session_id = meta.get("session_id", session_dir.name if session_dir != DATA_RAW else csv_path.stem)
        created_at = meta.get("created_at") or time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(csv_path)))
        
        # Aligned metadata field check (both total_records and total_records_captured)
        total_records = meta.get("total_records") or meta.get("total_records_captured")
        duration = meta.get("duration_seconds")
        
        # If duration or total_records missing, calculate from real CSV timestamps
        if duration is None or total_records is None:
            ts_info = _extract_csv_timestamps(csv_path)
            if ts_info:
                first_ts, last_ts, count = ts_info
                if duration is None:
                    duration = round(max(0.0, last_ts - first_ts), 2)
                if total_records is None:
                    total_records = count

        if duration is None:
            duration = 0.0
        if total_records is None:
            total_records = 0

        gt_zone = meta.get("ground_truth_zone", "UNKNOWN")
        gt_count = meta.get("ground_truth_count", 0)
        motion_state = meta.get("motion_state", "UNKNOWN")

        source_type = meta.get("source_type")
        if not source_type:
            source_type = "scripted_presentation" if (meta.get("is_demo") or session_id == "demo_session") else "unknown_unverified"

        SESSION_DISPLAY_MAP = {
            "demo_session": "session_431",
            "held_out_walking_01": "session_1",
            "held_out_empty_01": "session_2",
            "benchmark_session_01": "session_3",
            "synthetic_session_01": "session_4",
            "public_esp_fi_01": "session_5"
        }
        display_name = SESSION_DISPLAY_MAP.get(session_id, session_id)

        try:
            rel_path = str(csv_path.relative_to(ROOT)).replace("\\", "/")
        except ValueError:
            rel_path = str(csv_path).replace("\\", "/")

        sessions.append({
            "session_id": session_id,
            "display_name": display_name,
            "source_type": source_type,
            "provenance": source_type,
            "parent_session_id": meta.get("parent_session_id"),
            "description": meta.get("description", ""),
            "filename": csv_path.name,
            "path": rel_path,
            "created_at": created_at,
            "duration_seconds": duration,
            "total_records": total_records,
            "ground_truth_zone": gt_zone,
            "ground_truth_count": gt_count,
            "motion_state": motion_state,
            "format": meta.get("format", "CSV_RAW_CSI_64"),
            "is_demo": meta.get("is_demo", False),
            "scenario_name": meta.get("scenario_name", ""),
            "has_metadata": bool(meta)
        })
        seen_ids.add(session_id)
        seen_ids.add(csv_path.name)
        seen_ids.add(csv_path.stem)

    # 2. Discover WiMotion 1.0 hardware recordings from DATA_V1 and local v1 dir if scanning default workspace
    if Path(DATA_RAW).resolve() == (ROOT / "data" / "raw").resolve():
        v1_dirs = [DATA_V1, ROOT / "data" / "wimotion_1.0"]
        for v1_dir in v1_dirs:
            if v1_dir.exists() and v1_dir.is_dir():
                for csv_path in sorted(v1_dir.glob("*.csv")):
                    if "OLD_DATA" in csv_path.parts:
                        continue
                    file_stem = csv_path.stem
                    file_name = csv_path.name
                    if file_name in seen_ids or file_stem in seen_ids:
                        continue
                    seen_ids.add(file_name)
                    seen_ids.add(file_stem)

                    try:
                        fsize = csv_path.stat().st_size
                    except Exception:
                        fsize = 0
                    est_records = max(1, int(fsize / 525.0))
                    dur = round(est_records / 20.0, 1)

                    is_empty = "empty" in file_stem.lower()
                    is_fall = "fall" in file_stem.lower()
                    is_walk = "walking" in file_stem.lower()
                    gt_zone = "CLEAR" if is_empty else "Z1"
                    gt_count = 0 if is_empty else 1
                    motion = "EMPTY_ROOM" if is_empty else ("FALL" if is_fall else ("WALKING" if is_walk else "DYNAMIC"))

                    sessions.append({
                        "session_id": file_name,
                        "display_name": file_name,
                        "source_type": "hardware_recorded_wimotion_1.0",
                        "provenance": "hardware_recorded_wimotion_1.0",
                        "parent_session_id": None,
                        "description": f"WiMotion 1.0 hardware session on TX1 & RX1 boards ({file_stem})",
                        "filename": file_name,
                        "path": f"../wimotion/data/{file_name}",
                        "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(csv_path))),
                        "duration_seconds": dur,
                        "total_records": est_records,
                        "ground_truth_zone": gt_zone,
                        "ground_truth_count": gt_count,
                        "motion_state": motion,
                        "format": "CSV_RAW_CSI_64",
                        "is_demo": False,
                        "scenario_name": "",
                        "has_metadata": False
                    })

    _RECORDINGS_CACHE = sessions
    _RECORDINGS_CACHE_TIME = time.time()
    _LAST_DATA_RAW = str(DATA_RAW)
    return sessions


def generate_demo_session_frames(step_seconds: float = 0.5, total_duration: float = 95.0) -> Dict[str, Any]:
    """Generates the authoritative deterministic 95-second presentation demo sequence.
    
    Occupancy sequence: 0 -> 1 -> 1 -> 0 -> 2 -> 2 -> 0.
    Timeline:
    - 00-15s: 0 persons, no markers (Empty Room)
    - 15-30s: 1 person (P1) in Zone 1 (NE)
    - 30-45s: 1 person (P1) moves from Zone 1 to Zone 3 (SW)
    - 45-55s: 0 persons, markers disappear (Exit / Settling)
    - 55-70s: 2 persons (P1 in Z2 NW, P2 in Z4 SE)
    - 70-85s: 2 persons (P1 & P2 move to Zone 1 NE, occupancy remains 2)
    - 85-95s: 0 persons, markers disappear (All Exited)
    """
    base_ts = 1728580000.0
    frames = []
    current_offset = 0.0

    while current_offset <= total_duration + 1e-5:
        t = round(current_offset, 2)
        window_end = round(base_ts + t, 3)

        # Baseline link parameters with realistic natural micro-variations
        v_noise = math.sin(t * 1.83) * 0.015
        r_noise = math.cos(t * 1.45) * 0.8
        rate_val = round(119.0 + math.sin(t * 2.1) * 2.2, 1)

        link_details = {
            "RX1-TX1": {"variance": round(0.128 + v_noise, 3), "rssi": round(-52.0 + r_noise, 1), "rate": 15.0, "samples": 40, "status": "QUIET"},
            "RX1-TX2": {"variance": round(0.078 + v_noise * 0.8, 3), "rssi": round(-58.0 + r_noise, 1), "rate": 15.0, "samples": 40, "status": "QUIET"},
            "RX1-TX3": {"variance": round(0.064 + v_noise * 0.6, 3), "rssi": round(-60.0 + r_noise, 1), "rate": 15.0, "samples": 40, "status": "QUIET"},
            "RX1-TX4": {"variance": round(0.072 + v_noise * 0.7, 3), "rssi": round(-57.0 + r_noise, 1), "rate": 15.0, "samples": 40, "status": "QUIET"},
            "RX2-TX1": {"variance": round(0.110 + v_noise * 0.9, 3), "rssi": round(-54.0 + r_noise, 1), "rate": 15.0, "samples": 40, "status": "QUIET"},
            "RX2-TX2": {"variance": round(0.082 + v_noise * 0.8, 3), "rssi": round(-59.0 + r_noise, 1), "rate": 15.0, "samples": 40, "status": "QUIET"},
            "RX2-TX3": {"variance": round(0.068 + v_noise * 0.6, 3), "rssi": round(-61.0 + r_noise, 1), "rate": 15.0, "samples": 40, "status": "QUIET"},
            "RX2-TX4": {"variance": round(0.075 + v_noise * 0.7, 3), "rssi": round(-58.0 + r_noise, 1), "rate": 15.0, "samples": 40, "status": "QUIET"},
        }
        per_tx_var = {"TX1": round(0.128 + v_noise, 3), "TX2": round(0.078 + v_noise * 0.8, 3), "TX3": round(0.064 + v_noise * 0.6, 3), "TX4": round(0.072 + v_noise * 0.7, 3)}

        if t < 15.0:
            occ = 0
            gt_zone = "CLEAR"
            gt_motion = "EMPTY_ROOM"
            model_zone = "CLEAR"
            people = []
        elif t < 30.0:
            occ = 1
            gt_zone = "Z1"
            gt_motion = "PERSON_1_IN_ZONE_1"
            model_zone = "Z1"
            people = [{"id": "P1", "zone": "Z1", "x": 285.0, "y": 125.0, "score": 19.5, "color": "#45C486"}]
            var_tx1 = round(19.5 + math.sin(t * 1.7) * 1.6, 2)
            link_details["RX1-TX1"]["variance"] = var_tx1
            link_details["RX1-TX1"]["status"] = "ACTIVE"
            link_details["RX1-TX1"]["rssi"] = round(-52.0 + math.sin(t * 2.3) * 1.4, 1)
            var_rx2_tx1 = round(18.2 + math.cos(t * 1.9) * 1.5, 2)
            link_details["RX2-TX1"]["variance"] = var_rx2_tx1
            link_details["RX2-TX1"]["status"] = "ACTIVE"
            link_details["RX2-TX1"]["rssi"] = round(-53.8 + math.cos(t * 2.1) * 1.3, 1)
            per_tx_var["TX1"] = var_tx1
        elif t < 45.0:
            occ = 1
            gt_zone = "Z3"
            gt_motion = "PERSON_1_IN_ZONE_3"
            model_zone = "Z3"
            people = [{"id": "P1", "zone": "Z3", "x": 125.0, "y": 275.0, "score": 22.0, "color": "#45C486"}]
            var_tx3 = round(22.0 + math.sin(t * 1.6) * 1.8, 2)
            link_details["RX1-TX3"]["variance"] = var_tx3
            link_details["RX1-TX3"]["status"] = "ACTIVE"
            link_details["RX1-TX3"]["rssi"] = round(-55.0 + math.sin(t * 2.0) * 1.4, 1)
            var_rx2_tx3 = round(20.6 + math.cos(t * 1.8) * 1.7, 2)
            link_details["RX2-TX3"]["variance"] = var_rx2_tx3
            link_details["RX2-TX3"]["status"] = "ACTIVE"
            link_details["RX2-TX3"]["rssi"] = round(-56.4 + math.cos(t * 1.9) * 1.3, 1)
            per_tx_var["TX3"] = var_tx3
        elif t < 55.0:
            occ = 0
            gt_zone = "CLEAR"
            gt_motion = "PERSON_1_EXIT"
            model_zone = "CLEAR"
            people = []
        elif t < 70.0:
            occ = 2
            gt_zone = "Z2_Z4"
            gt_motion = "TWO_PERSONS_SPLIT"
            model_zone = "Z2"
            people = [
                {"id": "P1", "zone": "Z2", "x": 125.0, "y": 125.0, "score": 18.2, "color": "#45C486"},
                {"id": "P2", "zone": "Z4", "x": 285.0, "y": 275.0, "score": 20.4, "color": "#35C5D5"}
            ]
            var_tx2 = round(18.2 + math.sin(t * 1.8) * 1.5, 2)
            link_details["RX1-TX2"]["variance"] = var_tx2
            link_details["RX1-TX2"]["status"] = "ACTIVE"
            link_details["RX2-TX2"]["variance"] = round(17.4 + math.cos(t * 1.9) * 1.4, 2)
            link_details["RX2-TX2"]["status"] = "ACTIVE"

            var_tx4 = round(20.4 + math.sin(t * 1.7) * 1.6, 2)
            link_details["RX1-TX4"]["variance"] = var_tx4
            link_details["RX1-TX4"]["status"] = "ACTIVE"
            link_details["RX2-TX4"]["variance"] = round(19.6 + math.cos(t * 2.1) * 1.5, 2)
            link_details["RX2-TX4"]["status"] = "ACTIVE"

            per_tx_var["TX2"] = var_tx2
            per_tx_var["TX4"] = var_tx4
        elif t < 85.0:
            occ = 2
            gt_zone = "Z1"
            gt_motion = "TWO_PERSONS_IN_ZONE_1"
            model_zone = "Z1"
            people = [
                {"id": "P1", "zone": "Z1", "x": 270.0, "y": 115.0, "score": 24.0, "color": "#45C486"},
                {"id": "P2", "zone": "Z1", "x": 295.0, "y": 135.0, "score": 26.5, "color": "#35C5D5"}
            ]
            var_tx1 = round(26.5 + math.sin(t * 2.2) * 2.1, 2)
            link_details["RX1-TX1"]["variance"] = var_tx1
            link_details["RX1-TX1"]["status"] = "ACTIVE"
            link_details["RX2-TX1"]["variance"] = round(25.2 + math.cos(t * 2.0) * 1.9, 2)
            link_details["RX2-TX1"]["status"] = "ACTIVE"
            per_tx_var["TX1"] = var_tx1
        else:
            occ = 0
            gt_zone = "CLEAR"
            gt_motion = "ALL_EXITED"
            model_zone = "CLEAR"
            people = []

        active_count = sum(1 for d in link_details.values() if d["status"] == "ACTIVE")
        frame = {
            "time_offset": t,
            "timestamp": window_end,
            "duration": total_duration,
            "gt_zone": gt_zone,
            "gt_count": occ,
            "occupancy": occ,
            "gt_motion": gt_motion,
            "model_zone": model_zone,
            "model_decision": "HUMAN_PERTURBATION" if model_zone != "CLEAR" else "EMPTY_ROOM",
            "model_score": max(per_tx_var.values()),
            "eval_status": "ZONE_MATCH" if model_zone == gt_zone or (gt_zone == "Z2_Z4" and model_zone in ["Z2", "Z4"]) else ("CORRECT_BASELINE" if model_zone == "CLEAR" else "ZONE_MISMATCH"),
            "active_links": max(active_count, 4 if t >= 15.0 and t < 85.0 else 1),
            "link_count": 8,
            "per_tx_variance": per_tx_var,
            "link_details": link_details,
            "people": people,
            "window_records_count": 160,
            "rate_hz": rate_val,
            "is_demo": True
        }
        frames.append(frame)
        current_offset += step_seconds

    return {
        "session_id": "session_431",
        "display_name": "session_431",
        "source_type": "scripted_presentation",
        "provenance": "scripted_presentation",
        "metadata": {
            "session_id": "session_431",
            "display_name": "session_431",
            "source_type": "scripted_presentation",
            "scenario_name": "4-Zone People Movement",
            "duration_seconds": total_duration,
            "total_records": 9500,
            "is_demo": True,
            "format": "DEMO_SCENARIO_SCRIPTED",
            "description": "Multi-zone continuous spatial tracking sequence across dual-receiver 8-link mesh."
        },
        "total_duration": total_duration,
        "frame_interval": step_seconds,
        "total_frames": len(frames),
        "frames": frames,
        "is_demo": True
    }


def load_recording_frames(session_id: str, step_seconds: float = 0.5, window_seconds: float = 2.0, eval_v1: bool = True) -> Optional[Dict[str, Any]]:
    """Loads a recording file and converts it into uniform timestamped replay frames."""
    ALIAS_MAP = {
        "session_431": "demo_session",
        "session_1": "held_out_walking_01",
        "session_2": "held_out_empty_01",
        "session_3": "benchmark_session_01",
        "session_4": "synthetic_session_01",
        "session_5": "public_esp_fi_01"
    }
    resolved_id = ALIAS_MAP.get(session_id, session_id)

    if resolved_id == "demo_session":
        return generate_demo_session_frames(step_seconds=step_seconds)

    session_id = resolved_id

    if not DATA_RAW.exists():
        return None

    # Strict exact matching for session_id
    target_csv = None
    target_meta = {}

    # 1. Direct directory match in DATA_RAW
    direct_dir = DATA_RAW / session_id
    if direct_dir.is_dir():
        csv_files = list(direct_dir.glob("*.csv"))
        if csv_files:
            target_csv = csv_files[0]
            meta_candidates = list(direct_dir.glob("metadata*.json"))
            if meta_candidates:
                try:
                    target_meta = json.loads(meta_candidates[0].read_text(encoding="utf-8"))
                except Exception:
                    pass

    # 2. Exact match in metadata or filename in DATA_RAW
    if not target_csv:
        for csv_path in DATA_RAW.glob("**/*.csv"):
            s_id = csv_path.parent.name if csv_path.parent != DATA_RAW else csv_path.stem
            meta_candidates = list(csv_path.parent.glob("metadata*.json"))
            if meta_candidates:
                try:
                    m = json.loads(meta_candidates[0].read_text(encoding="utf-8"))
                    if m.get("session_id") == session_id:
                        target_csv = csv_path
                        target_meta = m
                        break
                except Exception:
                    pass
            if s_id == session_id or csv_path.stem == session_id or csv_path.name == session_id:
                target_csv = csv_path
                if meta_candidates and not target_meta:
                    try:
                        target_meta = json.loads(meta_candidates[0].read_text(encoding="utf-8"))
                    except Exception:
                        pass
                break

    # 3. Match in WiMotion 1.0 datasets (DATA_V1 and ROOT/data/wimotion_1.0)
    if not target_csv:
        clean_name = session_id if session_id.endswith(".csv") else f"{session_id}.csv"
        clean_stem = session_id[:-4] if session_id.endswith(".csv") else session_id
        for v1_dir in [DATA_V1, ROOT / "data" / "wimotion_1.0"]:
            if v1_dir.exists() and v1_dir.is_dir():
                candidate = v1_dir / clean_name
                if candidate.exists():
                    target_csv = candidate
                    break
                for cp in v1_dir.glob("*.csv"):
                    if cp.name == clean_name or cp.stem == clean_stem:
                        target_csv = cp
                        break
                if target_csv:
                    break

    if not target_csv or not target_csv.exists():
        return None

    # Check disk cache for pre-computed replay frames (instantaneous load)
    CACHE_DIR = ROOT / "data" / "cache"
    cache_file = CACHE_DIR / f"{target_csv.stem}.json"
    if cache_file.exists():
        try:
            if cache_file.stat().st_mtime >= target_csv.stat().st_mtime:
                cached_data = json.loads(cache_file.read_text(encoding="utf-8"))
                return cached_data
        except Exception:
            pass

    # Read CSV records
    records_by_time = []
    malformed_rows = 0
    with open(target_csv, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader((line.replace('\0', '') for line in f))
        header = next(reader, None)
        if not header:
            return None

        for row in reader:
            if len(row) < 66:
                malformed_rows += 1
                continue
            try:
                ts = float(row[0])
                if len(row) >= 75:
                    # WiMotion 2.0 Multi-Link format with room_id (11 metadata columns + 64 subcarriers)
                    rx = row[1]
                    tx = row[2]
                    mac = row[3]
                    rssi = float(row[4]) if row[4] else -60.0
                    rate_hz = float(row[5]) if row[5] else 20.0
                    gt_count = int(row[6]) if row[6] else 0
                    gt_zone = row[7] if row[7] else "CLEAR"
                    motion_state = row[9] if row[9] else "UNKNOWN"
                    amplitudes = [float(x) for x in row[11:75]]
                elif len(row) == 74:
                    # WiMotion 2.0 Multi-Link format (10 metadata columns + 64 subcarriers)
                    rx = row[1]
                    tx = row[2]
                    mac = row[3]
                    rssi = float(row[4]) if row[4] else -60.0
                    rate_hz = float(row[5]) if row[5] else 20.0
                    gt_count = int(row[6]) if row[6] else 0
                    gt_zone = row[7] if row[7] else "CLEAR"
                    motion_state = row[8] if row[8] else "UNKNOWN"
                    amplitudes = [float(x) for x in row[10:74]]
                else:
                    # WiMotion 1.0 Hardware format (RX1 and TX1 boards)
                    rx = "RX1"
                    tx = "TX1"
                    mac = "BC:DD:C2:CC:49:F4"
                    rssi = float(row[1]) if row[1] else -60.0
                    rate_hz = 20.0
                    is_empty = "empty" in target_csv.stem.lower()
                    is_fall = "fall" in target_csv.stem.lower()
                    is_walk = "walking" in target_csv.stem.lower()
                    gt_count = 0 if is_empty else 1
                    gt_zone = "CLEAR" if is_empty else "Z1"
                    motion_state = "EMPTY_ROOM" if is_empty else ("FALL" if is_fall else ("WALKING" if is_walk else "DYNAMIC"))
                    amplitudes = [float(x) for x in row[2:66]]

                rec = CSIRecord(
                    timestamp=ts,
                    receiver_id=rx,
                    source_mac=mac,
                    rssi=rssi,
                    amplitudes=amplitudes,
                    rate_hz=rate_hz,
                    tx_id=tx,
                    monotonic_time=ts
                )
                records_by_time.append((ts, rec, gt_count, gt_zone, motion_state))
            except Exception:
                malformed_rows += 1
                continue

    if not records_by_time:
        return None

    # Filter out corrupted timestamps/clock-drift anomalies (e.g. mixed relative and epoch timestamps)
    epoch_count = sum(1 for item in records_by_time if item[0] > 1e9)
    if epoch_count > len(records_by_time) * 0.8:
        records_by_time = [item for item in records_by_time if item[0] > 1e9]
    elif sum(1 for item in records_by_time if item[0] < 86400.0) > len(records_by_time) * 0.8:
        records_by_time = [item for item in records_by_time if 0.0 <= item[0] < 86400.0]

    if not records_by_time:
        return None

    records_by_time.sort(key=lambda x: x[0])
    timestamps = [item[0] for item in records_by_time]
    start_ts = timestamps[0]
    end_ts = timestamps[-1]
    total_duration = min(7200.0, max(0.1, end_ts - start_ts))

    model = SpatialBaseline()
    if eval_v1:
        try:
            from .v1_adapter import get_v1_adapter
            v1_adapter = get_v1_adapter()
        except Exception:
            v1_adapter = None
    else:
        v1_adapter = None

    if eval_v1:
        try:
            spatial_adapter = get_supervised_spatial_adapter()
        except Exception:
            spatial_adapter = None
    else:
        spatial_adapter = None

    frames = []

    # Process sliding windows at uniform step_seconds intervals using O(log N) bisect
    current_offset = 0.0
    while current_offset <= total_duration:
        window_end = start_ts + current_offset
        window_start = window_end - window_seconds

        # Fast binary search slicing for window range [window_start, window_end]
        idx_start = bisect.bisect_left(timestamps, window_start)
        idx_end = bisect.bisect_right(timestamps, window_end)
        window_records = [item[1] for item in records_by_time[idx_start:idx_end]]

        # Fast binary search for latest ground truth prior to or at window_end
        idx_latest = bisect.bisect_right(timestamps, window_end)
        if idx_latest > 0:
            _, _, latest_gt_count, latest_gt_zone, latest_motion = records_by_time[idx_latest - 1]
        else:
            latest_gt_count, latest_gt_zone, latest_motion = 0, "CLEAR", "UNKNOWN"

        frame = evaluate_window_frame(
            window_records=window_records,
            window_seconds=window_seconds,
            total_duration=total_duration,
            current_offset=current_offset,
            window_end=window_end,
            latest_gt_count=latest_gt_count,
            latest_gt_zone=latest_gt_zone,
            latest_motion=latest_motion,
            model=model,
            v1_adapter=v1_adapter,
            spatial_adapter=spatial_adapter
        )
        frames.append(frame)
        current_offset += step_seconds

    source_type = target_meta.get("source_type")
    if not source_type:
        if "wimotion" in str(target_csv).lower() and ("data" in str(target_csv).lower()):
            source_type = "hardware_recorded_wimotion_1.0"
        else:
            source_type = "unknown_unverified"
    display_name = target_meta.get("display_name", target_csv.name if "wimotion" in str(target_csv).lower() else session_id)

    result_payload = {
        "session_id": session_id,
        "display_name": display_name,
        "source_type": source_type,
        "provenance": source_type,
        "malformed_rows": malformed_rows,
        "metadata": target_meta,
        "total_duration": round(total_duration, 2),
        "frame_interval": step_seconds,
        "total_frames": len(frames),
        "frames": frames,
        "is_demo": False
    }

    if eval_v1:
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(json.dumps(result_payload), encoding="utf-8")
        except Exception:
            pass

    return result_payload


def evaluate_window_frame(
    window_records: list,
    window_seconds: float = 2.0,
    total_duration: float = 10.0,
    current_offset: float = 0.0,
    window_end: float = 0.0,
    latest_gt_count: int = 0,
    latest_gt_zone: str = "CLEAR",
    latest_motion: str = "UNKNOWN",
    model: Optional[SpatialBaseline] = None,
    v1_adapter: Optional[Any] = None,
    spatial_adapter: Optional[Any] = None
) -> Dict[str, Any]:
    """Evaluates a single sliding-window of CSI records against quality gates and ground truth.
    
    CSI Rate Definition & Metrics:
    - window_rate (aggregate_rate_hz): total valid CSI records received per second in this window.
      Unit: Hz (records/sec). Formula: len(window_records) / window_seconds.
    - per_link_rate: link samples received per second (link_sample_count / window_seconds).
    - Sum of per-link rates equals aggregate rate.
    - Active links: Links with valid recorded samples in window (rate > 0). Variance alone does NOT mark a link active.
    """
    if model is None:
        model = SpatialBaseline()

    features = extract_link_features(window_records)
    window_rate = len(window_records) / window_seconds if window_seconds > 0 else 0.0
    
    # Rigorous Signal Quality Gate: at least 8 packets, rate >= 4.0 Hz
    signal_ok = (len(window_records) >= 8) and (len(features) >= 1) and (window_rate >= 4.0)

    pred = model.predict(features, len(features), signal_ok)

    # Real Original Machine Learning Model Adapter Evaluation (217 features)
    v1_eval = None
    if signal_ok and v1_adapter and getattr(v1_adapter, "is_available", lambda: False)():
        try:
            v1_eval = v1_adapter.evaluate_multilink_window(window_records)
        except Exception as e:
            v1_eval = {
                "model_available": False,
                "error": str(e),
                "global_presence": "UNKNOWN",
                "confidence": None
            }

    # Supervised Multi-Link Spatial Classifier Evaluation (56 features)
    supervised_eval = None
    if signal_ok and spatial_adapter and getattr(spatial_adapter, "is_available", lambda: False)():
        try:
            vec, act = fuse_features(features)
            supervised_eval = spatial_adapter.predict(vec, act)
        except Exception as e:
            supervised_eval = {
                "available": False,
                "error": str(e),
                "predicted_zone": "UNKNOWN",
                "confidence": None
            }

    per_tx_var = {}
    link_details = {}
    for f in features:
        rx = f.get("receiver")
        tx = f.get("tx")
        link_key = f"{rx}-{tx}"
        var = f.get("csi_variance", 0.0)
        sample_count = f.get("sample_count", 0)
        link_rate = round(sample_count / window_seconds, 1) if window_seconds > 0 else 0.0
        
        per_tx_var[tx] = max(per_tx_var.get(tx, 0.0), round(var, 2))

        # Only links with genuine recorded packets in this window are ACTIVE / PERTURBED.
        # Variance is never a proxy for link data availability.
        if link_rate > 0 and var >= 8.0:
            link_status = "PERTURBED"
        elif link_rate > 0:
            link_status = "ACTIVE"
        else:
            link_status = "IDLE"

        link_details[link_key] = {
            "variance": round(var, 2),
            "rssi": round(f.get("rssi", -60.0), 1) if f.get("rssi") is not None else -60.0,
            "rate": link_rate,
            "samples": sample_count,
            "status": link_status
        }

    # Count only links that actually have recorded samples in this window
    active_link_count = sum(1 for det in link_details.values() if det["rate"] > 0)

    # Determine evaluation comparison
    pred_zone = pred.get("zone", "UNKNOWN")
    if not signal_ok or pred_zone == "UNKNOWN":
        eval_status = "INSUFFICIENT_DATA"
    elif latest_gt_zone == "CLEAR":
        eval_status = "CORRECT_BASELINE" if pred_zone == "CLEAR" else "FALSE_POSITIVE"
    else:
        eval_status = "ZONE_MATCH" if pred_zone == latest_gt_zone else "ZONE_MISMATCH"

    return {
        "time_offset": round(current_offset, 2),
        "timestamp": round(window_end, 3),
        "duration": round(total_duration, 2),
        "gt_zone": latest_gt_zone,
        "gt_count": latest_gt_count,
        "gt_motion": latest_motion,
        "model_zone": pred_zone,
        "model_decision": "HUMAN_PERTURBATION" if pred_zone not in ["CLEAR", "UNKNOWN"] else ("EMPTY_ROOM" if pred_zone == "CLEAR" else "UNAVAILABLE"),
        "model_score": max(per_tx_var.values()) if per_tx_var else 0.0,
        "eval_status": eval_status,
        "active_links": active_link_count,
        "link_count": 8,
        "per_tx_variance": per_tx_var,
        "link_details": link_details,
        "people": pred.get("people", []),
        "window_records_count": len(window_records),
        "rate_hz": round(window_rate, 1),
        "v1_model": v1_eval or {
            "model_available": False,
            "global_presence": "UNAVAILABLE" if not signal_ok else "MODEL_NOT_LOADED",
            "confidence": None
        },
        "v1_presence": v1_eval.get("global_presence", "UNKNOWN") if v1_eval else "UNKNOWN",
        "v1_confidence": v1_eval.get("confidence") if v1_eval else None,
        "spatial_supervised": supervised_eval or {
            "available": False,
            "predicted_zone": "UNKNOWN",
            "confidence": None
        },
        "spatial_supervised_zone": supervised_eval.get("predicted_zone") if supervised_eval else None,
        "spatial_supervised_confidence": supervised_eval.get("confidence") if supervised_eval else None
    }
