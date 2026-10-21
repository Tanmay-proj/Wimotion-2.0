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
