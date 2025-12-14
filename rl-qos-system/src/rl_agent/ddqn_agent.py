#!/usr/bin/env python3
"""
Complete DDQN Agent Implementation
Double Deep Q-Network for QoS Allocation
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque, namedtuple
import yaml
import os

Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])


class DQNNetwork(nn.Module):
    """Deep Q-Network with improved architecture"""
    
    def __init__(self, state_dim, action_dim, hidden_layers=[128, 128, 64]):
        super(DQNNetwork, self).__init__()
        
        layers = []
        input_dim = state_dim
        
        # Build hidden layers
        for hidden_dim in hidden_layers:
            layers.extend([
                nn.Linear(input_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),  # Batch normalization for stability
                nn.ReLU(),
                nn.Dropout(0.1)  # Prevent overfitting
            ])
            input_dim = hidden_dim
        
        # Output layer
        layers.append(nn.Linear(input_dim, action_dim))
        
        self.network = nn.Sequential(*layers)
        
        # Initialize weights using Xavier initialization
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        """Xavier initialization for better gradient flow"""
        if isinstance(module, nn.Linear):
            nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                nn.init.constant_(module.bias, 0)
    
    def forward(self, state):
        """Forward pass"""
        return self.network(state)


class PrioritizedReplayBuffer:
    """
    Prioritized Experience Replay Buffer
    Samples important experiences more frequently
    """
    
    def __init__(self, capacity, alpha=0.6):
        self.capacity = capacity
        self.alpha = alpha  # Prioritization exponent
        self.buffer = []
        self.priorities = []
        self.pos = 0
    
    def push(self, state, action, reward, next_state, done):
        """Add experience with maximum priority"""
        max_priority = max(self.priorities) if self.priorities else 1.0
        
        experience = Experience(state, action, reward, next_state, done)
        
        if len(self.buffer) < self.capacity:
            self.buffer.append(experience)
            self.priorities.append(max_priority)
        else:
            self.buffer[self.pos] = experience
            self.priorities[self.pos] = max_priority
        
        self.pos = (self.pos + 1) % self.capacity
    
    def sample(self, batch_size, beta=0.4):
        """Sample batch with priority-based probability"""
        if len(self.buffer) == 0:
            return [], [], []
        
        # Calculate sampling probabilities
        priorities = np.array(self.priorities[:len(self.buffer)])
        probs = priorities ** self.alpha
        probs /= probs.sum()
        
        # Sample indices
        indices = np.random.choice(len(self.buffer), batch_size, p=probs, replace=False)
        
        # Calculate importance sampling weights
        total = len(self.buffer)
        weights = (total * probs[indices]) ** (-beta)
        weights /= weights.max()
        
        experiences = [self.buffer[idx] for idx in indices]
        
        return experiences, indices, weights
    
    def update_priorities(self, indices, priorities):
        """Update priorities based on TD errors"""
        for idx, priority in zip(indices, priorities):
            self.priorities[idx] = priority + 1e-5  # Small constant to avoid zero priority
    
    def __len__(self):
        return len(self.buffer)


class SimpleReplayBuffer:
    """Simple uniform replay buffer (fallback)"""
    
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        self.buffer.append(Experience(state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        return random.sample(self.buffer, min(batch_size, len(self.buffer)))
    
    def __len__(self):
        return len(self.buffer)


class DDQNAgent:
    """
    Double DQN Agent with Prioritized Experience Replay
    Handles action selection, training, and model management
    """
    
    def __init__(self, config_path=None, state_dim=8, action_dim=3):
        # Load configuration
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            # Default configuration
            self.config = {
                'agent': {'state_dim': state_dim, 'action_dim': action_dim},
                'network': {'hidden_layers': [128, 128, 64]},
                'training': {
                    'batch_size': 64,
                    'gamma': 0.99,
                    'epsilon_start': 1.0,
                    'epsilon_end': 0.01,
                    'epsilon_decay': 0.995,
                    'learning_rate': 0.0001,
                    'memory_size': 100000,
                    'target_update_freq': 10
                }
            }
        
        agent_config = self.config['agent']
        network_config = self.config['network']
        train_config = self.config['training']
        
        # Network parameters
        self.state_dim = agent_config['state_dim']
        self.action_dim = agent_config['action_dim']
        
        # Training parameters
        self.batch_size = train_config['batch_size']
        self.gamma = train_config['gamma']
        self.epsilon = train_config['epsilon_start']
        self.epsilon_end = train_config['epsilon_end']
        self.epsilon_decay = train_config['epsilon_decay']
        self.target_update_freq = train_config['target_update_freq']
        
        # Device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Networks
        self.policy_net = DQNNetwork(
            self.state_dim,
            self.action_dim,
            network_config['hidden_layers']
        ).to(self.device)
        
        self.target_net = DQNNetwork(
            self.state_dim,
            self.action_dim,
            network_config['hidden_layers']
        ).to(self.device)
        
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        # Optimizer with gradient clipping
        self.optimizer = optim.Adam(
            self.policy_net.parameters(),
            lr=train_config['learning_rate'],
            weight_decay=1e-5  # L2 regularization
        )
        
        # Learning rate scheduler
        self.scheduler = optim.lr_scheduler.StepLR(self.optimizer, step_size=100, gamma=0.9)
        
        # Loss function (Huber loss is more robust than MSE)
        self.criterion = nn.SmoothL1Loss()
        
        # Replay buffer (use simple buffer for compatibility)
        self.memory = SimpleReplayBuffer(train_config['memory_size'])
        
        # Tracking
        self.steps = 0
        self.training_steps = 0
        
        print(f"DDQN Agent initialized: state_dim={self.state_dim}, action_dim={self.action_dim}")
    
    def select_action(self, state, epsilon=None):
        """
        Epsilon-greedy action selection
        
        Args:
            state: Current state (numpy array or list)
            epsilon: Exploration rate (uses self.epsilon if None)
        
        Returns:
            action: Integer action (0, 1, or 2)
        """
        if epsilon is None:
            epsilon = self.epsilon
        
        # Epsilon-greedy exploration
        if random.random() < epsilon:
            return random.randint(0, self.action_dim - 1)
        else:
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                q_values = self.policy_net(state_tensor)
                return q_values.argmax().item()
    
    def store_experience(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        self.memory.push(state, action, reward, next_state, done)
    
    def train_step(self):
        """
        Perform one training step
        
        Returns:
            loss: Training loss (None if not enough samples)
        """
        if len(self.memory) < self.batch_size:
            return None
        
        # Sample batch
        batch = self.memory.sample(self.batch_size)
        
        # Unpack batch
        states = torch.FloatTensor([e.state for e in batch]).to(self.device)
        actions = torch.LongTensor([e.action for e in batch]).to(self.device)
        rewards = torch.FloatTensor([e.reward for e in batch]).to(self.device)
        next_states = torch.FloatTensor([e.next_state for e in batch]).to(self.device)
        dones = torch.FloatTensor([e.done for e in batch]).to(self.device)
        
        # Current Q values
        current_q_values = self.policy_net(states).gather(1, actions.unsqueeze(1))
        
        # Double DQN: use policy net to select actions, target net to evaluate
        with torch.no_grad():
            # Select best actions using policy net
            next_actions = self.policy_net(next_states).argmax(1)
            # Evaluate using target net
            next_q_values = self.target_net(next_states).gather(1, next_actions.unsqueeze(1)).squeeze()
            # Target Q values with terminal state handling
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
        
        # Compute loss
        loss = self.criterion(current_q_values.squeeze(), target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        
        # Gradient clipping for stability
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        
        self.optimizer.step()
        
        self.training_steps += 1
        
        return loss.item()
    
    def update_target_network(self):
        """Copy weights from policy net to target net"""
        self.target_net.load_state_dict(self.policy_net.state_dict())
    
    def decay_epsilon(self):
        """Decay exploration rate"""
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
    
    def save_model(self, path):
        """Save complete model state"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save({
            'policy_net': self.policy_net.state_dict(),
            'target_net': self.target_net.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'steps': self.steps,
            'training_steps': self.training_steps
        }, path)
        print(f"Model saved to {path}")
    
    def load_model(self, path):
        """Load complete model state"""
        if not os.path.exists(path):
            print(f"Model file not found: {path}")
            return False
        
        checkpoint = torch.load(path, map_location=self.device)
        self.policy_net.load_state_dict(checkpoint['policy_net'])
        self.target_net.load_state_dict(checkpoint['target_net'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.epsilon = checkpoint.get('epsilon', 0.0)
        self.steps = checkpoint.get('steps', 0)
        self.training_steps = checkpoint.get('training_steps', 0)
        
        # Set to evaluation mode
        self.policy_net.eval()
        self.target_net.eval()
        
        print(f"Model loaded from {path}")
        print(f"Steps: {self.steps}, Training steps: {self.training_steps}, Epsilon: {self.epsilon}")
        return True
    
    def get_info(self):
        """Get agent information"""
        return {
            'state_dim': self.state_dim,
            'action_dim': self.action_dim,
            'epsilon': self.epsilon,
            'steps': self.steps,
            'training_steps': self.training_steps,
            'memory_size': len(self.memory),
            'device': str(self.device)
        }


if __name__ == '__main__':
    # Test agent creation
    print("Testing DDQN Agent...")
    agent = DDQNAgent(state_dim=8, action_dim=3)
    
    # Test action selection
    test_state = np.random.rand(8)
    action = agent.select_action(test_state)
    print(f"Selected action: {action}")
    
    # Test experience storage
    agent.store_experience(test_state, action, 10.0, test_state, False)
    print(f"Memory size: {len(agent.memory)}")
    
    print("DDQN Agent test successful!")
