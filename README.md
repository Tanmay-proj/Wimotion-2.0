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
                         │  (COM8)    (COM9)  │
               ┌─────────► (Laptop at Center) ◄─────────┐
               │         └────────────────────┘         │
               │                                        │
        [TX3: SW Corner] ─────────────────────── [TX4: SE Corner]
        (1C:69:20:31:4B:40)                      (CC:7B:5C:28:84:70)
```

- **Hardware Deployment Reality:**
  - **Physical Deployment (Oct 20, 2026):** **6 physical COTS ESP32-WROOM-32 microcontrollers** active simultaneously: 2 Receivers (RX1 on COM8, RX2 on COM9) + 4 Transmitters (TX1 in Z1 `BC:DD:C2:CC:49:F4`, TX2 in Z2 `1C:69:20:31:38:08`, TX3 in Z3 `1C:69:20:31:4B:40`, TX4 in Z4 `CC:7B:5C:28:84:70`). Uncoordinated ambient beacon frames (`4C:11:AE:64:9A:05`) are strictly demultiplexed as `UNKNOWN` and never assigned to TX3.
  - **Full 8-Link Physical Mesh:** Capturing concurrent multi-link CSI across dual USB-UART host receivers (116,588 frames across initial exploratory trials, plus 56,386 frames across 10 controlled Phase B sessions totaling over 172,000 physical frames; see [Live Hardware Report](docs/LIVE_HARDWARE_MULTI_LINK_REPORT.md) and [Phase B Honest Scorecard](docs/PHASE_B_HONEST_SCORECARD.md)).
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
| **Automated Unit Tests** | ✅ **Passing (56/56 in CI)** | Mode isolation, transactional rollback, single-RX coverage, variance-rate independence, rate aggregation, bisect equivalence, server readiness gate, provenance tracking, v1 model adapter contracts, benchmark generator metadata contract, zero-denominator metric safety, per-link FPR evaluation, spatial model zero-leakage session split, recorder zones schema, rogue TX suppression resilience, physical log validation, strict count match, orphan isolation, train-serving feature parity, missing link masking, short window gating, non-finite amplitude resilience, canonical schema contract, sibling path containment security, CORS origin restriction, replay cache schema version rejection, and live engine dual-output telemetry (`tests/test_spatial.py`) |
| **Colleague Audit Suite** | ✅ **Passing (6/6)** | Hardware coverage integrity, rate conservation, zero-sample link gating (`scripts/verify_six_checks.py`) |
| **Dataset Provenance Audit** | ✅ **Complete (593 Sessions)** | Comprehensive audit distinguishing physical sessions from benchmarks (`docs/DATASET_AUDIT_REPORT.md`) |
| **V1 Model Adapter** | ✅ **Actively Integrated** | Real 217-feature extraction pipeline & HistGradientBoosting classifier (`presence_model.pkl`) called in Live and Replay (`spatial/v1_adapter.py`) |
| **Per-Link Evaluation (Phase 5)** | ✅ **Verified Breakdown** | Evaluates V1 presence model independently per physical link, reporting accuracy, coverage, recall, specificity, and false-positive rate (`scripts/evaluate_models.py`) |
| **Supervised Spatial Model (Phase 6)** | ✅ **Implemented & Benchmarked** | 56-dim multi-link feature space with session-wise splits (GroupShuffleSplit) preventing overlapping-window leakage, benchmarked alongside SpatialBaseline, RandomForest, and LogisticRegression (`scripts/train_spatial_model.py`) |
| **Public Dataset Adapters** | ✅ **Implemented** | ESP-Fi HAR, RF_ESP32, and WiCAL dataset adapters (`spatial/dataset_adapters/`) |
| **Controlled Synthetic Augmentation** | ✅ **Implemented** | Physics-informed RF gain & Gaussian multipath perturbation with parent tracking (`spatial/augmentation.py`) |
| **Hardware Inventory & Standby** | ✅ **6 Physical Nodes Active** | 6 physical ESP32 boards deployed in room mesh (2 RX + 4 TX). Host USB-UART defaults to Safe Standby when server not in LIVE mode. |
| **Data Sessions & Provenance** | ✅ **Honest Classification** | Physical hardware captures (`session_real_001` through `007`), software benchmark (`benchmark_session_01`), unverified import (`public_esp_fi_01`), synthetic augmented (`synthetic_session_01`), scripted demo (`session_431`). |

---

## 3. Quickstart & Verification

### 1. Master One-Click Reproducibility Runner
Run the entire end-to-end verification, test, and evaluation suite:
```bash
py -3.10 scripts/run_master_evaluation.py
```
This executes:
1. Automated unit test suite (56 tests, 100% pass)
2. Colleague 6-point verification suite (6 checks, 100% pass)
3. Read-only hardware session & label provenance audit
4. Multi-model benchmark training & evaluation with calibrated CLEAR energy gate ($\theta = 1.80$)
5. Exact model artifact hash & git commit verification

### 2. Run Automated Unit Tests (56 Tests) & 6-Point Audit Suite Individually
```bash
py -3.10 -m unittest discover -s tests -v
py -3.10 scripts/verify_six_checks.py
```

### 3. Multi-Model Evaluation & Scientific Evidence
```bash
py -3.10 scripts/evaluate_models.py
```
Regenerates `docs/EVALUATION_REPORT.md` across 5 distinct evaluation tracks and includes the Phase 5 Per-Link evaluation table:
- **Track A:** Genuine Held-Out Single-Link Hardware Evaluation (`hardware_recorded_single_link`)
- **Track B:** Generated Benchmark Regression Experiment (`synthetic_generated_benchmark`)
- **Track C:** Unverified Public Benchmark Import Experiment (`unverified_import`)
- **Track D:** Synthetic Augmentation Experiment (`synthetic_augmented`)
- **Track E:** Scripted Presentation Scenario (`scripted_presentation`)

### 4. Supervised Spatial Model Training (Zero-Leakage Session Splits)
```bash
py -3.10 scripts/train_spatial_model.py --dataset phase_b --classifier random_forest
```
Trains the supervised classifier on the 56-dimensional multi-link feature space using session-wise splits, reporting both learned accuracy, calibrated energy-gated metrics, and baseline comparison.

### 5. Launch Tactical Console & Observatory Dashboard
Double-click `run_wimotion_2.0.bat` and select **Option [4]**, or run directly:
```bash
py -3.10 -m uvicorn spatial.server:app --host 127.0.0.1 --port 8000
```

The browser will automatically open to [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## 4. Final Submission Documentation Pack

Detailed guides and scientific deliverables are located in the `docs/` directory:
- 📑 [System Architecture & Geometry Specification](docs/ARCHITECTURE.md)
- 📋 [Dataset Audit & Provenance Verification Report](docs/DATASET_AUDIT_REPORT.md)
- 🎯 [Presentation Day Demo Runbook](docs/DEMO_RUNBOOK.md)
- 📊 [Scientific Evaluation & Evidence Report](docs/EVALUATION_REPORT.md)
- 🎓 [Examiner Viva Q&A Guide](docs/VIVA_QNA.md)
- 📈 [Phase B Controlled Scorecard](docs/PHASE_B_HONEST_SCORECARD.md)


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
  Physical hardware deployment consists of **6 physical ESP32 microcontrollers** (2 Receivers + 4 Transmitters) forming a genuine 8-link distributed mesh, capturing over 172,000 frames across empirical testing campaigns (116,588 exploratory frames + 56,386 controlled Phase B frames; see `docs/LIVE_HARDWARE_MULTI_LINK_REPORT.md`, `docs/PHASE_B_HONEST_SCORECARD.md`, and `HARDWARE_SESSION_LOG.txt`).
- **Safety Guarantee:**
  Project WiMotion v1.0 (`wimotion/`) remains 100% frozen, intact, and fully operational as an independent baseline.
