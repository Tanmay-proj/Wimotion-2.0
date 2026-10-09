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


@app.get("/")
def get_dashboard():
    if DASHBOARD_PATH.exists():
        return FileResponse(DASHBOARD_PATH)
    return HTMLResponse("<h1>WiMotion 2.0 Spatial API Running</h1><p>Visit /api/spatial</p>")


@app.get("/api/spatial")
def get_spatial():
    global engine_instance
    if engine_instance:
        state = engine_instance.get_state()
        state["mode"] = "LIVE HARDWARE"
        state["hardware_connected"] = True
        return state
    return LATEST_STATE


@app.post("/api/spatial/simulate")
def update_simulate(state: dict):
    """Allows testing HUD with simulated multi-person scenarios via POST"""
    global LATEST_STATE
    LATEST_STATE.update(state)
    LATEST_STATE["mode"] = "DEMO INJECTION (SIMULATED)"
    LATEST_STATE["timestamp"] = time.time()
    return {"status": "updated", "state": LATEST_STATE}


@app.get("/health")
def health():
    return {
        "ok": True,
        "engine": "WiMotion 2.0 Multi-Link",
        "mode": "LIVE HARDWARE" if engine_instance else "STANDBY / DEMO",
        "timestamp": time.time()
    }
