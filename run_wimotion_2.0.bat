@echo off
setlocal
cd /d "%~dp0"
title WiMotion 2.0 — Multi-Link RF Spatial Sensing & Occupancy Engine

:MENU
cls
echo ==============================================================================
echo              WiMotion 2.0 (Wi-CaL Multi-Link Sensing Edition)
echo       Tactical RF Multi-Person Occupancy & Spatial Sector Observatory
echo ==============================================================================
echo.
echo   [1] Run Multi-Link Unit Tests (test_spatial.py)
echo   [2] Run Synthetic 3-Stage Replay (0 -> 1 -> 2 Persons Simulation)
echo   [3] Hardware Diagnostics & Auto-Discovery (Scans COM ports & TX MACs)
echo   [4] Start Live Multi-Person HUD Server (FastAPI @ http://127.0.0.1:8000)
echo   [5] Record Multi-Link Training Dataset Session
echo   [6] ESP32 Firmware Management (Clone & Flash Boards)
echo   [7] Exit
echo.
echo ==============================================================================
set /p opt="Select an option [1-7]: "

if "%opt%"=="1" goto TESTS
if "%opt%"=="2" goto REPLAY
if "%opt%"=="3" goto DIAG
if "%opt%"=="4" goto SERVER
if "%opt%"=="5" goto RECORD
if "%opt%"=="6" goto FLASH
if "%opt%"=="7" goto EXIT
goto MENU

:TESTS
echo.
echo [*] Running Multi-Link Unit Tests...
py -3.10 -m unittest discover -s tests -v
pause
goto MENU

:REPLAY
echo.
echo [*] Starting Synthetic 3-Stage Replay...
py -3.10 -m spatial.replay
pause
goto MENU

:DIAG
echo.
echo [*] Scanning COM Ports and Transmitter MAC Addresses...
py -3.10 scripts/0_check_multilink_hardware.py
pause
goto MENU

:SERVER
echo.
echo [*] Enabling Live Hardware Serial Engine...
set WIMOTION_ENABLE_SERIAL=1
echo [*] Starting WiMotion 2.0 HUD Server...
echo [*] Opening Dashboard in browser: http://127.0.0.1:8000
start http://127.0.0.1:8000
py -3.10 -m uvicorn spatial.server:app --host 127.0.0.1 --port 8000
pause
goto MENU

:RECORD
echo.
set /p sess="Enter Session Name (e.g. session_001): "
set /p z="Enter Zone (Z1, Z2, Z3, Z4, CLEAR): "
set /p cnt="Enter Person Count (0, 1, 2): "
set /p dur="Enter Duration in seconds (e.g. 20): "
py -3.10 scripts/record_multilink_dataset.py --session %sess% --zone %z% --count %cnt% --duration %dur%
pause
goto MENU

:FLASH
echo.
echo [*] Launching ESP32 Firmware Management and Flashing Utility...
py -3.10 scripts/flash_tool.py
pause
goto MENU

:EXIT
exit /b 0
