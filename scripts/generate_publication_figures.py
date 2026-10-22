import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

OUTPUT_DIR = Path(r"e:\WIFI_INTERFEROMETRIC_NEURAL_SENSING\wimotion_2.0\docs\figures\generated_diagrams")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['mathtext.fontset'] = 'dejavusans'

COLOR_NAVY = "#1B365D"
COLOR_SLATE = "#334155"
COLOR_BLUE = "#2563EB"
COLOR_LIGHT_BG = "#F8FAFC"
COLOR_GREEN = "#16A34A"
COLOR_RED = "#DC2626"

def create_fresnel_diagram():
    fig, ax = plt.subplots(figsize=(10.5, 4.8), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    
    # Coordinates for TX and RX
    tx_x, tx_y = 1.2, 2.0
    rx_x, rx_y = 7.8, 2.0
    mid_x = (tx_x + rx_x) / 2.0
    mid_y = 2.0
    
    a = (rx_x - tx_x) / 2.0 + 0.35  # semi-major axis = 3.65
    b = 1.30                        # semi-minor axis (r1 representation)
    
    # 1st Fresnel Zone Ellipse (translucent fill + dashed border)
    ellipse = patches.Ellipse((mid_x, mid_y), width=2*a, height=2*b, 
                              edgecolor=COLOR_NAVY, facecolor='#E0F2FE', 
                              alpha=0.65, linestyle='--', linewidth=2.2, zorder=2)
    ax.add_patch(ellipse)
    
    # 2nd Fresnel Zone outer dashed boundary
    ellipse_outer = patches.Ellipse((mid_x, mid_y), width=2*(a+0.45), height=2*(b+0.45), 
                                    edgecolor='#94A3B8', facecolor='none', 
                                    linestyle=':', linewidth=1.3, alpha=0.6, zorder=1)
    ax.add_patch(ellipse_outer)

    # Direct Line-of-Sight (LOS) Baseline (D)
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

    # Point P on the boundary (placed on left quadrant so rays don't collide with r1)
    px = mid_x - 1.8
    py = mid_y + b * np.sqrt(max(0, 1 - ((px - mid_x)/a)**2))
    ax.plot([tx_x, px], [tx_y, py], color=COLOR_BLUE, linewidth=1.8, linestyle='--', zorder=4)
    ax.plot([px, rx_x], [py, rx_y], color=COLOR_BLUE, linewidth=1.8, linestyle='--', zorder=4)
    ax.scatter([px], [py], color=COLOR_BLUE, s=55, zorder=6)
    
    # Ray labels
    ax.text((tx_x + px)/2 - 0.25, (tx_y + py)/2 + 0.15, r"$d_1$", fontsize=11, fontweight='bold', color=COLOR_BLUE)
    ax.text((px + rx_x)/2 - 0.3, (py + rx_y)/2 + 0.25, r"$d_2$", fontsize=11, fontweight='bold', color=COLOR_BLUE)
    ax.text(px, py + 0.16, r"Boundary Point $P(x, y)$", fontsize=9.5, fontweight='bold', color=COLOR_SLATE, ha='center')

    # TX Node box & label (centered at tx_x)
    tx_w, tx_h = 1.4, 0.85
    tx_box = patches.FancyBboxPatch((tx_x - tx_w, tx_y - tx_h/2), tx_w, tx_h, boxstyle="round,pad=0.06",
                                   edgecolor=COLOR_NAVY, facecolor='#F8FAFC', linewidth=1.8, zorder=5)
    ax.add_patch(tx_box)
    ax.scatter([tx_x], [tx_y], color=COLOR_GREEN, s=70, edgecolors=COLOR_NAVY, linewidths=1.8, zorder=6)
    ax.text(tx_x - tx_w/2, tx_y + 0.14, "TX Node", fontsize=10.5, fontweight='bold', color=COLOR_NAVY, ha='center', zorder=6)
    ax.text(tx_x - tx_w/2, tx_y - 0.18, r"$(x_{tx}, y_{tx})$", fontsize=9.0, color=COLOR_SLATE, ha='center', zorder=6)
    
    # RX Node box & label (centered at rx_x)
    rx_w, rx_h = 1.4, 0.85
    rx_box = patches.FancyBboxPatch((rx_x, rx_y - rx_h/2), rx_w, rx_h, boxstyle="round,pad=0.06",
                                   edgecolor=COLOR_NAVY, facecolor='#F8FAFC', linewidth=1.8, zorder=5)
    ax.add_patch(rx_box)
    ax.scatter([rx_x], [rx_y], color=COLOR_BLUE, s=70, edgecolors=COLOR_NAVY, linewidths=1.8, zorder=6)
    ax.text(rx_x + rx_w/2, rx_y + 0.14, "RX Node", fontsize=10.5, fontweight='bold', color=COLOR_NAVY, ha='center', zorder=6)
    ax.text(rx_x + rx_w/2, rx_y - 0.18, r"$(x_{rx}, y_{rx})$", fontsize=9.0, color=COLOR_SLATE, ha='center', zorder=6)

    # Top title banner box
    top_w, top_h = 6.2, 0.65
    top_box = patches.FancyBboxPatch((mid_x - top_w/2, 3.75), top_w, top_h, boxstyle="round,pad=0.08",
                                    edgecolor=COLOR_NAVY, facecolor='#1B365D', linewidth=1.5, zorder=5)
    ax.add_patch(top_box)
    ax.text(mid_x, 3.75 + top_h/2, r"1st FRESNEL ZONE BOUNDARY ($n = 1$) :  $d_1 + d_2 = D + \frac{\lambda}{2}$", 
            fontsize=10.5, fontweight='bold', color='#FFFFFF', ha='center', va='center', zorder=6)

    # Direct LOS Baseline Label below line
    ax.text(mid_x, mid_y - 0.32, r"Direct Line-of-Sight Baseline ($D = 4.0\mathrm{\ m}$)", 
            fontsize=10.0, fontweight='bold', color=COLOR_NAVY, ha='center')
    ax.text(mid_x, mid_y - 0.58, r"RF Parameters: $f = 2.437\mathrm{\ GHz\ (Channel\ 6)},\ \lambda = \frac{c}{f} \approx 0.123\mathrm{\ m\ (12.3\ cm)}$", 
            fontsize=8.5, color=COLOR_SLATE, ha='center')

    # Subtle legend in bottom right
    leg_box = patches.FancyBboxPatch((6.0, 0.72), 3.0, 0.48, boxstyle="round,pad=0.05",
                                    edgecolor='#CBD5E1', facecolor='#F8FAFC', linewidth=1.0, zorder=4)
    ax.add_patch(leg_box)
    ax.plot([6.2, 6.6], [0.96, 0.96], color=COLOR_NAVY, linestyle='--', linewidth=1.8)
    ax.text(6.75, 0.96, "Constructive Boundary", fontsize=8.0, color=COLOR_SLATE, va='center')

    # Set bounds and styling
    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(0.5, 4.6)
    ax.axis('off')
    
    # Save figure
    out_path = OUTPUT_DIR / "diagram_3_fresnel_zone_geometry.png"
    plt.tight_layout()
    plt.savefig(str(out_path), dpi=300, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close()
    print(f"[+] Successfully generated Fresnel diagram: {out_path} ({os.path.getsize(out_path):,} bytes)")

if __name__ == "__main__":
    create_fresnel_diagram()
