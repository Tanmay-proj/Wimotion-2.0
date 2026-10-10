import csv
import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict
import numpy as np

from .types import CSIRecord
from .features import extract_link_features
from .inference import SpatialBaseline

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"


def list_recordings() -> List[Dict[str, Any]]:
    """Discovers all available recorded sessions in data/raw."""
    if not DATA_RAW.exists():
        return []

    sessions = []
    # Search for any csv files inside data/raw
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
        duration = meta.get("duration_seconds")
        total_records = meta.get("total_records")
        gt_zone = meta.get("ground_truth_zone", "UNKNOWN")
        gt_count = meta.get("ground_truth_count", 0)
        motion_state = meta.get("motion_state", "UNKNOWN")

        # Fallback record count estimation if not in metadata
        if total_records is None:
            try:
                with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
                    total_records = max(0, sum(1 for _ in f) - 1)
            except Exception:
                total_records = 0

        if duration is None:
            duration = round(total_records / 160.0, 1) if total_records > 0 else 0.0

        sessions.append({
            "session_id": session_id,
            "filename": csv_path.name,
            "path": str(csv_path.relative_to(ROOT)).replace("\\", "/"),
            "created_at": created_at,
            "duration_seconds": duration,
            "total_records": total_records,
            "ground_truth_zone": gt_zone,
            "ground_truth_count": gt_count,
            "motion_state": motion_state,
            "format": "CSV_RAW_CSI_64",
            "has_metadata": bool(meta)
        })

    return sessions


def load_recording_frames(session_id: str, step_seconds: float = 0.5, window_seconds: float = 2.0) -> Optional[Dict[str, Any]]:
    """Loads a recording file and converts it into uniform timestamped replay frames."""
    if not DATA_RAW.exists():
        return None

    # Locate CSV file matching session_id
    target_csv = None
    target_meta = {}

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
        if s_id == session_id or session_id in csv_path.name:
            target_csv = csv_path
            if meta_candidates and not target_meta:
                try:
                    target_meta = json.loads(meta_candidates[0].read_text(encoding="utf-8"))
                except Exception:
                    pass
            break

    if not target_csv or not target_csv.exists():
        return None

    # Read CSV records
    records_by_time = []
    with open(target_csv, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            return None

        for row in reader:
            if len(row) < 74:
                continue
            try:
                ts = float(row[0])
                rx = row[1]
                tx = row[2]
                mac = row[3]
                rssi = float(row[4]) if row[4] else -60.0
                rate_hz = float(row[5]) if row[5] else 20.0
                gt_count = int(row[6]) if row[6] else 0
                gt_zone = row[7] if row[7] else "CLEAR"
                motion_state = row[8] if row[8] else "UNKNOWN"
                amplitudes = [float(x) for x in row[10:74]]

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
                continue

    if not records_by_time:
        return None

    records_by_time.sort(key=lambda x: x[0])
    start_ts = records_by_time[0][0]
    end_ts = records_by_time[-1][0]
    total_duration = max(0.1, end_ts - start_ts)

    model = SpatialBaseline()
    frames = []

    # Process sliding windows at uniform step_seconds intervals
    current_offset = 0.0
    while current_offset <= total_duration:
        window_end = start_ts + current_offset
        window_start = window_end - window_seconds

        # Select records within window
        window_records = [
            item[1]
            for item in records_by_time
            if window_start <= item[0] <= window_end
        ]

        # Latest ground truth in window
        latest_items = [
            item for item in records_by_time
            if item[0] <= window_end
        ]
        if latest_items:
            _, _, latest_gt_count, latest_gt_zone, latest_motion = latest_items[-1]
        else:
            latest_gt_count, latest_gt_zone, latest_motion = 0, "CLEAR", "UNKNOWN"

        features = extract_link_features(window_records) if window_records else []
        pred = model.predict(features, len(features), len(window_records) > 0)

        per_tx_var = {}
        link_details = {}
        for f in features:
            rx = f.get("receiver")
            tx = f.get("tx")
            link_key = f"{rx}-{tx}"
            var = f.get("csi_variance", 0.0)
            per_tx_var[tx] = max(per_tx_var.get(tx, 0.0), round(var, 2))
            link_details[link_key] = {
                "variance": round(var, 2),
                "rssi": round(f.get("rssi", -60.0), 1) if f.get("rssi") is not None else -60.0,
                "rate": round(f.get("sample_count", 0) / window_seconds, 1),
                "status": "ACTIVE" if var > 0.0 else "IDLE"
            }

        # Determine evaluation comparison
        pred_zone = pred.get("zone", "CLEAR")
        if latest_gt_zone == "CLEAR":
            eval_status = "CORRECT_BASELINE" if pred_zone == "CLEAR" else "FALSE_POSITIVE"
        else:
            eval_status = "ZONE_MATCH" if pred_zone == latest_gt_zone else "ZONE_MISMATCH"

        frame = {
            "time_offset": round(current_offset, 2),
            "timestamp": round(window_end, 3),
            "duration": round(total_duration, 2),
            "gt_zone": latest_gt_zone,
            "gt_count": latest_gt_count,
            "gt_motion": latest_motion,
            "model_zone": pred_zone,
            "model_decision": "HUMAN_PERTURBATION" if pred_zone != "CLEAR" else "EMPTY_ROOM",
            "model_score": max(per_tx_var.values()) if per_tx_var else 0.0,
            "eval_status": eval_status,
            "active_links": len(features),
            "link_count": 8,
            "per_tx_variance": per_tx_var,
            "link_details": link_details,
            "people": pred.get("people", []),
            "window_records_count": len(window_records),
            "rate_hz": round(len(window_records) / window_seconds, 1)
        }
        frames.append(frame)
        current_offset += step_seconds

    return {
        "session_id": session_id,
        "metadata": target_meta,
        "total_duration": round(total_duration, 2),
        "frame_interval": step_seconds,
        "total_frames": len(frames),
        "frames": frames
    }
