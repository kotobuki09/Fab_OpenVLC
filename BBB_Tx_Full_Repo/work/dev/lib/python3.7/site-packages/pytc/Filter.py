__author__ = 'P.Gawlowicz'

import iptc
from pyroute2.netlink import NetlinkError

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class FlowMarkGenerator(object, metaclass=Singleton):
    def __init__(self):
        self.value = 1

    def GenerateValue(self):
        curVal = self.value
        self.value += 1
        return curVal


class FlowDesc(object):
    def __init__(self, src=None, srcPort=None, dst=None, dstPort=None, prot=None, name=None, srcMac=None, dstMac=None):
        self.mSrcAddress = src
        self.mDstAddress = dst
        self.mSrcPort = srcPort
        self.mDstPort = dstPort
        self.mProt = prot
        self.mName = name
        self.mSrcMac = srcMac
        self.mDstMac = dstMac


class Filter(object):
    #AC to TOS mapping
    BE = 20
    BK = 40
    VO = 160
    VI = 200

    def __init__(self, name):
        self.mName = name
        self.mIsInstalled = False
        #for traffic control
        self.mTcProtocol = 'ip'
        self.mParent = None
        self.mPrio = 1
        self.mTarget = None

        #for IPTABLES
        self.mTable = 'mangle'
        self.mChain = 'POSTROUTING'
        self.mIpTablesProtocol = None
        self.mSrcAddress = None
        self.mDstAddress = None
        self.mSrcPort = None
        self.mDstPort = None
        self.mMarkId = FlowMarkGenerator().GenerateValue()
        self.mTos = self.BE

        #for filter in QDISC
        self.isMacFilter = False
        self.mSrcMac = None
        self.mDstMac = None

    def setParent(self, parent):
        """
        Func desc
        """
        self.mParent = parent
        return

    def setInterface(self, iface):
        """
        Func desc
        """
        self.mInterface = iface
        return

    def setFilterPriority(self, priority):
        """
        Func desc
        """
        self.mPrio = priority
        return

    def setFiveTuple(self, src=None, srcPort=None, dst=None, dstPort=None, prot=None):
        """
        Func desc
        """
        self.mSrcAddress = src
        self.mDstAddress = dst
        self.mSrcPort = srcPort
        self.mDstPort = dstPort
        self.mIpTablesProtocol = prot
        pass

    def setMacFilter(self, src=None, dst=None):
        """
        Func desc
        """
        self.isMacFilter = True
        self.mSrcMac = src
        self.mDstMac = dst
        pass

    def setFlowId(self, flowid):
        """
        Func desc
        """
        self.mMarkId = flowid
        return

    def setTos(self, tos):
        """
        Func desc
        """
        self.mTos = tos
        return

    def setTarget(self, target):
        """
        Func desc
        """
        self.mTarget = target
        return        

    def installMarkRuleInIpTables(self, ipr):
        rule = iptc.Rule()

        #rule.in_interface = "eth0"
        #rule.out_interface = "eth0"

        if self.mSrcAddress is not None:
            rule.src = self.mSrcAddress
        
        if self.mDstAddress is not None:
            rule.dst = self.mDstAddress
        
        if self.mIpTablesProtocol is not None:
            rule.protocol = self.mIpTablesProtocol
            match = iptc.Match(rule, self.mIpTablesProtocol)

            if self.mSrcPort is not None:
                match.sport = self.mSrcPort

            if self.mDstPort is not None:
                match.dport = self.mDstPort
            
            rule.add_match(match)
        
        target = iptc.Target(rule, "MARK")
        target.set_mark = str(self.mMarkId)
        rule.target = target
        chain = iptc.Chain(iptc.Table(self.mTable), self.mChain)
        chain.insert_rule(rule)
        
        if self.mTos is not None:
            target = iptc.Target(rule, "TOS")
            target.set_tos = str(self.mTos)
            rule.target = target
            chain.insert_rule(rule)
        pass

    def installMarkFilter(self, ipr):
        ifindex = self.mInterface.mIndex
        idx = self.mTarget.mHandle.getHex()
        parent = self.mParent.mHandle.getHex()
        mark=self.mMarkId

        ETH_P_IP = 0x0800
        fprio = self.mPrio
        extra_args = {}

        try:
            ipr.tc("add-filter", 'fw', ifindex, mark, 
                        parent=parent, 
                        protocol=ETH_P_IP, 
                        prio=fprio,
                        classid=idx,
                        **extra_args)
        except NetlinkError as e:
            print("Exception during filter installation")
        except Exception as e:
            print("Exception during filter installation")
            raise

    def installMacFilter(self, ipr):
        #tc filter add dev eth0 parent 1: prio 21 protocol ip u32 match ether dst b8:ae:ed:75:25:30 flowid 1:11

        ifindex = self.mInterface.mIndex
        idx = self.mTarget.mHandle.getHex()
        parent = self.mParent.mHandle.getHex()

        ETH_P_IP = 0x0800
        fprio = self.mPrio
        extra_args = {}

        if 0:
            try:
                mykeys = []
                if self.mSrcMac:
                    pass
                if self.mDstMac:
                    mykeys.extend(["0x0000b8ae/0x0000ffff-16", "0xed752530/0xffffffff-12"])
                ipr.tc("add-filter", 'u32', ifindex, 
                            parent=parent, 
                            protocol=ETH_P_IP, 
                            prio=fprio,
                            target=idx,
                            keys=mykeys
                            )

            except NetlinkError as e:
                print("Exception during filter installation")
            except Exception as e:
                print("Exception during filter installation")
                raise
        
        else:
            import os
            ifName = self.mInterface.mName
            parent = self.mParent.mHandle.getHexStr()
            fprio = self.mPrio
            dstMac = self.mDstMac
            target = self.mTarget.mHandle.getHexStr()
            cmd =  "tc filter add dev {0} \
                    parent {1} prio {2} protocol ip \
                    u32 match ether dst {3} \
                    flowid {4}".format(ifName, parent, fprio, dstMac, target)
            os.system(cmd)

            pass


    def install(self, ipr):
        if self.isMacFilter == True:
            self.installMacFilter(ipr)
        else:
            self.installMarkFilter(ipr)
            self.installMarkRuleInIpTables(ipr)

