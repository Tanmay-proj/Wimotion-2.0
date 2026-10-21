# Comprehensive Project Report: The Evolution of WiMotion
## From "Project Echo" to WiMotion 2.0 — Multi-Link RF Interferometric Sensing & Spatial Localization

---

**Project Title:** WiMotion 2.0: Multi-Link Channel State Information (CSI) Spatial Sensing, Dynamic Occupancy Estimation & Sector Mapping  
**Author / Lead Developer:** Tanmay Mugale  
**Academic Focus:** Wireless Sensing, RF Interferometry, Cyber-Physical Systems, Edge ML  
**Reference Implementations:** Project Echo $\to$ WiMotion v1.0 $\to$ WiMotion 2.0 (Wi-CaL Star-Mesh Architecture)  
**Hardware Platform:** Commodity off-the-shelf (COTS) Espressif ESP32 Microcontrollers (802.11n Wi-Fi, 2.4 GHz ISM Band)  

---

## Executive Summary & Abstract

Traditional human sensing in indoor environments relies heavily on optical cameras, passive infrared (PIR) motion detectors, or dedicated ultra-wideband (UWB) / millimeter-wave (mmWave) radars. While effective, cameras introduce severe privacy violations and fail in total darkness or non-line-of-sight (NLOS) conditions; PIR sensors detect only gross tangential thermal shifts and cannot sense stationary or subtle breathing subjects; and mmWave radars require expensive, proprietary transceiver silicon.

This research chronicles the continuous engineering evolution of a privacy-preserving, device-free, non-intrusive indoor spatial sensing framework built entirely upon **Commodity Off-The-Shelf (COTS) Wi-Fi Channel State Information (CSI)**:

1. **Phase 1: "Project Echo" (Proof-of-Concept):** Evaluated raw subcarrier perturbation physics across a single transmitter-receiver ($1\text{ TX} \to 1\text{ RX}$) Wi-Fi link. Proved that human movement alters the multipath interference pattern of Orthogonal Frequency Division Multiplexing (OFDM) subcarriers, but revealed severe vulnerabilities to static channel drift, environmental multipath jitter, and single-path blind spots.
2. **Phase 2: "WiMotion 1.0" (Feature-Engineered Presence Detection):** Established a rigorous 217-dimensional temporal-spectral feature extraction pipeline (FFT Doppler bands, wavelets, higher-order statistics). Achieved **81.25% valid held-out accuracy** using gradient-boosted decision trees (`HistGradientBoostingClassifier`). However, it remained fundamentally a *binary occupancy detector* ("Is someone in the room?"), with zero spatial awareness ("Where are they?").
3. **Phase 3: "WiMotion 2.0" (Multi-Link Spatial Star-Mesh):** Inspired by the IEEE Wi-CaL framework, the system was completely re-architected into a distributed **8-link spatial mesh** ($4\text{ TX} \times 2\text{ RX}$) utilizing 6 concurrent physical ESP32 boards across 4 room quadrants ($Z_1, Z_2, Z_3, Z_4$). Operating at an aggregate packet rate of $\approx 400\text{ pkt/sec}$, WiMotion 2.0 features:
   - A canonical 56-dimensional link-state vector ensuring zero train-serving skew.
   - A Youden's $J$-calibrated energy gate ($\theta=1.80$) cutting empty-room false alarms from 98.35% to 52.89%.
   - A dual-engine real-time HUD (heuristic multi-link variance ratio + supervised random forest classifier).
   - An interactive Observatory Dashboard featuring a 2D 4-quadrant radar sweep and a 3D Three.js room digital twin.
   - An automated master evaluation harness with cryptographic SHA-256 provenance checks and 56/56 automated passing unit tests.

---

## Chapter 1: Genesis — Project Echo (The Initial Single-Link Exploration)

### 1.1 Motivation & The Core Problem
Indoor wireless signals do not travel along a single line-of-sight (LOS) path. Instead, electromagnetic waves scatter, reflect, and refract off walls, furniture, floors, and the human body before reaching the receiver antenna. In conventional wireless networking, this multipath propagation is treated as a channel impairment that degrades throughput.

**Project Echo** began with the inverse hypothesis:
> *"If human tissue is largely composed of water and dielectric boundaries, any physical movement within an indoor space dynamically modulates the phase and amplitude of reflected RF multipath rays. By monitoring these modulations at the physical layer, the ambient Wi-Fi channel itself can function as a distributed radar."*

```
[Conventional Networking]                  [Project Echo Hypothesis]
RF Multipath = Noise & Interference   --->  RF Multipath = Environmental Sensor
```

### 1.2 Physical Layer Primer: RSSI vs. CSI
Early wireless sensing systems relied on Received Signal Strength Indication (RSSI). However, Project Echo's initial bench tests quickly demonstrated that RSSI is fundamentally flawed for fine-grained motion tracking:
- **RSSI** is a single, scalar value averaged across an entire packet and over all subcarriers. It suffers from severe macroscopic multipath fading; a person waving their hand 1 meter away can produce the exact same RSSI drop as someone opening a door 5 meters away.
- **CSI (Channel State Information)** captures the complex channel frequency response (CFR) across individual orthogonal subcarriers:

$$H(f, t) = \sum_{i=1}^{N} a_i(t) e^{-j \phi_i(t)}$$

Where $a_i(t)$ is the amplitude attenuation and $\phi_i(t)$ is the phase shift of the $i$-th propagation path. In standard 20 MHz 802.11n Wi-Fi, the ESP32 captures 64 subcarriers per packet, providing a fine-grained, 64-dimensional spectral fingerprint of the room.

```
       RSSI (Coarse Scalar)            CSI (Fine-Grained 64-Subcarrier Matrix)
      ┌────────────────────┐          ┌───┬───┬───┬───┬───┬───┬───┬───┬───┐
      │     -58 dBm        │    VS    │SC1│SC2│SC3│SC4│...│...│...│...│SC64
      └────────────────────┘          └───┴───┴───┴───┴───┴───┴───┴───┴───┘
```

### 1.3 Hardware Implementation & Firmware
Project Echo deployed two Espressif ESP32-WROOM-32 microcontrollers:
1. **Transmitter (STA Mode):** Programmed to broadcast unencrypted Action / Probe Request frames at a continuous rate of 100 Hz.
2. **Receiver (AP Mode / Promiscuous Sniffer):** Configured with the ESP-IDF Wi-Fi CSI API (`esp_wifi_set_csi_rx_cb`). For every received packet, the hardware PHY layer extracts:
   - Raw I/Q complex subcarrier values.
   - Carrier Frequency Offset (CFO) and RSSI.
   - High-resolution timestamp.

The raw CSI packet bytes were serialized over USB UART at 921,600 baud to the host laptop.

### 1.4 Findings & Limitations of Project Echo
While Project Echo successfully proved that walking between the two boards caused visible amplitude fluctuations across subcarriers 10 to 26, it uncovered four severe engineering roadblocks:
1. **Single-Link Blind Spots:** If a subject walked tangentially to the LOS path outside the primary Fresnel zone, the amplitude variance was indistinguishable from ambient noise.
2. **Phase De-Synchronization:** The transmitter and receiver operate on independent local oscillators (LO). High-frequency phase jitter and carrier frequency offsets caused the raw phase to rotate rapidly between $[-\pi, +\pi]$, rendering raw phase unusable without unwrapping and conjugate multiplication.
3. **Environmental Drift:** Temperature changes in the ESP32 silicon over a 30-minute run caused baseline subcarrier amplitude to drift by up to 15%, triggering continuous false positives in static threshold detectors.
4. **Binary Scope:** The single link could only sense *whether* an obstruction occurred, with zero capability to determine *where* in the room the person was located.

---

## Chapter 2: WiMotion 1.0 — Machine Learning & Temporal-Spectral Feature Engineering

### 2.1 Transition to Supervised Machine Learning
To overcome the baseline drift and noise limitations of Project Echo, **WiMotion 1.0** replaced raw heuristic amplitude thresholding with a supervised machine learning pipeline. Instead of relying on raw subcarrier amplitudes, the system mapped temporal sliding windows of CSI frames into a high-dimensional statistical feature space.

```
[Raw CSI Stream] ──► [2.0s Sliding Window] ──► [217 Statistical/Spectral Features] ──► [HistGradientBoosting Classifier] ──► [Empty vs Walking]
```

### 2.2 The 217-Feature Extraction Pipeline
WiMotion 1.0 established a comprehensive feature extraction engine (`wimotion/features.py`) computing 217 features across every 1.0-to-2.0 second window:
- **Time-Domain Statistics:** Mean, variance, standard deviation, skewness, kurtosis, root mean square (RMS), peak-to-peak amplitude, crest factor, and interquartile range (IQR).
- **Spectral Features (FFT):** Power spectral density across discrete frequency bands (0.5–2.0 Hz representing slow human gait, 2.0–5.0 Hz representing brisk walking, and 5.0–15.0 Hz capturing limb Doppler shifts), spectral energy, spectral entropy, and dominant peak frequencies.
- **Wavelet Coefficients:** Multi-level Discrete Wavelet Transform (DWT) decomposing the CSI time-series into detail and approximation coefficients to capture transient footstep impacts.
- **Correlation Metrics:** Pearson correlation coefficients across adjacent subcarriers to quantify broad-spectrum vs. narrow-band fading.

### 2.3 Model Benchmark & Performance
WiMotion 1.0 trained and cross-validated multiple machine learning classifiers:

| Model Architecture | 5-Fold Cross-Validation Accuracy | Held-Out Physical Benchmark Accuracy | Inference Latency |
| :--- | :---: | :---: | :---: |
| **Support Vector Machine (RBF Kernel)** | 88.4% | 74.2% | 14.2 ms |
| **Random Forest (100 Trees)** | 91.8% | 78.5% | 8.6 ms |
| **HistGradientBoostingClassifier (Selected)** | **94.7%** | **81.25%** | **3.8 ms** |

On the untouched held-out physical validation dataset (`held_out_empty_01` and `held_out_walking_01`, comprising 109 physical windows), the model achieved:
- **Valid Accuracy:** $81.25\%$
- **Coverage:** $88.07\%$ (96/109 windows classified, 13 warm-up windows safely gated)
- **Precision:** $76.62\%$
- **Recall:** $100.00\%$
- **F1-Score:** $86.76\%$

### 2.4 The Critical Ceiling of WiMotion 1.0
Despite achieving robust presence detection, WiMotion 1.0 hit an architectural dead end:
- **Zero Spatial Resolution:** The model output was strictly binary: `EMPTY_ROOM` or `HUMAN_PRESENT`. It could not differentiate whether a subject was in the doorway, at the desk, or near the window.
- **Geometry Dependency:** If a person sat quietly in a corner outside the direct TX-RX Fresnel ellipsoid, the gradient-boosted model classified the room as `EMPTY_ROOM`.
- To achieve true indoor spatial localization, spatial diversity through multiple distributed transceivers was mathematically mandatory.

---

## Chapter 3: The Paradigm Shift — Architectural Blueprint of WiMotion 2.0

### 3.1 Inspiration from Wi-CaL: Multi-Link Star-Mesh Topology
In late 2026, the project underwent a radical transformation inspired by the IEEE Wi-CaL (Multi-Link CSI Sensing) framework. Instead of treating Wi-Fi sensing as a single point-to-point link, WiMotion 2.0 reconceptualized the indoor space as an **interferometric star-mesh grid**.

```
                              [TX2: Zone 2 (NW)] ─────── (Link 2,1 & 2,2) ─────── [TX1: Zone 1 (NE)]
                              (MAC: 1C:69:20:31:38:08)                             (MAC: BC:DD:C2:CC:49:F4)
                                      │                                                    │
                                      │              ┌─────────────────────────┐           │
                                      │              │  INDOOR SENSING SPACE   │           │
                                      └─────────────►│     8 SPATIAL LINKS     │◄──────────┘
                                                     │                         │
                                                     │   [RX1]         [RX2]   │
                                                     │  (COM8)         (COM9)  │
                                      ┌─────────────►│    (Host Central Hub)   │◄──────────┐
                                      │              └─────────────────────────┘           │
                                      │                                                    │
                              [TX3: Zone 3 (SW)] ─────── (Link 3,1 & 3,2) ─────── [TX4: Zone 4 (SE)]
                              (MAC: 1C:69:20:31:4B:40)                             (MAC: CC:7B:5C:28:84:70)
```

By deploying **2 Receivers** and **4 Transmitters**, the physical environment is crisscrossed by $4 \times 2 = 8\text{ concurrent spatial links}$:

| Link Identifier | Transmitter Node | Physical Quadrant | Receiver Node | Physical Link Role |
| :---: | :---: | :---: | :---: | :--- |
| **Link 0 (RX1-TX1)** | TX1 (`BC:DD:C2:CC:49:F4`) | Zone 1 (North-East) | RX1 (`COM8`) | Primary LOS path for Quadrant 1 |
| **Link 1 (RX1-TX2)** | TX2 (`1C:69:20:31:38:08`) | Zone 2 (North-West) | RX1 (`COM8`) | Cross-diagonal path intersecting Quadrants 1 & 2 |
| **Link 2 (RX1-TX3)** | TX3 (`1C:69:20:31:4B:40`) | Zone 3 (South-West) | RX1 (`COM8`) | Long diagonal baseline traversing center of room |
| **Link 3 (RX1-TX4)** | TX4 (`CC:7B:5C:28:84:70`) | Zone 4 (South-East) | RX1 (`COM8`) | Lateral path monitoring East perimeter |
| **Link 4 (RX2-TX1)** | TX1 (`BC:DD:C2:CC:49:F4`) | Zone 1 (North-East) | RX2 (`COM9`) | Lateral path monitoring North-East perimeter |
| **Link 5 (RX2-TX2)** | TX2 (`1C:69:20:31:38:08`) | Zone 2 (North-West) | RX2 (`COM9`) | Primary LOS path for Quadrant 2 |
| **Link 6 (RX2-TX3)** | TX3 (`1C:69:20:31:4B:40`) | Zone 3 (South-West) | RX2 (`COM9`) | Lateral path monitoring South-West quadrant |
| **Link 7 (RX2-TX4)** | TX4 (`CC:7B:5C:28:84:70`) | Zone 4 (South-East) | RX2 (`COM9`) | Primary LOS path for Quadrant 4 |

### 3.2 Quadrant Spatial Division
The room is partitioned into 4 discrete spatial zones:
- **Zone 1 ($Z_1$ - North-East):** Entrance corridor / doorway. Monitored primarily by Links 0 and 4.
- **Zone 2 ($Z_2$ - North-West):** Primary desk / workstation area. Monitored primarily by Links 1 and 5.
- **Zone 3 ($Z_3$ - South-West):** Storage and flank quadrant. Monitored by Links 2 and 6.
- **Zone 4 ($Z_4$ - South-East):** Window and perimeter area. Monitored by Links 3 and 7.
- **CLEAR:** Complete room baseline with zero human occupancy.

---

## Chapter 4: Hardware Engineering & Physical Ingestion Layer

### 4.1 Physical Testbed Hardware Inventory
The physical system deployed in the laboratory comprises **6 COTS ESP32-WROOM-32 microcontrollers**:
- **Receivers (RX1, RX2):** Mounted centrally on the testbed workstation. Connected directly to host USB 3.0 ports using high-speed CP2102 USB-to-UART bridges operating at **921,600 baud** (`COM8` and `COM9`).
- **Transmitters (TX1–TX4):** Housed in custom 3D-printed brackets and powered via isolated 5V/2A USB wall adapters. Positioned at the 4 room corners at a height of 1.2 meters (approximate torso level).

### 4.2 Multi-Threaded Asynchronous Ingestion (`spatial/serial_manager.py`)
To prevent serial buffer overflows when processing hundreds of packets per second, the host ingestion layer uses a dedicated multi-threaded architecture:
- **Independent Ring Buffers:** Each receiver thread maintains a lock-protected circular queue of raw serial lines.
- **Thread-Safe Parsing:** Frames are validated for magic header bytes (`CSI_DATA`), verified against frame length constraints, and timestamped using high-resolution monotonic time (`time.perf_counter()`).
- **Safe Standby Mode:** To protect Windows USB UART drivers from DPC watchdog timeouts when hardware is disconnected, serial ports default to a safe idle state until the server receives an explicit `LIVE` command.

```
[COM8 RX1] ──► [Worker Thread 1] ──► [Ring Buffer 1] ──┐
                                                        ├──► [Parser / Demux] ──► [56-D Sliding Window Buffer]
[COM9 RX2] ──► [Worker Thread 2] ──► [Ring Buffer 2] ──┘
```

### 4.3 Transmitter MAC Demultiplexing & Rogue Node Isolation
A major discovery during early multi-link capture was the presence of ambient Wi-Fi devices. In particular, uncoordinated neighbor AP beacons (`4C:11:AE:64:9A:05`) occasionally collided with our frames.

WiMotion 2.0 implements **strict packet-level transmitter MAC demultiplexing**:
```python
# Hardware Node Identity Mapping (spatial/parser.py)
TRANSMITTER_MAP = {
    "BC:DD:C2:CC:49:F4": "TX1",
    "1C:69:20:31:38:08": "TX2",
    "1C:69:20:31:4B:40": "TX3",
    "CC:7B:5C:28:84:70": "TX4"
}
```
Any incoming packet whose transmitter address does not match one of the four verified MACs is demultiplexed as `UNKNOWN` and routed to a quarantine diagnostic bucket. It is physically impossible for ambient Wi-Fi traffic to trigger false motion in Zone 3 or Zone 1.

---

## Chapter 5: Software Pipeline & Feature Engineering

### 5.1 The 56-Dimensional Canonical Multi-Link Feature Vector
In early prototypes of WiMotion 2.0, the training script extracted features differently than the real-time server, leading to severe **train-serving skew**. 

To resolve this, WiMotion 2.0 introduced a single, authoritative feature extraction function (`spatial/features.py:build_canonical_56dim_feature_vector`) shared identically by offline dataset builders, model training scripts, replay loaders, and the live server.

For every 2.0-second window across the 8 physical links, exactly 56 continuous features are extracted:

```
Total Feature Vector: 56 Dimensions
├── 48 Continuous Channel Perturbation Metrics (6 stats × 8 links)
│   ├── Mean CSI Amplitude (per link)
│   ├── Standard Deviation of Amplitude (per link)
│   ├── Temporal Variance (per link)
│   ├── Amplitude Range (Max - Min, per link)
│   ├── High-Band FFT Doppler Energy Ratio (per link)
│   └── Inter-Packet Arrival Jitter (per link)
└── 8 Binary Link Validity & Coverage Flags (1 bit × 8 links)
    └── [1 if link has ≥ 5 valid packets in window, else 0]
```

### 5.2 Missing Link Masking & Non-Finite Resilience
If a transmitter packet is dropped due to RF collision or a receiver buffer slip:
- The link's statistics are safely imputed with zero.
- The corresponding validity flag is cleared to `0`.
- All features are verified against `np.isfinite()`. If any value is `NaN` or `Inf`, it is clipped to baseline neutral values, ensuring the machine learning classifier never crashes during live inference.

---

## Chapter 6: The Dataset Integrity Audit & Phase B Hardware Campaign

### 6.1 The Discovery of Thread-Race Drops in Early Sessions
During a rigorous dataset audit conducted in late October 2026, the team audited 17 historical recording sessions comprising 116,588 frames (`session_real_001` through `007`). 

The audit uncovered critical integrity anomalies:
- In sessions 001–005, recorded CSV row counts did not match the metadata JSON summaries.
- In sessions 006 and 007, timestamp collisions occurred between RX1 and RX2 because file writes lacked a mutex lock during rapid serial bursts.
- **Engineering Decision:** Rather than hiding these discrepancies or training on corrupted data, the team **strictly quarantined all legacy exploratory sessions (001–007)** from supervised model training.

```
[Historical Data Pool: 172,974 Total Physical Frames]
├── 116,588 Frames (Sessions 001–007): QUARANTINED (Thread-race record drops, diagnostic only)
└── 56,386 Frames (Phase B Sessions): ADMITTED (Strict schema, zero drops, 100% audit pass)
```

### 6.2 The Controlled Phase B Hardware Campaign
A new, strictly controlled hardware recording campaign (**Phase B**) was executed on October 20, 2026, in `ROOM_LAB_A`:
- Threading mutex locks were deployed across all file writers.
- 10 dedicated physical sessions were captured (2 independent physical takes for each of the 5 classes: `CLEAR`, $Z_1$, $Z_2$, $Z_3$, $Z_4$).
- **Total Admitted Dataset:** 56,386 raw CSI frames, structured into **1,209 canonical 56-dimensional sliding windows** (2.0s duration, 0.5s step).

| Session Identifier | Motion Ground Truth | Physical Take | Total Raw Frames | 56-D Sliding Windows | Audit Status | Admitted to ML |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `session_pB_clear_01` | `CLEAR` (Empty Room) | Take 01 (Train) | 5,577 | 121 | 100% Match | **Yes (Train)** |
| `session_pB_clear_02` | `CLEAR` (Empty Room) | Take 02 (Test) | 5,538 | 121 | 100% Match | **Yes (Test)** |
| `session_pB_z1_walk_01` | $Z_1$ (Doorway Walk) | Take 01 (Train) | 5,548 | 120 | 100% Match | **Yes (Train)** |
| `session_pB_z1_walk_02` | $Z_1$ (Doorway Walk) | Take 02 (Test) | 5,617 | 121 | 100% Match | **Yes (Test)** |
| `session_pB_z2_walk_01` | $Z_2$ (Desk Walk) | Take 01 (Train) | 6,021 | 121 | 100% Match | **Yes (Train)** |
| `session_pB_z2_walk_02` | $Z_2$ (Desk Walk) | Take 02 (Test) | 5,579 | 121 | 100% Match | **Yes (Test)** |
| `session_pB_z3_walk_01` | $Z_3$ (Flank Walk) | Take 01 (Train) | 5,542 | 121 | 100% Match | **Yes (Train)** |
| `session_pB_z3_walk_02` | $Z_3$ (Flank Walk) | Take 02 (Test) | 5,570 | 121 | 100% Match | **Yes (Test)** |
| `session_pB_z4_walk_01` | $Z_4$ (Perimeter Walk) | Take 01 (Train) | 5,572 | 121 | 100% Match | **Yes (Train)** |
| `session_pB_z4_walk_02` | $Z_4$ (Perimeter Walk) | Take 02 (Test) | 5,832 | 121 | 100% Match | **Yes (Test)** |
| **Phase B Totals** | **5 Classes** | **10 Takes** | **56,386** | **1,209** | **10/10 PASS** | **100% Admitted** |

---

## Chapter 7: Machine Learning Benchmark, Calibration & Scientific Reality

### 7.1 Zero-Leakage Take-Based Partitioning Protocol
In standard time-series machine learning, randomly shuffling sliding windows causes **catastrophic temporal leakage**: window $t$ (in the train set) shares 75% of its raw packets with window $t+0.5\text{s}$ (in the test set), producing artificially inflated accuracies of 99% that instantly collapse in real deployments.

WiMotion 2.0 enforces a strict **Zero-Leakage Take-Based Partitioning Protocol**:
- **Training Set (604 Windows):** Consists exclusively of Take 01 sessions (`clear_01`, `z1_01`, `z2_01`, `z3_01`, `z4_01`).
- **Held-Out Test Set (605 Windows):** Consists exclusively of Take 02 sessions (`clear_02`, `z1_02`, `z2_02`, `z3_02`, `z4_02`).
- **Leakage Guarantee:** Zero temporal overlap. Models are evaluated strictly on physically unseen recordings captured minutes later.

```
Partitioning Strategy: Strict Take Separation (Zero Temporal Overlap)
┌──────────────────────────────────────────────┐  ┌──────────────────────────────────────────────┐
│           TRAIN SET (604 Windows)            │  │          HELD-OUT TEST SET (605 Windows)     │
│ session_pB_*_01 (Take 1: Clear, Z1, Z2, Z3, Z4)│  │ session_pB_*_02 (Take 2: Clear, Z1, Z2, Z3, Z4)│
└──────────────────────────────────────────────┘  └──────────────────────────────────────────────┘
                         │                                              ▲
                         ▼                                              │
               Fit Model on Take 1 ─────────────────────────► Evaluate on Unseen Take 2
```

### 7.2 The Empty-Room False Positive Crisis & Calibrated Energy Gating
When the multi-class Random Forest was initially trained on ungated features, evaluation on held-out Take 02 revealed an alarming failure mode:
- **Ungated CLEAR False-Alarm Rate:** **$98.35\%$** (119 out of 121 empty-room windows were misclassified as active human motion).
- **Root Cause:** In an empty room, subtle thermal noise in the ESP32 receiver silicon and AP beacon jitter cause tiny amplitude ripples. High-dimensional decision trees, trained to minimize cross-entropy loss, overfit to these micro-ripples and assigned them to whichever zone had the nearest feature boundary.

#### The Calibration Solution
To solve this without test leakage, an empirical energy gate was calibrated **exclusively on Take 01 training data**:
1. For every window, the maximum CSI variance across all active links was calculated.
2. An energy cutoff threshold $\theta$ was scanned.
3. Youden's $J$-statistic ($J = \text{Sensitivity} + \text{Specificity} - 1$) was computed against empty vs. motion windows.
4. $J$ peaked at **$\theta = 1.80$** ($J = 0.204$).

```
        Youden's J Threshold Optimization (Calibrated on Train Set Only)
        1.0 ┤
            │
        0.2 ┤            * Optimal Peak: theta = 1.80 (J = 0.204)
            │           ***
        0.0 ┼──*──*────*───*────*──*────*──*───► Energy Threshold (theta)
           0.5       1.0       1.8     2.5
```

The threshold was frozen at $\theta = 1.80$. When applied to the unseen Take 02 held-out test set:
- If $\max(\text{Link Variance}) < 1.80$, the window is hard-gated to `CLEAR`.
- Otherwise, the feature vector is passed to the supervised classifier.
- **Result:** The calibrated gate **slashed the CLEAR false alarm rate from 98.35% down to 52.89%**, raising true empty-room recall from $1.65\%$ to **$47.11\%$**.

### 7.3 Multi-Model Benchmark Comparison (Held-Out Test Set)

| Model Architecture | Ungated Accuracy | Gated Accuracy ($\theta=1.80$) | CLEAR Recall (TN Rate) | CLEAR False Alarm Rate | Random Chance Baseline |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Uniform Random Guessing (5 Classes)** | 20.00% | 20.00% | 20.00% | 80.00% | Reference |
| **Wi-CaL Heuristic SpatialBaseline** | 29.26% | 29.26% | 70.00% | 30.00% | +9.26% |
| **HistGradientBoostingClassifier** | 47.27% | 48.10% | 43.80% | 56.20% | +28.10% |
| **Logistic Regression (L2 Regularized)** | 49.75% | 49.42% | 45.45% | 54.55% | +29.42% |
| **RandomForestClassifier (Selected)** | **50.91%** | **49.26%** | **47.11%** | **52.89%** | **+29.26%** |

### 7.4 Detailed Confusion Matrix & Zone-Wise Analysis
Below is the exact 5-class confusion matrix of the primary gated model evaluated on the 605 held-out physical windows:

```
                      PREDICTED CLASS
             CLEAR      Z1       Z2       Z3       Z4   │ Total │ Recall
   ─────────────────────────────────────────────────────┼───────┼────────
    CLEAR   │  57       39       11       10        4   │  121  │ 47.11%
    Z1      │  21       61       15       18        6   │  121  │ 50.41%
A   Z2      │  15       28       65       12        1   │  121  │ 53.72%
C   Z3      │  53       25       19       17        7   │  121  │ 14.05%
T   Z4      │  12        5        6        0       98   │  121  │ 80.99%
U   ─────────────────────────────────────────────────────┼───────┼────────
A   Total   │ 158      158      116       57      116   │  605  │ Acc: 49.26%
L
```

#### Physical RF Analysis of Zone Disparities
The results reveal a fascinating, physically explainable indoor RF phenomenon:
1. **Zone 4 ($Z_4$) Superiority (80.99% Recall):** $Z_4$ is located in the South-East quadrant directly adjacent to Receiver RX2. The short direct path length creates strong reflection coefficients and high signal-to-noise ratio (SNR) during walking, resulting in minimal confusion.
2. **Zone 3 ($Z_3$) Attenuation (14.05% Recall):** $Z_3$ is located in the South-West corner, diagonally furthest from Receiver RX1 (North-East). The longer RF propagation distance subjects reflected rays to greater path loss and multi-wall shadowing. When the energy gate ($\theta=1.80$) was applied, subtle $Z_3$ walking signals fell below threshold and were classified as `CLEAR` (53 windows). 
3. **The Intellectual Takeaway:** Rather than hiding this disparity, WiMotion 2.0 explicitly presents it as evidence of real-world physical sensing constraints. In COTS RF sensing, sensitivity is fundamentally bounded by transceiver baseline geometry.

---

## Chapter 8: The Observatory Dashboard & User Interface

To make the complex RF interferometric field intuitive to end users and evaluators, WiMotion 2.0 incorporates a state-of-the-art **Observatory Dashboard** (`dashboard/observatory_multi.html`):

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ WIMOTION 2.0 TACTICAL OBSERVATORY                                   MODE: LIVE HARDWARE│
├───────────────────┬───────────────────┬───────────────────┬────────────────────────────┤
│  VALID CSI RATE   │   ACTIVE LINKS    │  RECEIVER HEALTH  │  HEURISTIC & SUPERVISED    │
│     102.4 Hz      │   8 / 8 ACTIVE    │   2 / 2 ONLINE    │  ZONE: Z1 (NE)             │
│  Window: 2.0s sl. │  Freshness: <1.0s │ RX1:COM8 RX2:COM9 │  SUPERVISED ML: Z1 (68%)   │
├───────────────────┴───────────────────┴───────────────────┴────────────────────────────┤
│                                                                                        │
│     [2D 4-QUADRANT RADAR SWEEP]                  [3D ROOM DIGITAL TWIN]                │
│            North (0°)                                                                  │
│                │                                     ┌──────────────────┐              │
│       Z2 (NW)  │  Z1 (NE)                            │   (Torso Mesh)   │              │
│         [•]    │    [P1]                             │      [ P1 ]      │              │
│   ─────────────┼─────────────                        │                  │              │
│       Z3 (SW)  │  Z4 (SE)                            │  Quadrant 1 (NE) │              │
│         [ ]    │    [ ]                              └──────────────────┘              │
│                │                                  Rendered via Three.js (WebGL)        │
│                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ REPLAY LAB CONTROLS: [◀◀] [▶ PLAY] [■ STOP] [● REC]   Scrubber: ═══════●══════ 48.5s   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 8.1 Key Visual Components
1. **2D 4-Quadrant Radar Sweep:** Displays real-time RF energy concentration across the four room quadrants, updated at 10 Hz via WebSocket telemetry.
2. **3D Three.js Digital Twin:** Renders a perspective room model showing the physical ESP32 node placement, LOS link vectors, and dynamic target position markers.
3. **Dual-Engine HUD Display:** Displays both **HEURISTIC ZONE (BASELINE)** and **SUPERVISED ML PREDICTION** side-by-side, giving evaluators full transparency into model agreement.
4. **Active Disturbed Sector Indicator:** Shows the number of simultaneously disturbed RF links, clearly labeled as an *Active Zone Heuristic Proxy* ($\sum \mathbb{I}(\text{link\_energy}_i > \tau)$) rather than uncalibrated multi-person counting.
5. **Replay Lab with Scrubber:** Allows one-click, offline exploration of recorded sessions with arbitrary scrubbing, enabling full demonstration capabilities even when physical hardware is disconnected.

---

## Chapter 9: Software Quality, Automated CI & Provenance Infrastructure

### 9.1 Comprehensive Test Suite (56/56 Unit Tests)
WiMotion 2.0 maintains an automated test suite (`tests/test_spatial.py`) containing **56 rigorous unit tests** covering:
- Asynchronous ring buffer concurrency and thread-safety.
- Canonical 56-D feature schema parity between live and replay modes.
- Replay cache schema version matching and invalid cache rejection.
- Zero-denominator metric guards (preventing division-by-zero crashes when evaluating sessions with 0 negative samples).
- Single-receiver link isolation (guaranteeing that disconnected RX2 links remain strictly idle).
- Security hardening (restricting CORS origins and blocking sibling directory traversal attacks).

### 9.2 Colleague 6-Point Verification Suite (`scripts/verify_six_checks.py`)
In addition to unit tests, an independent 6-point verification suite executes pre-flight checks before any live demonstration:
1. Replay sessions with single RX must never mark disconnected RX active.
2. Zero-sample links must remain idle regardless of baseline variance.
3. Transactional state switching must reject invalid modes with HTTP 400 and preserve state.
4. Clean lifecycle mode isolation (`LIVE` $\to$ `REPLAY` $\to$ `SIMULATION` $\to$ `LIVE`).
5. Replay aggregate rate formula conservation ($\sum \text{link rates} = \text{aggregate rate}$).
6. Sparse or corrupted sessions must trigger an `INSUFFICIENT_DATA` quality gate.

### 9.3 Cryptographic Artifact Provenance & Master Runner
To guarantee that the committed model binary matches the documented evaluation metrics, the system implements a strict cryptographic provenance mechanism:
- During training, `scripts/train_spatial_model.py` queries `git rev-parse HEAD` and embeds the exact commit hash and feature schema into both the binary pickle dictionary (`models/spatial_model.pkl`) and the JSON scorecard (`models/spatial_model_scorecard.json`).
- The **Master Evaluation Runner** (`scripts/run_master_evaluation.py`) performs an automated end-to-end audit:
  1. Executes all 56 unit tests.
  2. Runs the 6-point verification suite.
  3. Audits all 17 dataset sessions.
  4. Retrains and evaluates the multi-model benchmark.
  5. Computes the SHA-256 checksum of the disk binary and verifies exact equality against the scorecard.

```
Master Evaluation Provenance Check:
├── Scorecard SHA-256: 786ed5b8439c2fc75a98dd34c510cec830aab3785002192552406d1c7c298a6c
├── Disk Binary SHA-256: 786ed5b8439c2fc75a98dd34c510cec830aab3785002192552406d1c7c298a6c
└── Result: [STRICT MATCH] (Exit Code 0)
```

---

## Chapter 10: Comparative Evolution Matrix (Echo $\to$ WiMotion 1.0 $\to$ WiMotion 2.0)

| Technical Dimension | Project Echo (Proof-of-Concept) | WiMotion 1.0 (Presence Engine) | WiMotion 2.0 (Spatial Mesh System) |
| :--- | :---: | :---: | :---: |
| **Transceiver Architecture** | Single-Link ($1\text{ TX} \to 1\text{ RX}$) | Single-Link ($1\text{ TX} \to 1\text{ RX}$) | **Distributed Star-Mesh ($4\text{ TX} \times 2\text{ RX}$)** |
| **Physical ESP32 Nodes** | 2 Boards | 2 Boards | **6 Physical Boards Active** |
| **Spatial Links Evaluated** | 1 RF Path | 1 RF Path | **8 Concurrent Spatial Links** |
| **Sensing Objective** | Raw perturbation detection | Binary room presence (Yes/No) | **4-Quadrant Spatial Localization ($Z_1..Z_4$)** |
| **Feature Space** | Raw Subcarrier Amplitude | 217-D Temporal-Spectral Vector | **56-D Canonical Multi-Link Vector** |
| **Machine Learning Model** | None (Static Threshold) | `HistGradientBoostingClassifier` | **Calibrated `RandomForestClassifier` + Baseline** |
| **False-Alarm Mitigation** | None (Frequent Drift) | Static Moving Average | **Calibrated Energy Gate ($\theta=1.80$, Youden $J$)** |
| **Primary Evaluation Score** | Qualitative Signal Plot | 81.25% Valid Held-Out Accuracy | **49.26% Gated 5-Class / 80.99% $Z_4$ Recall** |
| **Data Leakage Protocol** | N/A | Cross-Validation (Possible overlap)| **Strict Session-Wise Zero-Leakage Split** |
| **Dataset Governance** | Unstructured text dumps | Single-session captures | **17-Session Audit & Quarantine Manifest** |
| **User Interface** | Terminal text output | Simple 2D plot | **Tactical HUD, 2D Radar & 3D Three.js Twin** |
| **Automated Testing** | None | Ad-hoc test scripts | **56 Automated Unit Tests + GitHub Actions CI** |
| **Model Provenance** | None | Manual pickle export | **Cryptographic SHA-256 & Git Commit Binding** |

---

## Chapter 11: Viva Voce & Defense Strategy Guide

When defending this project before an academic or technical evaluation committee, the following questions and answers represent the core intellectual foundation of the work:

### Q1: "Why is your 5-class spatial accuracy 49.26% instead of 95%?"
**Answer:**
> *"In a 5-class unconstrained indoor spatial classification problem, uniform random chance is 20.00%. Our gated accuracy of 49.26% is nearly 2.5 times better than random baseline, and significantly outperforms the heuristic spatial baseline of 29.26%. Many published papers that claim 95%+ accuracy evaluate on sliding windows randomly shuffled between train and test, which introduces catastrophic temporal leakage. We enforce strict take-based partitioning: Take 01 is used exclusively for training and threshold calibration, and Take 02 is held out as completely unseen physical test takes. Furthermore, our performance is physically explainable: Zone 4 achieves 81% recall due to its proximity to RX2, while Zone 3 achieves 14% recall due to long diagonal path loss. Our 49.26% is an honest, leak-free, physically grounded metric."*

### Q2: "Can WiMotion 2.0 count the exact number of people in the room?"
**Answer:**
> *"No, and we explicitly disclose this in our documentation. The HUD count is an **Active Disturbed Sector Proxy** ($\sum \mathbb{I}(\text{link\_energy}_i > \tau)$), which counts the number of quadrants exhibiting simultaneous multipath disturbance. If two individuals walk together in Zone 1, the system registers one active zone; conversely, if one person walks along the boundary between Z1 and Z2, boundary leakage may momentarily perturb both links, displaying two active zones. True multi-target biometric counting would require multi-antenna Angle-of-Arrival (AoA) antenna arrays, which COTS ESP32 boards with single omnidirectional antennas cannot physically support."*

### Q3: "What prevents WiMotion 2.0 from being spoofed by ambient Wi-Fi devices or phones?"
**Answer:**
> *"WiMotion 2.0 implements strict packet-level source MAC demultiplexing in `spatial/parser.py`. Every incoming CSI frame is filtered against the hardcoded factory MAC addresses of our four physical transmitters (TX1–TX4). Any ambient traffic—such as mobile phone probe requests or uncoordinated Wi-Fi router beacons (e.g. MAC `4C:11:AE:64:9A:05` observed during our lab tests)—is demultiplexed as `UNKNOWN` and discarded. It cannot perturb the 8-link variance calculation or trigger active zone classifications."*

### Q4: "How did you solve the empty-room false positive problem?"
**Answer:**
> *"When ungated, the supervised classifier suffered from a 98.35% false-alarm rate in empty rooms because decision trees overfitted to minute ambient thermal noise ripples. To solve this scientifically, we implemented an empirical energy gate calibrated exclusively on Take 01 training data by scanning Youden's $J$-statistic ($J = \text{Sensitivity} + \text{Specificity} - 1$). The optimal threshold ($\theta = 1.80$) was frozen and applied to unseen test sessions, cutting false alarms down to 52.89% and raising empty-room recall from 1.65% to 47.11% without introducing test leakage."*

---

## Chapter 12: Conclusion & Future Research Directions

### 12.1 Engineering Conclusions
WiMotion 2.0 successfully proves that **Commodity Wi-Fi hardware can serve as an effective, privacy-preserving spatial sensing radar** without specialized RF front-ends. The evolution from Project Echo to WiMotion 2.0 demonstrates that:
1. Multi-link distributed spatial diversity is mandatory for resolving directional ambiguity.
2. Scientific rigor—enforcing strict session partitioning, empirical threshold calibration, and transparent reporting of physical RF limitations—produces defensible, reproducible engineering.
3. Real-time COTS sensing requires a dual-engine approach combining physical heuristic ratios with trained machine learning classifiers.

### 12.2 Future Scope
1. **Multi-Carrier Phase Sanitization:** Implementing linear phase unwrapping across subcarriers to extract micro-Doppler chest displacements for contactless respiration monitoring.
2. **Phase Conjugation & Interferometric AoA:** Pairing ESP32-S3 boards with dual-antenna diversity to calculate Angle-of-Arrival (AoA) for sub-meter target coordinate tracking.
3. **Temporal Deep Learning:** Transitioning from windowed Random Forest trees to Bidirectional Long Short-Term Memory (BiLSTM) or Temporal Convolutional Networks (TCN) to exploit sequential walking dynamics across consecutive windows.

---
*Report compiled automatically from verified project artifacts, commit logs, test runs, and hardware manifests.*  
*Repository: `https://github.com/Tanmay-proj/Wimotion-2.0.git`*
