import os
import logging
import random
import subprocess
import inspect
import fcntl, socket, struct
import netifaces as ni
from datetime import date, datetime

import copy
import iptc
from pytc.TrafficControl import TrafficControl
from pytc.Profile import Profile
from pytc.Filter import FlowDesc
import pytc.Qdisc
import pytc.Filter

import wishful_upis as upis
import wishful_framework as wishful_module
from wishful_framework.classes import exceptions
from wishful_framework.upi_arg_classes.flow_id import FlowId
from wishful_framework.upi_arg_classes.iptables import SimpleMatch, SimpleTarget, SimplePolicy, SimpleRule, SimpleChain, SimpleTable

__author__ = "Piotr Gawlowicz, A.Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, zubow}@tkn.tu-berlin.de"


@wishful_module.build_module
class NetworkModule(wishful_module.AgentModule):
    def __init__(self):
        super(NetworkModule, self).__init__()
        self.log = logging.getLogger('NetworkModule')


    @wishful_module.bind_function(upis.net.get_iface_hw_addr)
    def get_iface_hw_addr(self, iface):

        self.log.info('getHwAddr() called {}'.format(iface))
        retVal = ni.ifaddresses(iface)[ni.AF_LINK]
        #retVal = list(retVal[0].values())[1]
        retVal = retVal[0]
        retVal = retVal['addr']
        return retVal


    @wishful_module.bind_function(upis.net.get_iface_ip_addr)
    def get_iface_ip_addr(self, iface):
        """Interfaces may have multiple addresses, return a list with all addresses
        """
        #ip = ni.ifaddresses(iface)[2][0]['addr'] #this will return only the first ip address
        #return ip
        
        #this returns a list with all ip addresses
        ipList = [inetaddr['addr'] for inetaddr in ni.ifaddresses(iface)[ni.AF_INET]] 
        return ipList


    @wishful_module.bind_function(upis.net.change_routing)
    def change_routing(self, servingAP_ip_addr, targetAP_ip_addr, sta_ip_addr):

        # IPDB has a simple yet useful routing management interface.
        # To add a route, one can use almost any syntax::
        # pass spec as is
        # r = self.ip.routes.get('192.168.5.0/24')
        r = self.ip.routes.get(sta_ip_addr + '/32')
        if not r.gateway:
            self.log.info("Currently no gateway found, creating it...")
            self.ip.routes.add(dst=sta_ip_addr + '/32', gateway=targetAP_ip_addr).commit()
        else:
            self.log.info("Old gateway = %s for %s" % (r.gateway, sta_ip_addr))

            if (r.gateway.startswith(servingAP_ip_addr) or r.gateway.startswith(targetAP_ip_addr)):
                r.remove()

            self.ip.routes.add(dst=sta_ip_addr + '/32', gateway=targetAP_ip_addr).commit()

            r = self.ip.routes.get(sta_ip_addr + '/32')
            self.log.info("New gateway = %s for %s" % (r.gateway, sta_ip_addr))

        return True


    @wishful_module.bind_function(upis.net.set_ARP_entry)
    def set_ARP_entry(self, iface, mac_addr, ip_addr):
        """
            Manipulates the local ARP cache.
            todo: use Netlink API
        """
        try:
            [rcode, sout, serr] = self.run_command('sudo arp -s ' + ip_addr + ' -i '+ iface + ' ' + mac_addr)
            return sout
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))


    @wishful_module.bind_function(upis.net.set_netem_profile)
    def setProfile(self, iface, profile):
        self.log.debug('set_profile on interface: {}'.format(iface))

        tcMgr = TrafficControl()
        intface = tcMgr.getInterface(iface)
        intface.setProfile(profile)
        return "OK"


    @wishful_module.bind_function(upis.net.update_netem_profile)
    def updateProfile(self, iface, profile):
        self.log.debug('updateProfile on interface: {}'.format(iface))

        tcMgr = TrafficControl()
        intface = tcMgr.getInterface(iface)
        intface.updateProfile(profile)
        return "OK"


    @wishful_module.bind_function(upis.net.remove_netem_profile)
    def removeProfile(self, iface):
        self.log.debug('removeProfile on interface: {}'.format(iface))

        tcMgr = TrafficControl()
        intface = tcMgr.getInterface(iface)
        intface.clean()
        return "OK"


    @wishful_module.bind_function(upis.net.set_per_link_netem_profile)
    def setPerLinkProfile(self, iface, dstIpAddr, profile):
        self.log.debug('setPerLinkProfile on interface: {}'.format(iface))

        tcMgr = TrafficControl()
        intface = tcMgr.getInterface(iface)
        intface.setPerLinkProfile(profile, dstIpAddr)
        return "OK"


    @wishful_module.bind_function(upis.net.remove_per_link_netem_profile)
    def removePerLinkProfile(self, iface, dstIpAddr):
        self.log.debug('removePerLinkProfile on interface: {}'.format(iface))

        tcMgr = TrafficControl()
        intface = tcMgr.getInterface(iface)
        intface.cleanPerLinkProfile(dstIpAddr)
        return "OK"


    @wishful_module.bind_function(upis.net.update_per_link_netem_profile)
    def updatePerLinkProfile(self, iface, dstIpAddr, profile):
        self.log.debug('updatePerLinkProfile on interface: {}'.format(iface))

        tcMgr = TrafficControl()
        intface = tcMgr.getInterface(iface)
        intface.updatePerLinkProfile(profile, dstIpAddr)
        return "OK"


    @wishful_module.bind_function(upis.net.install_egress_scheduler)
    def installEgressScheduler(self, iface, scheduler):
        self.log.debug('installEgressScheduler on interface: {}'.format(iface))

        tcMgr = TrafficControl()
        intface = tcMgr.getInterface(iface)
        intface.setEgressScheduler(scheduler)
        return "OK"


    @wishful_module.bind_function(upis.net.remove_egress_scheduler)
    def removeEgressScheduler(self, iface):
        self.log.debug('removeEgressScheduler on interface: {}'.format(iface))

        tcMgr = TrafficControl()
        intface = tcMgr.getInterface(iface)
        intface.clean()
        tcMgr.cleanIpTables()
        return "OK"


    @wishful_module.bind_function(upis.net.clear_nf_tables)
    def clearIpTables(self, table="ALL", chain="ALL"):
        self.log.debug('clearIpTables'.format())

        tables = []
        chains = {}

        if table == "ALL":
            tables = ["raw", "mangle", "nat", "filter"]
        else:
            if not isinstance(table, list):
                table = [table]
            tables.extend(table)

        if chain == "ALL":
            chains["filter"] = ["INPUT","FORWARD","OUTPUT"]
            chains["nat"] = ["PREROUTING", "OUTPUT", "POSTROUTING"]
            chains["mangle"] = ["PREROUTING", "OUTPUT", "INPUT", "FORWARD", "POSTROUTING"]
            chains["raw"] = ["PREROUTING", "OUTPUT"]
        else:
            if not isinstance(chain, list):
                chain = [chain]
            chains[tables[0]].extend(chain)

        for tableName in tables:
            for chainName in chains[tableName]:
                chain = iptc.Chain(iptc.Table(tableName), chainName)
                chain.flush()

        return "OK"


    @wishful_module.bind_function(upis.net.get_nf_table)
    def getIpTable(self, tableName):
        self.log.debug('getIpTable'.format())

        #exec embedded function
        table = iptc.Table(tableName)
        #refresh table to get current counters
        table.refresh()
        #create simple table (ie. without pointers to ctypes)
        simpleTable = SimpleTable(table)
        return simpleTable

    @wishful_module.bind_function(upis.net.set_pkt_marking)
    def setMarking(self, flowId, markId=None, table="mangle", chain="POSTROUTING"):
        self.log.debug('setMarking'.format())

        if not markId:
            tcMgr = TrafficControl()
            markId = tcMgr.generateMark()

        rule = iptc.Rule()

        if flowId.srcAddress:
            rule.src = flowId.srcAddress

        if flowId.dstAddress:
            rule.dst = flowId.dstAddress

        if flowId.prot:
            rule.protocol = flowId.prot
            match = iptc.Match(rule, flowId.prot)

            if flowId.srcPort:
                match.sport = flowId.srcPort

            if flowId.dstPort:
                match.dport = flowId.dstPort

            rule.add_match(match)

        target = iptc.Target(rule, "MARK")
        target.set_mark = str(markId)
        rule.target = target
        chain = iptc.Chain(iptc.Table(table), chain)
        chain.insert_rule(rule)
        return markId


    @wishful_module.bind_function(upis.net.del_pkt_marking)
    def delMarking(self, flowId, markId, table="mangle", chain="POSTROUTING"):
        #TODO: store table and chain per flowId/mark in set_pkt_marking,
        #it should be possible to remove marking only with flowId/markId
        self.log.debug('delMarking'.format())

        rule = iptc.Rule()

        if flowId.srcAddress:
            rule.src = flowId.srcAddress

        if flowId.dstAddress:
            rule.dst = flowId.dstAddress

        if flowId.prot:
            rule.protocol = flowId.prot
            match = iptc.Match(rule, flowId.prot)

            if flowId.srcPort:
                match.sport = flowId.srcPort

            if flowId.dstPort:
                match.dport = flowId.dstPort

            rule.add_match(match)

        target = iptc.Target(rule, "MARK")
        target.set_mark = str(markId)
        rule.target = target
        chain = iptc.Chain(iptc.Table(table), chain)
        chain.delete_rule(rule)
        return "OK"


    @wishful_module.bind_function(upis.net.set_ip_tos)
    def setTos(self, flowId, tos, table="mangle", chain="POSTROUTING"):
        self.log.debug('setTos'.format())

        rule = iptc.Rule()

        if flowId.srcAddress:
            rule.src = flowId.srcAddress

        if flowId.dstAddress:
            rule.dst = flowId.dstAddress

        if flowId.prot:
            rule.protocol = flowId.prot
            match = iptc.Match(rule, flowId.prot)

            if flowId.srcPort:
                match.sport = flowId.srcPort

            if flowId.dstPort:
                match.dport = flowId.dstPort

            rule.add_match(match)

        target = iptc.Target(rule, "TOS")
        target.set_tos = str(tos)
        rule.target = target
        chain = iptc.Chain(iptc.Table(table), chain)
        chain.insert_rule(rule)
        return "OK"


    @wishful_module.bind_function(upis.net.del_ip_tos)
    def delTos(self, flowId, tos, table="mangle", chain="POSTROUTING"):
        #TODO: store table and chain per flowId/mark in set_pkt_marking,
        #it should be possible to remove marking only with flowId/markId
        self.log.debug('delTos'.format())

        rule = iptc.Rule()

        if flowId.srcAddress:
            rule.src = flowId.srcAddress

        if flowId.dstAddress:
            rule.dst = flowId.dstAddress

        if flowId.prot:
            rule.protocol = flowId.prot
            match = iptc.Match(rule, flowId.prot)

            if flowId.srcPort:
                match.sport = flowId.srcPort

            if flowId.dstPort:
                match.dport = flowId.dstPort

            rule.add_match(match)

        target = iptc.Target(rule, "TOS")
        target.set_tos = str(tos)
        rule.target = target
        chain = iptc.Chain(iptc.Table(table), chain)
        chain.delete_rule(rule)
        return "OK"
