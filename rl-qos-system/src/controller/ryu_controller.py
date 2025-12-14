#!/usr/bin/env python3
"""
Ryu SDN Controller with Integrated RL Agent
Complete production implementation for Linux deployment
"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp, ether_types
from ryu.lib import hub

import torch
import numpy as np
import threading
import time
import csv
import os
import sys
from datetime import datetime
from collections import defaultdict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.rl_agent.ddqn_agent import DDQNAgent
from src.monitoring.metrics_logger import MetricsLogger


class RLQoSController(app_manager.RyuApp):
    """
    SDN Controller with Integrated RL for QoS Allocation
    
    Features:
    - Real-time RL decision making (every 2 seconds)
    - OpenFlow 1.3 flow management
    - QoS queue enforcement
    - Live metrics logging
    - Stats collection from OVS
    """
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(RLQoSController, self).__init__(*args, **kwargs)
        
        self.logger.info("=" * 70)
        self.logger.info("RL-QoS SDN Controller Starting...")
        self.logger.info("=" * 70)
        
        # Network state
        self.datapaths = {}  # dpid → datapath object
        self.mac_to_port = {}  # MAC learning table
        
        # Port statistics
        self.port_stats = defaultdict(lambda: {
            'rx_bytes': 0,
            'tx_bytes': 0,
            'rx_packets': 0,
            'tx_packets': 0,
            'rx_dropped': 0,
            'tx_dropped': 0,
            'timestamp': time.time()
        })
        
        # Current bandwidth measurements
        self.current_bandwidth = {}  # port → {'rx': Mbps, 'tx': Mbps}
        
        # Device to port mapping (from topology)
        self.device_ports = {
            'work': [1, 2],       # h1, h2 connected to ports 1, 2
            'entertainment': [3, 4]  # h3, h4 connected to ports 3, 4
        }
        
        # Load RL agent
        self.logger.info("Loading RL Agent...")
        self.rl_agent = self._load_rl_agent()
        
        # Current QoS state
        self.current_action = 1  # Start with balanced
        self.action_names = {
            0: 'WORK_PRIORITY',
            1: 'BALANCED',
            2: 'ENTERTAINMENT_PRIORITY'
        }
        
        # Queue configuration
        self.queue_config = {
            0: {'work': 0, 'entertainment': 2},  # Work priority
            1: {'work': 1, 'entertainment': 1},  # Balanced
            2: {'work': 2, 'entertainment': 0}   # Entertainment priority
        }
        
        # Metrics logging
        log_dir = 'data/network_traces'
        os.makedirs(log_dir, exist_ok=True)
        self.metrics_logger = MetricsLogger(
            os.path.join(log_dir, 'live_metrics.csv')
        )
        
        # Start background threads
        self.monitor_thread = hub.spawn(self._monitor_loop)
        self.rl_thread = hub.spawn(self._rl_decision_loop)
        
        self.logger.info("✓ Controller initialized")
        self.logger.info("=" * 70)
    
    def _load_rl_agent(self):
        """Load trained RL model"""
        try:
            config_path = 'config/rl_config.yaml'
            agent = DDQNAgent(config_path=config_path)
            
            # Try to load trained model
            model_path = 'data/models/ddqn_best.pth'
            if os.path.exists(model_path):
                agent.load_model(model_path)
                self.logger.info(f"✓ Loaded trained model from {model_path}")
            else:
                self.logger.warning(f"⚠ Model not found: {model_path}")
                self.logger.warning("⚠ Using untrained agent (random policy)")
            
            # Set to inference mode (no exploration)
            agent.epsilon = 0.0
            
            return agent
            
        except Exception as e:
            self.logger.error(f"✗ Failed to load RL agent: {e}")
            return None
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """Handle switch connection"""
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id
        
        self.datapaths[dpid] = datapath
        
        self.logger.info(f"[SWITCH] Connected: DPID={dpid}")
        
        # Install table-miss flow entry (send unknown packets to controller)
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                         ofproto.OFPCML_NO_BUFFER)]
        self._add_flow(datapath, 0, match, actions)
        
        self.logger.info(f"[SWITCH] DPID={dpid} configured with table-miss rule")
    
    def _add_flow(self, datapath, priority, match, actions, buffer_id=None, 
                  idle_timeout=0, hard_timeout=0):
        """Add flow entry to switch"""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        
        if buffer_id:
            mod = parser.OFPFlowMod(
                datapath=datapath,
                buffer_id=buffer_id,
                priority=priority,
                match=match,
                instructions=inst,
                idle_timeout=idle_timeout,
                hard_timeout=hard_timeout
            )
        else:
            mod = parser.OFPFlowMod(
                datapath=datapath,
                priority=priority,
                match=match,
                instructions=inst,
                idle_timeout=idle_timeout,
                hard_timeout=hard_timeout
            )
        
        datapath.send_msg(mod)
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        """Handle packets sent to controller"""
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        
        # Ignore LLDP packets
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return
        
        dst = eth.dst
        src = eth.src
        dpid = datapath.id
        
        # Learn MAC address
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port
        
        # Determine output port
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD
        
        actions = [parser.OFPActionOutput(out_port)]
        
        # Install flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self._add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self._add_flow(datapath, 1, match, actions)
        
        # Send packet out
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        
        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data
        )
        datapath.send_msg(out)
    
    def _monitor_loop(self):
        """Periodically request port statistics"""
        self.logger.info("[MONITOR] Stats collection loop started")
        
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(1)  # Request every second
    
    def _request_stats(self, datapath):
        """Request port statistics from switch"""
        parser = datapath.ofproto_parser
        
        req = parser.OFPPortStatsRequest(datapath, 0, datapath.ofproto.OFPP_ANY)
        datapath.send_msg(req)
    
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        """Handle port statistics reply"""
        body = ev.msg.body
        
        for stat in body:
            port_no = stat.port_no
            
            # Skip local/special ports
            if port_no > 10000:
                continue
            
            # Calculate bandwidth
            prev_stat = self.port_stats[port_no]
            time_diff = time.time() - prev_stat['timestamp']
            
            if time_diff > 0:
                # Bytes to Mbps: (bytes * 8) / (time * 1e6)
                rx_bw = ((stat.rx_bytes - prev_stat['rx_bytes']) * 8) / (time_diff * 1e6)
                tx_bw = ((stat.tx_bytes - prev_stat['tx_bytes']) * 8) / (time_diff * 1e6)
                
                self.current_bandwidth[port_no] = {
                    'rx': max(0, rx_bw),
                    'tx': max(0, tx_bw)
                }
            
            # Update stored stats
            self.port_stats[port_no] = {
                'rx_bytes': stat.rx_bytes,
                'tx_bytes': stat.tx_bytes,
                'rx_packets': stat.rx_packets,
                'tx_packets': stat.tx_packets,
                'rx_dropped': stat.rx_dropped,
                'tx_dropped': stat.tx_dropped,
                'timestamp': time.time()
            }
    
    def _get_network_state(self):
        """Build state vector for RL agent"""
        # Aggregate bandwidth by device type
        work_bw = 0.0
        entertainment_bw = 0.0
        
        for port_no, bw in self.current_bandwidth.items():
            if port_no in self.device_ports['work']:
                work_bw += bw['rx'] + bw['tx']
            elif port_no in self.device_ports['entertainment']:
                entertainment_bw += bw['rx'] + bw['tx']
        
        # Latency (simplified - would use ping in production)
        work_latency = 10.0
        entertainment_latency = 10.0
        
        # Packet loss (from dropped packets)
        work_loss = 0.0
        entertainment_loss = 0.0
        
        for port_no in self.device_ports['work']:
            stat = self.port_stats.get(port_no, {})
            dropped = stat.get('rx_dropped', 0) + stat.get('tx_dropped', 0)
            packets = stat.get('rx_packets', 1) + stat.get('tx_packets', 1)
            work_loss += dropped / max(packets, 1)
        
        for port_no in self.device_ports['entertainment']:
            stat = self.port_stats.get(port_no, {})
            dropped = stat.get('rx_dropped', 0) + stat.get('tx_dropped', 0)
            packets = stat.get('rx_packets', 1) + stat.get('tx_packets', 1)
            entertainment_loss += dropped / max(packets, 1)
        
        # Total bandwidth
        total_bw = 100.0
        
        # Time of day
        time_of_day = datetime.now().hour / 23.0
        
        # Build state vector (normalized)
        state = np.array([
            min(work_bw / 100.0, 1.0),
            min(entertainment_bw / 100.0, 1.0),
            min(work_latency / 100.0, 1.0),
            min(entertainment_latency / 100.0, 1.0),
            min(work_loss, 1.0),
            min(entertainment_loss, 1.0),
            total_bw / 100.0,
            time_of_day
        ], dtype=np.float32)
        
        return state, work_bw, entertainment_bw, work_latency, entertainment_latency
    
    def _rl_decision_loop(self):
        """Main RL decision loop - runs every 2 seconds"""
        self.logger.info("[RL] Decision loop started")
        
        # Wait for switch to connect
        while not self.datapaths:
            hub.sleep(1)
        
        while True:
            try:
                # Get current state
                state, work_bw, ent_bw, work_lat, ent_lat = self._get_network_state()
                
                # RL decision
                if self.rl_agent:
                    action = self.rl_agent.select_action(state, epsilon=0.0)
                else:
                    action = 1  # Default to balanced
                
                # Log decision
                self.logger.info("-" * 70)
                self.logger.info(f"[RL] State: work_bw={work_bw:.1f} Mbps, "
                               f"ent_bw={ent_bw:.1f} Mbps, hour={datetime.now().hour}")
                self.logger.info(f"[RL] Action: {action} ({self.action_names[action]})")
                
                # Apply QoS policy if changed
                if action != self.current_action:
                    self._apply_qos_policy(action)
                    self.current_action = action
                    self.logger.info(f"[RL] ✓ Policy changed to {self.action_names[action]}")
                else:
                    self.logger.info(f"[RL] No change (keeping {self.action_names[action]})")
                
                # Log metrics for live monitoring
                self.metrics_logger.log({
                    'work_bw': work_bw,
                    'entertain_bw': ent_bw,
                    'work_lat': work_lat,
                    'entertain_lat': ent_lat,
                    'work_loss': state[4],
                    'entertain_loss': state[5],
                    'action': action,
                    'action_name': self.action_names[action],
                    'reward': 0  # Not training, no reward needed
                })
                
            except Exception as e:
                self.logger.error(f"[RL] Error in decision loop: {e}")
                import traceback
                traceback.print_exc()
            
            hub.sleep(2)  # Decision every 2 seconds
    
    def _apply_qos_policy(self, action):
        """Apply QoS policy by installing OpenFlow rules with queue assignments"""
        if not self.datapaths:
            return
        
        datapath = list(self.datapaths.values())[0]
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        
        # Get queue assignments for this action
        queues = self.queue_config[action]
        
        self.logger.info(f"[QoS] Applying policy: Work→Q{queues['work']}, "
                        f"Entertainment→Q{queues['entertainment']}")
        
        # Install rules for work ports
        for port_no in self.device_ports['work']:
            match = parser.OFPMatch(in_port=port_no)
            actions = [
                parser.OFPActionSetQueue(queues['work']),
                parser.OFPActionOutput(ofproto.OFPP_NORMAL)
            ]
            self._add_flow(datapath, 10, match, actions, hard_timeout=5)
        
        # Install rules for entertainment ports
        for port_no in self.device_ports['entertainment']:
            match = parser.OFPMatch(in_port=port_no)
            actions = [
                parser.OFPActionSetQueue(queues['entertainment']),
                parser.OFPActionOutput(ofproto.OFPP_NORMAL)
            ]
            self._add_flow(datapath, 10, match, actions, hard_timeout=5)
        
        self.logger.info(f"[QoS] ✓ Flow rules installed")
