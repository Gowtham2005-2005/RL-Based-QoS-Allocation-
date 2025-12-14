#!/bin/bash
# Traffic Generator - Creates realistic network traffic

echo "Traffic Generator Running..."
echo "Generating work and entertainment traffic patterns..."
echo ""

# Wait for Mininet to be ready
sleep 5

while true; do
    # Morning pattern (light traffic)
    echo "[$(date +%H:%M:%S)] Morning pattern - light traffic"
    for i in {1..10}; do
        timeout 1 sudo mn exec h1 ping -c 1 -i 0.2 10.0.0.3 > /dev/null 2>&1 &
        timeout 1 sudo mn exec h3 ping -c 1 -i 0.3 10.0.0.1 > /dev/null 2>&1 &
        sleep 0.5
    done
    
    # Work hours pattern (heavy work traffic)
    echo "[$(date +%H:%M:%S)] Work hours - heavy work traffic"
    for i in {1..15}; do
        timeout 2 sudo mn exec h1 ping -c 2 -i 0.1 10.0.0.3 > /dev/null 2>&1 &
        timeout 2 sudo mn exec h2 ping -c 2 -i 0.1 10.0.0.4 > /dev/null 2>&1 &
        timeout 1 sudo mn exec h3 ping -c 1 -i 0.4 10.0.0.1 > /dev/null 2>&1 &
        sleep 0.5
    done
    
    # Lunch break (balanced)
    echo "[$(date +%H:%M:%S)] Lunch break - balanced traffic"
    for i in {1..10}; do
        timeout 1 sudo mn exec h1 ping -c 1 -i 0.2 10.0.0.3 > /dev/null 2>&1 &
        timeout 1 sudo mn exec h3 ping -c 1 -i 0.2 10.0.0.1 > /dev/null 2>&1 &
        sleep 0.5
    done
    
    # Evening pattern (heavy entertainment)
    echo "[$(date +%H:%M:%S)] Evening - heavy entertainment traffic"
    for i in {1..15}; do
        timeout 2 sudo mn exec h3 ping -c 2 -i 0.1 10.0.0.1 > /dev/null 2>&1 &
        timeout 2 sudo mn exec h4 ping -c 2 -i 0.1 10.0.0.2 > /dev/null 2>&1 &
        timeout 1 sudo mn exec h1 ping -c 1 -i 0.4 10.0.0.3 > /dev/null 2>&1 &
        sleep 0.5
    done
    
    # Night (light traffic)
    echo "[$(date +%H:%M:%S)] Night - light traffic"
    for i in {1..8}; do
        timeout 1 sudo mn exec h1 ping -c 1 -i 0.3 10.0.0.3 > /dev/null 2>&1 &
        timeout 1 sudo mn exec h3 ping -c 1 -i 0.3 10.0.0.1 > /dev/null 2>&1 &
        sleep 0.7
    done
    
    echo "[$(date +%H:%M:%S)] Pattern cycle complete, repeating..."
    echo ""
done
