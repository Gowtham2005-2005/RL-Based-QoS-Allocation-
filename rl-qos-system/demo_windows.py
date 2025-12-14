#!/usr/bin/env python3
"""
Windows Demo Script
Demonstrates RL agent training on Windows (no Mininet needed)
"""

import sys
import os

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.training.train import main as train_main


def demo_training():
    """Run RL training demo"""
    print("\n" + "=" * 70)
    print("RL-QoS System - Windows Training Demo")
    print("=" * 70)
    print("\nThis demo will:")
    print("  1. Create a simulated network environment")
    print("  2. Train a DDQN agent for 1000 episodes (~30-60 minutes)")
    print("  3. Save the trained model to data/models/")
    print("  4. Generate training visualizations")
    print("\nNote: This is TRAINING ONLY. Network deployment requires Linux.")
    print("=" * 70 + "\n")
    
    response = input("Start training? (y/n): ").strip().lower()
    
    if response == 'y':
        print("\nStarting training... (Press Ctrl+C to stop)\n")
        train_main()
    else:
        print("Training cancelled.")


def demo_agent_test():
    """Test trained agent"""
    print("\n" + "=" * 70)
    print("RL-QoS System - Agent Testing")
    print("=" * 70 + "\n")
    
    from src.rl_agent.ddqn_agent import DDQNAgent
    from src.environment.network_env import NetworkEnvironment
    import numpy as np
    
    # Check if model exists
    model_path = 'data/models/ddqn_best.pth'
    if not os.path.exists(model_path):
        print(f"ERROR: Trained model not found at {model_path}")
        print("Please train the model first using option 1")
        return
    
    # Load agent
    print("Loading trained agent...")
    agent = DDQNAgent(config_path='config/rl_config.yaml')
    agent.load_model(model_path)
    
    # Create environment
    env = NetworkEnvironment()
    
    print("\nRunning test episodes...\n")
    
    action_names = ['Work Priority', 'Balanced', 'Entertainment Priority']
    
    # Run 5 test episodes
    for ep in range(5):
        state = env.reset()
        episode_reward = 0
        
        print(f"\n--- Episode {ep + 1} ---")
        
        for step in range(20):  # 20 steps per episode
            # Agent selects action (no exploration)
            action = agent.select_action(state, epsilon=0.0)
            
            # Take step
            next_state, reward, done = env.step(action)
            episode_reward += reward
            
            # Display
            work_bw = state[0] * 100
            ent_bw = state[1] * 100
            hour = int(state[7] * 23)
            
            print(f"  Step {step + 1:2d}: Hour={hour:02d}:00 | "
                  f"Work={work_bw:5.1f} Mbps | Ent={ent_bw:5.1f} Mbps | "
                  f"Action={action_names[action]:20s} | Reward={reward:6.2f}")
            
            state = next_state
            
            if done:
                break
        
        print(f"Episode {ep + 1} Total Reward: {episode_reward:.2f}")
    
    print("\n" + "=" * 70)
    print("Testing complete!")
    print("=" * 70 + "\n")


def demo_visualization():
    """Show training visualization"""
    print("\n" + "=" * 70)
    print("Training Visualization")
    print("=" * 70 + "\n")
    
    plot_path = 'data/training_logs/training_curve.png'
    
    if not os.path.exists(plot_path):
        print(f"ERROR: Training plot not found at {plot_path}")
        print("Please train the model first using option 1")
        return
    
    print(f"Opening training plot: {plot_path}")
    
    # Open image
    import platform
    if platform.system() == 'Windows':
        os.startfile(plot_path)
    elif platform.system() == 'Darwin':  # macOS
        os.system(f'open "{plot_path}"')
    else:  # Linux
        os.system(f'xdg-open "{plot_path}"')


def demo_live_monitor():
    """Start live monitoring (simulated)"""
    print("\n" + "=" * 70)
    print("Live Monitoring Demo")
    print("=" * 70 + "\n")
    
    print("Starting live bandwidth monitor...")
    print("This will show a real-time plot with simulated data.")
    print("Close the plot window to stop.\n")
    
    # Import and run live plotter
    from src.monitoring.live_plotter import LivePlotter
    from src.monitoring.metrics_logger import MetricsLogger
    import numpy as np
    import time
    import threading
    
    # Create metrics logger
    logger = MetricsLogger()
    logger.clear_log()
    
    # Start data generator thread
    def generate_demo_data():
        """Generate demo metrics data"""
        action = 1
        step = 0
        
        while True:
            # Simulate changing network conditions
            hour = (step // 10) % 24
            
            if 9 <= hour <= 17:  # Work hours
                work_bw = 60 + np.random.randn() * 5
                ent_bw = 35 + np.random.randn() * 5
                action = 0 if step % 20 < 15 else 1
            elif 18 <= hour <= 23:  # Evening
                work_bw = 30 + np.random.randn() * 5
                ent_bw = 65 + np.random.randn() * 5
                action = 2 if step % 20 < 15 else 1
            else:  # Night
                work_bw = 20 + np.random.randn() * 3
                ent_bw = 25 + np.random.randn() * 3
                action = 1
            
            metrics = {
                'work_bw': max(0, work_bw),
                'entertain_bw': max(0, ent_bw),
                'work_lat': 10 + np.random.randn() * 2,
                'entertain_lat': 12 + np.random.randn() * 2,
                'work_loss': max(0, np.random.randn() * 0.01),
                'entertain_loss': max(0, np.random.randn() * 0.01),
                'action': action,
                'action_name': ['work', 'balanced', 'entertainment'][action],
                'reward': 10 + np.random.randn() * 5
            }
            
            logger.log(metrics)
            time.sleep(1)
            step += 1
    
    # Start generator thread
    generator_thread = threading.Thread(target=generate_demo_data, daemon=True)
    generator_thread.start()
    
    # Wait a bit for initial data
    time.sleep(2)
    
    # Start live plotter
    plotter = LivePlotter()
    plotter.run()


def main_menu():
    """Main menu"""
    while True:
        print("\n" + "=" * 70)
        print("RL-QoS System - Windows Demo")
        print("=" * 70)
        print("\nOptions:")
        print("  1. Train RL Agent (30-60 minutes)")
        print("  2. Test Trained Agent")
        print("  3. View Training Visualization")
        print("  4. Live Monitoring Demo (simulated)")
        print("  5. Exit")
        print("\n" + "=" * 70)
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            demo_training()
        elif choice == '2':
            demo_agent_test()
        elif choice == '3':
            demo_visualization()
        elif choice == '4':
            demo_live_monitor()
        elif choice == '5':
            print("\nExiting. Goodbye!")
            break
        else:
            print("\nInvalid option. Please try again.")


if __name__ == '__main__':
    main_menu()
