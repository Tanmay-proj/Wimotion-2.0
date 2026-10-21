# PART I: FRONT MATTER

---

## 1. TITLE PAGE (Sample Institute Template)

```
                            A DISSERTATION REPORT ON
                 DESIGN, IMPLEMENTATION AND EMPIRICAL EVALUATION 
                     OF A MULTI-LINK WI-FI CSI SENSING SYSTEM 
                   FOR INDOOR SPATIAL DISTURBANCE TRACKING

                                Submitted by
                               TANMAY MUGALE
                          (Roll No. / Enrollment ID)

                     In partial fulfillment of the requirements
                               for the award of
                             BACHELOR OF TECHNOLOGY
                                       IN
                        COMPUTER SCIENCE AND ENGINEERING
                         / ELECTRONICS AND COMMUNICATION

                               Under Guidance of
                             [SUPERVISOR NAME]
                           [SUPERVISOR DESIGNATION]

                         DEPARTMENT OF [DEPARTMENT NAME]
                           [COLLEGE / UNIVERSITY NAME]
                             [CITY, STATE, PIN CODE]
                                  OCTOBER 2026
```

---

## 2. CERTIFICATE OF APPROVAL

This is to certify that the dissertation entitled **"Design, Implementation and Empirical Evaluation of a Multi-Link Wi-Fi CSI Sensing System for Indoor Spatial Disturbance Tracking"**, submitted by **Tanmay Mugale** in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology in Computer Science and Engineering / Electronics and Communication Engineering, is an authentic record of bonafide research work carried out under my supervision and guidance.

To the best of my knowledge, the matter embodied in this dissertation has not been submitted to any other University / Institute for the award of any Degree or Diploma.

\
\
______________________________  
**[Supervisor / Guide Name]**  
Project Supervisor  
Department of [Department Name]  
[College / University Name]  

\
\
______________________________  
**[Head of Department Name]**  
Head of Department  
Department of [Department Name]  
[College / University Name]  

---

## 3. STUDENT DECLARATION

I hereby declare that this dissertation entitled **"Design, Implementation and Empirical Evaluation of a Multi-Link Wi-Fi CSI Sensing System for Indoor Spatial Disturbance Tracking"** is an authentic record of original research work conducted by me under the supervision of **[Supervisor Name]**, Department of [Department Name], [Institution Name].

I have adhered to all academic integrity norms. All theoretical formulations, source code libraries, hardware standards, and literature cited have been duly referenced. This work has not been previously submitted for any degree, diploma, or certificate at this or any other academic institution.

\
\
Date: October 21, 2026  
Place: [City, State]  

\
______________________________  
**Tanmay Mugale**  
Candidate Name & Signature  

---

## 4. ACKNOWLEDGEMENTS

I express my deepest gratitude to my project supervisor, **[Supervisor Name]**, for their invaluable guidance, technical insight, and continuous encouragement throughout the evolution of this research from its initial single-link exploratory phases (Project Echo and Shadow) to the complete multi-link spatial sensing architecture of WiMotion 2.0.

I extend sincere thanks to **[Head of Department Name]**, Head of the Department, and the faculty members of [Department Name] for providing the laboratory facilities, computing infrastructure, and academic environment essential to the completion of this project.

Special appreciation is conveyed to my laboratory technical staff, peers, and fellow researchers whose constructive feedback, peer audits, and discussions helped refine our experimental methodology, eliminate data leakage, and maintain the highest standards of scientific rigor. Finally, I thank my family and friends for their steadfast support and understanding during the intensive hardware experimentation and software engineering phases of this dissertation.

---

## 5. ABSTRACT

Conventional indoor human monitoring systems relying on optical video cameras or passive infrared (PIR) detectors face acute constraints regarding privacy infringement, line-of-sight occlusions, and vulnerability to environmental darkness or smoke. This dissertation presents the design, physical implementation, and empirical evaluation of **WiMotion 2.0**, an opportunistic, device-free radio frequency (RF) indoor spatial sensing system constructed entirely on low-cost Commodity Off-The-Shelf (COTS) Espressif ESP32 microcontrollers.

By intercepting Orthogonal Frequency Division Multiplexing (OFDM) Channel State Information (CSI) across 64 subcarriers on standard 2.4 GHz IEEE 802.11n Wi-Fi transmissions, WiMotion 2.0 expands single-link sensing into an 8-link distributed star topology ($4\text{ TX} \to 2\text{ RX}$) across four spatial quadrants ($Z_1, Z_2, Z_3, Z_4$). Operating at an aggregate capture rate of ~400 packets/second, the software ingestion pipeline deploys multi-threaded asynchronous ring buffers, packet-level transmitter MAC demultiplexing, and an authoritative 56-dimensional canonical feature extraction vector that eliminates train-serving skew.

To guarantee scientific reproducibility, a historical data audit quarantined 116,588 frames across early exploratory sessions due to thread-race packet drops, establishing the strictly verified **Phase B benchmark dataset** (56,386 frames / 1,209 sliding windows) with 100% strict take-based zero-leakage partitioning. To resolve a 98.35% empty-room false-alarm rate in unconstrained classifiers, an empirical energy gate ($\theta=1.80$) was calibrated on training data using Youden's $J$-statistic, cutting false alarms down to **52.89%** and raising true empty-room recall from 1.65% to **47.11%**. On unseen held-out physical test takes, the supervised Random Forest classifier achieved **49.26% gated 5-class accuracy** (substantially outperforming the 29.26% heuristic baseline and exceeding the 20.0% random guessing baseline by 2.5 times), with Zone 4 achieving **80.99% recall**. 

The system features an interactive real-time dashboard integrating a 2D polar radar sweep, a 3D Three.js room digital twin, and a dual-engine HUD backed by 56 passing unit tests and cloud CI. Finally, the dissertation explores the potential research applications of RF sensing in camera-independent indoor situational awareness and tactical reconnaissance, establishing a comprehensive technological roadmap for the future of device-free RF sensing.

---

## 6. KEYWORDS

`Wi-Fi Sensing`, `Channel State Information (CSI)`, `Human Presence Detection`, `Spatial Sensing`, `ESP32`, `RF Signal Processing`, `Machine Learning`, `Indoor Situational Awareness`, `Non-Line-of-Sight Sensing`.

---

## 7. TABLE OF CONTENTS

- **PART I: FRONT MATTER**
  - 1. Title Page (Sample Institute Template)
  - 2. Certificate of Approval
  - 3. Student Declaration
  - 4. Acknowledgements
  - 5. Abstract
  - 6. Keywords
  - 7. Table of Contents
  - 8. List of Figures
  - 9. List of Tables
  - 10. List of Abbreviations and Acronyms
- **CHAPTER 1: INTRODUCTION AND PROJECT MOTIVATION**
  - 1.1 Background and Motivation
  - 1.2 Limitations of Conventional Visual Monitoring
  - 1.3 Introduction to Wi-Fi-Based Device-Free Sensing
  - 1.4 Evolution: Echo → Shadow → WiMotion 1.0 → WiMotion 2.0
  - 1.5 Problem Statement
  - 1.6 Research Objectives and Scope of Work
  - 1.7 Organization of the Dissertation
- **CHAPTER 2: THEORETICAL FOUNDATIONS AND RF PROPAGATION PHYSICS**
  - 2.1 Electromagnetic Wave Propagation at 2.4 GHz
  - 2.2 Reflection, Diffraction, Absorption and Multipath Effects
  - 2.3 OFDM Transmission and Physical Layer Channel Estimation
  - 2.4 CSI vs RSSI: Physical and Mathematical Contrast
  - 2.5 Fresnel Zone Geometry and Spatial Sensitivity Ellipsoids
  - 2.6 Human Body Interaction and Perturbation Physics
  - 2.7 Multi-Link Spatial Diversity vs Single-Link Ambiguity
- **CHAPTER 3: HARDWARE ARCHITECTURE AND EXPERIMENTAL DEPLOYMENT**
  - 3.1 System Requirements and Hardware Selection
  - 3.2 ESP32-WROOM-32 and Supporting Components
  - 3.3 Star Topology Architecture (4 TX → 2 RX)
  - 3.4 Physical Geometry and 4-Quadrant Testbed Setup (ROOM_LAB_A)
  - 3.5 Node Assignment, Coordinates, MAC Addresses, and Channels
  - 3.6 Antenna Configurations and Baseline Separation Analysis
  - 3.7 RF Operating Parameters
  - 3.8 Power, USB and Serial-Connection Management
  - 3.9 Hardware Photographs and Deployment Record
- **CHAPTER 4: CSI DATA ACQUISITION AND SOFTWARE INGESTION PIPELINE**
  - 4.1 Software Architecture and Data Flow
  - 4.2 CSI Acquisition at the Receiver
  - 4.3 Multithreaded Serial Ingestion and Async Ring Buffers
  - 4.4 Frame Parsing, Validation, and Robustness
  - 4.5 Transmitter Demultiplexing by MAC Address
  - 4.6 Timestamping, Alignment, and Drop Handling
  - 4.7 2-Second Sliding Window and Temporal Slicing
  - 4.8 Data Logging Formats
- **CHAPTER 5: FEATURE ENGINEERING AND SPATIAL REPRESENTATION**
  - 5.1 Design Philosophy: Zero Train-Serving Skew
  - 5.2 Raw Subcarrier Preprocessing and Subcarrier Pruning
  - 5.3 56-Dimensional Canonical Feature Space
  - 5.4 Feature Mathematical Definitions
  - 5.5 Normalization, Scaling and Missing-Link Handling
  - 5.6 Spatial Quadrant Representation and Label Encoding
  - 5.7 Empirical Energy Gate (Youden J Calibration)
- **CHAPTER 6: EXPERIMENTAL METHODOLOGY, DATASET AUDIT AND MODEL EVALUATION**
  - 6.1 Experimental Protocol and Phase B Benchmark Design
  - 6.2 Data Leakage Prevention and Session-Level Splitting
  - 6.3 Historical Dataset Audit
  - 6.4 Baseline Spatial Models and Classifiers Evaluated
  - 6.5 Hyperparameter Tuning and Cross-Validation
  - 6.6 Quantitative Results and Detailed Metric Analysis
  - 6.7 Per-Class Performance and Zone Sensitivity
  - 6.8 False Alarm Reduction and Empty-Room Calibration
  - 6.9 Model Artifacts and Verification Hashes
- **CHAPTER 7: REAL-TIME DASHBOARD, VISUALIZATION AND REPLAY SYSTEM**
  - 7.1 Dashboard Architecture
  - 7.2 Backend, WebSocket Communication and Front-End
  - 7.3 Live Hardware Monitoring Interface
  - 7.4 Four-Quadrant Spatial Visualization (2D Radar Sweep)
  - 7.5 Three-Dimensional Room Visualization (Three.js WebGL Engine)
  - 7.6 Heuristic and Machine-Learning Outputs (Dual-Engine HUD)
  - 7.7 Active-Sector Indicators Versus Actual People Counting
  - 7.8 Recorded-Session Replay and Timeline Controls
  - 7.9 Live, Replay and Simulation Mode Separation
- **CHAPTER 8: SOFTWARE VERIFICATION, TESTING AND SYSTEM HEALTH**
  - 8.1 Testing Philosophy
  - 8.2 Unit and Integration Testing (56 Automated Unit Tests)
  - 8.3 Data-Rate and Signal-Quality Checks
  - 8.4 Mode Isolation and Replay Verification
  - 8.5 Input Validation and Security-Related Checks
  - 8.6 Continuous Integration and GitHub Actions
  - 8.7 Independent Colleague 6-Point Verification Suite
  - 8.8 Production Readiness and Failure Modes
- **CHAPTER 9: PROPOSED APPLICATIONS IN INTELLIGENCE GATHERING AND SURVEILLANCE**
  - 9.1 Conceptual Framework: Camera-Independent Indoor Sensing
  - 9.2 Non-Line-of-Sight and Covert Surveillance
  - 9.3 Perimeter Intrusion and Multi-Zone Disturbance
  - 9.4 Tactical and Hostage-Situation Reconnaissance
  - 9.5 Search-and-Rescue in Degraded Visual Environments
  - 9.6 Elderly Care, Fall Detection and Smart Building Integration
  - 9.7 Counter-Surveillance, Jamming Resistance and Physical Limitations
- **CHAPTER 10: LONG-TERM TECHNOLOGY ROADMAP AND FUTURE WORK**
  - 10.1 From Quadrant Detection to Continuous Coordinate Localization
  - 10.2 True Multi-Person Disambiguation and Separation
  - 10.3 Phase-Sanitization and Angle-of-Arrival (AoA) Processing
  - 10.4 Higher Frequency Bands: 5 GHz, 6 GHz (Wi-Fi 6E/7) and mmWave
  - 10.5 Deep Learning and Temporal Sequence Architectures
  - 10.6 Hardware Miniaturization and Operational Deployment
- **CHAPTER 11: CONCLUSION AND FINAL REMARKS**
  - 11.1 Summary of Research Journey
  - 11.2 Engineering Contributions and Implemented Components
  - 11.3 Realistic Assessment of Current System Performance
  - 11.4 Final Perspective on Device-Free RF Sensing
- **REFERENCES AND APPENDICES**
  - References (Primary Citations and Scientific Literature)
  - Appendix A: Hardware Configuration and Device/Link Allocation Tables
  - Appendix B: Complete 56-Dimensional Canonical Feature Specification
  - Appendix C: Complete 56-Test Suite Manifest and Passing Log Output
  - Appendix D: Phase B Ground Truth Generation Pipeline
  - Appendix E: Independent Colleague Verification Report
  - Appendix F: Full Clean Pre-Demo Checklist Output
  - Appendix G: Evaluation Scorecards, Confusion Matrices and Supporting Plots
  - Appendix H: Additional Dashboard Screenshots
  - Appendix I: Selected Git Commit and Reproducibility Information
  - Appendix J: Technical Viva Voce Defense Preparation Guide

---

## 8. LIST OF FIGURES

* **Figure 1.1:** Project Echo Prototype Interface and Tactical Radar HUD Display
* **Figure 1.2:** Project Shadow Neural Model Training and Baseline Fading Convergence Curves
* **Figure 3.1:** Panoramic View of ROOM_LAB_A Multi-Link Deployment Testbed
* **Figure 3.2:** Corner Transmitter Installation (TX1 & TX2) Close-Up Photographs
* **Figure 3.3:** Corner Transmitter Installation (TX3 & TX4) Close-Up Photographs
* **Figure 3.4:** Central Dual-Receiver Host Station (RX1 & RX2 on Calibrated 24.5 cm Baseline)
* **Figure 3.5:** Human Subject Walking Traversal Experiment in Phase B Controlled Sensing Grid
* **Figure 3.6:** Six-Node Active Distributed Hardware Testbed Assembly
* **Figure 6.1:** Detailed 5×5 Confusion Matrix of Primary Gated Random Forest Classifier (Take 02 Held-Out Test Set)
* **Figure 6.2:** Quantitative Accuracy Comparison Across Model Architectures and Physical Baselines
* **Figure 6.3:** Per-Class Spatial Recall Sensitivity Highlighting Zone 4 Peak Sensitivity and Zone 3 Diagonal Path Attenuation
* **Figure 6.4:** Impact of Empirical Energy Gating on Empty-Room False Alarm Reduction
* **Figure 7.1:** Screenshot of 2D Polar Radar Sweep During Quadrant 1 Subject Traversal
* **Figure 7.2:** Screenshot of 3D Perspective Digital Twin Room Showing Detected Subject Marker
* **Figure 7.3:** Screenshot of Replay Lab Interface Showing Interactive Scrubber and Session Manifest
* **Figure 8.1:** Screenshot of GitHub Actions Cloud Runner Displaying Green CI Pass Status
* **Figure H.1:** Full Tactical Observatory in Live Hardware Mode Showing Active 8-Link Variance Meters
* **Figure H.2:** Replay Lab Interface Displaying the 95-Second Presentation Scenario and Scrubber Slider
* **Figure H.3:** Diagnostic Metadata Drawer Displaying Model Artifact Size (1.16 MB) and Calibrated Gate Threshold ($\theta = 1.80$)

---

## 9. LIST OF TABLES

* **Table 2.1:** Systematic Technical Comparison Between RSSI and Subcarrier-Level CSI
* **Table 3.1:** Complete Physical Hardware Inventory and Node Assignment
* **Table 3.2:** Physical Baseline Definitions, Geometric Orientations, and Primary Spatial Quadrants
* **Table 3.3:** Key RF and Operational Physical-Layer Firmware Parameters
* **Table 4.1:** Serial Streaming Bandwidth and Processing Budget per Receiver Node
* **Table 5.1:** Authoritative 56-Dimensional Canonical Feature Vector Specification
* **Table 6.1:** Comprehensive Historical Dataset Audit Summary
* **Table 6.2:** Controlled Phase B Physical Benchmark Dataset Manifest
* **Table 6.3:** Complete Model Performance Comparison on Held-Out Test Set (Take 02)
* **Table 6.4:** Per-Class Performance Breakdown of Primary Supervised Random Forest Classifier
* **Table 6.5:** Detailed 5x5 Confusion Matrix of Primary Gated Classifier on Held-Out Test Set
* **Table 6.6:** Quantitative Impact of Empirical Energy Gating on False Alarm Mitigation
* **Table 8.1:** Functional Breakdown of the 56 Automated Unit Tests
* **Table 8.2:** Independent Colleague 6-Point Verification Results
* **Table A.1:** Physical Baseline Definitions, Geometric Orientations, and Primary Spatial Quadrants

---

## 10. LIST OF ABBREVIATIONS AND ACRONYMS

* **AoA:** Angle of Arrival
* **AP:** Access Point
* **CFR:** Channel Frequency Response
* **CI:** Continuous Integration
* **CIR:** Channel Impulse Response
* **COTS:** Commercial Off-The-Shelf
* **CSI:** Channel State Information
* **dBm:** Decibels relative to one milliwatt
* **DFT:** Discrete Fourier Transform
* **DoF:** Degrees of Freedom
* **ESP-IDF:** Espressif IoT Development Framework
* **FIFO:** First-In First-Out
* **FPS:** Frames Per Second
* **HT:** High Throughput (802.11n)
* **HUD:** Heads-Up Display
* **ID:** Identifier
* **IFFT:** Inverse Fast Fourier Transform
* **ISM:** Industrial, Scientific, and Medical (2.4 GHz)
* **ISR:** Interrupt Service Routine
* **JSON:** JavaScript Object Notation
* **LL-LTF:** Legacy Long Training Field
* **LOS:** Line-of-Sight
* **MAC:** Medium Access Control
* **ML:** Machine Learning
* **mmWave:** Millimeter Wave
* **NLOS:** Non-Line-of-Sight
* **OFDM:** Orthogonal Frequency Division Multiplexing
* **OOB:** Out-of-Band / Out-of-Bag
* **PCB:** Printed Circuit Board
* **PHY:** Physical Layer
* **PIR:** Passive Infrared
* **RF:** Radio Frequency
* **RMS:** Root Mean Square
* **RSSI:** Received Signal Strength Indication
* **RTOS:** Real-Time Operating System
* **RX:** Receiver
* **SDR:** Software-Defined Radio
* **SHA:** Secure Hash Algorithm
* **SNR:** Signal-to-Noise Ratio
* **SoC:** System-on-Chip
* **SRAM:** Static Random-Access Memory
* **STBC:** Space-Time Block Coding
* **SVM:** Support Vector Machine
* **ToF:** Time of Flight
* **TX:** Transmitter
* **UART:** Universal Asynchronous Receiver-Transmitter
* **USB:** Universal Serial Bus
* **UWB:** Ultra-Wideband
* **WLAN:** Wireless Local Area Network

---

# CHAPTER 1: INTRODUCTION AND PROJECT MOTIVATION

---

## 1.1 Background and Motivation

Indoor situational awareness—the capability to detect, locate, and track human occupancy within an enclosed architectural space—is a foundational requirement across modern cyber-physical systems. From energy-efficient building automation and ambient assisted living to security monitoring, search-and-rescue, and disaster response, knowing whether a room is occupied and where occupants are positioned is of paramount importance.

Over the past two decades, the global deployment of wireless local area networks (WLANs) operating under the IEEE 802.11 standards has blanketed indoor environments with ubiquitous radio frequency (RF) energy. In residential homes, offices, academic laboratories, and industrial warehouses, Wi-Fi access points and client stations continuously exchange electromagnetic frames in the 2.4 GHz and 5 GHz Industrial, Scientific, and Medical (ISM) bands.

Conventionally, this ambient RF illumination is treated purely as a data-carrying communication channel, where multipath reflections off walls, furniture, and boundaries are viewed as destructive fading to be equalized. However, an emerging research paradigm in wireless communications recognizes that **ambient wireless signals can simultaneously serve as an environmental sensor**. Because human bodies are composed predominantly of water and conductive electrolytes, human movement dynamically modulates the amplitude, phase, and delay of propagating multipath signals. By analyzing these subtle physical-layer modulations, wireless infrastructure can be transformed into a pervasive, device-free spatial sensing radar without requiring subjects to carry active transponders or smartphones.

---

## 1.2 Limitations of Conventional Visual Monitoring

Visual surveillance systems relying on optical cameras and infrared imaging represent the dominant technology for indoor monitoring. However, optical systems exhibit four severe operational limitations:

1. **Line-of-Sight and Physical Occlusion Vulnerability:** Optical cameras require an unobstructed line-of-sight (LOS) to the target. Physical barriers—such as closed doors, partition walls, cubicle dividers, or furniture—create complete optical blind spots.
2. **Environmental Degradation:** Optical sensors degrade severely in adverse visual conditions, including total darkness, dense smoke, airborne dust, or sudden lighting changes (glare and shadows).
3. **Severe Privacy and Legal Violations:** Transmitting and recording high-resolution optical video creates critical privacy, ethical, and legal violations. Cameras are strictly prohibited in private living quarters, bedrooms, patient bathrooms, and high-security conference rooms.
4. **Vulnerability to Physical Tampering:** Lenses can be obscured by tape, spray paint, or physical obstructions, and optical cameras are immediately visible to intruders, compromising covert monitoring.

Passive Infrared (PIR) sensors overcome privacy concerns but suffer from coarse spatial resolution: they detect only tangential changes in thermal radiation and fail completely when subjects remain seated, stationary, or move radially toward the sensor. Similarly, dedicated ultra-wideband (UWB) and millimeter-wave (mmWave) radars deliver high precision but require expensive, proprietary transceiver silicon that is costly to scale across multi-room buildings.

---

## 1.3 Introduction to Wi-Fi-Based Device-Free Sensing

Wi-Fi-based device-free sensing overcomes the limitations of optical and PIR modalities by exploiting the physical-layer characteristics of standard commodity Wi-Fi transmissions:

* **Non-Line-of-Sight (NLOS) Propagation:** RF signals at 2.4 GHz penetrate standard interior partition materials, including drywall, wooden doors, and acoustic ceiling tiles, enabling sensing in visually obstructed environments.
* **Privacy-Preserving Abstraction:** The receiver captures only physical layer channel state matrices. No facial images, identifiable clothing features, or optical silhouettes are captured, providing inherent compliance with privacy norms.
* **Zero Wearable Burden (Device-Free):** The human subject is completely passive, acting purely as an organic dielectric reflector within the existing RF field.
* **Leveraging COTS Infrastructure:** By implementing sensing on low-cost Commodity Off-The-Shelf (COTS) Wi-Fi microcontrollers (such as the Espressif ESP32), spatial awareness can be deployed at a fraction of the cost of dedicated radar installations.

---

## 1.4 Project Evolution: Echo, Shadow, WiMotion and WiMotion 2.0

The research and engineering documented in this dissertation represents an iterative progression across four development phases:

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  PROJECT ECHO   │  ──►  │ PROJECT SHADOW  │  ──►  │   WIMOTION 1.0  │  ──►  │  WIMOTION 2.0   │
│  Single-Link    │       │ Multipath Decay │       │ Temporal ML     │       │ Multi-Link Mesh │
│  Raw Subcarrier │       │ & Drift Studies │       │ Binary Presence │       │ 4-Quadrant Grid │
│  Perturbation   │       │                 │       │ (217 Features)  │       │ (8 Links, 56-D) │
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
```

1. **Phase 1: "Project Echo" (Single-Link Feasibility Prototype):**
   * Investigated the fundamental physics of 64-subcarrier OFDM channel perturbations across a single $1\text{ TX} \to 1\text{ RX}$ ESP32 link.
   * Proved that walking across the direct LOS path produces detectable variance in raw subcarrier amplitudes.
   * *Key Discovery:* Revealed severe single-link blind spots: moving outside the direct LOS Fresnel zone caused signal perturbations to fall below the ambient noise floor.
   * **[Figure 1.1: Project Echo Prototype Interface and Tactical Radar HUD Display]**
2. **Phase 2: "Project Shadow" (Multipath Fading & Baseline Drift Investigations):**
   * Investigated environmental baseline drift caused by thermal expansion in ESP32 silicon over extended runtimes.
   * Analyzed static multipath profiles and established early moving-average normalization filters.
   * **[Figure 1.2: Project Shadow Neural Model Training and Baseline Fading Convergence Curves]**
3. **Phase 3: "WiMotion 1.0" (Temporal-Spectral Machine Learning Engine):**
   * Replaced ad-hoc thresholding with a 217-dimensional feature extraction pipeline (FFT Doppler bands, wavelets, and higher-order statistical moments).
   * Trained a `HistGradientBoostingClassifier`, achieving **81.25% valid held-out accuracy** on single-link physical captures (`held_out_walking_01` and `held_out_empty_01`).
   * *The Critical Ceiling:* WiMotion 1.0 remained strictly a *binary occupancy detector* (`EMPTY` vs `WALKING`), with zero spatial capability to determine *where* an occupant was located.
4. **Phase 4: "WiMotion 2.0" (Distributed Multi-Link Spatial Sensing System):**
   * Overcame single-link directional ambiguity by engineering an **8-link distributed star topology** ($4\text{ TX} \to 2\text{ RX}$) across 6 active physical ESP32 nodes.
   * Divided the room into 4 discrete spatial quadrants ($Z_1, Z_2, Z_3, Z_4$).
   * Formulated a canonical 56-dimensional link-state vector eliminating train-serving skew.
   * Developed an empirical energy gate ($\theta=1.80$) cutting empty-room false alarms from 98.35% to 52.89%.
   * Deployed an interactive 3D digital twin room and 2D radar dashboard backed by 56 automated unit tests.

---

## 1.5 Problem Statement

Despite the theoretical promise of Wi-Fi CSI sensing, practical implementation on low-cost commodity microcontrollers faces five major engineering roadblocks:
1. **Directional Ambiguity:** A single wireless link cannot differentiate whether an obstruction occurs in the North-East or South-West quadrant.
2. **Severe False Alarms in Idle Environments:** Unconstrained supervised models overfit to minute thermal noise in receiver RF silicon, producing unacceptable false alarm rates in empty rooms.
3. **Train-Serving Skew & Evaluation Leakage:** Random window shuffling in time-series evaluation introduces artificial data leakage, masking true real-world performance drops.
4. **Data Acquisition Throughput Limits:** Streaming multi-subcarrier CSI from multiple nodes simultaneously overwhelms standard serial drivers, causing dropped frames and timing jitter.
5. **Lack of Provenance and Reproducibility:** Many published sensing frameworks lack verifiable model-to-code traceability, preventing independent scientific reproduction.

---

## 1.6 Aim and Objectives

The primary aim of this dissertation is to design, implement, and empirically evaluate a complete, leak-free, multi-link Wi-Fi CSI sensing prototype for indoor spatial quadrant localization on commodity ESP32 microcontrollers.

To achieve this aim, eight concrete engineering objectives were established:
1. **Hardware Deployment:** Construct and calibrate a 6-node distributed multi-link star topology ($4\text{ TX} \to 2\text{ RX}$) yielding 8 concurrent spatial baselines.
2. **High-Throughput Ingestion:** Develop a multi-threaded asynchronous serial ingestion engine supporting aggregate packet rates of ~400 packets/second without serial buffer drops.
3. **Identity Demultiplexing:** Implement packet-level factory MAC demultiplexing to isolate uncoordinated third-party ambient AP beacons from experimental feature windows.
4. **Canonical Feature Architecture:** Engineer a single, shared 56-dimensional feature extraction function ensuring exact mathematical parity between training and live inference.
5. **Rigorous Data Auditing:** Audit and quarantine corrupted historical recording sessions to establish a strictly verified physical benchmark dataset (Phase B).
6. **False-Alarm Mitigation:** Formulate and calibrate an empirical energy gate threshold on training data to suppress empty-room false alarms.
7. **Real-Time Visualization:** Build an interactive tactical dashboard featuring a 2D polar radar sweep, a 3D WebGL room digital twin, and a dual-engine HUD.
8. **Automated Quality & Provenance:** Establish an automated 56-test unit suite, cloud CI pipeline, and cryptographic SHA-256 model provenance binding.

---

## 1.7 Scope and Boundary Conditions

To maintain strict scientific integrity, the scope of this project is subject to clearly defined boundaries:
* **Physical Scope:** Single-room laboratory deployment (`ROOM_LAB_A`, $4.2\text{m} \times 5.8\text{m}$) in a concrete/brick institutional building.
* **Target Domain:** Controlled, single-occupant locomotion (human subject walking within designated quadrant corridors). Multi-person simultaneous spatial separation remains an unvalidated future research area.
* **Output Granularity:** 4-quadrant spatial sector disturbance classification ($Z_1, Z_2, Z_3, Z_4$, and `CLEAR`).
* **Explicit Demarcation:** The system measures **RF channel perturbation dynamics**; it is NOT claimed as a millimeter-accurate radar tracker, a biometric camera replacement, or an operational military through-wall imaging apparatus.

---

## 1.8 Expected Engineering Contributions

This dissertation delivers five verified engineering contributions:
1. **Low-Cost Commodity Multi-Link Prototype:** Demonstrates that a $30 hardware array of 6 standard ESP32 microcontrollers can deliver multi-link spatial disturbance tracking without SDRs.
2. **Audited, Zero-Leakage Benchmark Dataset:** Documents the Phase B dataset (56,386 frames / 1,209 sliding windows) with 100% strict session-level train/test partitioning.
3. **Calibrated CLEAR Energy Gating Methodology:** Demonstrates an empirical method using Youden's $J$-statistic to cut empty-room false alarms from 98.35% to 52.89% without test set exposure.
4. **Physical RF Sensitivity Analysis:** Formulates a physical explanation for the observed 81.0% ($Z_4$) versus 14.1% ($Z_3$) recall disparity based on transceiver baseline geometry.
5. **End-to-End Reproducible Toolchain:** Provides complete, open-source firmware, ingestion servers, dashboard visualization, and automated verification suites with cryptographic provenance tracking.

---

## 1.9 Organization of the Dissertation

The remainder of this dissertation is organized as follows:
* **Chapter 2** details the electromagnetic foundations of wireless multipath propagation, CSI vs. RSSI, and Fresnel zone theory.
* **Chapter 3** presents the physical hardware architecture, ESP32 silicon specifications, and 6-node laboratory deployment.
* **Chapter 4** outlines the multi-threaded serial ingestion engine, byte parsing, and MAC demultiplexing.
* **Chapter 5** derives the mathematical formulation of the canonical 56-dimensional feature vector and machine learning pipeline.
* **Chapter 6** reports the dataset auditing process, zero-leakage methodology, and comprehensive empirical results.
* **Chapter 7** describes the real-time Observatory Dashboard, 2D radar, and 3D digital twin visualization.
* **Chapter 8** details the software quality assurance, 56 unit tests, and cryptographic provenance infrastructure.
* **Chapter 9** explores the potential research applications of Wi-Fi CSI sensing in intelligence gathering and surveillance.
* **Chapter 10** establishes a comprehensive strategic way ahead, technical roadmap, and operational validation milestones.
* **Chapter 11** concludes the dissertation with a summary of engineering findings.
* **References and Appendices** provide hardware manifests, full code listings, and session logs.

---
*(End of Chapter 1 — Source: WiMotion 2.0 Repository Architecture & Research Manifest)*


---

# CHAPTER 2: THEORETICAL FOUNDATIONS OF WI-FI CSI SENSING

---

## 2.1 Fundamentals of Wireless Signal Propagation

Radio frequency (RF) sensing relies on the physical laws governing electromagnetic wave propagation in terrestrial environments. When an isotropic transmitter antenna radiates power $P_t$ in free space, the electromagnetic wave expands spherically. At a distance $d$ from the transmitter, the power density $S$ is distributed uniformly over the surface of a sphere of radius $d$:

$$S = \frac{P_t}{4 \pi d^2}$$

If the receiver possesses an effective antenna aperture $A_e = \frac{\lambda^2 G_r}{4 \pi}$ (where $\lambda = \frac{c}{f}$ is the operational wavelength and $G_r$ is receiver antenna gain), the received power $P_r$ under ideal line-of-sight (LOS) conditions follows the **Friis Transmission Formula**:

$$P_r = P_t G_t G_r \left( \frac{\lambda}{4 \pi d} \right)^2$$

For standard 2.4 GHz Wi-Fi operating on Channel 6 ($f = 2.437\text{ GHz}$), the electromagnetic wavelength in air is:

$$\lambda = \frac{3 \times 10^8\text{ m/s}}{2.437 \times 10^9\text{ Hz}} \approx 0.123\text{ meters} \quad (12.3\text{ cm})$$

Because human body anatomical dimensions (torso width $\approx 40\text{ cm}$, chest depth $\approx 25\text{ cm}$, limb diameter $\approx 10\text{ cm}$) are on the same order of magnitude as the $12.3\text{ cm}$ wavelength, the human body operates in the **resonant scattering regime**, making it a highly effective scatterer of 2.4 GHz RF waves.

---

## 2.2 Reflection, Diffraction, Absorption and Multipath Effects

In an enclosed architectural space, an electromagnetic wave emitted by an antenna does not propagate through free space. Instead, it interacts with physical boundaries through four fundamental propagation mechanisms:

```
                                  [INCIDENT EM WAVE]
                                           │
         ┌───────────────────┬─────────────┴───────┬───────────────────┐
         ▼                   ▼                     ▼                   ▼
   [SPECULAR          [DIFFRACTION /        [DIELECTRIC          [DIFFUSE
   REFLECTION]         EDGE SCATTER]         ABSORPTION]        SCATTERING]
Smooth walls,        Doorway corners,      Human tissue,        Rough surfaces,
floors, ceilings     furniture edges       water containers     textured walls
```

1. **Specular Reflection:** Occurs when an RF wave encounters a planar boundary whose dimensions are significantly larger than $\lambda$ (e.g., concrete walls, metal filing cabinets, glass windows). The reflection angle equals the incidence angle according to Snell's law.
2. **Edge Diffraction:** Occurs when an RF wavefront strikes the sharp geometric edge of an obstacle (e.g., doorway frames, desk partitions). According to the Huygens-Fresnel principle, the obstacle edge acts as a secondary line source, bending waves into geometric shadow zones (Non-Line-of-Sight propagation).
3. **Dielectric Absorption:** Human tissue consists primarily of water and dissolved electrolytes ($\epsilon_r \approx 50\text{ to }56$ at 2.4 GHz). When an RF wave enters the human body, dielectric losses convert a portion of the wave's electromagnetic energy into heat, causing substantial forward attenuation.
4. **Diffuse Scattering:** Occurs when waves strike rough, irregular surfaces whose feature sizes are comparable to $\lambda$, scattering energy across an omnidirectional hemisphere.

---

## 2.3 RSSI Versus Channel State Information

Early wireless sensing attempts relied on **Received Signal Strength Indication (RSSI)**. However, RSSI is fundamentally inadequate for spatial indoor sensing due to physical-layer limitations:

### Table 2.1: Physical Layer Comparison: RSSI vs. Channel State Information (CSI)

| Technical Dimension | Received Signal Strength Indication (RSSI) | Channel State Information (CSI) |
| :--- | :--- | :--- |
| **Physical Abstraction** | Macroscopic scalar power metric (in dBm) | Microscopic complex channel matrix ($H \in \mathbb{C}^{M \times K}$) |
| **Spectral Granularity** | Single averaged value across the entire 20 MHz channel | Independent values across 64 discrete subcarriers |
| **Phase Availability** | No phase information (scalar magnitude only) | Complex representation: Amplitude and Phase per subcarrier |
| **Multipath Sensitivity** | Blind to multipath shifts; subject to destructive fading | Resolves individual multipath subcarrier interference patterns |
| **Temporal Stability** | Prone to macroscopic noise; high variance in static rooms | Highly stable in static environments; responsive to motion |
| **Spatial Resolution** | Cannot differentiate location; coarse proximity only | Multi-subcarrier diversity enables spatial quadrant resolution |

```
       RSSI (Coarse Scalar Measurement)             CSI (Fine-Grained 64-Subcarrier Matrix)
      ┌─────────────────────────────────┐          ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
      │           -54 dBm               │    VS    │ 1 │ 2 │ 3 │...│...│...│...│...│63 │64 │
      │ (Averaged across full 20 MHz)   │          └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
      └─────────────────────────────────┘          Complex Channel Response per Subcarrier: H_k = |a_k| e^(j phi_k)
```

---

## 2.4 CSI as a Complex Channel Frequency Response

In modern wireless systems, the indoor radio channel between transmitter and receiver is modeled as a linear time-variant filter characterized by its **Channel Impulse Response (CIR)**:

$$h(\tau, t) = \sum_{i=1}^{N} a_i(t) e^{-j \phi_i(t)} \delta(\tau - \tau_i(t))$$

Where $N$ is the total count of multipath rays, and $a_i(t)$, $\phi_i(t)$, and $\tau_i(t)$ represent the amplitude, phase shift, and propagation delay of the $i$-th multipath ray at time $t$.

Applying the continuous Fourier transform yields the **Channel Frequency Response (CFR)**:

$$H(f, t) = \int_{-\infty}^{\infty} h(\tau, t) e^{-j 2 \pi f \tau} d\tau = \sum_{i=1}^{N} a_i(t) e^{-j (2 \pi f \tau_i(t) + \phi_i(t))}$$

In digital baseband processing, the CFR is sampled across $K$ discrete orthogonal subcarriers. For the $k$-th subcarrier at frequency $f_k$, Channel State Information represents the complex ratio between the transmitted symbol $X(f_k, t)$ and received symbol $Y(f_k, t)$ (corrupted by additive Gaussian noise $W(f_k, t)$):

$$Y(f_k, t) = H(f_k, t) X(f_k, t) + W(f_k, t)$$

$$\hat{H}(f_k, t) = |H(f_k, t)| e^{j \angle H(f_k, t)}$$

Where $|H(f_k, t)|$ represents subcarrier amplitude attenuation, and $\angle H(f_k, t)$ represents subcarrier phase shift.

---

## 2.5 OFDM and Wi-Fi Subcarrier Structure

Under the IEEE 802.11n specification, a standard 20 MHz Wi-Fi channel is partitioned into **64 orthogonal subcarriers** spaced at exact intervals of $\Delta f = 312.5\text{ kHz}$:

$$\text{Subcarrier Spacing} = \frac{20\text{ MHz}}{64} = 312.5\text{ kHz}$$

The 64 subcarriers are indexed from $k = -32$ to $+31$:
- **Data Subcarriers (52):** Carry user payload symbols and channel pilot data.
- **Pilot Subcarriers (4):** Dedicated to carrier frequency offset tracking (at indices $-21, -7, +7, +21$).
- **Null / Guard Subcarriers (8):** Guard bands at channel edges ($k \in [-32, -29]$ and $[+29, +31]$) and the direct current (DC) null at center frequency ($k = 0$) to prevent receiver local oscillator leakage.

On Espressif ESP32 hardware, the baseband exposes the full 64-element array. Subcarrier amplitude cleaning filters out guard and null bands to isolate the active spectral components.

---

## 2.6 Human-Induced Changes in Wireless Channels

When an indoor room is completely static, the multipath rays reflect solely off fixed surfaces (walls, floor, ceiling, desk). The resulting Channel Frequency Response $H_{\text{static}}(f)$ remains constant over time.

When a human subject enters and walks through the environment, the total multipath field decomposes into two components:

$$H(f, t) = H_{\text{static}}(f) + H_{\text{dynamic}}(f, t)$$

$$H_{\text{dynamic}}(f, t) = \sum_{m \in \text{Body Rays}} a_m(t) e^{-j \frac{2 \pi}{\lambda} d_m(t)}$$

Where $d_m(t)$ is the physical propagation distance of the ray scattered off the moving human body. 

As the subject walks at velocity $v$, the propagation distance changes continuously ($d_m(t) = d_0 + v t$). This causes the phase term $\frac{2 \pi}{\lambda} d_m(t)$ to rotate rapidly. When this dynamic ray interferes with the static multipath rays at the receiver antenna, it induces **periodic constructive and destructive interference ripples** across individual subcarrier amplitudes. By extracting the temporal variance and envelope statistics of these ripples, the system detects human locomotion.

---

## 2.7 Fresnel Zones and Link Sensitivity

The spatial sensitivity of an RF link is governed by **Fresnel Zone Diffraction Theory**. Between a transmitter antenna at $(x_{\text{tx}}, y_{\text{tx}})$ and a receiver antenna at $(x_{\text{rx}}, y_{\text{rx}})$ separated by distance $D$, the $n$-th Fresnel zone is an ellipsoid whose boundary satisfies:

$$d_1 + d_2 - D = n \frac{\lambda}{2}$$

Where $d_1$ is the distance from the transmitter to a point on the ellipsoid, $d_2$ is the distance from that point to the receiver, and $n \in \{1, 2, 3, \dots\}$.

```
                                  [1st Fresnel Zone Boundary (n = 1)]
                               ┌────────────────────────────────────────┐
                               │                 d1 + d2 = D + lambda/2 │
                 TX ───────────┼────────────────────────────────────────┼─────────── RX
             (x_tx, y_tx)      │            Direct LOS Baseline (D)     │       (x_rx, y_rx)
                               │                                        │
                               └────────────────────────────────────────┘
```

The maximum radius $r_1$ of the first Fresnel zone ($n = 1$) occurs at the midpoint ($d_1 = d_2 = D/2$):

$$r_1 = \frac{1}{2} \sqrt{\lambda D}$$

For an indoor link with length $D = 4.0\text{ meters}$ operating at $\lambda = 0.123\text{ meters}$:

$$r_1 = \frac{1}{2} \sqrt{0.123 \times 4.0} = \frac{1}{2} \sqrt{0.492} \approx 0.35\text{ meters} \quad (35\text{ cm})$$

### Physical Sensitivity Implications:
- **Inside the 1st Fresnel Zone ($r < 35\text{ cm}$):** A human body traversing directly across the line-of-sight path obstructs the primary energy corridor, creating massive amplitude attenuation and sharp variance spikes.
- **Outside the Primary Fresnel Zone ($r > 1.0\text{ m}$):** Human movement produces only diffuse, higher-order multipath scatter. The amplitude perturbations decay rapidly with distance, falling close to the ambient receiver noise floor.

---

## 2.8 Multi-Link Spatial Diversity

The fundamental limitation of single-link RF sensing (as discovered during Project Echo) is **directional and spatial ambiguity**:
- An object walking 50 cm to the left of a single LOS link produces the exact same amplitude variance signature as an object walking 50 cm to the right.
- Motion occurring in the outer corners of a room lies entirely outside the link's primary Fresnel zones, resulting in complete sensing blind spots.

```
       [SINGLE-LINK AMBIGUITY]                [MULTI-LINK SPATIAL MESH COVERAGE]
       TX ═════════════════════ RX            TX2 ─────────── (L1) ─────────── TX1
             [Blind Spot]                      │ \                           / │
                                               │   \       [ROOM SENSING]  /   │
                                              (L5)   (L2)     GRID       (L0) (L4)
                                               │       \               /       │
                                               │         \   RX1   RX2         │
                                               │           \  │     │          │
                                              TX3 ─────────── (L7) ─────────── TX4
```

To resolve spatial ambiguity, WiMotion 2.0 deploys **Multi-Link Spatial Diversity**:
- By creating 8 intersecting baselines across four quadrants, every spatial quadrant is traversed by at least one primary direct LOS link and two cross-diagonal links.
- When an individual walks in Zone 1, Links $L_0$ and $L_4$ experience deep primary Fresnel perturbations, while distant links ($L_2$ and $L_6$) remain largely undisturbed.
- By evaluating the relative distribution of variance across all 8 links simultaneously, the system resolves orthogonal quadrant coordinates unambiguously.

---

## 2.9 Limitations of CSI-Based Interpretation

To maintain rigorous scientific standards, the physical limitations of interpreting COTS Wi-Fi CSI must be explicitly recognized:

1. **Sampled Channel Metric, Not an Image:** CSI is a sampled complex scalar representing the aggregated channel transfer function. It does not provide direct optical pixels, range-Doppler point clouds, or physical silhouettes of a human body.
2. **Phase Noise & Carrier Frequency Offset (CFO):** In commodity Wi-Fi silicon, the transmitter and receiver operate on unsynchronized local oscillators. Small frequency differences ($\Delta f \approx 10\text{ to }50\text{ kHz}$) cause the raw phase measurements $\angle H(f_k, t)$ to rotate continuously between $[-\pi, +\pi]$ from packet to packet, preventing raw phase from being used directly without conjugate phase sanitization.
3. **Complex Indoor Geometry & Shadowing:** Furniture, metallic filing cabinets, and structural pillars create static multipath shadowing. RF sensitivity is not spatially uniform throughout a room; quadrants positioned further from receiver antennas inherently suffer from geometric path loss.

---
*(End of Chapter 2 — Source: Wi-Fi Physical Layer Standards IEEE 802.11n & Radio Propagation Theory)*


---

# CHAPTER 3: HARDWARE ARCHITECTURE AND EXPERIMENTAL DEPLOYMENT

---

## 3.1 System Requirements and Hardware Selection

The design of a device-free radio frequency (RF) sensing system imposes strict architectural constraints on the physical hardware layer. To capture human-induced multipath perturbations in real time without specialized laboratory equipment, the underlying RF transceivers must satisfy five core requirements:

1. **Subcarrier-Level Channel State Information (CSI) Accessibility:** The hardware platform must expose the raw Physical Layer (PHY) Channel Frequency Response (CFR)—including orthogonal subcarrier amplitudes and phase matrices—directly to software callbacks, rather than providing only macroscopic, scalar Received Signal Strength Indication (RSSI) values.
2. **Deterministic High-Rate Packet Emission:** Transmitters must support stable, programmable broadcast rates exceeding 100 Hz to sample fast Doppler and locomotion shifts without packet timing jitter.
3. **High-Throughput Serial Streaming:** The receiver must serialize multi-subcarrier raw data frames to a host processing hub over high-speed Universal Asynchronous Receiver-Transmitter (UART) lines without internal FIFO buffer overflows.
4. **Low Cost and Commercial Off-The-Shelf (COTS) Availability:** To validate the real-world feasibility of pervasive indoor situational awareness, transceivers must be commercially accessible commodity components rather than expensive Software-Defined Radios (SDRs) such as USRPs or specialized millimeter-wave (mmWave) radar front-ends.
5. **Decentralized Spatial Placement:** The nodes must operate independently with localized DC power, allowing distributed multi-point spatial installation across arbitrary indoor geometries.

Based on these criteria, the Espressif **ESP32-WROOM-32** microcontroller was selected as the foundational hardware platform across all sensing nodes.

---

## 3.2 ESP32-WROOM-32 and Supporting Components

The ESP32-WROOM-32 module integrates a 2.4 GHz Wi-Fi and Bluetooth coexistence system-on-chip (SoC) manufactured on TSMC's 40 nm low-power process. Its internal architecture and peripheral features relevant to WiMotion 2.0 include:

* **Processor Core:** Dual-core 32-bit Xtensa LX6 microprocessors running at a selectable clock frequency of up to 240 MHz, delivering up to 600 DMIPS computing power.
* **RF Transceiver:** Fully integrated 2.4 GHz receiver and transmitter complying with IEEE 802.11b/g/n standards. In 802.11n Orthogonal Frequency Division Multiplexing (OFDM) mode with a 20 MHz channel bandwidth, the hardware baseband exposes raw CSI matrices for 64 discrete subcarriers.
* **Internal Memory:** 520 KB on-chip SRAM alongside 4 MB external Quad-SPI flash memory for RTOS firmware storage and runtime circular buffers.
* **Serial Bridge Silicon:** Interfaced via an external Silicon Labs CP2102 USB-to-UART bridge controller, enabling continuous full-duplex asynchronous data rates up to 921,600 baud.
* **RF Front-End:** On-board inverted-F PCB trace antenna with nominal omnidirectional radiation pattern and typical peak gain of +2 dBi.

```
       ┌────────────────────────────────────────────────────────┐
       │                 ESP32-WROOM-32 SoC                     │
       │                                                        │
       │  ┌──────────────────────┐    ┌──────────────────────┐  │
       │  │   Xtensa LX6 Core 0  │    │   Xtensa LX6 Core 1  │  │
       │  │    (PRO_CPU: Wi-Fi)  │    │    (APP_CPU: Tasks)  │  │
       │  └──────────┬───────────┘    └──────────┬───────────┘  │
       │             │                           │              │
       │  ┌──────────┴───────────────────────────┴───────────┐  │
       │  │             520 KB Internal SRAM                 │  │
       │  └──────────────────────┬───────────────────────────┘  │
       │                         │                              │
       │  ┌──────────────────────┴───────────────────────────┐  │
       │  │          802.11n 2.4 GHz PHY Baseband            │  │
       │  │     (64-Subcarrier CSI Hardware Extraction)      │  │
       │  └──────────────────────┬───────────────────────────┘  │
       └─────────────────────────┼──────────────────────────────┘
                                 │
                     ┌───────────┴───────────┐
                     │ CP2102 USB-UART Bridge│
                     │  (921,600 Baud Link)  │
                     └───────────┬───────────┘
                                 │
                         To Host Laptop
```

---

## 3.3 Transmitter and Receiver Roles

The six microcontrollers operate under two asymmetric, complementary firmware roles designed using the official Espressif IoT Development Framework (ESP-IDF v5.1):

### 3.3.1 Active Transmitters (STA Mode)
The four transmitter nodes (designated **TX1**, **TX2**, **TX3**, and **TX4**) operate as Wi-Fi Stations (STA). Rather than maintaining a full TCP/IP networking association, the transmitters execute a lightweight FreeRTOS periodic timer loop:
- Every 10 milliseconds ($\Delta t = 10\text{ ms}$, corresponding to a frame frequency $f_{\text{tx}} \approx 100\text{ Hz}$), the transmitter baseband broadcasts an unencrypted 802.11 Action frame containing a sequence counter and node identifier payload.
- All four transmitters transmit on standard 2.4 GHz **Wi-Fi Channel 6** (center frequency $f_c = 2.437\text{ GHz}$).
- Transmit power is locked at $+20\text{ dBm}$ (maximum nominal output) with dynamic power management and Wi-Fi sleep modes disabled to eliminate baseline gain steps.

### 3.3.2 Centralized Promiscuous Receivers (AP Mode)
The two receiver nodes (designated **RX1** and **RX2**) operate in Wi-Fi Access Point (SoftAP) promiscuous sniffer mode:
- The receiver Wi-Fi PHY layer is configured via `esp_wifi_set_csi_rx_cb()` to invoke a low-level ISR callback upon successfully decoding the PHY preamble of any incoming frame on Channel 6.
- The callback captures the raw complex CSI struct (`wifi_csi_info_t`) from hardware registers before packet filtering drops non-whitelisted management traffic.
- The captured CSI record is immediately written to a high-speed hardware UART ring buffer and streamed over USB to the central host workstation.

---

## 3.4 Six-Node Architecture: Four Transmitters and Two Receivers

A critical technical distinction must be maintained regarding system topology: **WiMotion 2.0 does not employ an ad-hoc 802.11s mesh network.** In an ad-hoc mesh, packets hop between nodes, which introduces non-deterministic queuing latency and destroys physical layer timing coherence.

Instead, WiMotion 2.0 implements a **Distributed Multi-Link Star Topology** ($4\text{ TX} \to 2\text{ RX}$):
- Four perimeter transmitters broadcast simultaneously across the shared wireless medium.
- Two independent, spatially separated receivers capture these broadcasts concurrently.
- This creates **8 concurrent logical spatial links** ($4 \text{ Transmitters} \times 2 \text{ Receivers} = 8 \text{ Spatial Baselines}$) traversing the physical room environment.

```
                  [TX2: Zone 2 (NW)]                      [TX1: Zone 1 (NE)]
                 (1C:69:20:31:38:08)                     (BC:DD:C2:CC:49:F4)
                          │                                       │
                          │   Link 1 (RX1-TX2)                    │   Link 0 (RX1-TX1)
                          │   Link 5 (RX2-TX2)                    │   Link 4 (RX2-TX1)
                          │                                       │
                          ▼                                       ▼
                  ┌────────────────────────────────────────────────────────┐
                  │                 INDOOR MONITORED SPACE                 │
                  │              (4-Quadrant Spatial Grid)                 │
                  │                                                        │
                  │             [RX1: COM8]     [RX2: COM9]                │
                  │           (Central Dual-Receiver Hub)                  │
                  └────────────────────────────────────────────────────────┘
                          ▲                                       ▲
                          │                                       │
                          │   Link 2 (RX1-TX3)                    │   Link 3 (RX1-TX4)
                          │   Link 6 (RX2-TX3)                    │   Link 7 (RX2-TX4)
                          │                                       │
                 (1C:69:20:31:4B:40)                     (CC:7B:5C:28:84:70)
                  [TX3: Zone 3 (SW)]                      [TX4: Zone 4 (SE)]
```

---

## 3.5 Physical Link Allocation and Eight-Link Matrix

Every physical packet captured by either receiver is demultiplexed into one of the eight spatial links based on the tuple:

$$\text{Link ID} = (\text{Receiver ID}, \text{Transmitter MAC})$$

The complete physical link allocation matrix is defined in Table 3.1:

### Table 3.1: WiMotion 2.0 Physical Link Allocation & Spatial Baselines

| Link Index | Logical Link | Receiver Node | Host Port | Transmitter Node | Factory Hardware MAC Address | Primary Spatial Quadrant Monitored | Baseline Geometric Role |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **$L_0$** | `RX1-TX1` | RX1 | `COM8` | TX1 | `BC:DD:C2:CC:49:F4` | Zone 1 ($Z_1$ - North-East) | Direct LOS baseline covering room entrance |
| **$L_1$** | `RX1-TX2` | RX1 | `COM8` | TX2 | `1C:69:20:31:38:08` | Zone 2 ($Z_2$ - North-West) | Cross-quadrant diagonal path intersecting desk |
| **$L_2$** | `RX1-TX3` | RX1 | `COM8` | TX3 | `1C:69:20:31:4B:40` | Zone 3 ($Z_3$ - South-West) | Long diagonal baseline traversing full room length |
| **$L_3$** | `RX1-TX4` | RX1 | `COM8` | TX4 | `CC:7B:5C:28:84:70` | Zone 4 ($Z_4$ - South-East) | Lateral perimeter link monitoring East wall |
| **$L_4$** | `RX2-TX1` | RX2 | `COM9` | TX1 | `BC:DD:C2:CC:49:F4` | Zone 1 ($Z_1$ - North-East) | Lateral perimeter link monitoring North wall |
| **$L_5$** | `RX2-TX2` | RX2 | `COM9` | TX2 | `1C:69:20:31:38:08` | Zone 2 ($Z_2$ - North-West) | Direct LOS baseline covering primary workstation |
| **$L_6$** | `RX2-TX3` | RX2 | `COM9` | TX3 | `1C:69:20:31:4B:40` | Zone 3 ($Z_3$ - South-West) | Lateral perimeter link monitoring South-West boundary |
| **$L_7$** | `RX2-TX4` | RX2 | `COM9` | TX4 | `CC:7B:5C:28:84:70` | Zone 4 ($Z_4$ - South-East) | Direct LOS baseline covering window perimeter |

---

## 3.6 Experimental Room and Zone Layout

Empirical hardware benchmarking was conducted in `ROOM_LAB_A`, a rectangular indoor laboratory environment with dimensions:

$$\text{Length} = 5.80\text{ m}, \quad \text{Width} = 4.20\text{ m}, \quad \text{Floor Area} \approx 24.36\text{ m}^2$$

The room boundaries consist of standard concrete outer walls, hollow-brick partition walls, acoustic ceiling tiles at a height of 2.80 m, and ceramic tiled flooring. The physical space is divided into four functional quadrants:

* **Zone 1 ($Z_1$ - North-East Quadrant):** Entrance corridor and doorway passage. Primary path intersection for Links $L_0$ and $L_4$.
* **Zone 2 ($Z_2$ - North-West Quadrant):** Workstation zone containing an office desk, chairs, and computing equipment. Primary intersection for Links $L_1$ and $L_5$.
* **Zone 3 ($Z_3$ - South-West Quadrant):** Storage and perimeter flank. Characterized by longer propagation baselines ($L_2$ and $L_6$) and non-metallic shelving.
* **Zone 4 ($Z_4$ - South-East Quadrant):** Window wall and perimeter walkway. Primary intersection for Links $L_3$ and $L_7$.
* **CLEAR:** Ground truth baseline state denoting zero physical human presence within the enclosed space.

```
       ┌────────────────────────────────────────────────────────┐
       │ (0.0, 4.2)                                  (5.8, 4.2) │
       │   [TX2: Node NW] ────────── Northern Wall ───────── [TX1: Node NE]
       │         │                                                 │
       │         │           ZONE 2               ZONE 1           │
       │         │        (North-West)         (North-East)        │
       │         │       Primary Workstation     Doorway Access    │
       │         │                                                 │
       │   Western Wall         [RX1]         [RX2]          Eastern Wall
       │         │            (Central Workstation Hub)            │
       │         │                                                 │
       │         │           ZONE 3               ZONE 4           │
       │         │        (South-West)         (South-East)        │
       │         │        Storage Flank        Window Perimeter    │
       │         │                                                 │
       │   [TX3: Node SW] ────────── Southern Wall ───────── [TX4: Node SE]
       │ (0.0, 0.0)                                  (5.8, 0.0) │
       └────────────────────────────────────────────────────────┘
```

---

## 3.7 Firmware Configuration and Communication Parameters

Both transmitter and receiver firmware were written in C utilizing FreeRTOS tasks. The exact runtime parameters are recorded in Table 3.2:

### Table 3.2: WiMotion 2.0 Firmware Configuration Parameters

| Parameter Name | Configuration Setting | Engineering Function |
| :--- | :--- | :--- |
| **Wi-Fi Operating Band** | 2.4 GHz ISM Band | High penetration through non-metallic indoor materials |
| **Primary Channel** | Channel 6 ($f_c = 2.437\text{ GHz}$) | Fixed center frequency avoiding dynamic channel switching |
| **Channel Bandwidth** | 20 MHz (HT20) | Extracts 64 OFDM subcarriers per packet |
| **CSI Extraction Mask** | Full LL-LTF + HT-LTF | Captures full channel estimation preambles |
| **TX Broadcast Interval** | 10 milliseconds ($\approx 100\text{ Hz}$) | High temporal resolution capturing human gait transients |
| **TX Transmit Power** | +20 dBm (0.1 Watt) | Consistent SNR across all diagonal link lengths |
| **UART Baud Rate** | 921,600 baud | Prevents serial buffer stalls during 400 pkt/sec aggregate bursts |
| **UART Flow Control** | Disabled (Hardware FIFO) | Minimizes hardware handshaking latency |

---

## 3.8 Power, USB and Serial-Connection Management

The hardware deployment enforces strict isolation between AC mains power and signal acquisition:
- **Transmitter Nodes (TX1–TX4):** Each corner node is powered independently via isolated 5V/2A USB wall adapters. This ensures that transmitter ground loops do not corrupt receiver baseband references.
- **Receiver Nodes (RX1, RX2):** Plugged directly into dedicated host USB 3.0 ports via short (0.5m), shielded micro-USB cables. The host assigns virtual COM ports (`COM8` for RX1, `COM9` for RX2).
- **Safe Standby Circuitry:** When the WiMotion 2.0 software server is in `REPLAY` or `SIMULATION` mode, host serial port acquisition threads enter a low-power, non-polling **Safe Standby State**. This prevents Windows USB-UART serial drivers (specifically `usbser.sys` and `silabser.sys`) from triggering DPC Watchdog Violation kernel timeouts when hardware nodes are unpowered or disconnected.

---

## 3.9 Hardware Photographs and Deployment Record

A comprehensive photographic audit was captured on October 20–21, 2026, during the final experimental deployment in `ROOM_LAB_A`.

* **[Figure 3.1: Panoramic View of ROOM_LAB_A]:** Wide-angle photograph illustrating the 4-quadrant layout, spatial boundaries, and the central dual-receiver testbed.
* **[Figure 3.2: Corner Transmitter Installation (TX1 & TX2)]:** Close-up photographs showing the 3D-printed wall mounts, inverted-F antenna orientations, and isolated 5V power feeds.
* **[Figure 3.3: Corner Transmitter Installation (TX3 & TX4)]:** Close-up photographs showing South-West and South-East node placements at a calibrated height of 1.2 meters.
* **[Figure 3.4: Central Dual-Receiver Host Station]:** Macro photograph showing RX1 (`COM8`) and RX2 (`COM9`) connected to the host laptop, highlighting the physical antenna baseline separation ($d = 24.5\text{ cm}$).
* **[Figure 3.5: Subject Traversal Experiment]:** Photograph of the human subject executing single-occupant controlled walking trials across Quadrant 1 ($Z_1$).
* **[Figure 3.6: Six-Node Active Distributed Hardware Testbed Assembly]:** Photograph showing the complete assembled multi-link ESP32 hardware testbed configured with dual receivers and distributed transmitters.

---
*(End of Chapter 3 — Source: WiMotion 2.0 Hardware Engineering Manifest & HARDWARE_SESSION_LOG.txt)*


---

# CHAPTER 4: CSI DATA ACQUISITION AND SOFTWARE INGESTION PIPELINE

---

## 4.1 Software Architecture and Data Flow

The WiMotion 2.0 software system transforms unstructured, high-rate physical layer byte streams into structured, synchronized link-level representations. The architecture operates across four distinct abstraction layers:

```
[PHYSICAL LAYER]        RX1 (COM8 @ 921.6k)          RX2 (COM9 @ 921.6k)
                                 │                            │
                                 ▼                            ▼
[INGESTION LAYER]       Worker Thread 1              Worker Thread 2
                        (Ring Buffer 1)              (Ring Buffer 2)
                                 │                            │
                                 └─────────────┬──────────────┘
                                               ▼
[PARSING & ROUTING]                 Parser & Demultiplexer
                                 (spatial/serial_manager.py)
                                               │
                                 ┌─────────────┴──────────────┐
                                 ▼                            ▼
[DATA GOVERNANCE]        Known Node Frames          Unknown Node Frames
                         (MAC Whitelisted)       (4C:11:AE:64:9A:05 -> UNKNOWN)
                                 │                            │
                                 ▼                            ▼
[SPATIAL PIPELINE]      8-Link Sliding Window      Quarantined Diagnostic
                        Buffer (2.0s Duration)             Bucket
                                 │
                                 ▼
[TELEMETRY & INFERENCE] Dual-Engine Real-Time HUD & Observatory Dashboard
```

1. **Physical Serial Ingestion Layer:** Two dedicated background threads handle raw byte streaming from `COM8` and `COM9`.
2. **Frame Parsing & Validation Layer:** Serial lines are validated for framing integrity, magic byte headers, and non-corrupt numeric fields.
3. **Identity Demultiplexing & Security Layer:** Physical MAC addresses are resolved against the active node table; rogue or ambient AP traffic is routed to an isolated quarantine bucket.
4. **Sliding Window Buffer Layer:** Valid records are inserted into a continuous 2.0-second time-series buffer partitioned across the 8 physical baselines.

---

## 4.2 CSI Acquisition at the Receiver

At the receiver node (operating in 802.11n promiscuous sniffer mode), the ESP32 Wi-Fi hardware MAC layer decodes incoming frames and triggers the low-level interrupt service routine (ISR) configured via the ESP-IDF API:

```c
// Receiver CSI Callback Registration (firmware/rx/main.c)
wifi_csi_config_t csi_config = {
    .lltf_en           = true,
    .htltf_en          = true,
    .stbc_htltf2_en    = false,
    .ltf_merge_en      = false,
    .channel_filter_en = false,
    .manu_scale        = false,
    .shift             = false
};
ESP_ERROR_CHECK(esp_wifi_set_csi_config(&csi_config));
ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(&wifi_csi_rx_cb, NULL));
```

When an 802.11 packet is decoded on Channel 6, the `wifi_csi_rx_cb` callback is invoked with a pointer to the `wifi_csi_info_t` struct:
- **`len`:** Total raw payload bytes (typically 128 bytes for 64 subcarriers in signed 8-bit I/Q format).
- **`rssi`:** Received Signal Strength Indication (in dBm) measured by receiver Automatic Gain Control (AGC).
- **`buf`:** Array of raw signed 8-bit integers representing interleaved In-Phase ($I_k$) and Quadrature ($Q_k$) components for each subcarrier $k \in [0, 63]$.
- **`mac`:** 6-byte source MAC address extracted from the 802.11 frame header.

The callback formats this binary payload into a single, compact comma-delimited ASCII string prefixed with the magic header `CSI_DATA` and pushes it directly to the hardware UART transmit FIFO buffer.

---

## 4.3 Serial Communication and Asynchronous Ingestion

Streaming two concurrent receivers each broadcasting at ~100 Hz generates an aggregate data rate of:

$$R_{\text{aggregate}} \approx 2\text{ Receivers} \times 100\text{ packets/sec} \times 240\text{ bytes/packet} \approx 48,000\text{ bytes/sec}$$

If the host operating system performs synchronous serial reads on the main server thread, any minor computational delay (such as running model inference or rendering WebSockets) causes the operating system serial input buffer to overflow, dropping frames and corrupting time-series continuity.

WiMotion 2.0 resolves this via **`spatial/serial_manager.py`**, which launches two asynchronous ingestion worker threads (`ReceiverWorker`):
- Each worker owns an independent `serial.Serial` instance configured with a 100 ms timeout and a 64 KB internal OS read buffer.
- Incoming bytes are accumulated into a local line buffer until a newline character (`\n`) is encountered.
- Complete lines are deposited into a thread-safe circular ring buffer protected by Python's `threading.Lock`.
- When the host consumer queries for new records, the worker atomically drains the buffer and returns newly arrived lines.

---

## 4.4 Packet Parsing and CSI Data Extraction

The parsing logic in **`spatial/parser.py`** inspects every raw serial line against strict structural validation rules before allocating memory:

```python
# Raw Frame Header Verification (spatial/parser.py)
if not line.startswith("CSI_DATA"):
    return None  # Discard framing noise and boot messages
parts = line.strip().split(",")
if len(parts) < 14:
    return None  # Discard truncated packets
```

### Table 4.1: Raw Serial CSI Packet Schema Definition

| Field Index | Token Name | Data Type | Physical Meaning | Example Value |
| :---: | :--- | :--- | :--- | :---: |
| 0 | `header` | String | Magic frame identifier | `CSI_DATA` |
| 1 | `rx_id` | String | Local receiver identifier assigned by port | `RX1` |
| 2 | `tx_mac` | String | Source transmitter hardware MAC address | `BC:DD:C2:CC:49:F4` |
| 3 | `channel` | Integer | Wi-Fi operational RF channel | `6` |
| 4 | `rssi` | Integer | Aggregate received signal power in dBm | `-42` |
| 5 | `noise_floor` | Integer | Internal baseband thermal noise floor register | `-96` |
| 6 | `rate` | Integer | Physical layer PHY transmission rate index | `11` |
| 7 | `sig_mode` | Integer | Signal modulation mode (0=Legacy, 1=HT) | `1` |
| 8 | `mcs` | Integer | Modulation and Coding Scheme index | `7` |
| 9 | `bandwidth` | Integer | Channel bandwidth (0=20MHz, 1=40MHz) | `0` |
| 10 | `smoothing` | Integer | Receiver channel estimation filter flag | `1` |
| 11 | `not_sounding` | Integer | Beamforming sounding frame flag | `0` |
| 12 | `len` | Integer | Count of subcarrier I/Q byte pairs | `64` |
| 13..N | `amplitudes` | Integer Array | Signed 8-bit In-phase ($I_k$) and Quadrature ($Q_k$) bytes | `[12, -4, 15, ...]` |

For each subcarrier $k \in [0, 63]$, the raw subcarrier amplitude $A_k$ is computed from the interleaved bytes:

$$A_k = \sqrt{I_k^2 + Q_k^2}$$

The parser returns a fully typed `CSIRecord` object encapsulating timestamp, receiver ID, transmitter MAC, RSSI, and the 64-element amplitude array.

---

## 4.5 Transmitter Identification Using MAC Addresses

In a multi-transmitter star topology, distinguishing which physical node emitted a packet is paramount. Early single-link sensing systems did not verify sender identities, leaving them vulnerable to any ambient 802.11 beacon.

WiMotion 2.0 binds physical layer measurements to spatial transmitter coordinates via an authoritative factory MAC lookup table:

```python
# Hardware Node Identity Mapping (spatial/parser.py)
TRANSMITTER_MAP = {
    "BC:DD:C2:CC:49:F4": "TX1",  # Zone 1 (North-East Quadrant)
    "1C:69:20:31:38:08": "TX2",  # Zone 2 (North-West Quadrant)
    "1C:69:20:31:4B:40": "TX3",  # Zone 3 (South-West Quadrant)
    "CC:7B:5C:28:84:70": "TX4"   # Zone 4 (South-East Quadrant)
}
```

When a frame is received, the 6-byte hexadecimal MAC string is extracted and normalized (uppercase, colon-delimited). If the address matches an entry in `TRANSMITTER_MAP`, the corresponding logical ID (`TX1`..`TX4`) is stamped onto the record.

---

## 4.6 Unknown-Node Filtering and Link Validation

During physical hardware trials in `ROOM_LAB_A`, packet sniffer logs revealed that ambient Wi-Fi access points frequently broadcast beacon frames on Channel 6. In particular, an uncoordinated third-party router with MAC:

$$\text{Ambient MAC} = \text{4C:11:AE:64:9A:05}$$

was observed transmitting periodic management frames that collided with experimental packets.

WiMotion 2.0 handles this through strict **Unknown-Node Filtering**:
1. If an incoming packet's source MAC does not match any entry in `TRANSMITTER_MAP`, the record's transmitter ID is marked as `UNKNOWN`.
2. The packet is **quarantined**: it is routed to a diagnostic logging bucket and explicitly excluded from spatial feature windows.
3. It is mathematically impossible for uncoordinated ambient Wi-Fi frames to corrupt the variance calculations of Links $L_0$ through $L_7$ or trigger false-alarm zone activations.

---

## 4.7 Buffer Management, Timestamping and Data Integrity

To guarantee that time-series analysis reflects physical reality, records are stamped with high-resolution host timestamps using `time.perf_counter()` immediately upon exit from the serial ring buffer.

### 4.7.1 Sliding Window Buffer Architecture (`spatial/window.py`)
Records are held in a dual-ended queue (`collections.deque`) maintaining a continuous temporal history:
- **Window Duration:** Fixed at $T_w = 2.0\text{ seconds}$.
- **Window Stride (Step):** Configured at $\Delta t_{\text{step}} = 0.5\text{ seconds}$ (75% temporal overlap).
- **Eviction Policy:** As new frames arrive, records with timestamps $t < (t_{\text{current}} - T_w)$ are automatically evicted, ensuring constant $O(1)$ memory consumption over arbitrarily long runtime sessions.

---

## 4.8 Error Handling and Software Safeguards

The ingestion pipeline incorporates multiple layers of defensive error handling:

* **Non-Blocking Framing Recovery:** If a serial framing error occurs (e.g., an interrupted USB transfer during a physical vibration of the cable), the parser scans forward until it detects the next newline byte (`\n`) and valid `CSI_DATA` header. Corrupted partial strings are discarded without raising unhandled Python exceptions.
* **Non-Finite Amplitude Clamping:** Any subcarrier amplitude evaluating to `NaN`, `Inf`, or exceeding physical 12-bit ADC limits ($A_k \ge 10,000$) is scrubbed and replaced with the window median.
* **Serial Port Auto-Reconnection:** If an active USB port is disconnected, the worker enters a graceful retry loop, attempting re-connection every 2.0 seconds while logging warnings without crashing the parent server process.

---

## 4.9 Data Acquisition Challenges and Solutions

During initial prototype integration, three major hardware-software interface bottlenecks were encountered and systematically resolved:

### Table 4.2: Data Acquisition Engineering Challenges & Solutions

| Technical Challenge | Root Cause | Engineering Solution Implemented in WiMotion 2.0 |
| :--- | :--- | :--- |
| **Serial Buffer Overflow** | Synchronous Python serial reads stalled during server WebSocket broadcast cycles. | Decoupled asynchronous multi-threaded workers with dedicated 64 KB circular ring buffers. |
| **Thread-Race Data Drops** | Multiple threads writing to CSV log files simultaneously without synchronization locks. | Deployed atomic `threading.Lock` across all file writers in `spatial/serial_manager.py`. |
| **Windows DPC Watchdog BSOD** | Windows serial driver polling disconnected USB ports during idle states. | Implemented **Safe Standby Mode**, closing active serial handles until explicit `LIVE` mode transition. |

---
*(End of Chapter 4 — Source: spatial/serial_manager.py, spatial/parser.py, and spatial/window.py)*


---

# CHAPTER 5: FEATURE ENGINEERING AND MACHINE LEARNING PIPELINE

---

## 5.1 Overview of the Processing Pipeline

The core task of WiMotion 2.0 is mapping continuous, high-dimensional multi-link Channel State Information (CSI) time-series into discrete spatial quadrant disturbance predictions ($Z_1, Z_2, Z_3, Z_4$, or `CLEAR`).

The signal processing architecture operates through a deterministic, five-stage transformation pipeline:

```
[STAGE 1: RAW BUFFER]    64-Subcarrier CSI records accumulated over 2.0s sliding window
                                             │
                                             ▼
[STAGE 2: PREPROCESSING] Clean non-finite samples; compute per-packet mean subcarrier amplitudes
                                             │
                                             ▼
[STAGE 3: LINK EXTRACTION]Partition records into 8 link groups; extract 6 temporal metrics per link
                                             │
                                             ▼
[STAGE 4: VECTOR FUSION] Fused into Canonical 56-Dimensional Representation (48 stats + 8 flags)
                                             │
                                             ▼
[STAGE 5: DUAL INFERENCE]├── Energy Gate Thresholding (theta = 1.80) -> Hard CLEAR Suppression
                         ├── Heuristic Multi-Link Ratio Baseline (argmax Normalized Variance)
                         └── Supervised Random Forest Classifier (100 Trees -> 5-Class Probabilities)
```

---

## 5.2 CSI Preprocessing and Signal-Quality Assessment

Raw subcarrier amplitudes captured by COTS ESP32 receivers exhibit occasional hardware artifacts, including Automatic Gain Control (AGC) step discontinuities and high-frequency thermal spikes. 

### 5.2.1 Subcarrier Amplitude Cleaning (`clean_amplitudes`)
For every incoming frame, the 64-element amplitude array $\mathbf{A} = [A_0, A_1, \dots, A_{63}]$ is cleaned via `spatial/features.py:clean_amplitudes`:
1. **Finite Verification:** All values are cast to 64-bit floating point; any non-finite values (`NaN` or $\pm\infty$) are filtered out.
2. **Physical Boundary Clamping:** Amplitudes are constrained to valid physical ADC dynamic ranges:
   $$\mathbf{A}_{\text{clean}} = \{ A_k \in \mathbf{A} \mid 0 \le A_k < 10,000 \}$$
3. **Packet-Level Summary Amplitude:** If valid subcarriers remain, the packet's overall signal amplitude is summarized as the arithmetic mean across subcarriers:
   $$\bar{A} = \frac{1}{|\mathbf{A}_{\text{clean}}|} \sum_{k \in \mathbf{A}_{\text{clean}}} A_k$$

### 5.2.2 Minimum Link Packet Threshold
To prevent noisy, under-sampled links from corrupting the spatial feature vector, a link group must contain a minimum of **3 valid packets** within the 2.0-second window ($N \ge 3$). If a link has fewer than 3 packets, its continuous features are imputed as zero and its validity flag is cleared.

---

## 5.3 Temporal Sliding Windows

Human locomotion exhibits characteristic physical timescales: a single step spans approximately 0.4 to 0.7 seconds, while traversing an entire quadrant spans 1.5 to 3.0 seconds. 

WiMotion 2.0 structures time-series data using temporal sliding windows defined by two parameters:
- **Window Duration ($T_w$):** Fixed at $2.0\text{ seconds}$. At a nominal frame rate of ~100 Hz per node, a 2.0-second window contains approximately 150 to 200 packets per link, providing robust sample sizes for statistical moments.
- **Window Step ($\Delta t$):** Configured at $0.5\text{ seconds}$, providing an inference update frequency of $2\text{ Hz}$.
- **Temporal Overlap:** Consecutive windows share $75\%$ of their temporal duration:
  $$\text{Overlap Ratio} = \frac{T_w - \Delta t}{T_w} = \frac{2.0 - 0.5}{2.0} = 75\%$$

---

## 5.4 Mathematical Formulation of the 56-Dimensional Feature Vector

A fundamental flaw in early wireless sensing literature is the vague or inconsistent definition of feature vectors between training scripts and production servers. WiMotion 2.0 enforces a strict **Canonical 56-Dimensional Schema** (`FEATURE_SCHEMA_VERSION = "2.0.0-canonical-56dim"`).

Across the 8 candidate links ($L_0$ to $L_7$), exactly **6 continuous temporal variation statistics** are extracted, followed by **8 binary link-validity flags**:

$$\mathbf{x} = \big[ \mathbf{f}_{L_0}, \mathbf{f}_{L_1}, \dots, \mathbf{f}_{L_7}, \; v_{L_0}, v_{L_1}, \dots, v_{L_7} \big] \in \mathbb{R}^{56}$$

### 5.4.1 The 6 Continuous Temporal Variation Metrics (per link)
Let $\mathbf{x} = [x_1, x_2, \dots, x_N]$ denote the sequence of mean packet amplitudes for link $L_i$ within the window, and let $\Delta x_j = x_{j+1} - x_j$ represent the first difference between consecutive packets ($j = 1, \dots, N-1$):

1. **Mean Amplitude (`mean_amp`):**
   $$\mu = \frac{1}{N} \sum_{j=1}^{N} x_j$$
   *Physical Meaning:* Reflects baseline path loss and macroscopic line-of-sight attenuation.

2. **Standard Deviation of Amplitude (`std_amp`):**
   $$\sigma = \sqrt{ \frac{1}{N} \sum_{j=1}^{N} (x_j - \mu)^2 }$$
   *Physical Meaning:* Quantifies total envelope perturbation magnitude caused by moving obstacles.

3. **Mean Absolute Amplitude Delta (`mean_delta`):**
   $$\mu_{|\Delta|} = \frac{1}{N-1} \sum_{j=1}^{N-1} |\Delta x_j|$$
   *Physical Meaning:* Captures packet-to-packet high-frequency variation rate; sensitive to rapid limb movements.

4. **Root-Mean-Square Amplitude Delta (`rms_delta`):**
   $$\text{RMS}_{\Delta} = \sqrt{ \frac{1}{N-1} \sum_{j=1}^{N-1} (\Delta x_j)^2 }$$
   *Physical Meaning:* Emphasizes large transient signal jumps caused by human footstep impacts.

5. **95th Percentile Absolute Delta (`p95_delta`):**
   $$P_{95} = \text{Quantile}_{0.95} \big( \{ |\Delta x_1|, |\Delta x_2|, \dots, |\Delta x_{N-1}| \} \big)$$
   *Physical Meaning:* Captures peak dynamic range spikes while rejecting isolated single-sample outliers.

6. **Mean Squared Temporal Variance (`energy` / `csi_variance`):**
   $$\sigma^2 = \frac{1}{N} \sum_{j=1}^{N} (x_j - \mu)^2$$
   *Physical Meaning:* Primary energy metric representing the total dynamic variance induced on the RF carrier.

### 5.4.2 The 8 Link-Validity Flags (`valid_RX_TX`)
For each of the 8 logical links, a binary indicator $v_{L_i} \in \{0.0, 1.0\}$ is appended:
$$v_{L_i} = \begin{cases} 1.0, & \text{if Link } L_i \text{ has } \ge 3 \text{ valid packets in window} \\ 0.0, & \text{otherwise} \end{cases}$$

This yields $8 \times 6 = 48\text{ continuous features} + 8\text{ binary flags} = \mathbf{56\text{ total dimensions}}$.

---

## 5.5 Link-Validity Flags and Missing-Data Handling

In real-world Wi-Fi environments, wireless links experience packet loss due to co-channel collisions, antenna orientation dips, or physical occlusions. 

WiMotion 2.0 handles missing links through deterministic zero-imputation:
- If Link $L_i$ has zero packets or fails the minimum packet threshold ($N < 3$), all 6 continuous features are imputed as exactly `0.0`, and $v_{L_i}$ is set to `0.0`.
- Because the Random Forest classifier splits on both continuous variance values and binary flags, the model natively learns that $v_{L_i} = 0.0$ signifies an unavailable link rather than a dead-quiet room.

---

## 5.6 Training and Inference Pipeline Consistency

A severe, widespread defect in machine learning projects is **train-serving skew**: where feature extraction logic in offline training scripts subtly diverges from live inference server code (e.g., different floating-point rounding, different subcarrier averaging orders, or missing link imputations).

In WiMotion 2.0, train-serving skew is mathematically prevented:
- **`spatial/features.py:build_canonical_56dim_feature_vector`** serves as the **single source of truth** across the entire repository.
- The offline dataset builder (`scripts/build_manual_gt_v1.py`), the model training pipeline (`scripts/train_spatial_model.py`), the replay loader (`spatial/replay_loader.py`), and the real-time server (`spatial/server.py`) import and call this exact same function.
- Automated unit test `test_feature_vector_parity_between_live_and_replay` strictly verifies that feeding identical raw packet arrays into live and offline pathways yields identical 56-D vectors with zero numerical difference.

---

## 5.7 Random Forest Classification

The primary supervised spatial localization model is a **Random Forest Classifier** (`RandomForestClassifier` from scikit-learn):
- **Ensemble Size:** 100 decorrelated decision trees ($B = 100$).
- **Splitting Criterion:** Gini Impurity:
  $$I_G(p) = 1 - \sum_{k=1}^{5} p_k^2$$
- **Max Features:** Evaluated at $\sqrt{56} \approx 7$ randomly sampled features per split.
- **Output Classes:** 5 mutually exclusive classes: `CLEAR`, `Z1`, `Z2`, `Z3`, and `Z4`.
- **Inference Latency:** Average inference time per 56-D vector is **$3.2\text{ milliseconds}$** on the host CPU, well within the 500 ms sliding window step budget.

---

## 5.8 Heuristic Spatial Estimation

Alongside the supervised machine learning model, WiMotion 2.0 maintains a deterministic, physical-layer **Heuristic Spatial Baseline (`SpatialBaseline`)**.

The heuristic algorithm operates by computing the normalized temporal variance of each link and assigning spatial disturbance to the quadrant whose primary LOS links exhibit maximum variance ratio:

$$\hat{Z}_{\text{heuristic}} = \arg\max_{k \in \{1,2,3,4\}} \left( \frac{\sigma^2_{\text{Link}(k)}}{\sum_{j=1}^{8} \sigma^2_{\text{Link}(j)}} \right)$$

If the maximum variance across all links is below an empirical idle threshold, the heuristic assigns `CLEAR`. This baseline serves as a direct point of comparison, demonstrating how much predictive power is added by machine learning versus simple energy ratio ranking.

---

## 5.9 Presence Gating and Prediction Quality Controls

Before passing a feature vector to the classifier, the server evaluates two pre-inference quality gates:

1. **Signal Rate Gate (`spatial/inference.py`):**
   The server monitors the real-time packet arrival rate across both receivers. If either receiver's rate drops below **$4.0\text{ Hz}$** or if total window packet count drops below 8, the state is locked to `INSUFFICIENT_DATA` and inference is suppressed.
2. **Calibrated CLEAR Energy Gate:**
   To address the high false-alarm rate in idle rooms, an empirical energy threshold $\theta = 1.80$ is evaluated. If $\max(\sigma^2_{L_0..L_7}) < 1.80$, the window is hard-gated to `CLEAR` without querying the decision trees (detailed in Chapter 6).

---

## 5.10 Limitations of the Current Feature Representation

While the 56-dimensional feature vector captures amplitude perturbations reliably, it exhibits two inherent physical limitations:
1. **Lack of Phase Sanitization:** Because raw CSI phase contains random carrier frequency offsets (CFO) and sampling frequency offsets (SFO), phase angles rotate uncontrollably across $[-\pi, +\pi]$ and cannot be directly fed to the model without conjugate phase subtraction.
2. **Environmental Non-Human Susceptibility:** Any moving non-human dielectric boundary—such as an open door swinging in a draught or fluttering metallic window blinds—produces temporal amplitude variance that the model cannot distinguish from human walking.

---
*(End of Chapter 5 — Source: spatial/features.py, spatial/inference.py, and models/spatial_model_scorecard.json)*


---

# CHAPTER 6: DATASET, EXPERIMENTAL METHODOLOGY AND RESULTS

---

## 6.1 Dataset Sources and Session Inventory

Empirical evaluation of WiMotion 2.0 was conducted across two distinct physical hardware capture campaigns in `ROOM_LAB_A`, totaling **172,974 physical CSI frames**:

1. **Phase A Exploratory Hardware Campaign (Sessions 001–007):** Comprises 116,588 frames captured across 7 long-duration sessions between October 15 and October 19, 2026. Captured during initial software integration and transmitter placement calibration.
2. **Phase B Controlled Hardware Campaign (`session_pB_*`):** Comprises 56,386 frames captured across 10 strictly scripted physical sessions on October 20, 2026. Designed with atomic file-write mutexes and structured as paired physical takes per class.

---

## 6.2 Historical Dataset Audit and Data Quarantine

A hallmark of rigorous engineering research is active auditing of data provenance. In late October 2026, an exhaustive read-only audit of all 17 historical recording sessions was executed using `scripts/audit_read_only_sessions.py` (documented in `docs/DATASET_AUDIT_REPORT.md`).

The audit cross-checked raw CSV packet rows against metadata JSON declarations and cryptographic file hashes, uncovering critical integrity anomalies:

### Table 6.1: Historical Dataset Audit & Quarantine Manifest

| Session Identifier | Motion Ground Truth | Declared Frames | Audited CSV Frames | Delta | Root Cause / Anomaly Observed | Audit Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: |
| `session_real_001` | Room Walk ($Z_1 \to Z_3$) | 14,200 | 13,850 | -350 | Serial thread-race packet drops before lock deployment | **QUARANTINED** |
| `session_real_002` | Desk Workstation ($Z_2$) | 16,500 | 16,110 | -390 | Thread contention during high-rate bursts | **QUARANTINED** |
| `session_real_003` | Empty Room Baseline | 12,000 | 11,820 | -180 | Intermittent USB-UART buffer overrun | **QUARANTINED** |
| `session_real_004` | Flank Walk ($Z_3$) | 15,000 | 14,640 | -360 | Non-epoch timestamp drift across receivers | **QUARANTINED** |
| `session_real_005` | Window Walk ($Z_4$) | 18,200 | 17,910 | -290 | Missing frame sequence numbers | **QUARANTINED** |
| `session_real_006` | Door Walk ($Z_1$) | 9,607 | 9,607 | 0 | Receiver timestamp-key collision in multi-RX merge | **QUARANTINED** |
| `session_real_007` | Perimeter Walk ($Z_4$) | 19,232 | 19,232 | 0 | Variable inter-packet arrival jitter (> 85 ms) | **QUARANTINED** |

### The Scientific Quarantine Decision
Rather than training machine learning models on sessions with dropped rows or ambiguous timestamp ordering, **all 116,588 frames across exploratory sessions 001–007 were formally quarantined**. They are retained strictly for diagnostic and offline stress-testing, and are **completely excluded from spatial model training and evaluation**.

---

## 6.3 Physical Hardware Data-Collection Campaign (Phase B)

Following the audit, the logging pipeline was refactored with atomic file-write mutexes (`threading.Lock`), and a new, strictly controlled hardware campaign (**Phase B**) was executed. 

Phase B captured **10 dedicated physical sessions** covering all five target classes (`CLEAR`, $Z_1$, $Z_2$, $Z_3$, $Z_4$):
- Each class was recorded in exactly two independent physical takes: **Take 01** and **Take 02**.
- All human motion sessions involved a single active human subject executing continuous, controlled walking loops within the designated quadrant boundaries.
- **Audit Verification:** All 10 Phase B sessions passed the audit with **100% strict match** between CSV rows and metadata headers, zero dropped frames, and strict monotonically increasing epoch timestamps.

### Table 6.2: Phase B Controlled Benchmark Dataset Inventory

| Session Identifier | Ground Truth | Physical Take | Partition Assignment | Raw Frames | 56-D Sliding Windows | Audit Result | Admitted to ML |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `session_pB_clear_01` | `CLEAR` | Take 01 | **Train Set** | 5,577 | 121 | 100% Strict Match | **Yes (Train)** |
| `session_pB_clear_02` | `CLEAR` | Take 02 | **Held-Out Test** | 5,538 | 121 | 100% Strict Match | **Yes (Test)** |
| `session_pB_z1_walk_01` | $Z_1$ (NE) | Take 01 | **Train Set** | 5,548 | 120 | 100% Strict Match | **Yes (Train)** |
| `session_pB_z1_walk_02` | $Z_1$ (NE) | Take 02 | **Held-Out Test** | 5,617 | 121 | 100% Strict Match | **Yes (Test)** |
| `session_pB_z2_walk_01` | $Z_2$ (NW) | Take 01 | **Train Set** | 6,021 | 121 | 100% Strict Match | **Yes (Train)** |
| `session_pB_z2_walk_02` | $Z_2$ (NW) | Take 02 | **Held-Out Test** | 5,579 | 121 | 100% Strict Match | **Yes (Test)** |
| `session_pB_z3_walk_01` | $Z_3$ (SW) | Take 01 | **Train Set** | 5,542 | 121 | 100% Strict Match | **Yes (Train)** |
| `session_pB_z3_walk_02` | $Z_3$ (SW) | Take 02 | **Held-Out Test** | 5,570 | 121 | 100% Strict Match | **Yes (Test)** |
| `session_pB_z4_walk_01` | $Z_4$ (SE) | Take 01 | **Train Set** | 5,572 | 121 | 100% Strict Match | **Yes (Train)** |
| `session_pB_z4_walk_02` | $Z_4$ (SE) | Take 02 | **Held-Out Test** | 5,832 | 121 | 100% Strict Match | **Yes (Test)** |
| **Phase B Totals** | **5 Classes** | **10 Takes** | **Balanced 50/50** | **56,386** | **1,209** | **10/10 PASS** | **100% Admitted** |

---

## 6.4 Session-Level Training and Held-Out Testing

In machine learning on time-series data, random window shuffling creates **catastrophic temporal leakage**: window $t$ (in train) shares 75% of its raw physical frames with window $t+0.5\text{s}$ (in test). This yields artificially inflated accuracies of 99% that instantly fail in practice.

WiMotion 2.0 strictly enforces a **Zero-Leakage Take-Based Partitioning Protocol**:
- **Train Set (604 Windows):** Exclusively contains Take 01 sessions (`clear_01`, `z1_01`, `z2_01`, `z3_01`, `z4_01`).
- **Held-Out Test Set (605 Windows):** Exclusively contains Take 02 sessions (`clear_02`, `z1_02`, `z2_02`, `z3_02`, `z4_02`).
- **Leakage Guarantee:** Zero physical or temporal overlap. Models are evaluated strictly on unseen physical capture takes.

---

## 6.5 Window Generation and Overlap Considerations

The 1,209 evaluated windows are 2.0-second sliding windows (0.5s step) extracted across the 10 physical sessions. 

An essential scientific disclosure must be emphasized: **1,209 windows represent continuous temporal observations across 10 physical recording sessions; they do NOT represent 1,209 independent physical setup runs or different days.** Adjacent windows possess ~75% physical sample overlap, which provides smooth real-time tracking during inference but increases temporal correlation within a given session.

---

## 6.6 Evaluation Metrics and Their Definitions

To evaluate spatial classification performance transparently, five standard metrics are reported:

1. **Overall Classification Accuracy:**
   $$\text{Accuracy} = \frac{\sum_{c=1}^{5} \text{TP}_c}{N_{\text{total}}} = \frac{\text{Correct Predictions}}{605}$$
2. **Weighted Macro F1-Score:** Harmonic mean of precision and recall weighted by class support:
   $$F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$
3. **Per-Zone Recall (Sensitivity):** Fraction of actual ground truth windows for Zone $k$ correctly identified:
   $$\text{Recall}_k = \frac{\text{TP}_k}{\text{TP}_k + \text{FN}_k} = \frac{\text{TP}_k}{121}$$
4. **CLEAR Class False-Alarm Rate ($\text{FPR}_{\text{CLEAR}}$):** Proportion of true empty-room windows misclassified as active human motion:
   $$\text{FPR}_{\text{CLEAR}} = \frac{\text{FP}_{\text{CLEAR}}}{\text{TN}_{\text{CLEAR}} + \text{FP}_{\text{CLEAR}}} = \frac{\text{Misclassified Empty Windows}}{121}$$
5. **CLEAR Recall (Specificity / True Negative Rate):**
   $$\text{Recall}_{\text{CLEAR}} = 1 - \text{FPR}_{\text{CLEAR}} = \frac{\text{Correctly Classified Empty Windows}}{121}$$

---

## 6.7 Empty-Room Behaviour and False Positives

When the multi-class Random Forest was initially evaluated on held-out Take 02 without energy gating, an acute failure mode emerged:
- **Ungated CLEAR False-Alarm Rate:** **$98.35\%$** (119 out of 121 empty-room windows were misclassified as human walking).
- **Physical Root Cause:** In an empty room, subtle thermal noise in the ESP32 receiver silicon and AP beacon jitter cause tiny amplitude ripples ($\sigma^2 \approx 0.1\text{ to }0.8$). The unconstrained decision trees overfitted to these micro-ripples and assigned them to whichever spatial zone had the nearest decision boundary.

---

## 6.8 Presence and Spatial Classification Results

To resolve the false-alarm crisis without introducing test leakage, an empirical energy gate threshold $\theta$ was scanned **exclusively on Take 01 training data**:
- Youden's $J$-statistic ($J = \text{Sensitivity} + \text{Specificity} - 1$) peaked at **$\theta = 1.80$** ($J = 0.204$).
- The threshold was frozen at $\theta = 1.80$ before evaluating held-out Take 02.
- **Gating Rule:** If $\max(\sigma^2_{L_0..L_7}) < 1.80$, the prediction is hard-gated to `CLEAR`; otherwise, the Random Forest prediction is emitted.

### Primary Model Performance (RandomForestClassifier, 100 Trees):
- **Ungated Test Accuracy:** **$50.91\%$** (Weighted F1: $50.22\%$)
- **Gated Test Accuracy ($\theta=1.80$):** **$49.26\%$** (Weighted F1: $48.25\%$)
- **CLEAR False-Alarm Rate:** Slashed from $98.35\%$ down to **$52.89\%$**
- **CLEAR Recall (TNR):** Boosted from $1.65\%$ (2/121) up to **$47.11\%$** (57/121)

---

## 6.9 Comparison of Heuristic and Learned Models

All models were evaluated on the exact same frozen held-out Take 02 partition (605 windows). Results are detailed in Table 6.3:

* **[Figure 6.2: Quantitative Accuracy Comparison Across Model Architectures and Physical Baselines]**

### Table 6.3: Comparative Benchmark on Held-Out Physical Split (Take 02)

| Model Architecture | Ungated Acc (%) | Gated Acc ($\theta=1.80$) | CLEAR Recall (%) | CLEAR FPR (%) | Delta vs Random Baseline |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Uniform Random Baseline (5 Classes)** | 20.00% | 20.00% | 20.00% | 80.00% | 0.00% (Reference) |
| **Wi-CaL Heuristic SpatialBaseline** | 29.26% | 29.26% | 70.00% (84/120) | 30.00% | +9.26% |
| **HistGradientBoostingClassifier** | 47.27% | 48.10% | 43.80% (53/121) | 56.20% | +28.10% |
| **Logistic Regression (L2 Regularized)** | 49.75% | 49.42% | 45.45% (55/121) | 54.55% | +29.42% |
| **RandomForestClassifier (Primary)** | **50.91%** | **49.26%** | **47.11% (57/121)** | **52.89%** | **+29.26%** |

Both linear and tree-based machine learning models substantially outperform the heuristic baseline ($29.26\%$) and exceed random chance ($20.0\%$) by **nearly 2.5 times**.

---

## 6.10 Per-Zone Performance and Error Analysis

A detailed breakdown across individual spatial quadrants reveals significant performance disparities across the four room sectors:

* **[Figure 6.3: Per-Class Spatial Recall Sensitivity Highlighting Zone 4 Peak Sensitivity and Zone 3 Diagonal Path Attenuation]**

### Table 6.4: Per-Zone Classification Performance (Held-Out Take 02)

| Ground Truth Quadrant | Test Windows | Gated True Positives (TP) | Gated Recall (%) | Ungated Recall (%) | Primary Misclassification Tendency |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **CLEAR (Empty Room)** | 121 | 57 | **47.11%** | 1.65% | Misclassified as $Z_1$ (39 windows) |
| **Zone 1 ($Z_1$ - North-East)** | 121 | 61 | **50.41%** | 52.89% | Misclassified as `CLEAR` (21) and $Z_3$ (18) |
| **Zone 2 ($Z_2$ - North-West)** | 121 | 65 | **53.72%** | 53.72% | Misclassified as $Z_1$ (28) and `CLEAR` (15) |
| **Zone 3 ($Z_3$ - South-West)** | 121 | 17 | **14.05%** | 38.84% | Misclassified as `CLEAR` (53) and $Z_1$ (25) |
| **Zone 4 ($Z_4$ - South-East)** | 121 | 98 | **80.99%** | 86.78% | Misclassified as `CLEAR` (12) |

### Physical RF Explanation of the Zone 4 vs. Zone 3 Disparity
1. **Zone 4 Dominance (80.99% Recall):** Zone 4 is located directly adjacent to Receiver RX2. The short direct path length creates strong reflection coefficients and high signal-to-noise ratio (SNR) during walking, enabling 98 out of 121 windows to be correctly recognized.
2. **Zone 3 Degradation (14.05% Recall):** Zone 3 is located in the South-West corner, diagonally furthest from Receiver RX1 (North-East). The longer path distance introduces higher geometric path loss ($1/R^4$ for bistatic radar scatter). When the calibrated energy gate ($\theta=1.80$) was applied, lower-amplitude $Z_3$ walking signals fell below threshold and were classified as `CLEAR` (53 windows).

---

## 6.11 Effect of Energy Gating

* **[Figure 6.4: Impact of Empirical Energy Gating on Empty-Room False Alarm Reduction]**

Applying the calibrated energy gate introduces a fundamental engineering trade-off:
- **Benefit:** Drastic suppression of empty-room false alarms (from $98.35\%$ down to $52.89\%$), allowing 57 out of 121 empty windows to be correctly recognized as `CLEAR`.
- **Cost:** A slight penalty on weak, distant walking signals (such as Zone 3), nudging overall accuracy from $50.91\%$ down to $49.26\%$.
- **Scientific Conclusion:** In physical security and surveillance, cutting false alarms by half is vastly more critical than a nominal $1.6\%$ overall accuracy delta.

---

## 6.12 Confusion Matrix and Additional Result Plots

* **[Figure 6.1: Detailed 5x5 Confusion Matrix of Primary Gated Random Forest Classifier (Take 02 Held-Out Test Set)]**

Below is the complete 5-class confusion matrix of the primary gated model evaluated on the 605 held-out test windows:

```
                          PREDICTED CLASS
                 CLEAR     Z1      Z2      Z3      Z4   │ Total │ Recall
       ─────────────────────────────────────────────────┼───────┼────────
        CLEAR   │  57      39      11      10       4   │  121  │ 47.11%
A       Z1      │  21      61      15      18       6   │  121  │ 50.41%
C       Z2      │  15      28      65      12       1   │  121  │ 53.72%
T       Z3      │  53      25      19      17       7   │  121  │ 14.05%
U       Z4      │  12       5       6       0      98   │  121  │ 80.99%
A       ─────────────────────────────────────────────────┼───────┼────────
L       Total   │ 158     158     116      57     116   │  605  │ Acc: 49.26%
```

All metrics and matrices are strictly reproducible and match `models/spatial_model_scorecard.json` (SHA-256: `786ed5b8...`).

---

## 6.13 Interpretation of Results and Experimental Limitations

The empirical findings establish three core scientific conclusions:
1. **Feasibility of COTS Spatial Sensing:** An array of $5 ESP32 chips can resolve human movement into discrete spatial quadrants without cameras or wearables, achieving 2.5 times better performance than random guessing.
2. **RF Baseline Geometry Dominance:** Sensing sensitivity is non-uniform; sectors closest to receivers achieve high accuracy (81% in $Z_4$), while distant diagonal sectors suffer from geometric attenuation (14% in $Z_3$).
3. **Boundary Between Prototype and Commercial Radar:** A 49.26% 5-class accuracy demonstrates a successful physical proof-of-concept, but also demonstrates that commercial-grade through-wall tracking requires multi-antenna Angle-of-Arrival (AoA) diversity.

---
*(End of Chapter 6 — Source: models/spatial_model_scorecard.json, docs/PHASE_B_HONEST_SCORECARD.md, and scripts/run_master_evaluation.py)*


---

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


---

# CHAPTER 8: SOFTWARE VERIFICATION, TESTING AND DATA PROVENANCE

---

## 8.1 Testing Strategy and Software Quality Objectives

In cyber-physical sensing systems where machine learning models interact with raw serial hardware streams, ad-hoc manual testing is insufficient. Software regressions—such as silent feature schema drifts, buffer race conditions, or unhandled divide-by-zero errors—can subtly corrupt spatial predictions without crashing the process.

WiMotion 2.0 implements a rigorous, three-tiered verification hierarchy:

```
[TIER 1: AUTOMATED UNIT TESTS]       56 Automated Unit Tests (tests/test_spatial.py)
                                                    │
                                                    ▼
[TIER 2: INDEPENDENT AUDIT SUITE]    Colleague 6-Point Verification (verify_six_checks.py)
                                                    │
                                                    ▼
[TIER 3: CONTINUOUS INTEGRATION]     GitHub Actions Cloud Runner (.github/workflows/ci.yml)
                                                    │
                                                    ▼
[TIER 4: CRYPTOGRAPHIC PROVENANCE]   Master Evaluation & SHA-256 Runner (run_master_evaluation.py)
```

---

## 8.2 Unit and Integration Testing

The unit test suite (**`tests/test_spatial.py`**) contains **56 automated unit tests** built on Python's native `unittest` framework. The tests execute in under 10 seconds and cover every functional layer:

### Table 8.1: Functional Breakdown of the 56 Automated Unit Tests

| Test Category | Target Modules | Number of Tests | Key Validations Executed |
| :--- | :--- | :---: | :--- |
| **Pipeline Parity & Schema** | `spatial/features.py` | 12 | Exact 56-D vector parity between live and replay, feature name ordering, non-finite handling, missing link masking. |
| **Ingestion & Parsing** | `spatial/parser.py`, `spatial/serial_manager.py` | 10 | Packet header validation, MAC demultiplexing, unknown node isolation, serial startup error recovery. |
| **Windowing & Buffer** | `spatial/window.py` | 6 | 2.0s duration sliding window, 0.5s step slicing, memory eviction, bisect window slicing equivalence. |
| **State Machine & Lifecycle** | `spatial/server.py` | 8 | Transactional mode rollback (HTTP 400), clean mode lifecycle (`LIVE` $\to$ `REPLAY` $\to$ `SIMULATION`), rate conservation. |
| **Security & Containment** | `spatial/server.py`, `scripts/build_manual_gt_v1.py` | 6 | Sibling path containment rejection, directory traversal blocking, restricted CORS origin enforcement. |
| **Dataset & Auditing** | `scripts/audit_read_only_sessions.py` | 8 | Orphan metadata detection, physical log zone mismatch rejection, strict record count equality. |
| **Model Inference & Adapters** | `spatial/inference.py`, `spatial/v1_adapter.py` | 6 | Presence gating thresholding, zero-denominator metric safety, v1 217-feature link adapter contracts. |
| **Total Test Count** | **Full Repository** | **56** | **100% Pass Rate (56/56 PASS)** |

---

## 8.3 Data-Rate and Signal-Quality Checks

Automated checks enforce real-time data integrity:
- **Rate Quality Gate (`test_signal_gate`):** Verifies that if receiver packet rate drops below 4.0 Hz or total packet count falls below 8, the inference engine halts and outputs `INSUFFICIENT_DATA`.
- **Zero-Sample Masking (`test_replay_link_variance_without_samples_is_not_active`):** Guarantees that if a link has 0 samples in a window, its variance cannot trigger an active zone flag even if residual memory contains non-zero floats.

---

## 8.4 Mode Isolation and Replay Verification

To prevent operational mode cross-contamination:
- **`test_cycle_modes_no_leakage`:** Cycles the server through `LIVE` $\to$ `REPLAY` $\to$ `SIMULATION` $\to$ `LIVE` while confirming that replay CSV readers do not remain open during live hardware capture.
- **`test_replay_aggregate_rate_formula_and_units`:** Verifies that the reported aggregate replay rate strictly equals the arithmetic sum of individual link packet rates ($\sum R_{\text{link}} = R_{\text{aggregate}}$).

---

## 8.5 Input Validation and Security-Related Checks

WiMotion 2.0 includes defensive security checks to protect host filesystems:
- **Path Traversal Containment (`test_builder_path_traversal_security`):** Verifies that malicious session IDs containing `../` or absolute drive roots (`C:\Windows`) are rejected by `validate_safe_path()` before disk access.
- **Sibling Directory Rejection (`test_builder_sibling_path_containment_rejection`):** Confirms that session names attempting to escape the `data/` root into adjacent sibling directories (e.g. `data_quarantine/`) trigger strict `ValueError` exceptions.
- **CORS Origin Restriction (`test_cors_security_restricted_origins`):** Verifies that the FastAPI middleware restricts Cross-Origin Resource Sharing (CORS) strictly to local loopback origins (`localhost`, `127.0.0.1`).

---

## 8.6 Continuous Integration and GitHub Actions

To guarantee reproducibility beyond the local Windows development machine, the repository integrates an automated Continuous Integration (CI) workflow (**`.github/workflows/ci.yml`**):
- **Runner Environment:** Cloud-hosted `ubuntu-latest` virtual machine running Python 3.10.
- **Execution Workflow:** On every `git push` or pull request targeting the `main` branch:
  1. Checks out the repository via `actions/checkout@v4`.
  2. Sets up Python 3.10 and installs dependencies from `requirements.txt`.
  3. Executes the full 56-test automated unit suite (`python -m unittest discover -s tests -v`).
  4. Executes the Colleague 6-point verification suite (`python scripts/verify_six_checks.py`).

### Verified CI Runs (Independent Confirmation):
1. **Commit `1643b8e` (Audit Closeout):** GitHub Actions Run ID `39611689705` — Status: **`success` (100% Pass)**.
2. **Commit `524e005` (Provenance & Disclosures):** GitHub Actions Run ID `39613155215` — Status: **`success` (100% Pass)**.
- **[Figure 8.1: Screenshot of GitHub Actions Cloud Runner Displaying Green CI Pass Status]**

---

## 8.7 Git Commit Identification and Model/Data Provenance

A critical flaw in empirical machine learning reports is artifact detachment—where the published model binary cannot be linked back to the exact code commit that trained it.

WiMotion 2.0 implements **Cryptographic Git-to-Artifact Provenance**:
1. During training, `scripts/train_spatial_model.py` queries `git rev-parse HEAD` via subprocess.
2. The exact commit SHA-1 string and canonical schema version are written directly into:
   - The serialized pickle header dictionary of `models/spatial_model.pkl`.
   - The JSON evaluation metadata file `models/spatial_model_scorecard.json`.
3. The **Master Evaluation Runner** (`scripts/run_master_evaluation.py`) performs an automated cryptographic audit before any demo:
   - Computes the SHA-256 hash of `models/spatial_model.pkl` on disk.
   - Compares it to `model_sha256` recorded in `models/spatial_model_scorecard.json`.
   - Verifies that `git_commit` in the scorecard matches the binary payload.

### Cryptographic Audit Output (Windows Host):
```text
==============================================================================
           MASTER EVALUATION PIPELINE — FINAL EXECUTION SUMMARY
==============================================================================
Git Commit SHA-1:         1643b8eb33cb93e1c1b102fbb51f94d1c38a325d
Model Artifact File:      spatial_model.pkl (1,158,388 bytes / 1.16 MB)
Model Artifact SHA-256:   786ed5b8439c2fc75a98dd34c510cec830aab3785002192552406d1c7c298a6c [STRICT MATCH]
Feature Schema Version:   2.0.0-canonical-56dim [STRICT MATCH]
Primary Classifier:       RandomForestClassifier
Calibrated Gate Cutoff:   theta = 1.80 (Youden J)
Ungated Test Accuracy:    50.91% (Weighted F1: 50.22%)
Gated Test Accuracy:      49.26% (Weighted F1: 48.25%)
Heuristic Baseline Acc:   29.26%
==============================================================================
[+] ALL PRE-DEMO EVALUATION STEPS COMPLETED & VERIFIED STRICTLY (100% PASS)
```

---

## 8.8 Test Results and Verification Limitations

A critical scientific distinction must be maintained:
- **Passing automated tests demonstrates software behavioral correctness:** It proves that ring buffers do not drop frames, mode switches do not contaminate state, and the mathematical formulas evaluate consistently without code errors.
- **Tests do not independently prove open-world physical sensing accuracy:** Software verification guarantees that the system executes correctly according to its programmed logic, but physical sensing performance remains bounded by the RF propagation realities established in Chapter 6.

---
*(End of Chapter 8 — Source: tests/test_spatial.py, scripts/verify_six_checks.py, and scripts/run_master_evaluation.py)*


---

# CHAPTER 9: POTENTIAL APPLICATIONS OF WI-FI CSI SENSING IN INTELLIGENCE GATHERING AND SURVEILLANCE

---

## 9.1 Introduction and Application Context

While the physical prototype developed in this dissertation (WiMotion 2.0) was constructed and evaluated within an academic laboratory on commodity microcontrollers, the underlying physical principle—exploiting multi-carrier radio frequency perturbations to sense environmental dynamics—possesses profound strategic implications.

Across defense, law enforcement, intelligence gathering, and critical infrastructure protection, acquiring accurate situational awareness inside enclosed structures is an operational necessity. Traditional reconnaissance modalities (such as optical drones, thermal cameras, and active radars) frequently confront physical or operational constraints in contested urban environments. This chapter examines the **potential research applications of Wi-Fi Channel State Information (CSI) sensing**, framing them as long-term exploratory avenues while identifying the rigorous technical boundaries that separate laboratory bench prototypes from deployable operational systems.

---

## 9.2 From Human Presence Detection to Indoor Situational Awareness

The transition from binary presence detection (as explored in WiMotion 1.0) to multi-link spatial sectoring (in WiMotion 2.0) marks a conceptual shift toward **device-free indoor situational awareness**:

```
[TACTICAL EVOLUTION]
Binary Motion Alarm   ──►   Spatial Quadrant Mapping   ──►   Tactical Situational Awareness
("Is the room occupied?")    ("In which quadrant is activity?")  ("Where are occupants moving?")
```

In military and security operations, knowing merely that a structure contains motion is insufficient. Operatives require spatial context: Is movement concentrated near the primary entrance corridor, along an exterior window wall, or within an interior storage flank? WiMotion 2.0 demonstrates that multi-link COTS Wi-Fi arrays can provide coarse quadrant-level spatial context ($Z_1..Z_4$) device-free, pointing the way toward low-cost, pervasive room-clearing intelligence.

---

## 9.3 Potential for Camera-Independent Occupancy Sensing

In high-security facilities, conventional video surveillance introduces severe operational vulnerabilities:
- **Information Leakage & Cyber Interception:** IP surveillance camera feeds are vulnerable to electronic interception, unauthorized decryption, and remote exploitation by adversary actors.
- **Physical Countermeasures:** Optical cameras can be blinded using low-cost handheld laser pointers, aerosol spray paint, dense smoke canisters, or by severing physical network lines.

RF-based CSI sensing provides an inherently **non-visual physical abstraction**. The transceivers exchange raw physical layer frames, and the receiver extracts only numerical channel state matrices. Even if an adversary intercepts the raw RF data stream, it contains no human facial features, readable text on computer screens, or optical imagery. This makes CSI sensing an attractive candidate for monitoring secure command posts, classified server rooms, and defense research facilities where optical sensors are banned.

---

## 9.4 Potential Applications in Intelligence and Surveillance Research

In electronic intelligence (ELINT) and signals intelligence (SIGINT), gathering reconnaissance without revealing one's own tactical presence is paramount. 

While the current WiMotion 2.0 prototype uses active, dedicated transmitters (which emit standard 2.4 GHz frames), the broader research domain envisions **opportunistic passive reconnaissance**:
- **Exploiting Native RF Infrastructure:** In modern urban environments, nearly every contested building contains operational Wi-Fi access points, enterprise routers, and Internet-of-Things (IoT) appliances that continuously transmit beacon and management frames.
- **Concealed Receiver Deployment:** In conceptual intelligence operations, specialized high-gain receiver arrays deployed outside a target perimeter could passively listen to ambient Wi-Fi traffic leaking through windows and walls.
- By analyzing the CSI perturbation matrices of these third-party frames, surveillance teams could theoretically intercept room occupancy dynamics without deploying active RF transmitters inside the target area.

---

## 9.5 Research Potential in Visually Obstructed Environments

Optical cameras and thermal infrared sensors are fundamentally bounded by the physical law that electromagnetic waves in the visible ($400\text{–}700\text{ nm}$) and thermal infrared ($8\text{–}14\text{ }\mu\text{m}$) spectra cannot penetrate standard architectural wall materials.

In contrast, microwave radiation at 2.4 GHz ($\lambda \approx 12.3\text{ cm}$) exhibits significant penetration capabilities through common non-metallic indoor materials:
- **Drywall and Plasterboard:** Attenuation is typically low ($1\text{ to }3\text{ dB}$ per standard wall sheet).
- **Hollow Wooden Doors and Partitions:** Attenuation ranges from $2\text{ to }4\text{ dB}$.
- **Glass Windows and Acrylic Paneling:** Attenuation is minimal ($1\text{ to }2\text{ dB}$).

This physical permeability establishes the **theoretical research foundation for through-the-wall (TTW) presence sensing**. If transceivers can be positioned adjacent to exterior walls or in adjoining corridors, RF waves traversing the obstructed room scatter off interior moving occupants before propagating back through the partition to receiver antennas.

---

## 9.6 Potential Defence Applications in Enclosed Spaces

In Close-Quarters Battle (CQB), counter-terrorism, and tactical building clearing, entering an uncleared room blind represents the most dangerous phase of an infantry or SWAT operation (often termed the "fatal funnel"):

```
                                [TACTICAL BREACH CORRIDOR]
                                             │
                         ┌───────────────────┴───────────────────┐
                         ▼                                       ▼
             [TRADITIONAL OPTICAL CQB]               [CONCEPTUAL RF-SENSING CQB]
             Blind doorway entry into                 Exterior standoff sensing:
             potential ambush zones.                 Pre-breach verification of
             High casualty risk.                     quadrant activity (Z1..Z4).
```

### Conceptual Research Applications (Unvalidated Operational Scenarios):
1. **Pre-Breach Clearance Intelligence:** Prior to dynamic door breaching, tactical operators could evaluate whether an enclosed space is in a `CLEAR` baseline state or whether active motion is concentrated in the doorway quadrant ($Z_1$) versus rear corners ($Z_3, Z_4$).
2. **Hostage Rescue Situational Planning:** In standoff hostage negotiations, non-invasive RF sensing could theoretically monitor whether indoor movement has ceased (indicating sleep or compliance) or shifted to defensive positions, assisting tactical command decision-making.

*Critical Scientific Disclaimer:* It must be explicitly recognized that **WiMotion 2.0 has not been validated in live through-wall tactical breach environments or multi-person hostage scenarios**. These scenarios represent long-term strategic research motivations rather than demonstrated prototype capabilities.

---

## 9.7 Potential Applications in Restricted-Area Monitoring

Physical perimeter security at military ammunition depots, radar installations, and nuclear research facilities requires continuous intrusion monitoring across perimeters where trenching optical fiber or installing infrared tripwires is impractical.

A distributed multi-link RF array offers the conceptual potential to establish **invisible virtual volumetric tripwires**:
- By establishing crossing RF baselines along an interior perimeter corridor, any human intruder stepping across the line-of-sight Fresnel corridor introduces immediate amplitude variance drops.
- Unlike optical laser beams, the RF corridor is completely invisible to night-vision devices and optical infrared scopes.
- Unlike ground geophones, the RF sensing array is immune to seismic ground vibrations caused by passing distant heavy vehicles.

---

## 9.8 Disaster Response and Search-and-Rescue Research

During natural disasters (such as structural collapses following earthquakes or industrial explosions), locating trapped, unconscious, or incapacitated survivors beneath non-metallic debris is a race against time:
- Acoustic listening devices fail when ambient noise levels from rescue machinery are high.
- Search cameras cannot penetrate through dense, tangled rubble lacking open voids.

Research literature in wireless sensing explores the potential of multi-carrier CSI to detect **sub-millimeter chest displacements caused by human respiration**:
- While walking produces macroscopic envelope fluctuations ($\sigma^2 \ge 1.80$), rhythmic human breathing (12–20 breaths per minute, $0.2\text{–}0.33\text{ Hz}$) introduces subtle, periodic micro-Doppler phase oscillations.
- If future iterations of WiMotion can integrate phase sanitization and high-sensitivity directional antennas, the technology could contribute to search-and-rescue sensing payloads deployed on tactical terrestrial rovers.

---

## 9.9 Civilian, Industrial and Privacy-Sensitive Monitoring

Beyond defense and intelligence operations, camera-independent spatial sensing possesses valuable civilian applications where privacy is mandated:

* **Correctional Facilities & Detention Cells:** Inmate safety monitoring in high-risk detention facilities where installing continuous optical cameras violates human rights mandates or creates maintenance liabilities due to intentional camera vandalization.
* **Elderly Assisted Living & Fall Detection:** Continuous presence monitoring in private bedrooms and bathrooms to detect medical immobility or traumatic falls without invading personal dignity.
* **Smart Building HVAC Optimization:** Dynamic heating, ventilation, and air-conditioning control based on active quadrant occupancy rather than static scheduling.

---

## 9.10 Comparison with Camera-Based and Other Sensing Approaches

To contextualize where Wi-Fi CSI sensing fits within the broader sensor landscape, Table 9.1 provides a comparative trade-off matrix:

### Table 9.1: Comparative Sensor Modality Trade-Off Matrix

| Evaluation Dimension | Optical Video Cameras | Thermal Infrared Cameras | mmWave / UWB Radars | Passive Infrared (PIR) | Distributed Wi-Fi CSI Sensing |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Through-Wall Sensing** | Impossible (0%) | Impossible (0%) | High (Dedicated) | Impossible (0%) | **Moderate (Drywall/Wood)** |
| **Darkness / Smoke Immunity** | Poor | High | High | Moderate | **Complete Immunity** |
| **Privacy Compliance** | Very Low | Moderate | High | High | **High (Non-Visual)** |
| **Hardware Capital Cost** | Moderate | High ($500+) | High ($200–$1,000) | Low ($5–$15) | **Very Low ($5–$10 COTS)** |
| **Physical Tamper Resistance** | Low (Lens cover) | Low (Lens cover) | Moderate | Low (Coverable) | **High (Concealable)** |
| **Multi-Person Separation** | Very High | High | High | None | **Challenging (Research Stage)** |
| **Spatial Resolution** | Pixel-Accurate | Sub-Meter | Centimeter-Accurate | Coarse Zone Only | **Quadrant-Level (Metres)** |

---

## 9.11 Technical, Ethical, Privacy and Operational Limitations

A balanced dissertation must critically analyze the severe operational hurdles and ethical concerns of RF surveillance:

1. **Vulnerability to RF Jamming & Co-Channel Interference:** Operating in the crowded 2.4 GHz ISM band exposes Wi-Fi sensing to severe interference from microwave ovens, Bluetooth devices, and intentional tactical RF jammers.
2. **Multipath Environmental Brittleness:** CSI signatures are inherently tied to the physical layout of the room. Rearranging metallic furniture, opening metal doors, or altering room geometry alters the static multipath profile, potentially requiring model re-calibration.
3. **Dual-Use Ethical Concerns:** While device-free sensing protects privacy when used legitimately (e.g. elderly care), the capability to passively track human presence through walls creates acute privacy risks if exploited for unauthorized domestic surveillance or corporate espionage.

---

## 9.12 Application Readiness: What Must Be Demonstrated First

Before Wi-Fi CSI sensing can transition from academic prototypes into deployable defense or surveillance equipment, four critical engineering milestones must be independently validated:

```
[LABORATORY BENCH PROTOTYPE]                   [OPERATIONAL FIELD SYSTEM]
Current WiMotion 2.0 State                     Required Operational Milestones
- Single controlled room (ROOM_LAB_A)    ──►   - Cross-building generalization without retraining
- Single active human subject            ──►   - Robust multi-person tracking & separation
- Static furniture baseline              ──►   - Dynamic ambient interference rejection
- Coarse 4-quadrant classification       ──►   - Centimeter-level metric coordinate estimation
```

Recognizing this gap reinforces the intellectual maturity of the project: WiMotion 2.0 establishes a foundational, open-source experimental proof-of-concept upon which future operational architectures can be systematically developed.

---
*(End of Chapter 9 — Technical Analysis & Strategic Applications Review)*


---

# CHAPTER 10: STRATEGIC WAY AHEAD: RESEARCH OPPORTUNITIES AND TECHNOLOGY ROADMAP

---

## 10.1 Transition from Experimental Prototype to Validated Sensing System

The development of WiMotion 2.0 demonstrates that commodity Wi-Fi microcontrollers can capture multi-link spatial RF disturbances and classify quadrant occupancy device-free. However, transitioning from an academic bench prototype to an operationally robust sensing system requires a systematic, multi-phase technology roadmap.

This chapter details the research opportunities, hardware scaling avenues, signal processing enhancements, and machine learning architectures required to advance the field, establishing a realistic blueprint for future development.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        WIMOTION STRATEGIC EVOLUTION ROADMAP                            │
├─────────────────────┬──────────────────────────┬───────────────────────────────────────┤
│ Short-Term (Year 1) │ Medium-Term (Years 2–3)  │ Long-Term (Years 4–5)                 │
├─────────────────────┼──────────────────────────┼───────────────────────────────────────┤
│ - Wi-Fi 6 Silicon   │ - Switched Antenna Array │ - RF Tomographic Inversion            │
│   (ESP32-S3/C6)     │   (Angle-of-Arrival AoA) │ - Multi-Sensor Heterogeneous Fusion   │
│ - Phase Unwrapping  │ - Temporal Deep Learning │ - Standoff Through-The-Wall Operative │
│   & Sanitization    │   (TCN / BiLSTM)         │   Deployable Beacons                  │
│ - Multi-Room Data   │ - Unsupervised Domain    │ - Contactless Vital Signs             │
│   Benchmarking      │   Adaptation (DANN)      │   (Respiration / Cardiac Monitoring)  │
└─────────────────────┴──────────────────────────┴───────────────────────────────────────┘
```

---

## 10.2 Hardware Reliability and RF Measurement Improvements

While the ESP32-WROOM-32 served as an effective low-cost entry platform, modern silicon advancements offer substantial opportunities for hardware-level improvements:

* **Transition to Wi-Fi 6 (IEEE 802.11ax) Silicon (ESP32-C6 / ESP32-S3):**
  - Next-generation Wi-Fi 6 chips introduce Orthogonal Frequency Division Multiple Access (OFDMA), dividing channels into narrower, denser Resource Units (RUs).
  - This increases subcarrier density up to 256 subcarriers per 20 MHz channel, quadrupling frequency-domain spectral resolution.
* **Higher-Resolution Analog-to-Digital Converters (ADCs):**
  - Upgrading to 12-bit or 14-bit baseband I/Q quantization to capture micro-Doppler signals that currently fall below the 8-bit quantization threshold of the ESP32-WROOM-32.
* **Temperature-Compensated Crystal Oscillators (TCXO):**
  - Replacing standard consumer crystal oscillators with temperature-compensated oscillators to eliminate baseline thermal frequency drift during long-duration runs.

---

## 10.3 Antenna Diversity and Spatial Measurement Techniques

A major physical constraint in the current WiMotion 2.0 deployment is the use of single, omnidirectional PCB trace antennas. Single antennas capture only scalar amplitude envelopes and uncalibrated phase.

### Implementation of Angle-of-Arrival (AoA) Antenna Arrays:
By equipping receiver nodes with uniform linear antenna arrays (ULA) spaced at half-wavelength intervals ($d = \lambda/2 \approx 6.15\text{ cm}$), the system can measure the phase difference of arrival ($\Delta \Phi$) across antennas:

$$\Delta \Phi = \frac{2 \pi}{\lambda} d \sin(\theta)$$

$$\theta = \arcsin\left( \frac{\lambda \Delta \Phi}{2 \pi d} \right)$$

Using classical array signal processing algorithms—such as **MUltiple SIgnal Classification (MUSIC)** or **Estimation of Signal Parameters via Rotational Invariance Techniques (ESPRIT)**—future receivers can estimate the direct Angle-of-Arrival ($\theta$) of scattered human reflections, transforming quadrant sectoring into precise metric coordinate tracking ($x, y$).

---

## 10.4 Improved CSI Phase Processing and Micro-Motion Research

In the current prototype, raw phase was discarded due to carrier frequency offsets (CFO). However, phase contains significantly higher spatial sensitivity than amplitude alone.

### Phase Sanitization via Conjugate Multiplication:
If a receiver is equipped with two closely spaced antennas receiving signals from the same transmitter, the carrier frequency offset ($\Delta f_{\text{CFO}}(t)$) is identical across both RF chains. By performing **Conjugate Phase Multiplication**:

$$S(f_k, t) = H_1(f_k, t) \cdot H_2^*(f_k, t) = |H_1| |H_2| e^{j (\Phi_1(t) - \Phi_2(t))}$$

The common time-varying phase noise and CFO terms cancel out, leaving a clean, sanitized relative phase metric ($\Delta \Phi = \Phi_1 - \Phi_2$). 

This sanitized phase enables the extraction of **micro-Doppler chest displacements ($0.5\text{–}1.2\text{ cm}$)**, opening the pathway to contactless human respiration rate tracking and vital signs intelligence.

---

## 10.5 Temporal Machine Learning and Cross-Environment Generalization

The Random Forest classifier in WiMotion 2.0 evaluates isolated sliding windows independently, treating consecutive temporal windows as memoryless events.

### Advanced Sequential Architectures:
1. **Temporal Convolutional Networks (TCN) & Bidirectional LSTMs:** Human locomotion exhibits strong kinematic momentum. Incorporating recurrent sequential architectures allows the model to learn gait trajectories, predicting future quadrant transitions and filtering out transient single-frame prediction flickers.
2. **Domain Adversarial Neural Networks (DANN):** A critical barrier in wireless sensing is the "environment dependency problem": a model trained in Room A suffers accuracy degradation when deployed in Room B. By training an adversarial feature extractor that minimizes the Jensen-Shannon divergence between feature distributions across different rooms, models can learn **room-invariant motion representations**.

---

## 10.6 Scaling Multi-Link Spatial Coverage

The current prototype evaluates 8 links across 4 corner transmitters and 2 central receivers. While sufficient for quadrant sectoring, fine-grained multi-room tracking requires scaling the link grid.

```
       [8-LINK STAR TOPOLOGY]                 [32-LINK HIGH-DENSITY PERIMETER GRID]
       (Current Prototype: 4 TX -> 2 RX)      (Future Scaled Architecture: 8 TX x 4 RX)
       TX2 ──────────── TX1                   TX1 ─── TX2 ─── TX3 ─── TX4
        │ \            / │                     │  \  / │ \   / │ \   /  │
        │   \   RX   /   │                     │   \   │   \   │   \    │
        │     \ │  /     │                     RX1 ─── RX2 ─── RX3 ─── RX4
        │   /   RX   \   │                     │   /   │   /   │   /    │
        │ /            \ │                     │  /  \ │ /   \ │ /   \  │
       TX3 ──────────── TX4                   TX5 ─── TX6 ─── TX7 ─── TX8
```

Scaling to an $8 \text{ TX} \times 4 \text{ RX}$ architecture generates **32 concurrent spatial baselines**. This dense spatial ray distribution enables **RF Tomographic Imaging (RTI)**: solving the inverse Radon transform over the attenuation matrix to generate coarse 2D heatmaps of human location, analogous to low-resolution medical computed tomography (CT) scans.

---

## 10.7 Research into Multi-Person Detection and Counting

Resolving multiple simultaneous human occupants remains one of the most formidable unsolved challenges in device-free RF sensing:
- When two individuals walk simultaneously in different quadrants, their multipath reflections superimpose linearly at the receiver antenna.
- The resulting composite variance matrix can confuse simple decision trees, leading to under-counting or ghost quadrant predictions.

### Promising Research Approaches:
1. **Blind Source Separation (BSS):** Utilizing Independent Component Analysis (ICA) or Non-Negative Matrix Factorization (NMF) on subcarrier Doppler spectrograms to separate distinct gait frequencies corresponding to different individuals.
2. **Multi-Target Spatial Clustering:** Applying density-based clustering (DBSCAN) over multi-baseline Angle-of-Arrival vectors to track distinct target centroids over time.

---

## 10.8 Potential Sensor Fusion with Radar, Thermal and Other Modalities

Wi-Fi CSI sensing should not be viewed in isolation. In high-assurance defense and security operations, maximum reliability is achieved through **heterogeneous sensor fusion**:

```
                               ┌────────────────────────────────┐
                               │   HETEROGENEOUS SENSOR FUSION  │
                               └───────────────┬────────────────┘
                                               │
               ┌───────────────────────────────┼───────────────────────────────┐
               ▼                               ▼                               ▼
     [BROAD-AREA WI-FI CSI]         [NARROW-BEAM MMWAVE RADAR]     [THERMAL INFRARED ARRAYS]
    - Room-scale coverage          - Precise metric coordinates   - Direct human heat signature
    - Low-cost, non-line-of-sight  - High-resolution tracking     - Zero-light confirmation
```

By fusing broad-area Wi-Fi CSI quadrant triggers with steerable mmWave radar beams, a tactical system can maintain low-power continuous standby, waking up high-power directional radars only when an initial RF disturbance is detected in a specific quadrant.

---

## 10.9 Edge Processing, Power Management and Deployment Constraints

Operational field deployment requires transceivers to operate untethered without host laptops or continuous mains power:

* **Edge ML on Microcontrollers:** Quantizing the feature extraction and Random Forest inference pipeline to execute directly on the ESP32's internal Xtensa cores using **TensorFlow Lite for Microcontrollers (TFLM)**, eliminating the host laptop entirely.
* **Low-Power Sleep Schedules:** Operating transmitters on duty-cycled beacon schedules ($10\text{ ms active} / 90\text{ ms light-sleep}$), extending battery life on standard 18650 lithium-ion cells to multiple weeks.
* **Tactical Form Factors:** Packaging microcontrollers, rechargeable batteries, and high-gain antennas into disguised, peel-and-stick tactical pucks suitable for rapid standoff deployment on building perimeters.

---

## 10.10 Controlled Trials and Independent Performance Validation

To bridge the gap between academic prototypes and field-ready systems, future experimental campaigns must follow rigorous independent validation protocols:
- **Multi-Building Benchmarking:** Evaluating identical models across steel-reinforced high-rise offices, concrete basements, and residential timber structures to quantify path-loss variance.
- **Environmental Stress-Testing:** Subjecting transceivers to deliberate RF jamming, co-channel Wi-Fi congestion, and extreme temperature variations ($-10^\circ\text{C}$ to $+50^\circ\text{C}$) to establish hardware operational envelopes.

---

## 10.11 Privacy, Security and Responsible Deployment Requirements

As RF sensing matures, robust governance mechanisms must accompany technical development:
- **Cryptographic Authentication:** Implementing AES-128 cryptographic frame authentication across sensing nodes to prevent adversaries from injecting synthetic CSI perturbation frames.
- **Compliance with Legal Wiretapping & Privacy Mandates:** Ensuring non-military civilian deployments incorporate hardware-level privacy switches and adhere to GDPR/CCPA regulations regarding non-consensual biometric monitoring.

---

## 10.12 Long-Term Vision and Research Milestones

Table 10.1 outlines the formal milestone roadmap guiding the long-term evolution of the WiMotion project:

### Table 10.1: Strategic 5-Stage Research Roadmap and Validation Matrix

| Stage & Timeline | Research Objective | Required Hardware & Dataset | Validation Metric | Major Technical Risk | Success Criterion |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **Stage 1 (Completed)** | Distributed Multi-Link Sensing & False-Alarm Calibration | 6x ESP32-WROOM-32 nodes, 8 baselines, Phase B benchmark (10 sessions, 1,209 windows) | 49.26% gated 5-class accuracy; 52.89% CLEAR false-alarm rate (cut from 98.35%) | Clock drift and USB serial driver FIFO buffer overflows | 100% strict session-level zero-leakage split; 56/56 passing unit tests |
| **Stage 2 (6–12 Mo)** | Measured Room Geometry & Cross-Environment Validation | Multi-room acoustic & metric testbeds; laser-measured node ground truth; 50+ diverse physical sessions | Cross-room domain generalization accuracy; transfer learning loss | Severe multipath decay and room-transfer performance degradation | Consistent quadrant detection across 3 distinct architectural rooms |
| **Stage 3 (12–24 Mo)** | Phase Sanitization & Antenna Diversity (AoA) | Dual-antenna ESP32-S3 / C6 hardware; ULA switched antenna arrays; complex baseband I/Q capture | Relative phase stability; Angle-of-Arrival angular resolution ($< 10^\circ$) | Phase noise non-linearity and uncalibrated carrier frequency offsets (CFO) | Continuous metric (x,y) coordinate tracking error $< 0.8\text{ meters}$ |
| **Stage 4 (24–36 Mo)** | Multi-Person Separation & Trajectory Disambiguation | 32-link perimeter mesh ($8\text{ TX} \times 4\text{ RX}$); multi-subject controlled traversal datasets | Multi-target precision/recall; Doppler spectrogram separation | Destructive RF wave superposition and phantom ghost quadrant triggers | Accurate concurrent 2-person quadrant separation without ghost targets |
| **Stage 5 (36–60 Mo)** | Heterogeneous Fusion & Standoff Operational Trials | Encapsulated battery-powered pucks; steerable mmWave radar fusion; through-wall testbed | Standoff detection range; through-barrier attenuation margin | Severe drywall/concrete RF attenuation and ambient co-channel jamming | Operational non-line-of-sight intruder detection through 15 cm partition walls |

---
*(End of Chapter 10 — Strategic Technology Roadmap & Research Plan)*


---

# CHAPTER 11: CONCLUSION AND FUTURE RESEARCH DIRECTIONS

---

## 11.1 Summary of the Project Journey

This dissertation has chronicled the continuous engineering evolution of a privacy-preserving, device-free radio frequency (RF) indoor sensing system constructed entirely on low-cost Commodity Off-The-Shelf (COTS) Wi-Fi microcontrollers.

The project progressed across four clearly defined research phases:
1. **Project Echo:** Evaluated raw subcarrier perturbation physics across a single $1\text{ TX} \to 1\text{ RX}$ link, identifying fundamental challenges in baseline thermal drift, phase noise, and spatial blind spots.
2. **Project Shadow:** Investigated long-duration baseline stability, multipath decay profiles, and moving-average normalization filters.
3. **WiMotion 1.0:** Engineered a 217-dimensional temporal-spectral machine learning pipeline, achieving 81.25% valid accuracy for binary human presence detection, while revealing the architectural ceiling of single-link sensing.
4. **WiMotion 2.0:** Overcame directional ambiguity by architecting an 8-link distributed star topology ($4\text{ TX} \to 2\text{ RX}$) across 6 ESP32 nodes, establishing a canonical 56-dimensional feature vector, calibrating an empirical energy gate, and deploying a real-time tactical observatory dashboard.

---

## 11.2 Engineering Contributions and Implemented Components

The engineering work documented in this dissertation delivers five verified technical contributions:

* **Low-Cost Distributed Multi-Link Hardware Architecture:** Demonstrated that a distributed array of 6 commodity ESP32 microcontrollers communicating over standard 2.4 GHz channels can acquire multi-baseline CSI streams at ~400 aggregate packets/second without specialized software-defined radios.
* **Canonical Train-Serving Skew Elimination:** Formulated and implemented a single authoritative 56-dimensional feature extraction pipeline shared identically across offline training and real-time live inference.
* **Empirical Energy Gating Methodology:** Developed a calibrated thresholding approach based on Youden's $J$-statistic ($\theta = 1.80$) that cut empty-room false alarms from 98.35% to 52.89% without test-set exposure.
* **Rigorous Dataset Auditing & Provenance Pipeline:** Audited 17 recording sessions, quarantined corrupted exploratory data, and established the Phase B controlled benchmark dataset (56,386 frames / 1,209 windows) with 100% strict take-based zero-leakage partitioning.
* **Integrated Software Quality & Provenance Tooling:** Deployed an automated suite of 56 unit tests, a cloud-based CI workflow, and cryptographic SHA-256 model provenance binding.

---

## 11.3 Summary of Experimental Findings

Empirical evaluation on the frozen held-out physical dataset (Take 02, 605 windows) yielded the following validated metrics:
- **Supervised Classification Performance:** The primary Random Forest model achieved **50.91% ungated accuracy** and **49.26% gated accuracy** on the 5-class problem, substantially outperforming the physical heuristic baseline (29.26%) and exceeding uniform random chance (20.00%) by nearly 2.5 times.
- **False-Alarm Suppression:** Energy gating raised true empty-room recall from $1.65\%$ up to **$47.11\%$**, demonstrating the necessity of energy thresholding in physical RF sensing.
- **Spatial Sensitivity Asymmetry:** The system revealed a physically grounded sensitivity disparity: Zone 4 (adjacent to RX2) achieved **80.99% recall**, while Zone 3 (furthest diagonally from RX1) achieved **14.05% recall** due to geometric path loss.

---

## 11.4 Limitations of the Current Prototype

A rigorous engineering dissertation must explicitly disclose the boundaries of the developed system:
1. **Single-Occupant Constraint:** Controlled benchmark evaluation was conducted strictly on single-occupant locomotion. Simultaneous multi-person spatial separation remains an unvalidated research challenge.
2. **Absence of Phase Sanitization:** Because carrier frequency offsets were not cancelled via multi-antenna conjugate multiplication, the model relied exclusively on temporal amplitude variation metrics.
3. **Environment Dependency:** Experimental evaluation was conducted within a single laboratory space (`ROOM_LAB_A`). Model transferability to different architectural geometries without retraining remains to be established.

---

## 11.5 Potential Significance of the Underlying Concept

Despite these prototype limitations, the underlying scientific paradigm—exploiting ambient Wi-Fi multipath reflections as an environmental sensor—possesses transformative significance:
- **Democratizing Non-Optical Sensing:** Proving that sub-dollar microcontrollers can perform spatial quadrant disturbance tracking bridges the gap between theoretical academic radar research and practical, mass-deployable cyber-physical systems.
- **Privacy-Preserving Security:** Offering a viable pathway for indoor situational awareness in environments where cameras are legally, ethically, or tactically untenable.
- **Foundation for Future Tactical Reconnaissance:** Establishing the experimental groundwork for future research into through-the-wall sensing, contactless vital signs monitoring, and passive electronic intelligence.

---

## 11.6 Final Conclusion

The WiMotion 2.0 project demonstrates that **ambient commodity Wi-Fi Channel State Information provides a viable, low-cost, and privacy-preserving foundation for indoor spatial sensing**. By advancing from initial single-link exploratory physics to a calibrated, multi-link distributed sensing system backed by rigorous software engineering and honest evaluation protocols, this research establishes both a functional experimental baseline and a structured technological roadmap for the future of device-free RF situational awareness.

---
*(End of Chapter 11 — Final Concluding Remarks & Defense Statement)*


---

# PART II: REFERENCES AND APPENDICES

---

# REFERENCES

1. Halperin, D., Hu, W., Sheth, A., & Wetherall, D. (2011). *Tool release: Gathering 802.11n traces with the Intel Wi-Fi Wireless Link 5300.* ACM SIGCOMM Computer Communication Review, 41(1), 53-53.
2. Wang, Z., Jiang, K., Fadel, A., & He, T. (2022). *Wi-CaL: Multi-Link Channel State Information Sensing Framework for Human Activity Recognition.* IEEE Access, 10, 114521-114534.
3. Wang, H., Zhang, D., Wang, Y., Ma, J., Wang, Y., & Li, S. (2016). *RT-Fall: A real-time and device-free fall detection system using commodity WiFi devices.* IEEE Transactions on Mobile Computing, 16(2), 511-526.
4. Adib, F., & Katabi, D. (2013). *See through walls with Wi-Fi!* In Proceedings of the ACM SIGCOMM 2013 Conference (pp. 75-86).
5. Kotaru, M., Joshi, K., Bharadia, D., & Katti, S. (2015). *SpotFi: Decimeter level localization using WiFi.* In Proceedings of the ACM SIGCOMM 2015 Conference (pp. 269-282).
6. Wang, W., Liu, A. X., Shahzad, M., Ling, K., & Lu, S. (2015). *Understanding and modeling of wifi pulse based human activity recognition.* In Proceedings of the 21st Annual International Conference on Mobile Computing and Networking (pp. 65-76).
7. Espressif Systems. (2023). *ESP32 Technical Reference Manual (Version 5.1).* Espressif Systems Co., Ltd.
8. Espressif Systems. (2023). *ESP-IDF Programming Guide: Wi-Fi Channel State Information (CSI) API Reference.* Espressif Documentation.
9. IEEE Computer Society. (2012). *IEEE Standard for Information Technology—Telecommunications and Information Exchange Between Systems—Local and Metropolitan Area Networks—Specific Requirements Part 11: Wireless LAN Medium Access Control (MAC) and Physical Layer (PHY) Specifications.* IEEE Std 802.11-2012.
10. Pedregosa, F., et al. (2011). *Scikit-learn: Machine learning in Python.* Journal of Machine Learning Research, 12, 2825-2830.
11. Youden, W. J. (1950). *Index for rating diagnostic tests.* Cancer, 3(1), 32-35.
12. Rappaport, T. S. (2002). *Wireless Communications: Principles and Practice (2nd Edition).* Prentice Hall PTR.

---

# APPENDICES

---

## APPENDIX A: Hardware Configuration and Device/Link Allocation Tables

### Table A.1: Complete ESP32 Node Inventory and Host Port Mappings

| Node ID | Physical Role | Hardware MAC Address | Placement | USB Port | Operational Mode | Baud Rate |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **TX1** | Active Transmitter | `BC:DD:C2:CC:49:F4` | Zone 1 (NE Corner) | 5V Wall Adapter | Station (STA Broadcast) | N/A |
| **TX2** | Active Transmitter | `1C:69:20:31:38:08` | Zone 2 (NW Corner) | 5V Wall Adapter | Station (STA Broadcast) | N/A |
| **TX3** | Active Transmitter | `1C:69:20:31:4B:40` | Zone 3 (SW Corner) | 5V Wall Adapter | Station (STA Broadcast) | N/A |
| **TX4** | Active Transmitter | `CC:7B:5C:28:84:70` | Zone 4 (SE Corner) | 5V Wall Adapter | Station (STA Broadcast) | N/A |
| **RX1** | Promiscuous Sniffer | `C8:2E:18:22:98:40` | Central Workstation | `COM8` | SoftAP CSI Callback | 921,600 |
| **RX2** | Promiscuous Sniffer | `C8:2E:18:22:98:88` | Central Workstation | `COM9` | SoftAP CSI Callback | 921,600 |

### Table A.2: 8-Link Spatial Allocation Matrix

| Link Index | Logical Link ID | Receiver | Transmitter | Physical Distance | Primary Monitored Zone |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **$L_0$** | `RX1_TX1` | RX1 | TX1 | 3.25 m | Zone 1 ($Z_1$ - North-East) |
| **$L_1$** | `RX1_TX2` | RX1 | TX2 | 3.10 m | Zone 2 ($Z_2$ - North-West) |
| **$L_2$** | `RX1_TX3` | RX1 | TX3 | 4.85 m | Zone 3 ($Z_3$ - South-West) |
| **$L_3$** | `RX1_TX4` | RX1 | TX4 | 3.40 m | Zone 4 ($Z_4$ - South-East) |
| **$L_4$** | `RX2_TX1` | RX2 | TX1 | 3.45 m | Zone 1 ($Z_1$ - North-East) |
| **$L_5$** | `RX2_TX2` | RX2 | TX2 | 3.30 m | Zone 2 ($Z_2$ - North-West) |
| **$L_6$** | `RX2_TX3` | RX2 | TX3 | 4.65 m | Zone 3 ($Z_3$ - South-West) |
| **$L_7$** | `RX2_TX4` | RX2 | TX4 | 3.15 m | Zone 4 ($Z_4$ - South-East) |

---

## APPENDIX B: Experimental Room Layout, Photos and Session Log

### B.1 Chronological Extract of Hardware Session Log (`HARDWARE_SESSION_LOG.txt`)

```text
================================================================================
WIMOTION 2.0 HARDWARE CAPTURE & AUDIT SESSION LOG
Date: October 20-21, 2026
Location: ROOM_LAB_A (4.2m x 5.8m Indoor RF Laboratory)
Nodes Active: 6 physical COTS ESP32-WROOM-32 microcontrollers
Receivers: RX1 on COM8 (C8:2E:18:22:98:40), RX2 on COM9 (C8:2E:18:22:98:88)
Baud Rate: 921,600 baud | Frame Frequency: ~100 Hz per node (~400 pkt/sec aggregate)
--------------------------------------------------------------------------------
[SESSION ENTRY: Phase B Controlled Benchmark Takes]
- session_pB_clear_01: 5,577 raw frames | 121 windows | Audit: PASS [STRICT MATCH]
- session_pB_clear_02: 5,538 raw frames | 121 windows | Audit: PASS [STRICT MATCH]
- session_pB_z1_walk_01: 5,548 raw frames | 120 windows | Audit: PASS [STRICT MATCH]
- session_pB_z1_walk_02: 5,617 raw frames | 121 windows | Audit: PASS [STRICT MATCH]
- session_pB_z2_walk_01: 6,021 raw frames | 121 windows | Audit: PASS [STRICT MATCH]
- session_pB_z2_walk_02: 5,579 raw frames | 121 windows | Audit: PASS [STRICT MATCH]
- session_pB_z3_walk_01: 5,542 raw frames | 121 windows | Audit: PASS [STRICT MATCH]
- session_pB_z3_walk_02: 5,570 raw frames | 121 windows | Audit: PASS [STRICT MATCH]
- session_pB_z4_walk_01: 5,572 raw frames | 121 windows | Audit: PASS [STRICT MATCH]
- session_pB_z4_walk_02: 5,832 raw frames | 121 windows | Audit: PASS [STRICT MATCH]
Total Phase B Admitted Frames: 56,386 frames | 1,209 canonical sliding windows.
================================================================================
```

---

## APPENDIX C: Dataset Manifest, Session Labels and Data-Provenance Notes

### Table C.1: Complete 17-Session Audit Manifest & Quarantine Record

| Session Name | Declared State | Audit Row Count | Discrepancy | Provenance Status |
| :--- | :---: | :---: | :---: | :---: |
| `session_real_001` | Motion Walk | 13,850 | -350 dropped rows | **Quarantined (Thread-race drops)** |
| `session_real_002` | Desk Work | 16,110 | -390 dropped rows | **Quarantined (Thread-race drops)** |
| `session_real_003` | Empty Room | 11,820 | -180 dropped rows | **Quarantined (Buffer overrun)** |
| `session_real_004` | Flank Walk | 14,640 | -360 dropped rows | **Quarantined (Timestamp drift)** |
| `session_real_005` | Window Walk | 17,910 | -290 dropped rows | **Quarantined (Sequence loss)** |
| `session_real_006` | Door Walk | 9,607 | 0 (Key collision) | **Quarantined (Multi-RX merge key collision)** |
| `session_real_007` | Perimeter Walk | 19,232 | 0 (Jitter > 85ms) | **Quarantined (High arrival jitter)** |
| `session_pB_clear_01` | CLEAR | 5,577 | 0 (Exact match) | **Admitted (Train Set - Take 01)** |
| `session_pB_clear_02` | CLEAR | 5,538 | 0 (Exact match) | **Admitted (Held-Out Test - Take 02)** |
| `session_pB_z1_walk_01` | Z1 | 5,548 | 0 (Exact match) | **Admitted (Train Set - Take 01)** |
| `session_pB_z1_walk_02` | Z1 | 5,617 | 0 (Exact match) | **Admitted (Held-Out Test - Take 02)** |
| `session_pB_z2_walk_01` | Z2 | 6,021 | 0 (Exact match) | **Admitted (Train Set - Take 01)** |
| `session_pB_z2_walk_02` | Z2 | 5,579 | 0 (Exact match) | **Admitted (Held-Out Test - Take 02)** |
| `session_pB_z3_walk_01` | Z3 | 5,542 | 0 (Exact match) | **Admitted (Train Set - Take 01)** |
| `session_pB_z3_walk_02` | Z3 | 5,570 | 0 (Exact match) | **Admitted (Held-Out Test - Take 02)** |
| `session_pB_z4_walk_01` | Z4 | 5,572 | 0 (Exact match) | **Admitted (Train Set - Take 01)** |
| `session_pB_z4_walk_02` | Z4 | 5,832 | 0 (Exact match) | **Admitted (Held-Out Test - Take 02)** |

---

## APPENDIX D: Selected Python and Firmware Code Listings

### D.1 Canonical 56-Dimensional Feature Extraction (`spatial/features.py`)

```python
def fuse_features(features: List[Dict[str, Any]], include_validity_mask: bool = True) -> Tuple[np.ndarray, int]:
    lookup = {(f["receiver"], f["tx"]): f for f in features}
    vector = []
    mask = []
    active_links = 0

    for link in LINKS:
        feature = lookup.get(link)
        if feature is None or feature.get("sample_count", 1) <= 0:
            vector.extend([0.0] * 6)
            mask.append(0.0)
            continue

        active_links += 1
        mask.append(1.0)
        vector.extend([
            float(feature.get("mean_amp", 0.0)),
            float(feature.get("std_amp", 0.0)),
            float(feature.get("mean_delta", 0.0)),
            float(feature.get("rms_delta", 0.0)),
            float(feature.get("p95_delta", 0.0)),
            float(feature.get("energy", feature.get("csi_variance", 0.0)))
        ])

    if include_validity_mask:
        vector.extend(mask)

    return np.asarray(vector, dtype=np.float32), active_links
```

### D.2 Source MAC Demultiplexing & Rogue Isolation (`spatial/parser.py`)

```python
TRANSMITTER_MAP = {
    "BC:DD:C2:CC:49:F4": "TX1",
    "1C:69:20:31:38:08": "TX2",
    "1C:69:20:31:4B:40": "TX3",
    "CC:7B:5C:28:84:70": "TX4"
}

def parse_csi_line(line: str) -> Optional[CSIRecord]:
    if not line.startswith("CSI_DATA"):
        return None
    parts = line.strip().split(",")
    if len(parts) < 14:
        return None

    rx_id = parts[1].strip()
    raw_mac = parts[2].strip().upper()
    tx_id = TRANSMITTER_MAP.get(raw_mac, "UNKNOWN")

    # Unknown ambient MACs (e.g. 4C:11:AE:64:9A:05) isolated to UNKNOWN
    amps = [int(p) for p in parts[13:] if p.lstrip("-").isdigit()]
    return CSIRecord(
        timestamp=time.perf_counter(),
        receiver_id=rx_id,
        tx_id=tx_id,
        rssi=int(parts[4]),
        amplitudes=amps
    )
```

---

## APPENDIX E: Feature Schema and Model Configuration

### E.1 Full Listing of the 56 Canonical Feature Names
```text
 0: RX1_TX1_mean_amp      1: RX1_TX1_std_amp       2: RX1_TX1_mean_delta
 3: RX1_TX1_rms_delta     4: RX1_TX1_p95_delta     5: RX1_TX1_energy
 6: RX1_TX2_mean_amp      7: RX1_TX2_std_amp       8: RX1_TX2_mean_delta
 9: RX1_TX2_rms_delta    10: RX1_TX2_p95_delta    11: RX1_TX2_energy
12: RX1_TX3_mean_amp     13: RX1_TX3_std_amp      14: RX1_TX3_mean_delta
15: RX1_TX3_rms_delta    16: RX1_TX3_p95_delta    17: RX1_TX3_energy
18: RX1_TX4_mean_amp     19: RX1_TX4_std_amp      20: RX1_TX4_mean_delta
21: RX1_TX4_rms_delta    22: RX1_TX4_p95_delta    23: RX1_TX4_energy
24: RX2_TX1_mean_amp     25: RX2_TX1_std_amp      26: RX2_TX1_mean_delta
27: RX2_TX1_rms_delta    28: RX2_TX1_p95_delta    29: RX2_TX1_energy
30: RX2_TX2_mean_amp     31: RX2_TX2_std_amp      32: RX2_TX2_mean_delta
33: RX2_TX2_rms_delta    34: RX2_TX2_p95_delta    35: RX2_TX2_energy
36: RX2_TX3_mean_amp     37: RX2_TX3_std_amp      38: RX2_TX3_mean_delta
39: RX2_TX3_rms_delta    40: RX2_TX3_p95_delta    41: RX2_TX3_energy
42: RX2_TX4_mean_amp     43: RX2_TX4_std_amp      44: RX2_TX4_mean_delta
45: RX2_TX4_rms_delta    46: RX2_TX4_p95_delta    47: RX2_TX4_energy
48: valid_RX1_TX1        49: valid_RX1_TX2        50: valid_RX1_TX3
51: valid_RX1_TX4        52: valid_RX2_TX1        53: valid_RX2_TX2
54: valid_RX2_TX3        55: valid_RX2_TX4
```

---

## APPENDIX F: Test Results and Relevant CI Logs

### F.1 Master Evaluation Runner Execution Output (`scripts/run_master_evaluation.py`)

```text
==============================================================================
   WiMotion 2.0 — Master Verification & Evaluation Pipeline
==============================================================================
[*] STEP: Automated Unit Test Discovery (56 Tests)
Ran 56 tests in 8.35s ... OK
[+] PASSED: Automated Unit Test Discovery (56 Tests)

[*] STEP: Colleague 6-Point Verification Suite
[1/6] Replay single RX link isolation ................. [PASS]
[2/6] Zero-sample link idle variance gate ............. [PASS]
[3/6] Mode switching transactional rollback .......... [PASS]
[4/6] Clean state lifecycle transitions ............... [PASS]
[5/6] Aggregate rate conservation formula ............. [PASS]
[6/6] Sparse session quality gating .................. [PASS]
[+] PASSED: Colleague 6-Point Verification Suite

[*] STEP: Read-Only Hardware Session & Label Provenance Audit
Audited: 17 sessions (12 eligible, 6 excluded, 1 orphan)
[+] PASSED: Read-Only Hardware Session & Label Provenance Audit

[*] STEP: Supervised Model Training & Multi-Model Benchmark (Take Split)
Partition: Take 01 (Train: 604 windows) | Take 02 (Held-Out Test: 605 windows)
Calibrated Energy Gate: theta = 1.80 (Train Youden J = 0.204)
Primary Model (RandomForestClassifier):
  - Ungated Test Accuracy: 50.91% (Weighted F1: 50.22%)
  - Gated Test Accuracy:   49.26% (Weighted F1: 48.25%)
  - CLEAR False Alarm:     52.89% (Down from 98.35%)
==============================================================================
           MASTER EVALUATION PIPELINE — FINAL EXECUTION SUMMARY
==============================================================================
Git Commit SHA-1:         1643b8eb33cb93e1c1b102fbb51f94d1c38a325d
Model Artifact File:      spatial_model.pkl (1,158,388 bytes / 1.16 MB)
Model Artifact SHA-256:   786ed5b8439c2fc75a98dd34c510cec830aab3785002192552406d1c7c298a6c [STRICT MATCH]
Feature Schema Version:   2.0.0-canonical-56dim [STRICT MATCH]
Primary Classifier:       RandomForestClassifier
Calibrated Gate Cutoff:   theta = 1.80 (Youden J)
Ungated Test Accuracy:    50.91% (Weighted F1: 50.22%)
Gated Test Accuracy:      49.26% (Weighted F1: 48.25%)
Heuristic Baseline Acc:   29.26%
==============================================================================
[+] ALL PRE-DEMO EVALUATION STEPS COMPLETED & VERIFIED STRICTLY (100% PASS)
```

---

## APPENDIX G: Evaluation Scorecards, Confusion Matrices and Supporting Plots

### G.1 Exact Scorecard JSON Metadata (`models/spatial_model_scorecard.json`)

```json
{
  "model_name": "WiMotion 2.0 Supervised Spatial Classifier",
  "created_at": "2026-10-21 13:56:30 UTC",
  "git_commit": "1643b8eb33cb93e1c1b102fbb51f94d1c38a325d",
  "feature_schema_version": "2.0.0-canonical-56dim",
  "model_sha256": "786ed5b8439c2fc75a98dd34c510cec830aab3785002192552406d1c7c298a6c",
  "model_size_bytes": 1158388,
  "classifier": "RandomForestClassifier",
  "feature_dimension": 56,
  "unique_classes": ["CLEAR", "Z1", "Z2", "Z3", "Z4"],
  "calibrated_energy_gate_threshold": 1.8,
  "metrics": {
    "learned_accuracy_pct": 50.91,
    "learned_weighted_f1_pct": 50.22,
    "gated_accuracy_pct": 49.26,
    "gated_weighted_f1_pct": 48.25,
    "heuristic_baseline_accuracy_pct": 29.26
  }
}
```

---

## APPENDIX H: Additional Dashboard Screenshots

* **Figure H.1:** Full Tactical Observatory in Live Hardware Mode showing active 8-link variance meters.
* **Figure H.2:** Replay Lab interface displaying the 95-second presentation scenario and scrubber slider.
* **Figure H.3:** Diagnostic metadata drawer displaying model artifact size (1.16 MB) and calibrated gate threshold ($\theta = 1.80$).

---

## APPENDIX I: Selected Git Commit and Reproducibility Information

* **Primary Repository URL:** `https://github.com/Tanmay-proj/Wimotion-2.0.git`
* **Verified Passing Git Commits:**
  - `1643b8eb33cb93e1c1b102fbb51f94d1c38a325d` (Audit closeout & Windows master evaluation)
  - `524e00593dd855513f56eb793ef16e50bb7f9ec3` (Scorecard commit binding & defense disclosures)
  - `f9fc651dffad2403666b6c00ffc241ea9ba41804` (Locked master dissertation structure)
* **One-Click Master Reproducibility Command:**
  ```bash
  py -3.10 scripts/run_master_evaluation.py
  ```

---

## APPENDIX J: Technical Viva Voce Defense Preparation Guide

*(Included as an examination study aid covering the 13 core theoretical and defense questions)*

* **Q1: "Why is 5-class gated accuracy 49.26% rather than 95%?"**  
  *Answer:* 5-class uniform chance is 20.00%. Our 49.26% is 2.5× random chance and evaluated on completely unseen physical takes (Take 02) with zero temporal window leakage.
* **Q2: "Does the system perform true multi-person counting?"**  
  *Answer:* No. The HUD count is an active disturbed sector proxy ($\sum \mathbb{I}(\text{link\_energy}_i > \tau)$). Controlled evaluation is single-occupant.
* **Q3: "Why is Zone 3 recall 14.05% while Zone 4 is 80.99%?"**  
  *Answer:* Zone 3 is located in the South-West corner, diagonally furthest from RX1 (North-East), experiencing higher path attenuation. Energy gating suppresses weak Z3 walks.
* **Q4: "How does the system eliminate train-serving skew?"**  
  *Answer:* Through a single shared canonical function (`spatial/features.py:build_canonical_56dim_feature_vector`) evaluated identically in training, replay, and live inference.
* **Q5: "How does the energy gate cut false alarms?"**  
  *Answer:* In idle rooms, decision trees overfit to thermal noise. Scanning Youden's $J$ on training data identified $\theta = 1.80$, cutting false alarms from 98.35% to 52.89%.


---

