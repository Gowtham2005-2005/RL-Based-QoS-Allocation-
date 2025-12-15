# DEMONSTRATION QUICK REFERENCE

## 🚀 Start Demo
```bash
sudo bash scripts/launch_demo.sh
```

## 📊 What Opens:
1. **Mininet Network** (Green) - Main control
2. **Ryu Controller** (Cyan) - RL decisions
3. **Live Graphs** (GUI Window) - Real-time visualization
4. **iperf Server** (Yellow) - h1 work host
5. **iperf Client** (Magenta) - h3 entertainment
6. **Traffic Generator** (White) - Creates patterns

## 🎬 In Mininet Window:

### Start Traffic Test:
```
mininet> h1 iperf -s &
mininet> h3 iperf -c 10.0.0.1 -t 120 -i 1
```

### View OpenFlow Rules:
```
mininet> sh ovs-ofctl dump-flows s1 -O OpenFlow13
```

### Check QoS Queues:
```
mininet> sh ovs-vsctl list qos
mininet> sh ovs-vsctl list queue
```

##Manual Control (Override RL):

### Force WORK Priority:
```
mininet> sh ovs-ofctl add-flow s1 -O OpenFlow13 'priority=100,in_port=1,actions=set_queue:0,normal'
mininet> sh ovs-ofctl add-flow s1 -O OpenFlow13 'priority=100,in_port=3,actions=set_queue:2,normal'
```

### Force ENTERTAINMENT Priority:
```
mininet> sh ovs-ofctl add-flow s1 -O OpenFlow13 'priority=100,in_port=1,actions=set_queue:2,normal'
mininet> sh ovs-ofctl add-flow s1 -O OpenFlow13 'priority=100,in_port=3,actions=set_queue:0,normal'
```

### Let RL Take Over:
```
mininet> sh ovs-ofctl del-flows s1
```

## 📈 Watch For:
- **Ryu Window**: [RL] Action: 0/1/2 every 2 seconds
- **Graph Window**: Bandwidth lines changing color/height
- **iperf Window**: Mbps numbers changing

## 🛑 Stop Everything:
```bash
sudo bash scripts/cleanup.sh
```

## 🎓 For Professors:
1. Show RL training curve (data/training_logs/training_curve.png)
2. Run demo (sudo bash scripts/launch_demo.sh)
3. Start iperf test in Mininet
4. Point to:
   - Ryu: RL making decisions
   - Graph: Real-time visualization
   - iperf: Bandwidth actually changing
5. Manually override to show control
6. Let RL take over again
