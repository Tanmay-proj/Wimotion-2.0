# WiMotion 2.0 (Wi-CaL Multi-Link Sensing Edition)

**Project:** WiMotion 2.0 — WiFi Multi-Link Sensing, Localization & Occupancy Estimation  
**Evolution of:** Project WiMotion v1.0 (E:\WIFI_INTERFEROMETRIC_NEURAL_SENSING\wimotion)  
**Scientific Foundation:** Wi-CaL (IEEE Access 2022) Multi-Link CSI Sensing Framework  

---

## Objectives
1. **Multi-Link CSI Acquisition:** Simultaneous multi-stream CSI ingestion across distributed ESP32 nodes.
2. **Multi-Person Occupancy Counting:** Distinguishing between Empty (0), Single Occupant (1), and Multi-Occupant (2+) scenarios.
3. **Tactical Room Zone Localization:** Coarse 2D spatial mapping across functional room zones (e.g., Doorway/Breach, Center, Far Sector).
4. **Independent Safety:** Operates completely separate from `wimotion` (v1.0), preserving existing code, golden replays, and tests intact.
