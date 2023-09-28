import logging

from .rule import UpiRule, PktRule
from .packet_sniffer import PacketSniffer
import wishful_upis as upis
import wishful_framework as wishful_module


__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz}@tkn.tu-berlin.de"


@wishful_module.build_module
class RuleManagerModule(wishful_module.AgentModule):
    def __init__(self):
        super(RuleManagerModule, self).__init__()
        self.log = logging.getLogger('RuleManagerModule')

        self.ruleIdGen = 0
        self.rules = {}

        #sniffer contains iface and filter
        self.activePacketSniffers = []

        #list of active UPI generators per (iface, module, upi)
        self.activeUpiGenerators = []


    def get_pkt_sniffer(self, iface, pfilter):
        #check if packet sniffer with specific iface and filter exist, if not create one
        mySniffer = None
        for sniffer in self.activePacketSniffers:
            if iface == sniffer.iface and pfilter == sniffer.filter:
                self.log.info("Take existing sniffer for iface: {} and filer: {}".format(iface, pfilter))
                mySniffer = sniffer
                break

        if not mySniffer:
            self.log.info("Create new sniffer for iface: {} and filer: {}".format(iface, pfilter))
            mySniffer = PacketSniffer(iface=iface, pfilter=pfilter)
            self.activePacketSniffers.append(mySniffer)

        return mySniffer


    def remove_pkt_sniffer(self, sniffer):
        if sniffer in self.activePacketSniffers:
            self.activePacketSniffers.remove(sniffer)


    def generate_new_rule_id(self):
        self.ruleIdGen = self.ruleIdGen + 1
        return self.ruleIdGen


    @wishful_module.bind_function(upis.mgmt.add_rule)
    def add_rule(self, ruleDesc):
        ruleId = self.generate_new_rule_id()
        self.log.info("Add rule with ID: {}".format(ruleId))

        newRule = None
        event = ruleDesc["event"]
        if event.type == "TimeEvent":
            newRule = UpiRule(self.agent, self, ruleId, ruleDesc)
            newRule.setDaemon(True)
            newRule.start()
        elif event.type == "PktEvent":
            newRule = PktRule(self.agent, self, ruleId, ruleDesc)
            newRule.setDaemon(True)
            newRule.start()
        else:
            self.log.debug("Event Type not supported: {}".format(event.type))

        if newRule:
            self.rules[ruleId] = newRule
            return ruleId


    @wishful_module.bind_function(upis.mgmt.delete_rule)
    def delete_rule(self, ruleId):
        self.log.info("Delete rule with ID: {}".format(ruleId))
        if ruleId in self.rules:
            rule = self.rules[ruleId]
            rule.stop()
            del self.rules[ruleId]
            return "REMOVED"

        return "NOT_FOUND"


    @wishful_module.on_exit()
    @wishful_module.on_disconnected()
    def remove_all_rules(self):
        self.log.info("Remove all rules".format())
        for ruleId, rule in self.rules.items():
           rule.stop()
        self.rules = {}