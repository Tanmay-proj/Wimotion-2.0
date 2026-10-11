# WiMotion 2.0 — Scientific Evaluation & Validation Report

**Generated:** 2026-10-11 02:04:09 UTC  
**Methodology:** Rigorous multi-track evaluation separating untouched held-out sessions from in-session benchmarks, public datasets, and synthetic augmentation.

## 1. Dual-Engine Architecture Summary

| Component | Engine / Algorithm | Input Representation | Responsibility | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Presence Gating** | Original WiMotion HistGradientBoosting (v2.4) | 217 temporal-spectral features extracted per link stream | Binary Presence Detection (`empty_room` vs `human_present`) | **Active ML Model via Adapter** |
| **Spatial Sector Localization** | WiMotion 2.0 SpatialBaseline | Distributed 8-link CSI variance ratio ($argmax$) | Four-Quadrant Sector Mapping (Z1 NE, Z2 NW, Z3 SW, Z4 SE) | **Active Spatial Heuristic** |

## 2. Track A: Untouched Held-Out Hardware Evaluation

> [!IMPORTANT]
> Held-out sessions were recorded on genuine ESP32 hardware and remained completely untouched during model training. This provides an unbiased measure of generalization across distinct physical capture sessions.
> Note on Zero-Denominator Metrics: For sessions with 0 actual positives (e.g. pure Empty Room), Recall is mathematically Undefined (`N/A`), not 100%. Similarly, for sessions with 0 actual negatives, Specificity is Undefined (`N/A`).

| Session ID | Class | Total Windows | Valid / Invalid | ML Accuracy | ML Precision | ML Recall | ML Specificity | ML F1 | TP / FP / TN / FN |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `held_out_empty_01` | Empty Room | 44 | 37 / 7 | 51.35% | 0.0% | N/A (Undefined) | 51.35% | 0.0% | 0 / 18 / 19 / 0 |
| `held_out_walking_01` | Walking Presence | 65 | 59 / 6 | 100.0% | 100.0% | 100.0% | N/A (Undefined) | 100.0% | 59 / 0 / 0 / 0 |
| **COMBINED HELD-OUT** | **Imbalanced (44E / 65W)** | **109** | **96 / 13** | **81.25%** | **76.62%** | **100.0%** | **51.35%** | **86.76%** | **59 / 18 / 19 / 0** |

## 3. Track B, C, D & E: Benchmark, Public, Synthetic, and Scripted Results

| Track | Session ID | Provenance | Windows | Mean Rate | ML Accuracy | Spatial Heuristic Accuracy | Zone Hit (%) | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Track B: In-Session Hardware | `benchmark_session_01` | **HARDWARE_RECORDED** | 40 | 154.0 Hz | 35.9% | 90.0% | 60.0% | Physical RF capture |
| Track C: Public Benchmark | `public_esp_fi_01` | **PUBLIC_DATASET** | 20 | 144.0 Hz | 36.84% | 95.0% | 55.0% | AutoSmartGroup ESP-Fi HAR |
| Track D: Synthetic Augmentation | `synthetic_session_01` | **SYNTHETIC_AUGMENTED** | 40 | 154.0 Hz | 46.15% | 90.0% | 60.0% | Perturbed RF gain + noise |
| Track E: Scripted Presentation | `demo_session` | **SCRIPTED_PRESENTATION** | 191 | 119.0 Hz | N/A (Undefined) | 100.0% | 47.12% | Scripted video sync scenario (Synthetic RF tone lacks physical Doppler) |

## 4. Scientific Disclosures & Limitations

1. **Actual ML Model vs. Spatial Heuristic**: The reported ML Presence metrics are calculated using the real `HistGradientBoostingClassifier` executing over the 217-feature extraction pipeline. Spatial sector localization is driven by the multi-link variance ratio heuristic (`SpatialBaseline`), not by a multi-class learned spatial model.
2. **Zero-Denominator & Undefined Metric Transparency**: For single-class evaluation sessions (e.g. Empty Room with 0 positive ground truth samples), Recall is mathematically Undefined (`N/A`) rather than an inflated 100%. Similarly, Specificity is Undefined for sessions with 0 negative samples.
3. **Invalid Prediction Handling**: Any window where model availability is False or predictions are missing/invalid is explicitly tracked as `invalid_windows`. The evaluation suite never silently converts unclassified/missing predictions into `empty_room`.
4. **Window Overlap & Scope Disclosure**: Sliding windows (2.0s duration, 0.5s step) contain temporal overlap between consecutive time slices. The reported 81.25% held-out accuracy represents measured performance on these two genuine benchmark recordings (`held_out_empty_01` and `held_out_walking_01`) across 96 valid evaluated windows (with 13 warm-up windows tracked as invalid), not an unbounded claim of universal real-world accuracy across arbitrary rooms.
5. **Sample Imbalance Disclosure**: The held-out benchmark contains 44 Empty Room windows and 65 Walking Presence windows (40.4% / 59.6% ratio). It is not perfectly balanced 50/50.
6. **Physical Hardware Kit**: Physical hardware available in the lab consists of **4 COTS ESP32 boards** (typically deployed as 1 Master RX + 3 TX beacons or 2 RX + 2 TX). The 2 RX + 4 TX (6 nodes, 8 links) architecture represents the complete theoretical Wi-CaL grid supported by the firmware and dashboard software.
7. **Safe Standby Status**: Live serial ingestion on host is maintained in Safe Standby (Disconnected) by default to prevent Windows USB UART driver DPC watchdog timeouts until dedicated hardware ports are plugged in.
8. **Scripted Demo Role**: The 95-second dual-person scenario (`demo_session`) is strictly a presentation-mode tool for synchronizing with physical room videos; it is **never** presented as empirical hardware verification.