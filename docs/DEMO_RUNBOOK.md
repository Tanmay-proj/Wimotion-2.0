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
- Point out the **Standby State**: Show that when no hardware is transmitting, the system reports `STANDBY / AWAITING HARDWARE` honestly rather than faking data.
- State clearly: *"In our lab kit we have 4 physical ESP32 boards. The 8-link mesh is our theoretical multi-transceiver architecture, fully implemented in our ingestion and fusion pipeline."*

### Step 2: The 95-Second Presentation Video Sync Demo (02:00 - 05:00)
- In the top navigation, click **REPLAY LAB**.
- In the **Session Library** (left column), select **`Presentation Scenario (95s Multi-Zone)`**.
- Point out the provenance badge: `SCRIPTED PRESENTATION`.
- Click **▶ PLAY** to start synchronous playback alongside your recorded real room video.
- **Explain the sequence as it plays**:
  - `00:00 - 00:15`: Empty room. Occupancy = 0, no markers.
  - `00:15 - 00:30`: Tanmay enters Zone 1. Marker **P1** appears in Zone 1 (NE).
  - `00:30 - 00:45`: Tanmay walks across to Zone 3. Marker **P1** shifts to Zone 3 (SW).
  - `00:45 - 00:55`: Tanmay exits room. Room settles, markers disappear.
  - `00:55 - 01:10`: Two people enter! **P1** in Zone 2 (NW) and **P2** in Zone 4 (SE). Occupancy = 2.
  - `01:10 - 01:25`: Both people converge in Zone 1 (NE). Markers **P1** & **P2** visible in Zone 1.
  - `01:25 - 01:35`: Both exit. Occupancy returns to 0.

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
- Show that all **34/34 unit tests pass** and all **6/6 colleague audit checks pass**.

---

## 3. Manual 4-Board Physical Hardware Checklist

> [!NOTE]
> **Status: NOT RUN in automated environment.**
> This checklist is for manual execution when physical ESP32 boards are plugged into host USB ports.

| Step | Action | Expected Result | Status |
| :--- | :--- | :--- | :---: |
| **HW-1** | Flash `firmware/src/active_sta/` to 3 Transmitter ESP32 boards with distinct MAC addresses (TX1, TX2, TX3). Power via 5V USB adapters. | Blue LED blinks at 100 Hz broadcast rate. | `NOT RUN` |
| **HW-2** | Flash `firmware/src/active_ap/` to 1 Receiver ESP32 board (RX1). Plug into laptop USB (`COM3`). | Device registers in Windows Device Manager as Silicon Labs CP210x or CH340 on `COM3`. | `NOT RUN` |
| **HW-3** | Verify baud rate configuration in `config/nodes.json` (`921600` baud). | Configuration specifies `COM3` with matching baud. | `NOT RUN` |
| **HW-4** | Launch `py -3.10 spatial/live.py --port COM3` or start server and switch mode to `LIVE`. | Serial capture worker establishes connection; raw CSI lines parsed without framing errors. | `NOT RUN` |
| **HW-5** | Observe packet rate telemetry on Dashboard: verify minimum 4.0 Hz rate threshold is met. | Dashboard indicators show `RATE >= 4.0 Hz`, `SIGNAL_OK: TRUE`. | `NOT RUN` |
| **HW-6** | Baseline Calibration: Leave room empty for 10 seconds. | Zone displays `CLEAR`, active zone count = 0, presence = `empty_room`. | `NOT RUN` |
| **HW-7** | Sector Walk: Walk near TX1 (Zone 1). | Zone shifts to `Z1`, active zone count = 1, presence = `human_present`. | `NOT RUN` |
