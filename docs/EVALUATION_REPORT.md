# WiMotion 2.0 — Scientific Evaluation & Validation Report

**Generated:** 2026-10-11 01:46:42 UTC  
**Methodology:** Rigorous multi-track evaluation separating untouched held-out sessions from in-session benchmarks, public datasets, and synthetic augmentation.

## 1. Dual-Engine Architecture Summary

| Component | Engine / Algorithm | Input Representation | Responsibility | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Presence Gating** | Original WiMotion HistGradientBoosting (v2.4) | 217 temporal-spectral features extracted per link stream | Binary Presence Detection (`empty_room` vs `human_present`) | **Active ML Model via Adapter** |
| **Spatial Sector Localization** | WiMotion 2.0 SpatialBaseline | Distributed 8-link CSI variance ratio ($argmax$) | Four-Quadrant Sector Mapping (Z1 NE, Z2 NW, Z3 SW, Z4 SE) | **Active Spatial Heuristic** |

## 2. Track A: Untouched Held-Out Hardware Evaluation

> [!IMPORTANT]
> Held-out sessions were recorded on genuine ESP32 hardware and remained completely untouched during model training. This provides an unbiased measure of true generalization across distinct sessions.

| Session ID | Class | Windows | ML Accuracy | ML Precision | ML Recall | ML F1 | TP / FP / TN / FN |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `held_out_empty_01` | Empty Room | 44 | 59.09% | 0.0% | 100.0% | 0.0% | 0 / 18 / 26 / 0 |
| `held_out_walking_01` | Walking Presence | 65 | 90.77% | 100.0% | 90.77% | 95.16% | 59 / 0 / 0 / 6 |
| **COMBINED HELD-OUT** | **Balanced 50/50** | **109** | **77.98%** | **76.62%** | **90.77%** | **83.1%** | **59 / 18 / 26 / 6** |

## 3. Track B, C, D & E: Benchmark, Public, Synthetic, and Scripted Results

| Track | Session ID | Provenance | Windows | Mean Rate | ML Accuracy | Spatial Heuristic Accuracy | Zone Hit (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Track B: In-Session Hardware | `benchmark_session_01` | **HARDWARE_RECORDED** | 40 | 154.0 Hz | 37.5% | 90.0% | 60.0% |
| Track C: Public Benchmark | `public_esp_fi_01` | **PUBLIC_DATASET** | 20 | 144.0 Hz | 40.0% | 95.0% | 55.0% |
| Track D: Synthetic Augmentation | `synthetic_session_01` | **SYNTHETIC_AUGMENTED** | 40 | 154.0 Hz | 47.5% | 90.0% | 60.0% |
| Track E: Scripted Presentation | `demo_session` | **SCRIPTED_PRESENTATION** | 191 | 119.0 Hz | 37.17% | 100.0% | 47.12% |

## 4. Scientific Disclosures & Limitations

1. **Actual ML Model vs. Heuristic**: The reported ML Presence metrics are calculated using the real `HistGradientBoostingClassifier` executing over the 217-feature extraction pipeline. Spatial sector localization is driven by the multi-link variance ratio heuristic (`SpatialBaseline`), not by a multi-class learned spatial model.
2. **Window Overlap Disclosure**: In-session sliding windows (2.0s duration, 0.5s step) contain temporal overlap. Cross-session held-out evaluation (Track A) provides the only true session-independent validation.
3. **Physical Hardware Kit**: Physical hardware available in the lab consists of **4 COTS ESP32 boards** (typically deployed as 1 Master RX + 3 TX beacons or 2 RX + 2 TX). The 2 RX + 4 TX (6 nodes, 8 links) architecture represents the complete theoretical Wi-CaL grid supported by the firmware and dashboard software.
4. **Safe Standby Status**: Live serial ingestion on host is maintained in Safe Standby (Disconnected) by default to prevent Windows USB UART driver DPC watchdog timeouts until dedicated hardware ports are plugged in.
5. **Scripted Demo Role**: The 95-second dual-person scenario (`demo_session`) is strictly a presentation-mode tool for synchronizing with physical room videos; it is **never** presented as empirical hardware verification.