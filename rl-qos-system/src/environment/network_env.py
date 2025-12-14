#!/usr/bin/env python3
"""
Simulated Network Environment for RL Training
Generates synthetic traffic patterns - NO REAL NETWORK NEEDED
"""

import numpy as np
import random


class NetworkEnvironment:
    """
    Simulated network environment for RL training
    Mimics real network behavior with synthetic traffic
    """
    
    def __init__(self, config=None):
        # State space
        self.state_dim = 8
        # [work_bw, entertain_bw, work_lat, entertain_lat, work_loss, entertain_loss, total_bw, time_of_day]
        
        # Action space
        self.action_dim = 3
        # [0: Work Priority, 1: Balanced, 2: Entertainment Priority]
        
        # Network parameters
        self.total_bandwidth = 100.0  # Mbps
        self.base_work_demand = 40.0
        self.base_entertain_demand = 30.0
        self.base_latency = 10.0  # ms
        
        # Traffic patterns
        self.traffic_patterns = {
            'morning': {'work': 1.2, 'entertainment': 0.6},
            'work_hours': {'work': 1.8, 'entertainment': 0.4},
            'lunch': {'work': 0.8, 'entertainment': 1.2},
            'evening': {'work': 0.5, 'entertainment': 2.0},
            'night': {'work': 0.3, 'entertainment': 0.7}
        }
        
        # Episode tracking
        self.step_count = 0
        self.max_steps = 200
        
        self.reset()
    
    def reset(self):
        """Reset environment to initial state"""
        self.step_count = 0
        self.current_hour = random.randint(0, 23)
        
        # Initialize random demands with realistic values
        self.work_demand = self.base_work_demand + np.random.randn() * 10
        self.entertain_demand = self.base_entertain_demand + np.random.randn() * 10
        
        # Clip to reasonable ranges
        self.work_demand = np.clip(self.work_demand, 10, 90)
        self.entertain_demand = np.clip(self.entertain_demand, 10, 90)
        
        # Current allocated bandwidth (starts balanced)
        self.work_allocated = 50.0
        self.entertain_allocated = 50.0
        
        return self._get_state()
    
    def _get_time_multipliers(self):
        """Get traffic multipliers based on time of day"""
        hour = self.current_hour
        
        if 6 <= hour < 9:  # Morning
            pattern = self.traffic_patterns['morning']
        elif 9 <= hour < 12 or 13 <= hour < 17:  # Work hours
            pattern = self.traffic_patterns['work_hours']
        elif 12 <= hour < 13:  # Lunch
            pattern = self.traffic_patterns['lunch']
        elif 17 <= hour < 23:  # Evening
            pattern = self.traffic_patterns['evening']
        else:  # Night (23-6)
            pattern = self.traffic_patterns['night']
        
        return pattern['work'], pattern['entertainment']
    
    def _get_state(self):
        """Build current state vector"""
        # Get time-based multipliers
        work_mult, entertain_mult = self._get_time_multipliers()
        
        # Calculate actual bandwidth demands
        work_demand = np.clip(
            self.work_demand * work_mult + np.random.randn() * 5,
            0, 100
        )
        entertain_demand = np.clip(
            self.entertain_demand * entertain_mult + np.random.randn() * 5,
            0, 100
        )
        
        # Calculate congestion
        total_demand = work_demand + entertain_demand
        congestion_factor = max(1.0, total_demand / self.total_bandwidth)
        
        # Calculate actual bandwidth (limited by allocation and demand)
        work_bw = min(self.work_allocated, work_demand)
        entertain_bw = min(self.entertain_allocated, entertain_demand)
        
        # Latency increases with congestion
        work_latency = self.base_latency * congestion_factor
        entertain_latency = self.base_latency * congestion_factor
        
        # Add allocation-based latency (under-allocated traffic suffers)
        if work_demand > self.work_allocated:
            work_latency *= (work_demand / self.work_allocated)
        if entertain_demand > self.entertain_allocated:
            entertain_latency *= (entertain_demand / self.entertain_allocated)
        
        # Packet loss occurs when demand >> allocation
        work_loss = max(0, (work_demand - self.work_allocated) / 100.0)
        entertain_loss = max(0, (entertain_demand - self.entertain_allocated) / 100.0)
        
        # Add congestion-based loss
        if congestion_factor > 1.2:
            work_loss += (congestion_factor - 1.2) * 0.05
            entertain_loss += (congestion_factor - 1.2) * 0.05
        
        # Build state vector (normalized to 0-1)
        state = np.array([
            work_bw / 100.0,
            entertain_bw / 100.0,
            np.clip(work_latency / 100.0, 0, 1),
            np.clip(entertain_latency / 100.0, 0, 1),
            np.clip(work_loss, 0, 1),
            np.clip(entertain_loss, 0, 1),
            self.total_bandwidth / 100.0,
            self.current_hour / 23.0
        ], dtype=np.float32)
        
        return state
    
    def step(self, action):
        """
        Execute action and return next state, reward, done
        
        Actions:
            0: Work priority (work 70%, entertainment 30%)
            1: Balanced (work 50%, entertainment 50%)
            2: Entertainment priority (work 30%, entertainment 70%)
        """
        # Apply action to bandwidth allocation
        if action == 0:  # Work priority
            self.work_allocated = 70.0
            self.entertain_allocated = 30.0
        elif action == 1:  # Balanced
            self.work_allocated = 50.0
            self.entertain_allocated = 50.0
        elif action == 2:  # Entertainment priority
            self.work_allocated = 30.0
            self.entertain_allocated = 70.0
        
        # Get new state
        state = self._get_state()
        
        # Calculate reward
        reward = self._calculate_reward(state, action)
        
        # Update time and demands
        self.step_count += 1
        self.current_hour = (self.current_hour + 1) % 24
        
        # Add random variations to demands
        self.work_demand += np.random.randn() * 3
        self.entertain_demand += np.random.randn() * 3
        self.work_demand = np.clip(self.work_demand, 10, 90)
        self.entertain_demand = np.clip(self.entertain_demand, 10, 90)
        
        # Episode done after max_steps
        done = self.step_count >= self.max_steps
        
        # Get next state
        next_state = self._get_state()
        
        return next_state, reward, done
    
    def _calculate_reward(self, state, action):
        """
        Calculate reward based on QoS satisfaction
        
        Reward components:
        1. QoS satisfaction (main objective)
        2. Bandwidth utilization (efficiency)
        3. Packet loss penalty
        4. Time-appropriate action bonus
        """
        work_bw = state[0] * 100
        entertain_bw = state[1] * 100
        work_latency = state[2] * 100
        entertain_latency = state[3] * 100
        work_loss = state[4]
        entertain_loss = state[5]
        time_of_day = state[7] * 23
        
        reward = 0.0
        
        # === QoS Satisfaction Rewards ===
        
        if action == 0:  # Work priority
            # Good work performance
            if work_bw > 50 and work_latency < 20:
                reward += 15
            elif work_bw > 40:
                reward += 10
            
            # Penalty if work doesn't get good service
            if work_bw < 30 or work_latency > 50:
                reward -= 20
            
            # Minor penalty if entertainment suffers too much
            if entertain_bw < 15:
                reward -= 8
                
        elif action == 1:  # Balanced
            # Reward balanced allocation
            if 35 < work_bw < 65 and 35 < entertain_bw < 65:
                reward += 12
            
            # Penalty for imbalance
            if abs(work_bw - entertain_bw) > 30:
                reward -= 10
                
        elif action == 2:  # Entertainment priority
            # Good entertainment performance
            if entertain_bw > 50 and entertain_latency < 20:
                reward += 15
            elif entertain_bw > 40:
                reward += 10
            
            # Penalty if entertainment doesn't get good service
            if entertain_bw < 30 or entertain_latency > 50:
                reward -= 20
            
            # Minor penalty if work suffers too much
            if work_bw < 15:
                reward -= 8
        
        # === Bandwidth Utilization Reward ===
        total_usage = work_bw + entertain_bw
        utilization = total_usage / self.total_bandwidth
        reward += utilization * 3  # Encourage high utilization
        
        # === Packet Loss Penalty ===
        total_loss = work_loss + entertain_loss
        reward -= total_loss * 15  # Heavy penalty for packet loss
        
        # === Latency Penalty ===
        avg_latency = (work_latency + entertain_latency) / 2
        if avg_latency > 30:
            reward -= (avg_latency - 30) * 0.2
        
        # === Time-Appropriate Action Bonus ===
        if 9 <= time_of_day <= 17:  # Work hours
            if action == 0:  # Work priority is appropriate
                reward += 5
            elif action == 2:  # Entertainment priority is inappropriate
                reward -= 5
        elif 18 <= time_of_day <= 23:  # Evening
            if action == 2:  # Entertainment priority is appropriate
                reward += 5
            elif action == 0:  # Work priority is inappropriate
                reward -= 5
        
        # === Fairness ===
        # Slight penalty for extreme allocations
        if min(work_bw, entertain_bw) < 10:
            reward -= 3
        
        return reward
    
    def get_info(self):
        """Get environment information"""
        return {
            'step': self.step_count,
            'hour': self.current_hour,
            'work_demand': self.work_demand,
            'entertain_demand': self.entertain_demand,
            'work_allocated': self.work_allocated,
            'entertain_allocated': self.entertain_allocated
        }


if __name__ == '__main__':
    # Test environment
    print("Testing Network Environment...")
    env = NetworkEnvironment()
    
    state = env.reset()
    print(f"Initial state: {state}")
    
    for _ in range(5):
        action = random.randint(0, 2)
        next_state, reward, done = env.step(action)
        print(f"Action: {action}, Reward: {reward:.2f}, Done: {done}")
        
        if done:
            break
    
    print("Environment test successful!")
