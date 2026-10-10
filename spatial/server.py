import time
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .types import SpatialState
from .live import LiveSpatialEngine

app = FastAPI(title="WiMotion 2.0 Multi-Link Spatial API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DASHBOARD_PATH = Path(__file__).resolve().parent.parent / "dashboard" / "observatory_multi.html"

# Default state clearly states STANDBY / DEMO mode without pretending hardware is live
LATEST_STATE = {
    "timestamp": time.time(),
    "mode": "STANDBY / DEMO",
    "hardware_connected": False,
    "signal_ok": False,
    "count": 0,
    "people": [],
    "zone": "CLEAR",
    "active_links": 0,
    "link_count": 8,
    "confidence": 0.0,
    "rate_hz": 0.0,
    "reason": "AWAITING_HARDWARE_CONNECTION"
}

engine_instance = None


@app.on_event("startup")
def startup_event():
    global engine_instance
    try:
        # Check if hardware serial is enabled (default enabled, gracefully falls back if unattached)
        if os.environ.get("WIMOTION_ENABLE_SERIAL", "1") == "1":
            engine_instance = LiveSpatialEngine()
            engine_instance.start()
            print("[*] Started hardware serial engine in background.")
    except Exception as e:
        print(f"[!] Note: Serial hardware not attached ({e}), running in HTTP API mode.")


@app.on_event("shutdown")
def shutdown_event():
    global engine_instance
    if engine_instance:
        engine_instance.stop()


from .config import load_config
from .replay_loader import list_recordings, load_recording_frames

SYSTEM_EVENTS = [
    {
        "id": 1,
        "timestamp": time.time(),
        "time_str": time.strftime("%H:%M:%S"),
        "severity": "INFO",
        "title": "ENGINE_BOOT",
        "message": "WiMotion 2.0 Spatial API server initialized",
        "source": "SYSTEM"
    }
]


@app.get("/")
def get_dashboard():
    if DASHBOARD_PATH.exists():
        return FileResponse(DASHBOARD_PATH)
    return HTMLResponse("<h1>WiMotion 2.0 Spatial API Running</h1><p>Visit /api/spatial</p>")


@app.get("/api/config")
def get_config():
    """Returns configured nodes, ports, transmitters, and sampling rules."""
    try:
        cfg = load_config()
        return {
            "receivers": cfg.receivers,
            "transmitters": cfg.transmitters,
            "zones": cfg.zones,
            "sampling": {
                "target_hz": cfg.sampling.target_hz,
                "minimum_hz": cfg.sampling.minimum_hz,
                "window_seconds": cfg.sampling.window_seconds,
                "step_seconds": cfg.sampling.step_seconds
            }
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/spatial")
def get_spatial():
    global engine_instance
    if engine_instance:
        return engine_instance.get_state()
    return LATEST_STATE


@app.post("/api/spatial/simulate")
def update_simulate(state: dict):
    """Allows testing HUD with simulated multi-person scenarios via POST"""
    global LATEST_STATE
    LATEST_STATE.update(state)
    LATEST_STATE["mode"] = "DEMO INJECTION (SIMULATED)"
    LATEST_STATE["timestamp"] = time.time()
    return {"status": "updated", "state": LATEST_STATE}


@app.get("/api/recordings")
def get_recordings():
    """Returns list of all discoverable raw CSI dataset recordings."""
    return {
        "recordings": list_recordings(),
        "storage_path": "data/raw",
        "schema": "multilink_data_<zone>_<count>P_<motion_state>.csv + metadata.json"
    }


@app.get("/api/recordings/{session_id}/data")
def get_recording_data(session_id: str):
    """Loads and computes playback frames for the selected recorded session."""
    data = load_recording_frames(session_id)
    if data is None:
        return {"error": f"Recording session '{session_id}' not found or empty."}
    return data


@app.get("/api/events")
def get_events():
    """Returns recent system and playback events."""
    return {"events": SYSTEM_EVENTS[-50:]}


@app.post("/api/events")
def post_event(event: dict):
    """Allows logging client-side navigation, replay, or simulation events."""
    event_id = len(SYSTEM_EVENTS) + 1
    new_evt = {
        "id": event_id,
        "timestamp": event.get("timestamp", time.time()),
        "time_str": event.get("time_str", time.strftime("%H:%M:%S")),
        "severity": event.get("severity", "INFO"),
        "title": event.get("title", "USER_ACTION"),
        "message": event.get("message", ""),
        "source": event.get("source", "FRONTEND")
    }
    SYSTEM_EVENTS.append(new_evt)
    return {"status": "logged", "event": new_evt}


@app.get("/health")
def health():
    return {
        "ok": True,
        "engine": "WiMotion 2.0 Multi-Link",
        "mode": "LIVE HARDWARE" if engine_instance else "STANDBY / DEMO",
        "timestamp": time.time()
    }
