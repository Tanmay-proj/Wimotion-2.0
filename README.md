# WiMotion 2.0 (Wi-CaL Multi-Link Sensing Edition)

[![WiMotion 2.0 CI](https://github.com/Tanmay-proj/Wimotion-2.0/actions/workflows/ci.yml/badge.svg)](https://github.com/Tanmay-proj/Wimotion-2.0/actions/workflows/ci.yml)

**Project:** WiMotion 2.0 — Multi-Link RF Spatial Sensing, Occupancy Estimation & Sector Mapping  
**Evolution of:** Project WiMotion v1.0 (`wimotion/`)  
**Scientific Foundation:** Inspired by Wi-CaL (IEEE Access, Vol. 10, 2022) Multi-Link CSI Sensing Framework  

---

## 1. System Architecture & Hardware Deployment Reality

WiMotion 2.0 extends single-link WiFi sensing to a distributed spatial array using standard COTS ESP32 microcontrollers:

```
        [TX2: NW Corner] ─────────────────────── [TX1: NE Corner]
        (1C:69:20:31:38:08)                      (BC:DD:C2:CC:49:F4)
               │                                        │
               │         ┌────────────────────┐         │
               │         │  ROOM SENSING GRID │         │
               └─────────►  (8 MESH LINKS)    ◄─────────┘
                         │                    │
                         │   [RX1]    [RX2]   │
                         │  (COM3)    (COM8)  │
               ┌─────────► (Laptop at Center) ◄─────────┐
               │         └────────────────────┘         │
               │                                        │
        [TX3: SW Corner] ─────────────────────── [TX4: SE Corner]
        (CC:7B:5C:28:84:70)                      (1C:69:20:31:4B:40)
```

- **Hardware Deployment Reality:**
  - **Lab Inventory:** **4 physical COTS ESP32-WROOM-32 microcontrollers** (typically deployed as 1 Master RX on `COM3` + 3 TX Beacons in Z1, Z2, Z3, or 2 RX + 2 TX).
  - **Theoretical Grid:** 2 Receivers (`COM3`, `COM8`) $\times$ 4 Transmitters (TX1..TX4) forming an 8-link distributed mesh. Supported in firmware and software architecture, but theoretical.
- **Dual-Engine Inference Mode:**
  - **Presence Gating:** Original WiMotion ML Model (`HistGradientBoostingClassifier`, 217 temporal-spectral features, `presence_model.pkl`) via `spatial/v1_adapter.py`. Evaluated on untouched held-out single-link physical captures (`held_out_empty_01` + `held_out_walking_01`, 109 windows: **81.25% Valid Accuracy**, 88.07% Coverage, 71.56% Conservative All-Window Score).
  - **Sector Localization:** Spatial perturbation based on multi-link CSI variance ratio ranking ($argmax$). Heuristic spatial zoning, uncalibrated for absolute human count.

---

## 2. Research & Implementation Status Table

| Component | Status | Details |
| :--- | :---: | :--- |
| **Dual-RX Serial Ingestion** | ✅ **Implemented** | Asynchronous multi-threaded worker (`spatial/serial_manager.py`) |
| **Source-MAC Identification** | ✅ **Implemented** | Packet-level transmitter MAC demultiplexing (`spatial/parser.py`) |
| **8-Link Schema & Fusion** | ✅ **Implemented** | 56-dim feature vector (48 stats + 8-bit link validity mask) |
| **Signal Quality Gate** | ✅ **Implemented** | Blocks inference if receiver rate falls below 4.0 Hz or < 8 packets |
| **Sliding Window Buffer** | ✅ **Implemented** | 2.0s sliding window with 0.5s step (`spatial/window.py`) |
| **Strict Mode Isolation** | ✅ **Implemented** | Authoritative separation between LIVE hardware, REPLAY lab, and SIMULATION (`spatial/server.py`) |
| **Unified State Renderer** | ✅ **Implemented** | Consistent single-renderer driving metrics, 8-link mesh, timeline, and radar (`dashboard/observatory_multi.html`) |
| **Automated Unit Tests** | ✅ **Passing (39/39 in CI)** | Mode isolation, transactional rollback, single-RX coverage, variance-rate independence, rate aggregation, bisect equivalence, server readiness gate, provenance tracking, v1 model adapter contracts (missing model, cross-NumPy unpickling), benchmark generator metadata contract, zero-denominator metric safety, per-link FPR evaluation, spatial model zero-leakage session split, recorder zones schema, and rogue TX suppression resilience (`tests/test_spatial.py`) |
| **Colleague Audit Suite** | ✅ **Passing (6/6)** | Hardware coverage integrity, rate conservation, zero-sample link gating (`scripts/verify_six_checks.py`) |
| **Dataset Provenance Audit** | ✅ **Complete (593 Sessions)** | Comprehensive audit distinguishing 32 genuine physical sessions from 560 activity benchmarks (`docs/DATASET_AUDIT_REPORT.md`) |
| **V1 Model Adapter** | ✅ **Actively Integrated** | Real 217-feature extraction pipeline & HistGradientBoosting classifier (`presence_model.pkl`) called in Live and Replay (`spatial/v1_adapter.py`) |
| **Per-Link Evaluation (Phase 5)** | ✅ **Verified Breakdown** | Evaluates V1 presence model independently per physical link, reporting accuracy, coverage, recall, specificity, and false-positive rate (`scripts/evaluate_models.py`) |
| **Supervised Spatial Model (Phase 6)** | ✅ **Implemented & Benchmarked** | 56-dim multi-link feature space with session-wise splits (GroupShuffleSplit) preventing overlapping-window leakage, benchmarked alongside SpatialBaseline (`scripts/train_spatial_model.py`) |
| **Public Dataset Adapters** | ✅ **Implemented** | ESP-Fi HAR, RF_ESP32, and WiCAL dataset adapters (`spatial/dataset_adapters/`) |
| **Controlled Synthetic Augmentation** | ✅ **Implemented** | Physics-informed RF gain & Gaussian multipath perturbation with parent tracking (`spatial/augmentation.py`) |
| **Hardware Inventory & Standby** | ⚠️ **4 Boards / Safe Standby** | 4 physical ESP32 boards in kit. Host USB-UART defaults to Safe Standby (Disconnected) to prevent Windows DPC Watchdog BSODs until live demo capture. |
| **Data Sessions & Provenance** | ✅ **Honest Classification** | Single-link physical hardware (`held_out_empty_01`, `held_out_walking_01`), software benchmark (`benchmark_session_01`), unverified import (`public_esp_fi_01`), synthetic augmented (`synthetic_session_01`), scripted demo (`demo_session`). |

---

## 3. Quickstart & Verification

### 1. Run Automated Unit Tests (39 Tests) & 6-Point Audit Suite
```bash
py -3.10 -m unittest discover -s tests -v
py -3.10 scripts/verify_six_checks.py
```
Both test suites verify all core engineering constraints: single-RX isolation, variance-rate independence, transactional mode rollback, zero telemetry leakage, rate formula equivalence, quality gating, v1 model 217-feature contract, rogue TX suppression resilience, per-link FPR evaluation, and spatial training session-leakage prevention.

### 2. Multi-Model Evaluation & Scientific Evidence
```bash
py -3.10 scripts/evaluate_models.py
```
Regenerates `docs/EVALUATION_REPORT.md` across 5 distinct evaluation tracks and includes the Phase 5 Per-Link evaluation table:
- **Track A:** Genuine Held-Out Single-Link Hardware Evaluation (`hardware_recorded_single_link`)
- **Track B:** Generated Benchmark Regression Experiment (`synthetic_generated_benchmark`)
- **Track C:** Unverified Public Benchmark Import Experiment (`unverified_import`)
- **Track D:** Synthetic Augmentation Experiment (`synthetic_augmented`)
- **Track E:** Scripted Presentation Scenario (`scripted_presentation`)

### 3. Supervised Spatial Model Training (Zero-Leakage Session Splits)
```bash
py -3.10 scripts/train_spatial_model.py
```
Trains a supervised classifier on the 56-dimensional multi-link feature space using session-wise splits to prevent temporal leakage, reporting both learned accuracy and baseline heuristic comparison.

### 4. Launch Tactical Console & Observatory Dashboard
Double-click `run_wimotion_2.0.bat` and select **Option [4]**, or run directly:
```bash
py -3.10 -m uvicorn spatial.server:app --host 127.0.0.1 --port 8000
```
The browser will automatically open to [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## 4. Final Submission Documentation Pack

Detailed guides and scientific deliverables are located in the `docs/` directory:
- 📑 [System Architecture & Geometry Specification](file:///E:/WIFI_INTERFEROMETRIC_NEURAL_SENSING/wimotion_2.0/docs/ARCHITECTURE.md)
- 📋 [Dataset Audit & Provenance Verification Report](file:///E:/WIFI_INTERFEROMETRIC_NEURAL_SENSING/wimotion_2.0/docs/DATASET_AUDIT_REPORT.md)
- 🎯 [Presentation Day Demo Runbook](file:///E:/WIFI_INTERFEROMETRIC_NEURAL_SENSING/wimotion_2.0/docs/DEMO_RUNBOOK.md)
- 📊 [Scientific Evaluation & Evidence Report](file:///E:/WIFI_INTERFEROMETRIC_NEURAL_SENSING/wimotion_2.0/docs/EVALUATION_REPORT.md)
- 🎓 [Examiner Viva Q&A Guide](file:///E:/WIFI_INTERFEROMETRIC_NEURAL_SENSING/wimotion_2.0/docs/VIVA_QNA.md)

---

## 5. Engineering Principles & Scientific Integrity

- **Strict Data Provenance Contract:**
  Every session carries immutable metadata distinguishing true origin:
  - `hardware_recorded_single_link`: Physical capture from WiMotion v1 room trials (RX1-TX1) without fake interpolation.
  - `synthetic_generated_benchmark`: Multi-link CSI-like signal generated by mathematical script (`create_benchmark_session.py`) for deterministic pipeline regression.
  - `unverified_import`: Public schema sample (`public_esp_fi_01`) pending independent upstream verification.
  - `synthetic_augmented`: Controlled offline transformations tracking parent session ID, noise standard deviation, and random seed.
  - `scripted_presentation`: Deterministic 95-second dual-person scenario for viva/presentation video synchronization.
  - `unknown_unverified`: Default for missing or invalid metadata; never silently treated as genuine hardware.
- **Aggregate CSI Rate Metric Definition & Units:**
  The displayed CSI rate represents **valid CSI packets received per second** across all active links within the sliding window ($\Delta t = 2.0\text{ s}$):
  $$\text{Aggregate Rate (Hz)} = \frac{N_{\text{records}}}{\Delta t_{\text{window}}} = \sum_{k=1}^8 \text{Link Rate}_k$$
- **Original Model Preservation:**
  The original WiMotion model (`presence_model.pkl`, 217 features, trained with `scikit-learn 1.7.2`) is never retrained or modified. In WiMotion 2.0, it is executed via a link-level adapter (`V1PresenceModelAdapter`) grouping packets per link before computing presence.
- **Rogue / Unknown Node Protection:**
  Unmapped transmitter IDs are ranked separately and isolated to `UNKNOWN`. They cannot suppress a valid mapped transmitter exceeding the noise threshold.
- **Hardware Truth:**
  We own **4 physical ESP32 boards**. The 6-node / 8-link mesh is our theoretical system architecture, demonstrated via software pipeline simulation. Physical trials were conducted in single-link mode.
- **Safety Guarantee:**
  Project WiMotion v1.0 (`wimotion/`) remains 100% frozen, intact, and fully operational as an independent baseline.
