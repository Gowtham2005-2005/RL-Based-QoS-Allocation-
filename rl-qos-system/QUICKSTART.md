# 🚀 QUICK START - Windows

**Get your RL-QoS system running in 10 minutes!**

## ✅ What You'll Do

1. ✓ Install Python packages (2 minutes)
2. ✓ Test the system works (1 minute)
3. ✓ Train the RL agent (30-60 minutes) ← *Go have coffee!*
4. ✓ See the results (5 minutes)

---

## Step 1️⃣: Install Dependencies

Open **PowerShell** or **Command Prompt** in the project folder:

```powershell
cd "d:\final year project\rl-qos-system"
pip install torch numpy pandas matplotlib pyyaml tqdm
```

**Wait 2-3 minutes** for installation to complete.

---

## Step 2️⃣: Quick Test

Verify everything works:

```powershell
python test_system.py
```

✅ You should see:
```
✓ Python version OK
✓ PyTorch installed
✓ Agent imports successfully
✓ Environment works
✓ Training script ready
All systems ready!
```

---

## Step 3️⃣: Start Training

### Option A: Interactive Menu (Recommended)

```powershell
python demo_windows.py
```

Press `1` and hit Enter to start training.

### Option B: Direct Training

```powershell
python src/training/train.py
```

**What you'll see:**
```
Training: 100%|████████| 1000/1000 [30:00<00:00, reward=156.78, best=201.34]
✓ New best model saved!
Training complete!
```

**Time:** 30-60 minutes (be patient!)

**During training:**
- Go get coffee ☕
- Read a paper 📄
- The model is learning!

---

## Step 4️⃣: Test Your Trained Agent

```powershell
python demo_windows.py
```

Press `2` to test the trained agent.

**What you'll see:**
```
Episode 1 ---
  Step 1: Hour=14:00 | Work=65.3 Mbps | Ent=28.7 Mbps | Action=Work Priority
  Step 2: Hour=15:00 | Work=72.1 Mbps | Ent=22.3 Mbps | Action=Work Priority
...
```

The agent is making intelligent decisions! ✨

---

## Step 5️⃣: See Live Monitoring

```powershell
python demo_windows.py
```

Press `4` for live monitoring demo.

A **window will pop up** showing:
- Blue line = Work bandwidth
- Red line = Entertainment bandwidth
- Bottom = RL decisions changing

**Close the window** when done.

---

## 📊 What Gets Created

After training, you'll have:

```
data/
├── models/
│   └── ddqn_best.pth           ← Your trained AI model!
│
├── training_logs/
│   ├── training_curve.png      ← Learning graph
│   └── training_log.txt        ← Training summary
│
└── network_traces/
    └── live_metrics.csv        ← Test data
```

---

## 🎯 For Your Demonstration

### What to Show:

1. **Training Plot** (`data/training_logs/training_curve.png`)
   - Shows AI is learning
   - Reward goes up over time

2. **Test Run** (Option 2 in demo)
   - Shows agent making smart decisions
   - Different policies for different times

3. **Live Monitor** (Option 4 in demo)
   - Real-time visualization
   - Looks impressive! 🎉

---

## ❓ Quick Troubleshooting

### "No module named 'torch'"
```powershell
pip install torch
```

### "Model file not found"
**You need to train first!** Run Option 1 in demo.

### Training is slow
**Normal!** It takes 30-60 minutes. Go do something else.

### Error during training
Press `Ctrl+C` to stop, then:
```powershell
python test_system.py
```
Check what's wrong.

---

## 🎓 Understanding What Happened

### Training Phase:
1. **Created simulated network** (no real network needed)
2. **RL agent tried 200,000 actions** (1000 episodes × 200 steps)
3. **Learned optimal policies** from rewards/penalties
4. **Saved best model** to `ddqn_best.pth`

### Testing Phase:
1. **Loaded trained model** from file
2. **Applied to test scenarios** 
3. **Made intelligent decisions** based on learned knowledge

### The Magic:
- **No manual dataset required!** ✓
- **Agent teaches itself!** ✓
- **Gets smarter over time!** ✓

---

## 📝 For Your Report/Paper

### Key Points:
- ✅ Implemented Double DQN (state-of-the-art RL)
- ✅ Self-supervised learning (generates own data)
- ✅ Real-time decision making (2-second intervals)
- ✅ Time-aware policies (different for work hours vs evening)
- ✅ Complete working prototype

### Screenshots to Include:
1. Training curve showing learning
2. Test output showing decisions
3. Live monitoring graph
4. Code architecture diagram

---

## 🚀 Next Steps

**For Research:**
- ✅ You can demo this immediately
- ✅ Take screenshots of results
- ✅ Show training curve in presentation
- ✅ Demonstrate real-time decisions

**For Linux Deployment:**
- Would need Mininet (network emulator)
- Would need Ryu controller
- Would run on actual virtual network
- **But Windows version proves the concept!**

---

## 💡 Tips

1. **Training once is enough** - The model file can be reused
2. **Save your results** - Copy `data/` folder as backup
3. **Test multiple times** - Run Option 2 several times
4. **Take screenshots** - During training and testing

---

## ✅ Success Checklist

- [ ] Dependencies installed (`pip install ...`)
- [ ] System test passed (`python test_system.py`)
- [ ] Training completed (30-60 min)
- [ ] Model file exists (`data/models/ddqn_best.pth`)
- [ ] Agent tested (Option 2 works)
- [ ] Live monitor runs (Option 4 shows graphs)
- [ ] Screenshots taken for report

---

**Ready? Start here:**

```powershell
python demo_windows.py
```

**Press 1 to begin training!** 🚀
