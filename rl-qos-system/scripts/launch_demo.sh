#!/bin/bash
# Multi-Terminal Demo Launcher for Linux
# Opens all monitoring windows in separate terminals

echo "============================================================"
echo "RL-QoS System - Multi-Terminal Demo Launcher"
echo "============================================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: This script must be run as root (sudo)"
    exit 1
fi

# Check dependencies
echo "Checking dependencies..."
command -v xterm >/dev/null 2>&1 || { echo "ERROR: xterm not found. Install: sudo apt install xterm"; exit 1; }
command -v mn >/dev/null 2>&1 || { echo "ERROR: mininet not found. Install: sudo apt install mininet"; exit 1; }
command -v ryu-manager >/dev/null 2>&1 || { echo "ERROR: ryu not found. Install: pip install ryu"; exit 1; }

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "Project directory: $PROJECT_DIR"
echo ""

# Clean any previous Mininet
echo "Cleaning previous Mininet instances..."
mn -c > /dev/null 2>&1

# Kill any previous controller
pkill -9 -f ryu-manager 2>/dev/null

echo ""
echo "============================================================"
echo "Starting demonstration in 3 seconds..."
echo "============================================================"
echo ""
echo "Windows that will open:"
echo "  1. Mininet Network (CLI)"
echo "  2. Ryu Controller (RL decisions)"
echo "  3. Live Bandwidth Monitor (matplotlib)"
echo "  4. iperf Server (h1)"
echo "  5. iperf Client (h3)"
echo "  6. Traffic Generator"
echo ""
echo "Press Ctrl+C now to cancel, or wait..."
sleep 3

echo "Starting windows..."

# Terminal 1: Mininet Network
echo "Opening: Mininet Network..."
xterm -T "Mininet Network" -geometry 100x30+0+0 -bg black -fg green -e "
    cd '$PROJECT_DIR'
    echo '========================================='
    echo 'Mininet Network'
    echo '========================================='
    echo ''
    sudo python3 scripts/mininet_topology.py
" &
MININET_PID=$!

# Wait for Mininet to start
sleep 5

# Terminal 2: Ryu Controller with RL
echo "Opening: Ryu Controller..."
xterm -T "Ryu Controller + RL Agent" -geometry 100x35+950+0 -bg black -fg cyan -e "
    cd '$PROJECT_DIR'
    echo '========================================='
    echo 'Ryu SDN Controller with RL Agent'
    echo '========================================='
    echo ''
    echo 'Watch for RL decisions every 2 seconds!'
    echo ''
    sleep 2
    sudo PYTHONPATH='$PROJECT_DIR' ryu-manager --verbose src/controller/ryu_controller.py
" &
RYU_PID=$!

# Wait for controller to connect
sleep 5

# Terminal 3: Live Bandwidth Monitor
echo "Opening: Live Bandwidth Monitor..."
xterm -T "Live Bandwidth Monitor" -geometry 120x40+0+600 -bg white -fg black -e "
    cd '$PROJECT_DIR'
    echo '========================================='
    echo 'Live Bandwidth Monitor'
    echo '========================================='
    echo ''
    echo 'Starting real-time visualization...'
    echo 'Close window to stop monitoring'
    echo ''
    sleep 2
    python3 src/monitoring/live_plotter.py
" &
PLOTTER_PID=$!

# Terminal 4: iperf Server
echo "Opening: iperf Server..."
xterm -T "iperf Server (h1)" -geometry 80x20+950+650 -bg black -fg yellow -e "
    echo '========================================='
    echo 'iperf Server on h1 (Work Host)'
    echo '========================================='
    echo ''
    echo 'Waiting for Mininet...'
    sleep 8
    sudo mn -c > /dev/null 2>&1
    echo 'Starting iperf server...'
    echo ''
    # This won't work until Mininet is running, so we use a different approach
    tail -f /dev/null
" &

# Terminal 5: iperf Client  
echo "Opening: iperf Client..."
xterm -T "iperf Client (h3)" -geometry 80x20+1350+650 -bg black -fg magenta -e "
    echo '========================================='
    echo 'iperf Client on h3 (Entertainment)'
    echo '========================================='
    echo ''
    echo 'Instructions:'
    echo '  In Mininet terminal, run:'
    echo '    h1 iperf -s &'
    echo '    h3 iperf -c 10.0.0.1 -t 60 -i 1'
    echo ''
    echo 'Watch bandwidth change as RL adjusts QoS!'
    echo ''
    tail -f /dev/null
" &

# Terminal 6: Traffic Generator
echo "Opening: Traffic Generator..."
xterm -T "Traffic Generator" -geometry 80x15+1750+650 -bg black -fg white -e "
    cd '$PROJECT_DIR'
    echo '========================================='
    echo 'Traffic Generator'
    echo '========================================='
    echo ''
    echo 'Generating synthetic traffic patterns...'
    echo ''
    sleep 10
    bash scripts/traffic_generator.sh
" &

echo ""
echo "============================================================"
echo "All windows opened!"
echo "============================================================"
echo ""
echo "What's running:"
echo "  ✓ Mininet network (4 hosts, 1 switch)"
echo "  ✓ Ryu controller with RL agent"
echo "  ✓ Live bandwidth monitor"
echo "  ✓ Traffic generators"
echo ""
echo "In Mininet terminal, try:"
echo "  h1 iperf -s &                    # Start server"
echo "  h3 iperf -c 10.0.0.1 -t 60 -i 1  # Test bandwidth"
echo ""
echo "Watch:"
echo "  - Ryu terminal: RL decisions every 2 seconds"
echo "  - Live monitor: Bandwidth graphs updating"
echo "  - iperf: Bandwidth changing based on RL"
echo ""
echo "To stop everything:"
echo "  1. Close all xterm windows"
echo "  2. Or run: sudo bash scripts/cleanup.sh"
echo ""
echo "============================================================"
echo ""

# Wait for user to press Ctrl+C
trap "echo 'Stopping...'; bash scripts/cleanup.sh; exit 0" INT TERM
wait
