#!/usr/bin/python

__author__ = 'P.Gawlowicz'

from pytc.TrafficControl import TrafficControl
from pytc.Qdisc import *
from pytc.Filter import *
import logging
import time, sys

"""
EU project WISHFUL
"""

if __name__ == '__main__':

    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=FORMAT)
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    log.warning('Test Traffic Control')

    operation = "del"
    if len(sys.argv) > 1:
        operation = str(sys.argv[1])

    tcMgr = TrafficControl()
    wlan0 = tcMgr.getInterface('wlan0')

    if operation == "add":
        prioSched = PrioScheduler(bandNum=4)

        pfifo1 = prioSched.addQueue(PfifoQueue(limit=50))
        bfifo2 = prioSched.addQueue(BfifoQueue(limit=20000))
        pfifo3 = prioSched.addQueue(SfqQueue(perturb=11))
        tbf4   = prioSched.addQueue(TbfQueue(rate=1000*1024, burst=1600, limit=10*1024))

        filter1 = Filter(name="BnControlTraffic");
        filter1.setFiveTuple(src=None, dst='192.168.1.178', prot='udp', srcPort=None, dstPort='5001')
        filter1.setTarget(pfifo1)
        filter1.setFilterPriority(1)
        filter1.setFlowId(5)
        filter1.setTos(Filter.VI)
        prioSched.addFilter(filter1)

        filter4 = Filter(name="Background");
        filter4.setFiveTuple(src='10.0.0.2', dst=None, prot='tcp', srcPort='21', dstPort=None)
        filter4.setTarget(tbf4)
        filter4.setFilterPriority(100)
        filter4.setFlowId(128)
        filter4.setTos(Filter.BE)
        prioSched.addFilter(filter4)

        wlan0.setEgressScheduler(prioSched)
    else:
        wlan0.clean()
        tcMgr.cleanIpTables()
        pass