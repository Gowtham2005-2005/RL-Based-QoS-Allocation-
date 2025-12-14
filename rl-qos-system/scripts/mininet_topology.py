#!/usr/bin/env python3
"""
Mininet Network Topology for RL-QoS System
Creates 4 hosts, 1 OVS switch with QoS queues
"""

from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time
import subprocess


def setup_qos_queues():
    """Configure QoS queues on OVS switch"""
    info('*** Configuring QoS queues on switch s1\n')
    
    commands = [
        # Create QoS configuration
        'ovs-vsctl -- set port s1-eth1 qos=@newqos -- '
        '--id=@newqos create qos type=linux-htb other-config:max-rate=1000000000 queues=0=@q0,1=@q1,2=@q2 -- '
        '--id=@q0 create queue other-config:min-rate=700000000 other-config:max-rate=1000000000 -- '
        '--id=@q1 create queue other-config:min-rate=500000000 other-config:max-rate=1000000000 -- '
 '--id=@q2 create queue other-config:min-rate=300000000 other-config:max-rate=1000000000',
        
        # Apply to all ports
        'ovs-vsctl set port s1-eth2 qos=@newqos',
        'ovs-vsctl set port s1-eth3 qos=@newqos',
        'ovs-vsctl set port s1-eth4 qos=@newqos',
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            info(f'Warning: QoS command failed: {e}\n')
    
    info('*** QoS queues configured\n')


def create_topology():
    """Create network topology"""
    info('*** Creating RL-QoS Network Topology\n')
    
    # Create Mininet network
    net = Mininet(
        controller=RemoteController,
        switch=OVSKernelSwitch,
        link=TCLink,
        autoSetMacs=True,
        autoStaticArp=True
    )
    
    info('*** Adding controller\n')
    # Remote controller (Ryu will connect here)
    c0 = net.addController(
        'c0',
        controller=RemoteController,
        ip='127.0.0.1',
        port=6653
    )
    
    info('*** Adding switch\n')
    # OpenFlow 1.3 switch
    s1 = net.addSwitch(
        's1',
        protocols='OpenFlow13',
        failMode='secure'
    )
    
    info('*** Adding hosts\n')
    # Work hosts
    h1 = net.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
    
    # Entertainment hosts
    h3 = net.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')
    h4 = net.addHost('h4', ip='10.0.0.4/24', mac='00:00:00:00:00:04')
    
    info('*** Creating links\n')
    # Add links with bandwidth limit
    net.addLink(h1, s1, bw=100, delay='1ms')  # 100 Mbps
    net.addLink(h2, s1, bw=100, delay='1ms')
    net.addLink(h3, s1, bw=100, delay='1ms')
    net.addLink(h4, s1, bw=100, delay='1ms')
    
    info('*** Starting network\n')
    net.start()
    
    # Wait for switch to connect
    info('*** Waiting for switch to connect to controller...\n')
    time.sleep(3)
    
    # Setup QoS queues
    setup_qos_queues()
    
    info('\n')
    info('=' * 70 + '\n')
    info('Network Ready!\n')
    info('=' * 70 + '\n')
    info('Topology:\n')
    info('  Work Hosts:          h1 (10.0.0.1), h2 (10.0.0.2)\n')
    info('  Entertainment Hosts: h3 (10.0.0.3), h4 (10.0.0.4)\n')
    info('  Switch:              s1 (OpenFlow 1.3)\n')
    info('  Controller:          c0 (127.0.0.1:6653)\n')
    info('\n')
    info('QoS Queues:\n')
    info('  Queue 0: 700 Mbps min (High Priority)\n')
    info('  Queue 1: 500 Mbps min (Normal Priority)\n')
    info('  Queue 2: 300 Mbps min (Low Priority)\n')
    info( '=' * 70 + '\n')
    info('\n')
    info('Test connectivity:\n')
    net.pingAll()
    
    info('\n')
    info('=' * 70 + '\n')
    info('Commands you can try:\n')
    info('  h1 iperf -s &                    # Start iperf server on h1\n')
    info('  h3 iperf -c 10.0.0.1 -t 60       # Test bandwidth from h3\n')
    info('  h1 ping h3                       # Test latency\n')
    info('  exit                             # Stop network\n')
    info('=' * 70 + '\n')
    info('\n')
    
    # Enter CLI
    CLI(net)
    
    # Cleanup
    info('*** Stopping network\n')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    create_topology()
