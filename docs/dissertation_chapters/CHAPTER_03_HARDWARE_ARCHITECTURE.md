# CHAPTER 3: HARDWARE ARCHITECTURE AND EXPERIMENTAL DEPLOYMENT

---

## 3.1 System Requirements and Hardware Selection

The design of a device-free radio frequency (RF) sensing system imposes strict architectural constraints on the physical hardware layer. To capture human-induced multipath perturbations in real time without specialized laboratory equipment, the underlying RF transceivers must satisfy five core requirements:

1. **Subcarrier-Level Channel State Information (CSI) Accessibility:** The hardware platform must expose the raw Physical Layer (PHY) Channel Frequency Response (CFR)—including orthogonal subcarrier amplitudes and phase matrices—directly to software callbacks, rather than providing only macroscopic, scalar Received Signal Strength Indication (RSSI) values.
2. **Deterministic High-Rate Packet Emission:** Transmitters must support stable, programmable broadcast rates exceeding 100 Hz to sample fast Doppler and locomotion shifts without packet timing jitter.
3. **High-Throughput Serial Streaming:** The receiver must serialize multi-subcarrier raw data frames to a host processing hub over high-speed Universal Asynchronous Receiver-Transmitter (UART) lines without internal FIFO buffer overflows.
4. **Low Cost and Commercial Off-The-Shelf (COTS) Availability:** To validate the real-world feasibility of pervasive indoor situational awareness, transceivers must be commercially accessible commodity components rather than expensive Software-Defined Radios (SDRs) such as USRPs or specialized millimeter-wave (mmWave) radar front-ends.
5. **Decentralized Spatial Placement:** The nodes must operate independently with localized DC power, allowing distributed multi-point spatial installation across arbitrary indoor geometries.

Based on these criteria, the Espressif **ESP32-WROOM-32** microcontroller was selected as the foundational hardware platform across all sensing nodes.

---

## 3.2 ESP32-WROOM-32 and Supporting Components

The ESP32-WROOM-32 module integrates a 2.4 GHz Wi-Fi and Bluetooth coexistence system-on-chip (SoC) manufactured on TSMC's 40 nm low-power process. Its internal architecture and peripheral features relevant to WiMotion 2.0 include:

* **Processor Core:** Dual-core 32-bit Xtensa LX6 microprocessors running at a selectable clock frequency of up to 240 MHz, delivering up to 600 DMIPS computing power.
* **RF Transceiver:** Fully integrated 2.4 GHz receiver and transmitter complying with IEEE 802.11b/g/n standards. In 802.11n Orthogonal Frequency Division Multiplexing (OFDM) mode with a 20 MHz channel bandwidth, the hardware baseband exposes raw CSI matrices for 64 discrete subcarriers.
* **Internal Memory:** 520 KB on-chip SRAM alongside 4 MB external Quad-SPI flash memory for RTOS firmware storage and runtime circular buffers.
* **Serial Bridge Silicon:** Interfaced via an external Silicon Labs CP2102 USB-to-UART bridge controller, enabling continuous full-duplex asynchronous data rates up to 921,600 baud.
* **RF Front-End:** On-board inverted-F PCB trace antenna with nominal omnidirectional radiation pattern and typical peak gain of +2 dBi.

```
       ┌────────────────────────────────────────────────────────┐
       │                 ESP32-WROOM-32 SoC                     │
       │                                                        │
       │  ┌──────────────────────┐    ┌──────────────────────┐  │
       │  │   Xtensa LX6 Core 0  │    │   Xtensa LX6 Core 1  │  │
       │  │    (PRO_CPU: Wi-Fi)  │    │    (APP_CPU: Tasks)  │  │
       │  └──────────┬───────────┘    └──────────┬───────────┘  │
       │             │                           │              │
       │  ┌──────────┴───────────────────────────┴───────────┐  │
       │  │             520 KB Internal SRAM                 │  │
       │  └──────────────────────┬───────────────────────────┘  │
       │                         │                              │
       │  ┌──────────────────────┴───────────────────────────┐  │
       │  │          802.11n 2.4 GHz PHY Baseband            │  │
       │  │     (64-Subcarrier CSI Hardware Extraction)      │  │
       │  └──────────────────────┬───────────────────────────┘  │
       └─────────────────────────┼──────────────────────────────┘
                                 │
                     ┌───────────┴───────────┐
                     │ CP2102 USB-UART Bridge│
                     │  (921,600 Baud Link)  │
                     └───────────┬───────────┘
                                 │
                         To Host Laptop
```

---

## 3.3 Transmitter and Receiver Roles

The six microcontrollers operate under two asymmetric, complementary firmware roles designed using the official Espressif IoT Development Framework (ESP-IDF v5.1):

### 3.3.1 Active Transmitters (STA Mode)
The four transmitter nodes (designated **TX1**, **TX2**, **TX3**, and **TX4**) operate as Wi-Fi Stations (STA). Rather than maintaining a full TCP/IP networking association, the transmitters execute a lightweight FreeRTOS periodic timer loop:
- Every 10 milliseconds ($\Delta t = 10\text{ ms}$, corresponding to a frame frequency $f_{\text{tx}} \approx 100\text{ Hz}$), the transmitter baseband broadcasts an unencrypted 802.11 Action frame containing a sequence counter and node identifier payload.
- All four transmitters transmit on standard 2.4 GHz **Wi-Fi Channel 6** (center frequency $f_c = 2.437\text{ GHz}$).
- Transmit power is locked at $+20\text{ dBm}$ (maximum nominal output) with dynamic power management and Wi-Fi sleep modes disabled to eliminate baseline gain steps.

### 3.3.2 Centralized Promiscuous Receivers (AP Mode)
The two receiver nodes (designated **RX1** and **RX2**) operate in Wi-Fi Access Point (SoftAP) promiscuous sniffer mode:
- The receiver Wi-Fi PHY layer is configured via `esp_wifi_set_csi_rx_cb()` to invoke a low-level ISR callback upon successfully decoding the PHY preamble of any incoming frame on Channel 6.
- The callback captures the raw complex CSI struct (`wifi_csi_info_t`) from hardware registers before packet filtering drops non-whitelisted management traffic.
- The captured CSI record is immediately written to a high-speed hardware UART ring buffer and streamed over USB to the central host workstation.

---

## 3.4 Six-Node Architecture: Four Transmitters and Two Receivers

A critical technical distinction must be maintained regarding system topology: **WiMotion 2.0 does not employ an ad-hoc 802.11s mesh network.** In an ad-hoc mesh, packets hop between nodes, which introduces non-deterministic queuing latency and destroys physical layer timing coherence.

Instead, WiMotion 2.0 implements a **Distributed Multi-Link Star Topology** ($4\text{ TX} \to 2\text{ RX}$):
- Four perimeter transmitters broadcast simultaneously across the shared wireless medium.
- Two independent, spatially separated receivers capture these broadcasts concurrently.
- This creates **8 concurrent logical spatial links** ($4 \text{ Transmitters} \times 2 \text{ Receivers} = 8 \text{ Spatial Baselines}$) traversing the physical room environment.

```
                  [TX2: Zone 2 (NW)]                      [TX1: Zone 1 (NE)]
                 (1C:69:20:31:38:08)                     (BC:DD:C2:CC:49:F4)
                          │                                       │
                          │   Link 1 (RX1-TX2)                    │   Link 0 (RX1-TX1)
                          │   Link 5 (RX2-TX2)                    │   Link 4 (RX2-TX1)
                          │                                       │
                          ▼                                       ▼
                  ┌────────────────────────────────────────────────────────┐
                  │                 INDOOR MONITORED SPACE                 │
                  │              (4-Quadrant Spatial Grid)                 │
                  │                                                        │
                  │             [RX1: COM8]     [RX2: COM9]                │
                  │           (Central Dual-Receiver Hub)                  │
                  └────────────────────────────────────────────────────────┘
                          ▲                                       ▲
                          │                                       │
                          │   Link 2 (RX1-TX3)                    │   Link 3 (RX1-TX4)
                          │   Link 6 (RX2-TX3)                    │   Link 7 (RX2-TX4)
                          │                                       │
                 (1C:69:20:31:4B:40)                     (CC:7B:5C:28:84:70)
                  [TX3: Zone 3 (SW)]                      [TX4: Zone 4 (SE)]
```

---

## 3.5 Physical Link Allocation and Eight-Link Matrix

Every physical packet captured by either receiver is demultiplexed into one of the eight spatial links based on the tuple:

$$\text{Link ID} = (\text{Receiver ID}, \text{Transmitter MAC})$$

The complete physical link allocation matrix is defined in Table 3.1:

### Table 3.1: WiMotion 2.0 Physical Link Allocation & Spatial Baselines

| Link Index | Logical Link | Receiver Node | Host Port | Transmitter Node | Factory Hardware MAC Address | Primary Spatial Quadrant Monitored | Baseline Geometric Role |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **$L_0$** | `RX1-TX1` | RX1 | `COM8` | TX1 | `BC:DD:C2:CC:49:F4` | Zone 1 ($Z_1$ - North-East) | Direct LOS baseline covering room entrance |
| **$L_1$** | `RX1-TX2` | RX1 | `COM8` | TX2 | `1C:69:20:31:38:08` | Zone 2 ($Z_2$ - North-West) | Cross-quadrant diagonal path intersecting desk |
| **$L_2$** | `RX1-TX3` | RX1 | `COM8` | TX3 | `1C:69:20:31:4B:40` | Zone 3 ($Z_3$ - South-West) | Long diagonal baseline traversing full room length |
| **$L_3$** | `RX1-TX4` | RX1 | `COM8` | TX4 | `CC:7B:5C:28:84:70` | Zone 4 ($Z_4$ - South-East) | Lateral perimeter link monitoring East wall |
| **$L_4$** | `RX2-TX1` | RX2 | `COM9` | TX1 | `BC:DD:C2:CC:49:F4` | Zone 1 ($Z_1$ - North-East) | Lateral perimeter link monitoring North wall |
| **$L_5$** | `RX2-TX2` | RX2 | `COM9` | TX2 | `1C:69:20:31:38:08` | Zone 2 ($Z_2$ - North-West) | Direct LOS baseline covering primary workstation |
| **$L_6$** | `RX2-TX3` | RX2 | `COM9` | TX3 | `1C:69:20:31:4B:40` | Zone 3 ($Z_3$ - South-West) | Lateral perimeter link monitoring South-West boundary |
| **$L_7$** | `RX2-TX4` | RX2 | `COM9` | TX4 | `CC:7B:5C:28:84:70` | Zone 4 ($Z_4$ - South-East) | Direct LOS baseline covering window perimeter |

---

## 3.6 Experimental Room and Zone Layout

Empirical hardware benchmarking was conducted in `ROOM_LAB_A`, a rectangular indoor laboratory environment with dimensions:

$$\text{Length} = 5.80\text{ m}, \quad \text{Width} = 4.20\text{ m}, \quad \text{Floor Area} \approx 24.36\text{ m}^2$$

The room boundaries consist of standard concrete outer walls, hollow-brick partition walls, acoustic ceiling tiles at a height of 2.80 m, and ceramic tiled flooring. The physical space is divided into four functional quadrants:

* **Zone 1 ($Z_1$ - North-East Quadrant):** Entrance corridor and doorway passage. Primary path intersection for Links $L_0$ and $L_4$.
* **Zone 2 ($Z_2$ - North-West Quadrant):** Workstation zone containing an office desk, chairs, and computing equipment. Primary intersection for Links $L_1$ and $L_5$.
* **Zone 3 ($Z_3$ - South-West Quadrant):** Storage and perimeter flank. Characterized by longer propagation baselines ($L_2$ and $L_6$) and non-metallic shelving.
* **Zone 4 ($Z_4$ - South-East Quadrant):** Window wall and perimeter walkway. Primary intersection for Links $L_3$ and $L_7$.
* **CLEAR:** Ground truth baseline state denoting zero physical human presence within the enclosed space.

```
       ┌────────────────────────────────────────────────────────┐
       │ (0.0, 4.2)                                  (5.8, 4.2) │
       │   [TX2: Node NW] ────────── Northern Wall ───────── [TX1: Node NE]
       │         │                                                 │
       │         │           ZONE 2               ZONE 1           │
       │         │        (North-West)         (North-East)        │
       │         │       Primary Workstation     Doorway Access    │
       │         │                                                 │
       │   Western Wall         [RX1]         [RX2]          Eastern Wall
       │         │            (Central Workstation Hub)            │
       │         │                                                 │
       │         │           ZONE 3               ZONE 4           │
       │         │        (South-West)         (South-East)        │
       │         │        Storage Flank        Window Perimeter    │
       │         │                                                 │
       │   [TX3: Node SW] ────────── Southern Wall ───────── [TX4: Node SE]
       │ (0.0, 0.0)                                  (5.8, 0.0) │
       └────────────────────────────────────────────────────────┘
```

---

## 3.7 Firmware Configuration and Communication Parameters

Both transmitter and receiver firmware were written in C utilizing FreeRTOS tasks. The exact runtime parameters are recorded in Table 3.2:

### Table 3.2: WiMotion 2.0 Firmware Configuration Parameters

| Parameter Name | Configuration Setting | Engineering Function |
| :--- | :--- | :--- |
| **Wi-Fi Operating Band** | 2.4 GHz ISM Band | High penetration through non-metallic indoor materials |
| **Primary Channel** | Channel 6 ($f_c = 2.437\text{ GHz}$) | Fixed center frequency avoiding dynamic channel switching |
| **Channel Bandwidth** | 20 MHz (HT20) | Extracts 64 OFDM subcarriers per packet |
| **CSI Extraction Mask** | Full LL-LTF + HT-LTF | Captures full channel estimation preambles |
| **TX Broadcast Interval** | 10 milliseconds ($\approx 100\text{ Hz}$) | High temporal resolution capturing human gait transients |
| **TX Transmit Power** | +20 dBm (0.1 Watt) | Consistent SNR across all diagonal link lengths |
| **UART Baud Rate** | 921,600 baud | Prevents serial buffer stalls during 400 pkt/sec aggregate bursts |
| **UART Flow Control** | Disabled (Hardware FIFO) | Minimizes hardware handshaking latency |

---

## 3.8 Power, USB and Serial-Connection Management

The hardware deployment enforces strict isolation between AC mains power and signal acquisition:
- **Transmitter Nodes (TX1–TX4):** Each corner node is powered independently via isolated 5V/2A USB wall adapters. This ensures that transmitter ground loops do not corrupt receiver baseband references.
- **Receiver Nodes (RX1, RX2):** Plugged directly into dedicated host USB 3.0 ports via short (0.5m), shielded micro-USB cables. The host assigns virtual COM ports (`COM8` for RX1, `COM9` for RX2).
- **Safe Standby Circuitry:** When the WiMotion 2.0 software server is in `REPLAY` or `SIMULATION` mode, host serial port acquisition threads enter a low-power, non-polling **Safe Standby State**. This prevents Windows USB-UART serial drivers (specifically `usbser.sys` and `silabser.sys`) from triggering DPC Watchdog Violation kernel timeouts when hardware nodes are unpowered or disconnected.

---

## 3.9 Hardware Photographs and Deployment Record

A comprehensive photographic audit was captured on October 20–21, 2026, during the final experimental deployment in `ROOM_LAB_A`.

* **[Figure 3.1: Panoramic View of ROOM_LAB_A]:** Wide-angle photograph illustrating the 4-quadrant layout, spatial boundaries, and the central dual-receiver testbed.
* **[Figure 3.2: Corner Transmitter Installation (TX1 & TX2)]:** Close-up photographs showing the 3D-printed wall mounts, inverted-F antenna orientations, and isolated 5V power feeds.
* **[Figure 3.3: Corner Transmitter Installation (TX3 & TX4)]:** Close-up photographs showing South-West and South-East node placements at a calibrated height of 1.2 meters.
* **[Figure 3.4: Central Dual-Receiver Host Station]:** Macro photograph showing RX1 (`COM8`) and RX2 (`COM9`) connected to the host laptop, highlighting the physical antenna baseline separation ($d = 24.5\text{ cm}$).
* **[Figure 3.5: Subject Traversal Experiment]:** Photograph of the human subject executing single-occupant controlled walking trials across Quadrant 1 ($Z_1$).

---
*(End of Chapter 3 — Source: WiMotion 2.0 Hardware Engineering Manifest & HARDWARE_SESSION_LOG.txt)*
