# CHAPTER 4: CSI DATA ACQUISITION AND SOFTWARE INGESTION PIPELINE

---

## 4.1 Software Architecture and Data Flow

The WiMotion 2.0 software system transforms unstructured, high-rate physical layer byte streams into structured, synchronized link-level representations. The architecture operates across four distinct abstraction layers:

```
[PHYSICAL LAYER]        RX1 (COM8 @ 921.6k)          RX2 (COM9 @ 921.6k)
                                 │                            │
                                 ▼                            ▼
[INGESTION LAYER]       Worker Thread 1              Worker Thread 2
                        (Ring Buffer 1)              (Ring Buffer 2)
                                 │                            │
                                 └─────────────┬──────────────┘
                                               ▼
[PARSING & ROUTING]                 Parser & Demultiplexer
                                 (spatial/serial_manager.py)
                                               │
                                 ┌─────────────┴──────────────┐
                                 ▼                            ▼
[DATA GOVERNANCE]        Known Node Frames          Unknown Node Frames
                         (MAC Whitelisted)       (4C:11:AE:64:9A:05 -> UNKNOWN)
                                 │                            │
                                 ▼                            ▼
[SPATIAL PIPELINE]      8-Link Sliding Window      Quarantined Diagnostic
                        Buffer (2.0s Duration)             Bucket
                                 │
                                 ▼
[TELEMETRY & INFERENCE] Dual-Engine Real-Time HUD & Observatory Dashboard
```

1. **Physical Serial Ingestion Layer:** Two dedicated background threads handle raw byte streaming from `COM8` and `COM9`.
2. **Frame Parsing & Validation Layer:** Serial lines are validated for framing integrity, magic byte headers, and non-corrupt numeric fields.
3. **Identity Demultiplexing & Security Layer:** Physical MAC addresses are resolved against the active node table; rogue or ambient AP traffic is routed to an isolated quarantine bucket.
4. **Sliding Window Buffer Layer:** Valid records are inserted into a continuous 2.0-second time-series buffer partitioned across the 8 physical baselines.

---

## 4.2 CSI Acquisition at the Receiver

At the receiver node (operating in 802.11n promiscuous sniffer mode), the ESP32 Wi-Fi hardware MAC layer decodes incoming frames and triggers the low-level interrupt service routine (ISR) configured via the ESP-IDF API:

```c
// Receiver CSI Callback Registration (firmware/rx/main.c)
wifi_csi_config_t csi_config = {
    .lltf_en           = true,
    .htltf_en          = true,
    .stbc_htltf2_en    = false,
    .ltf_merge_en      = false,
    .channel_filter_en = false,
    .manu_scale        = false,
    .shift             = false
};
ESP_ERROR_CHECK(esp_wifi_set_csi_config(&csi_config));
ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(&wifi_csi_rx_cb, NULL));
```

When an 802.11 packet is decoded on Channel 6, the `wifi_csi_rx_cb` callback is invoked with a pointer to the `wifi_csi_info_t` struct:
- **`len`:** Total raw payload bytes (typically 128 bytes for 64 subcarriers in signed 8-bit I/Q format).
- **`rssi`:** Received Signal Strength Indication (in dBm) measured by receiver Automatic Gain Control (AGC).
- **`buf`:** Array of raw signed 8-bit integers representing interleaved In-Phase ($I_k$) and Quadrature ($Q_k$) components for each subcarrier $k \in [0, 63]$.
- **`mac`:** 6-byte source MAC address extracted from the 802.11 frame header.

The callback formats this binary payload into a single, compact comma-delimited ASCII string prefixed with the magic header `CSI_DATA` and pushes it directly to the hardware UART transmit FIFO buffer.

---

## 4.3 Serial Communication and Asynchronous Ingestion

Streaming two concurrent receivers each broadcasting at ~100 Hz generates an aggregate data rate of:

$$R_{\text{aggregate}} \approx 2\text{ Receivers} \times 100\text{ packets/sec} \times 240\text{ bytes/packet} \approx 48,000\text{ bytes/sec}$$

If the host operating system performs synchronous serial reads on the main server thread, any minor computational delay (such as running model inference or rendering WebSockets) causes the operating system serial input buffer to overflow, dropping frames and corrupting time-series continuity.

WiMotion 2.0 resolves this via **`spatial/serial_manager.py`**, which launches two asynchronous ingestion worker threads (`ReceiverWorker`):
- Each worker owns an independent `serial.Serial` instance configured with a 100 ms timeout and a 64 KB internal OS read buffer.
- Incoming bytes are accumulated into a local line buffer until a newline character (`\n`) is encountered.
- Complete lines are deposited into a thread-safe circular ring buffer protected by Python's `threading.Lock`.
- When the host consumer queries for new records, the worker atomically drains the buffer and returns newly arrived lines.

---

## 4.4 Packet Parsing and CSI Data Extraction

The parsing logic in **`spatial/parser.py`** inspects every raw serial line against strict structural validation rules before allocating memory:

```python
# Raw Frame Header Verification (spatial/parser.py)
if not line.startswith("CSI_DATA"):
    return None  # Discard framing noise and boot messages
parts = line.strip().split(",")
if len(parts) < 14:
    return None  # Discard truncated packets
```

### Table 4.1: Raw Serial CSI Packet Schema Definition

| Field Index | Token Name | Data Type | Physical Meaning | Example Value |
| :---: | :--- | :--- | :--- | :---: |
| 0 | `header` | String | Magic frame identifier | `CSI_DATA` |
| 1 | `rx_id` | String | Local receiver identifier assigned by port | `RX1` |
| 2 | `tx_mac` | String | Source transmitter hardware MAC address | `BC:DD:C2:CC:49:F4` |
| 3 | `channel` | Integer | Wi-Fi operational RF channel | `6` |
| 4 | `rssi` | Integer | Aggregate received signal power in dBm | `-42` |
| 5 | `noise_floor` | Integer | Internal baseband thermal noise floor register | `-96` |
| 6 | `rate` | Integer | Physical layer PHY transmission rate index | `11` |
| 7 | `sig_mode` | Integer | Signal modulation mode (0=Legacy, 1=HT) | `1` |
| 8 | `mcs` | Integer | Modulation and Coding Scheme index | `7` |
| 9 | `bandwidth` | Integer | Channel bandwidth (0=20MHz, 1=40MHz) | `0` |
| 10 | `smoothing` | Integer | Receiver channel estimation filter flag | `1` |
| 11 | `not_sounding` | Integer | Beamforming sounding frame flag | `0` |
| 12 | `len` | Integer | Count of subcarrier I/Q byte pairs | `64` |
| 13..N | `amplitudes` | Integer Array | Signed 8-bit In-phase ($I_k$) and Quadrature ($Q_k$) bytes | `[12, -4, 15, ...]` |

For each subcarrier $k \in [0, 63]$, the raw subcarrier amplitude $A_k$ is computed from the interleaved bytes:

$$A_k = \sqrt{I_k^2 + Q_k^2}$$

The parser returns a fully typed `CSIRecord` object encapsulating timestamp, receiver ID, transmitter MAC, RSSI, and the 64-element amplitude array.

---

## 4.5 Transmitter Identification Using MAC Addresses

In a multi-transmitter star topology, distinguishing which physical node emitted a packet is paramount. Early single-link sensing systems did not verify sender identities, leaving them vulnerable to any ambient 802.11 beacon.

WiMotion 2.0 binds physical layer measurements to spatial transmitter coordinates via an authoritative factory MAC lookup table:

```python
# Hardware Node Identity Mapping (spatial/parser.py)
TRANSMITTER_MAP = {
    "BC:DD:C2:CC:49:F4": "TX1",  # Zone 1 (North-East Quadrant)
    "1C:69:20:31:38:08": "TX2",  # Zone 2 (North-West Quadrant)
    "1C:69:20:31:4B:40": "TX3",  # Zone 3 (South-West Quadrant)
    "CC:7B:5C:28:84:70": "TX4"   # Zone 4 (South-East Quadrant)
}
```

When a frame is received, the 6-byte hexadecimal MAC string is extracted and normalized (uppercase, colon-delimited). If the address matches an entry in `TRANSMITTER_MAP`, the corresponding logical ID (`TX1`..`TX4`) is stamped onto the record.

---

## 4.6 Unknown-Node Filtering and Link Validation

During physical hardware trials in `ROOM_LAB_A`, packet sniffer logs revealed that ambient Wi-Fi access points frequently broadcast beacon frames on Channel 6. In particular, an uncoordinated third-party router with MAC:

$$\text{Ambient MAC} = \text{4C:11:AE:64:9A:05}$$

was observed transmitting periodic management frames that collided with experimental packets.

WiMotion 2.0 handles this through strict **Unknown-Node Filtering**:
1. If an incoming packet's source MAC does not match any entry in `TRANSMITTER_MAP`, the record's transmitter ID is marked as `UNKNOWN`.
2. The packet is **quarantined**: it is routed to a diagnostic logging bucket and explicitly excluded from spatial feature windows.
3. It is mathematically impossible for uncoordinated ambient Wi-Fi frames to corrupt the variance calculations of Links $L_0$ through $L_7$ or trigger false-alarm zone activations.

---

## 4.7 Buffer Management, Timestamping and Data Integrity

To guarantee that time-series analysis reflects physical reality, records are stamped with high-resolution host timestamps using `time.perf_counter()` immediately upon exit from the serial ring buffer.

### 4.7.1 Sliding Window Buffer Architecture (`spatial/window.py`)
Records are held in a dual-ended queue (`collections.deque`) maintaining a continuous temporal history:
- **Window Duration:** Fixed at $T_w = 2.0\text{ seconds}$.
- **Window Stride (Step):** Configured at $\Delta t_{\text{step}} = 0.5\text{ seconds}$ (75% temporal overlap).
- **Eviction Policy:** As new frames arrive, records with timestamps $t < (t_{\text{current}} - T_w)$ are automatically evicted, ensuring constant $O(1)$ memory consumption over arbitrarily long runtime sessions.

---

## 4.8 Error Handling and Software Safeguards

The ingestion pipeline incorporates multiple layers of defensive error handling:

* **Non-Blocking Framing Recovery:** If a serial framing error occurs (e.g., an interrupted USB transfer during a physical vibration of the cable), the parser scans forward until it detects the next newline byte (`\n`) and valid `CSI_DATA` header. Corrupted partial strings are discarded without raising unhandled Python exceptions.
* **Non-Finite Amplitude Clamping:** Any subcarrier amplitude evaluating to `NaN`, `Inf`, or exceeding physical 12-bit ADC limits ($A_k \ge 10,000$) is scrubbed and replaced with the window median.
* **Serial Port Auto-Reconnection:** If an active USB port is disconnected, the worker enters a graceful retry loop, attempting re-connection every 2.0 seconds while logging warnings without crashing the parent server process.

---

## 4.9 Data Acquisition Challenges and Solutions

During initial prototype integration, three major hardware-software interface bottlenecks were encountered and systematically resolved:

### Table 4.2: Data Acquisition Engineering Challenges & Solutions

| Technical Challenge | Root Cause | Engineering Solution Implemented in WiMotion 2.0 |
| :--- | :--- | :--- |
| **Serial Buffer Overflow** | Synchronous Python serial reads stalled during server WebSocket broadcast cycles. | Decoupled asynchronous multi-threaded workers with dedicated 64 KB circular ring buffers. |
| **Thread-Race Data Drops** | Multiple threads writing to CSV log files simultaneously without synchronization locks. | Deployed atomic `threading.Lock` across all file writers in `spatial/serial_manager.py`. |
| **Windows DPC Watchdog BSOD** | Windows serial driver polling disconnected USB ports during idle states. | Implemented **Safe Standby Mode**, closing active serial handles until explicit `LIVE` mode transition. |

---
*(End of Chapter 4 — Source: spatial/serial_manager.py, spatial/parser.py, and spatial/window.py)*
