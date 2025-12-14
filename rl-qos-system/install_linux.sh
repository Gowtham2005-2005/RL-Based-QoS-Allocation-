#!/bin/bash
# Linux Installation Script

echo "============================================================"
echo "RL-QoS System - Linux Installation"
echo "============================================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "Please do NOT run this as root (without sudo)"
    echo "Run: bash install_linux.sh"
    exit 1
fi

echo "This will install:"
echo "  - Python packages (PyTorch, NumPy, Pandas, etc.)"
echo "  - Mininet (network emulator)"
echo "  - Open vSwitch (software switch)"
echo "  - Ryu (SDN controller)"
echo "  - xterm (terminal emulator)"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

echo ""
echo "============================================================"
echo "Step 1: System Packages"
echo "============================================================"

sudo apt update
sudo apt install -y python3 python3-pip git xterm

echo ""
echo "============================================================"
echo "Step 2: Mininet and Open vSwitch"
echo "============================================================"

sudo apt install -y mininet openvswitch-switch

echo ""
echo "============================================================"
echo "Step 3: Python Packages"
echo "============================================================"

pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip3 install numpy pandas matplotlib pyyaml tqdm
pip3 install ryu eventlet

echo ""
echo "============================================================"
echo "Step 4: Create Data Directories"
echo "============================================================"

mkdir -p data/models data/training_logs data/network_traces

echo ""
echo "============================================================"
echo "Step 5: Make Scripts Executable"
echo "============================================================"

chmod +x scripts/*.sh
chmod +x scripts/*.py

echo ""
echo "============================================================"
echo "Installation Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Train the RL agent:"
echo "     python3 src/training/train.py"
echo ""
echo "  2. Start the demonstration:"
echo "     sudo bash scripts/launch_demo.sh"
echo ""
echo "  3. Read the deployment guide:"
echo "     cat LINUX_DEPLOYMENT.md"
echo ""
echo "============================================================"
