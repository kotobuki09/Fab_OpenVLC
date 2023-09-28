import logging
import threading
import _thread
import stream

from .elements import FilterContainter, PeakDetectorObj, MovAvgFilterObj, ActionObject, MatchObject
from .generators import UpiEventGenerator, PacketGenerator
from .packet_sniffer import MyPktSink
from wishful_framework import CmdDesc, Permanance


__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz}@tkn.tu-berlin.de"


class Rule(threading.Thread):
    def __init__(self, agent, ruleManager, ruleId, ruleDesc, name):
        super(Rule, self).__init__(name=name)
        self.log = logging.getLogger('Rule')
        self.agent = agent
        self.ruleManager = ruleManager
        self.id = ruleId
        self.ruleDesc = ruleDesc

        self.myGen = None
        self.filterContainter = None
        self.match = None
        self.action = None
        self.notify_ctrl = False
        self.permanence = Permanance.PERSISTENT
        self.sink = None
        self.calledAsGenerator = False

        self.LocalControllerId = None

        if "filters" in ruleDesc and ruleDesc["filters"]:
            self.filterContainter = FilterContainter()
            for f in ruleDesc["filters"]:
                if f.filter_type == "MovAvgFilter":
                    myFilter = MovAvgFilterObj(f.window_size)
                    self.filterContainter.add_filter(myFilter)
                elif f.filter_type == "PeakDetector":
                    myFilter = PeakDetectorObj(f.threshold)
                    self.filterContainter.add_filter(myFilter)
        
        if "match" in ruleDesc and ruleDesc["match"]:
            self.match = MatchObject(ruleDesc["match"])

        if "action" in ruleDesc and ruleDesc["action"]:
            self.action = ActionObject(agent, ruleDesc["action"])

        if "notify_ctrl" in ruleDesc and ruleDesc["notify_ctrl"]:
            self.notify_ctrl = True

        if "permanence" in ruleDesc:
            self.permanence = ruleDesc["permanence"]

        if "generator" in ruleDesc:
            self.calledAsGenerator = ruleDesc["generator"]

        #check if local control program
        if "LocalControllerId" in ruleDesc:
            self.LocalControllerId = ruleDesc["LocalControllerId"]


    def _notify_ctrl(self, sample):
        if self.LocalControllerId:
            dest = self.LocalControllerId
        else:
            dest = "controller"

        cmdDesc = CmdDesc()
        if self.calledAsGenerator:
            cmdDesc.type = "wishful_generator"
            cmdDesc.func_name = "wishful_generator"
        else:
            cmdDesc.type = "wishful_rule"
            cmdDesc.func_name = "wishful_rule"

        cmdDesc.call_id = str(0)
        cmdDesc.serialization_type = CmdDesc.PICKLE
        msg = sample

        encapsulatedMsg = {"node_uuid":self.agent.uuid, "rule_id":self.id, "msg":msg}
        msgContainer = [dest, cmdDesc, encapsulatedMsg]
        self.agent.send_upstream(msgContainer, self.LocalControllerId)


    def stop(self):
        if self.sink:
            self.sink.stop()
            [0,1,2,3,4] >> stream.smap(lambda x: x) >> self.sink
        self.myGen.stop()


    def run( self ):
        self.log.info("Start rule".format())
        if self.permanence == Permanance.TRANSIENT:
          self.sink = stream.item[:1]
        else:
          self.sink = stream.Sink()

        nop = stream.smap(lambda x: x)
        elements = [nop, nop, nop, nop, nop]

        if self.filterContainter:
            elements[0] = stream.smap(lambda x: self.filterContainter(x))

        #remove None value from pipline
        elements[1] = stream.sfilter(lambda x: True if x is not None else False)

        if self.match:
            elements[2] = stream.sfilter(lambda x: self.match(x))

        if self.action:
            elements[3] = stream.smap(lambda x: self.action(x))

        if self.notify_ctrl:
            elements[4] = stream.smap(self._notify_ctrl)

        eventGenerator = self.myGen()
        try:
            eventGenerator >> elements[0] >> elements[1] >> elements[2] >> elements[3] >> elements[4] >> self.sink
        except Exception as e:
            self.log.debug("Rule exits, reason: {}".format(e))

        #if TRANSIENT stop generator
        self.myGen.stop()
        #call next one more time to finalize generator
        try:
            next(eventGenerator)
        except:
            pass
        self.sink.stop()
        self.log.info("Rule exits".format())
        self.log.info("Active Threads:{}".format(threading.active_count()))
        _thread.exit()


class UpiRule(Rule):
    def __init__(self, agent, ruleManager, ruleId, ruleDesc):
        super(UpiRule, self).__init__(agent, ruleManager, ruleId, ruleDesc, name="UpiRule")
        self.log = logging.getLogger('UpiRule')

        self.myGen = UpiEventGenerator(agent, ruleDesc["event"])


class PktRule(Rule):
    def __init__(self, agent, ruleManager, ruleId, ruleDesc):
        super(PktRule, self).__init__(agent, ruleManager, ruleId, ruleDesc, name="PktRule")
        self.log = logging.getLogger('PktRule')

        self.iface = None
        self.selector = None
        self.pktMatch = None

        self.event = ruleDesc["event"]
        self.iface = self.event.iface

        if "pktMatch" in ruleDesc and ruleDesc["pktMatch"]:
            pktMatch = ruleDesc["pktMatch"]
            self.pktMatch = pktMatch.matchStr

        if "selector" in ruleDesc and ruleDesc["selector"]:
            selector = ruleDesc["selector"]
            self.selector = selector.field

        #get sniffer
        self.log.info("Get sniffer for interface: {} and filter: {}".format(self.iface, self.pktMatch))
        self.pktSniffer = self.ruleManager.get_pkt_sniffer(self.iface, self.pktMatch)

        self.myGen = PacketGenerator(iface=self.iface, pfilter=self.pktMatch, field_selector=self.selector)
        sinkName = "{}:{}".format(self.iface, self.pktMatch)
        self.myPktSink = MyPktSink(name=sinkName, field_selector=None, callback=self.myGen.pkt_recv_callback)
        self.pktSniffer.add_sink(self.myPktSink)

    def stop(self):
        super(PktRule, self).stop()
        self.pktSniffer.remove_sink(self.myPktSink)
