# WiMotion 2.0 (Wi-CaL Multi-Link Sensing Edition)

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

- **4 Transmitters (TX1–TX4):** Standalone ESP32 nodes placed in 4 quadrants (TX1=NE, TX2=NW, TX3=SW, TX4=SE) powered by 5V USB chargers.
- **2 Receivers (RX1, RX2):** ESP32 nodes connected directly to host PC via USB (`COM3` Master AP, `COM8` Passive Sniffer @ 921,600 baud).
- **8 Candidate Links:** $4 \times 2 = 8$ spatial CSI channels ($RX_1 \to TX_k$ and $RX_2 \to TX_k$ for $k \in \{1,2,3,4\}$).
- **Inference Mode:** Sector perturbation based on 64-subcarrier temporal variance ranking ($argmax$ strongest active zone). Heuristic spatial zoning, uncalibrated for absolute human count.

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
| **Automated Unit Tests** | ✅ **Passing (19/19)** | Mode isolation, transactional rollback, single-RX coverage, variance-rate independence, rate aggregation, bisect equivalence (`tests/test_spatial.py`) |
| **Dual-RX Flashed & Listening** | ✅ **Verified** | Master AP (`COM3`) & Passive Sniffer (`COM8`) active @ 921,600 baud |
| **Labelled Multi-Person Dataset** | ⏳ **Pending Collection** | Capture script ready (`scripts/record_multilink_dataset.py`) |
| **Trained Multi-Class ML Model** | ⏳ **Pending Dataset** | Scaffold baseline active; real ML model trained after data collection |

---

## 3. Quickstart & Verification

### 1. Run Automated Unit Tests
```bash
py -3.10 -m unittest discover -s tests -v
```

### 2. Launch Tactical Console & Web Server
```bash
py -3.10 -m uvicorn spatial.server:app --host 127.0.0.1 --port 8000
```
Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

### 3. Interactive Hardware Diagnostic (When ESP32 Boards Plugged In)
```bash
py -3.10 scripts/0_check_multilink_hardware.py --interactive
```

---

## 4. Engineering Principles & Scientific Integrity

- **Aggregate CSI Rate Metric Definition & Units:**
  The displayed CSI rate represents **valid CSI packets received per second** across all active links within the configured sliding window ($\Delta t = 2.0\text{ s}$ by default):
  $$\text{Aggregate Rate (Hz)} = \frac{N_{\text{records}}}{\Delta t_{\text{window}}} = \sum_{k=1}^8 \text{Link Rate}_k$$
  A link is defined as `ACTIVE` only when genuine recorded samples ($N_k > 0$) exist in that window. CSI variance is a physical perturbation measurement, never a substitute for packet presence.
- **Derived Hardware Availability in Replay:**
  In Replay Lab, receiver and link statuses are derived directly from empirical recorded coverage. If a session contains only RX1 data, RX2 is truthfully reported as `NO DATA` / `OFFLINE` (yielding `1 / 2 RECORDED`), preventing misleading assumptions of dual-receiver operation.
- **Transactional Mode Switching:**
  Operating mode changes (`LIVE`, `REPLAY`, `SIMULATION`) are committed by the UI only after backend confirmation (`POST /api/mode`), rolling back on communication error to prevent desynchronization between user controls and ingested telemetry.
- **Heuristic Zone Perturbation vs. Validated Human Counting:**
  The current spatial baseline tracks **perturbed RF sectors**, based on temporal CSI variance thresholds (threshold = 8.0). Active zone count reflects perturbed links, NOT an independently verified count of physical humans. A single individual walking across the room can perturb multiple links simultaneously, while two stationary individuals in one sector activate a single quadrant.
- **Truthful Telemetry Semantics:**
  When physical hardware is unplugged or CSI packets are interrupted (> 3.0s timeout), the system authoritatively reports `zone: UNKNOWN` and `inference_status: UNAVAILABLE`. Disconnected hardware is never falsely reported as an empty room (`CLEAR`).
- **Complete Mode Isolation:**
  Synthetic simulation data cannot leak into or override live hardware data. The backend explicitly manages operating modes (`LIVE`, `REPLAY`, `SIMULATION`), isolates memory stores, and clears stale values on mode switches.
- **Scaffold vs. Learned ML:**
  The current `SpatialBaseline` model serves as a deterministic functional scaffold to verify data pipelines, quality gates, and spatial visualization. Final crowd counting and localization require empirical cross-validation on real labelled session data.
- **Safety Guarantee:**
  Project WiMotion v1.0 (`wimotion/`) remains 100% frozen, intact, and fully operational as an independent baseline.
