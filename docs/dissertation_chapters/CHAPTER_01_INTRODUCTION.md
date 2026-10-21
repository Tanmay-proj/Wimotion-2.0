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
2. **Phase 2: "Project Shadow" (Multipath Fading & Baseline Drift Investigations):**
   * Investigated environmental baseline drift caused by thermal expansion in ESP32 silicon over extended runtimes.
   * Analyzed static multipath profiles and established early moving-average normalization filters.
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
