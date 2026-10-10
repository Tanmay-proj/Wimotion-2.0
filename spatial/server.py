import time
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .types import SpatialState
from .live import LiveSpatialEngine
from .config import load_config
from .replay_loader import list_recordings, load_recording_frames

DASHBOARD_PATH = Path(__file__).resolve().parent.parent / "dashboard" / "observatory_multi.html"

# Authoritative Operating Mode: "LIVE", "REPLAY", "SIMULATION"
CURRENT_MODE = "LIVE"

# Isolated Default Standby State
STANDBY_STATE = {
    "timestamp": time.time(),
    "source": "LIVE_STANDBY",
    "mode": "STANDBY / AWAITING HARDWARE",
    "hardware_connected": False,
    "signal_ok": False,
    "count": 0,
    "active_zone_count": 0,
    "people": [],
    "zone": "UNKNOWN",
    "inference_status": "UNAVAILABLE",
    "active_links": 0,
    "link_count": 8,
    "confidence": None,
    "rate_hz": 0.0,
    "reason": "AWAITING_HARDWARE_CONNECTION",
    "receiver_health": {},
    "link_features": []
}

# Isolated Simulation State (cannot leak into or be overridden by LIVE hardware)
SIMULATION_STATE = {
    "timestamp": time.time(),
    "source": "SIMULATION",
    "mode": "SIMULATION (SYNTHETIC BENCHMARK)",
    "hardware_connected": False,
    "signal_ok": True,
    "count": 0,
    "active_zone_count": 0,
    "people": [],
    "zone": "CLEAR",
    "inference_status": "BASELINE_CLEAR",
    "active_links": 8,
    "link_count": 8,
    "confidence": None,
    "rate_hz": 148.8,
    "reason": "SYNTHETIC_BENCHMARK",
    "receiver_health": {},
    "link_features": []
}

# Isolated Replay State
REPLAY_STATE = {
    "timestamp": time.time(),
    "source": "REPLAY",
    "mode": "RECORDED REPLAY",
    "hardware_connected": False,
    "signal_ok": False,
    "count": 0,
    "active_zone_count": 0,
    "people": [],
    "zone": "UNKNOWN",
    "inference_status": "AWAITING_REPLAY_START",
    "active_links": 0,
    "link_count": 8,
    "confidence": None,
    "rate_hz": 0.0,
    "reason": "REPLAY_STANDBY",
    "receiver_health": {},
    "link_features": []
}

engine_instance = None


def _launch_browser_when_ready(url: str = "http://127.0.0.1:8000", max_retries: int = 60, delay: float = 0.15):
    """
    Polls the server's /health endpoint in a background daemon thread.
    Opens the default browser only when HTTP 200 is confirmed, eliminating
    the 'Site can't be reached' connection-refused race condition.
    """
    import urllib.request
    import webbrowser
    import threading

    def _poll():
        health_url = f"{url}/health"
        for _ in range(max_retries):
            time.sleep(delay)
            try:
                with urllib.request.urlopen(health_url, timeout=0.5) as resp:
                    if resp.status == 200:
                        print(f"[*] Server ready! Opening observatory dashboard: {url}")
                        webbrowser.open(url)
                        return
            except Exception:
                pass
        print("[!] Note: Server health check timeout during auto-browser open.")

    t = threading.Thread(target=_poll, daemon=True, name="wimotion-browser-opener")
    t.start()
    return t


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    global engine_instance
    try:
        if os.environ.get("WIMOTION_ENABLE_SERIAL", "1") == "1":
            engine_instance = LiveSpatialEngine()
            engine_instance.start()
            print("[*] Started hardware serial engine in background.")
    except Exception as e:
        print(f"[!] Note: Serial hardware not attached ({e}), running in HTTP API mode.")

    # Only auto-open if explicitly requested and not running under CI / test harness
    if os.environ.get("WIMOTION_AUTO_OPEN_BROWSER", "0") == "1" and not os.environ.get("CI"):
        _launch_browser_when_ready()

    yield

    if engine_instance:
        engine_instance.stop()


app = FastAPI(title="WiMotion 2.0 Multi-Link Spatial API", version="2.0.0", lifespan=lifespan)

# Restrict CORS to exact local development and dashboard origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)



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
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mode")
def get_mode():
    """Returns current active operating mode."""
    return {"mode": CURRENT_MODE}


@app.post("/api/mode")
def set_mode(payload: dict):
    """Sets the authoritative operating mode ('LIVE', 'REPLAY', 'SIMULATION')."""
    global CURRENT_MODE, SIMULATION_STATE
    new_mode = payload.get("mode", "").upper()
    if new_mode not in ["LIVE", "REPLAY", "SIMULATION"]:
        raise HTTPException(status_code=400, detail="Mode must be 'LIVE', 'REPLAY', or 'SIMULATION'")

    old_mode = CURRENT_MODE
    CURRENT_MODE = new_mode

    # Clear stale simulation state when leaving simulation mode
    if old_mode == "SIMULATION" and new_mode != "SIMULATION":
        SIMULATION_STATE["people"] = []
        SIMULATION_STATE["zone"] = "CLEAR"
        SIMULATION_STATE["count"] = 0
        SIMULATION_STATE["active_zone_count"] = 0

    evt = {
        "id": len(SYSTEM_EVENTS) + 1,
        "timestamp": time.time(),
        "time_str": time.strftime("%H:%M:%S"),
        "severity": "INFO",
        "title": "MODE_SWITCH",
        "message": f"Operating mode switched from {old_mode} to {new_mode}",
        "source": "SERVER"
    }
    SYSTEM_EVENTS.append(evt)

    return {"status": "ok", "mode": CURRENT_MODE}


@app.get("/api/spatial")
def get_spatial():
    """Authoritative endpoint for current spatial state, strictly isolated by mode."""
    global engine_instance, CURRENT_MODE, SIMULATION_STATE, REPLAY_STATE, STANDBY_STATE

    if CURRENT_MODE == "SIMULATION":
        st = dict(SIMULATION_STATE)
        st["source"] = "SIMULATION"
        st["authoritative_mode"] = "SIMULATION"
        return st

    elif CURRENT_MODE == "REPLAY":
        st = dict(REPLAY_STATE)
        st["source"] = "REPLAY"
        st["authoritative_mode"] = "REPLAY"
        return st

    else:
        # LIVE hardware mode
        if engine_instance:
            st = engine_instance.get_state()
            st["source"] = "LIVE"
            st["authoritative_mode"] = "LIVE"
            return st
        st = dict(STANDBY_STATE)
        st["source"] = "LIVE_STANDBY"
        st["authoritative_mode"] = "LIVE"
        return st


@app.post("/api/spatial/simulate")
def update_simulate(state: dict):
    """Safely updates simulation state and authoritatively activates SIMULATION mode."""
    global SIMULATION_STATE, CURRENT_MODE
    CURRENT_MODE = "SIMULATION"
    SIMULATION_STATE.update(state)
    SIMULATION_STATE["source"] = "SIMULATION"
    SIMULATION_STATE["mode"] = state.get("mode", "SIMULATION (SYNTHETIC)")
    SIMULATION_STATE["timestamp"] = time.time()
    return {"status": "updated", "state": SIMULATION_STATE}


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
        raise HTTPException(status_code=404, detail=f"Recording session '{session_id}' not found or empty.")
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
    """Truthfully distinguishes server reachability, engine thread, and live hardware CSI ingestion."""
    hw_connected = False
    signal_ok = False
    rate = 0.0

    if engine_instance:
        st = engine_instance.get_state()
        hw_connected = st.get("hardware_connected", False)
        signal_ok = st.get("signal_ok", False)
        rate = st.get("rate_hz", 0.0)

    return {
        "ok": True,
        "server_reachable": True,
        "engine_active": engine_instance is not None,
        "hardware_connected": hw_connected,
        "signal_ok": signal_ok,
        "rate_hz": rate,
        "active_mode": CURRENT_MODE,
        "timestamp": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    os.environ["WIMOTION_AUTO_OPEN_BROWSER"] = "1"
    uvicorn.run("spatial.server:app", host="127.0.0.1", port=8000, reload=False)

