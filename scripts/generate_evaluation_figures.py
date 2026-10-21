"""
WiMotion 2.0 - High-Resolution Dissertation Evaluation Figures Generator
Produces publication-grade plots from models/spatial_model_scorecard.json
"""

import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

ROOT = Path(__file__).resolve().parent.parent
SCORECARD_PATH = ROOT / "models" / "spatial_model_scorecard.json"
ASSETS_DIR = ROOT / "docs" / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Academic Color Palette
COLOR_NAVY = "#1B365D"
COLOR_SLATE = "#2C3E50"
COLOR_ACCENT = "#2980B9"
COLOR_ALERT = "#C0392B"
COLOR_MUTED = "#7F8C8D"
COLOR_LIGHT = "#ECF0F1"

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.edgecolor"] = "#BDC3C7"
plt.rcParams["axes.linewidth"] = 0.8


def generate_confusion_matrix(scorecard):
    rf_data = scorecard["model_comparison"]["random_forest"]
    cm = np.array(rf_data["confusion_matrix_gated"])
    classes = scorecard["unique_classes"]

    fig, ax = plt.subplots(figsize=(6.5, 5.5), dpi=300)
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=classes,
        yticklabels=classes,
        title="WiMotion 2.0 - Gated 5-Class Confusion Matrix (Held-Out Test Take 02)",
        ylabel="True Class (Ground Truth)",
        xlabel="Predicted Class (Model Inference)",
    )

    ax.title.set_fontsize(11)
    ax.title.set_fontweight("bold")
    ax.xaxis.label.set_fontsize(10)
    ax.yaxis.label.set_fontsize(10)

    # Loop over data dimensions and create text annotations
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        row_sum = cm[i].sum()
        for j in range(cm.shape[1]):
            val = cm[i, j]
            pct = (val / row_sum) * 100.0 if row_sum > 0 else 0
            text_color = "white" if val > thresh else "black"
            ax.text(
                j,
                i,
                f"{val}\n({pct:.1f}%)",
                ha="center",
                va="center",
                color=text_color,
                fontsize=9,
                fontweight="bold" if i == j else "normal",
            )

    fig.tight_layout()
    out_path = ASSETS_DIR / "fig_6_1_confusion_matrix.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[+] Saved Confusion Matrix to {out_path}")


def generate_model_comparison(scorecard):
    models = [
        "Uniform Random\nChance Baseline",
        "Physical Heuristic\nRatio Baseline",
        "HistGradient\nBoosting (Gated)",
        "Logistic\nRegression (Gated)",
        "Random Forest\n(Ungated ML)",
        "Random Forest\n(Gated Primary)",
    ]
    accuracies = [20.00, 29.26, 48.10, 49.42, 50.91, 49.26]
    colors = [COLOR_MUTED, "#E67E22", COLOR_ACCENT, "#8E44AD", "#16A085", COLOR_NAVY]

    fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=300)
    bars = ax.bar(models, accuracies, color=colors, width=0.55, edgecolor="#34495E", linewidth=0.8)

    ax.set_ylabel("5-Class Spatial Accuracy (%)", fontsize=10, fontweight="bold")
    ax.set_title("Model Architecture Performance Comparison on Held-Out Test Set", fontsize=11, fontweight="bold", pad=12)
    ax.set_ylim(0, 65)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Add reference line for random chance
    ax.axhline(20.0, color=COLOR_ALERT, linestyle=":", linewidth=1.2, label="Random Guessing Baseline (20.0%)")
    ax.axhline(29.26, color="#D35400", linestyle="--", linewidth=1.2, label="Physical Heuristic Baseline (29.26%)")

    for bar in bars:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            h + 1.2,
            f"{h:.2f}%",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
        )

    ax.legend(loc="upper left", framealpha=0.9, fontsize=8.5)
    fig.tight_layout()
    out_path = ASSETS_DIR / "fig_6_2_model_comparison.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[+] Saved Model Comparison to {out_path}")


def generate_per_zone_recall(scorecard):
    classes = ["CLEAR\n(Empty Room)", "Zone 1\n(North-East)", "Zone 2\n(North-West)", "Zone 3\n(South-West)", "Zone 4\n(South-East)"]
    recalls = [47.11, 50.41, 53.72, 14.05, 80.99]
    colors = ["#34495E", "#2980B9", "#27AE60", "#E74C3C", "#8E44AD"]

    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=300)
    bars = ax.bar(classes, recalls, color=colors, width=0.52, edgecolor="#2C3E50", linewidth=0.8)

    ax.set_ylabel("True Class Recall Sensitivity (%)", fontsize=10, fontweight="bold")
    ax.set_title("Per-Class Spatial Recall Sensitivity (Held-Out Test Set)", fontsize=11, fontweight="bold", pad=12)
    ax.set_ylim(0, 95)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            h + 1.5,
            f"{h:.2f}%",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
        )

    # Annotation for Zone 3 and Zone 4
    ax.annotate(
        "Max Sensitivity (80.99%)\nShort baseline proximity",
        xy=(4, 82),
        xytext=(3.4, 88),
        arrowprops=dict(facecolor="black", shrink=0.05, width=0.8, headwidth=4),
        fontsize=8.5,
        fontweight="bold",
        color="#8E44AD",
    )
    ax.annotate(
        "Diagonal Path Attenuation\n(Weakest diagonal link)",
        xy=(3, 15),
        xytext=(2.3, 30),
        arrowprops=dict(facecolor="black", shrink=0.05, width=0.8, headwidth=4),
        fontsize=8.5,
        fontweight="bold",
        color="#C0392B",
    )

    fig.tight_layout()
    out_path = ASSETS_DIR / "fig_6_3_per_zone_recall.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[+] Saved Per-Zone Recall to {out_path}")


def generate_false_alarm_reduction():
    labels = ["Ungated ML Classifier\n(Overfitting to Silicon Noise)", "Gated Primary Classifier\n(Calibrated Youden J Threshold theta=1.80)"]
    false_alarms = [98.35, 52.89]
    true_recalls = [1.65, 47.11]

    x = np.arange(len(labels))
    width = 0.32

    fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=300)
    rects1 = ax.bar(x - width/2, false_alarms, width, label="False Alarm Rate (Lower is Better)", color="#E74C3C", edgecolor="#922B21", linewidth=0.8)
    rects2 = ax.bar(x + width/2, true_recalls, width, label="True Empty-Room Recall (Higher is Better)", color="#27AE60", edgecolor="#196F3D", linewidth=0.8)

    ax.set_ylabel("Percentage (%)", fontsize=10, fontweight="bold")
    ax.set_title("Impact of Empirical Energy Gating on Empty-Room Classification", fontsize=11, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.5)
    ax.set_ylim(0, 115)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend(loc="upper center", framealpha=0.9, fontsize=9)

    for rect in rects1:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., h + 1.5, f"{h:.2f}%", ha="center", va="bottom", fontsize=9.5, fontweight="bold", color="#C0392B")

    for rect in rects2:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., h + 1.5, f"{h:.2f}%", ha="center", va="bottom", fontsize=9.5, fontweight="bold", color="#27AE60")

    fig.tight_layout()
    out_path = ASSETS_DIR / "fig_6_4_false_alarm_reduction.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[+] Saved False Alarm Reduction Plot to {out_path}")


if __name__ == "__main__":
    with open(SCORECARD_PATH) as f:
        scorecard = json.load(f)

    generate_confusion_matrix(scorecard)
    generate_model_comparison(scorecard)
    generate_per_zone_recall(scorecard)
    generate_false_alarm_reduction()
    print("[+] All 4 evaluation figures generated successfully!")
