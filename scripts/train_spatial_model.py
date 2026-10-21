#!/usr/bin/env python3
"""
WiMotion 2.0 — Supervised Spatial Localization Model Trainer (Phase 6)

Trains a supervised spatial model to classify quadrant zone (CLEAR, Z1, Z2, Z3, Z4)
from 8-link distributed CSI features.

Scientific Standards:
  1. Session-Wise Train/Test Split: All windows from a session stay in either train or test.
     Zero temporal leakage across overlapping sliding windows.
  2. Multi-Link Feature Fusion: 56-dimensional vector (48 continuous link metrics + 8 link-validity flags).
  3. Direct Comparison: Evaluates against the heuristic SpatialBaseline on the exact same test splits.
  4. Honest Provenance: Distinguishes between physical hardware captures and benchmark sessions.
"""
import sys
import json
import time
import argparse
import pickle
from pathlib import Path
from collections import Counter
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, f1_score

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from spatial.types import CSIRecord
from spatial.features import extract_link_features, fuse_features
from spatial.inference import SpatialBaseline
from spatial.replay_loader import list_recordings, load_recording_frames

MODELS_DIR = ROOT / "models"
MODELS_DIR.mkdir(exist_ok=True)
DEFAULT_MODEL_OUT = MODELS_DIR / "spatial_model.pkl"
DEFAULT_SCORECARD_OUT = MODELS_DIR / "spatial_model_scorecard.json"


def extract_session_features(session_id: str):
    """
    Extracts 56-dim fused multi-link feature vectors and ground-truth zone labels
    for all valid sliding windows in a session.
    """
    data = load_recording_frames(session_id, eval_v1=False)
    if not data:
        return [], [], []

    frames = data.get("frames", [])
    X = []
    y = []
    baseline_preds = []

    spatial_heuristic = SpatialBaseline(variance_threshold=8.0)

    for f in frames:
        gt_zone = f.get("gt_zone")
        if not gt_zone or gt_zone == "UNKNOWN":
            continue

        vec = f.get("feature_vector")
        if vec is not None and len(vec) == 56 and np.all(np.isfinite(vec)):
            X.append(np.asarray(vec, dtype=np.float32))
            y.append(gt_zone)
            baseline_preds.append(f.get("model_zone", "CLEAR"))

    return X, y, baseline_preds


def train_spatial_pipeline(
    sessions: list,
    model_out: Path = DEFAULT_MODEL_OUT,
    scorecard_out: Path = DEFAULT_SCORECARD_OUT,
    classifier_type: str = "hist_gradient",
    n_splits: int = 3,
    test_size: float = 0.25,
    split_strategy: str = "take"
):
    print("=" * 78)
    print("   WiMotion 2.0 — Supervised Spatial Model Training Pipeline (Phase 6)")
    print("=" * 78)

    all_X = []
    all_y = []
    all_groups = []
    all_baseline = []
    session_provenances = {}

    print(f"[*] Extracting 56-dim multi-link features from {len(sessions)} candidate sessions...")
    for s in sessions:
        sid = s.get("session_id")
        prov = s.get("provenance", "unknown")
        session_provenances[sid] = prov

        X_s, y_s, b_s = extract_session_features(sid)
        if len(X_s) > 0:
            all_X.extend(X_s)
            all_y.extend(y_s)
            all_groups.extend([sid] * len(X_s))
            all_baseline.extend(b_s)
            print(f"    - {sid:30s} ({prov:25s}): {len(X_s)} windows | Classes: {set(y_s)}")

    if len(all_X) == 0:
        print("[!] Error: No valid feature windows extracted across provided sessions.")
        return 1

    X_arr = np.array(all_X, dtype=np.float32)
    y_arr = np.array(all_y)
    groups_arr = np.array(all_groups)
    baseline_arr = np.array(all_baseline)

    unique_classes = sorted(list(set(y_arr)))
    print(f"\n[+] Total Dataset: {len(X_arr)} windows from {len(set(groups_arr))} sessions.")
    print(f"    Classes: {unique_classes}")
    print(f"    Class Distribution: {dict(Counter(y_arr))}")

    # Session-Wise Split (Zero-Leakage Group Partitioning)
    print(f"\n[*] Partitioning by Session Groups (Strategy: {split_strategy})...")
    unique_sessions = np.unique(groups_arr)
    
    if split_strategy == "take":
        train_idx = np.array([i for i, g in enumerate(groups_arr) if g.endswith("_01") or "_01" in g])
        test_idx = np.array([i for i, g in enumerate(groups_arr) if g.endswith("_02") or "_02" in g])
        if len(train_idx) == 0 or len(test_idx) == 0:
            print("[!] Take split not applicable to all sessions, falling back to GroupShuffleSplit...")
            gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=42)
            train_idx, test_idx = next(gss.split(X_arr, y_arr, groups=groups_arr))
        else:
            print("    -> Natural Take-Based Split: All Take 01 in Train, All Take 02 in Held-Out Test.")
    elif len(unique_sessions) < 2:
        print("[!] Warning: Only 1 session with valid labels. Falling back to stratified window split.")
        from sklearn.model_selection import StratifiedShuffleSplit
        splitter = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=42)
        train_idx, test_idx = next(splitter.split(X_arr, y_arr))
    else:
        gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=42)
        train_idx, test_idx = next(gss.split(X_arr, y_arr, groups=groups_arr))

    X_train, X_test = X_arr[train_idx], X_arr[test_idx]
    y_train, y_test = y_arr[train_idx], y_arr[test_idx]
    train_sessions = np.unique(groups_arr[train_idx])
    test_sessions = np.unique(groups_arr[test_idx])
    b_test = baseline_arr[test_idx]

    print(f"    Train Set: {len(X_train)} windows across sessions: {list(train_sessions)}")
    print(f"    Test Set : {len(X_test)} windows across sessions: {list(test_sessions)}")
    
    # Assert zero overlap between train and test sessions
    overlap = set(train_sessions).intersection(set(test_sessions))
    assert len(overlap) == 0, f"Critical Leakage Violation: Sessions {overlap} appear in both train and test!"
    print("    -> Zero-Leakage Confirmed: No sessions overlap between train and test.")

    # Calibrate Energy Gate on Training Set ONLY (Zero Leakage)
    energy_indices = [k * 6 + 5 for k in range(8)]
    clear_max_v = np.max(X_train[y_train == "CLEAR"][:, energy_indices], axis=1)
    occ_max_v = np.max(X_train[y_train != "CLEAR"][:, energy_indices], axis=1)

    calibrated_th = 1.80
    best_j = -1.0
    for th in np.linspace(0.5, 6.0, 56):
        spec = float(np.mean(clear_max_v < th))
        sens = float(np.mean(occ_max_v >= th))
        j = spec + sens - 1.0
        if j > best_j:
            best_j = j
            calibrated_th = float(th)

    print(f"\n[*] Calibrated CLEAR Energy Gate on Training Set: threshold = {calibrated_th:.2f} (Train Youden J = {best_j:.3f})")

    # Multi-Model Benchmark Comparison (Phase 2B)
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    import subprocess

    candidate_models = {
        "hist_gradient": HistGradientBoostingClassifier(max_iter=100, learning_rate=0.1, random_state=42),
        "random_forest": RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42),
        "logistic_regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=42))
    }

    comparison_results = {}
    print("\n" + "=" * 78)
    print("           MULTI-MODEL BENCHMARK COMPARISON ON FROZEN HELD-OUT SPLIT")
    print("=" * 78)
    print(f"{'Model / Approach':<24} | {'Ungated Acc':<11} | {'Gated Acc':<11} | {'CLEAR Recall':<13} | {'CLEAR FPR':<10}")
    print("-" * 78)

    # Evaluate Heuristic SpatialBaseline
    b_acc = accuracy_score(y_test, b_test) * 100.0
    b_cm = confusion_matrix(y_test, b_test, labels=unique_classes)
    b_clear_rec = (b_cm[0, 0] / float(np.sum(b_cm[0]))) * 100.0 if np.sum(b_cm[0]) > 0 else 0.0
    b_clear_fpr = 100.0 - b_clear_rec
    comparison_results["SpatialBaseline"] = {
        "ungated_acc": round(b_acc, 2),
        "gated_acc": round(b_acc, 2),
        "clear_recall": round(b_clear_rec, 2),
        "clear_fpr": round(b_clear_fpr, 2)
    }
    print(f"{'SpatialBaseline (Heuristic)':<24} | {b_acc:<11.2f} | {b_acc:<11.2f} | {b_clear_rec:<.1f}% ({b_cm[0,0]}/{np.sum(b_cm[0])}) | {b_clear_fpr:<.1f}%")

    fitted_models = {}
    for m_key, m_clf in candidate_models.items():
        m_clf.fit(X_train, y_train)
        fitted_models[m_key] = m_clf

        pred_ungated = m_clf.predict(X_test)
        acc_u = accuracy_score(y_test, pred_ungated) * 100.0
        cm_u = confusion_matrix(y_test, pred_ungated, labels=unique_classes)

        # Apply frozen calibrated gate: if max link variance < threshold -> CLEAR
        gate_mask = np.max(X_test[:, energy_indices], axis=1) < calibrated_th
        pred_gated = np.copy(pred_ungated)
        pred_gated[gate_mask] = "CLEAR"

        acc_g = accuracy_score(y_test, pred_gated) * 100.0
        cm_g = confusion_matrix(y_test, pred_gated, labels=unique_classes)
        clear_rec_g = (cm_g[0, 0] / float(np.sum(cm_g[0]))) * 100.0 if np.sum(cm_g[0]) > 0 else 0.0
        clear_fpr_g = 100.0 - clear_rec_g

        comparison_results[m_key] = {
            "ungated_acc": round(acc_u, 2),
            "gated_acc": round(acc_g, 2),
            "clear_recall": round(clear_rec_g, 2),
            "clear_fpr": round(clear_fpr_g, 2),
            "confusion_matrix_gated": cm_g.tolist()
        }
        print(f"{m_clf.__class__.__name__:<24} | {acc_u:<11.2f} | {acc_g:<11.2f} | {clear_rec_g:<.1f}% ({cm_g[0,0]}/{np.sum(cm_g[0])}) | {clear_fpr_g:<.1f}%")

    print("=" * 78)

    # Primary Model Selection
    clf = fitted_models.get(classifier_type, fitted_models["hist_gradient"])
    y_pred = clf.predict(X_test)
    learned_acc = accuracy_score(y_test, y_pred) * 100.0
    learned_f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0) * 100.0

    # Gated Predictions for Primary Model
    gate_mask_test = np.max(X_test[:, energy_indices], axis=1) < calibrated_th
    y_pred_gated = np.copy(y_pred)
    y_pred_gated[gate_mask_test] = "CLEAR"
    gated_acc = accuracy_score(y_test, y_pred_gated) * 100.0
    gated_f1 = f1_score(y_test, y_pred_gated, average="weighted", zero_division=0) * 100.0

    print(f"\n--- Primary Model: {clf.__class__.__name__} ---")
    print(f"  Ungated Accuracy:  {learned_acc:.2f}%  (Weighted F1: {learned_f1:.2f}%)")
    print(f"  Gated Accuracy:    {gated_acc:.2f}%  (Weighted F1: {gated_f1:.2f}%)")
    print("\n--- Gated Model Classification Report ---")
    print(classification_report(y_test, y_pred_gated, zero_division=0))

    cm_primary = confusion_matrix(y_test, y_pred_gated, labels=unique_classes)
    print("--- Gated Confusion Matrix (Labels: " + ", ".join(unique_classes) + ") ---")
    print(cm_primary)

    # Retrieve Git Commit Hash for Complete Provenance
    try:
        git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip()
    except Exception:
        git_commit = "unknown"

    from spatial.features import FEATURE_SCHEMA_VERSION, get_feature_names

    # Save Model Artifacts
    model_payload = {
        "model": clf,
        "classes": list(unique_classes),
        "feature_dim": 56,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "feature_names": get_feature_names(),
        "classifier_name": clf.__class__.__name__,
        "train_sessions": list(train_sessions),
        "test_sessions": list(test_sessions),
        "calibrated_energy_gate_threshold": round(calibrated_th, 4),
        "test_accuracy": round(learned_acc, 2),
        "test_f1": round(learned_f1, 2),
        "gated_test_accuracy": round(gated_acc, 2),
        "gated_test_f1": round(gated_f1, 2),
        "baseline_test_accuracy": round(b_acc, 2),
        "session_wise_split": True,
        "leakage_prevented": True,
        "git_commit": git_commit,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }

    with open(model_out, "wb") as f:
        pickle.dump(model_payload, f)
    print(f"\n[+] Trained model saved to: {model_out}")

    scorecard = {
        "model_name": "WiMotion 2.0 Supervised Spatial Classifier",
        "created_at": model_payload["created_at"],
        "git_commit": git_commit,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "classifier": model_payload["classifier_name"],
        "feature_dimension": 56,
        "unique_classes": unique_classes,
        "train_sessions": list(train_sessions),
        "test_sessions": list(test_sessions),
        "calibrated_energy_gate_threshold": round(calibrated_th, 4),
        "metrics": {
            "learned_accuracy_pct": round(learned_acc, 2),
            "learned_weighted_f1_pct": round(learned_f1, 2),
            "gated_accuracy_pct": round(gated_acc, 2),
            "gated_weighted_f1_pct": round(gated_f1, 2),
            "heuristic_baseline_accuracy_pct": round(b_acc, 2),
            "heuristic_baseline_f1_pct": round(f1_score(y_test, b_test, average="weighted", zero_division=0) * 100.0, 2)
        },
        "model_comparison": comparison_results,
        "session_leakage_prevented": True
    }

    with open(scorecard_out, "w", encoding="utf-8") as f:
        json.dump(scorecard, f, indent=2)
    print(f"[+] Scorecard written to: {scorecard_out}")
    print("=" * 78)
    return 0


def main():
    parser = argparse.ArgumentParser(description="WiMotion 2.0 Supervised Spatial Model Trainer")
    parser.add_argument("--model-out", type=Path, default=DEFAULT_MODEL_OUT, help="Output path for trained model")
    parser.add_argument("--scorecard-out", type=Path, default=DEFAULT_SCORECARD_OUT, help="Output path for scorecard JSON")
    parser.add_argument("--classifier", type=str, choices=["hist_gradient", "random_forest", "logistic_regression"], default="hist_gradient")
    parser.add_argument("--dataset", type=str, choices=["phase_b", "audited", "all"], default="phase_b",
                        help="Dataset: 'phase_b' (10 fresh controlled takes), 'audited' (manual_gt_v1), or 'all'")
    parser.add_argument("--split-strategy", type=str, choices=["take", "group_shuffle"], default="take",
                        help="Split strategy: 'take' (Take 01 train, Take 02 test) or 'group_shuffle'")
    parser.add_argument("--test-size", type=float, default=0.25, help="Fraction of sessions reserved for testing (if group_shuffle)")
    args = parser.parse_args()

    recordings = list_recordings()
    # Filter sessions suitable for multi-link spatial training
    if args.dataset == "phase_b":
        trainable_sessions = [r for r in recordings if r.get("session_id", "").startswith("session_pB_")]
    elif args.dataset == "audited":
        manifest_p = ROOT / "data" / "processed" / "manual_gt_v1" / "manifest.csv"
        if manifest_p.exists():
            import pandas as pd
            df_m = pd.read_csv(manifest_p)
            valid_ids = set(df_m[df_m["audited_status"] == "ELIGIBLE"]["session_id"].tolist())
            trainable_sessions = [r for r in recordings if r.get("session_id") in valid_ids]
        else:
            trainable_sessions = [r for r in recordings if r.get("session_id", "").startswith("session_pB_") or r.get("session_id") in ["session_real_006_tx2_walk", "session_real_007_tx4_walk"]]
    else:
        trainable_sessions = []
        for r in recordings:
            sid = r.get("session_id", "")
            if sid in ["benchmark_session_01", "synthetic_session_01", "public_esp_fi_01", "held_out_empty_01", "held_out_walking_01"] or sid.startswith("session_real_") or sid.startswith("session_pB_"):
                trainable_sessions.append(r)

    return train_spatial_pipeline(
        sessions=trainable_sessions,
        model_out=args.model_out,
        scorecard_out=args.scorecard_out,
        classifier_type=args.classifier,
        test_size=args.test_size,
        split_strategy=args.split_strategy
    )


if __name__ == "__main__":
    sys.exit(main())

