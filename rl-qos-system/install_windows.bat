@echo off
REM Quick Installation Script for Windows
REM Run this FIRST before anything else

echo ============================================================
echo RL-QoS System - Windows Installation
echo ============================================================
echo.

echo Step 1: Installing Python packages...
echo This may take 2-5 minutes. Please wait...
echo.

pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install numpy pandas matplotlib pyyaml tqdm
pip install loguru seaborn scipy

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Run: python test_system.py
echo   2. Run: python demo_windows.py
echo.
pause
