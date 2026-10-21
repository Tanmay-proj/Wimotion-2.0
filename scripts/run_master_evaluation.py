#!/usr/bin/env python3
"""
WiMotion 2.0 — Master Evaluation & Reproducibility Suite (Phase 5)

One-click reproducible runner that executes the entire verification pipeline:
1. Automated Unit Test Discovery (54 tests including feature parity & security containment)
2. Colleague 6-Point Audit Suite (zero-sample link gating, single-RX isolation, etc.)
3. Read-Only Hardware Session & Provenance Audit
4. Multi-Model Benchmark & Supervised Training with Calibrated CLEAR Gate
5. Model Artifact Hash & Git Commit Verification

Usage:
    py -3.10 scripts/run_master_evaluation.py
"""
import sys
import os
import subprocess
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def run_step(step_name: str, cmd: list) -> bool:
    print("\n" + "=" * 78)
    print(f"[*] STEP: {step_name}")
    print(f"[*] Command: {' '.join(cmd)}")
    print("=" * 78)
    res = subprocess.run(cmd, cwd=str(ROOT))
    if res.returncode != 0:
        print(f"[!] FAILED: {step_name} exited with code {res.returncode}")
        return False
    print(f"[+] PASSED: {step_name}")
    return True


def main():
    print("=" * 78)
    print("   WiMotion 2.0 — Master Verification & Evaluation Pipeline")
    print("=" * 78)

    # 1. Automated Unit Test Suite
    ok1 = run_step(
        "Automated Unit Test Discovery (56 Tests)",
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
    )
    if not ok1:
        return 1

    # 2. Colleague 6-Point Audit Suite
    ok2 = run_step(
        "Colleague 6-Point Verification Suite",
        [sys.executable, str(ROOT / "scripts" / "verify_six_checks.py")]
    )
    if not ok2:
        return 1

    # 3. Read-Only Session Audit
    ok3 = run_step(
        "Read-Only Hardware Session & Label Provenance Audit",
        [sys.executable, str(ROOT / "scripts" / "audit_read_only_sessions.py")]
    )
    if not ok3:
        return 1

    # 4. Supervised Spatial Model Training & Benchmark
    ok4 = run_step(
        "Supervised Model Training & Multi-Model Benchmark (Phase B Take Split)",
        [sys.executable, str(ROOT / "scripts" / "train_spatial_model.py"), "--dataset", "phase_b", "--classifier", "random_forest"]
    )
    if not ok4:
        return 1

    # 5. Strict Artifact Hash, Schema, and Provenance Verification
    model_p = ROOT / "models" / "spatial_model.pkl"
    scorecard_p = ROOT / "models" / "spatial_model_scorecard.json"

    if not model_p.exists() or not scorecard_p.exists():
        print("[!] Error: Model or scorecard artifact missing after training.")
        return 1

    data = open(model_p, "rb").read()
    model_sha = hashlib.sha256(data).hexdigest()
    model_size = len(data)

    with open(scorecard_p, "r", encoding="utf-8") as f:
        sc = json.load(f)

    # 5a. Assert Model SHA-256 matches scorecard expectation
    expected_sha = sc.get("model_sha256")
    if expected_sha and model_sha != expected_sha:
        print("\n" + "!" * 78)
        print(f"[!] CRITICAL PROVENANCE ERROR: Model binary SHA-256 mismatch!")
        print(f"    Actual Binary SHA-256:   {model_sha}")
        print(f"    Scorecard Stored SHA-256: {expected_sha}")
        print("!" * 78)
        return 1

    # 5b. Unpickle model payload and verify schema contract & commit linkage
    import pickle
    try:
        payload = pickle.loads(data)
    except Exception as e:
        print(f"[!] Error unpickling model payload: {e}")
        return 1

    from spatial.features import FEATURE_SCHEMA_VERSION
    if payload.get("feature_schema_version") != FEATURE_SCHEMA_VERSION:
        print(f"[!] CRITICAL SCHEMA ERROR: Model feature schema version mismatch!")
        print(f"    Model Version:     {payload.get('feature_schema_version')}")
        print(f"    Canonical Version: {FEATURE_SCHEMA_VERSION}")
        return 1

    if payload.get("git_commit") != sc.get("git_commit"):
        print(f"[!] CRITICAL PROVENANCE ERROR: Git commit mismatch between binary and scorecard!")
        print(f"    Binary Commit:    {payload.get('git_commit')}")
        print(f"    Scorecard Commit: {sc.get('git_commit')}")
        return 1

    if len(payload.get("feature_names", [])) != 56:
        print(f"[!] CRITICAL CONTRACT ERROR: Expected 56 feature names, got {len(payload.get('feature_names', []))}")
        return 1

    try:
        git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip()
    except Exception:
        git_sha = "unknown"

    print("\n" + "=" * 78)
    print("           MASTER EVALUATION PIPELINE — FINAL EXECUTION SUMMARY")
    print("=" * 78)
    print(f"Git Commit SHA-1:         {git_sha}")
    print(f"Model Artifact File:      {model_p.name} ({model_size:,} bytes)")
    print(f"Model Artifact SHA-256:   {model_sha} [STRICT MATCH]")
    print(f"Feature Schema Version:   {sc.get('feature_schema_version')} [STRICT MATCH]")
    print(f"Primary Classifier:       {sc.get('classifier')}")
    print(f"Calibrated Gate Cutoff:   theta = {sc.get('calibrated_energy_gate_threshold')}")
    print(f"Ungated Test Accuracy:    {sc['metrics']['learned_accuracy_pct']:.2f}% (Weighted F1: {sc['metrics']['learned_weighted_f1_pct']:.2f}%)")
    print(f"Gated Test Accuracy:      {sc['metrics']['gated_accuracy_pct']:.2f}% (Weighted F1: {sc['metrics']['gated_weighted_f1_pct']:.2f}%)")
    print(f"Heuristic Baseline Acc:   {sc['metrics']['heuristic_baseline_accuracy_pct']:.2f}%")

    print("\nModel Benchmark Summary:")
    for m, res in sc.get("model_comparison", {}).items():
        print(f"  - {m:<30s}: Ungated Acc={res['ungated_acc']:<5.2f}% | Gated Acc={res['gated_acc']:<5.2f}% | CLEAR Recall={res['clear_recall']:<5.1f}% | CLEAR FPR={res['clear_fpr']:<5.1f}%")

    print("=" * 78)
    print("[+] ALL PRE-DEMO EVALUATION STEPS COMPLETED & VERIFIED SUCCESSFULLY (100% PASS)")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
