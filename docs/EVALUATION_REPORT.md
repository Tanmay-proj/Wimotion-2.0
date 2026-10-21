# WiMotion 2.0 — Scientific Evaluation & Validation Report

**Generated:** 2026-10-18 18:15:00 UTC  
**Methodology:** Rigorous multi-track evaluation separating genuine physical hardware sessions from software-generated benchmarks, unverified public imports, synthetic variants, and scripted presentations.

## 1. Dual-Engine Architecture Summary

| Component | Engine / Algorithm | Input Representation | Responsibility | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Presence Gating** | Original WiMotion HistGradientBoosting (v2.4) | 217 temporal-spectral features extracted per link stream | Binary Presence Detection (`empty_room` vs `human_present`) | **Active ML Model via Adapter** |
| **Spatial Sector Localization** | WiMotion 2.0 SpatialBaseline | Distributed 8-link CSI variance ratio ($argmax$) | Four-Quadrant Sector Mapping (Z1 NE, Z2 NW, Z3 SW, Z4 SE) | **Active Spatial Heuristic** |

## 2. Track A: Genuine Single-Link Hardware Evaluation

> [!IMPORTANT]
> Track A sessions were recorded on genuine ESP32 hardware (RX1-TX1 single-link) during original WiMotion v1 physical trials and remained untouched during WiMotion 2.0 multi-link development.
> Note on Zero-Denominator Metrics: For sessions with 0 actual ground truth positives (pure Empty Room), Recall is mathematically Undefined (`N/A`). For sessions with 0 actual negatives, Specificity is Undefined (`N/A`).
> Valid Accuracy is computed strictly over classified windows (`valid_windows`); Coverage reports the classified window percentage.

| Session ID | Provenance | Total Windows | Valid / Invalid | Coverage | Valid ML Accuracy | Conservative All-Window | ML Precision | ML Recall | ML Specificity | ML FPR | ML F1 | TP / FP / TN / FN |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `held_out_empty_01` | `hardware_recorded_single_link` | 44 | 37 / 7 | 84.09% | 51.35% | 43.18% | 0.0% | N/A (Undefined) | 51.35% | 48.65% | 0.0% | 0 / 18 / 19 / 0 |
| `held_out_walking_01` | `hardware_recorded_single_link` | 65 | 59 / 6 | 90.77% | 100.0% | 90.77% | 100.0% | 100.0% | N/A (Undefined) | N/A (Undefined) | 100.0% | 59 / 0 / 0 / 0 |
| **COMBINED TRACK A** | **hardware_single_link** | **109** | **96 / 13** | **88.07%** | **81.25%** | **71.56%** | **76.62%** | **100.0%** | **51.35%** | **48.65%** | **86.76%** | **59 / 18 / 19 / 0** |

## 3. Phase 5: Per-Link Presence Model Evaluation Breakdown

> [!IMPORTANT]
> As established by the scientific audit, each physical RX-TX wireless link experiences unique multipath, antenna orientations, and propagation characteristics. Evaluating the V1 presence model independently per physical link ensures we do not assume uniform link performance across the multi-link mesh.

| Session ID | Link ID | Total Windows | Valid / Invalid | Coverage | Valid Accuracy | Recall | Specificity | False Positive Rate | F1 Score | Confusion Matrix |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `held_out_empty_01` | `RX1-TX1` | 37 | 37 / 0 | 100.0% | 51.35% | N/A (Undefined) | 51.35% | 48.65% | 0.0% | TP=0, FP=18, TN=19, FN=0 |
| `held_out_walking_01` | `RX1-TX1` | 59 | 59 / 0 | 100.0% | 100.0% | 100.0% | N/A (Undefined) | N/A (Undefined) | 100.0% | TP=59, FP=0, TN=0, FN=0 |
| `benchmark_session_01` | `RX1-TX1` | 39 | 39 / 0 | 100.0% | 35.9% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=14, FN=25 |
| `benchmark_session_01` | `RX1-TX2` | 39 | 39 / 0 | 100.0% | 35.9% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=14, FN=25 |
| `benchmark_session_01` | `RX1-TX3` | 39 | 39 / 0 | 100.0% | 35.9% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=14, FN=25 |
| `benchmark_session_01` | `RX1-TX4` | 39 | 39 / 0 | 100.0% | 35.9% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=14, FN=25 |
| `benchmark_session_01` | `RX2-TX1` | 39 | 39 / 0 | 100.0% | 35.9% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=14, FN=25 |
| `benchmark_session_01` | `RX2-TX2` | 39 | 39 / 0 | 100.0% | 35.9% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=14, FN=25 |
| `benchmark_session_01` | `RX2-TX3` | 39 | 39 / 0 | 100.0% | 35.9% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=14, FN=25 |
| `benchmark_session_01` | `RX2-TX4` | 39 | 39 / 0 | 100.0% | 35.9% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=14, FN=25 |
| `public_esp_fi_01` | `RX1-TX1` | 19 | 19 / 0 | 100.0% | 36.84% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=7, FN=12 |
| `public_esp_fi_01` | `RX1-TX2` | 19 | 19 / 0 | 100.0% | 36.84% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=7, FN=12 |
| `public_esp_fi_01` | `RX1-TX3` | 19 | 19 / 0 | 100.0% | 36.84% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=7, FN=12 |
| `public_esp_fi_01` | `RX1-TX4` | 19 | 19 / 0 | 100.0% | 36.84% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=7, FN=12 |
| `public_esp_fi_01` | `RX2-TX1` | 19 | 19 / 0 | 100.0% | 36.84% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=7, FN=12 |
| `public_esp_fi_01` | `RX2-TX2` | 19 | 19 / 0 | 100.0% | 36.84% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=7, FN=12 |
| `public_esp_fi_01` | `RX2-TX3` | 19 | 19 / 0 | 100.0% | 36.84% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=7, FN=12 |
| `public_esp_fi_01` | `RX2-TX4` | 19 | 19 / 0 | 100.0% | 36.84% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=7, FN=12 |
| `synthetic_session_01` | `RX1-TX1` | 39 | 39 / 0 | 100.0% | 35.9% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=14, FN=25 |
| `synthetic_session_01` | `RX1-TX2` | 39 | 39 / 0 | 100.0% | 35.9% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=14, FN=25 |
| `synthetic_session_01` | `RX1-TX3` | 39 | 39 / 0 | 100.0% | 43.59% | 12.0% | 100.0% | 0.0% | 21.43% | TP=3, FP=0, TN=14, FN=22 |
| `synthetic_session_01` | `RX1-TX4` | 39 | 39 / 0 | 100.0% | 35.9% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=14, FN=25 |
| `synthetic_session_01` | `RX2-TX1` | 39 | 39 / 0 | 100.0% | 35.9% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=14, FN=25 |
| `synthetic_session_01` | `RX2-TX2` | 39 | 39 / 0 | 100.0% | 35.9% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=14, FN=25 |
| `synthetic_session_01` | `RX2-TX3` | 39 | 39 / 0 | 100.0% | 38.46% | 4.0% | 100.0% | 0.0% | 7.69% | TP=1, FP=0, TN=14, FN=24 |
| `synthetic_session_01` | `RX2-TX4` | 39 | 39 / 0 | 100.0% | 35.9% | 0.0% | 100.0% | 0.0% | 0.0% | TP=0, FP=0, TN=14, FN=25 |

## 4. Track B, C, D & E: Software Benchmarks, Imports, Synthetic, and Scripted Results

| Track | Session ID | Provenance | Total Windows | Valid / Invalid | Mean Rate | ML Valid Accuracy | Spatial Heuristic Accuracy | Zone Hit (%) | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Track B: Generated Benchmark | `benchmark_session_01` | `synthetic_generated_benchmark` | 40 | 39 / 1 | 154.0 Hz | 35.9% | 90.0% | 60.0% | Software-generated 8-link benchmark (scripts/create_benchmark_session.py) |
| Track C: Unverified Public Import | `public_esp_fi_01` | `unverified_import` | 20 | 19 / 1 | 144.0 Hz | 36.84% | 95.0% | 55.0% | Locally formatted test sample; origin unverified against raw upstream capture |
| Track D: Synthetic Augmentation | `synthetic_session_01` | `synthetic_augmented` | 40 | 39 / 1 | 154.0 Hz | 46.15% | 90.0% | 60.0% | Perturbed RF gain + noise derived from benchmark_session_01 |
| Track E: Scripted Presentation | `demo_session` | `scripted_presentation` | 191 | 0 / 191 | 119.0 Hz | N/A (Undefined) | 100.0% | 47.12% | Scripted presentation scenario (Synthetic flat RF tones lack Doppler micro-dynamics -> ML invalid) |

## 5. Scientific Disclosures & Limitations

1. **Actual ML Model vs. Spatial Heuristic**: The reported ML Presence metrics are calculated using the real `HistGradientBoostingClassifier` executing over the 217-feature extraction pipeline. Spatial sector localization is driven by the multi-link variance ratio heuristic (`SpatialBaseline`), not by an end-to-end multi-class learned spatial neural network.
2. **Zero-Denominator & Undefined Metric Transparency**: For single-class evaluation sessions (e.g. Empty Room with 0 positive ground truth samples), Recall is mathematically Undefined (`N/A`) rather than an inflated 100%. Similarly, Specificity is Undefined for sessions with 0 negative samples.
3. **Coverage & Invalid Window Policy**: Windows where model predictions are unavailable or buffer is warming up (< 5 frames per link) are tracked explicitly as `invalid_windows`. Valid Accuracy is defined as `(TP + TN) / valid_windows * 100`. The conservative All-Window score counts invalid windows as failures.
4. **Window Overlap & Scope Disclosure**: Sliding windows (2.0s duration, 0.5s step) contain ~75% temporal overlap between consecutive time slices. The reported 81.25% valid held-out accuracy represents measured performance on these two genuine WiMotion v1 benchmark recordings across 96 valid evaluated windows, not an unbounded claim of universal real-world accuracy across arbitrary environments.
5. **Sample Imbalance Disclosure**: The held-out benchmark contains 44 Empty Room windows and 65 Walking Presence windows (40.4% / 59.6% ratio). It is not perfectly balanced 50/50.
6. **Training vs. Replay Window Duration**: The original model was trained on 1.0-second sliding windows (`window_duration_sec: 1.0`), while WiMotion 2.0 multi-link live/replay sliding window buffer uses 2.0-second windows with 0.5s step. Resampling interpolates onto uniform grids, but the duration difference is an explicit engineering limitation.
7. **Physical Hardware Deployment Evolution**: In initial single-link trials and early lab demonstrations, 4 physical ESP32 boards were deployed. On October 20, 2026, a complete 6-node array (2 Receivers + 4 Transmitters) was deployed in the room mesh to record the 10 Phase B controlled benchmark sessions (1,209 windows across 8 concurrent physical links; see [Phase B Honest Scorecard](PHASE_B_HONEST_SCORECARD.md)).
8. **Phase B Supervised Multi-Link Model (Phase 6)**: The supervised 5-class model trained on Take 01 sessions achieved 47.27% accuracy on held-out Take 02 sessions, outperforming the heuristic baseline (29.26%) and random chance (20.00%). Empty-room false-positive rate remains high (98.35%) without prior hard energy gating, confirming that idle RF variations can be misclassified as active motion sectors.
9. **Safe Standby Status**: Live serial ingestion on host is maintained in Safe Standby (Disconnected) by default to prevent Windows USB UART driver DPC watchdog timeouts until dedicated hardware ports are plugged in.
10. **Scripted Demo Role**: The 95-second dual-person scenario (`demo_session`) is strictly a presentation-mode tool for synchronizing with physical room videos; it is **never** presented as empirical hardware verification.