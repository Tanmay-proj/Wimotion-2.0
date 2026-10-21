# CHAPTER 5: FEATURE ENGINEERING AND MACHINE LEARNING PIPELINE

---

## 5.1 Overview of the Processing Pipeline

The core task of WiMotion 2.0 is mapping continuous, high-dimensional multi-link Channel State Information (CSI) time-series into discrete spatial quadrant disturbance predictions ($Z_1, Z_2, Z_3, Z_4$, or `CLEAR`).

The signal processing architecture operates through a deterministic, five-stage transformation pipeline:

```
[STAGE 1: RAW BUFFER]    64-Subcarrier CSI records accumulated over 2.0s sliding window
                                             │
                                             ▼
[STAGE 2: PREPROCESSING] Clean non-finite samples; compute per-packet mean subcarrier amplitudes
                                             │
                                             ▼
[STAGE 3: LINK EXTRACTION]Partition records into 8 link groups; extract 6 temporal metrics per link
                                             │
                                             ▼
[STAGE 4: VECTOR FUSION] Fused into Canonical 56-Dimensional Representation (48 stats + 8 flags)
                                             │
                                             ▼
[STAGE 5: DUAL INFERENCE]├── Energy Gate Thresholding (theta = 1.80) -> Hard CLEAR Suppression
                         ├── Heuristic Multi-Link Ratio Baseline (argmax Normalized Variance)
                         └── Supervised Random Forest Classifier (100 Trees -> 5-Class Probabilities)
```

---

## 5.2 CSI Preprocessing and Signal-Quality Assessment

Raw subcarrier amplitudes captured by COTS ESP32 receivers exhibit occasional hardware artifacts, including Automatic Gain Control (AGC) step discontinuities and high-frequency thermal spikes. 

### 5.2.1 Subcarrier Amplitude Cleaning (`clean_amplitudes`)
For every incoming frame, the 64-element amplitude array $\mathbf{A} = [A_0, A_1, \dots, A_{63}]$ is cleaned via `spatial/features.py:clean_amplitudes`:
1. **Finite Verification:** All values are cast to 64-bit floating point; any non-finite values (`NaN` or $\pm\infty$) are filtered out.
2. **Physical Boundary Clamping:** Amplitudes are constrained to valid physical ADC dynamic ranges:
   $$\mathbf{A}_{\text{clean}} = \{ A_k \in \mathbf{A} \mid 0 \le A_k < 10,000 \}$$
3. **Packet-Level Summary Amplitude:** If valid subcarriers remain, the packet's overall signal amplitude is summarized as the arithmetic mean across subcarriers:
   $$\bar{A} = \frac{1}{|\mathbf{A}_{\text{clean}}|} \sum_{k \in \mathbf{A}_{\text{clean}}} A_k$$

### 5.2.2 Minimum Link Packet Threshold
To prevent noisy, under-sampled links from corrupting the spatial feature vector, a link group must contain a minimum of **3 valid packets** within the 2.0-second window ($N \ge 3$). If a link has fewer than 3 packets, its continuous features are imputed as zero and its validity flag is cleared.

---

## 5.3 Temporal Sliding Windows

Human locomotion exhibits characteristic physical timescales: a single step spans approximately 0.4 to 0.7 seconds, while traversing an entire quadrant spans 1.5 to 3.0 seconds. 

WiMotion 2.0 structures time-series data using temporal sliding windows defined by two parameters:
- **Window Duration ($T_w$):** Fixed at $2.0\text{ seconds}$. At a nominal frame rate of ~100 Hz per node, a 2.0-second window contains approximately 150 to 200 packets per link, providing robust sample sizes for statistical moments.
- **Window Step ($\Delta t$):** Configured at $0.5\text{ seconds}$, providing an inference update frequency of $2\text{ Hz}$.
- **Temporal Overlap:** Consecutive windows share $75\%$ of their temporal duration:
  $$\text{Overlap Ratio} = \frac{T_w - \Delta t}{T_w} = \frac{2.0 - 0.5}{2.0} = 75\%$$

---

## 5.4 Mathematical Formulation of the 56-Dimensional Feature Vector

A fundamental flaw in early wireless sensing literature is the vague or inconsistent definition of feature vectors between training scripts and production servers. WiMotion 2.0 enforces a strict **Canonical 56-Dimensional Schema** (`FEATURE_SCHEMA_VERSION = "2.0.0-canonical-56dim"`).

Across the 8 candidate links ($L_0$ to $L_7$), exactly **6 continuous temporal variation statistics** are extracted, followed by **8 binary link-validity flags**:

$$\mathbf{x} = \big[ \mathbf{f}_{L_0}, \mathbf{f}_{L_1}, \dots, \mathbf{f}_{L_7}, \; v_{L_0}, v_{L_1}, \dots, v_{L_7} \big] \in \mathbb{R}^{56}$$

### 5.4.1 The 6 Continuous Temporal Variation Metrics (per link)
Let $\mathbf{x} = [x_1, x_2, \dots, x_N]$ denote the sequence of mean packet amplitudes for link $L_i$ within the window, and let $\Delta x_j = x_{j+1} - x_j$ represent the first difference between consecutive packets ($j = 1, \dots, N-1$):

1. **Mean Amplitude (`mean_amp`):**
   $$\mu = \frac{1}{N} \sum_{j=1}^{N} x_j$$
   *Physical Meaning:* Reflects baseline path loss and macroscopic line-of-sight attenuation.

2. **Standard Deviation of Amplitude (`std_amp`):**
   $$\sigma = \sqrt{ \frac{1}{N} \sum_{j=1}^{N} (x_j - \mu)^2 }$$
   *Physical Meaning:* Quantifies total envelope perturbation magnitude caused by moving obstacles.

3. **Mean Absolute Amplitude Delta (`mean_delta`):**
   $$\mu_{|\Delta|} = \frac{1}{N-1} \sum_{j=1}^{N-1} |\Delta x_j|$$
   *Physical Meaning:* Captures packet-to-packet high-frequency variation rate; sensitive to rapid limb movements.

4. **Root-Mean-Square Amplitude Delta (`rms_delta`):**
   $$\text{RMS}_{\Delta} = \sqrt{ \frac{1}{N-1} \sum_{j=1}^{N-1} (\Delta x_j)^2 }$$
   *Physical Meaning:* Emphasizes large transient signal jumps caused by human footstep impacts.

5. **95th Percentile Absolute Delta (`p95_delta`):**
   $$P_{95} = \text{Quantile}_{0.95} \big( \{ |\Delta x_1|, |\Delta x_2|, \dots, |\Delta x_{N-1}| \} \big)$$
   *Physical Meaning:* Captures peak dynamic range spikes while rejecting isolated single-sample outliers.

6. **Mean Squared Temporal Variance (`energy` / `csi_variance`):**
   $$\sigma^2 = \frac{1}{N} \sum_{j=1}^{N} (x_j - \mu)^2$$
   *Physical Meaning:* Primary energy metric representing the total dynamic variance induced on the RF carrier.

### 5.4.2 The 8 Link-Validity Flags (`valid_RX_TX`)
For each of the 8 logical links, a binary indicator $v_{L_i} \in \{0.0, 1.0\}$ is appended:
$$v_{L_i} = \begin{cases} 1.0, & \text{if Link } L_i \text{ has } \ge 3 \text{ valid packets in window} \\ 0.0, & \text{otherwise} \end{cases}$$

This yields $8 \times 6 = 48\text{ continuous features} + 8\text{ binary flags} = \mathbf{56\text{ total dimensions}}$.

---

## 5.5 Link-Validity Flags and Missing-Data Handling

In real-world Wi-Fi environments, wireless links experience packet loss due to co-channel collisions, antenna orientation dips, or physical occlusions. 

WiMotion 2.0 handles missing links through deterministic zero-imputation:
- If Link $L_i$ has zero packets or fails the minimum packet threshold ($N < 3$), all 6 continuous features are imputed as exactly `0.0`, and $v_{L_i}$ is set to `0.0`.
- Because the Random Forest classifier splits on both continuous variance values and binary flags, the model natively learns that $v_{L_i} = 0.0$ signifies an unavailable link rather than a dead-quiet room.

---

## 5.6 Training and Inference Pipeline Consistency

A severe, widespread defect in machine learning projects is **train-serving skew**: where feature extraction logic in offline training scripts subtly diverges from live inference server code (e.g., different floating-point rounding, different subcarrier averaging orders, or missing link imputations).

In WiMotion 2.0, train-serving skew is mathematically prevented:
- **`spatial/features.py:build_canonical_56dim_feature_vector`** serves as the **single source of truth** across the entire repository.
- The offline dataset builder (`scripts/build_manual_gt_v1.py`), the model training pipeline (`scripts/train_spatial_model.py`), the replay loader (`spatial/replay_loader.py`), and the real-time server (`spatial/server.py`) import and call this exact same function.
- Automated unit test `test_feature_vector_parity_between_live_and_replay` strictly verifies that feeding identical raw packet arrays into live and offline pathways yields identical 56-D vectors with zero numerical difference.

---

## 5.7 Random Forest Classification

The primary supervised spatial localization model is a **Random Forest Classifier** (`RandomForestClassifier` from scikit-learn):
- **Ensemble Size:** 100 decorrelated decision trees ($B = 100$).
- **Splitting Criterion:** Gini Impurity:
  $$I_G(p) = 1 - \sum_{k=1}^{5} p_k^2$$
- **Max Features:** Evaluated at $\sqrt{56} \approx 7$ randomly sampled features per split.
- **Output Classes:** 5 mutually exclusive classes: `CLEAR`, `Z1`, `Z2`, `Z3`, and `Z4`.
- **Inference Latency:** Average inference time per 56-D vector is **$3.2\text{ milliseconds}$** on the host CPU, well within the 500 ms sliding window step budget.

---

## 5.8 Heuristic Spatial Estimation

Alongside the supervised machine learning model, WiMotion 2.0 maintains a deterministic, physical-layer **Heuristic Spatial Baseline (`SpatialBaseline`)**.

The heuristic algorithm operates by computing the normalized temporal variance of each link and assigning spatial disturbance to the quadrant whose primary LOS links exhibit maximum variance ratio:

$$\hat{Z}_{\text{heuristic}} = \arg\max_{k \in \{1,2,3,4\}} \left( \frac{\sigma^2_{\text{Link}(k)}}{\sum_{j=1}^{8} \sigma^2_{\text{Link}(j)}} \right)$$

If the maximum variance across all links is below an empirical idle threshold, the heuristic assigns `CLEAR`. This baseline serves as a direct point of comparison, demonstrating how much predictive power is added by machine learning versus simple energy ratio ranking.

---

## 5.9 Presence Gating and Prediction Quality Controls

Before passing a feature vector to the classifier, the server evaluates two pre-inference quality gates:

1. **Signal Rate Gate (`spatial/inference.py`):**
   The server monitors the real-time packet arrival rate across both receivers. If either receiver's rate drops below **$4.0\text{ Hz}$** or if total window packet count drops below 8, the state is locked to `INSUFFICIENT_DATA` and inference is suppressed.
2. **Calibrated CLEAR Energy Gate:**
   To address the high false-alarm rate in idle rooms, an empirical energy threshold $\theta = 1.80$ is evaluated. If $\max(\sigma^2_{L_0..L_7}) < 1.80$, the window is hard-gated to `CLEAR` without querying the decision trees (detailed in Chapter 6).

---

## 5.10 Limitations of the Current Feature Representation

While the 56-dimensional feature vector captures amplitude perturbations reliably, it exhibits two inherent physical limitations:
1. **Lack of Phase Sanitization:** Because raw CSI phase contains random carrier frequency offsets (CFO) and sampling frequency offsets (SFO), phase angles rotate uncontrollably across $[-\pi, +\pi]$ and cannot be directly fed to the model without conjugate phase subtraction.
2. **Environmental Non-Human Susceptibility:** Any moving non-human dielectric boundary—such as an open door swinging in a draught or fluttering metallic window blinds—produces temporal amplitude variance that the model cannot distinguish from human walking.

---
*(End of Chapter 5 — Source: spatial/features.py, spatial/inference.py, and models/spatial_model_scorecard.json)*
