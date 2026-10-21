# WiMotion 2.0 — Final Viva Q&A Guide (Examiner Preparation)

This guide contains the most probable questions examiners will ask during project evaluation, paired with clear, confident, scientifically grounded answers in easy English.

---

### Q1: What is Channel State Information (CSI), and how is it different from RSSI?
**Answer:**
> "RSSI (Received Signal Strength Indicator) is just a single macroscopic scalar value representing overall packet power. It fluctuates violently due to multi-path fading and cannot detect fine-grained movement.  
> CSI (Channel State Information), on the other hand, reveals subcarrier-level channel frequency response across 64 orthogonal OFDM subcarriers (HT20 mode). When a human moves through the Fresnel zones between transceivers, body reflection alters the amplitude and phase of specific subcarriers. This microscopic fingerprint allows us to detect human presence, motion, and spatial sector without wearables or cameras."

---

### Q2: What is the hardware topology of WiMotion 2.0?
**Answer:**
> "Theoretically, WiMotion 2.0 specifies an **8-link distributed sensing mesh** formed by:
> - **Two Receivers (RX1 and RX2)**: ESP32 development boards listening in CSI promiscuous monitor mode at 921,600 baud (`COM3` Master AP, `COM8` Passive Sniffer).
> - **Four Transmitter Beacons (TX1, TX2, TX3, TX4)**: Positioned in four distinct room sectors (TX1=NE/Z1, TX2=NW/Z2, TX3=SW/Z3, TX4=SE/Z4).
> In our **physical laboratory kit**, we currently possess **4 physical COTS ESP32-WROOM-32 microcontrollers** (deployed as 1 Master RX + 3 TX Beacons, or 2 RX + 2 TX). The complete 6-node / 8-link system is our **theoretical system architecture**, fully supported and verified through our software replay and simulation pipeline, while our physical hardware trials were conducted on single-link setups."

---

### Q3: How do you handle your original WiMotion model in WiMotion 2.0? Did you retrain it?
**Answer:**
> "We did **not** retrain or discard the original WiMotion model. The original model (`presence_model.pkl`, HistGradientBoosting, scikit-learn 1.7.2) was trained on 217 temporal-spectral features (Doppler power spectrum, SVD spatial coherence, subcarrier variance) extracted from 1.0-second single-link CSI windows with 94.74% historical cross-validation accuracy.  
> In WiMotion 2.0, because we process multi-link packet streams, we built a dedicated **Link-Level Adapter (`V1PresenceModelAdapter`)**. This adapter groups multi-link packets by `(RX, TX)` pair, extracts the exact 217-feature vector per link, and evaluates presence independently per link before aggregating across the room. We disclose that the original training window was 1.0s while our multi-link live buffer uses 2.0s with 0.5s step."

---

### Q4: In your Replay Lab, is the data real or simulated?
**Answer:**
> "We maintain strict scientific provenance with zero fake data across 5 distinct tracks:
> 1. **Genuine Single-Link Hardware (`held_out_empty_01`, `held_out_walking_01`)**: Real physical ESP32 room captures from WiMotion v1 evaluation trials (RX1-TX1).
> 2. **Generated Benchmark (`benchmark_session_01`)**: A software-generated multi-link CSI benchmark created by mathematical script (`create_benchmark_session.py`) for deterministic multi-link pipeline regression. It is explicitly labeled `synthetic_generated_benchmark`.
> 3. **Unverified Public Import (`public_esp_fi_01`)**: Local sample formatted according to ESP-Fi HAR schema, tagged as `unverified_import` pending external raw dataset verification.
> 4. **Synthetic Augmentation (`synthetic_session_01`)**: Controlled offline transformation with recorded parent session ID and random seed (`synthetic_augmented`).
> 5. **Presentation Scenario (`demo_session`)**: Deterministic 95-second dual-person scenario designed to synchronize with our recorded video demonstration (`scripted_presentation`)."

---

### Q5: What happens if an unmapped transmitter or rogue device transmits on the same channel?
**Answer:**
> "In `spatial/inference.py`, we implement a two-tier transmitter ranking:
> 1. We map transmitters against `tx_zone_map` and rank known and unknown transmitters separately.
> 2. A rogue transmitter with high variance **cannot suppress** a valid mapped transmitter that exceeds the threshold. The valid mapped transmitter is selected as the primary zone.
> 3. If only unmapped transmitters exceed threshold, the primary zone is isolated to `UNKNOWN` and **never** defaulted to Z1, Z2, Z3, or Z4.
> 4. If aggregate packet rate drops below 4.0 Hz or valid packets in a window are under 8, our Signal Quality Gate triggers `INSUFFICIENT_DATA` or `SIGNAL_UNSTABLE`."

---

### Q6: What are the main limitations of the system?
**Answer:**
> "1. **Multi-path interference from static obstacles**: Metallic objects and concrete walls cause static reflections, which we mitigate using median baseline subtraction.
> 2. **LOS vs. NLOS sensitivity**: Non-Line-of-Sight human movement attenuates higher subcarrier frequencies more rapidly.
> 3. **Concurrency and counting limits**: `active_zone_count` reflects distinct active RF sectors exceeding the variance threshold, not a calibrated count of physical individuals. Resolving multiple overlapping targets in the same sector requires Angle-of-Arrival (AoA) antenna arrays, which is our planned future work.
> 4. **Hardware deployment constraint**: Physical hardware trials were performed with single-link captures; the full 6-node 8-link mesh is implemented and verified in software."

---

### Q7: How does your system differentiate between the ML model and the spatial heuristic?
**Answer:**
> "We maintain complete separation of responsibilities:
> 1. **Stage 1 (ML Presence Gating)**: Driven by the original WiMotion model (`HistGradientBoostingClassifier`, 217 features). On untouched held-out physical hardware sessions (109 windows), it achieves **81.25% Valid Accuracy** (88.07% coverage, 71.56% conservative all-window score, 100% recall, 51.35% specificity, 86.76% F1). Buffer warm-up windows are disclosed as invalid.
> 2. **Stage 2 (Spatial Sector Localization)**: Driven by the `SpatialBaseline` heuristic based on Wi-CaL multi-link CSI variance ratio ranking ($argmax$). It determines whether perturbation is in Sector Z1, Z2, Z3, or Z4.
> We never conflate heuristic sector ranking with trained ML classification, and our evaluation suite benchmarks both independently with full confusion matrices."

---

### Q8: What claims are safe to make, and what claims must NOT be made?
**Answer:**
> **SAFE CLAIMS TO DEFEND CONFIDENTLY:**
> - Dual-engine pipeline: ML presence gating (217 features) + multi-link spatial zoning heuristic + 56-dim supervised spatial classifier.
> - 56/56 automated unit tests and 6/6 pre-demo verification checks passing in CI.
> - 81.25% valid accuracy on untouched held-out single-link physical hardware captures (Presence detector).
> - 50.91% accuracy on 5-class held-out physical session takes (Supervised RandomForest classifier), outperforming heuristic baseline (29.26%) and random chance (20.00%). With calibrated energy gating ($\theta = 1.80$), CLEAR false-positive rate is cut from 98.4% to 52.9% (47.1% recall).

> - Deterministic replay lab with timeline scrubbing, rate quality gating, and XSS-safe rendering.
> - Rogue transmitter isolation and suppression resilience (`4C:11:AE:64:9A:05` strictly quarantined to UNKNOWN).
> - Transactional mode isolation (LIVE, REPLAY, SIMULATION).
>
> **CLAIMS YOU MUST NEVER MAKE (SCIENTIFICALLY UNTRUE):**
> - **Historical vs Current Hardware:** Clarify the evolution: early experiments (v1 and initial tests) operated on 2 to 4 boards. On October 20, 2026, a 6-node physical deployment (2 RX + 4 TX) was deployed to record the 10 Phase B sessions (1,209 windows).
> - Do NOT claim `benchmark_session_01` was recorded from physical hardware (it is software-generated).
> - Do NOT claim `active_zone_count` is a calibrated count of physical people (it is active RF perturbation sectors).
> - Do NOT claim 94.74% accuracy was measured on the multi-link system (that was historical 5-fold CV on single-link v1 data).

