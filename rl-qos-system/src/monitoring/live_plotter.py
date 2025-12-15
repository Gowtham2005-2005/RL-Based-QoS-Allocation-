#!/usr/bin/env python3
"""
ENHANCED Live Network Monitor with Real-time Graphs
Keeps window open, updates continuously, professional visualization
"""

import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend to keep window open
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime


class EnhancedLiveMonitor:
    """Enhanced real-time network monitor with professional visualization"""
    
    def __init__(self, metrics_file='data/network_traces/live_metrics.csv'):
        self.metrics_file = metrics_file
        
        # Setup figure with dark theme for professional look
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.canvas.manager.set_window_title('RL-QoS Live Network Monitor')
        
        # Create grid for subplots
        gs = self.fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        self.ax_bandwidth = self.fig.add_subplot(gs[0, :])  # Top: bandwidth (full width)
        self.ax_latency = self.fig.add_subplot(gs[1, 0])    # Middle left: latency
        self.ax_action = self.fig.add_subplot(gs[1, 1])     # Middle right: RL actions
        self.ax_stats = self.fig.add_subplot(gs[2, :])      # Bottom: statistics (full width)
        self.ax_stats.axis('off')  # Text only
        
        # Action mapping
        self.action_names = {
            0: 'WORK\nPRIORITY',
            1: 'BALANCED',
            2: 'ENTERTAINMENT\nPRIORITY'
        }
        
        self.action_colors = {
            0: '#00ff00',  # Green for work
            1: '#ffff00',  # Yellow for balanced
            2: '#ff00ff'   # Magenta for entertainment
        }
        
        # Data storage
        self.max_points = 100
        self.frame_count = 0
        
        print("=" * 70)
        print("ENHANCED LIVE NETWORK MONITOR")
        print("=" * 70)
        print(f"Monitoring: {metrics_file}")
        print("Window will stay open - close it manually when done")
        print("Graph updates every second")
        print("=" * 70)
    
    def animate(self, frame):
        """Animation update function"""
        try:
            if not os.path.exists(self.metrics_file):
                return
            
            # Read data
            df = pd.read_csv(self.metrics_file)
            
            if len(df) == 0:
                return
            
            # Limit to recent data
            if len(df) > self.max_points:
                df = df.tail(self.max_points)
            
            # Clear all axes
            self.ax_bandwidth.clear()
            self.ax_latency.clear()
            self.ax_action.clear()
            self.ax_stats.clear()
            self.ax_stats.axis('off')
            
            # === 1. BANDWIDTH GRAPH (TOP) ===
            time_idx = range(len(df))
            
            self.ax_bandwidth.plot(time_idx, df['work_bw'], 'g-', linewidth=3, 
                                  label='Work Traffic', marker='o', markersize=4)
            self.ax_bandwidth.plot(time_idx, df['entertain_bw'], 'm-', linewidth=3,
                                  label='Entertainment Traffic', marker='s', markersize=4)
            
            # Fill areas
            self.ax_bandwidth.fill_between(time_idx, 0, df['work_bw'], alpha=0.3, color='green')
            self.ax_bandwidth.fill_between(time_idx, 0, df['entertain_bw'], alpha=0.3, color='magenta')
            
            # Total bandwidth line
            total_bw = df['work_bw'] + df['entertain_bw']
            self.ax_bandwidth.plot(time_idx, total_bw, 'c--', linewidth=2, 
                                  label='Total Usage', alpha=0.7)
            
            self.ax_bandwidth.set_ylabel('Bandwidth (Mbps)', fontsize=12, fontweight='bold')
            self.ax_bandwidth.set_title('REAL-TIME BANDWIDTH ALLOCATION', 
                                       fontsize=14, fontweight='bold', color='cyan')
            self.ax_bandwidth.legend(loc='upper left', fontsize=10)
            self.ax_bandwidth.grid(True, alpha=0.3, linestyle='--')
            self.ax_bandwidth.set_ylim([0, 110])
            
            # Current values annotation
            if len(df) > 0:
                last_work = df['work_bw'].iloc[-1]
                last_ent = df['entertain_bw'].iloc[-1]
                self.ax_bandwidth.text(0.98, 0.95, 
                                      f'Current:\nWork: {last_work:.1f} Mbps\nEnt: {last_ent:.1f} Mbps',
                                      transform=self.ax_bandwidth.transAxes,
                                      fontsize=10, verticalalignment='top',
                                      horizontalalignment='right',
                                      bbox=dict(boxstyle='round', facecolor='black', alpha=0.8),
                                      color='yellow')
            
            # === 2. LATENCY GRAPH (MIDDLE LEFT) ===
            self.ax_latency.plot(time_idx, df['work_lat'], 'g-', linewidth=2, 
                                label='Work Latency', marker='o', markersize=3)
            self.ax_latency.plot(time_idx, df['entertain_lat'], 'm-', linewidth=2,
                                label='Entertainment Latency', marker='s', markersize=3)
            
            # Threshold line
            self.ax_latency.axhline(y=30, color='red', linestyle='--', 
                                   linewidth=2, label='Target (30ms)', alpha=0.7)
            
            self.ax_latency.set_ylabel('Latency (ms)', fontsize=11, fontweight='bold')
            self.ax_latency.set_title('NETWORK LATENCY', fontsize=12, fontweight='bold', color='yellow')
            self.ax_latency.legend(loc='upper left', fontsize=9)
            self.ax_latency.grid(True, alpha=0.3, linestyle='--')
            
            # === 3. RL ACTION VISUALIZATION (MIDDLE RIGHT) ===
            # Show action history as color-coded bars
            actions = df['action'].values[-30:]  # Last 30 actions
            action_time = range(len(actions))
            
            colors = [self.action_colors.get(int(a), '#ffffff') for a in actions]
            
            self.ax_action.bar(action_time, np.ones(len(actions)), 
                              color=colors, width=1.0, edgecolor='white', linewidth=0.5)
            
            self.ax_action.set_ylabel('RL Policy', fontsize=11, fontweight='bold')
            self.ax_action.set_title('RL DECISIONS (Last 30)', fontsize=12, fontweight='bold', color='cyan')
            self.ax_action.set_ylim([0, 1.2])
            self.ax_action.set_yticks([])
            
            # Add legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor=self.action_colors[0], label='Work Priority'),
                Patch(facecolor=self.action_colors[1], label='Balanced'),
                Patch(facecolor=self.action_colors[2], label='Entertainment')
            ]
            self.ax_action.legend(handles=legend_elements, loc='upper right', fontsize=8)
            self.ax_action.grid(True, alpha=0.2, axis='x')
            
            # === 4. STATISTICS PANEL (BOTTOM) ===
            if len(df) >= 10:
                recent = df.tail(10)
                
                stats_text = f"""
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  LIVE STATISTICS (Last 10 Readings)                                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  Work Traffic:                                                                           │
│    • Average: {recent['work_bw'].mean():.1f} Mbps  │  Peak: {recent['work_bw'].max():.1f} Mbps  │  Min: {recent['work_bw'].min():.1f} Mbps    │
│                                                                                          │
│  Entertainment Traffic:                                                                  │
│    • Average: {recent['entertain_bw'].mean():.1f} Mbps  │  Peak: {recent['entertain_bw'].max():.1f} Mbps  │  Min: {recent['entertain_bw'].min():.1f} Mbps    │
│                                                                                          │
│  RL Action Distribution:                                                                 │
│    • Work Priority: {(recent['action'] == 0).sum()}/10  │  Balanced: {(recent['action'] == 1).sum()}/10  │  Entertainment: {(recent['action'] == 2).sum()}/10   │
│                                                                                          │
│  Current RL Mode: {self.action_names[int(df['action'].iloc[-1])]:^20s}                                                     │
│  Total Readings: {len(df):>5d}                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                """
                
                self.ax_stats.text(0.05, 0.95, stats_text,
                                  transform=self.ax_stats.transAxes,
                                  fontsize=10, verticalalignment='top',
                                  fontfamily='monospace',
                                  color='cyan',
                                  bbox=dict(boxstyle='round', facecolor='black', alpha=0.9))
            
            # Overall title with timestamp
            self.fig.suptitle(f'RL-QoS LIVE NETWORK MONITOR - {datetime.now().strftime("%H:%M:%S")}',
                            fontsize=16, fontweight='bold', color='white')
            
            self.frame_count += 1
            
        except Exception as e:
            print(f"Error in animation: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Start the live monitor"""
        # Create animation that updates every second
        ani = animation.FuncAnimation(
            self.fig,
            self.animate,
            interval=1000,  # Update every 1000ms (1 second)
            cache_frame_data=False,
            blit=False
        )
        
        # Keep window open
        plt.show(block=True)  # Block until window is closed


if __name__ == '__main__':
    if len(sys.argv) > 1:
        metrics_file = sys.argv[1]
    else:
        metrics_file = 'data/network_traces/live_metrics.csv'
    
    monitor = EnhancedLiveMonitor(metrics_file)
    monitor.run()
