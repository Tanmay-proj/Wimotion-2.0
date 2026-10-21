# WiMotion 2.0 — System Architecture & Scientific Design

## 1. System Overview
WiMotion 2.0 is an advanced Commodity WiFi Channel State Information (CSI) Spatial Sensing and Multi-Person Occupancy Engine.
The system transforms raw 802.11n OFDM subcarrier amplitude and phase perturbations captured across distributed transceivers into real-time presence detection, sector tracking, and multi-link telemetry.

```
+-------------------------------------------------------------------------------+
|                             DATA ACQUISITION LAYER                            |
|                                                                               |
|  [Hardware Nodes]          [Public CSI Datasets]       [Synthetic Augmentor]  |
|   RX1 / RX2 ESP32           ESP-Fi HAR / WiCAL          Physics-Informed Gain |
|   TX1..TX4 Beacons          RF_ESP32 Indoor             & Gaussian Noise      |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                          SOURCE & PROVENANCE GATEWAY                          |
|                                                                               |
|   Strict Provenance Tracking:                                                 |
|   - hardware_recorded     - public_dataset                                    |
|   - scripted_presentation - synthetic_augmented                              |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                       SIGNAL QUALITY & FEATURE PIPELINE                       |
|                                                                               |
|   1. Temporal Windowing (O(log N) Bisect Slicing, dt in [0.5s, 2.0s])         |
|   2. Physical Quality Gate: >= 8 packets, rate >= 4.0 Hz                      |
|   3. Feature Pipelines:                                                       |
|      - WiMotion 2.0 Spatial: Per-link CSI variance across 8 links             |
|      - WiMotion v1 Adapter: 217 temporal-spectral statistical features         |
|        (SVD Coherence, Doppler Spectrum, Subcarrier Variance)                 |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                             INFERENCE SUBSYSTEM                               |
|                                                                               |
|   [Stage-1 Link Presence Gate]             [Spatial Multi-Link Sector Map]    |
|   HistGradientBoosting / ExtraTrees        Wi-CaL Sector Energy Comparison    |
|   Input: 217 features                      Input: 8-link distributed variance  |
|   Output: Presence Probability [0..1]      Output: Z1 (NE), Z2 (NW),          |
|                                                    Z3 (SW), Z4 (SE)           |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                    OBSERVATORY HUD & DASHBOARD SUBSYSTEM                      |
|                                                                               |
|   - Real-Time Tactical Radar (Four-Quadrant Snapping, Enlarged Discs P1/P2)   |
|   - Session Library with Natural Naming and Honest Provenance Metadata        |
|   - 8-Link Health Matrix (Variance, RSSI, Rate Hz, Per-Link Health)           |
|   - Deterministic Playback Scrubber, Speed Controls, and Step Buttons         |
+-------------------------------------------------------------------------------+
```

---

## 2. Hardware Topology & Geometry
The multi-link sensing grid operates in a 4-quadrant spatial configuration:

- **Receivers (RX1, RX2)**: Located along the room baseline, collecting interleaved CSI packets from all transmitters.
- **Transmitter Beacons (TX1 to TX4)**:
  - **TX1**: North-East Quadrant (**Zone 1 / Z1**)
  - **TX2**: North-West Quadrant (**Zone 2 / Z2**)
  - **TX3**: South-West Quadrant (**Zone 3 / Z3**)
  - **TX4**: South-East Quadrant (**Zone 4 / Z4**)
- **Unknown Transmitter Policy**: Unmapped or rogue transmitter IDs are ranked separately and isolated to `UNKNOWN`. A rogue transmitter cannot suppress a valid mapped transmitter exceeding the noise threshold, and is **never** assigned to Z1, Z2, Z3, or Z4.

---

## 3. Data Integrity & Provenance Contract
Every session is uniquely identified with honest backend metadata:
- `hardware_recorded_single_link`: Physical room capture from WiMotion v1 physical trials (RX1-TX1) without fake interpolation.
- `synthetic_generated_benchmark`: Multi-link CSI-like signal generated by mathematical script (`create_benchmark_session.py`) for deterministic multi-link pipeline regression.
- `unverified_import`: Public schema sample (`public_esp_fi_01`) pending independent upstream verification.
- `synthetic_augmented`: Controlled offline transformations tracking parent session ID, noise standard deviation, and random seed.
- `scripted_presentation`: Deterministic 95-second dual-person scenario for viva/presentation video synchronization.
- `unknown_unverified`: Assigned automatically to any session missing provenance metadata; never silently admitted as genuine hardware.

---

## 4. Dual-Engine Call Paths & Inference Consistency

To ensure scientific honesty and complete architectural transparency, WiMotion 2.0 strictly decouples **Learned ML Binary Presence Detection** from **Heuristic Multi-Link Sector Localization**:

```
[Raw CSI Packet Stream]
         │
         ▼
[Sliding Window Slicing] (Δt = 2.0s, step = 0.5s, rate quality gate >= 4.0 Hz)
         │
         ├───► [Stage 1: ML Binary Presence Gating]
         │     ├── Caller: LiveSpatialEngine._process_window() OR load_recording_frames()
         │     ├── Engine: spatial.v1_adapter.V1PresenceModelAdapter
         │     ├── Classifier: HistGradientBoostingClassifier (Original wimotion model)
         │     ├── Pipeline: 217 temporal-spectral statistical features per link stream
         │     └── Output: {"global_presence": "human_present" | "empty_room", "confidence": float}
         │
         └───► [Stage 2: Spatial Sector Localization]
               ├── Caller: LiveSpatialEngine._process_window() OR load_recording_frames()
               ├── Engine: spatial.baseline.SpatialBaseline (Wi-CaL Energy Comparison)
               ├── Metric: Multi-link CSI temporal variance ratio (argmax across Z1..Z4)
               └── Output: {"model_zone": "Z1" | "Z2" | "Z3" | "Z4" | "CLEAR" | "UNKNOWN"}
```

### Call Trace by Operational Mode:
1. **LIVE HARDWARE Mode (`spatial/live.py` -> `spatial/server.py`)**:
   - `LiveSpatialEngine.run()` ingests asynchronous packets from `SerialCaptureManager`.
   - `_process_window()` calls `self.v1_adapter.evaluate_multilink_window(records)` for ML presence and `self.baseline.evaluate(window_df, records)` for sector mapping.
   - Result is exposed through `GET /api/spatial` when authoritative mode is `LIVE`.
2. **RECORDED REPLAY Mode (`spatial/replay_loader.py` -> `spatial/server.py`)**:
   - `load_recording_frames(session_id)` loads session CSV records and uses binary search (`bisect`) for sliding window slicing.
   - For every window, invokes `v1_adapter.evaluate_multilink_window(window_records)` and `spatial_baseline.evaluate(window_df, window_records)`.
   - Cached frames with real ML + heuristic outputs are returned via `GET /api/recordings/{session_id}/data`.
3. **SIMULATION / SCRIPTED Mode (`spatial/server.py` & `demo_session`)**:
   - Deterministic 95-second timeline built for viva video synchronization.
   - Explicitly tagged with `source_type: "scripted_presentation"`; ML model evaluations on this synthetic signal reflect lack of physical Doppler dynamics (evaluated truthfully as ~37.17% accuracy).

---

## 5. Physical Hardware Deployment Evolution

| Specification | Phase A Lab Demonstrations | Phase B Controlled Benchmark Deployment (Oct 20, 2026) | Full Theoretical Spec |
| :--- | :--- | :--- | :--- |
| **Total ESP32 Boards** | **4 COTS Microcontrollers** | **6 COTS Microcontrollers** | **6 Microcontrollers** |
| **Receiver (RX) Nodes** | 1-2 RX (`COM8` / legacy `COM3`) | 2 RX Nodes (`COM8`, `COM9`) | 2 RX Nodes (RX1, RX2) |
| **Transmitter (TX) Nodes** | 2-3 Beacons (TX1-TX3) | 4 Beacons (TX1: Z1, TX2: Z2, TX3: Z3, TX4: Z4) | 4 Beacons (TX1 to TX4) |
| **Active Spatial Links** | 3 to 4 Links (Degraded mesh) | 8 Concurrent Physical Mesh Links | 8 Links ($2 \text{ RX} \times 4 \text{ TX}$) |
| **Baud Rate & Mode** | 921,600 baud, 802.11n HT20 promiscuous | 921,600 baud, 802.11n HT20 promiscuous | 921,600 baud |
| **Datasets Captured** | `session_real_001` to `007` | `session_pB_clear_01..02`, `session_pB_z1..z4_walk_01..02` (10 takes) | Continuous streaming |
| **Safe Standby Policy** | Active on host (prevents USB-UART watchdog timeout BSODs) | Active on host | RTOS / Linux daemon |

> [!NOTE]
> WiMotion 2.0 software gracefully adapts between a full 6-node 8-link mesh and degraded single-RX or 4-link setups without synthesizing fake link data or crashing.

---

## 6. External Dataset Attributions & Academic Licences

All external benchmark datasets integrated into WiMotion 2.0 are attributed to their upstream academic research sources:

| Dataset Identifier | Upstream Source & Authors | Upstream Repository / Publication | Upstream Licence | Data Format & Subcarriers |
| :--- | :--- | :--- | :--- | :--- |
| **`ESP_FI_HAR`** | AutoSmartGroup (IEEE IoT Journal 2023) | [GitHub: AutoSmartGroup/ESP-Fi-HAR](https://github.com/AutoSmartGroup/ESP-Fi-HAR) | Open Academic / MIT | 52 subcarriers @ 100 Hz, 3-antenna ESP32 CSV/MAT |
| **`RF_ESP32`** | Mohammed-Baqir | [GitHub: Mohammed-Baqir/RF_ESP32_Dataset](https://github.com/Mohammed-Baqir/RF_ESP32_Dataset) | Open Academic Research | 64 subcarriers @ 50 Hz, single-link indoor CSV |
| **`WICAL`** | Fuhai Wang et al. (IEEE Access 2022) | [GitHub: fuhaiwang/WiCAL](https://github.com/fuhaiwang/WiCAL) | Open Academic Research | Multi-AP CSI coordinates & subcarrier amplitudes |

