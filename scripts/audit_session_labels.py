import glob
import json
import pandas as pd
from pathlib import Path

sessions = sorted(glob.glob('data/raw/session_real_*'))
print(f"Found {len(sessions)} real sessions.\n" + "="*60)

for s in sessions:
    csvs = glob.glob(f'{s}/*.csv')
    jsons = glob.glob(f'{s}/*.json')
    s_name = Path(s).name
    print(f"\nSession: {s_name}")
    
    if jsons:
        with open(jsons[0]) as f:
            meta = json.load(f)
            print(f"  [METADATA JSON]")
            print(f"    Zone: {meta.get('ground_truth_zone', meta.get('ground_truth_zones'))}")
            print(f"    Count: {meta.get('ground_truth_count')}")
            print(f"    Motion: {meta.get('motion_state')}")
            print(f"    Notes: {meta.get('notes')}")
            
    if csvs:
        df = pd.read_csv(csvs[0], encoding='utf-8', encoding_errors='replace', low_memory=False)
        total_rows = len(df)
        gt_zones = df['ground_truth_zone'].unique().tolist() if 'ground_truth_zone' in df.columns else ['N/A']
        gt_counts = df['ground_truth_count'].unique().tolist() if 'ground_truth_count' in df.columns else ['N/A']
        motions = df['motion_state'].unique().tolist() if 'motion_state' in df.columns else ['N/A']
        print(f"  [RAW CSV] Total rows: {total_rows}")
        print(f"    Unique ground_truth_zone: {gt_zones}")
        print(f"    Unique ground_truth_count: {gt_counts}")
        print(f"    Unique motion_state: {motions}")
