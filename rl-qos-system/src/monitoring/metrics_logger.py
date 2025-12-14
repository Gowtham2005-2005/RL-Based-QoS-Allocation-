#!/usr/bin/env python3
"""
Metrics Logger
Logs network metrics to CSV for analysis
"""

import csv
import os
from datetime import datetime


class MetricsLogger:
    """Logs network metrics to CSV file"""
    
    def __init__(self, log_file='data/network_traces/live_metrics.csv'):
        self.log_file = log_file
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Initialize CSV file with headers
        self.initialize_log()
    
    def initialize_log(self):
        """Create CSV file with headers"""
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp',
                'work_bw',
                'entertain_bw',
                'work_lat',
                'entertain_lat',
                'work_loss',
                'entertain_loss',
                'action',
                'action_name',
                'reward'
            ])
        print(f"Metrics log initialized: {self.log_file}")
    
    def log(self, metrics):
        """
        Log metrics to CSV
        
        Args:
            metrics: Dictionary with keys:
                - work_bw: Work bandwidth (Mbps)
                - entertain_bw: Entertainment bandwidth (Mbps)
                - work_lat: Work latency (ms)
                - entertain_lat: Entertainment latency (ms)
                - work_loss: Work packet loss (0-1)
                - entertain_loss: Entertainment packet loss (0-1)
                - action: RL action (0, 1, or 2)
                - action_name: Action name string
                - reward: Reward value (optional)
        """
        try:
            with open(self.log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    metrics.get('work_bw', 0),
                    metrics.get('entertain_bw', 0),
                    metrics.get('work_lat', 0),
                    metrics.get('entertain_lat', 0),
                    metrics.get('work_loss', 0),
                    metrics.get('entertain_loss', 0),
                    metrics.get('action', 1),
                    metrics.get('action_name', 'balanced'),
                    metrics.get('reward', 0)
                ])
        except Exception as e:
            print(f"Error logging metrics: {e}")
    
    def clear_log(self):
        """Clear existing log and reinitialize"""
        self.initialize_log()


if __name__ == '__main__':
    # Test logger
    print("Testing MetricsLogger...")
    
    logger = MetricsLogger('data/network_traces/test_metrics.csv')
    
    # Log some sample data
    for i in range(5):
        metrics = {
            'work_bw': 50 + i * 5,
            'entertain_bw': 30 + i * 3,
            'work_lat': 10 + i,
            'entertain_lat': 12 + i,
            'work_loss': 0.01,
            'entertain_loss': 0.02,
            'action': i % 3,
            'action_name': ['work_priority', 'balanced', 'entertainment'][i % 3],
            'reward': 10.0 + i
        }
        logger.log(metrics)
    
    print("Test data logged successfully!")
