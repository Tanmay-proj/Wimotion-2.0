from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any
import json


@dataclass
class SamplingConfig:
    target_hz: float = 20.0
    minimum_hz: float = 4.0
    window_seconds: float = 2.0
    step_seconds: float = 0.5


@dataclass
class NodeConfig:
    receivers: Dict[str, Any]
    transmitters: Dict[str, Any]
    zones: List[str]
    sampling: SamplingConfig


def load_config(path: str = "config/nodes.json") -> NodeConfig:
    p = Path(path)
    if not p.is_absolute():
        # Resolve relative to project root (parent of spatial directory)
        root = Path(__file__).resolve().parent.parent
        p = root / path

    data = json.loads(p.read_text(encoding="utf-8"))

    sampling = SamplingConfig(**data.get("sampling", {}))

    return NodeConfig(
        receivers=data["receivers"],
        transmitters=data["transmitters"],
        zones=data["zones"],
        sampling=sampling
    )


def build_mac_map(config: NodeConfig) -> Dict[str, str]:
    mapping = {}
    for tx_id, info in config.transmitters.items():
        mac = info.get("mac", "")
        if mac.startswith("REPLACE"):
            continue
        mac = mac.replace("-", ":").upper()
        mapping[mac] = tx_id
    return mapping
