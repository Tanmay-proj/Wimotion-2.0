# CHAPTER 7: REAL-TIME DASHBOARD, VISUALIZATION AND REPLAY SYSTEM

---

## 7.1 Dashboard Architecture

To translate complex multi-link RF perturbation matrices into intuitive spatial telemetry, WiMotion 2.0 incorporates a high-performance, single-page **Real-Time Tactical Observatory Dashboard** (`dashboard/observatory_multi.html`).

The visualization architecture is built upon a reactive, decoupled client-server model:

```
[FASTAPI APPLICATION SERVER]  ──(WebSocket @ 10 Hz)──►  [BROWSER WEB RUNTIME]
- spatial/server.py                                     - dashboard/observatory_multi.html
- Serial Ingestion Engine                               - Vanilla CSS Dark Theme (Glassmorphism)
- Sliding Window Buffers                                - Canvas 2D Polar Radar Sweep Engine
- Feature Extraction & Inference Engine                 - Three.js WebGL 3D Room Digital Twin
- Replay Lab State Machine                              - Dual-Engine HUD & Telemetry Matrix
```

The front-end avoids heavy third-party JavaScript frameworks (such as React or Angular) to eliminate virtual DOM reconciliation overhead, ensuring deterministic 60 FPS canvas rendering even during rapid serial bursts.

---

## 7.2 Backend, WebSocket Communication and Front-End

Data synchronization between the Python backend and browser runtime is established via an asynchronous WebSocket connection (`ws://127.0.0.1:8000/ws`):
- **Serialization Rate:** Every 100 milliseconds ($10\text{ Hz}$ update rate), the backend serializes the current link health, aggregate CSI packet rates, 8-link variance values, heuristic spatial estimation, and supervised model probabilities into a JSON telemetry packet.
- **Bi-Directional Command Channel:** The same WebSocket interface allows the operator to send operational commands from the browser to the backend, including mode transitions (`LIVE`, `REPLAY`, `SIMULATION`), session loading, and scrubber seek requests.

---

## 7.3 Live Hardware Monitoring Interface

The top tier of the dashboard provides continuous diagnostic metrics across four primary telemetry cards:

```
┌───────────────────┬───────────────────┬───────────────────┬────────────────────────────┐
│  VALID CSI RATE   │   ACTIVE LINKS    │  RECEIVER HEALTH  │  HEURISTIC & SUPERVISED    │
│     102.4 Hz      │   8 / 8 ACTIVE    │   2 / 2 ONLINE    │  ZONE: Z1 (NE)             │
│  Window: 2.0s sl. │  Freshness: <1.0s │ RX1:COM8 RX2:COM9 │  SUPERVISED ML: Z1 (68%)   │
└───────────────────┴───────────────────┴───────────────────┴────────────────────────────┘
```

1. **Card 1: Valid CSI Rate:** Displays the aggregate packet arrival frequency across both receivers, dynamically calculated over the 2.0-second sliding window buffer. Includes real-time indicators for per-receiver rates (`RX1: 51.2 Hz | RX2: 51.2 Hz`).
2. **Card 2: Active Links Matrix:** Shows the count of active spatial baselines meeting the freshness threshold ($t_{\text{last}} < 3.0\text{s}$) alongside stale link alerts.
3. **Card 3: Receiver Hardware Health:** Monitors USB serial connection state across `COM8` and `COM9`, indicating synchronization locks and baud health.
4. **Card 4: Spatial Classification HUD:** Displays current zone disturbance estimates, maximum link variance score, and model confidence percentages.

---

## 7.4 Four-Quadrant Spatial Visualization (2D Radar Sweep)

The central workstation features a custom HTML5 Canvas **2D Polar Radar Sweep**:
- **Polar Coordinates:** Visualizes the room partitioned into four quadrants centered around the host receivers ($Z_1$ at $45^\circ$, $Z_2$ at $315^\circ$, $Z_3$ at $225^\circ$, $Z_4$ at $135^\circ$).
- **Dynamic Heat Glow:** The background phosphor intensity of each sector scales logarithmically with the instantaneous temporal variance ($\sigma^2$) of its primary line-of-sight RF links.
- **Sweeping Beam:** An animated radar sweep line rotates at 30 RPM, providing immediate visual feedback of active signal scanning.
- **[Figure 7.1: Screenshot of 2D Polar Radar Sweep During Quadrant 1 Subject Traversal]**

---

## 7.5 Three-Dimensional Room Visualization (Three.js WebGL Engine)

To provide spatial depth, the dashboard integrates a 3D perspective wireframe room model rendered via the Three.js WebGL library:
- **Spatial Geometry:** A scale wireframe perspective of `ROOM_LAB_A` with dimension markers.
- **Node Placements:** Four corner transmitter beacons (color-coded cyan and amber) with dynamic pulsating halos reflecting packet transmission.
- **Dynamic Disturbance Marker ($P_1$):** When a spatial quadrant exceeds the motion threshold, a 3D avatar marker interpolates toward the centroid of the disturbed quadrant with smooth exponential easing.
- **[Figure 7.2: Screenshot of 3D Perspective Digital Twin Room Showing Detected Subject Marker]**

*Important Technical Clarification:* The moving 3D avatar marker represents the centroid of the **detected RF disturbance zone**; it is an intuitive graphical indicator, NOT a physical millimeter-accurate radar point-cloud track.

---

## 7.6 Heuristic and Machine-Learning Outputs (Dual-Engine HUD)

To maintain complete intellectual honesty during demonstrations, WiMotion 2.0 displays two independent spatial outputs side-by-side on the real-time HUD:

```
[DUAL-ENGINE HUD TELEMETRY]
├── HEURISTIC ZONE (BASELINE):  Z1 (NE)  [Max Var Ratio: 0.64]
└── SUPERVISED ML PREDICTION:   Z1 (NE)  [Confidence: 68.4%]
```

1. **Heuristic Zone (Physical Ratio Baseline):** Calculated purely from the ratio of maximum link variance without querying machine learning decision trees.
2. **Supervised ML Prediction:** Emitted by the 56-D Random Forest classifier, gated by the empirical energy threshold ($\theta = 1.80$).
- When both engines agree, the operator has high confidence in spatial disturbance. When they diverge, the UI highlights the ambiguity, enabling evaluators to inspect baseline multipath behavior in real time.

---

## 7.7 Active-Sector Indicators Versus Actual People Counting

A common pitfall in indoor RF sensing demonstrations is claiming that energy perturbations represent verified "people counts." 

WiMotion 2.0 explicitly rejects this false equivalence:
- The dashboard displays an indicator titled **`ACTIVE ZONES PROXY`** with an explicit tooltip disclosure:
  $$\text{Active Sector Count} = \sum_{k=1}^{4} \mathbb{I}(\text{Link Energy}_k > \tau)$$
- If two individuals walk together within Zone 1, the system reports **1 Active Zone**.
- Conversely, if a single individual walks along the boundary dividing Zone 1 and Zone 2, boundary multipath leakage may briefly perturb both links, reporting **2 Active Zones**.
- The indicator is formally documented as an **Active Disturbed Sector Proxy**, NOT ground-truth biometric multi-person counting.

---

## 7.8 Recorded-Session Replay and Timeline Controls

To enable comprehensive evaluation without requiring physical hardware connected during viva examinations, the dashboard features a full-featured **Replay Lab**:
- **Session Library:** A side navigation panel listing all audited benchmark recordings (`session_pB_*`, `benchmark_session_01`).
- **Scrubber Slider:** An interactive timeline slider allowing operators to jump to arbitrary time offsets within a recording.
- **Playback Controls:** Play, pause, step forward, and playback speed multipliers ($1\times, 2\times, 4\times$).
- **Bit-Exact Reproduction:** The replay loader reads raw recorded CSV packet lines and streams them through the exact same feature extraction and inference functions, reproducing identical telemetry to live hardware.
- **[Figure 7.3: Screenshot of Replay Lab Interface Showing Interactive Scrubber and Session Manifest]**

---

## 7.9 Live, Replay and Simulation Mode Separation

To prevent data contamination, the server enforces strict transactional mode isolation governed by an authoritative state machine:

```
                  ┌──────────────┐
                  │ SAFE STANDBY │
                  └──────┬───────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   ┌─────────┐      ┌──────────┐    ┌────────────┐
   │  LIVE   │◄────►│  REPLAY  │◄──►│ SIMULATION │
   └─────────┘      └──────────┘    └────────────┘
```

- In `LIVE` mode, the server connects to physical serial ports `COM8` and `COM9`.
- In `REPLAY` mode, serial ports are placed in Safe Standby, and packets are sourced exclusively from recorded CSV files.
- In `SIMULATION` mode, synthetic link benchmarks are generated algorithmically for regression testing.
- Mode transitions are strictly verified: any invalid mode switch request is rejected with HTTP 400, preserving existing state without leakage.

---

## 7.10 Dashboard Demonstration and Known Limitations

While the Observatory Dashboard delivers high operational clarity, two technical limitations are noted:
1. **Browser WebGL Resource Contention:** On low-power host laptops lacking dedicated GPUs, rendering complex Three.js perspective meshes at 60 FPS can cause brief 20–30 ms JavaScript main-thread pauses.
2. **Sliding Window Visual Delay:** Because the feature pipeline operates on 2.0-second sliding windows, visual quadrant transitions exhibit an inherent ~0.5-second smoothing latency following physical walking shifts.

---
*(End of Chapter 7 — Source: dashboard/observatory_multi.html and spatial/server.py)*
