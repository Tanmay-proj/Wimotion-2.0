import pandas as pd
import json
from pathlib import Path

root = Path("data/raw/session_real_006_tx2_walk")
csv_path = next(root.glob("*.csv"))
json_path = next(root.glob("*.json"))
df = pd.read_csv(csv_path)
meta = json.loads(json_path.read_text(encoding="utf-8"))

print("Metadata zone:", meta.get("ground_truth_zone"))
print("Metadata count:", meta.get("ground_truth_count"))
print("Metadata motion:", meta.get("motion_state"))
print("\nRows:", len(df))
print("\nFrames per receiver and TX:")
print(df.groupby(["receiver", "tx", "source_mac"]).size().to_string())
print("\nUnique ground-truth labels:")
for col in ["ground_truth_zone", "ground_truth_count", "motion_state"]:
    if col in df.columns:
        print(col, "=", df[col].dropna().unique().tolist())
print("\nTX2 MAC present:", (df["source_mac"].astype(str).str.upper() == "1C:69:20:31:38:08").any())
