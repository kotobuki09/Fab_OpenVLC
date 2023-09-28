#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Wishful IEEE 802.11 example.
"""

from mininet.net import Mininet
from mininet.node import Controller,OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

from wishful_mininet import WishfulNode, WishfulAgent, WishfulController

__author__ = "Zubow"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{zubow}@tkn.tu-berlin.de"


def topology():

    "Create a network."
    net = Mininet( controller=Controller, link=TCLink, switch=OVSKernelSwitch )

    print "*** Creating nodes"
    sta1 = net.addStation( 'sta1', mac='00:00:00:00:00:02', ip='10.0.0.2/8' )
    sta2 = net.addStation( 'sta2', mac='00:00:00:00:00:03', ip='10.0.0.3/8' )
    ap1 = net.addBaseStation( 'ap1', ssid= 'new-ssid1', mode= 'g', channel= '1', position='15,50,0' )
    ap2 = net.addBaseStation( 'ap2', ssid= 'new-ssid2', mode= 'g', channel= '6', position='25,30,0' )
    c1 = net.addController( 'c1', controller=Controller )

    print "*** Creating links"
    net.addLink(ap1, ap2)
    net.addLink(ap1, sta1)
    net.addLink(ap1, sta2)

    print "*** Starting network"
    net.build()
    c1.start()
    ap1.start( [c1] )
    ap2.start( [c1] )

    ap1.cmd('ifconfig ap1-eth1 20.0.0.2/8')
    ap2.cmd('ifconfig ap2-eth1 20.0.0.3/8')

    print "*** Starting Wishful framework"
    folder = './'

    print "*** ... agents ..."
    agent1 = WishfulAgent(ap1, folder + 'agent', folder + 'agent_config_1.yaml')
    agent2 = WishfulAgent(ap2, folder + 'agent', folder + 'agent_config_2.yaml')
    agent1.start()
    agent2.start()

    print "*** ... controller ..."
    wf_ctrl = WishfulController(ap1, folder + 'global_controller', folder + 'controller_config.yaml')
    wf_ctrl.start()

    print "*** Starting network"

    """uncomment to plot graph"""
    net.plotGraph(max_x=100, max_y=100)

    net.startMobility(startTime=0)
    net.mobility('sta1', 'start', time=0, position='10,45,0')
    net.mobility('sta1', 'stop', time=60, position='50,20,0')
    net.mobility('sta2', 'start', time=0, position='0,60,0')
    net.mobility('sta2', 'stop', time=60, position='30,10,0')
    net.stopMobility(stopTime=60)

    print "*** Running CLI"
    CLI( net )

    print "*** Stopping network"
    wf_ctrl.stop()    
    agent1.stop()
    agent2.stop()
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    topology()