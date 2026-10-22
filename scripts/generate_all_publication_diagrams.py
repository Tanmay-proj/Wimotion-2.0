# -*- coding: utf-8 -*-
"""
generate_all_publication_diagrams.py
Generates 12 publication-quality technical diagrams for WiMotion 2.0 dissertation
following the user's MASTER PROMPT:
- Preserves 100% of technical labels, equations, variables, and numerical values.
- Academic Navy (#1B365D), Slate (#334155), Blue accent (#2563EB), Clean white background.
- High-resolution 300 DPI output suitable for university engineering report insertion.
"""
import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

OUTPUT_DIR = Path(r"e:\WIFI_INTERFEROMETRIC_NEURAL_SENSING\wimotion_2.0\docs\figures\generated_diagrams")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['mathtext.fontset'] = 'dejavusans'

COLOR_NAVY = "#1B365D"       # Primary deep academic navy
COLOR_SLATE = "#334155"      # Secondary slate grey
COLOR_MUTED = "#64748B"      # Muted grey
COLOR_BLUE = "#2563EB"       # Bright tech blue accent
COLOR_SKY = "#0284C7"        # Sky accent
COLOR_GREEN = "#16A34A"      # Active / TX green
COLOR_RED = "#DC2626"        # Alert / highlight red
COLOR_AMBER = "#D97706"      # Warning amber
COLOR_BG_LIGHT = "#F8FAFC"   # Light container fill
COLOR_BORDER = "#CBD5E1"     # Border grey
COLOR_BODY = "#1E293B"       # Body text dark slate


def save_fig(fig, filename):
    out_path = OUTPUT_DIR / filename
    plt.tight_layout()
    plt.savefig(str(out_path), dpi=300, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close(fig)
    print(f"[+] Generated: {filename} ({os.path.getsize(out_path):,} bytes)")


# =============================================================================
# 1. PROJECT EVOLUTION TIMELINE (Figure 1.3)
# =============================================================================
def generate_diagram_1_evolution():
    fig, ax = plt.subplots(figsize=(11.0, 3.8), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    stages = [
        {
            "phase": "PHASE 1 (2024)",
            "title": "PROJECT ECHO",
            "sub": "Single-Link Feasibility",
            "items": ["1 TX ➔ 1 RX ESP32 Link", "Raw Subcarrier Perturbation", "Direct LOS Variance", "Critical Blind Spot Discovery"],
            "color": "#64748B"
        },
        {
            "phase": "PHASE 2 (Early 2025)",
            "title": "PROJECT SHADOW",
            "sub": "Multipath & Drift Study",
            "items": ["Silicon Thermal Baseline Drift", "Static Multipath Fading", "Moving-Average Filters", "Signal Normalization Bounds"],
            "color": "#0284C7"
        },
        {
            "phase": "PHASE 3 (Mid 2025)",
            "title": "WIMOTION 1.0",
            "sub": "Temporal ML Engine",
            "items": ["217-D Temporal Features", "HistGradientBoosting Classifier", "81.25% Binary Accuracy", "Binary Only: Zero Spatial Info"],
            "color": "#2563EB"
        },
        {
            "phase": "PHASE 4 (Oct 2026)",
            "title": "WIMOTION 2.0",
            "sub": "Multi-Link Star Mesh",
            "items": ["8 Distributed Spatial Links", "4-Quadrant Grid (Z1–Z4)", "56-D Canonical Feature Vector", "Youden J Calibrated Energy Gate"],
            "color": COLOR_NAVY
        }
    ]

    card_w, card_h = 2.35, 3.0
    start_x = 0.4
    spacing = 2.65

    for idx, s in enumerate(stages):
        cx = start_x + idx * spacing
        cy = 0.4
        
        is_final = (idx == 3)
        bg_col = "#EFF6FF" if is_final else "#F8FAFC"
        border_col = COLOR_NAVY if is_final else COLOR_BORDER
        lw = 2.2 if is_final else 1.4

        card = patches.FancyBboxPatch((cx, cy), card_w, card_h, boxstyle="round,pad=0.08",
                                     edgecolor=border_col, facecolor=bg_col, linewidth=lw, zorder=2)
        ax.add_patch(card)

        header_bg = s["color"]
        h_box = patches.FancyBboxPatch((cx + 0.08, cy + card_h - 0.72), card_w - 0.16, 0.64,
                                      boxstyle="round,pad=0.05", edgecolor=header_bg, facecolor=header_bg, zorder=3)
        ax.add_patch(h_box)

        ax.text(cx + card_w/2, cy + card_h - 0.28, s["phase"], fontsize=8.0, fontweight='bold', color='#E2E8F0', ha='center', zorder=4)
        ax.text(cx + card_w/2, cy + card_h - 0.54, s["title"], fontsize=10.0, fontweight='bold', color='#FFFFFF', ha='center', zorder=4)
        ax.text(cx + card_w/2, cy + card_h - 0.95, s["sub"], fontsize=9.0, fontweight='bold', color=COLOR_NAVY if is_final else COLOR_SLATE, ha='center', zorder=4)

        for b_idx, item in enumerate(s["items"]):
            by = cy + card_h - 1.35 - b_idx * 0.40
            ax.text(cx + 0.18, by, "•", fontsize=10.0, color=s["color"], fontweight='bold', zorder=4)
            ax.text(cx + 0.32, by, item, fontsize=7.8, color=COLOR_SLATE, zorder=4)

        if idx < len(stages) - 1:
            ax.annotate("", xy=(cx + card_w + 0.22, cy + card_h/2), xytext=(cx + card_w + 0.04, cy + card_h/2),
                        arrowprops=dict(arrowstyle="->", color=COLOR_SLATE, lw=2.0), zorder=5)

    ax.set_xlim(0.1, 10.9)
    ax.set_ylim(0.1, 3.6)
    ax.axis('off')
    save_fig(fig, "diagram_1_project_evolution.png")


# =============================================================================
# 2. RSSI VS CSI COMPARISON (Figure 2.3)
# =============================================================================
def generate_diagram_2_rssi_vs_csi():
    fig, ax = plt.subplots(figsize=(10.5, 4.4), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    card_w, card_h = 4.4, 3.7
    rssi_x, rssi_y = 0.5, 0.4
    r_box = patches.FancyBboxPatch((rssi_x, rssi_y), card_w, card_h, boxstyle="round,pad=0.08",
                                  edgecolor='#94A3B8', facecolor='#F8FAFC', linewidth=1.6, zorder=2)
    ax.add_patch(r_box)

    rh_box = patches.FancyBboxPatch((rssi_x + 0.1, rssi_y + card_h - 0.7), card_w - 0.2, 0.6,
                                   boxstyle="round,pad=0.05", edgecolor='#64748B', facecolor='#64748B', zorder=3)
    ax.add_patch(rh_box)
    ax.text(rssi_x + card_w/2, rssi_y + card_h - 0.4, "RSSI (Received Signal Strength Indicator)", 
            fontsize=10.0, fontweight='bold', color='#FFFFFF', ha='center', zorder=4)

    meter_box = patches.FancyBboxPatch((rssi_x + 0.8, rssi_y + card_h - 1.8), card_w - 1.6, 0.85,
                                      boxstyle="round,pad=0.05", edgecolor='#CBD5E1', facecolor='#FFFFFF', linewidth=1.2, zorder=3)
    ax.add_patch(meter_box)
    ax.text(rssi_x + card_w/2, rssi_y + card_h - 1.3, "-54 dBm", fontsize=18, fontweight='bold', color='#DC2626', ha='center', zorder=4)
    ax.text(rssi_x + card_w/2, rssi_y + card_h - 1.62, "Coarse 1-Dimensional Scalar Value", fontsize=8.0, color=COLOR_MUTED, ha='center', zorder=4)

    r_points = [
        "Single scalar averaged across full 20 MHz channel",
        "Subject to destructive multipath superposition",
        "High variance without motion; misses fine movements",
        "Coarse proximity only; cannot resolve spatial quadrant"
    ]
    for idx, pt in enumerate(r_points):
        py = rssi_y + card_h - 2.15 - idx * 0.38
        ax.text(rssi_x + 0.3, py, "✖", fontsize=9.0, color='#DC2626', zorder=4)
        ax.text(rssi_x + 0.6, py, pt, fontsize=8.2, color=COLOR_SLATE, zorder=4)

    vs_circle = patches.Circle((5.25, 2.25), radius=0.38, edgecolor=COLOR_NAVY, facecolor='#1B365D', zorder=5)
    ax.add_patch(vs_circle)
    ax.text(5.25, 2.25, "VS", fontsize=11, fontweight='bold', color='#FFFFFF', ha='center', va='center', zorder=6)

    csi_x, csi_y = 5.6, 0.4
    c_box = patches.FancyBboxPatch((csi_x, csi_y), card_w, card_h, boxstyle="round,pad=0.08",
                                  edgecolor=COLOR_NAVY, facecolor='#EFF6FF', linewidth=2.0, zorder=2)
    ax.add_patch(c_box)

    ch_box = patches.FancyBboxPatch((csi_x + 0.1, csi_y + card_h - 0.7), card_w - 0.2, 0.6,
                                   boxstyle="round,pad=0.05", edgecolor=COLOR_NAVY, facecolor=COLOR_NAVY, zorder=3)
    ax.add_patch(ch_box)
    ax.text(csi_x + card_w/2, csi_y + card_h - 0.4, "CSI (Channel State Information)", 
            fontsize=10.0, fontweight='bold', color='#FFFFFF', ha='center', zorder=4)

    sub_box = patches.FancyBboxPatch((csi_x + 0.4, csi_y + card_h - 1.8), card_w - 0.8, 0.85,
                                    boxstyle="round,pad=0.05", edgecolor='#93C5FD', facecolor='#FFFFFF', linewidth=1.2, zorder=3)
    ax.add_patch(sub_box)

    np.random.seed(42)
    amps = 12 + 8 * np.sin(np.linspace(0, np.pi, 32)) + np.random.normal(0, 1.2, 32)
    bar_x_start = csi_x + 0.6
    bar_spacing = 3.2 / 32
    for b_idx in range(32):
        bx = bar_x_start + b_idx * bar_spacing
        bh = max(0.1, amps[b_idx] / 35.0 * 0.45)
        ax.add_patch(patches.Rectangle((bx, csi_y + card_h - 1.7), bar_spacing * 0.75, bh, 
                                       facecolor=COLOR_BLUE, edgecolor='none', zorder=4))

    ax.text(csi_x + card_w/2, csi_y + card_h - 1.15, r"64-Subcarrier Matrix: $H_k = |a_k| e^{j \angle \phi_k}$", 
            fontsize=8.5, fontweight='bold', color=COLOR_NAVY, ha='center', zorder=5)

    c_points = [
        "Captures fine-grained frequency-domain subcarrier response",
        "Separates static multipath reflections from dynamic human motion",
        "Subcarrier diversity resolves micro-Doppler perturbations",
        "Powers multi-link spatial classification into 4 quadrants"
    ]
    for idx, pt in enumerate(c_points):
        py = csi_y + card_h - 2.15 - idx * 0.38
        ax.text(csi_x + 0.3, py, "✔", fontsize=9.0, color='#16A34A', zorder=4)
        ax.text(csi_x + 0.6, py, pt, fontsize=8.2, color=COLOR_SLATE, zorder=4)

    ax.set_xlim(0.2, 10.3)
    ax.set_ylim(0.2, 4.3)
    ax.axis('off')
    save_fig(fig, "diagram_2_rssi_vs_csi.png")


# =============================================================================
# 3. FRESNEL ZONE GEOMETRY (Figure 2.1 - The user's uploaded example)
# =============================================================================
def generate_diagram_3_fresnel():
    fig, ax = plt.subplots(figsize=(10.5, 4.6), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    
    tx_x, tx_y = 1.2, 2.0
    rx_x, rx_y = 7.8, 2.0
    mid_x = (tx_x + rx_x) / 2.0
    mid_y = 2.0
    
    a = (rx_x - tx_x) / 2.0 + 0.35  # semi-major axis
    b = 1.30                        # semi-minor axis
    
    # 1st Fresnel Zone Ellipse
    ellipse = patches.Ellipse((mid_x, mid_y), width=2*a, height=2*b, 
                              edgecolor=COLOR_NAVY, facecolor='#E0F2FE', 
                              alpha=0.65, linestyle='--', linewidth=2.2, zorder=2)
    ax.add_patch(ellipse)
    
    # 2nd Fresnel Zone boundary
    ellipse_outer = patches.Ellipse((mid_x, mid_y), width=2*(a+0.45), height=2*(b+0.45), 
                                    edgecolor='#94A3B8', facecolor='none', 
                                    linestyle=':', linewidth=1.3, alpha=0.6, zorder=1)
    ax.add_patch(ellipse_outer)

    # Direct LOS Baseline
    ax.plot([tx_x, rx_x], [tx_y, rx_y], color=COLOR_NAVY, linewidth=2.8, linestyle='-', zorder=3)
    
    # Midpoint and radius r1 dimension line
    ax.plot([mid_x, mid_x], [mid_y, mid_y + b], color=COLOR_RED, linewidth=2.0, linestyle='-', zorder=4)
    ax.scatter([mid_x], [mid_y + b], color=COLOR_RED, s=40, zorder=5)
    
    # r1 annotation card
    r1_box = patches.FancyBboxPatch((mid_x + 0.15, mid_y + 0.35), 2.2, 0.65, boxstyle="round,pad=0.06",
                                   edgecolor='#FCA5A5', facecolor='#FEF2F2', linewidth=1.2, zorder=5)
    ax.add_patch(r1_box)
    ax.text(mid_x + 0.25, mid_y + 0.73, r"Max Radius $r_1 \approx 0.35\mathrm{\ m\ (35\ cm)}$", 
            fontsize=9.0, fontweight='bold', color='#991B1B', zorder=6)
    ax.text(mid_x + 0.25, mid_y + 0.47, r"$r_1 = \frac{1}{2}\sqrt{\lambda D}\quad (n=1\mathrm{\ at\ midpoint})$", 
            fontsize=8.5, color='#B91C1C', zorder=6)

    # Point P on the boundary
    px = mid_x - 1.8
    py = mid_y + b * np.sqrt(max(0, 1 - ((px - mid_x)/a)**2))
    ax.plot([tx_x, px], [tx_y, py], color=COLOR_BLUE, linewidth=1.8, linestyle='--', zorder=4)
    ax.plot([px, rx_x], [py, rx_y], color=COLOR_BLUE, linewidth=1.8, linestyle='--', zorder=4)
    ax.scatter([px], [py], color=COLOR_BLUE, s=55, zorder=6)
    
    # Ray labels
    ax.text((tx_x + px)/2 - 0.25, (tx_y + py)/2 + 0.15, r"$d_1$", fontsize=11, fontweight='bold', color=COLOR_BLUE)
    ax.text((px + rx_x)/2 - 0.3, (py + rx_y)/2 + 0.25, r"$d_2$", fontsize=11, fontweight='bold', color=COLOR_BLUE)
    ax.text(px, py + 0.16, r"Boundary Point $P(x, y)$", fontsize=9.5, fontweight='bold', color=COLOR_SLATE, ha='center')

    # TX Node box & label
    tx_w, tx_h = 1.4, 0.85
    tx_box = patches.FancyBboxPatch((tx_x - tx_w, tx_y - tx_h/2), tx_w, tx_h, boxstyle="round,pad=0.06",
                                   edgecolor=COLOR_NAVY, facecolor='#F8FAFC', linewidth=1.8, zorder=5)
    ax.add_patch(tx_box)
    ax.scatter([tx_x], [tx_y], color=COLOR_GREEN, s=70, edgecolors=COLOR_NAVY, linewidths=1.8, zorder=6)
    ax.text(tx_x - tx_w/2, tx_y + 0.14, "TX Node", fontsize=10.5, fontweight='bold', color=COLOR_NAVY, ha='center', zorder=6)
    ax.text(tx_x - tx_w/2, tx_y - 0.18, r"$(x_{tx}, y_{tx})$", fontsize=9.0, color=COLOR_SLATE, ha='center', zorder=6)
    
    # RX Node box & label
    rx_w, rx_h = 1.4, 0.85
    rx_box = patches.FancyBboxPatch((rx_x, rx_y - rx_h/2), rx_w, rx_h, boxstyle="round,pad=0.06",
                                   edgecolor=COLOR_NAVY, facecolor='#F8FAFC', linewidth=1.8, zorder=5)
    ax.add_patch(rx_box)
    ax.scatter([rx_x], [rx_y], color=COLOR_BLUE, s=70, edgecolors=COLOR_NAVY, linewidths=1.8, zorder=6)
    ax.text(rx_x + rx_w/2, rx_y + 0.14, "RX Node", fontsize=10.5, fontweight='bold', color=COLOR_NAVY, ha='center', zorder=6)
    ax.text(rx_x + rx_w/2, rx_y - 0.18, r"$(x_{rx}, y_{rx})$", fontsize=9.0, color=COLOR_SLATE, ha='center', zorder=6)

    # Top title banner box
    top_w, top_h = 6.4, 0.65
    top_box = patches.FancyBboxPatch((mid_x - top_w/2, 3.75), top_w, top_h, boxstyle="round,pad=0.08",
                                    edgecolor=COLOR_NAVY, facecolor=COLOR_NAVY, linewidth=1.5, zorder=5)
    ax.add_patch(top_box)
    ax.text(mid_x, 3.75 + top_h/2, r"1st FRESNEL ZONE BOUNDARY ($n = 1$) :  $d_1 + d_2 = D + \frac{\lambda}{2}$", 
            fontsize=10.5, fontweight='bold', color='#FFFFFF', ha='center', va='center', zorder=6)

    # Direct LOS Baseline Label
    ax.text(mid_x, mid_y - 0.32, r"Direct Line-of-Sight Baseline ($D = 4.0\mathrm{\ m}$)", 
            fontsize=10.0, fontweight='bold', color=COLOR_NAVY, ha='center')
    ax.text(mid_x, mid_y - 0.58, r"RF Operating Parameters: $f = 2.437\mathrm{\ GHz\ (Channel\ 6)},\ \lambda = \frac{c}{f} \approx 0.123\mathrm{\ m\ (12.3\ cm)}$", 
            fontsize=8.5, color=COLOR_SLATE, ha='center')

    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(1.1, 4.6)
    ax.axis('off')
    save_fig(fig, "diagram_3_fresnel_zone_geometry.png")


# =============================================================================
# 4. SINGLE-LINK VS MULTI-LINK (Figure 2.2)
# =============================================================================
def generate_diagram_4_single_vs_multilink():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.8), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    for ax in (ax1, ax2):
        ax.set_facecolor('#FFFFFF')
        ax.set_aspect('equal')
        ax.set_xlim(-0.3, 5.3)
        ax.set_ylim(-0.2, 5.3)
        ax.axis('off')

    # LEFT: Single Link Ambiguity
    ax1.plot([0.2, 4.8, 4.8, 0.2, 0.2], [0.5, 0.5, 4.7, 4.7, 0.5], color=COLOR_BORDER, lw=1.6)
    tx_pt, rx_pt = np.array([0.7, 2.6]), np.array([4.3, 2.6])
    ax1.plot([tx_pt[0], rx_pt[0]], [tx_pt[1], rx_pt[1]], color=COLOR_NAVY, lw=2.5)
    el = patches.Ellipse((2.5, 2.6), 3.8, 1.2, color='#E0F2FE', alpha=0.55, ls='--', ec=COLOR_NAVY, lw=1.5)
    ax1.add_patch(el)
    
    # Blind spot areas in corners
    for bx, by in [(1.2, 3.9), (3.8, 3.9), (1.2, 1.3), (3.8, 1.3)]:
        ax1.add_patch(patches.Circle((bx, by), 0.55, color='#FEE2E2', alpha=0.75, ls=':', ec='#EF4444', lw=1.2))
        ax1.text(bx, by, "BLIND\nSPOT", fontsize=7.2, color='#991B1B', fontweight='bold', ha='center', va='center')

    ax1.scatter([tx_pt[0]], [tx_pt[1]], color=COLOR_GREEN, s=75, ec=COLOR_NAVY, zorder=5)
    ax1.scatter([rx_pt[0]], [rx_pt[1]], color=COLOR_BLUE, s=75, ec=COLOR_NAVY, zorder=5)
    ax1.text(tx_pt[0], tx_pt[1] - 0.38, "TX", fontsize=9.5, fontweight='bold', ha='center')
    ax1.text(rx_pt[0], rx_pt[1] - 0.38, "RX", fontsize=9.5, fontweight='bold', ha='center')

    tb1 = patches.FancyBboxPatch((0.2, 4.75), 4.6, 0.45, boxstyle="round,pad=0.04", fc='#64748B', ec='none')
    ax1.add_patch(tb1)
    ax1.text(2.5, 4.97, "SINGLE-LINK AMBIGUITY (1 LINK)", fontsize=9.0, fontweight='bold', color='#FFFFFF', ha='center', va='center')
    ax1.text(2.5, 0.20, "Severe Corner Blind Spots; Zero Spatial Resolution", fontsize=8.0, color=COLOR_MUTED, ha='center')

    # RIGHT: Multi-Link Spatial Mesh Coverage
    ax2.plot([0.2, 4.8, 4.8, 0.2, 0.2], [0.5, 0.5, 4.7, 4.7, 0.5], color=COLOR_BORDER, lw=1.6)
    
    tx_corners = {
        "TX2 (NW)": (0.8, 4.0),
        "TX1 (NE)": (4.2, 4.0),
        "TX3 (SW)": (0.8, 1.2),
        "TX4 (SE)": (4.2, 1.2)
    }
    rx1, rx2 = (2.2, 2.8), (2.8, 2.4)

    link_colors = ['#2563EB', '#0284C7', '#059669', '#D97706', '#7C3AED', '#DB2777', '#475569', '#0891B2']
    c_idx = 0
    for t_name, t_pos in tx_corners.items():
        ax2.plot([t_pos[0], rx1[0]], [t_pos[1], rx1[1]], color=link_colors[c_idx % len(link_colors)], lw=1.8, alpha=0.9)
        c_idx += 1
        ax2.plot([t_pos[0], rx2[0]], [t_pos[1], rx2[1]], color=link_colors[c_idx % len(link_colors)], lw=1.8, alpha=0.9, ls='--')
        c_idx += 1

    for t_name, t_pos in tx_corners.items():
        ax2.scatter([t_pos[0]], [t_pos[1]], color=COLOR_GREEN, s=75, ec=COLOR_NAVY, zorder=5)
        ax2.text(t_pos[0], t_pos[1] + (0.24 if t_pos[1] > 2.6 else -0.32), t_name.split()[0], fontsize=8.5, fontweight='bold', ha='center')

    ax2.scatter([rx1[0]], [rx1[1]], color=COLOR_BLUE, s=75, ec=COLOR_NAVY, zorder=5)
    ax2.scatter([rx2[0]], [rx2[1]], color='#9333EA', s=75, ec=COLOR_NAVY, zorder=5)
    ax2.text(rx1[0] - 0.35, rx1[1], "RX1", fontsize=8.0, fontweight='bold', color=COLOR_BLUE)
    ax2.text(rx2[0] + 0.15, rx2[1], "RX2", fontsize=8.0, fontweight='bold', color='#9333EA')

    ax2.plot([2.5, 2.5], [0.5, 4.7], color='#E2E8F0', lw=1.0, ls=':')
    ax2.plot([0.2, 4.8], [2.6, 2.6], color='#E2E8F0', lw=1.0, ls=':')

    tb2 = patches.FancyBboxPatch((0.2, 4.75), 4.6, 0.45, boxstyle="round,pad=0.04", fc=COLOR_NAVY, ec='none')
    ax2.add_patch(tb2)
    ax2.text(2.5, 4.97, "MULTI-LINK STAR MESH (8 SPATIAL LINKS)", fontsize=9.0, fontweight='bold', color='#FFFFFF', ha='center', va='center')
    ax2.text(2.5, 0.20, "Complete Spatial Mesh Grid; Resolves 4 Quadrants", fontsize=8.0, color=COLOR_NAVY, ha='center', fontweight='bold')

    save_fig(fig, "diagram_4_single_vs_multilink.png")


# =============================================================================
# 5. DISTRIBUTED STAR TOPOLOGY & 8 SPATIAL LINKS (Figure 3.7)
# =============================================================================
def generate_diagram_5_star_topology():
    fig, ax = plt.subplots(figsize=(10.5, 6.0), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    ax.plot([0.5, 9.5, 9.5, 0.5, 0.5], [0.5, 0.5, 5.5, 5.5, 0.5], color=COLOR_NAVY, lw=2.2)
    ax.text(5.0, 5.68, "ROOM_LAB_A : 4-Quadrant Multi-Link Sensing Domain (4.2m x 5.8m)", 
            fontsize=10.5, fontweight='bold', color=COLOR_NAVY, ha='center')

    ax.plot([5.0, 5.0], [0.5, 5.5], color='#94A3B8', lw=1.2, ls='--')
    ax.plot([0.5, 9.5], [3.0, 3.0], color='#94A3B8', lw=1.2, ls='--')

    # Watermarks placed in center of quadrants so they don't collide with corner cards
    ax.text(2.75, 3.75, "ZONE 2 (NW)", fontsize=13, fontweight='bold', color='#E2E8F0', ha='center')
    ax.text(7.25, 3.75, "ZONE 1 (NE)", fontsize=13, fontweight='bold', color='#E2E8F0', ha='center')
    ax.text(2.75, 2.25, "ZONE 3 (SW)", fontsize=13, fontweight='bold', color='#E2E8F0', ha='center')
    ax.text(7.25, 2.25, "ZONE 4 (SE)", fontsize=13, fontweight='bold', color='#E2E8F0', ha='center')

    tx_nodes = {
        "TX2 (Zone 2 NW)\nMAC: 1C:69:20:31:38:08": (1.4, 4.6),
        "TX1 (Zone 1 NE)\nMAC: BC:DD:C2:CC:49:F4": (8.6, 4.6),
        "TX3 (Zone 3 SW)\nMAC: 1C:69:20:31:4A:8C": (1.4, 1.4),
        "TX4 (Zone 4 SE)\nMAC: 1C:69:20:31:4C:E8": (8.6, 1.4)
    }
    
    rx1 = (4.7, 3.3)
    rx2 = (5.3, 2.7)

    links = [
        ("Link 1: RX1-TX2", tx_nodes["TX2 (Zone 2 NW)\nMAC: 1C:69:20:31:38:08"], rx1, '#2563EB', '-'),
        ("Link 5: RX2-TX2", tx_nodes["TX2 (Zone 2 NW)\nMAC: 1C:69:20:31:38:08"], rx2, '#38BDF8', '--'),
        ("Link 0: RX1-TX1", tx_nodes["TX1 (Zone 1 NE)\nMAC: BC:DD:C2:CC:49:F4"], rx1, '#059669', '-'),
        ("Link 4: RX2-TX1", tx_nodes["TX1 (Zone 1 NE)\nMAC: BC:DD:C2:CC:49:F4"], rx2, '#34D399', '--'),
        ("Link 2: RX1-TX3", tx_nodes["TX3 (Zone 3 SW)\nMAC: 1C:69:20:31:4A:8C"], rx1, '#DC2626', '-'),
        ("Link 6: RX2-TX3", tx_nodes["TX3 (Zone 3 SW)\nMAC: 1C:69:20:31:4A:8C"], rx2, '#F87171', '--'),
        ("Link 3: RX1-TX4", tx_nodes["TX4 (Zone 4 SE)\nMAC: 1C:69:20:31:4C:E8"], rx1, '#D97706', '-'),
        ("Link 7: RX2-TX4", tx_nodes["TX4 (Zone 4 SE)\nMAC: 1C:69:20:31:4C:E8"], rx2, '#FBBF24', '--'),
    ]

    for lname, start, end, lcol, lstyle in links:
        ax.plot([start[0], end[0]], [start[1], end[1]], color=lcol, lw=1.8, ls=lstyle, zorder=3)

    for label, pos in tx_nodes.items():
        tb = patches.FancyBboxPatch((pos[0] - 1.1, pos[1] - 0.45), 2.2, 0.9, boxstyle="round,pad=0.05",
                                   edgecolor=COLOR_GREEN, facecolor='#F0FDF4', lw=1.5, zorder=4)
        ax.add_patch(tb)
        ax.scatter([pos[0]], [pos[1]], color=COLOR_GREEN, s=70, ec=COLOR_NAVY, zorder=6)
        ax.text(pos[0], pos[1] + 0.14, label.split('\n')[0], fontsize=8.0, fontweight='bold', color='#14532D', ha='center', zorder=7)
        ax.text(pos[0], pos[1] - 0.22, label.split('\n')[1], fontsize=6.8, color=COLOR_MUTED, ha='center', zorder=7)

    rxb = patches.FancyBboxPatch((4.1, 2.1), 1.8, 1.8, boxstyle="round,pad=0.06",
                                edgecolor=COLOR_NAVY, facecolor='#EFF6FF', lw=1.8, zorder=4)
    ax.add_patch(rxb)
    ax.scatter([rx1[0]], [rx1[1]], color=COLOR_BLUE, s=80, ec=COLOR_NAVY, zorder=6)
    ax.scatter([rx2[0]], [rx2[1]], color='#9333EA', s=80, ec=COLOR_NAVY, zorder=6)
    ax.plot([rx1[0], rx2[0]], [rx1[1], rx2[1]], color='#64748B', lw=1.5, ls=':')
    ax.text(5.0, 3.65, "CENTRAL DUAL RX", fontsize=8.5, fontweight='bold', color=COLOR_NAVY, ha='center', zorder=7)
    ax.text(rx1[0] - 0.1, rx1[1] - 0.28, "RX1 (COM8)", fontsize=7.2, fontweight='bold', color=COLOR_BLUE, ha='center', zorder=7)
    ax.text(rx2[0] + 0.1, rx2[1] + 0.28, "RX2 (COM9)", fontsize=7.2, fontweight='bold', color='#9333EA', ha='center', zorder=7)
    ax.text(5.0, 2.22, "Baseline d = 24.5 cm", fontsize=6.8, color=COLOR_MUTED, ha='center', zorder=7)

    ax.set_xlim(0.1, 9.9)
    ax.set_ylim(0.1, 5.9)
    ax.axis('off')
    save_fig(fig, "diagram_5_star_topology_mesh.png")


# =============================================================================
# 6. END-TO-END SOFTWARE INGESTION PIPELINE (Figure 4.1)
# =============================================================================
def generate_diagram_7_software_pipeline():
    fig, ax = plt.subplots(figsize=(10.5, 6.8), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    tiers = [
        ("LAYER 1: PHYSICAL ACQUISITION", [
            ("RX1 (COM8 @ 921,600 baud)", "COTS ESP32-WROOM-32 (~100 Hz)", COLOR_BLUE),
            ("RX2 (COM9 @ 921,600 baud)", "COTS ESP32-WROOM-32 (~100 Hz)", '#9333EA')
        ]),
        ("LAYER 2: MULTITHREADED SERIAL INGESTION", [
            ("Worker Thread 1 (Async Ring Buffer 1)", "Thread-safe 4096-frame circular queue", '#0284C7'),
            ("Worker Thread 2 (Async Ring Buffer 2)", "Thread-safe 4096-frame circular queue", '#7C3AED')
        ]),
        ("LAYER 3: FRAME PARSING & MAC DEMULTIPLEXING", [
            ("Header Validation & Frame Unpacking", "Discard framing noise; split 64 subcarriers", COLOR_SLATE),
            ("Packet-Level Transmitter MAC Demux", "Demux into 4 Transmitters (TX1, TX2, TX3, TX4)", COLOR_NAVY)
        ]),
        ("LAYER 4: SLIDING WINDOW & CANONICAL FEATURE ENGINE", [
            ("2.0-Second Sliding Window Accumulator", "100–105 Hz temporal window slicing", '#D97706'),
            ("56-D Canonical Feature Vector", "48 signal metrics + 8 link-active binary flags", COLOR_NAVY)
        ]),
        ("LAYER 5: GATED INFERENCE & REAL-TIME OUTPUT", [
            ("Supervised Random Forest Classifier", "Trained on zero-leakage Phase B takes", '#059669'),
            ("Youden J Energy Gate (θ = 1.80)", "Suppresses 98.35% empty-room false alarms", '#DC2626'),
            ("WebSocket Server (10 Hz Stream)", "Powers Live Observatory & Three.js 3D Twin", COLOR_NAVY)
        ])
    ]

    card_y = 5.9
    for tier_title, boxes in tiers:
        th = patches.FancyBboxPatch((0.5, card_y), 9.5, 0.42, boxstyle="round,pad=0.04",
                                    edgecolor=COLOR_NAVY, facecolor=COLOR_NAVY, lw=1.2, zorder=3)
        ax.add_patch(th)
        ax.text(0.7, card_y + 0.21, tier_title, fontsize=8.5, fontweight='bold', color='#FFFFFF', va='center', zorder=4)

        b_count = len(boxes)
        bw = (9.5 - (b_count - 1) * 0.3) / b_count
        by = card_y - 0.68
        for idx, (b_name, b_desc, b_col) in enumerate(boxes):
            bx = 0.5 + idx * (bw + 0.3)
            box = patches.FancyBboxPatch((bx, by), bw, 0.62, boxstyle="round,pad=0.04",
                                        edgecolor=b_col, facecolor='#F8FAFC', lw=1.4, zorder=2)
            ax.add_patch(box)
            ax.text(bx + bw/2, by + 0.40, b_name, fontsize=8.0, fontweight='bold', color=b_col, ha='center', zorder=4)
            ax.text(bx + bw/2, by + 0.16, b_desc, fontsize=6.8, color=COLOR_MUTED, ha='center', zorder=4)

        if tier_title != tiers[-1][0]:
            ax.annotate("", xy=(5.25, by - 0.28), xytext=(5.25, by - 0.04),
                        arrowprops=dict(arrowstyle="->", color=COLOR_NAVY, lw=1.8), zorder=5)

        card_y -= 1.34

    ax.set_xlim(0.2, 10.3)
    ax.set_ylim(-0.3, 6.6)
    ax.axis('off')
    save_fig(fig, "diagram_7_software_pipeline_architecture.png")


# =============================================================================
# 7. CANONICAL 56-DIMENSIONAL FEATURE EXTRACTION PIPELINE (Figure 5.1)
# =============================================================================
def generate_diagram_8_feature_pipeline():
    fig, ax = plt.subplots(figsize=(10.5, 5.2), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    steps = [
        ("STAGE 1: RAW BUFFER", "64-Subcarrier CSI records across 2.0s sliding window\n~200 packets per receiver at 100 Hz", '#64748B'),
        ("STAGE 2: PREPROCESSING", "Clean non-finite samples; prune guard & pilot subcarriers (0, 32)\nCompute per-packet mean subcarrier amplitudes", '#0284C7'),
        ("STAGE 3: LINK EXTRACTION", "Partition records into 8 link groups (RX1-TX1..4, RX2-TX1..4)\nExtract 6 temporal metrics per link (48 signal features total)", '#2563EB'),
        ("STAGE 4: VECTOR FUSION", "Fuse 48 signal statistics + 8 link-active binary presence flags\nYields authoritative 56-Dimensional Canonical Feature Space", COLOR_NAVY)
    ]

    for s_idx, (stitle, sdesc, scol) in enumerate(steps):
        sy = 4.2 - s_idx * 1.15
        sbox = patches.FancyBboxPatch((0.6, sy), 9.3, 0.85, boxstyle="round,pad=0.06",
                                     edgecolor=scol, facecolor='#F8FAFC' if s_idx < 3 else '#EFF6FF', 
                                     lw=2.0 if s_idx == 3 else 1.4, zorder=2)
        ax.add_patch(sbox)

        badge = patches.FancyBboxPatch((0.8, sy + 0.12), 2.2, 0.60, boxstyle="round,pad=0.04",
                                      edgecolor=scol, facecolor=scol, lw=1.0, zorder=3)
        ax.add_patch(badge)
        ax.text(1.9, sy + 0.42, stitle, fontsize=8.5, fontweight='bold', color='#FFFFFF', ha='center', va='center', zorder=4)
        ax.text(3.3, sy + 0.42, sdesc, fontsize=8.0, color=COLOR_SLATE, va='center', zorder=4)

        if s_idx < 3:
            ax.annotate("", xy=(5.25, sy - 0.28), xytext=(5.25, sy - 0.03),
                        arrowprops=dict(arrowstyle="->", color=scol, lw=1.8), zorder=5)

    bot_box = patches.FancyBboxPatch((0.6, -0.1), 9.3, 0.85, boxstyle="round,pad=0.06",
                                    edgecolor=COLOR_BORDER, facecolor='#F1F5F9', lw=1.2, zorder=2)
    ax.add_patch(bot_box)
    ax.text(5.25, 0.52, "6 Extracted Temporal Metrics per Spatial Link:", fontsize=8.5, fontweight='bold', color=COLOR_NAVY, ha='center')
    metrics_str = "1. Mean Amplitude (μ)  |  2. Std Dev (σ)  |  3. Mean Delta (Δ)  |  4. RMS Delta  |  5. 95th Percentile Delta  |  6. Total Energy (E)"
    ax.text(5.25, 0.20, metrics_str, fontsize=7.8, color=COLOR_SLATE, ha='center')

    ax.set_xlim(0.2, 10.2)
    ax.set_ylim(-0.2, 4.8)
    ax.axis('off')
    save_fig(fig, "diagram_8_canonical_feature_pipeline.png")


# =============================================================================
# 8. REPLAY LAB FINITE STATE MACHINE (Figure 7.4)
# =============================================================================
def generate_diagram_10_fsm():
    fig, ax = plt.subplots(figsize=(10.5, 4.8), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    states = {
        "STANDBY": ("SAFE STANDBY\n(Default Quiescent)", (5.25, 3.4), '#64748B'),
        "LIVE": ("LIVE HARDWARE\n(Active COM8/COM9 Streaming)", (1.8, 1.3), '#16A34A'),
        "REPLAY": ("REPLAY LAB\n(Deterministic CSV Playback)", (5.25, 1.3), '#2563EB'),
        "SIM": ("SIMULATION\n(Synthetic Wave Generator)", (8.7, 1.3), '#D97706')
    }

    for s_key, (s_name, (sx, sy), scol) in states.items():
        sb = patches.FancyBboxPatch((sx - 1.25, sy - 0.45), 2.5, 0.9, boxstyle="round,pad=0.08",
                                   edgecolor=scol, facecolor='#F8FAFC', lw=2.0, zorder=3)
        ax.add_patch(sb)
        ax.text(sx, sy, s_name, fontsize=8.5, fontweight='bold', color=scol, ha='center', va='center', zorder=4)

    # Transition arrows with clean label placement
    ax.annotate("", xy=(2.2, 1.8), xytext=(4.3, 3.2),
                arrowprops=dict(arrowstyle="->", color=COLOR_SLATE, lw=1.8), zorder=5)
    ax.text(3.0, 2.7, "Connect Serial / Start Stream", fontsize=7.5, color=COLOR_SLATE, rotation=35, ha='center')

    ax.annotate("", xy=(5.25, 1.8), xytext=(5.25, 2.9),
                arrowprops=dict(arrowstyle="->", color=COLOR_SLATE, lw=1.8), zorder=5)
    ax.text(5.35, 2.35, "Load Session CSV", fontsize=7.5, color=COLOR_SLATE, ha='left')

    ax.annotate("", xy=(8.3, 1.8), xytext=(6.2, 3.2),
                arrowprops=dict(arrowstyle="->", color=COLOR_SLATE, lw=1.8), zorder=5)
    ax.text(7.5, 2.7, "Enable Synthetic Mode", fontsize=7.5, color=COLOR_SLATE, rotation=-35, ha='center')

    # Safety Guard Callout
    guard_box = patches.FancyBboxPatch((1.2, 0.05), 8.1, 0.65, boxstyle="round,pad=0.05",
                                      edgecolor='#FCA5A5', facecolor='#FEF2F2', lw=1.2, zorder=3)
    ax.add_patch(guard_box)
    ax.text(5.25, 0.38, "Hardware Isolation Guard: Active serial threads are strictly terminated before replay initialization,\npreventing Windows COM port collisions and driver lockups.",
            fontsize=7.8, color='#991B1B', fontweight='bold', ha='center', va='center')

    ax.set_xlim(0.2, 10.3)
    ax.set_ylim(-0.1, 4.2)
    ax.axis('off')
    save_fig(fig, "diagram_10_fsm_state_machine.png")


# =============================================================================
# 9. FOUR-TIER TESTING HIERARCHY (Figure 8.1)
# =============================================================================
def generate_diagram_11_testing_hierarchy():
    fig, ax = plt.subplots(figsize=(10.5, 4.8), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    tiers = [
        ("TIER 4: CRYPTOGRAPHIC PROVENANCE", "Master Evaluation & SHA-256 Provenance Runner (run_master_evaluation.py)\nValidates spatial_model.pkl SHA-256 (786ed5b8...) against published evaluation hashes", '#1B365D'),
        ("TIER 3: CONTINUOUS INTEGRATION", "GitHub Actions Cloud Runner (.github/workflows/ci.yml)\nAutomated linting, import tests, and unit test pass on every git push", '#0284C7'),
        ("TIER 2: INDEPENDENT AUDIT SUITE", "Colleague 6-Point Verification Suite (verify_six_checks.py)\nZero train/test leakage verification, strictly audited session boundaries", '#2563EB'),
        ("TIER 1: AUTOMATED UNIT TESTS", "56 Automated Unit Tests (tests/test_spatial.py)\nCovers ring buffers, MAC demux, sliding windows, and canonical feature extraction", '#16A34A')
    ]

    for idx, (ttitle, tdesc, tcol) in enumerate(tiers):
        ty = 3.6 - idx * 1.05
        tw = 9.2 - idx * 0.4
        tx = 0.65 + idx * 0.2

        tbox = patches.FancyBboxPatch((tx, ty), tw, 0.85, boxstyle="round,pad=0.06",
                                     edgecolor=tcol, facecolor='#F8FAFC', lw=1.6, zorder=2)
        ax.add_patch(tbox)

        badge = patches.FancyBboxPatch((tx + 0.15, ty + 0.45), tw - 0.3, 0.32, boxstyle="round,pad=0.03",
                                      edgecolor=tcol, facecolor=tcol, lw=1.0, zorder=3)
        ax.add_patch(badge)
        ax.text(tx + tw/2, ty + 0.61, ttitle, fontsize=8.5, fontweight='bold', color='#FFFFFF', ha='center', va='center', zorder=4)
        ax.text(tx + tw/2, ty + 0.24, tdesc, fontsize=7.5, color=COLOR_SLATE, ha='center', va='center', zorder=4)

        if idx < 3:
            ax.annotate("", xy=(5.25, ty - 0.22), xytext=(5.25, ty - 0.02),
                        arrowprops=dict(arrowstyle="->", color=tcol, lw=1.6), zorder=5)

    ax.set_xlim(0.2, 10.2)
    ax.set_ylim(-0.2, 4.4)
    ax.axis('off')
    save_fig(fig, "diagram_11_four_tier_verification.png")


# =============================================================================
# 10. EXPERIMENTAL PROTOTYPE VS OPERATIONAL APPLICATION BOUNDARY (Figure 9.1)
# =============================================================================
def generate_diagram_12_scope_boundary():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.4), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    for ax in (ax1, ax2):
        ax.set_facecolor('#FFFFFF')
        ax.axis('off')

    b1 = patches.FancyBboxPatch((0.05, 0.05), 0.9, 0.9, boxstyle="round,pad=0.04",
                               edgecolor=COLOR_NAVY, facecolor='#EFF6FF', lw=2.0)
    ax1.add_patch(b1)
    
    h1 = patches.FancyBboxPatch((0.08, 0.78), 0.84, 0.14, boxstyle="round,pad=0.03",
                                edgecolor=COLOR_NAVY, facecolor=COLOR_NAVY)
    ax1.add_patch(h1)
    ax1.text(0.5, 0.85, "WIMOTION 2.0 PROTOTYPE (Current Work)", fontsize=9.5, fontweight='bold', color='#FFFFFF', ha='center', va='center')

    p1_items = [
        "Single-room controlled deployment (ROOM_LAB_A: 4.2m x 5.8m)",
        "Single human occupant locomotion; walking along corridors",
        "Coarse 4-quadrant spatial sectoring (Z1, Z2, Z3, Z4, CLEAR)",
        "49.26% gated 5-class feasibility accuracy (vs. 20% random)",
        "Low-cost COTS ESP32 nodes (<$4/node; ~$25-$30 total array)",
        "Strictly evaluated with zero test leakage on held-out Take 02"
    ]
    for idx, itm in enumerate(p1_items):
        ax1.text(0.12, 0.68 - idx * 0.10, "✔  " + itm, fontsize=7.8, color=COLOR_SLATE)

    b2 = patches.FancyBboxPatch((0.05, 0.05), 0.9, 0.9, boxstyle="round,pad=0.04",
                               edgecolor='#0284C7', facecolor='#F0F9FF', lw=2.0)
    ax2.add_patch(b2)
    
    h2 = patches.FancyBboxPatch((0.08, 0.78), 0.84, 0.14, boxstyle="round,pad=0.03",
                                edgecolor='#0284C7', facecolor='#0284C7')
    ax2.add_patch(h2)
    ax2.text(0.5, 0.85, "FUTURE OPERATIONAL DOMAINS (Proposed)", fontsize=9.5, fontweight='bold', color='#FFFFFF', ha='center', va='center')

    p2_items = [
        "Camera-independent smart building occupancy sensing",
        "Covert perimeter intrusion monitoring & invisible tripwires",
        "Search-and-rescue void sensing in smoke/degraded visuals",
        "Non-invasive elderly fall detection & medical room monitoring",
        "Tactical indoor reconnaissance prior to building entry",
        "Multi-person separation via Doppler Angle-of-Arrival (AoA)"
    ]
    for idx, itm in enumerate(p2_items):
        ax2.text(0.12, 0.68 - idx * 0.10, "➔  " + itm, fontsize=7.8, color=COLOR_NAVY)

    save_fig(fig, "diagram_12_prototype_vs_operational_scope.png")


# =============================================================================
# 11. DECOUPLED CLIENT-SERVER VISUALIZATION (Figure 7.3)
# =============================================================================
def generate_diagram_9_client_server():
    fig, ax = plt.subplots(figsize=(10.5, 4.4), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    card_w, card_h = 4.3, 3.6
    bx, by = 0.5, 0.4
    b_box = patches.FancyBboxPatch((bx, by), card_w, card_h, boxstyle="round,pad=0.08",
                                  edgecolor=COLOR_NAVY, facecolor='#EFF6FF', lw=1.8, zorder=2)
    ax.add_patch(b_box)

    bh_box = patches.FancyBboxPatch((bx + 0.1, by + card_h - 0.7), card_w - 0.2, 0.6,
                                   boxstyle="round,pad=0.05", edgecolor=COLOR_NAVY, facecolor=COLOR_NAVY, zorder=3)
    ax.add_patch(bh_box)
    ax.text(bx + card_w/2, by + card_h - 0.4, "FASTAPI APPLICATION BACKEND", 
            fontsize=9.5, fontweight='bold', color='#FFFFFF', ha='center', zorder=4)

    b_items = [
        "spatial/server.py Application Runtime",
        "Dual-COM Serial Ingestion Workers (COM8 / COM9)",
        "Sliding Window Ring Buffers (2.0s duration)",
        "Canonical 56-D Feature Extraction Engine",
        "Gated Random Forest Inference Model",
        "Replay Lab & Simulation State Machine"
    ]
    for idx, bi in enumerate(b_items):
        ax.text(bx + 0.3, by + card_h - 1.15 - idx * 0.40, "•  " + bi, fontsize=8.0, color=COLOR_SLATE, zorder=4)

    ws_box = patches.FancyBboxPatch((4.9, 1.8), 0.7, 0.8, boxstyle="round,pad=0.06",
                                   edgecolor='#0284C7', facecolor='#0284C7', zorder=5)
    ax.add_patch(ws_box)
    ax.text(5.25, 2.3, "WebSocket", fontsize=7.8, fontweight='bold', color='#FFFFFF', ha='center', zorder=6)
    ax.text(5.25, 2.0, "10 Hz", fontsize=7.2, color='#E0F2FE', ha='center', zorder=6)

    ax.annotate("", xy=(5.6, 2.2), xytext=(4.9, 2.2),
                arrowprops=dict(arrowstyle="<->", color=COLOR_NAVY, lw=2.0), zorder=6)

    fx, fy = 5.7, 0.4
    f_box = patches.FancyBboxPatch((fx, fy), card_w, card_h, boxstyle="round,pad=0.08",
                                  edgecolor=COLOR_BLUE, facecolor='#F8FAFC', lw=1.8, zorder=2)
    ax.add_patch(f_box)

    fh_box = patches.FancyBboxPatch((fx + 0.1, fy + card_h - 0.7), card_w - 0.2, 0.6,
                                   boxstyle="round,pad=0.05", edgecolor=COLOR_BLUE, facecolor=COLOR_BLUE, zorder=3)
    ax.add_patch(fh_box)
    ax.text(fx + card_w/2, fy + card_h - 0.4, "BROWSER OBSERVATORY RUNTIME", 
            fontsize=9.5, fontweight='bold', color='#FFFFFF', ha='center', zorder=4)

    f_items = [
        "dashboard/observatory_multi.html",
        "Vanilla CSS Dark Glassmorphism Design",
        "HTML5 Canvas 2D Polar Radar Sweep Engine",
        "Three.js WebGL 3D Room Digital Twin",
        "Dual-Engine HUD (Heuristic & Supervised ML)",
        "Recorded-Session Replay Lab Timeline Controls"
    ]
    for idx, fi in enumerate(f_items):
        ax.text(fx + 0.3, fy + card_h - 1.15 - idx * 0.40, "•  " + fi, fontsize=8.0, color=COLOR_SLATE, zorder=4)

    ax.set_xlim(0.2, 10.3)
    ax.set_ylim(0.2, 4.3)
    ax.axis('off')
    save_fig(fig, "diagram_9_client_server_visualization.png")


# =============================================================================
# 12. STRUCTURED ENGINEERING ROADMAP TABLE (Figure 10.1)
# =============================================================================
def generate_diagram_13_roadmap():
    fig, ax = plt.subplots(figsize=(10.8, 4.8), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    mb = patches.FancyBboxPatch((0.4, 0.3), 10.0, 4.2, boxstyle="round,pad=0.08",
                               edgecolor=COLOR_NAVY, facecolor='#FFFFFF', lw=1.8, zorder=2)
    ax.add_patch(mb)

    tb = patches.FancyBboxPatch((0.4, 3.9), 10.0, 0.6, boxstyle="round,pad=0.05",
                                edgecolor=COLOR_NAVY, facecolor=COLOR_NAVY, zorder=3)
    ax.add_patch(tb)
    ax.text(5.4, 4.2, "WIMOTION STRUCTURED ENGINEERING UPGRADE ROADMAP", fontsize=10.5, fontweight='bold', color='#FFFFFF', ha='center', va='center')

    cols = [(0.6, 2.8, "CURRENT BOTTLENECK"), (3.6, 3.2, "PROPOSED UPGRADE"), (7.0, 3.2, "TARGET BENCHMARK")]
    hb = patches.FancyBboxPatch((0.5, 3.35), 9.8, 0.45, boxstyle="round,pad=0.03",
                               edgecolor='#CBD5E1', facecolor='#F1F5F9', zorder=3)
    ax.add_patch(hb)
    for cx, cw, cname in cols:
        ax.text(cx + cw/2, 3.58, cname, fontsize=8.5, fontweight='bold', color=COLOR_NAVY, ha='center', va='center')

    rows = [
        ("Amplitude-Only Data\n(Carrier frequency offset / phase noise)", 
         "Wi-Fi 6 (ESP32-C6) Silicon &\nConjugate Multiplication", 
         "Sanitized Phase & Angle-of-Arrival (AoA)\nAngular tracking resolution < 10°"),
        ("Single-Room Bias\n(Static multipath structure shift)", 
         "Domain-Adversarial Neural\nNetworks (DANN)", 
         "Cross-Room Transfer Accuracy > 65%\nwithout full retake training"),
        ("Memoryless Windows\n(Per-window classification flickers)", 
         "Temporal Convolutional Networks\n(TCN / Bidirectional LSTM)", 
         "Gait Trajectory Smoothing &\nTransient Spike Flicker Elimination"),
        ("Single Occupant Limitation\n(Signal interference superposition)", 
         "Subcarrier Doppler BSS &\nMulti-Target Trajectory Clustering", 
         "Concurrent 2-Person Separation\nwithout false quadrant ghosting")
    ]

    for r_idx, (c1, c2, c3) in enumerate(rows):
        ry = 2.65 - r_idx * 0.75
        bg_col = '#F8FAFC' if r_idx % 2 == 1 else '#FFFFFF'
        rb = patches.Rectangle((0.5, ry), 9.8, 0.68, facecolor=bg_col, edgecolor='#E2E8F0', lw=0.8, zorder=3)
        ax.add_patch(rb)

        ax.text(0.7, ry + 0.34, c1, fontsize=7.5, color='#991B1B', va='center')
        ax.text(3.7, ry + 0.34, c2, fontsize=7.5, color=COLOR_NAVY, fontweight='bold', va='center')
        ax.text(7.1, ry + 0.34, c3, fontsize=7.5, color='#15803D', va='center')

    ax.set_xlim(0.1, 10.7)
    ax.set_ylim(0.1, 4.7)
    ax.axis('off')
    save_fig(fig, "diagram_13_engineering_roadmap.png")


# =============================================================================
# 13. PROPAGATION MECHANISMS (Figure 2.1 / Section 2.2)
# =============================================================================

def generate_diagram_propagation_mechanisms():
    fig, ax = plt.subplots(figsize=(10.5, 4.4), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    # Top Incident Wave box
    inc_w, inc_h = 3.6, 0.75
    inc_x, inc_y = 5.25 - inc_w/2, 3.4
    inc_box = patches.FancyBboxPatch((inc_x, inc_y), inc_w, inc_h, boxstyle="round,pad=0.08",
                                     edgecolor=COLOR_NAVY, facecolor=COLOR_NAVY, lw=1.8, zorder=3)
    ax.add_patch(inc_box)
    ax.text(5.25, inc_y + inc_h/2, "INCIDENT ELECTROMAGNETIC WAVE\n(2.4 GHz RF Wavefront from Transmitter)", 
            fontsize=9.5, fontweight='bold', color='#FFFFFF', ha='center', va='center', zorder=4)

    # 4 Mechanism Cards
    cards = [
        {
            "title": "SPECULAR REFLECTION",
            "sub": "Angle of reflection = Angle of incidence",
            "items": ["Planar boundaries (smooth walls)", "Floors and ceiling slabs", "Metal cabinets and glass panes", r"Snell's Law: $\theta_r = \theta_i$"],
            "color": COLOR_NAVY
        },
        {
            "title": "EDGE DIFFRACTION",
            "sub": "Wavefront bending into shadow zones",
            "items": ["Doorway frame corners", "Desk partitions & structural pillars", "Huygens-Fresnel secondary waves", "Non-Line-of-Sight (NLOS) paths"],
            "color": COLOR_BLUE
        },
        {
            "title": "DIELECTRIC ABSORPTION",
            "sub": "Forward energy attenuation to heat",
            "items": ["Human tissue & body torso", r"Water / electrolyte mix ($\epsilon_r \approx 54$)", "Direct-path signal shadowing", "Significant amplitude reduction"],
            "color": COLOR_AMBER
        },
        {
            "title": "DIFFUSE SCATTERING",
            "sub": "Rough surface omnidirectional scatter",
            "items": ["Textured walls & irregular edges", r"Feature dimensions $\sim \lambda$ (12.3 cm)", "Hemispherical energy dispersion", "Randomized multipath phases"],
            "color": COLOR_SLATE
        }
    ]

    card_w, card_h = 2.25, 2.5
    spacing = 2.45
    start_x = 0.55

    for idx, c in enumerate(cards):
        cx = start_x + idx * spacing
        cy = 0.35

        card = patches.FancyBboxPatch((cx, cy), card_w, card_h, boxstyle="round,pad=0.06",
                                     edgecolor=c["color"], facecolor=COLOR_BG_LIGHT, lw=1.5, zorder=2)
        ax.add_patch(card)

        # Header box
        h_box = patches.FancyBboxPatch((cx + 0.06, cy + card_h - 0.58), card_w - 0.12, 0.52,
                                       boxstyle="round,pad=0.04", edgecolor=c["color"], facecolor=c["color"], zorder=3)
        ax.add_patch(h_box)
        ax.text(cx + card_w/2, cy + card_h - 0.32, c["title"], fontsize=8.5, fontweight='bold', color='#FFFFFF', ha='center', zorder=4)

        ax.text(cx + card_w/2, cy + card_h - 0.82, c["sub"], fontsize=7.2, fontstyle='italic', color=COLOR_SLATE, ha='center', zorder=4)

        for b_idx, item in enumerate(c["items"]):
            by = cy + card_h - 1.15 - b_idx * 0.32
            ax.text(cx + 0.14, by, "•", fontsize=8.5, color=c["color"], fontweight='bold', zorder=4)
            ax.text(cx + 0.26, by, item, fontsize=7.2, color=COLOR_BODY, zorder=4)

        # Connector arrow from incident wave
        ax.annotate("", xy=(cx + card_w/2, cy + card_h), xytext=(5.25, inc_y),
                    arrowprops=dict(arrowstyle="->", color=c["color"], lw=1.5, connectionstyle=f"angle,angleA=0,angleB=90,rad=5"), zorder=1)

    ax.set_xlim(0.1, 10.4)
    ax.set_ylim(0.1, 4.3)
    ax.axis('off')
    save_fig(fig, "diagram_propagation_mechanisms.png")


# =============================================================================
# 14. ESP32 SOC HARDWARE ARCHITECTURE (Figure 3.1b / Section 3.2)
# =============================================================================
def generate_diagram_esp32_hardware_arch():
    fig, ax = plt.subplots(figsize=(10.0, 5.2), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    # Outer ESP32 SoC Container
    soc_w, soc_h = 8.6, 3.4
    soc_x, soc_y = 0.7, 1.4
    soc_box = patches.FancyBboxPatch((soc_x, soc_y), soc_w, soc_h, boxstyle="round,pad=0.10",
                                     edgecolor=COLOR_NAVY, facecolor='#F8FAFC', lw=2.2, zorder=2)
    ax.add_patch(soc_box)

    # SoC Header Banner
    h_box = patches.FancyBboxPatch((soc_x + 0.15, soc_y + soc_h - 0.55), soc_w - 0.3, 0.45,
                                   boxstyle="round,pad=0.05", edgecolor=COLOR_NAVY, facecolor=COLOR_NAVY, zorder=3)
    ax.add_patch(h_box)
    ax.text(soc_x + soc_w/2, soc_y + soc_h - 0.32, "ESP32-WROOM-32 SYSTEM-ON-CHIP (SoC) ARCHITECTURE", 
            fontsize=10.0, fontweight='bold', color='#FFFFFF', ha='center', va='center', zorder=4)

    # Core 0 and Core 1 boxes
    core_w, core_h = 3.6, 0.75
    # Core 0
    c0_box = patches.FancyBboxPatch((soc_x + 0.45, soc_y + soc_h - 1.55), core_w, core_h, boxstyle="round,pad=0.06",
                                    edgecolor=COLOR_BLUE, facecolor='#EFF6FF', lw=1.5, zorder=3)
    ax.add_patch(c0_box)
    ax.text(soc_x + 0.45 + core_w/2, soc_y + soc_h - 1.05, "Xtensa LX6 Core 0 (PRO_CPU)", fontsize=9.0, fontweight='bold', color=COLOR_NAVY, ha='center', zorder=4)
    ax.text(soc_x + 0.45 + core_w/2, soc_y + soc_h - 1.35, "Dedicated Wi-Fi MAC / PHY ISR & CSI Hook", fontsize=7.5, color=COLOR_SLATE, ha='center', zorder=4)

    # Core 1
    c1_box = patches.FancyBboxPatch((soc_x + soc_w - 0.45 - core_w, soc_y + soc_h - 1.55), core_w, core_h, boxstyle="round,pad=0.06",
                                    edgecolor=COLOR_BLUE, facecolor='#EFF6FF', lw=1.5, zorder=3)
    ax.add_patch(c1_box)
    ax.text(soc_x + soc_w - 0.45 - core_w/2, soc_y + soc_h - 1.05, "Xtensa LX6 Core 1 (APP_CPU)", fontsize=9.0, fontweight='bold', color=COLOR_NAVY, ha='center', zorder=4)
    ax.text(soc_x + soc_w - 0.45 - core_w/2, soc_y + soc_h - 1.35, "FreeRTOS Scheduling & Packet Serialization", fontsize=7.5, color=COLOR_SLATE, ha='center', zorder=4)

    # Shared Internal SRAM
    sram_w, sram_h = 7.7, 0.60
    sram_box = patches.FancyBboxPatch((soc_x + 0.45, soc_y + soc_h - 2.35), sram_w, sram_h, boxstyle="round,pad=0.06",
                                      edgecolor=COLOR_SLATE, facecolor='#FFFFFF', lw=1.4, zorder=3)
    ax.add_patch(sram_box)
    ax.text(soc_x + soc_w/2, soc_y + soc_h - 2.05, "520 KB On-Chip SRAM (DMA Ping-Pong Buffers & Circular Queues)", 
            fontsize=8.5, fontweight='bold', color=COLOR_NAVY, ha='center', va='center', zorder=4)

    # 802.11n PHY Baseband
    phy_w, phy_h = 7.7, 0.65
    phy_box = patches.FancyBboxPatch((soc_x + 0.45, soc_y + 0.25), phy_w, phy_h, boxstyle="round,pad=0.06",
                                     edgecolor=COLOR_NAVY, facecolor='#E0F2FE', lw=1.6, zorder=3)
    ax.add_patch(phy_box)
    ax.text(soc_x + soc_w/2, soc_y + 0.68, "802.11n 2.4 GHz PHY Baseband & Hardware OFDM Demodulator", 
            fontsize=9.0, fontweight='bold', color=COLOR_NAVY, ha='center', zorder=4)
    ax.text(soc_x + soc_w/2, soc_y + 0.42, "Direct CSI Hardware Extraction: 64 Subcarriers (52 Data, 4 Pilots, 8 Nulls)", 
            fontsize=7.8, color=COLOR_BLUE, ha='center', zorder=4)

    # CP2102 Bridge Controller
    br_w, br_h = 4.8, 0.70
    br_x, br_y = soc_x + soc_w/2 - br_w/2, 0.28
    br_box = patches.FancyBboxPatch((br_x, br_y), br_w, br_h, boxstyle="round,pad=0.06",
                                    edgecolor=COLOR_NAVY, facecolor='#EFF6FF', lw=1.6, zorder=3)
    ax.add_patch(br_box)
    ax.text(soc_x + soc_w/2, br_y + 0.45, "Silicon Labs CP2102 USB-to-UART Bridge Controller", 
            fontsize=8.5, fontweight='bold', color=COLOR_NAVY, ha='center', zorder=4)
    ax.text(soc_x + soc_w/2, br_y + 0.20, "High-Speed Full-Duplex Serial Link @ 921,600 Baud", 
            fontsize=7.5, color=COLOR_SLATE, ha='center', zorder=4)

    # Connector Arrows
    ax.annotate("", xy=(soc_x + soc_w/2, br_y + br_h), xytext=(soc_x + soc_w/2, soc_y),
                arrowprops=dict(arrowstyle="<->", color=COLOR_NAVY, lw=2.0), zorder=4)
    ax.text(soc_x + soc_w/2 + 0.15, (br_y + br_h + soc_y)/2, "UART DMA", fontsize=7.0, color=COLOR_SLATE, va='center')

    # Antenna icon top
    ant_x = soc_x + 1.2
    ax.plot([ant_x, ant_x], [soc_y + soc_h, soc_y + soc_h + 0.25], color=COLOR_NAVY, lw=2.0)
    ax.plot([ant_x - 0.25, ant_x + 0.25], [soc_y + soc_h + 0.25, soc_y + soc_h + 0.25], color=COLOR_NAVY, lw=2.0)
    ax.plot([ant_x, ant_x - 0.25], [soc_y + soc_h + 0.25, soc_y + soc_h + 0.40], color=COLOR_NAVY, lw=1.5)
    ax.plot([ant_x, ant_x + 0.25], [soc_y + soc_h + 0.25, soc_y + soc_h + 0.40], color=COLOR_NAVY, lw=1.5)
    ax.text(ant_x + 0.4, soc_y + soc_h + 0.28, "Inverted-F PCB Antenna (+2 dBi)", fontsize=7.8, color=COLOR_SLATE)

    ax.set_xlim(0.2, 9.8)
    ax.set_ylim(0.05, 5.15)
    ax.axis('off')
    save_fig(fig, "diagram_esp32_hardware_arch.png")


# =============================================================================
# 15. ROOM COORDINATES & QUADRANT BOUNDARY MAP (Figure 3.3b / Section 3.5)
# =============================================================================
def generate_diagram_room_coordinates_layout():
    fig, ax = plt.subplots(figsize=(9.8, 6.2), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    # Room Dimensions: W = 5.8 m, H = 4.2 m
    rx, ry, rw, rh = 1.0, 0.8, 7.8, 4.6

    # Room Wall Boundary
    room_wall = patches.Rectangle((rx, ry), rw, rh, facecolor='#FAFAFA', edgecolor=COLOR_NAVY, lw=2.4, zorder=2)
    ax.add_patch(room_wall)

    # Quadrant Dividers (dashed lines)
    mid_x = rx + rw / 2.0
    mid_y = ry + rh / 2.0
    ax.plot([mid_x, mid_x], [ry, ry + rh], color='#CBD5E1', linestyle='--', lw=1.6, zorder=3)
    ax.plot([rx, rx + rw], [mid_y, mid_y], color='#CBD5E1', linestyle='--', lw=1.6, zorder=3)

    # Quadrant Shading & Titles
    quads = [
        {"name": "ZONE 2 (North-West)", "sub": "Primary Workstation Desk", "bx": rx, "by": mid_y, "col": "#EFF6FF"},
        {"name": "ZONE 1 (North-East)", "sub": "Doorway Access Corridor", "bx": mid_x, "by": mid_y, "col": "#FEF3C7"},
        {"name": "ZONE 3 (South-West)", "sub": "Storage Flank & Shelving", "bx": rx, "by": ry, "col": "#F1F5F9"},
        {"name": "ZONE 4 (South-East)", "sub": "Window Perimeter Walkway", "bx": mid_x, "by": ry, "col": "#DCFCE7"}
    ]
    for q in quads:
        qp = patches.Rectangle((q["bx"], q["by"]), rw/2, rh/2, facecolor=q["col"], alpha=0.35, zorder=2)
        ax.add_patch(qp)
        ax.text(q["bx"] + rw/4, q["by"] + rh/4 + 0.22, q["name"], fontsize=9.5, fontweight='bold', color=COLOR_NAVY, ha='center', zorder=4)
        ax.text(q["bx"] + rw/4, q["by"] + rh/4 - 0.08, q["sub"], fontsize=7.8, fontstyle='italic', color=COLOR_SLATE, ha='center', zorder=4)

    # Wall Annotations
    ax.text(mid_x, ry + rh + 0.18, "NORTHERN WALL (5.8 m)", fontsize=8.5, fontweight='bold', color=COLOR_SLATE, ha='center')
    ax.text(mid_x, ry - 0.26, "SOUTHERN WALL (5.8 m)", fontsize=8.5, fontweight='bold', color=COLOR_SLATE, ha='center')
    ax.text(rx - 0.22, mid_y, "WESTERN\nWALL\n(4.2 m)", fontsize=8.0, fontweight='bold', color=COLOR_SLATE, ha='center', va='center')
    ax.text(rx + rw + 0.22, mid_y, "EASTERN\nWALL\n(4.2 m)", fontsize=8.0, fontweight='bold', color=COLOR_SLATE, ha='center', va='center')

    # Corner Transmitters
    tx_nodes = [
        {"id": "TX2 (NW)", "coord": "(0.0, 4.2)", "mac": "1C:69:20:31:38:08", "x": rx, "y": ry + rh, "align": "left", "ox": 0.15, "oy": -0.45},
        {"id": "TX1 (NE)", "coord": "(5.8, 4.2)", "mac": "BC:DD:C2:CC:49:F4", "x": rx + rw, "y": ry + rh, "align": "right", "ox": -0.15, "oy": -0.45},
        {"id": "TX3 (SW)", "coord": "(0.0, 0.0)", "mac": "1C:69:20:31:3B:AC", "x": rx, "y": ry, "align": "left", "ox": 0.15, "oy": 0.45},
        {"id": "TX4 (SE)", "coord": "(5.8, 0.0)", "mac": "1C:69:20:31:38:34", "x": rx + rw, "y": ry, "align": "right", "ox": -0.15, "oy": 0.45}
    ]
    for t in tx_nodes:
        ax.scatter([t["x"]], [t["y"]], color=COLOR_GREEN, s=110, edgecolors=COLOR_NAVY, lw=2.0, zorder=6)
        card_w = 2.4
        card_x = t["x"] + (0.1 if t["align"] == "left" else -card_w - 0.1)
        card_y = t["y"] + (-0.85 if "North" in t["coord"] or "4.2" in t["coord"] else 0.15)
        cb = patches.FancyBboxPatch((card_x, card_y), card_w, 0.70, boxstyle="round,pad=0.04",
                                    edgecolor=COLOR_NAVY, facecolor='#FFFFFF', lw=1.2, zorder=5)
        ax.add_patch(cb)
        ax.text(card_x + card_w/2, card_y + 0.46, f"{t['id']} — {t['coord']}", fontsize=8.0, fontweight='bold', color=COLOR_NAVY, ha='center', zorder=6)
        ax.text(card_x + card_w/2, card_y + 0.20, f"MAC: {t['mac']}", fontsize=7.0, color=COLOR_SLATE, ha='center', zorder=6)

    # Central Workstation Hub (Dual Receivers)
    hub_w, hub_h = 2.6, 0.95
    hub_box = patches.FancyBboxPatch((mid_x - hub_w/2, mid_y - hub_h/2), hub_w, hub_h, boxstyle="round,pad=0.06",
                                     edgecolor=COLOR_NAVY, facecolor='#FFFFFF', lw=2.0, zorder=5)
    ax.add_patch(hub_box)
    ax.text(mid_x, mid_y + 0.28, "CENTRAL RECEIVER HUB (2.9, 2.1)", fontsize=8.0, fontweight='bold', color=COLOR_NAVY, ha='center', zorder=6)
    ax.text(mid_x, mid_y + 0.05, "RX1 (COM8)  ◄── 24.5 cm ──►  RX2 (COM9)", fontsize=7.5, color=COLOR_BLUE, ha='center', zorder=6)
    ax.text(mid_x, mid_y - 0.22, "Co-Located Host Laptop Station", fontsize=7.0, fontstyle='italic', color=COLOR_SLATE, ha='center', zorder=6)

    ax.set_xlim(0.2, 9.6)
    ax.set_ylim(0.2, 5.8)
    ax.axis('off')
    save_fig(fig, "diagram_room_coordinates_layout.png")


# =============================================================================
# 16. TELEMETRY HUD METRIC CARDS (Figure 7.2b / Section 7.3)
# =============================================================================
def generate_diagram_telemetry_hud_cards():
    fig, ax = plt.subplots(figsize=(10.5, 2.4), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    cards = [
        {
            "title": "VALID CSI RATE",
            "val": "102.4 Hz",
            "sub": "Aggregate Ingestion Rate",
            "detail": "Window: 2.0s sliding | 100% nominal",
            "val_col": COLOR_NAVY,
            "badge_bg": "#EFF6FF",
            "badge_txt": "ONLINE",
            "badge_col": "#15803D"
        },
        {
            "title": "ACTIVE LINKS MATRIX",
            "val": "8 / 8 ACTIVE",
            "sub": "Spatial Coverage Baselines",
            "detail": "Freshness: < 1.0s (Timeout: 3.0s)",
            "val_col": "#15803D",
            "badge_bg": "#DCFCE7",
            "badge_txt": "L0 – L7 OK",
            "badge_col": "#15803D"
        },
        {
            "title": "RECEIVER HEALTH",
            "val": "2 / 2 ONLINE",
            "sub": "Dual USB-Serial Synchronization",
            "detail": "RX1: COM8 (51.2 Hz) | RX2: COM9 (51.2 Hz)",
            "val_col": COLOR_NAVY,
            "badge_bg": "#EFF6FF",
            "badge_txt": "921,600 BAUD",
            "badge_col": COLOR_BLUE
        },
        {
            "title": "DUAL-ENGINE HUD",
            "val": "ZONE: Z1 (NE)",
            "sub": "Supervised ML Prediction: Z1",
            "detail": "Confidence: 68.4% | Gate: θ = 1.80",
            "val_col": "#B45309",
            "badge_bg": "#FEF3C7",
            "badge_txt": "AGREEMENT",
            "badge_col": "#B45309"
        }
    ]

    card_w, card_h = 2.25, 1.85
    start_x = 0.5
    spacing = 2.45

    for idx, c in enumerate(cards):
        cx = start_x + idx * spacing
        cy = 0.25

        card = patches.FancyBboxPatch((cx, cy), card_w, card_h, boxstyle="round,pad=0.06",
                                     edgecolor=COLOR_BORDER, facecolor='#FFFFFF', lw=1.4, zorder=2)
        ax.add_patch(card)

        # Header title
        ax.text(cx + 0.15, cy + card_h - 0.28, c["title"], fontsize=8.0, fontweight='bold', color=COLOR_NAVY, zorder=3)

        # Badge
        badge = patches.FancyBboxPatch((cx + card_w - 0.95, cy + card_h - 0.38), 0.82, 0.24, boxstyle="round,pad=0.03",
                                      edgecolor=c["badge_bg"], facecolor=c["badge_bg"], zorder=3)
        ax.add_patch(badge)
        ax.text(cx + card_w - 0.54, cy + card_h - 0.26, c["badge_txt"], fontsize=6.5, fontweight='bold', color=c["badge_col"], ha='center', zorder=4)

        # Main Big Value
        ax.text(cx + 0.15, cy + card_h - 0.72, c["val"], fontsize=12.0, fontweight='bold', color=c["val_col"], zorder=3)

        # Subtitle
        ax.text(cx + 0.15, cy + card_h - 1.05, c["sub"], fontsize=7.5, color=COLOR_SLATE, zorder=3)

        # Divider line
        ax.plot([cx + 0.15, cx + card_w - 0.15], [cy + card_h - 1.25, cy + card_h - 1.25], color='#E2E8F0', lw=0.8, zorder=3)

        # Detail text
        ax.text(cx + 0.15, cy + 0.30, c["detail"], fontsize=6.8, color=COLOR_MUTED, zorder=3)

    ax.set_xlim(0.1, 10.4)
    ax.set_ylim(0.1, 2.3)
    ax.axis('off')
    save_fig(fig, "diagram_telemetry_hud_cards.png")


def generate_all():
    print("[*] Generating all 16 publication-quality diagrams...")
    generate_diagram_1_evolution()
    generate_diagram_2_rssi_vs_csi()
    generate_diagram_3_fresnel()
    generate_diagram_4_single_vs_multilink()
    generate_diagram_5_star_topology()
    generate_diagram_7_software_pipeline()
    generate_diagram_8_feature_pipeline()
    generate_diagram_9_client_server()
    generate_diagram_10_fsm()
    generate_diagram_11_testing_hierarchy()
    generate_diagram_12_scope_boundary()
    generate_diagram_13_roadmap()
    generate_diagram_propagation_mechanisms()
    generate_diagram_esp32_hardware_arch()
    generate_diagram_room_coordinates_layout()
    generate_diagram_telemetry_hud_cards()
    print("[+] All 16 publication diagrams successfully generated!")


if __name__ == "__main__":
    generate_all()

