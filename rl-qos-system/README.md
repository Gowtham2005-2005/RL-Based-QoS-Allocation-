# RL-Based QoS System - Complete Linux Implementation

**Production-Grade SDN System with RL for Research Demonstration**

---

## 🎯 For Linux Deployment

This is a **complete, production-ready** implementation of an RL-based QoS allocation system using:
- **Ryu SDN Controller** with integrated RL
- **Mininet** network emulation
- **Open vSwitch** with QoS queues
- **Real-time GUI** visualizations
- **Professional demonstration** setup

---

## 🚀 Quick Start (Linux)

### Installation
```bash
bash install_linux.sh
```

### Train RL Agent
```bash
python3 src/training/train.py
```

### Run Demonstration
```bash
sudo bash scripts/launch_demo.sh
```

This opens **6 terminal windows**:
1. Mininet network (CLI)
2. Ryu controller (RL decisions)
3. Live bandwidth monitor (graphs)
4. iperf server
5. iperf client
6. Traffic generator

---

## 📖 Documentation

- **[LINUX_DEPLOYMENT.md](LINUX_DEPLOYMENT.md)** - Complete deployment guide
- **[QUICKSTART.md](QUICKSTART.md)** - Windows training guide
- **Code comments** - All files documented

---

## 🎬 What Professors Will See

### **Real Network Components:**
✅ Mininet with 4 hosts, 1 OVS switch  
✅ Ryu SDN controller with OpenFlow 1.3  
✅ QoS queues (3 per port: High, Normal, Low)  
✅ RL agent making decisions every 2 seconds  

### **Live Visualizations:**
✅ Real-time bandwidth graphs (matplotlib)  
✅ iperf showing actual throughput changes  
✅ OpenFlow flow rules visible  
✅ Network topology  

### **RL in Action:**
✅ State: [bandwidth, latency, packet loss, time]  
✅ Action: [Work Priority, Balanced, Entertainment]  
✅ Decisions logged and visualized  
✅ QoS enforcement visible in iperf  

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────┐
│          Application Layer               │
│  ┌────────────────────────────────────┐ │
│  │   RL Agent (DDQN)                  │ │
│  │   - Loads trained model            │ │
│  │   - Makes decisions every 2s       │ │
│  └────────────────────────────────────┘ │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Control Plane                    │
│  ┌────────────────────────────────────┐ │
│  │   Ryu SDN Controller               │ │
│  │   - OpenFlow 1.3                   │ │
│  │   - Stats collection               │ │
│  │   - Flow management                │ │
│  └────────────────────────────────────┘ │
└─────────────────┬───────────────────────┘
                  │ OpenFlow Protocol
┌─────────────────▼───────────────────────┐
│          Data Plane                      │
│  ┌────────────────────────────────────┐ │
│  │   Open vSwitch (s1)                │ │
│  │   - QoS queues configured          │ │
│  │   - Flow table                     │ │
│  │   - Port statistics                │ │
│  └────────────────────────────────────┘ │
│         ▲       ▲       ▲       ▲       │
│         │       │       │       │       │
│  ┌──────┴─┐ ┌──┴───┐ ┌─┴────┐ ┌┴─────┐│
│  │ h1     │ │ h2   │ │ h3   │ │ h4   ││
│  │ Work   │ │ Work │ │ Ent. │ │ Ent. ││
│  └────────┘ └──────┘ └──────┘ └──────┘│
└─────────────────────────────────────────┘
```

---

## 🔬 Technical Details

### **RL Implementation**
- **Algorithm:** Double DQN (DDQN)
- **State space:** 8D continuous
- **Action space:** 3 discrete actions
- **Training:** 1000 episodes (~200K steps)
- **Framework:** PyTorch

### **SDN Implementation**  
- **Controller:** Ryu (Python-based)
- **Protocol:** OpenFlow 1.3
- **Switch:** Open vSwitch (OVS)
- **QoS:** Linux HTB queues

### **Network Setup**
- **Emulator:** Mininet
- **Topology:** Single switch, 4 hosts
- **Bandwidth:** 100 Mbps links
- **Queues:** 3-level priority (700/500/300 Mbps min)

---

## 📊 Demo Checklist

**Before Starting:**
- [ ] Linux system ready (Ubuntu 20.04+)
- [ ] Dependencies installed
- [ ] RL agent trained (model exists)
- [ ] Tested once successfully

**During Demo:**
- [ ] 6 windows visible
- [ ] Ryu showing RL decisions
- [ ] Graph updating in real-time
- [ ] iperf bandwidth changing
- [ ] Clear explanations prepared

---

## 🎓 Research Contributions

1. **RL-based dynamic QoS** - First implementation with DDQN
2. **Self-supervised learning** - No manual dataset
3. **Real-time adaptation** - 2-second decision cycle
4. **Production deployment** - Actual SDN components
5. **Time-aware policies** - Learns temporal patterns

---

## 📁 Key Files

```
rl-qos-system/
├── src/controller/ryu_controller.py     ⭐ Ryu + RL integration
├── src/rl_agent/ddqn_agent.py          ⭐ DDQN implementation
├── scripts/mininet_topology.py         ⭐ Network setup
├── scripts/launch_demo.sh              ⭐ Multi-window launcher
├── LINUX_DEPLOYMENT.md                 ⭐ Deployment guide
└── data/models/ddqn_best.pth          (created after training)
```

---

## ❓ Common Questions

**Q: Why Linux?**  
A: Mininet and OVS are Linux-only. For real network deployment, we need actual SDN components.

**Q: Can I train on Windows?**  
A: Yes! See QUICKSTART.md. Train on Windows, then deploy model on Linux.

**Q: How long is the demo?**  
A: 10-15 minutes total. Setup takes ~3 minutes, demonstration ~7 minutes, Q&A ~5 minutes.

**Q: What if something breaks?**  
A: Run `sudo bash scripts/cleanup.sh` and restart. Always have screenshots/video backup.

---

## 🚀 Start Command

```bash
# Train first (30-60 min):
python3 src/training/train.py

# Then demonstrate:
sudo bash scripts/launch_demo.sh
```

**Read LINUX_DEPLOYMENT.md for complete demonstration script!**

---

**Ready for your research presentation! 🎓✨**
