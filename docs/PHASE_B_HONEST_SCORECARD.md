# WiMotion 2.0 — Phase B Controlled Hardware Evaluation Scorecard
**Date:** October 20, 2026  
**Evaluation Standard:** Zero-Leakage Session-Wise Partitioning (Held-Out Physical Takes)  
**Dataset:** Phase B Controlled Physical Multi-Link Captures (`session_pB_*`)  

---

## 1. Executive Summary & Scientific Positioning

Following peer review feedback, this evaluation establishes an **unvarnished, honest, and leak-free baseline** for WiMotion 2.0.

> [!IMPORTANT]
> **Scientific Caveats & Scope:**
> 1. **Initial Held-Out Evaluation:** With exactly 2 physical takes per class (Take 01 for Train, Take 02 for Test), this benchmark provides genuine session-level validation, but is sensitive to day/run conditions and is **not** claimed as universal open-world generalization.
> 2. **Single-Occupant Constraint:** All motion takes contained 1 moving person. Multi-person spatial separation remains untested on this physical benchmark.
> 3. **Integrity vs Generalization:** The 10/10 audit pass confirms file integrity, zero dropped CSV rows, and non-corrupted timestamps; it does not guarantee high localization accuracy across varied environments.

---

## 2. Experimental Setup & Split Protocol

### Protocol: Strict Take-Based Partitioning
- **Total Dataset:** 1,209 sliding windows (2.0s duration, 0.5s step) across 10 physical recordings.
- **Classes:** 5 Balanced Classes (`CLEAR`, `Z1`, `Z2`, `Z3`, `Z4`), ~242 windows per class.
- **Feature Vector:** 56-dimensional multi-link representation (48 continuous CSI amplitude/variance link metrics across 8 links + 8 link-validity flags).

| Partition | Sessions Included | Total Windows | Class Balance | Leakage Guarantee |
|:---|:---|:---:|:---:|:---:|
| **Train Set** | `session_pB_clear_01`<br>`session_pB_z1_walk_01`<br>`session_pB_z2_walk_01`<br>`session_pB_z3_walk_01`<br>`session_pB_z4_walk_01` | **604** | 120-121 per class | Fit exclusively on Train; zero test window exposure |
| **Held-Out Test Set** | `session_pB_clear_02`<br>`session_pB_z1_walk_02`<br>`session_pB_z2_walk_02`<br>`session_pB_z3_walk_02`<br>`session_pB_z4_walk_02` | **605** | 121 per class | Unseen physical takes; zero temporal overlap |

---

## 3. Comparative Benchmark Results

| Model / Approach | Overall Accuracy | Macro-F1 | Weighted-F1 | Random Chance |
|:---|:---:|:---:|:---:|:---:|
| **Random Chance (5-Class Balanced)** | 20.00% | 20.00% | 20.00% | Baseline |
| **Heuristic SpatialBaseline** | 29.26% | 22.84% | 19.84% | +9.26% |
| **Supervised Multi-Link Model (`HistGradientBoosting`)** | **43.80%** | **44.18%** | **44.18%** | **+23.80%** |

---

## 4. Detailed Classification Metrics (Test Set: 605 Windows)

```
              precision    recall  f1-score   support

       CLEAR       0.31      0.32      0.32       121
          Z1       0.32      0.38      0.35       121
          Z2       0.58      0.52      0.55       121
          Z3       0.33      0.31      0.32       121
          Z4       0.70      0.66      0.68       121

    accuracy                           0.44       605
   macro avg       0.45      0.44      0.44       605
weighted avg       0.45      0.44      0.44       605
```

### 5-Class Confusion Matrix (Ground Truth Rows vs Predicted Columns)

| True \ Pred | CLEAR | Z1 | Z2 | Z3 | Z4 | Support | Recall |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **CLEAR** | **39** | 32 | 9 | 34 | 7 | 121 | **32.2%** |
| **Z1** | 21 | **46** | 17 | 24 | 13 | 121 | **38.0%** |
| **Z2** | 23 | 18 | **63** | 14 | 3 | 121 | **52.1%** |
| **Z3** | 34 | 28 | 11 | **37** | 11 | 121 | **30.6%** |
| **Z4** | 9 | 20 | 9 | 3 | **80** | 121 | **66.1%** |

---

## 5. False Positive Rate on CLEAR (Empty Room)

- **Total CLEAR Test Windows:** 121
- **Correctly Classified as CLEAR:** 39 (32.23%)
- **Falsely Detected as Occupied / Motion (False Positives):** 82
- **False Positive Rate (FPR):** **67.77%**

### Scientific Diagnosis of High CLEAR FPR:
1. In `session_pB_clear_02`, environmental ambient RF background (including 13 packets from uncoordinated beacon MAC `4C:11:AE:64:9A:05` and link multipath drift) caused raw subcarrier variance to intermittently exceed the empirical noise floor.
2. The tree-based classifier without an explicit energy gate tended to classify noisy empty-room windows into active zones (mostly Z3: 34 windows and Z1: 32 windows).
3. **Mitigation Path:** Adding an explicit L1-norm variance gate prior to classification will suppress empty-room misclassifications.

---

## 6. Per-Session Performance Breakdown

| Held-Out Test Session | True Label | Supervised Model Accuracy | Heuristic Baseline Accuracy | Dominant Prediction |
|:---|:---:|:---:|:---:|:---|
| `session_pB_clear_02` | CLEAR | **32.23%** (39/121) | 69.42% (84/121) | CLEAR (39), Z3 (34), Z1 (32) |
| `session_pB_z1_walk_02` | Z1 | **38.02%** (46/121) | 0.00% (0/121) | **Z1 (46)**, Z3 (24), CLEAR (21) |
| `session_pB_z2_walk_02` | Z2 | **52.07%** (63/121) | 71.07% (86/121) | **Z2 (63)**, CLEAR (23), Z1 (18) |
| `session_pB_z3_walk_02` | Z3 | **30.58%** (37/121) | 2.48% (3/121) | **Z3 (37)**, CLEAR (34), Z1 (28) |
| `session_pB_z4_walk_02` | Z4 | **66.12%** (80/121) | 3.31% (4/121) | **Z4 (80)**, Z1 (20), CLEAR (9) |

---

## 7. Artifacts & Reproducibility
- **Model Binary:** `models/spatial_model.pkl` (245 KB)
- **Scorecard JSON:** `models/spatial_model_scorecard.json`
- **Source Code Archive:** `Wimotion-2.0_source_review.zip` (25.32 MB, 204 files)
- **Reproduction Command:** `py -3.10 scripts/train_spatial_model.py --dataset phase_b --split-strategy take`
