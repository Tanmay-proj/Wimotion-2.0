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
