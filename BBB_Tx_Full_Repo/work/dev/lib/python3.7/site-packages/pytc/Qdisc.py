__author__ = 'P.Gawlowicz'

# Pyroute stuff
from pyroute2 import IPRoute
from pyroute2.netlink.rtnl import TC_H_ROOT
from pyroute2.netlink.rtnl import RTM_NEWTCLASS
from pyroute2.netlink.rtnl import RTM_DELTCLASS
from pyroute2.netlink.rtnl import RTM_NEWQDISC
from pyroute2.netlink.rtnl import RTM_DELQDISC
from pyroute2.netlink.rtnl import RTM_NEWTFILTER
from pyroute2.netlink.rtnl import RTM_DELTFILTER
from pyroute2.netlink import NetlinkError

import time

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class MajorHandleGenerator(object, metaclass=Singleton):
    def __init__(self):
        self.value = 1

    def GenerateValue(self):
        curVal = self.value
        self.value += 1
        return curVal

class MinorHandleGenerator(object):
    def __init__(self):
        self.value = 1

    def GenerateValue(self):
        curVal = self.value
        self.value += 1
        return curVal


class Handle(object):
    def __init__(self, major, minor):
        self.mMajor = major
        self.mMinor = minor
        pass

    def __str__(self):
        return ("%d:%d" % (self.mMajor, self.mMinor))

    def __repr__(self):
        return self.__str__()

    def getStr(self):
        return ("%d:%d" % (self.mMajor, self.mMinor))

    def getHexStr(self):
        return ("%s:%s" % (hex(self.mMajor).split('x')[1], hex(self.mMinor).split('x')[1]))

    def getHex(self):
        return int(hex((self.mMajor<<16) + self.mMinor), 0)       

class TcClass(object):
    def __init__(self, handle=None, parent=None, installed=False):
        self.mHandle = handle
        self.mParent = parent
        self.mInstalled = installed
        self.leaf = None
        self.mInterface = None
        pass

    def setInterface(self, interface):
        self.mInterface = interface

#TODO: add autocommit as decorator
def autocommit(fn):
    def new(*args):
        obj = args[0]
        ret = fn(*args)
        if obj.autocommit:
            obj.refresh()
        return ret
    return new

class Qdisc(object):
    def __init__(self):
        self.mMinorHandleGen = MinorHandleGenerator()
        majorHandleGen = MajorHandleGenerator()
        self.mHandle = Handle(majorHandleGen.GenerateValue(),0)
        self.mParent = None

        self.isEgress = False
        self.isIngress = False

        self.mInterface = None
        pass

    def setInterface(self, interface):
        """
        Func desc
        """
        self.mInterface = interface
        pass

    def setParent(self, parent):
        """
        Func desc
        """
        self.mParent = parent
        pass

    def setEgress(self):
        """
        Func desc
        """
        self.isEgress = True
        self.isIngress = False
        pass

    def setIngress(self):
        """
        Func desc
        """
        self.isIngress = True
        self.isEgress = False
        pass

    def installFilters(self, ipr):
        """
        Func desc
        """
        pass        

class ClasslessQdisc(Qdisc):
    def __init__(self):
        super(ClasslessQdisc,self).__init__()
        pass

class ClassfulQdisc(Qdisc):
    def __init__(self):
        super(ClassfulQdisc,self).__init__()
        self.mClasses = []    
        self.mQueues = []
        self.mFilters = []
        pass

    def addClass(self, installed=False):
        """
        Func desc
        """
        classMinorVal = self.mMinorHandleGen.GenerateValue()
        classHandle = Handle(self.mHandle.mMajor, classMinorVal)
        parentHandle = Handle(self.mHandle.mMajor, 0)
        newClass = TcClass(classHandle, parentHandle, installed)
        self.mClasses.append(newClass)
        return newClass

    def delClass(self, classHandle):
        """
        Func desc
        """
        return 

    def addSched(self, sched):
        """
        Func desc
        """
        return

    def delSched(self, sched):
        """
        Func desc
        """
        return

    def addQueue(self, queue):
        """
        Func desc
        """
        found=False
        for c in self.mClasses:
            if c.leaf == None:
                found=True
                break
    
        parentHandle = c.mHandle
        queue.setParent(parentHandle)
        c.leaf = queue
        self.mQueues.append(queue)
        return queue

    def delQueue(self, queue):
        """
        Func desc
        """
        queue.setParent(None)
        #del self.mQueues[0]
        return queue

    def addFilter(self, tcfilter):
        """
        Func desc
        """
        tcfilter.setParent(self)
        self.mFilters.append(tcfilter)
        pass

    def setInterface(self, interface):
        """
        Func desc
        """
        self.mInterface = interface

        for tcClass in self.mClasses:
            tcClass.setInterface(interface)

        for queue in self.mQueues:
            queue.mInterface = interface

        for tcfilter in self.mFilters:
            tcfilter.mInterface = interface
        pass

    def setInterfaceToFilters(self, iface):
        """
        Func desc
        """
        for tcfilter in self.mFilters:
            tcfilter.setInterface(iface)
        pass

    def installFilters(self, ipr):
        """
        Func desc
        """
        for tcfilter in self.mFilters:
            if tcfilter.mIsInstalled is False:
                tcfilter.install(ipr)
                tcfilter.mIsInstalled = True
        pass

    def delFilter(self, tcfilter):
        """
        Func desc
        """
        tcfilter.setParent(None)
        #find and delete
        #del self.mFilters[tcfilter.mPrio]

        return

class PfifoQueue(ClasslessQdisc):
    def __init__(self, limit=100):
        super(PfifoQueue,self).__init__()
        self.mLimit = limit
    
    def install(self,ipr):
        ifid = self.mInterface.mIndex
        idx = self.mHandle.getHex()
        parent = self.mParent.getHex()
        try:
            ipr.tc(
                "add", 'pfifo', ifid, idx,
                parent=parent,
                limit=self.mLimit, 
            )
        except NetlinkError as e:
            print("Could not set PFIFO for interface: {0}".format(ifid))
        except Exception as e:
            print("Could not set profile for interface: {0}".format(ifid))
            raise



class BfifoQueue(ClasslessQdisc):
    def __init__(self, limit=10240):
        super(BfifoQueue,self).__init__()
        self.mLimit = limit

    def install(self,ipr):
        ifid = self.mInterface.mIndex
        idx = self.mHandle.getHex()
        parent = self.mParent.getHex()
        try:
            ipr.tc(
                "add", 'bfifo', ifid, idx,
                parent=parent,
                limit=self.mLimit, 
            )
        except NetlinkError as e:
            print("Could not set BFIFO for interface: {0}".format(ifid))
        except Exception as e:
            print("Could not set profile for interface: {0}".format(ifid))
            raise


class PfifoFastQueue(ClasslessQdisc):
    def __init__(self, limit=100):
        super(PfifoFastQueue,self).__init__()
        self.mLimit = limit

    def install(self, ipr):
        pass

class TbfQueue(ClasslessQdisc):
    def __init__(self, rate=2**22-1, burst=10*1024, limit=10000):
        super(TbfQueue,self).__init__()
        self.mRate = rate
        self.mBurst = burst
        self.mLimit = limit
    
    def install(self,ipr):
        ifid = self.mInterface.mIndex
        idx = self.mHandle.getHex()
        parent = self.mParent.getHex()
        try:
            ipr.tc(
                "add", 'tbf', ifid, idx,
                parent=parent,
                rate=self.mRate,
                burst=self.mBurst,
                limit=self.mLimit, 
            )
        except NetlinkError as e:
            print("Could not set TBF for interface: {0}".format(ifid))
        except Exception as e:
            print("Could not set profile for interface: {0}".format(ifid))
            raise

    def update(self,ipr):
        from pyroute2.netlink import NLM_F_REQUEST
        from pyroute2.netlink import NLM_F_ACK
        from pyroute2.netlink.rtnl import RTM_NEWQDISC

        ifid = self.mInterface.mIndex
        handle = self.mHandle.getHex()
        parent = self.mParent.getHex()
        flags = NLM_F_REQUEST | NLM_F_ACK

        try:
            ipr.tc(
                (RTM_NEWQDISC, flags), 'tbf', ifid, handle,
                parent=parent,
                rate=self.mRate,
                burst=self.mBurst,
                limit=self.mLimit, 
            )

        except NetlinkError as e:
            print("Could not update TBF for interface: {0}".format(ifid))
        except Exception as e:
            print("Could not update TBF for interface: {0}".format(ifid))
            raise


class SfqQueue(ClasslessQdisc):
    def __init__(self, limit=127, quantum=1514, depth=127, divisor=1024, perturb=10):
        super(SfqQueue,self).__init__()
        self.perturb = perturb
        self.limit=limit,
        self.quantum=quantum,
        self.depth=depth,
        self.divisor=divisor,

    def install(self,ipr):
        ifid = self.mInterface.mIndex
        idx = self.mHandle.getHex()

        if self.isEgress:
            parentId = TC_H_ROOT
        else:
            parentId = self.mParent.getHex()

        try:
            ipr.tc(
                "add", 'sfq', ifid, idx,
                parent=parentId,
                limit=self.limit,
                quantum=self.quantum,
                depth=self.depth,
                divisor=self.divisor,
                perturb=self.perturb,
            )
        except NetlinkError as e:
            print("Could not set TBF for interface: {0}".format(ifid))
        except Exception as e:
            print("Could not set profile for interface: {0}".format(ifid))
            raise

class NetemScheduler(ClasslessQdisc):
    def __init__(self, delay=0):
        super(NetemScheduler,self).__init__()
        self.mDelay = delay
        self.mProfile=None
        self.mShaper=None
        pass

    def setProfile(self, profile):
        self.mProfile = profile
        self.mDelay = profile.delay["TIME"] * 1000
        pass

    def addShaper(self, shaper):
        self.mShaper=shaper
        shaper.mParent = self.mHandle
        if self.mInterface is not None:
            self.mShaper.mInterface = self.mInterface
        pass

    def getShaper(self):
        return self.mShaper

    def setInterface(self, interface):
        """
        Func desc
        """
        self.mInterface = interface
        if self.mShaper is not None:
            self.mShaper.mInterface = interface

    def installSelf(self,ipr):
        profile = self.mProfile
        ifid = self.mInterface.mIndex
        idx = self.mHandle.getHex()
        
        if self.isEgress:
            parentId = TC_H_ROOT
        else:
            parentId = self.mParent.getHex()

        try:
            extra_args = {}
            if profile:
                extra_args.update({
                    'limit' : profile.plimit,
                    'delay' : profile.delay["TIME"] * 1000,
                    'jitter' : profile.delay["JITTER"] * 1000,
                    'delay_corr' : profile.delay["CORRELATION"],
                    'distribution' : profile.distribution,
                    'loss' : profile.loss["PERCENT"],
                    'loss_corr' : profile.loss["CORRELATION"],
                    'prob_corrupt' : profile.corruption["PERCENT"],
                    'corr_corrupt' : profile.corruption["CORRELATION"],
                    'duplicate' : profile.duplication["PERCENT"],
                    'dup_corr' : profile.duplication["CORRELATION"],
                    'prob_reorder' : profile.reorder["PERCENT"],
                    'corr_reorder' : profile.reorder["CORRELATION"],
                    'gap' : profile.reorder["GAP"],
                })
            else:
                extra_args.update({
                    'delay': self.mDelay * 1000
                })
            ipr.tc(
                "add", 'netem', ifid, idx,
                parent=parentId,
                **extra_args
            )                
        except NetlinkError as e:
            print("Could not set profile do interface: {0}".format(ifid))
        except Exception as e:
            print("Could not set profile do interface: {0}".format(ifid))
            raise

    def installShaper(self,ipr):
        if self.mShaper is not None:
            self.mShaper.install(ipr)

    def install(self,ipr):
        self.installSelf(ipr)
        self.installShaper(ipr)
        pass

    def updateSelf(self,ipr):
        from pyroute2.netlink import NLM_F_REQUEST
        from pyroute2.netlink import NLM_F_ACK
        from pyroute2.netlink.rtnl import RTM_NEWQDISC

        profile = self.mProfile
        ifid = self.mInterface.mIndex
        idx = self.mHandle.getHex()
        
        if self.isEgress:
            parentId = TC_H_ROOT
        else:
            parentId = self.mParent.getHex()

        flags = NLM_F_REQUEST | NLM_F_ACK

        try:
            ipr.tc(
                (RTM_NEWQDISC, flags), 'netem', ifid, idx,
                parent=parentId,
                limit=profile.plimit,
                delay=profile.delay["TIME"] * 1000,
                jitter=profile.delay["JITTER"] * 1000,
                delay_corr=profile.delay["CORRELATION"],
                distribution=profile.distribution,
                loss=profile.loss["PERCENT"],
                loss_corr=profile.loss["CORRELATION"],
                prob_corrupt=profile.corruption["PERCENT"],
                corr_corrupt=profile.corruption["CORRELATION"],
                duplicate=profile.duplication["PERCENT"],
                dup_corr=profile.duplication["CORRELATION"],
                prob_reorder=profile.reorder["PERCENT"],
                corr_reorder=profile.reorder["CORRELATION"],
                gap=profile.reorder["GAP"],
            )
        except NetlinkError as e:
            print("Could not update profile do interface: {0}".format(ifid))
        except Exception as e:
            print("Could not update profile do interface: {0}".format(ifid))
            raise

    def updateShaper(self,ipr):
        if self.mShaper is not None:
            self.mShaper.update(ipr)

    def update(self,ipr):
        self.updateSelf(ipr)
        self.updateShaper(ipr)
        pass


class PrioScheduler(ClassfulQdisc):
    def __init__(self, bandNum):
        super(PrioScheduler,self).__init__()
        self.mBandNum = bandNum
        for i in range(0, self.mBandNum):
            self.addClass(installed=True)

    def setInterface(self, interface):
        """
        Func desc
        """
        self.mInterface = interface
        for queue in self.mQueues:
            queue.mInterface = interface

        self.setInterfaceToFilters(interface)    
        pass
    
    def installSelf(self, ipr):
        ifid = self.mInterface.mIndex
        idx = self.mHandle.getHex()
        
        if self.isEgress:
            parentId = TC_H_ROOT
        else:
            parentId = self.mParent.getHex()

        try:
            ipr.tc(
                "add", 'prio', ifid, idx,
                parent=parentId,
                bands=self.mBandNum,
            )
        except NetlinkError as e:
            print("Could not set profile do interface: {0}".format(ifid))
        except Exception as e:
            print("Could not set profile do interface: {0}".format(ifid))
            raise

    def installQueues(self, ipr):
        ifid = self.mInterface.mIndex
        idx = self.mHandle.getHex()

        for queue in self.mQueues:
            queue.install(ipr)  
        pass

    def install(self, ipr):
        self.installSelf(ipr)
        self.installQueues(ipr)
        pass

class HtbClass(ClassfulQdisc, TcClass):
    def __init__(self, **kwargs):
        super(HtbClass,self).__init__()
        self.rate = kwargs.get('rate', None)
        self.ceil = kwargs.get('ceil', None)
        self.mQueue = None
        self.installed = False
        pass

    def addClass(self, htbClass):
        classMinorVal = self.mMinorHandleGen.GenerateValue()
        classHandle = Handle(self.mHandle.mMajor, classMinorVal)
        parentHandle = self.mHandle
        
        htbClass.mHandle = classHandle
        htbClass.mParent = parentHandle
        htbClass.mMinorHandleGen = self.mMinorHandleGen

        self.mClasses.append(htbClass)
        return htbClass

    def setQueue(self, queue):
        self.leaf = queue.mHandle
        parentHandle = self.mHandle
        queue.setParent(parentHandle)
        self.mQueue = queue
        return queue
    
    def setInterface(self, interface):
        self.mInterface = interface
        for tcClass in self.mClasses:
            tcClass.setInterface(interface)

        if self.mQueue:
            self.mQueue.mInterface = interface

    def installQueue(self, ipr):
        if self.mQueue:
            self.mQueue.install(ipr)

    def installTcClasses(self, ipr):
        for tcClass in self.mClasses:
            tcClass.install(ipr)

    def installSelf(self, ipr):
        ifid = self.mInterface.mIndex
        idx = self.mHandle.getHex()
        parentId = self.mParent.getHex()

        try:
            extra_args = {}
            extra_args.update({
                    'rate': (self.rate or (2**22 - 1)),
                    'ceil': (self.ceil or (2**22 - 1))
                    })
            #tc class add dev eth0 parent 1: classid 1:1 htb rate 100Mbit ceil 100Mbit
            ipr.tc(
                'add-class', 'htb', ifid, idx,
                parent=parentId,
                **extra_args
            )
        
        except NetlinkError as e:
            print("Could not install HTB Class to interface: {0}".format(ifid))
        except Exception as e:
            print("Could not install HTB Class to interface: {0}".format(ifid))
            raise

    def install(self, ipr):
        self.installed = True
        self.installSelf(ipr)
        self.installTcClasses(ipr)
        if self.mQueue:
            self.installQueue(ipr)

class HtbScheduler(ClassfulQdisc):
    def __init__(self, defaultClass = None):
        super(HtbScheduler,self).__init__()
        self.defaultClass = defaultClass
        pass

    def setDefaultClass(self, defaultClass):
        self.defaultClass = defaultClass
        return defaultClass

    def addClass(self, htbClass):
        classMinorVal = self.mMinorHandleGen.GenerateValue()
        classHandle = Handle(self.mHandle.mMajor, classMinorVal)
        parentHandle = Handle(self.mHandle.mMajor, 0)
        
        htbClass.mHandle = classHandle
        htbClass.mParent = parentHandle
        htbClass.mMinorHandleGen = self.mMinorHandleGen

        self.mClasses.append(htbClass)
        return htbClass

    def installSelf(self, ipr):
        ifid = self.mInterface.mIndex
        idx = self.mHandle.getHex()
        
        if self.isEgress:
            parentId = TC_H_ROOT
        else:
            parentId = self.mParent.getHex()

        try:
            extra_args = {}
            if not self.defaultClass:
                #TODO add default class handle
                extra_args.update({
                    'default': 0
                })
            else:
                extra_args.update({
                    'default': 0
                })
            ipr.tc(
                "add", 'htb', ifid, idx,
                parent=parentId,
                **extra_args
            )
            #tc qdisc add dev eth0 handle 1: root htb default 0
        except NetlinkError as e:
            print("Could not install HTB to interface: {0}".format(ifid))
        except Exception as e:
            print("Could not install HTB to interface: {0}".format(ifid))
            raise

    def installTcClasses(self, ipr):
        for tcClass in self.mClasses:
            if tcClass.installed is False:
                tcClass.install(ipr)
                tcClass.installed = True

    def install(self, ipr):
        self.installSelf(ipr)
        self.installTcClasses(ipr)
        pass

    def refresh(self, ipr):
        self.setInterface(self.mInterface)
        self.installTcClasses(ipr)
        self.installFilters(ipr)
        pass