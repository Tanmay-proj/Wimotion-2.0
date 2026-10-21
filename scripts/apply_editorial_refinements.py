# -*- coding: utf-8 -*-
"""
apply_editorial_refinements.py
Applies strict academic peer-audit revisions to MASTER_DISSERTATION_FINAL.md:
- Replaces generic Front Matter placeholders with official names:
  OC Tanmay Mugale (TES-4312), OC Rishabh Rathore (TES-4316),
  DS Guide: Lt Col Rajat Gaur, DS Co-Guide: Maj Vaibhav Kukreti, MCEME.
- Refines Abstract and Chapter 6 to accurately frame the 49.26% test accuracy
  as a baseline feasibility proof-of-concept on ultra-low-cost microcontrollers.
- Re-calibrates the 52.89% false-alarm rate framing (substantially reduced from
  98.35%, but clearly acknowledging that 52.89% requires further multi-link correlation).
- Clarifies over-the-air packet generation (~400 pkts/s aggregate) vs. single-receiver
  serial telemetry ingestion (102.4 Hz on HUD).
- Reconciles hardware BoM (~$25–$30 total array, <$4 per ESP32 node; eliminates 'sub-dollar').
- Trims Chapter 9 into a tight 3.5-page focused discussion on non-visual occupancy sensing,
  unattended perimeter monitoring, and search-and-rescue.
- Trims Chapter 10 into a crisp 4-page engineering roadmap with clear bottleneck-to-metric milestones.
"""
import sys
from pathlib import Path

MD_PATH = Path(r"e:\WIFI_INTERFEROMETRIC_NEURAL_SENSING\wimotion_2.0\docs\MASTER_DISSERTATION_FINAL.md")

with open(MD_PATH, "r", encoding="utf-8") as f:
    text = f.read()

# ----------------------------------------------------
# 1. Update Front Matter
# ----------------------------------------------------
fm_anchor_start = text.find("# PART I: FRONT MATTER")
fm_anchor_end = text.find("## 7. TABLE OF CONTENTS")
if fm_anchor_start == -1 or fm_anchor_end == -1:
    raise ValueError("Could not find Front Matter anchors in markdown!")

front_matter_old = text[fm_anchor_start:fm_anchor_end]

front_matter_new = """# PART I: FRONT MATTER

---

## 1. TITLE PAGE

```
                            A DISSERTATION REPORT ON
                 DESIGN, IMPLEMENTATION AND EMPIRICAL EVALUATION 
                     OF A MULTI-LINK WI-FI CSI SENSING SYSTEM 
                   FOR INDOOR SPATIAL DISTURBANCE TRACKING
                                (WiMotion 2.0)

                                 Submitted by
                         OC TANMAY MUGALE  (TES-4312)
                        OC RISHABH RATHORE (TES-4316)

                     In partial fulfillment of the requirements
                               for the award of
                             BACHELOR OF TECHNOLOGY
                                       IN
                        COMPUTER SCIENCE AND ENGINEERING /
                       ELECTRONICS AND COMMUNICATION ENGINEERING

                              Under Guidance of
                         DS GUIDE: LT COL RAJAT GAUR
                      DS CO-GUIDE: MAJ VAIBHAV KUKRETI

                     FACULTY OF ELECTRONICS AND MECHANICAL ENGINEERING
                  MILITARY COLLEGE OF ELECTRONICS AND MECHANICAL ENGINEERING
                                  (MCEME)
                                OCTOBER 2026
```

---

## 2. CERTIFICATE OF APPROVAL

This is to certify that the dissertation entitled **"Design, Implementation and Empirical Evaluation of a Multi-Link Wi-Fi CSI Sensing System for Indoor Spatial Disturbance Tracking (WiMotion 2.0)"**, submitted by **OC Tanmay Mugale (TES-4312)** and **OC Rishabh Rathore (TES-4316)** in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology in Computer Science and Engineering / Electronics and Communication Engineering, is an authentic record of bonafide research work carried out under our supervision and guidance.

To the best of our knowledge, the matter embodied in this dissertation has not been submitted to any other University / Institute for the award of any Degree or Diploma.

\\
\\
______________________________  
**Lt Col Rajat Gaur**  
Project Supervisor / DS Guide  
Faculty of Electronics and Mechanical Engineering  
Military College of Electronics and Mechanical Engineering (MCEME)  

\\
\\
______________________________  
**Maj Vaibhav Kukreti**  
DS Co-Guide  
Faculty of Electronics and Mechanical Engineering  
Military College of Electronics and Mechanical Engineering (MCEME)  

---

## 3. STUDENT DECLARATION

We hereby declare that this dissertation entitled **"Design, Implementation and Empirical Evaluation of a Multi-Link Wi-Fi CSI Sensing System for Indoor Spatial Disturbance Tracking (WiMotion 2.0)"** is an authentic record of original research work conducted by us under the supervision of **Lt Col Rajat Gaur (DS Guide)** and **Maj Vaibhav Kukreti (DS Co-Guide)**, Faculty of Electronics and Mechanical Engineering, Military College of Electronics and Mechanical Engineering (MCEME).

We have adhered to all academic integrity norms. All theoretical formulations, source code libraries, hardware standards, and literature cited have been duly referenced. This work has not been previously submitted for any degree, diploma, or certificate at this or any other academic institution.

\\
\\
Date: October 21, 2026  
Place: Secunderabad  

\\
\\
______________________________          ______________________________  
**OC Tanmay Mugale (TES-4312)**         **OC Rishabh Rathore (TES-4316)**  
Cadet Candidate Signature               Cadet Candidate Signature  

---

## 4. ACKNOWLEDGEMENTS

We express our deepest gratitude to our project supervisor, **Lt Col Rajat Gaur (DS Guide)**, and **Maj Vaibhav Kukreti (DS Co-Guide)**, for their invaluable guidance, technical insight, and continuous encouragement throughout the evolution of this research from its initial single-link exploratory phases (Project Echo and Shadow) to the complete multi-link spatial sensing architecture of WiMotion 2.0.

We extend sincere thanks to the Head of Faculty, Directing Staff, and officers of the **Military College of Electronics and Mechanical Engineering (MCEME)** for providing the laboratory facilities, computing infrastructure, and academic environment essential to the completion of this project.

Special appreciation is conveyed to our directing staff, laboratory technical staff, peers, and fellow course cadets whose constructive feedback, peer audits, and technical reviews helped refine our experimental methodology, eliminate data leakage, and maintain the highest standards of scientific rigor. Finally, we thank our families and comrades for their steadfast support and understanding during the intensive hardware experimentation and software engineering phases of this dissertation.

---

## 5. ABSTRACT

Conventional indoor human monitoring systems relying on optical video cameras or passive infrared (PIR) detectors face acute operational constraints regarding privacy infringement, line-of-sight occlusions, and vulnerability to environmental darkness or smoke. This dissertation presents the design, physical implementation, and empirical evaluation of **WiMotion 2.0**, an opportunistic, device-free radio frequency (RF) indoor spatial sensing system constructed entirely on low-cost Commodity Off-The-Shelf (COTS) Espressif ESP32 microcontrollers (<$4 per node; ~$25–$30 total hardware array).

By intercepting Orthogonal Frequency Division Multiplexing (OFDM) Channel State Information (CSI) across 64 subcarriers on standard 2.4 GHz IEEE 802.11n Wi-Fi transmissions, WiMotion 2.0 expands single-link sensing into an 8-link distributed star topology ($4\\text{ TX} \\to 2\\text{ RX}$) across four spatial quadrants ($Z_1, Z_2, Z_3, Z_4$). Operating at an aggregate broadcast transmission rate of ~400 packets/second across transmitters with dual-receiver serial ingestion at ~100–105 Hz, the software pipeline deploys multi-threaded asynchronous ring buffers, packet-level transmitter MAC demultiplexing, and an authoritative 56-dimensional canonical feature extraction vector that eliminates train-serving skew.

To guarantee scientific reproducibility, a historical data audit quarantined 116,588 frames across early exploratory sessions due to thread-race packet drops, establishing the strictly verified **Phase B benchmark dataset** (56,386 frames / 1,209 sliding windows) with 100% strict take-based zero-leakage partitioning. To address an acute 98.35% empty-room false-alarm rate in unconstrained classifiers, an empirical energy gate ($\\theta=1.80$) was calibrated on training data using Youden's $J$-statistic, reducing false alarms to **52.89%** and raising true empty-room recall from 1.65% to **47.11%**. While this reduction demonstrates the efficacy of amplitude thresholding, the remaining 52.89% false alarm rate highlights that ambient RF noise and static multipath drift require multi-link spatial correlation and phase calibration in future work.

On unseen held-out physical test takes (Take 02), the supervised Random Forest classifier achieved a **49.26% gated 5-class accuracy** (substantially outperforming the 29.26% heuristic baseline and exceeding the 20.0% random guessing baseline by nearly 2.5 times), with Zone 4 achieving **80.99% recall** due to proximity to receiver antenna clusters, while Zone 3 exhibited **14.05% recall** due to diagonal multipath attenuation. This performance establishes an empirical feasibility baseline for low-cost RF spatial disturbance sensing. The system features an interactive real-time dashboard integrating a 2D polar radar sweep, a 3D Three.js room digital twin, and a dual-engine HUD backed by 56 automated unit tests and cloud CI. Finally, the dissertation explores potential research applications in camera-independent indoor situational awareness and establishes a grounded, 5-stage technology roadmap for future development.

---

## 6. KEYWORDS

Wi-Fi Sensing, Channel State Information (CSI), Human Presence Detection, Spatial Sensing, ESP32, RF Signal Processing, Machine Learning, Non-Line-of-Sight Sensing, Situational Awareness.

---

"""

text = text.replace(front_matter_old, front_matter_new)
print("[+] Front matter updated.")

# ----------------------------------------------------
# 2. Update Chapter 1 Contributions & Scope
# ----------------------------------------------------
text = text.replace(
    "Demonstrates that a $30 hardware array of 6 standard ESP32 microcontrollers can deliver multi-link spatial disturbance tracking without SDRs.",
    "Demonstrates that an ultra-low-cost hardware array (~$25–$30 total BoM; <$4 per ESP32 node) can deliver multi-link spatial disturbance tracking without specialized software-defined radios."
)

# ----------------------------------------------------
# 3. Update Chapter 6 Results Framing
# ----------------------------------------------------
ch6_orig_far = """- **Gated Test Accuracy ($\\\\theta=1.80$):** **$49.26\%$** (Weighted F1: $48.25\%$)
- **CLEAR False-Alarm Rate:** Slashed from $98.35\%$ down to **$52.89\%$**
- **CLEAR Recall (TNR):** Boosted from $1.65\%$ (2/121) up to **$47.11\%$** (57/121)"""

ch6_new_far = """- **Gated Test Accuracy ($\\\\theta=1.80$):** **$49.26\%$** (Weighted F1: $48.25\%$)
- **CLEAR False-Alarm Rate:** Reduced from $98.35\%$ down to **$52.89\%$** (notable suppression, though 52.89% remaining false alarms indicate further multi-link correlation is required)
- **CLEAR Recall (TNR):** Improved from $1.65\%$ (2/121) up to **$47.11\%$** (57/121)"""

text = text.replace(ch6_orig_far, ch6_new_far)

text = text.replace(
    "Both linear and tree-based machine learning models substantially outperform the heuristic baseline ($29.26\%$) and exceed random chance ($20.0\%$) by **nearly 2.5 times**.",
    "Both linear and tree-based machine learning models substantially outperform the heuristic baseline ($29.26\%$) and exceed random chance ($20.0\%$) by **nearly 2.5 times**. This 49.26% accuracy establishes an empirical feasibility baseline on ultra-low-cost commodity hardware; it confirms that spatial disturbance can be resolved across coarse quadrants, though it represents a baseline feasibility demonstration rather than an operational localization system."
)

text = text.replace(
    "In physical security and surveillance, cutting false alarms by half is vastly more critical than a nominal $1.6\%$ overall accuracy delta.",
    "The calibrated energy gate achieved a substantial reduction in false alarms (from 98.35% down to 52.89%), demonstrating the viability of amplitude thresholding. However, the remaining 52.89% false alarm rate confirms that single-threshold amplitude gating alone cannot fully resolve environmental multipath drift, underscoring the necessity of multi-link spatial correlation in future work."
)

# ----------------------------------------------------
# 4. Update Chapter 7 Telemetry Clarification
# ----------------------------------------------------
ch7_orig_hud = """1. **Card 1: Valid CSI Rate:** Displays the aggregate packet arrival frequency across both receivers, dynamically calculated over the 2.0-second sliding window buffer. Includes real-time indicators for per-receiver rates (`RX1: 51.2 Hz | RX2: 51.2 Hz`)."""

ch7_new_hud = """1. **Card 1: Valid CSI Rate:** Displays the aggregate serial ingestion rate across both active receivers (`RX1: 51.2 Hz | RX2: 51.2 Hz`, totaling 102.4 Hz across COM8 and COM9). While the four distributed transmitters broadcast an aggregate RF packet rate of ~400 packets/second over the air (~100 pkts/s per TX), each receiver ingests ~50–52 packets/second of synchronized valid frames over its dedicated USB-UART link, providing smooth 102.4 Hz telemetry updates to the sliding window buffer."""

text = text.replace(ch7_orig_hud, ch7_new_hud)

# ----------------------------------------------------
# 5. Trim Chapter 9 (Intelligence / Defense Applications)
# ----------------------------------------------------
ch9_start = text.find("# CHAPTER 9: POTENTIAL APPLICATIONS")
ch9_end = text.find("# CHAPTER 10: STRATEGIC WAY AHEAD")

if ch9_start != -1 and ch9_end != -1:
    ch9_new = """# CHAPTER 9: POTENTIAL APPLICATIONS OF WI-FI CSI SENSING IN INTELLIGENCE GATHERING AND SURVEILLANCE

---

## 9.1 Introduction and Application Context

While the physical prototype developed in this dissertation (WiMotion 2.0) was evaluated within a controlled single-room academic laboratory on commodity microcontrollers, the underlying physical principle—exploiting multi-carrier radio frequency perturbations to sense environmental dynamics—possesses profound strategic implications.

Across defense, law enforcement, critical infrastructure protection, and disaster response, acquiring situational awareness inside enclosed structures is an operational necessity. Traditional reconnaissance modalities (such as optical drones, thermal cameras, and active radars) frequently confront physical or operational constraints in contested urban environments. This chapter examines the **potential research applications of Wi-Fi Channel State Information (CSI) sensing**, framing them as long-term exploratory avenues while strictly maintaining the technical boundaries separating laboratory bench prototypes from deployable operational systems.

```
[EXPERIMENTAL SCALE vs. OPERATIONAL APPLICATION]
┌─────────────────────────────────────────┐       ┌─────────────────────────────────────────┐
│     WIMOTION 2.0 PROTOTYPE (Current)    │       │     FUTURE RESEARCH DOMAINS (Scope)     │
├─────────────────────────────────────────┤       ├─────────────────────────────────────────┤
│ - Single-room controlled deployment     │  ──►  │ - Camera-independent occupancy sensing  │
│ - Single human occupant locomotion      │       │ - Perimeter disturbance & tripwires     │
│ - Coarse 4-quadrant spatial sectoring   │       │ - Search-and-rescue void sensing        │
│ - 49.26% gated feasibility accuracy     │       │ - Non-invasive civilian assisted living │
└─────────────────────────────────────────┘       └─────────────────────────────────────────┘
```

---

## 9.2 Camera-Independent Occupancy Sensing and Privacy Compliance

In high-security and privacy-mandated facilities, conventional video surveillance introduces acute operational vulnerabilities:
- **Physical Occlusion & Environmental Darkness:** Optical cameras fail completely in total darkness, dense smoke, airborne dust, or behind partition walls and closed doors.
- **Cyber & Optical Interception Risks:** Video streams transmitted over local networks can be intercepted or decrypted, exposing facial features and sensitive displays. Furthermore, lenses are readily blinded by laser dazzlers, aerosol sprays, or physical obstructions.

RF-based CSI sensing provides an inherently **non-visual physical abstraction**. The transceivers exchange raw physical layer frames, and the receiver extracts numerical channel state matrices. Even if intercepted, the data stream contains no facial features, legible documents, or optical silhouettes. This non-optical nature makes CSI sensing an attractive candidate for:
1. **Classified Facility Monitoring:** Continuous presence verification in sensitive installations where optical cameras are strictly prohibited by security regulations.
2. **Privacy-Mandated Civilian Spaces:** Monitoring in bedrooms, patient recovery wards, and restrooms for medical immobility or fall detection without violating personal dignity.

---

## 9.3 Potential Dual-Use Security and Perimeter Monitoring Applications

In security and perimeter protection, distributed multi-link RF arrays offer the conceptual potential to establish **unattended, invisible disturbance corridors**:

1. **Virtual Volumetric Tripwires:** By establishing crossing RF baselines along interior hallways or security corridors, an intruder crossing the Fresnel zone alters the multipath channel matrix. Unlike optical laser tripwires, the RF baseline is completely invisible to night-vision devices and infrared optics; unlike seismic geophones, it is immune to distant ground vehicular vibrations.
2. **Pre-Entry Clearance Intelligence:** Prior to entering an enclosed, visually obstructed room during building-clearing or security checks, exterior non-line-of-sight sensing could theoretically indicate whether a room is in a baseline `CLEAR` state or whether motion is active in entrance versus rear quadrants.

*Explicit Technical Boundary:* It must be emphasized that **WiMotion 2.0 has NOT been tested in through-wall tactical breach environments or multi-occupant tactical scenarios**. These concepts represent long-term research motivations rather than current operational claims.

---

## 9.4 Search-and-Rescue and Civilian Dual-Use Research

Beyond security, device-free RF sensing addresses critical challenges in humanitarian and emergency response:
- **Collapsed Structure Void Sensing:** Following earthquakes or structural collapses, locating trapped individuals beneath non-metallic debris (drywall, timber, bricks) is critical. While walking produces macroscopic variance, rhythmic human respiration (0.2–0.33 Hz) creates periodic micro-Doppler oscillations. Research literature indicates that with sanitized phase and high-gain antennas, RF sensing could detect vital-sign chest displacements device-free.
- **Elderly Assisted Living & Smart Buildings:** Continuous non-intrusive fall detection and automated occupancy-driven HVAC/lighting control that operates without requiring elderly occupants to wear pendants or carry battery-powered tags.

---

## 9.5 Comparative Sensor Trade-Offs and Operational Constraints

To establish a defensible perspective, Table 9.1 contextualizes Wi-Fi CSI sensing against established sensor modalities:

### Table 9.1: Comparative Sensor Modality Trade-Off Matrix

| Evaluation Dimension | Optical Cameras | Thermal Infrared | Dedicated mmWave Radar | Passive Infrared (PIR) | Distributed Wi-Fi CSI (WiMotion 2.0) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Through-Wall Sensing** | Impossible (0%) | Impossible (0%) | High (Dedicated UWB) | Impossible (0%) | **Moderate (Drywall / Timber)** |
| **Darkness / Smoke Immunity** | Poor | High | High | Moderate | **Complete Immunity** |
| **Privacy Preservation** | Very Low | Moderate | High | High | **High (Non-Visual Physical Metric)** |
| **Hardware Capital Cost** | Moderate | High ($500+) | High ($200–$1,000) | Low ($5–$15) | **Ultra-Low (<$4/node; ~$25–$30 array)** |
| **Multi-Person Separation** | Very High | High | High | None | **Challenging (Unsolved Research)** |
| **Spatial Resolution** | Pixel-Level | Sub-Meter | Centimeter-Level | Coarse Sector Only | **Quadrant-Level (Metres)** |

### Critical Technical and Operational Limitations:
1. **Multipath Environmental Dependency:** CSI signatures depend directly on room geometry and metallic boundary placements. Rearranging metallic furniture alters the static multipath profile, necessitating model adaptation.
2. **Susceptibility to Co-Channel RF Congestion:** Operating on unlicensed 2.4 GHz channels exposes the system to interference from heavy Wi-Fi data traffic, Bluetooth transmissions, and consumer electronics.
3. **Application Readiness Gap:** Transitioning from single-room quadrant classification (49.26% accuracy) to deployable security equipment requires resolving multi-person superposition, cross-environment transferability, and phase drift calibration.

---
*(End of Chapter 9 — Technical Analysis & Strategic Applications Review)*

---

"""
    text = text[:ch9_start] + ch9_new + text[ch9_end:]
    print("[+] Chapter 9 trimmed and replaced.")

# ----------------------------------------------------
# 6. Trim Chapter 10 (Engineering Roadmap)
# ----------------------------------------------------
ch10_start = text.find("# CHAPTER 10: STRATEGIC WAY AHEAD")
ch10_end = text.find("# CHAPTER 11: CONCLUSION")

if ch10_start != -1 and ch10_end != -1:
    ch10_new = """# CHAPTER 10: STRATEGIC WAY AHEAD: RESEARCH OPPORTUNITIES AND TECHNOLOGY ROADMAP

---

## 10.1 Structured Evolution: From Bench Prototype to Validated System

The development of WiMotion 2.0 proves that commodity Wi-Fi microcontrollers can capture multi-link spatial RF perturbations and classify coarse quadrant occupancy device-free. Advancing from this academic proof-of-concept to an operationally robust sensing system requires addressing specific hardware, signal processing, and algorithmic bottlenecks through a structured, multi-phase engineering roadmap:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        WIMOTION STRUCTURED ENGINEERING ROADMAP                         │
├─────────────────────┬──────────────────────────┬───────────────────────────────────────┤
│ Current Bottleneck  │ Proposed Upgrade         │ Target Engineering Benchmark          │
├─────────────────────┼──────────────────────────┼───────────────────────────────────────┤
│ Amplitude-Only Data │ Wi-Fi 6 (ESP32-C6) &     │ Sanitized Phase & Angle-of-Arrival    │
│ (Phase noise / CFO) │ Conjugate Multiplication │ (AoA angular resolution < 10°)        │
├─────────────────────┼──────────────────────────┼───────────────────────────────────────┤
│ Single-Room Bias    │ Domain-Adversarial Neural│ Cross-Room Transfer Accuracy > 65%    │
│ (Multipath shift)   │ Networks (DANN)          │ without complete model retraining     │
├─────────────────────┼──────────────────────────┼───────────────────────────────────────┤
│ Memoryless Windows  │ Temporal Convolutional   │ Gait Trajectory Smoothing &           │
│ (Window flickers)   │ Networks (TCN / BiLSTM)  │ Prediction Flicker Elimination        │
├─────────────────────┼──────────────────────────┼───────────────────────────────────────┤
│ Single Occupant Only│ Subcarrier Doppler BSS   │ Concurrent 2-Person Separation        │
│ (Superposition)     │ & Multi-Target Clustering│ without ghost quadrant triggers       │
└─────────────────────┴──────────────────────────┴───────────────────────────────────────┘
```

---

## 10.2 Hardware Scaling and Antenna Diversity

While the ESP32-WROOM-32 served as a viable entry platform, modern silicon advancements offer concrete hardware-level upgrades:

* **Transition to Wi-Fi 6 (IEEE 802.11ax) Silicon (ESP32-C6 / ESP32-S3):**
  - Next-generation Wi-Fi 6 microcontrollers introduce Orthogonal Frequency Division Multiple Access (OFDMA), dividing channels into narrower Resource Units (RUs) with up to 256 subcarriers per 20 MHz channel—quadrupling frequency-domain spectral resolution over legacy 802.11n.
* **Angle-of-Arrival (AoA) Uniform Linear Antenna Arrays (ULA):**
  - By equipping receivers with dual antennas spaced at half-wavelength intervals ($d = \\lambda/2 \\approx 6.15\\text{ cm}$), the system measures phase difference of arrival:
    $$\\Delta \\Phi = \\frac{2 \\pi}{\\lambda} d \\sin(\\theta) \\implies \\theta = \\arcsin\\left( \\frac{\\lambda \\Delta \\Phi}{2 \\pi d} \\right)$$
  - Applying array processing algorithms (e.g., MUSIC or ESPRIT) will allow direct estimation of the scattered angle $\\theta$, elevating coarse quadrant sectoring into continuous coordinate tracking.

---

## 10.3 Signal Processing Enhancements and Machine Learning Architectures

1. **CSI Phase Sanitization via Conjugate Multiplication:**
   - By receiving transmissions across two closely spaced antennas on the same receiver, carrier frequency offset ($\\Delta f_{\\text{CFO}}$) cancels out identically via conjugate multiplication:
     $$S(f_k, t) = H_1(f_k, t) \\cdot H_2^*(f_k, t) = |H_1| |H_2| e^{j(\\Phi_1(t) - \\Phi_2(t))}$$
   - This isolates sanitized relative phase ($\\Delta \\Phi$), providing sensitivity to sub-centimeter displacements necessary for contactless respiration monitoring.
2. **Sequential Gait Modeling (TCN / BiLSTM):**
   - Incorporating temporal sequence modeling allows the network to exploit kinematic continuity, smoothing quadrant transitions and suppressing transient single-window misclassifications.
3. **Cross-Environment Domain Adaptation (DANN):**
   - Minimizing feature divergence across distinct rooms using adversarial domain classifiers to learn environment-invariant motion features, mitigating the requirement to retrain models for every new room.

---

## 10.4 Strategic 5-Stage Research Roadmap and Validation Matrix

Table 10.1 establishes the formal milestone framework guiding long-term development:

### Table 10.1: Strategic 5-Stage Research Roadmap and Validation Matrix

| Stage & Timeline | Research Objective | Required Hardware & Dataset | Validation Metric | Major Technical Risk | Success Criterion |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **Stage 1 (Completed)** | Distributed Multi-Link Sensing & False-Alarm Calibration | 6x ESP32-WROOM-32 nodes, 8 baselines, Phase B benchmark (10 sessions, 1,209 windows) | 49.26% gated 5-class accuracy; 52.89% CLEAR false-alarm rate (cut from 98.35%) | Clock drift and USB serial driver FIFO buffer overflows | 100% strict session-level zero-leakage split; 56/56 passing unit tests |
| **Stage 2 (6–12 Mo)** | Measured Room Geometry & Cross-Environment Validation | Multi-room metric testbeds; laser-measured node ground truth; 50+ diverse physical sessions | Cross-room domain generalization accuracy; transfer learning loss | Severe multipath decay and room-transfer performance degradation | Consistent quadrant detection across 3 distinct architectural rooms |
| **Stage 3 (12–24 Mo)** | Phase Sanitization & Antenna Diversity (AoA) | Dual-antenna ESP32-S3 / C6 hardware; ULA switched antenna arrays; complex baseband I/Q capture | Relative phase stability; Angle-of-Arrival angular resolution ($< 10^\\circ$) | Phase noise non-linearity and uncalibrated carrier frequency offsets (CFO) | Continuous metric coordinate tracking error $< 0.8\\text{ meters}$ |
| **Stage 4 (24–36 Mo)** | Multi-Person Separation & Trajectory Disambiguation | 32-link perimeter mesh ($8\\text{ TX} \\times 4\\text{ RX}$); multi-subject controlled traversal datasets | Multi-target precision/recall; Doppler spectrogram separation | Destructive RF wave superposition and phantom ghost quadrant triggers | Accurate concurrent 2-person quadrant separation without ghost targets |
| **Stage 5 (36–60 Mo)** | Heterogeneous Fusion & Standoff Operational Trials | Encapsulated battery-powered pucks; steerable mmWave radar fusion; through-wall testbed | Standoff detection range; through-barrier attenuation margin | Severe drywall/concrete RF attenuation and ambient co-channel jamming | Operational non-line-of-sight intruder detection through 15 cm partition walls |

---
*(End of Chapter 10 — Strategic Technology Roadmap & Research Plan)*

---

"""
    text = text[:ch10_start] + ch10_new + text[ch10_end:]
    print("[+] Chapter 10 streamlined and replaced.")

# ----------------------------------------------------
# 7. Update Chapter 11 Conclusions
# ----------------------------------------------------
text = text.replace(
    "Proving that sub-dollar microcontrollers can perform spatial quadrant disturbance tracking",
    "Proving that ultra-low-cost commodity microcontrollers (<$4 per node; ~$25–$30 total array) can perform spatial quadrant disturbance tracking"
)

with open(MD_PATH, "w", encoding="utf-8") as f:
    f.write(text)

print(f"[+] SUCCESS! Refined MASTER_DISSERTATION_FINAL.md saved. Length: {len(text)} chars, Lines: {len(text.splitlines())}")
