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
