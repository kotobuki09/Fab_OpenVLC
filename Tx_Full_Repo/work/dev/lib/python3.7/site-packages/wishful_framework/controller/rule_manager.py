import logging
from wishful_framework import TimeEvent, PktEvent, MovAvgFilter, PeakDetector, Match, Action, Permanance

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


class RuleDescriptor(object):
    def __init__(self, ruleManager, agentUuid, ruleId, event, filters=[], match=None, action=None, permanence=Permanance.PERSISTENT, ctrl_cb=None):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))
        self.agentUuid = agentUuid
        self.id = ruleId
        self.ruleManager = ruleManager
        self.event = event
        self.filters = filters
        self.match = match
        self.action = action
        self.permanence = permanence
        self.ctrl_cb = ctrl_cb

    def remove(self):
        return self.ruleManager.remove(self.id, self.agentUuid)


class RuleManager(object):
    def __init__(self, controller):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))

        self.controller = controller
        self.ruleIdGen = 0
        
        self.rules_by_node = {}


    def generate_new_rule_id(self):
        self.ruleIdGen = self.ruleIdGen + 1
        return self.ruleIdGen

    def _receive(self, group, node, msg):
        node_uuid = msg["node_uuid"]
        rule_id = msg["rule_id"]
        msg = msg["msg"]

        node_rules = []
        if node_uuid in self.rules_by_node:
            node_rules = self.rules_by_node[node_uuid]

        myRule = None
        for rule in node_rules:
            if rule_id == rule.id:
                myRule = rule
                break

        if myRule:
            myRule.ctrl_cb(group, node, rule_id, msg)


    def add(self, event, pktMatch=None, selector=None, filters=[], match=None, action=None, permanence=Permanance.PERSISTENT, ctrl_callback=None):
        self.log.debug("Adding new rule to node".format())

        destNode = self.controller._scope
        destNode = self.controller.nodeManager.get_node_by_str(destNode)
        destNodeUuid = destNode.id

        notify_ctrl = False
        if ctrl_callback:
            notify_ctrl = True

        #TODO: improve serialization
        rule = {"event":event, "pktMatch":pktMatch, "selector":selector, "filters":filters, 
                "match":match, "action":action, "permanence":permanence, "notify_ctrl":notify_ctrl}

        rule_id = self.controller.blocking(True).mgmt.add_rule(rule)
        descriptor = RuleDescriptor(self, destNodeUuid, rule_id, event, filters, match, action, permanence, ctrl_callback)

        if destNodeUuid in self.rules_by_node:
            self.rules_by_node[destNodeUuid].append(descriptor)
        else:
            self.rules_by_node[destNodeUuid] = [descriptor]

        return descriptor


    def remove(self, ruleId, agentUuid=None):
        self.log.debug("remove rule with id: {}".format(ruleId))

        if agentUuid in self.rules_by_node:
            myRule = None
            for rule in self.rules_by_node[agentUuid]:
                if ruleId == rule.id:
                    myRule = rule
                    break
            if myRule:
                self.rules_by_node[agentUuid].remove(myRule)
                del myRule

        if agentUuid:
            retVal = self.controller.blocking(True).node(agentUuid).mgmt.delete_rule(ruleId)
        else:
            retVal = self.controller.blocking(True).mgmt.delete_rule(ruleId)
        return retVal



class LocalRuleDescriptor(object):
    def __init__(self, ruleManager, ruleId, event, filters=[], match=None, action=None, permanence=Permanance.PERSISTENT, ctrl_cb=None):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))
        self.id = ruleId
        self.ruleManager = ruleManager
        self.event = event
        self.filters = filters
        self.match = match
        self.action = action
        self.permanence = permanence
        self.ctrl_cb = ctrl_cb

    def remove(self):
        return self.ruleManager.remove(self.id)


class LocalRuleManager(object):
    def __init__(self, controller):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))

        self.controller = controller
        self.ruleIdGen = 0
        self.rules = []

    def generate_new_rule_id(self):
        self.ruleIdGen = self.ruleIdGen + 1
        return self.ruleIdGen

    def _receive(self, msg):
        node_uuid = msg["node_uuid"]
        rule_id = msg["rule_id"]
        msg = msg["msg"]

        myRule = None
        for rule in self.rules:
            if rule_id == rule.id:
                myRule = rule
                break

        if myRule:
            myRule.ctrl_cb(rule_id, msg)


    def add(self, event, pktMatch=None, selector=None, filters=[], match=None, action=None, permanence=Permanance.PERSISTENT, ctrl_callback=None):
        self.log.debug("Adding new rule to node".format())

        notify_ctrl = False
        if ctrl_callback:
            notify_ctrl = True

        rule = {"event":event, "pktMatch":pktMatch, "selector":selector, "filters":filters, 
                "match":match, "action":action, "permanence":permanence, "notify_ctrl":notify_ctrl,
                "LocalControllerId":self.controller.id}

        rule_id = self.controller.blocking(True).mgmt.add_rule(rule)
        descriptor = LocalRuleDescriptor(self, rule_id, event, filters, match, action, permanence, ctrl_callback)
        self.rules.append(descriptor)

        return descriptor


    def remove(self, ruleId):
        self.log.debug("remove rule with id: {}".format(ruleId))

        myRule = None
        for rule in self.rules:
            if ruleId == rule.id:
                myRule = rule
                break

        if myRule:
            self.rules.remove(myRule)
            del myRule

        retVal = self.controller.blocking(True).mgmt.delete_rule(ruleId)
        return retVal