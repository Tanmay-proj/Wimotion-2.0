from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CSIRecord:
    timestamp: float
    receiver_id: str
    source_mac: str
    rssi: Optional[float]
    amplitudes: List[float]
    rate_hz: Optional[float] = None
    tx_id: Optional[str] = None
    monotonic_time: float = 0.0


@dataclass
class LinkFeatures:
    receiver_id: str
    tx_id: str
    sample_count: int
    mean_amp: float
    std_amp: float
    mean_delta: float
    rms_delta: float
    p95_delta: float
    energy: float
    valid: bool = True


@dataclass
class SpatialState:
    timestamp: float
    signal_ok: bool
    count: int
    zone: str
    people: List[Dict[str, Any]] = field(default_factory=list)
    link_count: int = 0
    active_links: int = 0
    confidence: float = 0.0
    reason: str = ""
