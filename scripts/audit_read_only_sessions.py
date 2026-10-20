import glob
import json
import hashlib
from pathlib import Path
import pandas as pd
import numpy as np

# Authoritative physical experiment registry based on HARDWARE_SESSION_LOG.txt
# Physical ground truth requires BOTH recorded parameters AND verified lab log evidence
DOCUMENTED_PHYSICAL_LOG = {
    "session_real_001_empty": {
        "logged_activity": "Empty room baseline; room unoccupied",
        "verified_zone": "CLEAR",
        "verified_count": 0,
        "tx_placement_verified": False, # Empty room - no single TX active zone
        "has_operator_log_evidence": True,
        "known_hardware_notes": "Phase 1 pre-lock multithreading write collision dropped 84 rows; 4 non-epoch timestamps."
    },
    "session_real_002_near_rx1": {
        "logged_activity": "User standing near RX1 baseline",
        "verified_zone": "Z1",
        "verified_count": 1,
        "tx_placement_verified": False, # Positioned at RX1, not near specific TX node
        "has_operator_log_evidence": True,
        "known_hardware_notes": "Positioned at RX1; 1 truncated non-epoch timestamp."
    },
    "session_real_003_tx_walk": {
        "logged_activity": "User walking within 0.5ft of TX1 target till 1907hrs",
        "verified_zone": "Z1",
        "verified_count": 1,
        "tx_placement_verified": False, # Recorder ran in auto-mode without --zone CLI flag
        "has_operator_log_evidence": True,
        "known_hardware_notes": "Auto-mode without manual --zone; prototype predictions entered CSV."
    },
    "session_real_004_mystery_tx": {
        "logged_activity": "User walking near diagonally opposite TX (SW / Z3) till 1916hrs",
        "verified_zone": "Z3",
        "verified_count": 1,
        "tx_placement_verified": False,
        "has_operator_log_evidence": True,
        "known_hardware_notes": "Auto-mode without manual --zone; prototype predictions in CSV."
    },
    "session_real_005_blind_tx": {
        "logged_activity": "Repeat walk near Z3 board",
        "verified_zone": "Z3",
        "verified_count": 1,
        "tx_placement_verified": False,
        "has_operator_log_evidence": True,
        "known_hardware_notes": "Auto-mode without manual --zone; prototype predictions in CSV."
    },
    "session_real_006_tx2_walk": {
        "logged_activity": "Physical walk near TX2 (1C:69:20:31:38:08 / Zone Z2) till 1946hrs",
        "verified_zone": "Z2",
        "verified_count": 1,
        "tx_placement_verified": True, # Verified physical placement near TX2 with manual CLI flags
        "has_operator_log_evidence": True,
        "known_hardware_notes": "Recorded with --zone Z2 --count 1 --motion-state WALKING_NEAR_TX2. 2,562 packets from TX2."
    },
    "session_real_007_tx4_walk": {
        "logged_activity": "Physical walk near TX4 (CC:7B:5C:28:84:70 / Zone Z4) till 1955hrs",
        "verified_zone": "Z4",
        "verified_count": 1,
        "tx_placement_verified": True, # Verified physical placement near TX4 with manual CLI flags
        "has_operator_log_evidence": True,
        "known_hardware_notes": "Recorded with --zone Z4 --count 1 --motion-state WALKING_NEAR_TX4. 7,184 packets from TX4."
    },
    "session_pB_clear_01": {
        "logged_activity": "Phase B empty room baseline; room unoccupied",
        "verified_zone": "CLEAR",
        "verified_count": 0,
        "tx_placement_verified": True, # Verified room empty baseline
        "has_operator_log_evidence": True,
        "known_hardware_notes": "Phase B take 01: 5,576 records, 0 count delta, 0 non-epoch timestamps."
    },
    "session_pB_clear_02": {
        "logged_activity": "Phase B empty room baseline repeat; room unoccupied",
        "verified_zone": "CLEAR",
        "verified_count": 0,
        "tx_placement_verified": True,
        "has_operator_log_evidence": True,
        "known_hardware_notes": "Phase B take 02 repeat empty room."
    },
    "session_pB_z1_walk_01": {
        "logged_activity": "Phase B walking near TX1 in Zone Z1",
        "verified_zone": "Z1",
        "verified_count": 1,
        "tx_placement_verified": True,
        "has_operator_log_evidence": True,
        "known_hardware_notes": "Phase B take 01 walk near TX1 (BC:DD:C2:CC:49:F4)."
    },
    "session_pB_z1_walk_02": {
        "logged_activity": "Phase B repeat walk near TX1 in Zone Z1",
        "verified_zone": "Z1",
        "verified_count": 1,
        "tx_placement_verified": True,
        "has_operator_log_evidence": True,
        "known_hardware_notes": "Phase B take 02 walk near TX1 (BC:DD:C2:CC:49:F4)."
    },
    "session_pB_z2_walk_01": {
        "logged_activity": "Phase B walking near TX2 in Zone Z2",
        "verified_zone": "Z2",
        "verified_count": 1,
        "tx_placement_verified": True,
        "has_operator_log_evidence": True,
        "known_hardware_notes": "Phase B take 01 walk near TX2 (1C:69:20:31:38:08)."
    },
    "session_pB_z2_walk_02": {
        "logged_activity": "Phase B repeat walk near TX2 in Zone Z2",
        "verified_zone": "Z2",
        "verified_count": 1,
        "tx_placement_verified": True,
        "has_operator_log_evidence": True,
        "known_hardware_notes": "Phase B take 02 walk near TX2 (1C:69:20:31:38:08)."
    },
    "session_pB_z3_walk_01": {
        "logged_activity": "Phase B walking near TX3 in Zone Z3",
        "verified_zone": "Z3",
        "verified_count": 1,
        "tx_placement_verified": True,
        "has_operator_log_evidence": True,
        "known_hardware_notes": "Phase B take 01 walk near TX3 (1C:69:20:31:4B:40)."
    },
    "session_pB_z3_walk_02": {
        "logged_activity": "Phase B repeat walk near TX3 in Zone Z3",
        "verified_zone": "Z3",
        "verified_count": 1,
        "tx_placement_verified": True,
        "has_operator_log_evidence": True,
        "known_hardware_notes": "Phase B take 02 walk near TX3 (1C:69:20:31:4B:40)."
    },
    "session_pB_z4_walk_01": {
        "logged_activity": "Phase B walking near TX4 in Zone Z4",
        "verified_zone": "Z4",
        "verified_count": 1,
        "tx_placement_verified": True,
        "has_operator_log_evidence": True,
        "known_hardware_notes": "Phase B take 01 walk near TX4 (CC:7B:5C:28:84:70)."
    },
    "session_pB_z4_walk_02": {
        "logged_activity": "Phase B repeat walk near TX4 in Zone Z4",
        "verified_zone": "Z4",
        "verified_count": 1,
        "tx_placement_verified": True,
        "has_operator_log_evidence": True,
        "known_hardware_notes": "Phase B take 02 walk near TX4 (CC:7B:5C:28:84:70)."
    }
}


def compute_file_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def run_comprehensive_audit():
    root_dir = Path("data/raw")
    all_real_dirs = sorted(list(root_dir.glob("session_real_*")) + list(root_dir.glob("session_pB_*")))
    
    with open("config/nodes.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    known_macs = {
        config["transmitters"]["TX1"]["mac"].upper(): "TX1",
        config["transmitters"]["TX2"]["mac"].upper(): "TX2",
        config["transmitters"]["TX3"]["mac"].upper(): "TX3",
        config["transmitters"]["TX4"]["mac"].upper(): "TX4",
    }
    
    audit_results = []
    orphan_results = []
    
    print("=" * 90)
    print("   WiMotion 2.0 — Rigorous Read-Only Hardware Session & Label Provenance Audit")
    print("=" * 90)
    
    for s_dir in all_real_dirs:
        s_id = s_dir.name
        csv_files = list(s_dir.glob("*.csv"))
        json_files = list(s_dir.glob("*.json"))
        
        # 6. Flag Ambiguous Multi-File Sessions (Don't silently pick [0])
        if len(csv_files) > 1:
            orphan_results.append({
                "session_id": s_id,
                "status": "AMBIGUOUS_MULTIPLE_CSVS",
                "details": f"Found {len(csv_files)} CSV files: {[f.name for f in csv_files]}",
                "action": "Exclude session until single authoritative CSV is designated"
            })
            continue
            
        if len(json_files) > 1:
            orphan_results.append({
                "session_id": s_id,
                "status": "AMBIGUOUS_MULTIPLE_JSONS",
                "details": f"Found {len(json_files)} JSON files: {[f.name for f in json_files]}",
                "action": "Exclude session until single authoritative metadata is designated"
            })
            continue
            
        # Flag Metadata-Only Sessions (JSON exists but no CSV)
        if json_files and not csv_files:
            orphan_results.append({
                "session_id": s_id,
                "status": "METADATA_ONLY_NO_CSV",
                "details": f"Metadata exists ({json_files[0].name}) but CSV data file is missing",
                "action": "Quarantine session; missing raw RF data"
            })
            continue
            
        # Flag CSV-Only Orphan Sessions (CSV exists but JSON missing)
        if csv_files and not json_files:
            csv_path = csv_files[0]
            sha = compute_file_sha256(csv_path)
            try:
                line_count = sum(1 for _ in open(csv_path, "r", encoding="utf-8", errors="ignore")) - 1
            except Exception:
                line_count = -1
            orphan_results.append({
                "session_id": s_id,
                "status": "ORPHAN_MISSING_METADATA",
                "details": f"CSV {csv_path.name} ({line_count} rows, SHA-256: {sha[:16]}...) lacks metadata JSON",
                "action": "Quarantine session; do not invent metadata or ground truth"
            })
            print(f"\n[!] ORPHAN DETECTED: {s_id}")
            print(f"    CSV File: {csv_path.name} ({line_count} rows)")
            print(f"    Issue: Missing metadata JSON file. Flagged into orphan report.")
            continue
            
        if not csv_files or not json_files:
            continue
            
        csv_path = csv_files[0]
        json_path = json_files[0]
        csv_sha256 = compute_file_sha256(csv_path)
        
        with open(json_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            
        meta_count_claimed = meta.get("total_records_captured", 0)
        meta_gt_zone = meta.get("ground_truth_zone")
        meta_gt_count = meta.get("ground_truth_count")
        meta_motion = meta.get("motion_state")
        meta_duration = meta.get("duration_seconds", 0.0)
        auto_detected = meta.get("auto_detected", False)
        
        # Read CSV without modifying
        df = pd.read_csv(csv_path, encoding="utf-8", encoding_errors="replace", low_memory=False)
        csv_row_count = len(df)
        
        # 1. Strict Count Match Verification
        count_diff = abs(csv_row_count - meta_count_claimed)
        count_match = (count_diff == 0) # Exact 0 tolerance
        
        # 2. Label Consistency Check
        csv_zones = df["ground_truth_zone"].dropna().unique().tolist() if "ground_truth_zone" in df.columns else []
        csv_counts = df["ground_truth_count"].dropna().unique().tolist() if "ground_truth_count" in df.columns else []
        
        single_zone_in_csv = (len(csv_zones) == 1)
        single_count_in_csv = (len(csv_counts) == 1)
        csv_zone_val = csv_zones[0] if single_zone_in_csv else None
        csv_count_val = csv_counts[0] if single_count_in_csv else None
        
        zone_matches_meta = single_zone_in_csv and (csv_zone_val == meta_gt_zone)
        count_matches_meta = single_count_in_csv and (csv_count_val == meta_gt_count)
        
        # 3. Independent Physical Log & Provenance Cross-Check (Explicit Value Comparison)
        phys_log = DOCUMENTED_PHYSICAL_LOG.get(s_id)
        has_log_entry = (phys_log is not None)
        has_log_evidence = phys_log.get("has_operator_log_evidence", False) if has_log_entry else False
        logged_zone = phys_log.get("verified_zone") if has_log_entry else None
        logged_count = phys_log.get("verified_count") if has_log_entry else None
        
        # Explicit value check between physical lab log, CSV, and metadata
        zone_matches_physical_log = (
            single_zone_in_csv 
            and csv_zone_val is not None 
            and logged_zone is not None 
            and csv_zone_val == logged_zone 
            and meta_gt_zone == logged_zone
        )
        count_matches_physical_log = (
            single_count_in_csv 
            and csv_count_val is not None 
            and logged_count is not None 
            and csv_count_val == logged_count 
            and meta_gt_count == logged_count
        )
        
        is_genuine_manual_gt = (
            not auto_detected 
            and single_zone_in_csv 
            and zone_matches_meta 
            and has_log_evidence
            and zone_matches_physical_log
            and count_matches_physical_log
        )
        label_source = "manual" if is_genuine_manual_gt else ("auto_generated" if auto_detected or not single_zone_in_csv else "UNVERIFIED")
        
        # 4. Transmitter Mapping Verification Check
        mapping_verified = phys_log.get("tx_placement_verified", False) if has_log_entry else False
        
        # 5. Comprehensive Timestamp Validation & Diagnostics
        ts_nan_count = 0
        ts_non_numeric_count = 0
        ts_non_epoch_count = 0
        calculated_duration = 0.0
        ts_min = None
        ts_max = None
        ts_first = None
        ts_last = None
        ts_valid = False
        is_monotonic = False
        interleaved_out_of_order_count = 0
        exact_row_duplicates = 0
        quantized_ts_mac_collisions = 0
        
        if "timestamp" in df.columns:
            ts_nan_count = int(df["timestamp"].isna().sum())
            ts_series = pd.to_numeric(df["timestamp"], errors="coerce")
            ts_non_numeric_count = int(ts_series.isna().sum()) - ts_nan_count
            valid_ts = ts_series.dropna()
            
            if len(valid_ts) > 0:
                ts_first = float(valid_ts.iloc[0])
                ts_last = float(valid_ts.iloc[-1])
                ts_min = float(valid_ts.min())
                ts_max = float(valid_ts.max())
                ts_non_epoch_count = int((valid_ts < 1.0e9).sum())
                calculated_duration = round(ts_max - ts_min, 3)
                duration_delta = abs(calculated_duration - meta_duration)
                
                # Timestamp is strictly valid ONLY if:
                # 1) All timestamps are valid epoch timestamps (>= 1.0e9)
                # 2) Zero NaN or non-numeric values
                # 3) Calculated duration matches metadata duration within 2.5 seconds
                ts_valid = (ts_non_epoch_count == 0) and (ts_non_numeric_count == 0) and (duration_delta < 2.5) and (len(valid_ts) == len(df))
                
                # Check for dual-serial interleaving between RX1 and RX2
                diffs = np.diff(valid_ts.values)
                interleaved_out_of_order_count = int(np.sum(diffs < 0))
                is_monotonic = (interleaved_out_of_order_count == 0)
                
            # Duplicate record investigation: Distinguish exact full-row vs quantized timestamp bursts
            exact_row_duplicates = int(df.duplicated().sum())
            subset_cols = [c for c in ["timestamp", "receiver", "source_mac"] if c in df.columns]
            if len(subset_cols) >= 2:
                quantized_ts_mac_collisions = int(df.duplicated(subset=subset_cols).sum())

        # 6. MAC Address Breakdown
        mac_counts = {}
        unknown_mac_count = 0
        known_mac_count = 0
        if "source_mac" in df.columns:
            mac_series = df["source_mac"].astype(str).str.upper().value_counts()
            for mac, cnt in mac_series.items():
                if mac in known_macs:
                    tx_label = known_macs[mac]
                    mac_counts[f"{tx_label} ({mac})"] = int(cnt)
                    known_mac_count += int(cnt)
                else:
                    mac_counts[f"UNKNOWN ({mac})"] = int(cnt)
                    unknown_mac_count += int(cnt)

        # 7. Strict Eligibility Decision (All Conditions Mandatory!)
        exclusion_reasons = []
        if not count_match:
            exclusion_reasons.append(f"Record count mismatch (CSV={csv_row_count} vs Meta={meta_count_claimed}, delta={count_diff})")
        if auto_detected:
            exclusion_reasons.append("Auto-detected mode in recorder; unverified ground truth")
        if not single_zone_in_csv:
            exclusion_reasons.append(f"Fluctuating zone labels in CSV: {csv_zones}")
        if not single_count_in_csv:
            exclusion_reasons.append(f"Fluctuating person counts in CSV: {csv_counts}")
        if not zone_matches_meta:
            exclusion_reasons.append(f"CSV zone {csv_zones} does not match metadata {meta_gt_zone}")
        if not has_log_entry:
            exclusion_reasons.append("No entry in physical lab experiment log")
        if not zone_matches_physical_log:
            exclusion_reasons.append(f"Zone mismatch against physical log (CSV={csv_zone_val} vs Log={logged_zone})")
        if not count_matches_physical_log:
            exclusion_reasons.append(f"Count mismatch against physical log (CSV={csv_count_val} vs Log={logged_count})")
        if label_source != "manual":
            exclusion_reasons.append(f"Label source is '{label_source}', not verified 'manual'")
        if not ts_valid:
            if ts_non_epoch_count > 0:
                exclusion_reasons.append(f"Non-epoch corrupted timestamps found: {ts_non_epoch_count} rows < 1e9 (min={ts_min})")
            if ts_non_numeric_count > 0:
                exclusion_reasons.append(f"Non-numeric timestamp rows: {ts_non_numeric_count}")
            duration_delta = abs(calculated_duration - meta_duration)
            if duration_delta >= 2.5:
                exclusion_reasons.append(f"Duration mismatch (calc={calculated_duration}s vs meta={meta_duration}s)")
        if not mapping_verified:
            exclusion_reasons.append("Transmitter physical placement not independently verified (not near verified TX node)")

        is_eligible = (len(exclusion_reasons) == 0)
        decision = "PASS (Audited Candidate for manual_gt_v1)" if is_eligible else "FAIL / EXCLUDE"

        print(f"\n[-] Session: {s_id}")
        print(f"    CSV Rows:            {csv_row_count} | Meta Records: {meta_count_claimed} | Strict Match: {count_match}")
        print(f"    CSV GT Zone:         {csv_zones} (Meta: {meta_gt_zone} | Log: {logged_zone})")
        print(f"    CSV GT Count:        {csv_counts} (Meta: {meta_gt_count} | Log: {logged_count})")
        print(f"    Label Source:        {label_source} (Log Evidence: {has_log_evidence})")
        print(f"    TX Mapping Verified: {mapping_verified}")
        print(f"    Timestamps:          Valid={ts_valid} | Span={calculated_duration}s (Meta={meta_duration}s) | Non-Epoch={ts_non_epoch_count} | Interleaved={interleaved_out_of_order_count} | Exact Row Dups={exact_row_duplicates} | Quantized Collisions={quantized_ts_mac_collisions}")
        print(f"    Known MAC Frames:    {known_mac_count} | Unknown MAC Frames: {unknown_mac_count}")
        print(f"    CSV SHA-256:         {csv_sha256[:16]}...")
        print(f"    -> AUDIT RESULT:     {decision}")
        if exclusion_reasons:
            print(f"       Exclusion Reason: {'; '.join(exclusion_reasons)}")
            
        audit_results.append({
            "session_id": s_id,
            "source_type": meta.get("source_type", "hardware_recorded_multilink"),
            "label_source": label_source,
            "ground_truth_zone": meta_gt_zone if single_zone_in_csv else "MIXED/UNVERIFIED",
            "ground_truth_count": meta_gt_count if single_count_in_csv else -1,
            "motion_state": meta_motion,
            "csv_rows": csv_row_count,
            "meta_records": meta_count_claimed,
            "count_match_strict": count_match,
            "count_diff": count_diff,
            "calculated_duration_s": calculated_duration,
            "meta_duration_s": meta_duration,
            "ts_valid": ts_valid,
            "ts_min": ts_min,
            "ts_max": ts_max,
            "ts_non_epoch_count": ts_non_epoch_count,
            "interleaved_stream_order": interleaved_out_of_order_count,
            "exact_row_duplicates": exact_row_duplicates,
            "quantized_ts_mac_collisions": quantized_ts_mac_collisions,
            "known_mac_frames": known_mac_count,
            "unknown_mac_frames": unknown_mac_count,
            "mapping_verified": mapping_verified,
            "zone_matches_physical_log": zone_matches_physical_log,
            "count_matches_physical_log": count_matches_physical_log,
            "audited_candidate_only": is_eligible,
            "csv_sha256": csv_sha256,
            "exclusion_reason": "; ".join(exclusion_reasons) if exclusion_reasons else "NONE (Eligible candidate)"
        })
        
    df_audit = pd.DataFrame(audit_results)
    df_orphans = pd.DataFrame(orphan_results)
    
    out_audit_csv = Path("scripts/audit_summary_output.csv")
    out_orphan_csv = Path("scripts/orphan_sessions_output.csv")
    df_audit.to_csv(out_audit_csv, index=False)
    df_orphans.to_csv(out_orphan_csv, index=False)
    
    print("\n" + "=" * 90)
    print(f"[+] Audit Complete:")
    print(f"    - Sessions Audited:   {len(df_audit)}")
    print(f"    - Eligible Sessions:  {int(df_audit['audited_candidate_only'].sum())}")
    print(f"    - Excluded Sessions:  {int((~df_audit['audited_candidate_only']).sum()) + len(df_orphans)}")
    print(f"    - Orphan Sessions:    {len(df_orphans)}")
    print(f"    - Output Summary:     {out_audit_csv}")
    print(f"    - Orphan Summary:     {out_orphan_csv}")
    print("=" * 90)
    return df_audit, df_orphans


if __name__ == "__main__":
    run_comprehensive_audit()
