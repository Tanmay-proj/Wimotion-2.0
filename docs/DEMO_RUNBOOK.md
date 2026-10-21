# WiMotion 2.0 — Presentation Day Demo Runbook

## Overview
This runbook provides the exact sequence of actions for presenting WiMotion 2.0 to examiners, project evaluators, and audience members.

---

## 1. Quick Startup (Zero-Friction Launch)
1. Double-click `run_wimotion_2.0.bat` in the project root.
2. Select **Option [4]** (`Start Live Multi-Person HUD Server`).
3. The FastAPI server starts at `http://127.0.0.1:8000` and automatically opens the **Observatory Dashboard** in your default web browser.

---

## 2. Recommended Presentation Sequence

### Step 1: Architecture & Live Standby (00:00 - 02:00)
- Show the **Overview Tab**: Explain the 4-quadrant layout (Z1 NE, Z2 NW, Z3 SW, Z4 SE) and the distributed 8-link mesh (RX1/RX2 $\times$ TX1..TX4).
- State clearly: *"Our physical lab deployment consists of 6 physical ESP32 boards: 2 Receivers (RX1 on COM8, RX2 on COM9) connected over USB UART to the laptop, and 4 Transmitters (TX1-TX4) deployed in the four room sectors (Z1 NE, Z2 NW, Z3 SW, Z4 SE) forming an 8-link distributed mesh."*
- Highlight Dual-Engine outputs: The dashboard displays both **HEURISTIC ZONE (BASELINE)** and **SUPERVISED ML ZONE** side-by-side, with human count treated as active perturbation sectors rather than unvalidated multi-person count.

### Step 2: The 95-Second Presentation Video Sync Demo (02:00 - 05:00)
- In the top navigation, click **REPLAY LAB**.
- In the **Session Library** (left column), select **`Presentation Scenario (95s Multi-Zone)`**.
- Point out the provenance badge: `SCRIPTED PRESENTATION`.
- Click **▶ PLAY** to start synchronous playback alongside your recorded room demonstration video.
- **Explain the sequence as it plays**:
  - `00:00 - 00:15`: Empty room. Active Sectors = 0, no markers.
  - `00:15 - 00:30`: Tanmay enters Zone 1. Marker **P1** appears in Zone 1 (NE).
  - `00:30 - 00:45`: Tanmay walks across to Zone 3. Marker **P1** shifts to Zone 3 (SW).
  - `00:45 - 00:55`: Tanmay exits room. Room settles, markers disappear.
  - `00:55 - 01:10`: Two simulated motion tracks enter: **P1** in Zone 2 (NW) and **P2** in Zone 4 (SE). Active Sectors = 2.
  - `01:10 - 01:25`: Both simulated tracks converge in Zone 1 (NE). Markers **P1** & **P2** visible in Zone 1.
  - `01:25 - 01:35`: Both exit. Active Sectors return to 0.

> [!IMPORTANT]
> **Scripted Demo vs Physical Validation Disclosure:**
> State clearly to evaluators: *"The 95-second replay is a scripted presentation scenario designed to demonstrate the UI multi-marker rendering engine. In contrast, our empirical spatial ML classifier is trained and evaluated strictly on physical single-occupant controlled sessions (`session_pB_*`). The real-time HUD count represents an Active Disturbed Sector Proxy ($\sum \mathbb{I}(\text{link\_energy}_i > \tau)$), not ground-truth biometric multi-person counting."*


### Step 3: Software Multi-Link Regression & Genuine Single-Link Replay (05:00 - 07:00)
- Select **`Generated Benchmark: Zone 3 Dynamic (8-Link Simulation)`** in the Session Library.
- Highlight the **`SYNTHETIC GENERATED BENCHMARK`** badge.
- Explain: *"This benchmark evaluates our 8-link sector variance spatial algorithm without pretending it was recorded from physical hardware."*
- Demonstrate the **Scrubber**: Drag the scrubber slider to jump across time windows and observe the sector variance response.
- Next, select **`Held-Out Hardware Capture: Walking Presence`** and **`Held-Out Hardware Capture: Empty Room`**:
- Highlight the **`HARDWARE RECORDED SINGLE-LINK`** badge.
- Explain: *"These are physical ESP32 captures from WiMotion v1 room trials evaluated with our 217-feature machine learning model."*

### Step 4: Model & Dataset Provenance Defense (07:00 - 09:00)
- Point to **`Public Schema Import: ESP-Fi HAR`** (`UNVERIFIED IMPORT`) and **`Synthetic Augmentation: Z3 Perturbed`** (`SYNTHETIC AUGMENTED`).
- Explain the rigorous scientific protocol:
  - Original WiMotion model (`presence_model.pkl`, 217 features, scikit-learn 1.7.2) operates through our link-level adapter.
  - Synthetic augmentation is strictly used for training diversity; held-out evaluation is only reported on genuine data.

### Step 5: Verification Suite Evidence (09:00 - 10:00)
- Switch to terminal: run:
  ```bash
  py -3.10 -m unittest discover -s tests -v
  py -3.10 scripts/verify_six_checks.py
  py -3.10 scripts/evaluate_models.py
  ```
- Show that all **56/56 unit tests pass** and all **6/6 colleague audit checks pass**.

---

## 3. Physical Hardware Deployment Checklist

> [!NOTE]
> **Status: Bench-Verified in Physical Lab Deployment (October 20-21, 2026).**
> This checklist describes the physical ESP32 setup when nodes are connected to host USB ports (`COM8` and `COM9`), as recorded in [HARDWARE_SESSION_LOG.txt](HARDWARE_SESSION_LOG.txt).
> 
> *For evaluators and reviewers without the 6 physical ESP32 boards plugged into local USB ports:* WiMotion 2.0 provides the fully reproducible **Replay Lab Mode** (`py -3.10 spatial/server.py` with playback from any of the 10 controlled `session_pB_*` recordings). Replay mode feeds the exact recorded CSI packets through the identical live feature extraction, energy gate, and spatial classifier pipeline, allowing complete interactive verification of all system behaviors without requiring physical hardware present.


| Step | Action | Expected Result | Status |
| :--- | :--- | :--- | :---: |
| **HW-1** | Flash `firmware/tx/active_sta.bin` to 4 Transmitter ESP32 boards with distinct MAC addresses (TX1-TX4). Power via 5V USB wall adapters in 4 room corners. | Blue LED blinks at active frame broadcast rate. | `VERIFIED` |
| **HW-2** | Flash `firmware/rx/active_ap.bin` to 2 Receiver ESP32 boards (RX1, RX2). Plug into laptop USB (`COM8` and `COM9`). | Devices register in Windows Device Manager as Silicon Labs CP210x / CH340 on `COM8` and `COM9`. | `VERIFIED` |
| **HW-3** | Verify baud rate and port configuration in `config/nodes.json` (`COM8` and `COM9` @ `921600` baud). | Configuration specifies `COM8` and `COM9` with matching baud. | `VERIFIED` |
| **HW-4** | Launch `py -3.10 spatial/server.py` and switch mode to `LIVE`. | Serial capture worker connects to both receivers; raw CSI frames parsed without framing errors. | `VERIFIED` |
| **HW-5** | Observe packet rate telemetry on Dashboard: verify minimum 4.0 Hz rate threshold per receiver is met. | Dashboard indicators show `RATE >= 4.0 Hz`, `SIGNAL_OK: TRUE`. | `VERIFIED` |
| **HW-6** | Baseline Calibration: Leave room empty for 10 seconds. | Zone displays `CLEAR`, active sector count = 0, presence = `empty_room`. | `VERIFIED` |
| **HW-7** | Sector Walk: Walk near TX1 (Zone 1). | Zone shifts to `Z1`, active zone count = 1, presence = `human_present`. | `VERIFIED` (Phase B Take 01 & 02) |
| **HW-8** | Full 4-Quadrant Walking Validation: Physical walk across Z1, Z2, Z3, Z4. | Recorded across 10 controlled Phase B takes (56,386 frames / 1,209 sliding windows). Z4 achieved 80.99% recall, Z2 53.72%, Z1 50.41%, Z3 14.05%. | `VERIFIED` |
