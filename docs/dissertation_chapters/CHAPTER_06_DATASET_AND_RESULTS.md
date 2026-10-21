# CHAPTER 6: DATASET, EXPERIMENTAL METHODOLOGY AND RESULTS

---

## 6.1 Dataset Sources and Session Inventory

Empirical evaluation of WiMotion 2.0 was conducted across two distinct physical hardware capture campaigns in `ROOM_LAB_A`, totaling **172,974 physical CSI frames**:

1. **Phase A Exploratory Hardware Campaign (Sessions 001–007):** Comprises 116,588 frames captured across 7 long-duration sessions between October 15 and October 19, 2026. Captured during initial software integration and transmitter placement calibration.
2. **Phase B Controlled Hardware Campaign (`session_pB_*`):** Comprises 56,386 frames captured across 10 strictly scripted physical sessions on October 20, 2026. Designed with atomic file-write mutexes and structured as paired physical takes per class.

---

## 6.2 Historical Dataset Audit and Data Quarantine

A hallmark of rigorous engineering research is active auditing of data provenance. In late October 2026, an exhaustive read-only audit of all 17 historical recording sessions was executed using `scripts/audit_read_only_sessions.py` (documented in `docs/DATASET_AUDIT_REPORT.md`).

The audit cross-checked raw CSV packet rows against metadata JSON declarations and cryptographic file hashes, uncovering critical integrity anomalies:

### Table 6.1: Historical Dataset Audit & Quarantine Manifest

| Session Identifier | Motion Ground Truth | Declared Frames | Audited CSV Frames | Delta | Root Cause / Anomaly Observed | Audit Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: |
| `session_real_001` | Room Walk ($Z_1 \to Z_3$) | 14,200 | 13,850 | -350 | Serial thread-race packet drops before lock deployment | **QUARANTINED** |
| `session_real_002` | Desk Workstation ($Z_2$) | 16,500 | 16,110 | -390 | Thread contention during high-rate bursts | **QUARANTINED** |
| `session_real_003` | Empty Room Baseline | 12,000 | 11,820 | -180 | Intermittent USB-UART buffer overrun | **QUARANTINED** |
| `session_real_004` | Flank Walk ($Z_3$) | 15,000 | 14,640 | -360 | Non-epoch timestamp drift across receivers | **QUARANTINED** |
| `session_real_005` | Window Walk ($Z_4$) | 18,200 | 17,910 | -290 | Missing frame sequence numbers | **QUARANTINED** |
| `session_real_006` | Door Walk ($Z_1$) | 9,607 | 9,607 | 0 | Receiver timestamp-key collision in multi-RX merge | **QUARANTINED** |
| `session_real_007` | Perimeter Walk ($Z_4$) | 19,232 | 19,232 | 0 | Variable inter-packet arrival jitter (> 85 ms) | **QUARANTINED** |

### The Scientific Quarantine Decision
Rather than training machine learning models on sessions with dropped rows or ambiguous timestamp ordering, **all 116,588 frames across exploratory sessions 001–007 were formally quarantined**. They are retained strictly for diagnostic and offline stress-testing, and are **completely excluded from spatial model training and evaluation**.

---

## 6.3 Physical Hardware Data-Collection Campaign (Phase B)

Following the audit, the logging pipeline was refactored with atomic file-write mutexes (`threading.Lock`), and a new, strictly controlled hardware campaign (**Phase B**) was executed. 

Phase B captured **10 dedicated physical sessions** covering all five target classes (`CLEAR`, $Z_1$, $Z_2$, $Z_3$, $Z_4$):
- Each class was recorded in exactly two independent physical takes: **Take 01** and **Take 02**.
- All human motion sessions involved a single active human subject executing continuous, controlled walking loops within the designated quadrant boundaries.
- **Audit Verification:** All 10 Phase B sessions passed the audit with **100% strict match** between CSV rows and metadata headers, zero dropped frames, and strict monotonically increasing epoch timestamps.

### Table 6.2: Phase B Controlled Benchmark Dataset Inventory

| Session Identifier | Ground Truth | Physical Take | Partition Assignment | Raw Frames | 56-D Sliding Windows | Audit Result | Admitted to ML |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `session_pB_clear_01` | `CLEAR` | Take 01 | **Train Set** | 5,577 | 121 | 100% Strict Match | **Yes (Train)** |
| `session_pB_clear_02` | `CLEAR` | Take 02 | **Held-Out Test** | 5,538 | 121 | 100% Strict Match | **Yes (Test)** |
| `session_pB_z1_walk_01` | $Z_1$ (NE) | Take 01 | **Train Set** | 5,548 | 120 | 100% Strict Match | **Yes (Train)** |
| `session_pB_z1_walk_02` | $Z_1$ (NE) | Take 02 | **Held-Out Test** | 5,617 | 121 | 100% Strict Match | **Yes (Test)** |
| `session_pB_z2_walk_01` | $Z_2$ (NW) | Take 01 | **Train Set** | 6,021 | 121 | 100% Strict Match | **Yes (Train)** |
| `session_pB_z2_walk_02` | $Z_2$ (NW) | Take 02 | **Held-Out Test** | 5,579 | 121 | 100% Strict Match | **Yes (Test)** |
| `session_pB_z3_walk_01` | $Z_3$ (SW) | Take 01 | **Train Set** | 5,542 | 121 | 100% Strict Match | **Yes (Train)** |
| `session_pB_z3_walk_02` | $Z_3$ (SW) | Take 02 | **Held-Out Test** | 5,570 | 121 | 100% Strict Match | **Yes (Test)** |
| `session_pB_z4_walk_01` | $Z_4$ (SE) | Take 01 | **Train Set** | 5,572 | 121 | 100% Strict Match | **Yes (Train)** |
| `session_pB_z4_walk_02` | $Z_4$ (SE) | Take 02 | **Held-Out Test** | 5,832 | 121 | 100% Strict Match | **Yes (Test)** |
| **Phase B Totals** | **5 Classes** | **10 Takes** | **Balanced 50/50** | **56,386** | **1,209** | **10/10 PASS** | **100% Admitted** |

---

## 6.4 Session-Level Training and Held-Out Testing

In machine learning on time-series data, random window shuffling creates **catastrophic temporal leakage**: window $t$ (in train) shares 75% of its raw physical frames with window $t+0.5\text{s}$ (in test). This yields artificially inflated accuracies of 99% that instantly fail in practice.

WiMotion 2.0 strictly enforces a **Zero-Leakage Take-Based Partitioning Protocol**:
- **Train Set (604 Windows):** Exclusively contains Take 01 sessions (`clear_01`, `z1_01`, `z2_01`, `z3_01`, `z4_01`).
- **Held-Out Test Set (605 Windows):** Exclusively contains Take 02 sessions (`clear_02`, `z1_02`, `z2_02`, `z3_02`, `z4_02`).
- **Leakage Guarantee:** Zero physical or temporal overlap. Models are evaluated strictly on unseen physical capture takes.

---

## 6.5 Window Generation and Overlap Considerations

The 1,209 evaluated windows are 2.0-second sliding windows (0.5s step) extracted across the 10 physical sessions. 

An essential scientific disclosure must be emphasized: **1,209 windows represent continuous temporal observations across 10 physical recording sessions; they do NOT represent 1,209 independent physical setup runs or different days.** Adjacent windows possess ~75% physical sample overlap, which provides smooth real-time tracking during inference but increases temporal correlation within a given session.

---

## 6.6 Evaluation Metrics and Their Definitions

To evaluate spatial classification performance transparently, five standard metrics are reported:

1. **Overall Classification Accuracy:**
   $$\text{Accuracy} = \frac{\sum_{c=1}^{5} \text{TP}_c}{N_{\text{total}}} = \frac{\text{Correct Predictions}}{605}$$
2. **Weighted Macro F1-Score:** Harmonic mean of precision and recall weighted by class support:
   $$F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$
3. **Per-Zone Recall (Sensitivity):** Fraction of actual ground truth windows for Zone $k$ correctly identified:
   $$\text{Recall}_k = \frac{\text{TP}_k}{\text{TP}_k + \text{FN}_k} = \frac{\text{TP}_k}{121}$$
4. **CLEAR Class False-Alarm Rate ($\text{FPR}_{\text{CLEAR}}$):** Proportion of true empty-room windows misclassified as active human motion:
   $$\text{FPR}_{\text{CLEAR}} = \frac{\text{FP}_{\text{CLEAR}}}{\text{TN}_{\text{CLEAR}} + \text{FP}_{\text{CLEAR}}} = \frac{\text{Misclassified Empty Windows}}{121}$$
5. **CLEAR Recall (Specificity / True Negative Rate):**
   $$\text{Recall}_{\text{CLEAR}} = 1 - \text{FPR}_{\text{CLEAR}} = \frac{\text{Correctly Classified Empty Windows}}{121}$$

---

## 6.7 Empty-Room Behaviour and False Positives

When the multi-class Random Forest was initially evaluated on held-out Take 02 without energy gating, an acute failure mode emerged:
- **Ungated CLEAR False-Alarm Rate:** **$98.35\%$** (119 out of 121 empty-room windows were misclassified as human walking).
- **Physical Root Cause:** In an empty room, subtle thermal noise in the ESP32 receiver silicon and AP beacon jitter cause tiny amplitude ripples ($\sigma^2 \approx 0.1\text{ to }0.8$). The unconstrained decision trees overfitted to these micro-ripples and assigned them to whichever spatial zone had the nearest decision boundary.

---

## 6.8 Presence and Spatial Classification Results

To resolve the false-alarm crisis without introducing test leakage, an empirical energy gate threshold $\theta$ was scanned **exclusively on Take 01 training data**:
- Youden's $J$-statistic ($J = \text{Sensitivity} + \text{Specificity} - 1$) peaked at **$\theta = 1.80$** ($J = 0.204$).
- The threshold was frozen at $\theta = 1.80$ before evaluating held-out Take 02.
- **Gating Rule:** If $\max(\sigma^2_{L_0..L_7}) < 1.80$, the prediction is hard-gated to `CLEAR`; otherwise, the Random Forest prediction is emitted.

### Primary Model Performance (RandomForestClassifier, 100 Trees):
- **Ungated Test Accuracy:** **$50.91\%$** (Weighted F1: $50.22\%$)
- **Gated Test Accuracy ($\theta=1.80$):** **$49.26\%$** (Weighted F1: $48.25\%$)
- **CLEAR False-Alarm Rate:** Slashed from $98.35\%$ down to **$52.89\%$**
- **CLEAR Recall (TNR):** Boosted from $1.65\%$ (2/121) up to **$47.11\%$** (57/121)

---

## 6.9 Comparison of Heuristic and Learned Models

All models were evaluated on the exact same frozen held-out Take 02 partition (605 windows). Results are detailed in Table 6.3:

### Table 6.3: Comparative Benchmark on Held-Out Physical Split (Take 02)

| Model Architecture | Ungated Acc (%) | Gated Acc ($\theta=1.80$) | CLEAR Recall (%) | CLEAR FPR (%) | Delta vs Random Baseline |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Uniform Random Baseline (5 Classes)** | 20.00% | 20.00% | 20.00% | 80.00% | 0.00% (Reference) |
| **Wi-CaL Heuristic SpatialBaseline** | 29.26% | 29.26% | 70.00% (84/120) | 30.00% | +9.26% |
| **HistGradientBoostingClassifier** | 47.27% | 48.10% | 43.80% (53/121) | 56.20% | +28.10% |
| **Logistic Regression (L2 Regularized)** | 49.75% | 49.42% | 45.45% (55/121) | 54.55% | +29.42% |
| **RandomForestClassifier (Primary)** | **50.91%** | **49.26%** | **47.11% (57/121)** | **52.89%** | **+29.26%** |

Both linear and tree-based machine learning models substantially outperform the heuristic baseline ($29.26\%$) and exceed random chance ($20.0\%$) by **nearly 2.5 times**.

---

## 6.10 Per-Zone Performance and Error Analysis

A detailed breakdown across individual spatial quadrants reveals significant performance disparities across the four room sectors:

### Table 6.4: Per-Zone Classification Performance (Held-Out Take 02)

| Ground Truth Quadrant | Test Windows | Gated True Positives (TP) | Gated Recall (%) | Ungated Recall (%) | Primary Misclassification Tendency |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **CLEAR (Empty Room)** | 121 | 57 | **47.11%** | 1.65% | Misclassified as $Z_1$ (39 windows) |
| **Zone 1 ($Z_1$ - North-East)** | 121 | 61 | **50.41%** | 52.89% | Misclassified as `CLEAR` (21) and $Z_3$ (18) |
| **Zone 2 ($Z_2$ - North-West)** | 121 | 65 | **53.72%** | 53.72% | Misclassified as $Z_1$ (28) and `CLEAR` (15) |
| **Zone 3 ($Z_3$ - South-West)** | 121 | 17 | **14.05%** | 38.84% | Misclassified as `CLEAR` (53) and $Z_1$ (25) |
| **Zone 4 ($Z_4$ - South-East)** | 121 | 98 | **80.99%** | 86.78% | Misclassified as `CLEAR` (12) |

### Physical RF Explanation of the Zone 4 vs. Zone 3 Disparity
1. **Zone 4 Dominance (80.99% Recall):** Zone 4 is located directly adjacent to Receiver RX2. The short direct path length creates strong reflection coefficients and high signal-to-noise ratio (SNR) during walking, enabling 98 out of 121 windows to be correctly recognized.
2. **Zone 3 Degradation (14.05% Recall):** Zone 3 is located in the South-West corner, diagonally furthest from Receiver RX1 (North-East). The longer path distance introduces higher geometric path loss ($1/R^4$ for bistatic radar scatter). When the calibrated energy gate ($\theta=1.80$) was applied, lower-amplitude $Z_3$ walking signals fell below threshold and were classified as `CLEAR` (53 windows).

---

## 6.11 Effect of Energy Gating

Applying the calibrated energy gate introduces a fundamental engineering trade-off:
- **Benefit:** Drastic suppression of empty-room false alarms (from $98.35\%$ down to $52.89\%$), allowing 57 out of 121 empty windows to be correctly recognized as `CLEAR`.
- **Cost:** A slight penalty on weak, distant walking signals (such as Zone 3), nudging overall accuracy from $50.91\%$ down to $49.26\%$.
- **Scientific Conclusion:** In physical security and surveillance, cutting false alarms by half is vastly more critical than a nominal $1.6\%$ overall accuracy delta.

---

## 6.12 Confusion Matrix and Additional Result Plots

Below is the complete 5-class confusion matrix of the primary gated model evaluated on the 605 held-out test windows:

```
                          PREDICTED CLASS
                 CLEAR     Z1      Z2      Z3      Z4   │ Total │ Recall
       ─────────────────────────────────────────────────┼───────┼────────
        CLEAR   │  57      39      11      10       4   │  121  │ 47.11%
A       Z1      │  21      61      15      18       6   │  121  │ 50.41%
C       Z2      │  15      28      65      12       1   │  121  │ 53.72%
T       Z3      │  53      25      19      17       7   │  121  │ 14.05%
U       Z4      │  12       5       6       0      98   │  121  │ 80.99%
A       ─────────────────────────────────────────────────┼───────┼────────
L       Total   │ 158     158     116      57     116   │  605  │ Acc: 49.26%
```

All metrics and matrices are strictly reproducible and match `models/spatial_model_scorecard.json` (SHA-256: `786ed5b8...`).

---

## 6.13 Interpretation of Results and Experimental Limitations

The empirical findings establish three core scientific conclusions:
1. **Feasibility of COTS Spatial Sensing:** An array of $5 ESP32 chips can resolve human movement into discrete spatial quadrants without cameras or wearables, achieving 2.5 times better performance than random guessing.
2. **RF Baseline Geometry Dominance:** Sensing sensitivity is non-uniform; sectors closest to receivers achieve high accuracy (81% in $Z_4$), while distant diagonal sectors suffer from geometric attenuation (14% in $Z_3$).
3. **Boundary Between Prototype and Commercial Radar:** A 49.26% 5-class accuracy demonstrates a successful physical proof-of-concept, but also demonstrates that commercial-grade through-wall tracking requires multi-antenna Angle-of-Arrival (AoA) diversity.

---
*(End of Chapter 6 — Source: models/spatial_model_scorecard.json, docs/PHASE_B_HONEST_SCORECARD.md, and scripts/run_master_evaluation.py)*
