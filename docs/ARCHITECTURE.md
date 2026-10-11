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
- **Unknown Transmitter Policy**: Any unmapped MAC or transmitter ID is routed to `UNKNOWN` and explicitly isolated; it is **never** assigned to a default zone.

---

## 3. Data Integrity & Provenance Contract
Every session is uniquely identified with honest backend metadata:
- `hardware_recorded`: Physical capture from ESP32 boards; packet rates and timestamps strictly computed from file without interpolation.
- `scripted_presentation`: Deterministic 95-second dual-person scenario for viva/presentation video synchronization.
- `public_dataset`: External benchmark data (e.g. ESP-Fi HAR) with attributed paper/license metadata.
- `synthetic_augmented`: Controlled offline transformations tracking parent session ID, noise standard deviation, and random seed.
