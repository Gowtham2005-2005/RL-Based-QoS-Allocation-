#!/bin/bash
# Cleanup Script - Stops all processes and cleans up

echo "============================================================"
echo "Cleaning up RL-QoS System"
echo "============================================================"

# Kill all xterm windows
echo "Closing GUI windows..."
pkill -9 xterm 2>/dev/null

# Stop Ryu controller
echo "Stopping Ryu controller..."
pkill -9 -f ryu-manager 2>/dev/null

# Stop Mininet
echo "Stopping Mininet..."
sudo mn -c > /dev/null 2>&1

# Stop any iperf processes
echo "Stopping iperf..."
pkill -9 iperf 2>/dev/null

# Stop traffic generator
pkill -9 -f traffic_generator 2>/dev/null

# Clean OVS
echo "Cleaning Open vSwitch..."
sudo ovs-vsctl del-br s1 2>/dev/null
sudo ovs-vsctl del-qos s1-eth1 2>/dev/null
sudo ovs-vsctl del-qos s1-eth2 2>/dev/null
sudo ovs-vsctl del-qos s1-eth3 2>/dev/null
sudo ovs-vsctl del-qos s1-eth4 2>/dev/null

echo ""
echo "============================================================"
echo "Cleanup complete!"
echo "============================================================"
echo ""
echo "All processes stopped. You can restart with:"
echo "  sudo bash scripts/launch_demo.sh"
echo ""
