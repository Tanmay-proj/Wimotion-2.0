import sys
import shutil
import json
import hashlib
import argparse
from pathlib import Path
import pandas as pd


def compute_file_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def build_processed_dataset(output_dir: Path, force_rebuild: bool = False):
    base_dir = output_dir
    audit_dir = base_dir / "audit"
    candidates_dir = base_dir / "audited_candidates"
    
    # Security assertion: Target MUST reside strictly within data/processed
    allowed_root = Path("data/processed").resolve()
    target_resolved = base_dir.resolve()
    if not str(target_resolved).startswith(str(allowed_root)):
        print(f"\n[!] SECURITY ERROR: Target directory '{base_dir}' must be inside 'data/processed'!")
        print(f"[*] Operation aborted to protect raw data and project integrity.\n")
        sys.exit(1)

    # 1. Output protection:
    # Default behavior: STOP if output directory with manifest already exists.
    # Rebuild only if --force-rebuild is explicitly passed!
    manifest_file = base_dir / "manifest.csv"
    if base_dir.exists() and (manifest_file.exists() or candidates_dir.exists()):
        if not force_rebuild:
            print(f"\n[!] ERROR: Output dataset '{base_dir}' already exists!")
            print(f"[*] To prevent accidental data loss, the builder will NOT delete or overwrite existing output.")
            print(f"[*] To explicitly force a rebuild of generated artifacts, re-run with:")
            print(f"      py -3.10 scripts/build_manual_gt_v1.py --force-rebuild")
            print(f"[*] Or specify a new version directory:")
            print(f"      py -3.10 scripts/build_manual_gt_v1.py --output-dir data/processed/manual_gt_v2\n")
            sys.exit(1)
        else:
            print(f"\n[*] Explicit --force-rebuild passed. Selectively clearing generated artifacts in '{base_dir}'...")
            print(f"[*] Raw data in data/raw remains 100% untouched and immutable.")
            # Selectively clean only script-generated artifacts (preserving any manual docs)
            if candidates_dir.exists():
                shutil.rmtree(candidates_dir)
            if audit_dir.exists():
                shutil.rmtree(audit_dir)
            if manifest_file.exists():
                manifest_file.unlink()
            
    audit_dir.mkdir(parents=True, exist_ok=True)
    candidates_dir.mkdir(parents=True, exist_ok=True)
    
    audit_summary_path = Path("scripts/audit_summary_output.csv")
    orphan_summary_path = Path("scripts/orphan_sessions_output.csv")
    
    if not audit_summary_path.exists():
        print(f"[!] Audit summary not found at {audit_summary_path}. Run audit_read_only_sessions.py first.")
        sys.exit(1)
        
    df_audit = pd.read_csv(audit_summary_path)
    df_orphans = pd.read_csv(orphan_summary_path) if orphan_summary_path.exists() else pd.DataFrame()
    
    manifest_rows = []
    excluded_rows = []
    provenance_rows = []
    hash_verification_rows = []
    
    print("\n" + "=" * 80)
    print("   WiMotion 2.0 — Building Audited Dataset & SHA-256 Hash Verification")
    print("=" * 80)
    
    for _, row in df_audit.iterrows():
        s_id = row["session_id"]
        is_inc = bool(row["audited_candidate_only"])
        
        manifest_rows.append({
            "session_id": s_id,
            "source_type": row["source_type"],
            "label_source": row["label_source"],
            "ground_truth_zone": row["ground_truth_zone"],
            "ground_truth_count": row["ground_truth_count"],
            "motion_state": row["motion_state"],
            "mapping_verified": row["mapping_verified"],
            "zone_matches_physical_log": row["zone_matches_physical_log"],
            "count_matches_physical_log": row["count_matches_physical_log"],
            "count_match_strict": row["count_match_strict"],
            "ts_valid": row["ts_valid"],
            "audited_candidate_only": is_inc,
            "exclusion_reason": row["exclusion_reason"]
        })
        
        provenance_rows.append({
            "session_id": s_id,
            "source_type": row["source_type"],
            "csv_rows": row["csv_rows"],
            "meta_records": row["meta_records"],
            "count_diff": row["count_diff"],
            "duration_s": row["calculated_duration_s"],
            "meta_duration_s": row["meta_duration_s"],
            "ts_min": row["ts_min"],
            "ts_max": row["ts_max"],
            "ts_non_epoch_count": row["ts_non_epoch_count"],
            "interleaved_stream_order": row["interleaved_stream_order"],
            "exact_row_duplicates": row["exact_row_duplicates"],
            "quantized_ts_mac_collisions": row["quantized_ts_mac_collisions"],
            "known_mac_frames": row["known_mac_frames"],
            "unknown_mac_frames": row["unknown_mac_frames"],
            "label_source": row["label_source"],
            "ground_truth_zone": row["ground_truth_zone"],
            "ground_truth_count": row["ground_truth_count"],
            "mapping_verified": row["mapping_verified"],
            "audit_status": "ELIGIBLE_CANDIDATE" if is_inc else "EXCLUDED",
            "notes": "Passed all strict audit criteria" if is_inc else row["exclusion_reason"]
        })
        
        if not is_inc:
            excluded_rows.append({
                "session_id": s_id,
                "reason": row["exclusion_reason"],
                "csv_rows": row["csv_rows"],
                "meta_records": row["meta_records"],
                "relabel_possible": ("Fluctuating" in str(row["exclusion_reason"]) or "mismatch" in str(row["exclusion_reason"])),
                "action_required": "Retain in raw quarantine; requires fresh repeatable recording in Phase B"
            })
        else:
            # Copy candidate session files and verify cryptographic SHA-256 identity
            src_dir = Path("data/raw") / s_id
            dst_sess_dir = candidates_dir / s_id
            dst_sess_dir.mkdir(exist_ok=True)
            
            for f in src_dir.glob("*.*"):
                src_hash = compute_file_sha256(f)
                dst_file = dst_sess_dir / f.name
                shutil.copy2(f, dst_file)
                dst_hash = compute_file_sha256(dst_file)
                
                # Cryptographic assertion: Bit-for-bit identity
                assert src_hash == dst_hash, f"Hash mismatch during copy of {f.name}!"
                
                hash_verification_rows.append({
                    "session_id": s_id,
                    "filename": f.name,
                    "source_path": str(f),
                    "destination_path": str(dst_file),
                    "source_sha256": src_hash,
                    "destination_sha256": dst_hash,
                    "verification_status": "IDENTICAL_BIT_FOR_BIT",
                    "bytes_verified": f.stat().st_size
                })
                print(f"  [+] Copied & Verified: {s_id}/{f.name} (SHA-256: {src_hash[:16]}...)")
                
    # Export all reports
    if not df_orphans.empty:
        df_orphans.to_csv(audit_dir / "orphan_missing_metadata.csv", index=False)
    pd.DataFrame(manifest_rows).to_csv(base_dir / "manifest.csv", index=False)
    pd.DataFrame(provenance_rows).to_csv(audit_dir / "label_provenance.csv", index=False)
    pd.DataFrame(excluded_rows).to_csv(audit_dir / "excluded_sessions.csv", index=False)
    pd.DataFrame(hash_verification_rows).to_csv(audit_dir / "hash_verification_report.csv", index=False)
    
    print("\n" + "=" * 80)
    print(f"[+] Build Complete for '{base_dir}':")
    print(f"    - manifest.csv:                   {len(manifest_rows)} sessions cataloged")
    print(f"    - label_provenance.csv:           full provenance details")
    print(f"    - excluded_sessions.csv:          {len(excluded_rows)} excluded sessions with documented reasons")
    print(f"    - orphan_missing_metadata.csv:    {len(df_orphans)} orphan directories listed")
    print(f"    - hash_verification_report.csv:   {len(hash_verification_rows)} files cryptographically verified")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="WiMotion 2.0 Audited Manual Ground Truth Dataset Builder")
    parser.add_argument("--output-dir", type=str, default="data/processed/manual_gt_v1", help="Destination directory for processed dataset")
    parser.add_argument("--force-rebuild", action="store_true", help="Explicitly allow clearing and rebuilding existing output directory")
    args = parser.parse_args()
    
    build_processed_dataset(Path(args.output_dir), force_rebuild=args.force_rebuild)


if __name__ == "__main__":
    main()
