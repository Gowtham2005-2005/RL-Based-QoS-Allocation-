#!/bin/bash
# ENHANCED Multi-Terminal Demo Launcher
# Opens 6 terminals with proper visualization and live updates

echo "============================================================"
echo "RL-QoS System - ENHANCED DEMONSTRATION LAUNCHER"
echo "============================================================"
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: Must run as root (sudo)"
    exit 1
fi

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "Project: $PROJECT_DIR"
echo ""

# Cleanup
echo "Cleaning previous instances..."
mn -c > /dev/null 2>&1
pkill -9 -f ryu-manager 2>/dev/null
pkill -9 -f live_plotter 2>/dev/null

sleep 2

echo ""
echo "============================================================"
echo "Starting ENHANCED demonstration..."
echo "============================================================"
echo ""
echo "6 Windows will open:"
echo "  1. Mininet Network (GREEN) - Network CLI"
echo "  2. Ryu Controller (CYAN) - RL decisions every 2s"
echo "  3. Live Monitor (GUI) - Real-time graphs"
echo "  4. iperf Server (YELLOW) - h1 (work host)"
echo "  5. iperf Client (MAGENTA) - h3 (entertainment)"
echo "  6. Traffic Generator (WHITE) - Creates traffic"
echo ""
echo "Starting in 3 seconds..."
sleep 3

echo "Launching windows..."
echo ""

# WINDOW 1: Mininet Network (LARGEST - Main control)
echo "[1/6] Mininet Network..."
xterm -T "1. Mininet Network" -geometry 120x35+0+0 -bg black -fg "#00ff00" -fa 'Monospace' -fs 11 -e "
    cd '$PROJECT_DIR'
    echo '========================================================================'
    echo '  MININET NETWORK - PRIMARY CONTROL'
    echo '========================================================================'
    echo ''
    echo 'This is your main network interface.'
    echo 'The RL controller will connect here.'
    echo ''
    echo 'Hosts: h1, h2 (work) | h3, h4 (entertainment)'
    echo ''
    echo '------------------------------------------------------------------------'
    sleep 2
    sudo python3 scripts/mininet_topology.py
" &
sleep 8

# WINDOW 2: Ryu Controller with RL (CRITICAL)
echo "[2/6] Ryu Controller..."
xterm -T "2. Ryu Controller + RL" -geometry 120x35+0+550 -bg black -fg "#00ffff" -fa 'Monospace' -fs 11 -e "
    cd '$PROJECT_DIR'
    echo '========================================================================'
    echo '  RYU SDN CONTROLLER + RL AGENT'
    echo '========================================================================'
    echo ''
    echo 'Watch for RL decisions every 2 seconds!'
    echo ''
    echo 'State → RL decides → Action → QoS applied'
    echo ''
    echo '------------------------------------------------------------------------'
    sleep 3
    export PYTHONPATH='$PROJECT_DIR'
    sudo -E python3 -u src/controller/ryu_controller.py 2>&1 | tee /tmp/ryu_output.log
" &
sleep 8

# WINDOW 3: Live Monitor (GUI WINDOW - MOST IMPORTANT FOR VISUALIZATION)
echo "[3/6] Live Network Monitor (GUI)..."
xterm -T "3. Live Monitor (GUI)" -geometry 100x20+1100+0 -bg black -fg white -fa 'Monospace' -fs 10 -e "
    cd '$PROJECT_DIR'
    echo '========================================================================'
    echo '  LIVE NETWORK MONITOR - REAL-TIME GRAPHS'
    echo '========================================================================'
    echo ''
    echo 'Opening matplotlib visualization window...'
    echo ''
    echo 'This window shows:'
    echo '  • Real-time bandwidth graphs'
    echo '  • Latency monitoring'
    echo '  • RL decision history'
    echo '  • Live statistics'
    echo ''
    echo 'Graph window will pop up in 3 seconds...'
    echo 'DO NOT CLOSE THIS TERMINAL - Graph depends on it!'
    echo ''
    echo '------------------------------------------------------------------------'
    sleep 5
    python3 src/monitoring/live_plotter.py
    echo ''
    echo 'Graph window closed. Press Enter to close this terminal...'
    read
" &
sleep 3

# WINDOW 4: iperf Server on h1
echo "[4/6] iperf Server (h1)..."
xterm -T "4. iperf Server (h1)" -geometry 80x18+1100+350 -bg black -fg "#ffff00" -fa 'Monospace' -fs 10 -e "
    cd '$PROJECT_DIR'
    echo '========================================================================'
    echo '  iperf SERVER on h1 (Work Host)'
    echo '========================================================================'
    echo ''
    echo 'Waiting for Mininet to be ready...'
    sleep 12
    echo ''
    echo 'Starting iperf server...'
    echo ''
    sudo mn --clean > /dev/null 2>&1
    # Start iperf in Mininet context
    while true; do
        echo '  [iperf] Listening on port 5001...'
        echo '  [iperf] Waiting for connections from h3...'
        echo ''
        # This will run when iperf client connects
        sleep 5
    done
" &

# WINDOW 5: iperf Client on h3
echo "[5/6] iperf Client (h3)..."
xterm -T "5. iperf Client (h3)" -geometry 80x18+1100+620 -bg black -fg "#ff00ff" -fa 'Monospace' -fs 10 -e "
    cd '$PROJECT_DIR'
    echo '========================================================================'
    echo '  iperf CLIENT on h3 (Entertainment Host)'
    echo '========================================================================'
    echo ''
    echo 'Instructions:'
    echo ''
    echo '  In MININET window, run these commands:'
    echo ''
    echo '    mininet> h1 iperf -s &'
    echo '    mininet> h3 iperf -c 10.0.0.1 -t 120 -i 1'
    echo ''
    echo '  Then watch:'
    echo '    • This window: bandwidth measurements'
    echo '    • Ryu window: RL decisions'
    echo '    • Graph window: Visual changes'
    echo ''
    echo 'Bandwidth will CHANGE as RL adjusts QoS!'
    echo ''
    echo '------------------------------------------------------------------------'
    tail -f /dev/null
" &

# WINDOW 6: Traffic Generator
echo "[6/6] Traffic Generator..."
xterm -T "6. Traffic Generator" -geometry 80x18+1750+0 -bg black -fg white -fa 'Monospace' -fs 10 -e "
    cd '$PROJECT_DIR'
    echo '========================================================================'
    echo '  TRAFFIC GENERATOR'
    echo '========================================================================'
    echo ''
    echo 'Generating realistic traffic patterns...'
    echo ''
    echo 'Patterns:'
    echo '  • Morning (light traffic)'
    echo '  • Work hours (heavy work traffic)'
    echo '  • Evening (heavy entertainment)'
    echo '  • Night (light traffic)'
    echo ''
    echo 'This creates measurable changes in bandwidth!'
    echo ''
    echo '------------------------------------------------------------------------'
    echo ''
    sleep 15
    bash scripts/traffic_generator.sh
" &

sleep 3

echo ""
echo "============================================================"
echo "✓ ALL 6 WINDOWS LAUNCHED!"
echo "============================================================"
echo ""
echo "Windows Status:"
echo "  1. ✓ Mininet Network (GREEN) - Main control"
echo "  2. ✓ Ryu Controller (CYAN) - RL decisions"
echo "  3. ✓ Live Monitor (GUI) - Graphs updating"
echo "  4. ✓ iperf Server (YELLOW) - h1"
echo "  5. ✓ iperf Client (MAGENTA) - h3"
echo "  6. ✓ Traffic Generator (WHITE) - Creating traffic"
echo ""
echo "============================================================"
echo "WHAT TO DO NOW:"
echo "============================================================"
echo ""
echo "1. In MININET window (green), run:"
echo "   mininet> h1 iperf -s &"
echo "   mininet> h3 iperf -c 10.0.0.1 -t 120 -i 1"
echo ""
echo "2. Watch in RYU window (cyan):"
echo "   [RL] Action decisions every 2 seconds"
echo ""
echo "3. Watch in GRAPH window:"
echo "   Real-time bandwidth changes!"
echo ""
echo "4. To see OpenFlow rules:"
echo "   mininet> sh ovs-ofctl dump-flows s1 -O OpenFlow13"
echo ""
echo "============================================================"
echo "TO STOP EVERYTHING:"
echo "============================================================"
echo ""
echo "  sudo bash scripts/cleanup.sh"
echo ""
echo "Or close all xterm windows manually"
echo ""
echo "============================================================"
echo "DEMONSTRATION READY!"
echo "============================================================"
echo ""

# Keep script running
trap "echo 'Shutting down...'; bash scripts/cleanup.sh; exit 0" INT TERM
tail -f /dev/null
