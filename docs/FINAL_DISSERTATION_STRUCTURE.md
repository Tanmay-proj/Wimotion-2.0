# Final Master Dissertation Structure & Writing Blueprint
## Title: Design, Implementation and Empirical Evaluation of a Multi-Link Wi-Fi CSI Sensing System for Indoor Spatial Disturbance Tracking

---

## 🏛️ PART I — FRONT MATTER (Indicative Pages: i – x)

- **1. Cover Page / Title Page:** University-prescribed format (Project Title, Author: Tanmay Mugale, Supervisor, Department, Institution, Month/Year).
- **2. Certificate of Approval:** Official certificate signed by Project Supervisor / Guide and Head of Department (HOD).
- **3. Student Declaration:** Formal declaration of original work, acknowledging academic integrity and citations.
- **4. Acknowledgements:** Formal expression of gratitude to mentors, laboratory technical staff, peers, and institution.
- **5. Abstract:** Self-contained summary (250–300 words) summarizing the background, methodology (6 ESP32 nodes, 8 links), experimental findings (49.26% gated 5-class accuracy, energy gating impact), and research roadmap.
- **6. Keywords:** `Wi-Fi Sensing`, `Channel State Information (CSI)`, `Human Presence Detection`, `Spatial Sensing`, `ESP32`, `RF Signal Processing`, `Machine Learning`.
- **7. Table of Contents:** Automatically generated heading hierarchy from Word / LaTeX.
- **8. List of Figures:** Enumerated list of all diagrams, hardware photographs, screenshots, and plots with page numbers.
- **9. List of Tables:** Enumerated list of all comparative benchmark tables, configuration matrices, and session audit manifests.
- **10. List of Abbreviations and Acronyms:** CSI, CFR, RSSI, OFDM, COTS, NLOS, LOS, DWT, MAC, AP, STA, PRR, SNR, FPR, TPR.

---

## 📖 CHAPTER 1 — INTRODUCTION AND PROJECT MOTIVATION (Approx. 8–10 Pages)

* **1.1 Background and Motivation**
  * Need for ubiquitous indoor situational awareness in residential, commercial, and sensitive environments.
  * The growing ubiquity of 2.4 GHz IEEE 802.11 Wi-Fi signals in everyday infrastructure.
* **1.2 Limitations of Conventional Visual Monitoring**
  * Line-of-sight constraints, failure in zero-light, smoke, or physical occlusions.
  * Privacy, ethical, and regulatory barriers in private dwellings, restrooms, and clinical facilities.
* **1.3 Introduction to Wi-Fi-Based Device-Free Sensing**
  * The paradigm of opportunistic RF sensing: Humans as dynamic dielectric reflectors without carrying wearable devices or smartphones.
* **1.4 Project Evolution: Echo, Shadow, WiMotion and WiMotion 2.0**
  * *Project Echo:* Initial proof-of-concept exploring raw subcarrier amplitude perturbations on single link.
  * *Project Shadow:* Preliminary multipath shadowing and baseline stability investigations.
  * *WiMotion 1.0:* 217-feature temporal-spectral machine learning pipeline for binary presence classification.
  * *WiMotion 2.0:* Distributed 8-link star topology ($4\text{ TX} \to 2\text{ RX}$) enabling 4-quadrant spatial localization.
* **1.5 Problem Statement**
  * Mitigating environmental drift, multipath ambiguity, and single-link blind spots using low-cost commodity microcontrollers.
* **1.6 Aim and Objectives**
  * Concrete engineering objectives: firmware deployment, multi-threaded serial ingestion, canonical feature extraction, calibrated false-alarm gating, and real-time visualization.
* **1.7 Scope and Boundary Conditions**
  * Controlled single-occupant indoor laboratory experiments.
  * Explicit demarcation: RF channel disturbance classification, not biometric human imaging or tracking.
* **1.8 Expected Contribution of the Project**
  * Low-cost COTS architecture, verified zero-leakage evaluation methodology, open reproducible toolchain.
* **1.9 Organization of the Dissertation**
  * Brief chapter-by-chapter roadmap of the report.

---

## 📡 CHAPTER 2 — THEORETICAL FOUNDATIONS OF WI-FI CSI SENSING (Approx. 9–11 Pages)

* **2.1 Fundamentals of Wireless Signal Propagation**
  * Free-space path loss, Friis transmission formula, and indoor multipath reflection mechanisms.
* **2.2 Reflection, Diffraction, Absorption and Multipath Effects**
  * Interaction of 2.4 GHz electromagnetic radiation with human tissue, building materials, and furniture.
* **2.3 RSSI Versus Channel State Information**
  * RSSI as a macroscopic, packet-averaged scalar prone to multi-path fading.
  * Channel State Information (CSI) as a fine-grained physical layer metric across subcarriers.
* **2.4 CSI as a Complex Channel Frequency Response**
  * Mathematical formulation of the complex CFR across subcarriers:
    $$H(f, t) = \sum_{i=1}^{N} a_i(t) e^{-j \phi_i(t)}$$
  * Decomposition into amplitude response $|H(f,t)|$ and phase response $\angle H(f,t)$.
* **2.5 OFDM and Wi-Fi Subcarrier Structure**
  * 802.11n 20 MHz channel allocation (64 subcarriers on ESP32 PHY: data, pilot, and null guard carriers).
* **2.6 Human-Induced Changes in Wireless Channels**
  * Dynamic multipath ray modulation caused by chest movement (breathing) and body locomotion (walking).
* **2.7 Fresnel Zones and Link Sensitivity**
  * 3D Fresnel ellipsoids defined between transceivers; constructive and destructive interference boundaries.
* **2.8 Multi-Link Spatial Diversity**
  * Spatial coverage expansion: Why intersecting cross-links resolve orthogonal directional ambiguity.
* **2.9 Limitations of CSI-Based Interpretation**
  * Phase noise, carrier frequency offset (CFO), local oscillator drift, and spatial ambiguity in complex rooms.

---

## 🛠️ CHAPTER 3 — HARDWARE ARCHITECTURE AND EXPERIMENTAL DEPLOYMENT (Approx. 9–11 Pages)

* **3.1 System Requirements and Hardware Selection**
  * Rationale for selecting low-cost COTS ESP32 silicon over expensive USRP / SDR platforms.
* **3.2 ESP32-WROOM-32 and Supporting Components**
  * Specifications: Dual Xtensa LX6 cores @ 240 MHz, 2.4 GHz Wi-Fi transceiver, CP2102 USB-to-UART bridge.
* **3.3 Transmitter and Receiver Roles**
  * TX nodes: Fixed station broadcast mode emitting frames at ~100 Hz.
  * RX nodes: Centralized promiscuous access points collecting CSI callbacks.
* **3.4 Six-Node Architecture: Four Transmitters and Two Receivers**
  * Clarification: A distributed multi-link star topology ($4 \text{ TX} \to 2 \text{ RX}$), avoiding the informal term "mesh".
* **3.5 Physical Link Allocation and Eight-Link Matrix**
  * Tabulation of all 8 logical links ($L_0$ to $L_7$) with transmitter MACs, receiver ports, and quadrant assignments.
* **3.6 Experimental Room and Zone Layout**
  * Geometry of `ROOM_LAB_A` (4.2m $\times$ 5.8m); quadrant definitions ($Z_1$ NE, $Z_2$ NW, $Z_3$ SW, $Z_4$ SE).
* **3.7 Firmware Configuration and Communication Parameters**
  * Baud rate (921,600 baud), packet broadcast rate (~100 Hz), channel configuration (Channel 6, 2.437 GHz).
* **3.8 Power, USB and Serial-Connection Management**
  * Isolated 5V USB wall adapters for TX nodes; dual USB 3.0 host connections (`COM8` and `COM9`) for receivers.
* **3.9 Hardware Photographs and Deployment Record**
  * Annotated photographs of laboratory setup, corner-mounted TX nodes, and receiver host workstation.

---

## ⚡ CHAPTER 4 — CSI DATA ACQUISITION AND SOFTWARE INGESTION PIPELINE (Approx. 8–10 Pages)

* **4.1 Software Architecture and Data Flow**
  * End-to-end architecture from raw serial streams to sliding window buffers and WebSocket emitters.
* **4.2 CSI Acquisition at the Receiver**
  * Low-level ESP-IDF CSI sniffer registration (`esp_wifi_set_csi_rx_cb`) and memory buffer handling.
* **4.3 Serial Communication and Asynchronous Ingestion**
  * High-throughput multi-threaded serial workers (`spatial/serial_manager.py`) with lock-protected ring buffers.
* **4.4 Packet Parsing and CSI Data Extraction**
  * Frame header validation (`CSI_DATA`), RSSI extraction, noise floor registers, and signed 8-bit I/Q unpacking.
* **4.5 Transmitter Identification Using MAC Addresses**
  * Packet-level factory MAC whitelisting mapping raw frames to logical nodes (`TX1..TX4`).
* **4.6 Unknown-Node Filtering and Link Validation**
  * Isolation of ambient third-party AP beacons (`4C:11:AE:64:9A:05`) to `UNKNOWN` quarantine bucket.
* **4.7 Buffer Management, Timestamping and Data Integrity**
  * Monotonic microsecond timestamping (`time.perf_counter()`), frame order verification, and overflow prevention.
* **4.8 Error Handling and Software Safeguards**
  * USB disconnection recovery, framing error suppression, and non-blocking timeout handling.
* **4.9 Data Acquisition Challenges and Solutions**
  * Resolution of Windows USB-UART driver latency and thread-safety race conditions.

---

## 🧬 CHAPTER 5 — FEATURE ENGINEERING AND MACHINE LEARNING PIPELINE (Approx. 8–10 Pages)

* **5.1 Overview of the Processing Pipeline**
  * Structured flow: Raw packets $\to$ Subcarrier cleaning $\to$ Link extraction $\to$ Feature fusion $\to$ Model inference.
* **5.2 CSI Preprocessing and Signal-Quality Assessment**
  * Removal of non-finite/corrupt amplitudes; subcarrier index filtering.
* **5.3 Temporal Sliding Windows**
  * Window duration (2.0s) and step size (0.5s) parameters; trade-off between latency and statistical stability.
* **5.4 Mathematical Formulation of the 56-Dimensional Feature Vector**
  * Accurate classification: 48 continuous temporal variation statistics (6 metrics $\times$ 8 links) + 8 binary validity flags.
  * Precise metric definitions: Mean amplitude ($\mu$), Standard deviation ($\sigma$), Mean absolute first difference ($|\Delta a|$), Root-mean-square delta ($\text{RMS}_{\Delta}$), 95th percentile delta ($P_{95}$), and Mean squared temporal variance (Energy).
  * *Correction note:* Explicitly labeled as temporal variation metrics, avoiding unvalidated physical "Doppler" claims.
* **5.5 Link-Validity Flags and Missing-Data Handling**
  * Active link masking (1.0 vs 0.0); zero-imputation policy for momentary packet dropouts.
* **5.6 Training and Inference Pipeline Consistency**
  * Canonical function (`build_canonical_56dim_feature_vector`) eliminating train-serving skew.
* **5.7 Random Forest Classification**
  * Supervised multi-class ensemble (100 estimators, Gini impurity, max depth constraints).
* **5.8 Heuristic Spatial Estimation**
  * Baseline spatial localization using maximum normalized multi-link variance ratio ($argmax$).
* **5.9 Presence Gating and Prediction Quality Controls**
  * Signal-rate thresholding (minimum 4.0 Hz rate per receiver, minimum 8 packets).
* **5.10 Limitations of the Current Feature Representation**
  * Lack of phase sanitization; sensitivity to non-human environmental perturbations (doors, curtains).

---

## 🧪 CHAPTER 6 — DATASET, EXPERIMENTAL METHODOLOGY AND RESULTS (Approx. 12–15 Pages)
*(Core Scientific Evaluation Chapter)*

* **6.1 Dataset Sources and Session Inventory**
  * Overview of all physical recording campaigns: historical exploratory trials and controlled Phase B sessions.
* **6.2 Historical Dataset Audit and Data Quarantine**
  * Systematic audit of 116,588 frames across Sessions 001–007 (`docs/DATASET_AUDIT_REPORT.md`).
  * Discovery of thread-race drops and key collisions; formal quarantine from supervised model training.
* **6.3 Physical Hardware Data-Collection Campaign**
  * Protocol for Phase B in `ROOM_LAB_A`: 10 physical capture takes, 56,386 frames, 1,209 sliding windows.
* **6.4 Session-Level Training and Held-Out Testing**
  * Zero-leakage protocol: Take 01 sessions (604 windows) for training; Take 02 sessions (605 windows) held out for testing.
* **6.5 Window Generation and Overlap Considerations**
  * Explicit disclosure: 1,209 windows represent temporally sliced observations of 10 physical sessions (~75% overlap between adjacent windows), not 1,209 independent physical days.
* **6.6 Evaluation Metrics and Their Definitions**
  * Mathematical definitions: 5-class classification accuracy, macro/weighted F1-score, per-class sensitivity (recall).
  * Definition of CLEAR false-alarm rate ($\text{FPR}_{\text{CLEAR}} = \text{FP} / (\text{FP} + \text{TN})$ on empty-room ground truth).
* **6.7 Empty-Room Behaviour and False Positives**
  * Failure analysis of ungated classification: 98.35% false-alarm rate in idle rooms due to thermal noise overfitting.
* **6.8 Presence and Spatial Classification Results**
  * Primary Random Forest model performance on held-out Take 02: **50.91% ungated accuracy**, **49.26% gated accuracy**.
* **6.9 Comparison of Heuristic and Learned Models**
  * Benchmark comparison: Uniform Random Chance (20.0%), Heuristic Baseline (29.26%), Logistic Regression (49.42%), HistGradientBoosting (48.10%), RandomForest (49.26%).
* **6.10 Per-Zone Performance and Error Analysis**
  * Detailed recall breakdown: Zone 4 = **80.99%** (98/121), Zone 2 = **53.72%** (65/121), Zone 1 = **50.41%** (61/121), Zone 3 = **14.05%** (17/121).
  * RF physical analysis: Long diagonal baseline attenuation causing Zone 3 signal drops vs. Zone 4 proximity to RX2.
* **6.11 Effect of Energy Gating**
  * Scan of Youden's $J$-statistic on Take 01 training data; optimal cutoff frozen at $\theta = 1.80$.
  * Quantitative impact: Suppressing CLEAR false-alarm rate from 98.35% down to **52.89%** (raising CLEAR recall from 1.65% to **47.11%**).
* **6.12 Confusion Matrix and Additional Result Plots**
  * Full 5-class confusion matrix of the gated primary classifier evaluated on the 605 held-out test windows.
* **6.13 Interpretation of Results and Experimental Limitations**
  * Honest engineering summary: Reliable single-occupant sector differentiation vs. challenging multi-zone ambiguity.

---

## 🖥️ CHAPTER 7 — REAL-TIME DASHBOARD, VISUALIZATION AND REPLAY SYSTEM (Approx. 8–10 Pages)

* **7.1 Dashboard Architecture**
  * Real-time web stack: FastAPI backend, HTML5/Vanilla CSS frontend, and WebSocket bidirectional telemetry.
* **7.2 Backend, WebSocket Communication and Front-End**
  * 10 Hz state serialization broadcasting valid CSI packet rates, link variance metrics, and classification results.
* **7.3 Live Hardware Monitoring Interface**
  * Metric cards displaying aggregate CSI rate, active link health (0/8 to 8/8), and serial port status (`COM8`/`COM9`).
* **7.4 Four-Quadrant Spatial Visualization**
  * Polar coordinate 2D radar sweep displaying energy concentration across quadrants $Z_1$ to $Z_4$.
* **7.5 Three-Dimensional Room Visualization**
  * Three.js WebGL perspective room model rendering physical node positions and dynamic target disturbance markers.
* **7.6 Heuristic and Machine-Learning Outputs**
  * Dual-Engine HUD: Simultaneous display of Heuristic Baseline and Supervised Random Forest predictions for transparency.
* **7.7 Active-Sector Indicators Versus Actual People Counting**
  * Explicit disclosure: HUD count is an active disturbed sector proxy ($\sum \mathbb{I}(\text{link\_energy}_i > \tau)$), not ground-truth biometric multi-person counting.
* **7.8 Recorded-Session Replay and Timeline Controls**
  * Replay Lab functionality: millisecond-accurate playback, scrub slider, and playback speed adjustment.
* **7.9 Live, Replay and Simulation Mode Separation**
  * Transactional state machine enforcing strict lifecycle isolation (`LIVE` $\to$ `REPLAY` $\to$ `SIMULATION`).
* **7.10 Dashboard Demonstration and Known Limitations**
  * Evaluation walkthrough and UI rendering latency considerations.

---

## 🛡️ CHAPTER 8 — SOFTWARE VERIFICATION, TESTING AND DATA PROVENANCE (Approx. 6–8 Pages)

* **8.1 Testing Strategy and Software Quality Objectives**
  * Automated testing philosophy: Preventing train-serving skew, mode contamination, and numerical errors.
* **8.2 Unit and Integration Testing**
  * Comprehensive suite of **56 automated unit tests** (`tests/test_spatial.py`) passing with 100% success rate.
* **8.3 Data-Rate and Signal-Quality Checks**
  * Automated tests verifying minimum 4.0 Hz rate thresholding and zero-sample link masking.
* **8.4 Mode Isolation and Replay Verification**
  * Testing transactional error rollback on invalid HTTP mode requests.
* **8.5 Input Validation and Security-Related Checks**
  * Verification of path traversal blocking (`test_builder_path_traversal_security`) and restricted CORS origins.
* **8.6 Continuous Integration and GitHub Actions**
  * Automated CI pipeline (`.github/workflows/ci.yml`) running on Ubuntu runners; verified green passes for commits `1643b8e` and `524e005`.
* **8.7 Git Commit Identification and Model/Data Provenance**
  * Embedding `git rev-parse HEAD` and canonical schema version into binary pickle dictionaries and JSON scorecards.
  * Master evaluation runner (`scripts/run_master_evaluation.py`) enforcing exact cryptographic SHA-256 matching.
* **8.8 Test Results and Verification Limitations**
  * Distinguishing software behavior verification from open-world physical generalization.

---

## 🎖️ CHAPTER 9 — POTENTIAL APPLICATIONS OF WI-FI CSI SENSING IN INTELLIGENCE GATHERING AND SURVEILLANCE (Approx. 10–12 Pages)
*(Strategic Application Chapter — Explicitly Framed as Research Potential)*

* **9.1 Introduction and Application Context**
  * The emerging role of RF-based sensing in modern defense, law enforcement, and physical security.
* **9.2 From Human Presence Detection to Indoor Situational Awareness**
  * The transition from coarse motion alarms to directional quadrant occupancy mapping.
* **9.3 Potential for Camera-Independent Occupancy Sensing**
  * Investigating non-optical sensing in environments where video cameras are legally or operationally restricted.
* **9.4 Potential Applications in Intelligence and Surveillance Research**
  * Strategic concepts in electronic intelligence (ELINT / SIGINT): Eavesdropping on ambient environmental perturbations.
* **9.5 Research Potential in Visually Obstructed Environments**
  * Theoretical analysis of radio wave penetration through drywall, hollow brick, and non-metallic interior partitions.
* **9.6 Potential Defence Applications in Enclosed Spaces**
  * Conceptual applications in pre-breach room clearing, tactical building reconnaissance, and hostage rescue planning.
  * *Important boundary:* Acknowledged as an unvalidated distant research scenario, not a current capability.
* **9.7 Potential Applications in Restricted-Area Monitoring**
  * Invisible virtual tripwire concepts for perimeter corridors, munitions storage, and critical server facilities.
* **9.8 Disaster Response and Search-and-Rescue Research**
  * Investigating potential applicability for locating trapped survivors under lightweight debris via dynamic multipath changes.
* **9.9 Civilian, Industrial and Privacy-Sensitive Monitoring**
  * Hospital patient monitoring, elderly fall detection, and smart facility management.
* **9.10 Comparison with Camera-Based and Other Sensing Approaches**
  * Comparative trade-off matrix: Optical vs Thermal vs PIR vs mmWave Radar vs Passive Wi-Fi CSI.
* **9.11 Technical, Ethical, Privacy and Operational Limitations**
  * Legal implications of covert RF eavesdropping; vulnerability to intentional RF jamming and spoofing.
* **9.12 Application Readiness: What Must Be Demonstrated First**
  * Concrete engineering criteria required before prototype concepts can be deployed in operational environments.

---

## 🚀 CHAPTER 10 — STRATEGIC WAY AHEAD: RESEARCH OPPORTUNITIES AND TECHNOLOGY ROADMAP (Approx. 10–12 Pages)
*(Long-Term Vision & Technology Roadmap)*

* **10.1 Transition from Experimental Prototype to Validated Sensing System**
  * Milestones required to evolve from a benchtop university prototype into a hardened edge device.
* **10.2 Hardware Reliability and RF Measurement Improvements**
  * Evaluating modern Wi-Fi 6 (802.11ax) silicon (ESP32-C6 / ESP32-S3) with higher ADC resolution and OFDMA subcarriers.
* **10.3 Antenna Diversity and Spatial Measurement Techniques**
  * Transitioning from omnidirectional antennas to switched directional arrays for physical Angle-of-Arrival (AoA) estimation.
* **10.4 Improved CSI Phase Processing and Micro-Motion Research**
  * Implementing linear phase unwrapping and conjugate phase multiplication ($H_1 \cdot H_2^*$) for respiration detection.
* **10.5 Temporal Machine Learning and Cross-Environment Generalization**
  * Shifting from window-averaged Random Forests to Temporal Convolutional Networks (TCN) and Bidirectional LSTMs.
  * Domain adaptation techniques (adversarial domain training) to transfer models across different rooms without retraining.
* **10.6 Scaling Multi-Link Spatial Coverage**
  * Architectural scaling from 8 links ($4\text{ TX} \times 2\text{ RX}$) to a 32-link perimeter array ($8\text{ TX} \times 4\text{ RX}$).
* **10.7 Research into Multi-Person Detection and Counting**
  * Signal decomposition challenges: Blind source separation (ICA) and deep spatial clustering for multi-occupant tracking.
* **10.8 Potential Sensor Fusion with Radar, Thermal and Other Modalities**
  * Complementary fusion: Combining broad-area Wi-Fi CSI coverage with narrow-beam mmWave radar verification.
* **10.9 Edge Processing, Power Management and Deployment Constraints**
  * Optimizing neural inference directly on edge microcontrollers (TensorFlow Lite for Microcontrollers); battery operation.
* **10.10 Controlled Trials and Independent Performance Validation**
  * Developing standardized benchmarking protocols across diverse physical structures (concrete, brick, steel-reinforced).
* **10.11 Privacy, Security and Responsible Deployment Requirements**
  * Implementing cryptographic authentication across transceivers to prevent rogue node injection.
* **10.12 Long-Term Vision and Research Milestones**
  * 1-year, 3-year, and 5-year technology evolution roadmap.

---

## 🏁 CHAPTER 11 — CONCLUSION AND FUTURE RESEARCH DIRECTIONS (Approx. 4–5 Pages)

* **11.1 Summary of the Project Journey**
  * Synthesis of the continuous research path from Project Echo to WiMotion 2.0.
* **11.2 Engineering Contributions and Implemented Components**
  * Functional multi-link COTS testbed, zero train-serving skew pipeline, calibrated energy gate, and 3D digital twin.
* **11.3 Summary of Experimental Findings**
  * Verified 49.26% 5-class gated accuracy, 52.89% false alarm reduction, and physical explanation of Zone 3 vs Zone 4 recall.
* **11.4 Limitations of the Current Prototype**
  * Single-occupant constraint, multipath baseline sensitivity, and single-room evaluation boundary.
* **11.5 Potential Significance of the Underlying Concept**
  * Affirmation of COTS Wi-Fi as a viable, low-cost paradigm for non-intrusive spatial awareness.
* **11.6 Final Conclusion**
  * Concluding thesis defense statement.

---

## 📚 PART II — REFERENCES AND APPENDICES (Approx. 15–20 Pages)

### References
* Academic literature on Wi-Fi CSI sensing (Wi-CaL, WiTrack, CARM, SpotFi).
* IEEE 802.11n/ac physical layer standards and Espressif ESP-IDF technical manuals.
* Signal processing, machine learning, and RF propagation foundational textbooks.

### Appendices
* **Appendix A: Hardware Configuration and Device/Link Allocation Tables**
  * Complete node MAC mapping, COM port baud rates, and serial configuration JSON.
* **Appendix B: Experimental Room Layout, Photos and Session Log**
  * Detailed dimensioned floorplan diagrams and full chronological capture log extracts.
* **Appendix C: Dataset Manifest, Session Labels and Data-Provenance Notes**
  * Tabulated breakdown of all 17 audited sessions and the 10 Phase B benchmark takes.
* **Appendix D: Selected Python and Firmware Code Listings**
  * Annotated source excerpts: `spatial/features.py`, `spatial/parser.py`, `scripts/train_spatial_model.py`.
* **Appendix E: Feature Schema and Model Configuration**
  * Full listing of all 56 feature names, schema versioning metadata, and Random Forest hyperparameters.
* **Appendix F: Test Results and Relevant CI Logs**
  * Full console logs of the 56 passing unit tests and GitHub Actions run confirmation.
* **Appendix G: Evaluation Scorecards, Confusion Matrices and Supporting Plots**
  * Complete output of `spatial_model_scorecard.json` and Youden's $J$ threshold sweep curves.
* **Appendix H: Additional Dashboard Screenshots**
  * High-resolution captures of Overview, Replay Lab, Diagnostic Pane, and Telemetry matrix.
* **Appendix I: Selected Git Commit and Reproducibility Information**
  * Repository structure, commit lineage (`1643b8e`, `524e005`), and one-click reproduction instructions.
* **Appendix J: Technical Viva Voce Defense Preparation Guide**
  * 13 core technical defense questions and answers (kept as an appendix for examination preparation).
