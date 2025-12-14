#!/usr/bin/env python3
"""
Live Bandwidth Plotter
Real-time visualization of network metrics
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np
import os
from datetime import datetime


class LivePlotter:
    """Real-time network metrics plotter"""
    
    def __init__(self, metrics_file='data/network_traces/live_metrics.csv'):
        self.metrics_file = metrics_file
        
        # Create figure with subplots
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(14, 10))
        self.fig.suptitle('RL-Based QoS System - Live Monitor', fontsize=16, fontweight='bold')
        
        # Action color mapping
        self.action_colors = {
            0: '#3498db',  # Blue - Work Priority
            1: '#95a5a6',  # Gray - Balanced
            2: '#e74c3c'   # Red - Entertainment Priority
        }
        
        self.action_names = {
            0: 'Work\nPriority',
            1: 'Balanced',
            2: 'Entertainment\nPriority'
        }
    
    def animate(self, frame):
        """Animation update function"""
        try:
            # Check if file exists
            if not os.path.exists(self.metrics_file):
                return
            
            # Read data
            df = pd.read_csv(self.metrics_file)
            
            if len(df) == 0:
                return
            
            # Limit to last 100 data points for readability
            if len(df) > 100:
                df = df.tail(100)
            
            # === Bandwidth Plot ===
            self.ax1.clear()
            self.ax1.plot(df.index, df['work_bw'], 'b-', linewidth=2.5, 
                         label='Work Bandwidth', marker='o', markersize=3)
            self.ax1.plot(df.index, df['entertain_bw'], 'r-', linewidth=2.5, 
                         label='Entertainment Bandwidth', marker='s', markersize=3)
            
            # Total bandwidth reference line
            total_bw = df['work_bw'] + df['entertain_bw']
            self.ax1.plot(df.index, total_bw, 'g--', linewidth=1.5, 
                         label='Total Usage', alpha=0.7)
            
            self.ax1.set_ylabel('Bandwidth (Mbps)', fontsize=11, fontweight='bold')
            self.ax1.set_title('Bandwidth Allocation Over Time', fontsize=12, fontweight='bold')
            self.ax1.legend(loc='upper left', fontsize=9)
            self.ax1.grid(True, alpha=0.3, linestyle='--')
            self.ax1.set_ylim([0, 110])
            
            # Add current values as text
            if len(df) > 0:
                last_work = df['work_bw'].iloc[-1]
                last_ent = df['entertain_bw'].iloc[-1]
                self.ax1.text(0.02, 0.98, f'Current: Work={last_work:.1f} Mbps, Ent={last_ent:.1f} Mbps',
                             transform=self.ax1.transAxes, fontsize=9,
                             verticalalignment='top', bbox=dict(boxstyle='round', 
                             facecolor='wheat', alpha=0.5))
            
            # === Latency Plot ===
            self.ax2.clear()
            self.ax2.plot(df.index, df['work_lat'], 'b-', linewidth=2, 
                         label='Work Latency', marker='o', markersize=3)
            self.ax2.plot(df.index, df['entertain_lat'], 'r-', linewidth=2, 
                         label='Entertainment Latency', marker='s', markersize=3)
            
            # Latency threshold line
            self.ax2.axhline(y=30, color='orange', linestyle='--', 
                           linewidth=1.5, label='Target Latency (30ms)', alpha=0.7)
            
            self.ax2.set_ylabel('Latency (ms)', fontsize=11, fontweight='bold')
            self.ax2.set_title('Network Latency', fontsize=12, fontweight='bold')
            self.ax2.legend(loc='upper left', fontsize=9)
            self.ax2.grid(True, alpha=0.3, linestyle='--')
            
            # === RL Action Plot ===
            self.ax3.clear()
            
            # Color-coded scatter plot
            colors = [self.action_colors.get(int(a), '#95a5a6') for a in df['action']]
            self.ax3.scatter(df.index, df['action'], c=colors, s=80, alpha=0.8, edgecolors='black')
            
            # Add connecting lines
            self.ax3.plot(df.index, df['action'], 'k-', linewidth=0.5, alpha=0.3)
            
            self.ax3.set_ylabel('RL Policy', fontsize=11, fontweight='bold')
            self.ax3.set_xlabel('Time Step', fontsize=11, fontweight='bold')
            self.ax3.set_title('RL Agent Decisions', fontsize=12, fontweight='bold')
            self.ax3.set_yticks([0, 1, 2])
            self.ax3.set_yticklabels([self.action_names[i] for i in [0, 1, 2]], fontsize=9)
            self.ax3.grid(True, alpha=0.3, linestyle='--', axis='x')
            self.ax3.set_ylim([-0.5, 2.5])
            
            # Add legend for actions
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor=self.action_colors[0], label='Work Priority'),
                Patch(facecolor=self.action_colors[1], label='Balanced'),
                Patch(facecolor=self.action_colors[2], label='Entertainment Priority')
            ]
            self.ax3.legend(handles=legend_elements, loc='upper left', fontsize=9)
            
            # Add statistics
            if len(df) >= 10:
                action_counts = df['action'].value_counts()
                stats_text = "Action Distribution (last 10): "
                stats_text += " | ".join([f"{self.action_names[i].replace(chr(10), ' ')}: {action_counts.get(i, 0)}" 
                                         for i in [0, 1, 2]])
                self.ax3.text(0.02, 0.02, stats_text,
                             transform=self.ax3.transAxes, fontsize=8,
                             verticalalignment='bottom', bbox=dict(boxstyle='round', 
                             facecolor='lightblue', alpha=0.5))
            
            plt.tight_layout(rect=[0, 0, 1, 0.97])
            
        except Exception as e:
            print(f"Error in animation: {e}")
    
    def run(self):
        """Start live plotting"""
        print("Starting live plotter...")
        print(f"Monitoring file: {self.metrics_file}")
        print("Close window to stop monitoring")
        
        # Create animation
        ani = animation.FuncAnimation(
            self.fig, 
            self.animate, 
            interval=1000,  # Update every 1 second
            cache_frame_data=False
        )
        
        plt.show()


def main():
    """Main function"""
    import sys
    
    # Get metrics file from command line or use default
    if len(sys.argv) > 1:
        metrics_file = sys.argv[1]
    else:
        metrics_file = 'data/network_traces/live_metrics.csv'
    
    # Create and run plotter
    plotter = LivePlotter(metrics_file)
    plotter.run()


if __name__ == '__main__':
    main()
