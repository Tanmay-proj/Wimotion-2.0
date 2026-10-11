#!/usr/bin/env python3
"""
Offline Reproducible Synthetic CSI Augmentation Utility.
Generates an augmented session from genuine benchmark capture with verified parent metadata.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from spatial.augmentation import create_augmented_session


def main():
    input_csv = ROOT / "data" / "raw" / "benchmark_session_01" / "multilink_data_Z3_1P_dynamic.csv"
    output_dir = ROOT / "data" / "raw" / "synthetic_session_01"

    if not input_csv.exists():
        print(f"[!] Error: Source benchmark CSV not found at {input_csv}")
        return 1

    print(f"[*] Reading genuine parent recording: {input_csv.name}")
    meta = create_augmented_session(
        input_csv_path=input_csv,
        output_dir=output_dir,
        parent_session_id="benchmark_session_01",
        output_session_id="synthetic_session_01",
        display_name="Synthetic Augmentation: Z3 Perturbed (Noise+Gain)",
        gain_variation=0.04,
        noise_std=0.03,
        seed=1337
    )

    print("[+] Successfully generated synthetic augmented session:")
    print(f"    - Session ID: {meta['session_id']}")
    print(f"    - Display Name: {meta['display_name']}")
    print(f"    - Source Type: {meta['source_type']}")
    print(f"    - Parent: {meta['parent_session_id']}")
    print(f"    - Records: {meta['total_records']}")
    print(f"    - Output Dir: {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
