#!/usr/bin/env python3
"""
Enhanced Mininet Network Topology with Fixed QoS Setup
"""

from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time
import subprocess
import os


def setup_qos_queues_fixed(switch_name='s1'):
    """Fixed QoS queue configuration"""
    info('*** Configuring QoS queues (FIXED VERSION)\n')
    
    # First, clear any existing QoS
    subprocess.run(f'ovs-vsctl -- --all destroy qos', shell=True, stderr=subprocess.DEVNULL)
    subprocess.run(f'ovs-vsctl -- --all destroy queue', shell=True, stderr=subprocess.DEVNULL)
    
    time.sleep(1)
    
    # Create queues first
    info('Creating queues...\n')
    
    # Queue 0: High priority (700 Mbps min)
    q0 = subprocess.check_output(
        'ovs-vsctl create queue other-config:min-rate=700000000 other-config:max-rate=1000000000',
        shell=True
    ).decode().strip()
    
    # Queue 1: Normal priority (500 Mbps min)
    q1 = subprocess.check_output(
        'ovs-vsctl create queue other-config:min-rate=500000000 other-config:max-rate=1000000000',
        shell=True
    ).decode().strip()
    
    # Queue 2: Low priority (300 Mbps min)
    q2 = subprocess.check_output(
        'ovs-vsctl create queue other-config:min-rate=300000000 other-config:max-rate=1000000000',
        shell=True
    ).decode().strip()
    
    info('Queues created\n')
    
    # Create QoS
    info('Creating QoS...\n')
    qos = subprocess.check_output(
        f'ovs-vsctl create qos type=linux-htb other-config:max-rate=1000000000 queues:0={q0} queues:1={q1} queues:2={q2}',
        shell=True
    ).decode().strip()
    
    info('QoS created\n')
    
    # Apply QoS to all interfaces
    for i in range(1, 5):
        port = f'{switch_name}-eth{i}'
        try:
            subprocess.run(f'ovs-vsctl set port {port} qos={qos}', shell=True, check=True)
            info(f'  Applied QoS to {port}\n')
        except:
            info(f'  Warning: Could not apply QoS to {port}\n')
    
    info('*** QoS configuration complete!\n')


def create_topology():
    """Create enhanced network topology"""
    info('\n')
    info('=' * 70 + '\n')
    info('RL-QoS Network Topology - Enhanced Version\n')
    info('=' * 70 + '\n\n')
    
    # Create Mininet network
    net = Mininet(
        controller=RemoteController,
        switch=OVSKernelSwitch,
        link=TCLink,
        autoSetMacs=True,
        autoStaticArp=True
    )
    
    info('*** Adding controller\n')
    c0 = net.addController(
        'c0',
        controller=RemoteController,
        ip='127.0.0.1',
        port=6653
    )
    
    info('*** Adding switch\n')
    s1 = net.addSwitch(
        's1',
        protocols='OpenFlow13',
        failMode='secure'
    )
    
    info('*** Adding hosts\n')
    # Work hosts (will get high priority during work hours)
    h1 = net.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
    
    # Entertainment hosts (will get high priority during evening)
    h3 = net.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')
    h4 = net.addHost('h4', ip='10.0.0.4/24', mac='00:00:00:00:00:04')
    
    info('*** Creating links (100 Mbps each)\n')
    net.addLink(h1, s1, bw=100, delay='1ms')
    net.addLink(h2, s1, bw=100, delay='1ms')
    net.addLink(h3, s1, bw=100, delay='1ms')
    net.addLink(h4, s1, bw=100, delay='1ms')
    
    info('*** Starting network\n')
    net.start()
    
    info('*** Waiting for controller connection...\n')
    time.sleep(5)
    
    # Setup QoS with fixed version
    setup_qos_queues_fixed('s1')
    
    time.sleep(2)
    
    info('\n')
    info('=' * 70 + '\n')
    info('NETWORK READY!\n')
    info('=' * 70 + '\n')
    info('Topology:\n')
    info('  Work Hosts:          h1 (10.0.0.1), h2 (10.0.0.2)\n')
    info('  Entertainment Hosts: h3 (10.0.0.3), h4 (10.0.0.4)\n')
    info('  Switch:              s1 (OpenFlow 1.3 with QoS)\n')
    info('  Controller:          Ryu at 127.0.0.1:6653\n')
    info('\n')
    info('QoS Queues Configured:\n')
    info('  Queue 0: High Priority   (700 Mbps minimum)\n')
    info('  Queue 1: Normal Priority (500 Mbps minimum)\n')
    info('  Queue 2: Low Priority    (300 Mbps minimum)\n')
    info('=' * 70 + '\n')
    
    # Test connectivity
    info('\nTesting network connectivity...\n')
    net.pingAll()
    
    info('\n')
    info('=' * 70 + '\n')
    info('READY FOR DEMONSTRATION!\n')
    info('=' * 70 + '\n')
    info('\nCommands you can try:\n')
    info('  h1 iperf -s &                      # Start iperf server\n')
    info('  h3 iperf -c 10.0.0.1 -t 60 -i 1    # Test bandwidth\n')
    info('  sh ovs-ofctl dump-flows s1 -O OpenFlow13  # View OpenFlow rules\n')
    info('  exit                               # Stop network\n')
    info('=' * 70 + '\n\n')
    
    # Start CLI
    CLI(net)
    
    # Cleanup
    info('*** Stopping network\n')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    create_topology()
