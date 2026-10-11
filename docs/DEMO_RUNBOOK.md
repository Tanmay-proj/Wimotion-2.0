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

### Step 2: The 95-Second Presentation Video Sync Demo (02:00 - 05:00)
- In the top navigation, click **REPLAY LAB**.
- In the **Session Library** (left column), select **`Presentation Scenario (95s Multi-Zone)`**.
- Point out the provenance badge: `PRESENTATION SCENARIO`.
- Click **▶ PLAY** to start synchronous playback alongside your recorded real room video.
- **Explain the sequence as it plays**:
  - `00:00 - 00:15`: Empty room. Occupancy = 0, no markers.
  - `00:15 - 00:30`: Tanmay enters Zone 1. Marker **P1** appears in Zone 1 (NE).
  - `00:30 - 00:45`: Tanmay walks across to Zone 3. Marker **P1** shifts to Zone 3 (SW).
  - `00:45 - 00:55`: Tanmay exits room. Room settles, markers disappear.
  - `00:55 - 01:10`: Two people enter! **P1** in Zone 2 (NW) and **P2** in Zone 4 (SE). Occupancy = 2.
  - `01:10 - 01:25`: Both people converge in Zone 1 (NE). Markers **P1** & **P2** visible in Zone 1.
  - `01:25 - 01:35`: Both exit. Occupancy returns to 0.

### Step 3: Genuine Hardware Replay Defense (05:00 - 07:00)
- Pause playback and select **`Hardware Benchmark: Zone 3 Dynamic (1-Person)`** in the Session Library.
- Highlight the **`HARDWARE RECORDED`** badge.
- Explain: *"This is an actual recording from our ESP32 boards in room benchmark mode. The CSI packet rate (~154 Hz), link variances, and RSSI are derived directly from the file's raw timestamps without interpolation."*
- Demonstrate the **Scrubber**: Drag the scrubber slider to jump across time windows and observe the real signal variance response.

### Step 4: Model & Dataset Provenance (07:00 - 09:00)
- Point to **`Public Dataset: ESP-Fi HAR (Walking Sample)`** (`PUBLIC DATASET`) and **`Synthetic Augmentation: Z3 Perturbed`** (`SYNTHETIC AUGMENTED`).
- Explain the rigorous scientific protocol:
  - Original WiMotion model (`presence_model.pkl`, 217 features, 94.7% CV) operates through our link-level adapter.
  - Synthetic augmentation is strictly used for training diversity; held-out evaluation is only reported on genuine data.

### Step 5: Verification Suite Evidence (09:00 - 10:00)
- Switch to terminal: run `py -3.10 -m unittest discover -s tests -v`.
- Show that all **29/29 unit tests pass**, including isolation, provenance, quality gates, and model adapter contracts.
