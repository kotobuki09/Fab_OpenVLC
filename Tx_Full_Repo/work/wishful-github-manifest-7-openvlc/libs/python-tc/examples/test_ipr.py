#!/usr/bin/python

__author__ = 'P.Gawlowicz'

from pytc.TrafficControl import TrafficControl
import logging
import time, sys

from pyroute2 import IPRoute
from pyroute2.netlink.rtnl import TC_H_ROOT
from pyroute2.netlink.rtnl import RTM_DELQDISC
from pyroute2.netlink import NetlinkError
from pyroute2.netlink import NLM_F_REQUEST
from pyroute2.netlink import NLM_F_ACK
from pyroute2.netlink.rtnl import RTM_NEWQDISC

ETH_P_IP = 0x0800
PRIO = 1
HANDLE_MIN = 2
HANDLE_MAX = (2 ** 16) - 1

if __name__ == '__main__':
    ipr = IPRoute()
    tcMgr = TrafficControl()
    wlan0 = tcMgr.getInterface('wlan0')
    ifindex = wlan0.getIndex()
     
    operation = "del"
    if len(sys.argv) > 1:
        operation = str(sys.argv[1])

    if operation == "add":
        wlan0.clean()
        
        ipr.tc("add", "prio", ifindex, 0x10000, bands=5)
        ipr.tc("add", "pfifo", ifindex, 0x20000, parent=0x10001, limit=135)
        ipr.tc("add", "bfifo", ifindex, 0x30000, parent=0x10002, limit=150000)
        ipr.tc("add", "tbf",   ifindex, 0x40000, parent=0x10003, rate=10000, burst=20000, limit=1000)

        mark = 10
        extra_args = {}
        ipr.tc("add-filter", 'fw', ifindex, mark, parent=0x10000, protocol=ETH_P_IP, prio=PRIO, \
                        classid=0x30000, **extra_args)
    
    elif operation == "change":
        flags = NLM_F_REQUEST | NLM_F_ACK
        ipr.tc((RTM_NEWQDISC, flags), "tbf", ifindex, 0x40000, parent=0x10003, rate=60000, burst=50000, limit=5000)
        #tc qdisc change dev eth0 handle 4: tbf rate 2048Kbit burst 20Kb limit 10000
    else:
        wlan0.clean()
