import threading
import time
import queue
from typing import Dict, Optional, Callable, Any
from pathlib import Path
from collections import Counter

from .types import CSIRecord
from .parser import parse_line
from .config import NodeConfig, build_mac_map

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


class SerialReceiverWorker(threading.Thread):
    def __init__(
        self,
        receiver_id: str,
        port: str,
        baud: int,
        mac_map: Dict[str, str],
        on_record_callback: Callable[[CSIRecord], None],
        rate_min: float = 4.0
    ):
        super().__init__(daemon=True)
        self.receiver_id = receiver_id
        self.port = port
        self.baud = baud
        self.mac_map = mac_map
        self.callback = on_record_callback
        self.rate_min = rate_min
        self.running = False
        self.serial_conn: Optional[serial.Serial] = None
        
        # Aggregate and per-link rate tracking
        self.packet_count = 0
        self.per_tx_counts = Counter()
        self.last_rate_calc = time.time()
        self.current_rate_hz = 0.0
        self.current_per_tx_rates = {}

    def run(self):
        self.running = True
        if not SERIAL_AVAILABLE:
            print(f"[!] PySerial not available. Cannot start {self.receiver_id} on {self.port}")
            return

        while self.running:
            try:
                print(f"[*] {self.receiver_id}: Connecting to {self.port} @ {self.baud} baud...")
                self.serial_conn = serial.Serial()
                self.serial_conn.port = self.port
                self.serial_conn.baudrate = self.baud
                self.serial_conn.timeout = 1.0
                self.serial_conn.dtr = False
                self.serial_conn.rts = False
                self.serial_conn.open()
                print(f"[+] {self.receiver_id}: Connected successfully to {self.port}")
                self.serial_conn.reset_input_buffer()

                while self.running:
                    line_bytes = self.serial_conn.readline()
                    if not line_bytes:
                        continue

                    try:
                        line = line_bytes.decode("ascii", errors="ignore").strip()
                    except Exception:
                        continue

                    record = parse_line(line, self.receiver_id)
                    if record:
                        # Map source MAC to TX ID
                        if record.source_mac in self.mac_map:
                            record.tx_id = self.mac_map[record.source_mac]
                        else:
                            record.tx_id = f"MAC_{record.source_mac[-5:].replace(':', '')}"

                        # Update aggregate and per-TX counters
                        self.packet_count += 1
                        self.per_tx_counts[record.tx_id] += 1

                        now = time.time()
                        dt = now - self.last_rate_calc
                        if dt >= 1.0:
                            self.current_rate_hz = self.packet_count / dt
                            self.current_per_tx_rates = {
                                tx: round(cnt / dt, 1)
                                for tx, cnt in self.per_tx_counts.items()
                            }
                            self.packet_count = 0
                            self.per_tx_counts.clear()
                            self.last_rate_calc = now

                        record.rate_hz = self.current_per_tx_rates.get(record.tx_id, None)
                        self.callback(record)

            except Exception as e:
                print(f"[!] {self.receiver_id} ({self.port}) connection error: {e}. Retrying in 2s...")
                time.sleep(2.0)
            finally:
                if self.serial_conn and self.serial_conn.is_open:
                    self.serial_conn.close()

    def stop(self):
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()


class MultiSerialManager:
    def __init__(self, config: NodeConfig, on_record_callback: Callable[[CSIRecord], None]):
        self.config = config
        self.mac_map = build_mac_map(config)
        self.callback = on_record_callback
        self.workers: Dict[str, SerialReceiverWorker] = {}

    def start_all(self):
        for rx_id, rx_cfg in self.config.receivers.items():
            port = rx_cfg.get("port", "COM8")
            baud = rx_cfg.get("baud", 921600)
            worker = SerialReceiverWorker(
                receiver_id=rx_id,
                port=port,
                baud=baud,
                mac_map=self.mac_map,
                on_record_callback=self.callback,
                rate_min=self.config.sampling.minimum_hz
            )
            self.workers[rx_id] = worker
            worker.start()
            print(f"[*] Started worker for {rx_id} on {port}")

    def stop_all(self):
        for rx_id, worker in self.workers.items():
            worker.stop()
            print(f"[*] Stopped worker {rx_id}")

    def get_health(self) -> Dict[str, Any]:
        health_report = {}
        for rx_id, w in self.workers.items():
            per_rates = dict(w.current_per_tx_rates)
            # Evaluate if all configured transmitters are transmitting above 1.0 Hz
            active_links_count = sum(1 for r in per_rates.values() if r >= 1.0)
            
            if w.current_rate_hz >= self.config.sampling.minimum_hz:
                if active_links_count >= len(self.config.transmitters):
                    status = "HEALTHY"
                elif active_links_count > 0:
                    status = "PARTIAL"
                else:
                    status = "PARTIAL"
            else:
                status = "DEGRADED"

            health_report[rx_id] = {
                "port": w.port,
                "running": w.running,
                "aggregate_rate_hz": round(w.current_rate_hz, 2),
                "rate_hz": round(w.current_rate_hz, 2),
                "per_link_rates": per_rates,
                "active_tx_count": active_links_count,
                "status": status,
                "healthy": status == "HEALTHY"
            }
        return health_report
