__author__ = 'P.Gawlowicz'

import time, sys, os
# Pyroute
from pyroute2 import IPRoute
from pyroute2.netlink.rtnl import TC_H_ROOT
from pyroute2.netlink.rtnl import RTM_NEWTCLASS
from pyroute2.netlink.rtnl import RTM_DELTCLASS
from pyroute2.netlink.rtnl import RTM_NEWQDISC
from pyroute2.netlink.rtnl import RTM_DELQDISC
from pyroute2.netlink.rtnl import RTM_NEWTFILTER
from pyroute2.netlink.rtnl import RTM_DELTFILTER
from pyroute2.netlink import NetlinkError

from pytc.Qdisc import NetemScheduler, TbfQueue, HtbScheduler, HtbClass
from pytc.Filter import FlowDesc, Filter
import iptc


class Interface(object):
    def __init__(self, name, index, ipr):
        self.mName = name
        self.mIndex = index
        self.mEgressScheduler = None
        self.mIngressScheduler = None
        self.mIpr = ipr
        self.mProfile = None

    def getName(self):
        return self.mName

    def getIndex(self):
        return self.mIndex

    def displayQdisc(self, ifname):
        cmd = str("tc qdisc show dev %s" % ifname )
        os.system(cmd);
    
    def displayClass(self, ifname):
        cmd = str("tc class show dev %s" % ifname )
        os.system(cmd);
    
    def displayFilter(self, ifname):
        cmd = str("tc filter show dev %s" % ifname )
        os.system(cmd);

    def displayIpTables(self):
        cmd = str("iptables -t mangle -vL")
        os.system(cmd);
    
    def cleanIpTables(self):
        chainNames = ["PREROUTING", "INPUT", "FORWARD", "OUTPUT", "POSTROUTING"]
        for name in chainNames:
            chain = iptc.Chain(iptc.Table(iptc.Table.MANGLE), name)
            chain.flush()

    def setEgressScheduler(self, sched):
        sched.setEgress()
       
        #Clean root before installation
        self.clean()

        #Set interface pointer
        sched.setInterface(self)
        self.mEgressScheduler = sched

        #Install root sched
        self.mEgressScheduler.install(self.mIpr)

        #clear iptables table: mangle
        self.cleanIpTables()

        #Install filters
        self.mEgressScheduler.installFilters(self.mIpr)

        #Display configuration
        if False:
            self.displayQdisc(self.mName)
            self.displayClass(self.mName)
            self.displayFilter(self.mName)
            self.displayIpTables()

        pass

    def updateEgressScheduler(self, sched):
        sched.setEgress()
        
        #Set interface pointer
        sched.setInterface(self)
        self.mEgressScheduler = sched

        #Update root sched
        self.mEgressScheduler.update(self.mIpr)

        #clear iptables table: mangle
        self.cleanIpTables()

        #Install filters
        self.mEgressScheduler.installFilters(self.mIpr)

        pass

    def delEgressScheduler(self):
        #Remove root qdisc
        self.clean()
        #Display configuration
        if False:
            self.displayQdisc(self.mName)
            self.displayClass(self.mName)
            self.displayFilter(self.mName)
        pass

    def setIngressScheduler(self, sched):
        sched.setIngress()
        self.mIngressScheduler = sched
        pass

    def delIngressScheduler(self):
        pass

    def setProfile(self, profile):
        self.mProfile = profile
        netem = NetemScheduler()
        netem.setInterface(self)
        netem.setProfile(profile)

        tbf = TbfQueue(rate=profile.rate, burst=profile.burst, limit=profile.blimit)
        netem.addShaper(tbf)

        self.setEgressScheduler(netem)

    def updateProfile(self, profile):
        oldProfile = self.mProfile
        self.mProfile = profile
        netem = self.mEgressScheduler
        netem.setProfile(profile)

        shaper = netem.getShaper()
        shaper.mRate = profile.rate
        shaper.mBurst = profile.burst
        shaper.mLimit = profile.blimit
        netem.addShaper(shaper)

        self.mEgressScheduler = netem

        self.updateEgressScheduler(netem)
        pass

    def clean(self):
        try:
            #self.logger.info("deleting root QDisc on {0}".format(eth_name))
            self.mIpr.tc('del', None, self.mIndex, 0, parent=TC_H_ROOT)
            self.mEgressScheduler = None
        except Exception as e:
            # a (2, 'No such file or directory') can be thrown if there is
            # nothing to delete. Ignore such error, return the error otherwise
            if isinstance(e, NetlinkError) and e.code == 2:
                print ("Could not delete root QDisc. There might have been nothing to delete")
            else:
                print(("Initializing root Qdisc for {0}", self.mName))
                raise
        pass

    def getMacForNeighborIp(self, dstNodeIp):
        dstNodeMac = None
        retVal = self.mIpr.get_neighbours(dst=dstNodeIp)
        tmp = retVal[0]
        tmp = tmp['attrs']
        for t in tmp:
            if t[0] == 'NDA_LLADDR':
                dstNodeMac  = t[1]
                break
        return dstNodeMac

    def setPerLinkProfile(self, profile, dstNodeIp):
        dstNodeMac = self.getMacForNeighborIp(dstNodeIp)
        htbSched = self.mEgressScheduler
        if isinstance(htbSched, HtbScheduler):
            print("HtbScheduler already installed")
        else:
            print("Need to install HtbScheduler")
            htbSched = HtbScheduler()
            self.mEgressScheduler = htbSched
            self.setEgressScheduler(htbSched)

        print("add class for emulation")
        htbclass = htbSched.addClass(HtbClass(rate=profile.rate, ceil=profile.rate))
        netem = NetemScheduler()
        netem.setInterface(self)
        netem.setProfile(profile)
        netem = htbclass.setQueue(netem)      

        htbfilter = Filter(name=dstNodeIp);
        htbfilter.setMacFilter(src=None, dst=dstNodeMac)
        htbfilter.setTarget(htbclass)
        htbSched.addFilter(htbfilter)
        htbSched.refresh(self.mIpr)
        pass

    def updatePerLinkProfile(self, profile, dstNodeIp):
        dstNodeMac = self.getMacForNeighborIp(dstNodeIp)
        outSched = self.mEgressScheduler

        pass

    def cleanPerLinkProfile(self, dstNodeIp):
        dstNodeMac = self.getMacForNeighborIp(dstNodeIp)
        outSched = self.mEgressScheduler
        if isinstance(outSched, HtbScheduler):
            print("HtbScheduler already installed")
        else:
            print("Need to install HtbScheduler")

        pass