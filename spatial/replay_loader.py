import csv
import json
import os
import time
import bisect
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict
import numpy as np

from .types import CSIRecord
from .features import extract_link_features
from .inference import SpatialBaseline

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"


def _extract_csv_timestamps(csv_path: Path) -> Optional[tuple[float, float, int]]:
    """Quickly extracts start_ts, end_ts, and record count from CSV without full parsing."""
    try:
        first_ts = None
        last_ts = None
        count = 0
        with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
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
    if not DATA_RAW.exists() or not session_id:
        return None

    # Strict exact matching for session_id
    target_csv = None
    target_meta = {}

    # 1. Direct directory match
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

    # 2. Exact match in metadata or filename
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
            if s_id == session_id or csv_path.stem == session_id:
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
    timestamps = [item[0] for item in records_by_time]
    start_ts = timestamps[0]
    end_ts = timestamps[-1]
    total_duration = max(0.1, end_ts - start_ts)

    model = SpatialBaseline()
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
            model=model
        )
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


def evaluate_window_frame(
    window_records: list,
    window_seconds: float = 2.0,
    total_duration: float = 10.0,
    current_offset: float = 0.0,
    window_end: float = 0.0,
    latest_gt_count: int = 0,
    latest_gt_zone: str = "CLEAR",
    latest_motion: str = "UNKNOWN",
    model: Optional[SpatialBaseline] = None
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
        "rate_hz": round(window_rate, 1)
    }
