# CHAPTER 2: THEORETICAL FOUNDATIONS OF WI-FI CSI SENSING

---

## 2.1 Fundamentals of Wireless Signal Propagation

Radio frequency (RF) sensing relies on the physical laws governing electromagnetic wave propagation in terrestrial environments. When an isotropic transmitter antenna radiates power $P_t$ in free space, the electromagnetic wave expands spherically. At a distance $d$ from the transmitter, the power density $S$ is distributed uniformly over the surface of a sphere of radius $d$:

$$S = \frac{P_t}{4 \pi d^2}$$

If the receiver possesses an effective antenna aperture $A_e = \frac{\lambda^2 G_r}{4 \pi}$ (where $\lambda = \frac{c}{f}$ is the operational wavelength and $G_r$ is receiver antenna gain), the received power $P_r$ under ideal line-of-sight (LOS) conditions follows the **Friis Transmission Formula**:

$$P_r = P_t G_t G_r \left( \frac{\lambda}{4 \pi d} \right)^2$$

For standard 2.4 GHz Wi-Fi operating on Channel 6 ($f = 2.437\text{ GHz}$), the electromagnetic wavelength in air is:

$$\lambda = \frac{3 \times 10^8\text{ m/s}}{2.437 \times 10^9\text{ Hz}} \approx 0.123\text{ meters} \quad (12.3\text{ cm})$$

Because human body anatomical dimensions (torso width $\approx 40\text{ cm}$, chest depth $\approx 25\text{ cm}$, limb diameter $\approx 10\text{ cm}$) are on the same order of magnitude as the $12.3\text{ cm}$ wavelength, the human body operates in the **resonant scattering regime**, making it a highly effective scatterer of 2.4 GHz RF waves.

---

## 2.2 Reflection, Diffraction, Absorption and Multipath Effects

In an enclosed architectural space, an electromagnetic wave emitted by an antenna does not propagate through free space. Instead, it interacts with physical boundaries through four fundamental propagation mechanisms:

```
                                  [INCIDENT EM WAVE]
                                           │
         ┌───────────────────┬─────────────┴───────┬───────────────────┐
         ▼                   ▼                     ▼                   ▼
   [SPECULAR          [DIFFRACTION /        [DIELECTRIC          [DIFFUSE
   REFLECTION]         EDGE SCATTER]         ABSORPTION]        SCATTERING]
Smooth walls,        Doorway corners,      Human tissue,        Rough surfaces,
floors, ceilings     furniture edges       water containers     textured walls
```

1. **Specular Reflection:** Occurs when an RF wave encounters a planar boundary whose dimensions are significantly larger than $\lambda$ (e.g., concrete walls, metal filing cabinets, glass windows). The reflection angle equals the incidence angle according to Snell's law.
2. **Edge Diffraction:** Occurs when an RF wavefront strikes the sharp geometric edge of an obstacle (e.g., doorway frames, desk partitions). According to the Huygens-Fresnel principle, the obstacle edge acts as a secondary line source, bending waves into geometric shadow zones (Non-Line-of-Sight propagation).
3. **Dielectric Absorption:** Human tissue consists primarily of water and dissolved electrolytes ($\epsilon_r \approx 50\text{ to }56$ at 2.4 GHz). When an RF wave enters the human body, dielectric losses convert a portion of the wave's electromagnetic energy into heat, causing substantial forward attenuation.
4. **Diffuse Scattering:** Occurs when waves strike rough, irregular surfaces whose feature sizes are comparable to $\lambda$, scattering energy across an omnidirectional hemisphere.

---

## 2.3 RSSI Versus Channel State Information

Early wireless sensing attempts relied on **Received Signal Strength Indication (RSSI)**. However, RSSI is fundamentally inadequate for spatial indoor sensing due to physical-layer limitations:

### Table 2.1: Physical Layer Comparison: RSSI vs. Channel State Information (CSI)

| Technical Dimension | Received Signal Strength Indication (RSSI) | Channel State Information (CSI) |
| :--- | :--- | :--- |
| **Physical Abstraction** | Macroscopic scalar power metric (in dBm) | Microscopic complex channel matrix ($H \in \mathbb{C}^{M \times K}$) |
| **Spectral Granularity** | Single averaged value across the entire 20 MHz channel | Independent values across 64 discrete subcarriers |
| **Phase Availability** | No phase information (scalar magnitude only) | Complex representation: Amplitude and Phase per subcarrier |
| **Multipath Sensitivity** | Blind to multipath shifts; subject to destructive fading | Resolves individual multipath subcarrier interference patterns |
| **Temporal Stability** | Prone to macroscopic noise; high variance in static rooms | Highly stable in static environments; responsive to motion |
| **Spatial Resolution** | Cannot differentiate location; coarse proximity only | Multi-subcarrier diversity enables spatial quadrant resolution |

```
       RSSI (Coarse Scalar Measurement)             CSI (Fine-Grained 64-Subcarrier Matrix)
      ┌─────────────────────────────────┐          ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
      │           -54 dBm               │    VS    │ 1 │ 2 │ 3 │...│...│...│...│...│63 │64 │
      │ (Averaged across full 20 MHz)   │          └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
      └─────────────────────────────────┘          Complex Channel Response per Subcarrier: H_k = |a_k| e^(j phi_k)
```

---

## 2.4 CSI as a Complex Channel Frequency Response

In modern wireless systems, the indoor radio channel between transmitter and receiver is modeled as a linear time-variant filter characterized by its **Channel Impulse Response (CIR)**:

$$h(\tau, t) = \sum_{i=1}^{N} a_i(t) e^{-j \phi_i(t)} \delta(\tau - \tau_i(t))$$

Where $N$ is the total count of multipath rays, and $a_i(t)$, $\phi_i(t)$, and $\tau_i(t)$ represent the amplitude, phase shift, and propagation delay of the $i$-th multipath ray at time $t$.

Applying the continuous Fourier transform yields the **Channel Frequency Response (CFR)**:

$$H(f, t) = \int_{-\infty}^{\infty} h(\tau, t) e^{-j 2 \pi f \tau} d\tau = \sum_{i=1}^{N} a_i(t) e^{-j (2 \pi f \tau_i(t) + \phi_i(t))}$$

In digital baseband processing, the CFR is sampled across $K$ discrete orthogonal subcarriers. For the $k$-th subcarrier at frequency $f_k$, Channel State Information represents the complex ratio between the transmitted symbol $X(f_k, t)$ and received symbol $Y(f_k, t)$ (corrupted by additive Gaussian noise $W(f_k, t)$):

$$Y(f_k, t) = H(f_k, t) X(f_k, t) + W(f_k, t)$$

$$\hat{H}(f_k, t) = |H(f_k, t)| e^{j \angle H(f_k, t)}$$

Where $|H(f_k, t)|$ represents subcarrier amplitude attenuation, and $\angle H(f_k, t)$ represents subcarrier phase shift.

---

## 2.5 OFDM and Wi-Fi Subcarrier Structure

Under the IEEE 802.11n specification, a standard 20 MHz Wi-Fi channel is partitioned into **64 orthogonal subcarriers** spaced at exact intervals of $\Delta f = 312.5\text{ kHz}$:

$$\text{Subcarrier Spacing} = \frac{20\text{ MHz}}{64} = 312.5\text{ kHz}$$

The 64 subcarriers are indexed from $k = -32$ to $+31$:
- **Data Subcarriers (52):** Carry user payload symbols and channel pilot data.
- **Pilot Subcarriers (4):** Dedicated to carrier frequency offset tracking (at indices $-21, -7, +7, +21$).
- **Null / Guard Subcarriers (8):** Guard bands at channel edges ($k \in [-32, -29]$ and $[+29, +31]$) and the direct current (DC) null at center frequency ($k = 0$) to prevent receiver local oscillator leakage.

On Espressif ESP32 hardware, the baseband exposes the full 64-element array. Subcarrier amplitude cleaning filters out guard and null bands to isolate the active spectral components.

---

## 2.6 Human-Induced Changes in Wireless Channels

When an indoor room is completely static, the multipath rays reflect solely off fixed surfaces (walls, floor, ceiling, desk). The resulting Channel Frequency Response $H_{\text{static}}(f)$ remains constant over time.

When a human subject enters and walks through the environment, the total multipath field decomposes into two components:

$$H(f, t) = H_{\text{static}}(f) + H_{\text{dynamic}}(f, t)$$

$$H_{\text{dynamic}}(f, t) = \sum_{m \in \text{Body Rays}} a_m(t) e^{-j \frac{2 \pi}{\lambda} d_m(t)}$$

Where $d_m(t)$ is the physical propagation distance of the ray scattered off the moving human body. 

As the subject walks at velocity $v$, the propagation distance changes continuously ($d_m(t) = d_0 + v t$). This causes the phase term $\frac{2 \pi}{\lambda} d_m(t)$ to rotate rapidly. When this dynamic ray interferes with the static multipath rays at the receiver antenna, it induces **periodic constructive and destructive interference ripples** across individual subcarrier amplitudes. By extracting the temporal variance and envelope statistics of these ripples, the system detects human locomotion.

---

## 2.7 Fresnel Zones and Link Sensitivity

The spatial sensitivity of an RF link is governed by **Fresnel Zone Diffraction Theory**. Between a transmitter antenna at $(x_{\text{tx}}, y_{\text{tx}})$ and a receiver antenna at $(x_{\text{rx}}, y_{\text{rx}})$ separated by distance $D$, the $n$-th Fresnel zone is an ellipsoid whose boundary satisfies:

$$d_1 + d_2 - D = n \frac{\lambda}{2}$$

Where $d_1$ is the distance from the transmitter to a point on the ellipsoid, $d_2$ is the distance from that point to the receiver, and $n \in \{1, 2, 3, \dots\}$.

```
                                  [1st Fresnel Zone Boundary (n = 1)]
                               ┌────────────────────────────────────────┐
                               │                 d1 + d2 = D + lambda/2 │
                 TX ───────────┼────────────────────────────────────────┼─────────── RX
             (x_tx, y_tx)      │            Direct LOS Baseline (D)     │       (x_rx, y_rx)
                               │                                        │
                               └────────────────────────────────────────┘
```

The maximum radius $r_1$ of the first Fresnel zone ($n = 1$) occurs at the midpoint ($d_1 = d_2 = D/2$):

$$r_1 = \frac{1}{2} \sqrt{\lambda D}$$

For an indoor link with length $D = 4.0\text{ meters}$ operating at $\lambda = 0.123\text{ meters}$:

$$r_1 = \frac{1}{2} \sqrt{0.123 \times 4.0} = \frac{1}{2} \sqrt{0.492} \approx 0.35\text{ meters} \quad (35\text{ cm})$$

### Physical Sensitivity Implications:
- **Inside the 1st Fresnel Zone ($r < 35\text{ cm}$):** A human body traversing directly across the line-of-sight path obstructs the primary energy corridor, creating massive amplitude attenuation and sharp variance spikes.
- **Outside the Primary Fresnel Zone ($r > 1.0\text{ m}$):** Human movement produces only diffuse, higher-order multipath scatter. The amplitude perturbations decay rapidly with distance, falling close to the ambient receiver noise floor.

---

## 2.8 Multi-Link Spatial Diversity

The fundamental limitation of single-link RF sensing (as discovered during Project Echo) is **directional and spatial ambiguity**:
- An object walking 50 cm to the left of a single LOS link produces the exact same amplitude variance signature as an object walking 50 cm to the right.
- Motion occurring in the outer corners of a room lies entirely outside the link's primary Fresnel zones, resulting in complete sensing blind spots.

```
       [SINGLE-LINK AMBIGUITY]                [MULTI-LINK SPATIAL MESH COVERAGE]
       TX ═════════════════════ RX            TX2 ─────────── (L1) ─────────── TX1
             [Blind Spot]                      │ \                           / │
                                               │   \       [ROOM SENSING]  /   │
                                              (L5)   (L2)     GRID       (L0) (L4)
                                               │       \               /       │
                                               │         \   RX1   RX2         │
                                               │           \  │     │          │
                                              TX3 ─────────── (L7) ─────────── TX4
```

To resolve spatial ambiguity, WiMotion 2.0 deploys **Multi-Link Spatial Diversity**:
- By creating 8 intersecting baselines across four quadrants, every spatial quadrant is traversed by at least one primary direct LOS link and two cross-diagonal links.
- When an individual walks in Zone 1, Links $L_0$ and $L_4$ experience deep primary Fresnel perturbations, while distant links ($L_2$ and $L_6$) remain largely undisturbed.
- By evaluating the relative distribution of variance across all 8 links simultaneously, the system resolves orthogonal quadrant coordinates unambiguously.

---

## 2.9 Limitations of CSI-Based Interpretation

To maintain rigorous scientific standards, the physical limitations of interpreting COTS Wi-Fi CSI must be explicitly recognized:

1. **Sampled Channel Metric, Not an Image:** CSI is a sampled complex scalar representing the aggregated channel transfer function. It does not provide direct optical pixels, range-Doppler point clouds, or physical silhouettes of a human body.
2. **Phase Noise & Carrier Frequency Offset (CFO):** In commodity Wi-Fi silicon, the transmitter and receiver operate on unsynchronized local oscillators. Small frequency differences ($\Delta f \approx 10\text{ to }50\text{ kHz}$) cause the raw phase measurements $\angle H(f_k, t)$ to rotate continuously between $[-\pi, +\pi]$ from packet to packet, preventing raw phase from being used directly without conjugate phase sanitization.
3. **Complex Indoor Geometry & Shadowing:** Furniture, metallic filing cabinets, and structural pillars create static multipath shadowing. RF sensitivity is not spatially uniform throughout a room; quadrants positioned further from receiver antennas inherently suffer from geometric path loss.

---
*(End of Chapter 2 — Source: Wi-Fi Physical Layer Standards IEEE 802.11n & Radio Propagation Theory)*
