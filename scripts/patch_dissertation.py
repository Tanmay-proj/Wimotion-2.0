"""
Insert Figure 6.1, 6.2, 6.3, 6.4 into Chapter 6 of docs/MASTER_DISSERTATION_FINAL.md
"""

from pathlib import Path

MD_PATH = Path(__file__).resolve().parent.parent / "docs" / "MASTER_DISSERTATION_FINAL.md"

with open(MD_PATH, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Figure 6.2 before Table 6.3
target_1 = "### Table 6.3: Comparative Benchmark on Held-Out Physical Split (Take 02)"
if "Figure 6.2" not in text and target_1 in text:
    replacement_1 = "* **[Figure 6.2: Quantitative Accuracy Comparison Across Model Architectures and Physical Baselines]**\n\n" + target_1
    text = text.replace(target_1, replacement_1)
    print("[+] Added Figure 6.2 callout.")

# 2. Figure 6.3 before Table 6.4
target_2 = "### Table 6.4: Per-Zone Classification Performance (Held-Out Take 02)"
if "Figure 6.3" not in text and target_2 in text:
    replacement_2 = "* **[Figure 6.3: Per-Class Spatial Recall Sensitivity Highlighting Zone 4 Peak Sensitivity and Zone 3 Diagonal Path Attenuation]**\n\n" + target_2
    text = text.replace(target_2, replacement_2)
    print("[+] Added Figure 6.3 callout.")

# 3. Figure 6.4 in Section 6.11
target_3 = "Applying the calibrated energy gate introduces a fundamental engineering trade-off:"
if "Figure 6.4" not in text and target_3 in text:
    replacement_3 = "* **[Figure 6.4: Impact of Empirical Energy Gating on Empty-Room False Alarm Reduction]**\n\n" + target_3
    text = text.replace(target_3, replacement_3)
    print("[+] Added Figure 6.4 callout.")

# 4. Figure 6.1 in Section 6.12
target_4 = "Below is the complete 5-class confusion matrix of the primary gated model evaluated on the 605 held-out test windows:"
if "Figure 6.1" not in text and target_4 in text:
    replacement_4 = "* **[Figure 6.1: Detailed 5x5 Confusion Matrix of Primary Gated Random Forest Classifier (Take 02 Held-Out Test Set)]**\n\n" + target_4
    text = text.replace(target_4, replacement_4)
    print("[+] Added Figure 6.1 callout.")

with open(MD_PATH, "w", encoding="utf-8") as f:
    f.write(text)

print("[+] Figure callouts inserted successfully!")
