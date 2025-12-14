#!/usr/bin/env python3
"""
RL Agent Training Script
Trains DDQN agent using simulated environment
NO EXTERNAL DATASET NEEDED - Generates its own data!
"""

import torch
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import sys
import os
from datetime import datetime
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.rl_agent.ddqn_agent import DDQNAgent
from src.environment.network_env import NetworkEnvironment


class RLTrainer:
    """Handles RL agent training"""
    
    def __init__(self, config_path):
        self.config_path = config_path
        
        # Create environment
        print("Creating simulated network environment...")
        self.env = NetworkEnvironment()
        
        # Create agent
        print("Initializing DDQN agent...")
        self.agent = DDQNAgent(config_path=config_path)
        
        # Training metrics
        self.episode_rewards = []
        self.episode_lengths = []
        self.losses = []
        self.epsilon_values = []
        
        # Best model tracking
        self.best_reward = -float('inf')
        self.best_episode = 0
        
        print("=" * 60)
        print("Trainer initialized successfully")
        print(f"State dim: {self.env.state_dim}")
        print(f"Action dim: {self.env.action_dim}")
        print(f"Device: {self.agent.device}")
        print("=" * 60)
    
    def train(self, num_episodes=1000, save_dir='data/models', log_dir='data/training_logs'):
        """Main training loop"""
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)
        
        print(f"\nStarting training for {num_episodes} episodes...")
        print("=" * 60)
        
        # Progress bar
        pbar = tqdm(range(1, num_episodes + 1), desc="Training")
        
        for episode in pbar:
            episode_reward, episode_loss, steps = self._train_episode()
            
            # Store metrics
            self.episode_rewards.append(episode_reward)
            self.episode_lengths.append(steps)
            if episode_loss:
                self.losses.append(np.mean(episode_loss))
            self.epsilon_values.append(self.agent.epsilon)
            
            # Update progress bar
            avg_reward = np.mean(self.episode_rewards[-10:]) if len(self.episode_rewards) >= 10 else episode_reward
            pbar.set_postfix({
                'reward': f'{episode_reward:.2f}',
                'avg_reward': f'{avg_reward:.2f}',
                'epsilon': f'{self.agent.epsilon:.3f}',
                'best': f'{self.best_reward:.2f}'
            })
            
            # Periodic logging
            if episode % 10 == 0:
                self._log_progress(episode, num_episodes)
            
            # Save best model
            if episode_reward > self.best_reward:
                self.best_reward = episode_reward
                self.best_episode = episode
                model_path = os.path.join(save_dir, 'ddqn_best.pth')
                self.agent.save_model(model_path)
                print(f"\n✓ New best model! Episode {episode}, Reward: {self.best_reward:.2f}")
            
            # Periodic checkpoint
            if episode % 100 == 0:
                checkpoint_path = os.path.join(save_dir, f'ddqn_ep{episode}.pth')
                self.agent.save_model(checkpoint_path)
                print(f"\n✓ Checkpoint saved: Episode {episode}")
            
            # Decay epsilon
            self.agent.decay_epsilon()
        
        print("\n" + "=" * 60)
        print("Training completed!")
        print(f"Best reward: {self.best_reward:.2f} (Episode {self.best_episode})")
        print("=" * 60)
        
        # Save final plots
        self._save_training_plots(log_dir)
        self._save_training_log(log_dir)
        
        return self.agent
    
    def _train_episode(self):
        """Train one episode"""
        state = self.env.reset()
        episode_reward = 0.0
        episode_loss = []
        steps = 0
        
        for step in range(self.env.max_steps):
            # Select action
            action = self.agent.select_action(state)
            
            # Execute action
            next_state, reward, done = self.env.step(action)
            
            # Store experience
            self.agent.store_experience(state, action, reward, next_state, done)
            
            # Train on batch
            if len(self.agent.memory) >= self.agent.batch_size:
                loss = self.agent.train_step()
                if loss is not None:
                    episode_loss.append(loss)
            
            # Update target network periodically
            if self.agent.steps % self.agent.target_update_freq == 0:
                self.agent.update_target_network()
            
            episode_reward += reward
            state = next_state
            steps += 1
            self.agent.steps += 1
            
            if done:
                break
        
        return episode_reward, episode_loss, steps
    
    def _log_progress(self, episode, total_episodes):
        """Log training progress"""
        avg_reward_10 = np.mean(self.episode_rewards[-10:])
        avg_reward_100 = np.mean(self.episode_rewards[-100:]) if len(self.episode_rewards) >= 100 else avg_reward_10
        avg_loss = np.mean(self.losses[-10:]) if self.losses else 0
        
        progress = (episode / total_episodes) * 100
        
        print(f"\n[Ep {episode}/{total_episodes}] "
              f"Progress: {progress:.1f}% | "
              f"Reward(10): {avg_reward_10:.2f} | "
              f"Reward(100): {avg_reward_100:.2f} | "
              f"Loss: {avg_loss:.4f} | "
              f"Epsilon: {self.agent.epsilon:.3f}")
    
    def _save_training_plots(self, log_dir):
        """Save training visualization"""
        print("\nGenerating training plots...")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Rewards plot
        ax1.plot(self.episode_rewards, alpha=0.3, color='blue', label='Episode Reward')
        if len(self.episode_rewards) >= 50:
            window = 50
            moving_avg = np.convolve(self.episode_rewards, np.ones(window)/window, mode='valid')
            ax1.plot(range(window-1, len(self.episode_rewards)), moving_avg, 
                    color='red', linewidth=2, label=f'Moving Avg ({window})')
        ax1.axhline(y=self.best_reward, color='green', linestyle='--', label='Best')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Total Reward')
        ax1.set_title('Training Rewards')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Loss plot
        if self.losses:
            ax2.plot(self.losses, alpha=0.6, color='orange')
            if len(self.losses) >= 50:
                window = 50
                loss_avg = np.convolve(self.losses, np.ones(window)/window, mode='valid')
                ax2.plot(range(window-1, len(self.losses)), loss_avg, 
                        color='red', linewidth=2, label='Moving Avg')
            ax2.set_xlabel('Training Step')
            ax2.set_ylabel('Loss')
            ax2.set_title('Training Loss')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        # Episode length plot
        ax3.plot(self.episode_lengths, alpha=0.5, color='purple')
        if len(self.episode_lengths) >= 50:
            window = 50
            length_avg = np.convolve(self.episode_lengths, np.ones(window)/window, mode='valid')
            ax3.plot(range(window-1, len(self.episode_lengths)), length_avg, 
                    color='red', linewidth=2, label='Moving Avg')
        ax3.set_xlabel('Episode')
        ax3.set_ylabel('Steps')
        ax3.set_title('Episode Length')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Epsilon decay plot
        ax4.plot(self.epsilon_values, color='green')
        ax4.set_xlabel('Episode')
        ax4.set_ylabel('Epsilon')
        ax4.set_title('Exploration Rate (Epsilon Decay)')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plot_path = os.path.join(log_dir, 'training_curve.png')
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Training plot saved: {plot_path}")
    
    def _save_training_log(self, log_dir):
        """Save training log as text"""
        log_path = os.path.join(log_dir, 'training_log.txt')
        
        with open(log_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("RL-QoS System - Training Log\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Episodes: {len(self.episode_rewards)}\n")
            f.write(f"Best Reward: {self.best_reward:.2f} (Episode {self.best_episode})\n")
            f.write(f"Average Reward (last 100): {np.mean(self.episode_rewards[-100:]):.2f}\n")
            f.write(f"Final Epsilon: {self.agent.epsilon:.4f}\n\n")
            
            f.write("Configuration:\n")
            f.write(f"  State Dim: {self.env.state_dim}\n")
            f.write(f"  Action Dim: {self.env.action_dim}\n")
            f.write(f"  Batch Size: {self.agent.batch_size}\n")
            f.write(f"  Gamma: {self.agent.gamma}\n")
            f.write(f"  Learning Rate: {self.agent.optimizer.param_groups[0]['lr']}\n")
            f.write(f"  Memory Size: {self.agent.config['training']['memory_size']}\n")
            f.write(f"  Device: {self.agent.device}\n\n")
            
            f.write("=" * 60 + "\n")
        
        print(f"✓ Training log saved: {log_path}")


def main():
    """Main training function"""
    print("\n" + "=" * 60)
    print("RL-QoS System - Agent Training")
    print("=" * 60 + "\n")
    
    # Paths
    config_path = 'config/rl_config.yaml'
    
    # Check if config exists
    if not os.path.exists(config_path):
        print(f"ERROR: Configuration file not found: {config_path}")
        print("Please ensure you're running from the project root directory")
        return
    
    # Create trainer
    trainer = RLTrainer(config_path)
    
    # Train
    try:
        trained_agent = trainer.train(
            num_episodes=1000,
            save_dir='data/models',
            log_dir='data/training_logs'
        )
        
        print("\n" + "=" * 60)
        print("✓ Training completed successfully!")
        print("=" * 60)
        print("\nGenerated files:")
        print("  - data/models/ddqn_best.pth       (Best model)")
        print("  - data/training_logs/training_curve.png  (Visualization)")
        print("  - data/training_logs/training_log.txt    (Training log)")
        print("\nNext steps:")
        print("  1. Start Mininet network (Linux only)")
        print("  2. Start Ryu controller with trained model")
        print("  3. Run demo to see RL in action!")
        print("=" * 60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user")
        print("Partial results saved")
    except Exception as e:
        print(f"\n\nERROR during training: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
