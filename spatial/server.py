import time
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .types import SpatialState
from .live import LiveSpatialEngine

app = FastAPI(title="WiMotion 2.0 Multi-Link Spatial API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DASHBOARD_PATH = Path(__file__).resolve().parent.parent / "dashboard" / "observatory_multi.html"

# Default state
LATEST_STATE = {
    "timestamp": time.time(),
    "signal_ok": True,
    "count": 0,
    "people": [],
    "zone": "CLEAR",
    "active_links": 8,
    "link_count": 8,
    "confidence": 0.85,
    "reason": "STANDBY"
}

engine_instance = None


@app.on_event("startup")
def startup_event():
    global engine_instance
    try:
        # Check if hardware serial is explicitly requested or run in mock/standby mode
        if os.environ.get("WIMOTION_ENABLE_SERIAL", "0") == "1":
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
        return engine_instance.get_state()
    return LATEST_STATE


@app.post("/api/spatial/simulate")
def update_simulate(state: dict):
    """Allows testing HUD with simulated multi-person scenarios via POST"""
    global LATEST_STATE
    LATEST_STATE.update(state)
    LATEST_STATE["timestamp"] = time.time()
    return {"status": "updated", "state": LATEST_STATE}


@app.get("/health")
def health():
    return {
        "ok": True,
        "engine": "WiMotion 2.0 Multi-Link",
        "timestamp": time.time()
    }
