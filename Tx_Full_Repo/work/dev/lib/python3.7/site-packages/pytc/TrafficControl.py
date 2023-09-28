__author__ = 'P.Gawlowicz'

import sys
from pyroute2 import IPRoute
from pyroute2.netlink.rtnl import TC_H_ROOT
from pyroute2.netlink.rtnl import RTM_DELQDISC
from pyroute2.netlink import NetlinkError

from pytc.Interface import Interface
import iptc


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class TrafficControl(object, metaclass=Singleton):
    def __init__(self):
        self.mIpr = IPRoute()
        self.mInterfaces = {}
        self.InterfaceDiscovery()
        self.markIdGenerator = 0;

    def InterfaceDiscovery(self):
        rawInts = self.mIpr.get_links()
        for interface in rawInts:
            ifname = interface.get_attr('IFLA_IFNAME')
            ifindex = interface['index']
            #print ifname, ifindex
            newInt = Interface(ifname, ifindex, self.mIpr)
            self.mInterfaces[ifname] = newInt

    def getInterface(self, name):
        return self.mInterfaces[name]

    def generateMark(self):
        self.markIdGenerator += 1
        return self.markIdGenerator

    def cleanIpTables(self):
        chainNames = ["PREROUTING", "INPUT", "FORWARD", "OUTPUT", "POSTROUTING"]
        for name in chainNames:
            chain = iptc.Chain(iptc.Table(iptc.Table.MANGLE), name)
            chain.flush()
