# WiMotion 2.0 — Scientific Evaluation & Validation Report

**Generated:** 2026-10-11 01:14:55 UTC  
**Evaluation Methodology:** In-session sliding window (2.0s duration, 0.5s step) across verified hardware captures, public datasets, and synthetic augmentation.

## 1. Multi-Model Architecture Summary

| Component | Model / Heuristic | Input Dimension | Role | Validation Accuracy |
| :--- | :--- | :--- | :--- | :--- |
| **Original WiMotion Stage-1** | HistGradientBoosting (v2.4) | 217 engineered features | Link Presence Gating | 94.74% CV (10 sessions) |
| **Original WiMotion Baseline** | ExtraTreesClassifier | 217 engineered features | Zero-Leakage Benchmark | 70.46% CV (in-fold tare) |
| **WiMotion 2.0 Spatial Engine** | Multi-Link Wi-CaL Variance | 8-link distributed mesh | Sector / Quadrant Mapping | Validated on RX1/RX2 Mesh |

## 2. Experimental Benchmark Results

| Session ID | Provenance Source | Duration | Valid Frames | Mean Rate (Hz) | Presence Acc (%) | Zone Hit Rate (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `benchmark_session_01` | **HARDWARE_RECORDED** | 19.95s | 40 | 154.0 | 90.0% | 60.0% |
| `public_esp_fi_01` | **PUBLIC_DATASET** | 9.95s | 20 | 144.0 | 95.0% | 55.0% |
| `synthetic_session_01` | **SYNTHETIC_AUGMENTED** | 19.95s | 40 | 154.0 | 90.0% | 60.0% |
| `demo_session` | **SCRIPTED_PRESENTATION** | 95.0s | 191 | 119.0 | 100.0% | 47.12% |

## 3. Findings & Limitations

1. **Replay Integrity**: Replay loader executes actual CSV files directly; telemetry is derived from true packet timestamps with zero fake interpolation.
2. **Single-Link vs. Multi-Link Distinction**: The original 217-feature model operates per link stream. Zone localization is derived from multi-link spatial sector geometry (Wi-CaL), not from single-link binary classification alone.
3. **Public Dataset Transfer**: ESP-Fi HAR records map cleanly to 64-carrier subcarrier format; cross-environment variance shifts require link-level calibration.
4. **Synthetic Augmentation**: Synthetic sessions are strictly tagged as `synthetic_augmented` with parent tracking (`benchmark_session_01`); they are never counted towards genuine hardware verification metrics.
5. **Presentation Scenario**: The 95-second dual-person scenario (`demo_session`) is explicitly tagged as `scripted_presentation` for synchronized video demonstration.