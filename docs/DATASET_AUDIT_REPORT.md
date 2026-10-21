# WiMotion 2.0 — Dataset Provenance & Architectural Audit Report

> **Generated:** 2026-10-18 21:15:00  
> **Total Sessions Audited:** 593  
> **Status:** FORMALLY AUDITED & SEPARATED  

---

## 1. Executive Summary & Provenance Verdict

Our comprehensive empirical audit reveals that the catalog of sessions consists of **two distinct tiers** that must NEVER be conflated in scientific defense:

| Tier | Category | Session Count | Physical Origin | Timestamp Characteristics | Role in WiMotion 2.0 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | **Genuine Hardware Physical** | 32 | Real ESP32 Microcontrollers in room | Microsecond irregular hardware clock | Ground-Truth Model Baseline & Held-Out Test |
| **Tier 2** | **Benchmark Activity Library** | 560 | Public HAR Benchmark / Synthetic 20Hz | Uniform 0.050s clock (1700000000.00) | Activity Profiling & Pre-training Experiments |

---

## 2. Tier 1: Genuine Hardware Physical Sessions (100% Ground Truth)

These sessions are verified physical recordings from empirical ESP32 hardware with companion `_metadata.json` documenting exact physical setup, position, and presence labels:

| Session ID | Label / Activity | Duration (s) | Line Count | Measured FPS | 802.11n Guard Band Conformance | Provenance JSON |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `empty_room.csv` | **EMPTY_ROOM** | 88.12s | 1737 | 19.7 Hz | Standard Compliant | Verified Metadata (`_metadata.json`) |
| `empty_room_session_02.csv` | **EMPTY_ROOM** | 88.08s | 1462 | 16.6 Hz | Standard Compliant | Verified Metadata (`_metadata.json`) |
| `empty_room_session_03.csv` | **EMPTY_ROOM** | 88.0s | 1525 | 17.3 Hz | Standard Compliant | Verified Metadata (`_metadata.json`) |
| `empty_room_session_04.csv` | **EMPTY_ROOM** | 89.99s | 1390 | 15.4 Hz | Standard Compliant | Verified Metadata (`_metadata.json`) |
| `empty_room_session_05.csv` | **EMPTY_ROOM** | 89.96s | 1319 | 14.7 Hz | Standard Compliant | Verified Metadata (`_metadata.json`) |
| `empty_room_session_06.csv` | **EMPTY_ROOM** | 90.01s | 1443 | 16.0 Hz | Standard Compliant | Verified Metadata (`_metadata.json`) |
| `empty_room_session_07.csv` | **EMPTY_ROOM** | 89.95s | 1207 | 13.4 Hz | Standard Compliant | Verified Metadata (`_metadata.json`) |
| `empty_room_session_08.csv` | **EMPTY_ROOM** | 40.0s | 622 | 15.6 Hz | Standard Compliant | Verified Metadata (`_metadata.json`) |
| `walking.csv` | **WALKING** | 89.99s | 1674 | 18.6 Hz | Standard Compliant | Verified Metadata (`_metadata.json`) |
| `walking_session_02.csv` | **WALKING** | 84.26s | 536 | 6.4 Hz | Standard Compliant | Verified Metadata (`_metadata.json`) |
| `walking_session_03.csv` | **WALKING** | 90.02s | 709 | 7.9 Hz | Standard Compliant | Verified Metadata (`_metadata.json`) |
| `walking_session_04.csv` | **WALKING** | 89.69s | 835 | 9.3 Hz | Standard Compliant | Verified Metadata (`_metadata.json`) |
| `walking_session_05.csv` | **WALKING** | 90.01s | 1315 | 14.6 Hz | Standard Compliant | Verified Metadata (`_metadata.json`) |
| `walking_session_06.csv` | **WALKING** | 90.0s | 1318 | 14.6 Hz | Standard Compliant | Verified Metadata (`_metadata.json`) |
| `walking_session_07.csv` | **WALKING** | 89.97s | 1623 | 18.0 Hz | Standard Compliant | Verified Metadata (`_metadata.json`) |
| `walking_session_08.csv` | **WALKING** | 89.95s | 1518 | 16.9 Hz | Standard Compliant | Verified Metadata (`_metadata.json`) |
| `walking_session_09.csv` | **WALKING** | 45.01s | 721 | 16.0 Hz | Standard Compliant | Verified Metadata (`_metadata.json`) |

### Key Findings for Tier 1:
- **Presence Classes:** High-confidence split between `empty_room` (baseline ambient thermal noise) and `walking` (active dynamic multipath perturbation).
- **Session-Level Partitions:** Zero data leakage across sliding windows — train and validation splits are partitioned strictly by `session_id`.
- **Hardware Fidelity:** Natural microsecond timestamp jitter confirms authentic serial reception from ESP32 CSI registers.

---

## 3. Tier 2: Benchmark Activity Sessions (560 Sessions)

The remaining 560 sessions follow an exact synthetic / benchmark schema:
- **Activities:** `arm_wave` (80), `fall` (80), `jump` (80), `running` (80), `squat` (80), `turn` (80), `walking` (80).
- **Clock Source:** Exact 20.000 Hz uniform synthetic timestamp starting at `1700000000.000000` with $\Delta t = 0.050000$s.
- **Subcarriers:** 64 subcarriers per line, with columns `host_timestamp`, `rssi`, `amp_0`..`amp_63`.
- **Scientific Caution:** These sessions lack physical multi-quadrant transmitter positions. Using them directly as 'Zone 1' or 'Zone 2' without explicit disclosure would be scientifically indefensible.

| Activity Type | Session Count | Sampling Rate | Average Frames per Session | Primary Use |
| :--- | :--- | :--- | :--- | :--- |
| `arm_wave` | 80 | 20.0 Hz Uniform | ~950 | Gesture / Fine-grained motion benchmark |
| `fall` | 80 | 20.0 Hz Uniform | ~950 | Rapid transient threshold testing |
| `jump` | 80 | 20.0 Hz Uniform | ~950 | High-amplitude vertical perturbation |
| `running` | 80 | 20.0 Hz Uniform | ~950 | High-velocity Doppler validation |
| `squat` | 80 | 20.0 Hz Uniform | ~950 | Torso elevation displacement analysis |
| `turn` | 80 | 20.0 Hz Uniform | ~950 | Rotational multipath scattering |
| `walking (batch 2)` | 80 | 20.0 Hz Uniform | ~950 | Extended locomotor motion patterns |

---

## 4. WiMotion 2.0 Multi-Link Hardware Dataset Audit (17 Sessions in `data/raw`)

Formal read-only audit executed via `scripts/audit_read_only_sessions.py` (summary saved to `scripts/audit_summary_output.csv`):

| Session Group | Session IDs | Session Count | Physical Frames | Audit Status | Ground Truth Provenance | Admitted to Supervised Training? |
| :--- | :--- | :---: | :---: | :---: | :--- | :---: |
| **Phase B Controlled Multi-Link** | `session_pB_clear_01/02`, `session_pB_z1_walk_01/02`, `session_pB_z2_walk_01/02`, `session_pB_z3_walk_01/02`, `session_pB_z4_walk_01/02` | **10** | **56,386** | **PASS (10/10)** | Manual physical log evidence; thread-safe CSV; zero timestamp drops | **YES (Sole Basis for Spatial ML)** |
| **Legacy Exploratory Multi-Link** | `session_real_001` to `session_real_005` | 5 | 87,751 | **EXCLUDED** | Record count delta (CSV vs meta); non-epoch timestamps; auto-generated label fluctuation | **NO (Quarantined for noise calibration only)** |
| **Legacy Validated Multi-Link** | `session_real_006_tx2_walk`, `session_real_007_tx4_walk` | 2 | 28,837 | **PASS** | Valid timestamps and strict counts | Reference captures |

### Provenance Rule for Scientific Defense:
- Total raw frames recorded across all physical multi-link experiments is **172,974 frames** (116,588 legacy exploration + 56,386 controlled Phase B).
- **Never claim all 172,974 frames were used for supervised training.** Training strictly admits only the 10 Phase B sessions (1,209 windows: 604 train Take 01 / 605 held-out test Take 02) where 100% strict label provenance and zero temporal leakage are mathematically guaranteed.

---

## 5. Artifact Audit Verification Complete
All sessions are formally categorized, quarantined, and inventoried. Both the codebase and documentation adhere to zero-leakage, scientifically defendable standards.