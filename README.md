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
| **Synthetic Replay Suite** | ✅ **Implemented** | 600-frame 3-stage validation (`spatial/replay.py`) |
| **Person Tracker Engine** | ✅ **Implemented** | Persistent ID assignment (`P1`, `P2`, `P3`) |
| **FastAPI Backend & API** | ✅ **Implemented** | Non-blocking HTTP endpoints (`GET /api/spatial`, `GET /health`) |
| **Tactical Multi-Person HUD** | ✅ **Implemented** | 4-sector glassmorphism HUD with dynamic avatars (`dashboard/`) |
| **Automated Unit Tests** | ✅ **Passing (6/6)** | Verified tensor shapes, gates, raw CSI parsing, and tracking (`tests/test_spatial.py`) |
| **Dual-RX Flashed & Listening** | ✅ **Verified** | Master AP (`COM3`) & Passive Sniffer (`COM8`) active @ 921,600 baud |
| **Labelled Multi-Person Dataset** | ⏳ **Pending Collection** | Capture script ready (`scripts/record_multilink_dataset.py`) |
| **Trained Multi-Class ML Model** | ⏳ **Pending Dataset** | Scaffold baseline active; real ML model trained after data collection |

---

## 3. Quickstart & Verification

### 1. Run Automated Unit Tests
```bash
py -3.10 -m unittest discover -s tests -v
```

### 2. Run Synthetic 3-Stage Replay
```bash
py -3.10 -m spatial.replay
```

### 3. Launch Tactical HUD Server
```bash
py -3.10 -m uvicorn spatial.server:app --host 127.0.0.1 --port 8000
```
Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

### 4. Interactive Hardware Diagnostic (When Boards Plugged In)
```bash
py -3.10 scripts/0_check_multilink_hardware.py --interactive
```

---

## 4. Engineering Principles & Scientific Integrity
- **Scaffold vs. Learned ML:** The current `SpatialBaseline` model serves as a deterministic functional scaffold to verify data pipelines and visualization. Final crowd counting and localization require empirical cross-validation on real labelled session data.
- **Safety Guarantee:** Project WiMotion v1.0 (`wimotion/`) remains 100% frozen, intact, and fully operational as an independent baseline.
