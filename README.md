# WiMotion 2.0 (Wi-CaL Multi-Link Sensing Edition)

[![WiMotion 2.0 CI](https://github.com/Tanmay-proj/Wimotion-2.0/actions/workflows/ci.yml/badge.svg)](https://github.com/Tanmay-proj/Wimotion-2.0/actions/workflows/ci.yml)

**Project:** WiMotion 2.0 — Multi-Link RF Spatial Sensing, Occupancy Estimation & Sector Mapping  
**Evolution of:** Project WiMotion v1.0 (`wimotion/`)  
**Scientific Foundation:** Inspired by Wi-CaL (IEEE Access, Vol. 10, 2022) Multi-Link CSI Sensing Framework  

---

## 1. System Architecture (4 TX × 2 RX Topology)

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
  - **Lab Inventory:** **4 physical COTS ESP32 microcontrollers** (typically deployed as 1 Master RX on `COM3` + 3 TX Beacons in Z1, Z2, Z3, or 2 RX + 2 TX).
  - **Theoretical Grid:** 2 Receivers (`COM3`, `COM8`) $\times$ 4 Transmitters (TX1..TX4) forming an 8-link distributed mesh. Fully supported in firmware and software architecture.
- **Dual-Engine Inference Mode:**
  - **Presence Gating:** Original WiMotion ML Model (`HistGradientBoostingClassifier`, 217 temporal-spectral features) via `spatial/v1_adapter.py`. Achieves **77.98% accuracy (83.1% F1)** on untouched held-out hardware sessions.
  - **Sector Localization:** Spatial perturbation based on multi-link CSI variance ratio ranking ($argmax$). Heuristic spatial zoning, uncalibrated for absolute human count.

---

## 2. Research & Implementation Status Table

| Component | Status | Details |
| :--- | :---: | :--- |
| **Dual-RX Serial Ingestion** | ✅ **Implemented** | Asynchronous multi-threaded worker (`spatial/serial_manager.py`) |
| **Source-MAC Identification** | ✅ **Implemented** | Packet-level transmitter MAC demultiplexing (`spatial/parser.py`) |
| **8-Link Schema & Fusion** | ✅ **Implemented** | 56-dim feature vector (48 stats + 8-bit link validity mask) |
| **Signal Quality Gate** | ✅ **Implemented** | Blocks inference if receiver rate falls below 4.0 Hz |
| **Sliding Window Buffer** | ✅ **Implemented** | 2.0s sliding window with 0.5s step (`spatial/window.py`) |
| **Strict Mode Isolation** | ✅ **Implemented** | Authoritative separation between LIVE hardware, REPLAY lab, and SIMULATION (`spatial/server.py`) |
| **Unified State Renderer** | ✅ **Implemented** | Consistent single-renderer driving metrics, 8-link mesh, timeline, and radar (`dashboard/observatory_multi.html`) |
| **Safe Replay Lab Engine** | ✅ **Implemented** | Timestamp-based playback with scrub, rate quality gate, and XSS-safe DOM nodes (`spatial/replay_loader.py`) |
| **Automated Unit Tests** | ✅ **Passing (33/33)** | Mode isolation, transactional rollback, single-RX coverage, variance-rate independence, rate aggregation, bisect equivalence, server readiness gate, provenance tracking, v1 model adapter contracts (missing model, insufficient frames, empty multi-link), zero-denominator metric safety, held-out session integrity, and rogue TX rejection (`tests/test_spatial.py`) |
| **Colleague Audit Suite** | ✅ **Passing (6/6)** | Hardware coverage integrity, rate conservation, zero-sample link gating (`scripts/verify_six_checks.py`) |
| **V1 Model Adapter** | ✅ **Actively Integrated** | Real 217-feature extraction pipeline & HistGradientBoosting classifier called in Live and Replay (`spatial/v1_adapter.py`) |
| **Session-Level Evaluation** | ✅ **Verified (81.25% Valid Acc)** | Untouched held-out hardware validation with zero silent fallback, undefined metric safety (N/A for empty-room recall), and separate invalid window tracking (`scripts/evaluate_models.py`) |
| **Public Dataset Adapters** | ✅ **Implemented** | ESP-Fi HAR, RF_ESP32, and WiCAL dataset adapters with upstream academic citations (`spatial/dataset_adapters/`) |
| **Controlled Synthetic Augmentation** | ✅ **Implemented** | Physics-informed RF gain & Gaussian multipath perturbation with parent tracking (`spatial/augmentation.py`) |
| **Hardware Inventory & Standby** | ⚠️ **4 Boards / Safe Standby** | 4 physical ESP32 boards in kit. Host USB-UART defaults to Safe Standby (Disconnected) to prevent Windows DPC Watchdog BSODs until dedicated demo capture. |
| **Labelled Benchmark Datasets** | ✅ **Standard Benchmarks Captured** | `benchmark_session_01` (1.49 MB), `held_out_empty_01`, `held_out_walking_01`, `public_esp_fi_01` |

---

## 3. Quickstart & Verification

### 1. Run Automated Unit Tests (33/33) & 6-Point Audit Suite
```bash
py -3.10 -m unittest discover -s tests -v
py -3.10 scripts/verify_six_checks.py
```
Both test suites verify all core engineering constraints: single-RX isolation, variance-rate independence, transactional mode rollback, zero telemetry leakage, rate formula equivalence, quality gating, v1 model 217-feature contract, and provenance integrity.

### 2. Multi-Model Evaluation & Scientific Evidence
```bash
py -3.10 scripts/evaluate_models.py
```
Generates `docs/EVALUATION_REPORT.md` comparing baseline spatial heuristics with the original WiMotion model across genuine recordings, public benchmarks, and synthetic samples.

### 3. Launch Tactical Console & Observatory Dashboard
Double-click `run_wimotion_2.0.bat` and select **Option [4]**, or run directly:
```bash
py -3.10 -m uvicorn spatial.server:app --host 127.0.0.1 --port 8000
```
The browser will automatically open to [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## 4. Final Submission Documentation Pack

Detailed guides and scientific deliverables are located in the `docs/` directory:
- 📑 [System Architecture & Geometry Specification](file:///E:/WIFI_INTERFEROMETRIC_NEURAL_SENSING/wimotion_2.0/docs/ARCHITECTURE.md)
- 🎯 [Presentation Day Demo Runbook](file:///E:/WIFI_INTERFEROMETRIC_NEURAL_SENSING/wimotion_2.0/docs/DEMO_RUNBOOK.md)
- 📊 [Scientific Evaluation & Evidence Report](file:///E:/WIFI_INTERFEROMETRIC_NEURAL_SENSING/wimotion_2.0/docs/EVALUATION_REPORT.md)
- 🎓 [Examiner Viva Q&A Guide](file:///E:/WIFI_INTERFEROMETRIC_NEURAL_SENSING/wimotion_2.0/docs/VIVA_QNA.md)

---

## 5. Engineering Principles & Scientific Integrity

- **Strict Data Provenance Contract:**
  Every session carries immutable metadata distinguishing true origin:
  - `hardware_recorded`: Physical capture from ESP32 hardware without fake interpolation.
  - `scripted_presentation`: Deterministic 95-second dual-person scenario for viva/presentation video synchronization.
  - `public_dataset`: External benchmark data (ESP-Fi HAR) with attributed paper and license.
  - `synthetic_augmented`: Controlled offline transformations tracking parent session ID, noise standard deviation, and random seed.
- **Aggregate CSI Rate Metric Definition & Units:**
  The displayed CSI rate represents **valid CSI packets received per second** across all active links within the sliding window ($\Delta t = 2.0\text{ s}$):
  $$\text{Aggregate Rate (Hz)} = \frac{N_{\text{records}}}{\Delta t_{\text{window}}} = \sum_{k=1}^8 \text{Link Rate}_k$$
- **Original Model Preservation:**
  The original WiMotion model (`presence_model.pkl`, 217 features, 94.74% CV) is never retrained or modified. In WiMotion 2.0, it is executed via a link-level adapter (`V1PresenceModelAdapter`) grouping packets per link before computing presence.
- **Rogue / Unknown Node Protection:**
  Unmapped transmitter IDs are strictly isolated to `UNKNOWN` and never assigned to a default zone.
- **Safety Guarantee:**
  Project WiMotion v1.0 (`wimotion/`) remains 100% frozen, intact, and fully operational as an independent baseline.
