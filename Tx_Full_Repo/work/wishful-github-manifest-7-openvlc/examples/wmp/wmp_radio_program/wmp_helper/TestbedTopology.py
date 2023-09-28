#!/usr/bin/python
__author__ = 'Pierluigi Gallo'
"""
EU project WISHFUL
"""
# from upis.upi_rn import UPI_RN
# from upis.upi_m import UPI_M
# from upis.upi_rn import UPI_RN
#
# from common.upihelper import from_unix_time, unix_time_as_tuple, get_now_full_second
# from helpers.application import ServerApplication, ClientApplication
# from helpers.mac_layer import EdcaQueueParameters
# from common.upihelper import Time
from controller.wishful_controller.node_manager import *
# from helpers.helper import NetworkFunctionHelper
# from helpers.helper import NetworkHelper, RadioHelper
# from functools import partial
from datetime import date, datetime, timedelta
import re
import time
import sys
import csv

class WiFiNode(Node):
    """
    This class defines an WiFi node and takes the most appropriate actions in order to :
        Set wireless lan interface ip address and network role (Station/AccessPoint)
        Stores/Removes low level measurements
        Store the low level measurements type
    """
    def __init__(self, node):
        """ Creates a new WiFiNode
        """
        super( WiFiNode, self ).__init__(node)
        eth_ipAddress_part = re.split(r'[:./\s]\s*', str(node))
        self.wlan_ipAddress = '192.168.3.' + eth_ipAddress_part[3]
        self.last_bunch_measurement = []
        self.measurement_types = []
        self.role = None
        self.platform = None

    def add_measure(self, measure):
        """ Adds a measure or a list of measurable in the list of node measurement
        :param measure: list of measure to add at last_bunch_measurement object attribute
        """
        self.last_bunch_measurement.append(measure)

    def get_available_measures(self):
        """ Gets the available measure of the node
        :return measure_list: the list of measure stored until now
        """
        return self.last_bunch_measurement


class TestbedTopology:
    """
    This class defines an experiment controller and takes the most appropriate actions in order to :
        Create the WiFiNode and Nodelist
        Setup the nodes roles (AP/STA)
        Setup the wireless network (Network create and station association)
        Managing the interface with WiSHFUL controller
    """

    def __init__(self, testbed_name, log):
        """ create a new testbed topology whose nodes belong to the same group
        """
        # name of the experiment group; only nodes of this group can be controlled
        self.exp_group_name=testbed_name
        self.log = log

        #used to save specific information for WiFi node
        self.wifi_ap_wmp_nodes = []
        self.wifinodes = [] #
        self.athnodes = [] #

        #used to run UPI function on node
        self.nodes = []     #
        self.ap_wmp_nodes = [] #
        self.wmp_nodes = []  #
        self.ath_nodes = []  #

        #used to save the total number of node present in the experiment
        self.experiment_nodes_number = 0
        self.wmp_nodes_number = 0
        self.ath_nodes_number = 0

    def setExperimentNodesNumber(self, nodes_number):
        # for ttilab testbed
        # 1 10.163.8.26     alix2     AP
        # 2 10.163.8.44     alix5     STA1
        # 3 10.163.8.57     alix7     STA2
        # 4 10.163.8.60     alix10    STA3
        # 5 10.163.8.69     alix11    STA4
        # 6 10.163.8.70     alix12    STA5
        # 7 10.163.8.71     alix13    STA6
        self.experiment_nodes_number = nodes_number
        return

    def getExperimentNodesNumber(self):
        return self.experiment_nodes_number


    def add_wmp_node(self, node, role):
        if role == 'AP':
            self.ap_wmp_nodes.append(node)
        elif role == 'STA':
            self.wmp_nodes.append(node)
        else:
            self.log.error('Error in node role : %s' % role)


    def setAP(self, node, essid):
        """ Creates infrastructure BSS, uses node such as Access Point
        :param node: elected Access Point Node
        :param essid: the SSID
        """
        # UPI_R function is execute immediately
        exec_time = None

        # eth_ipAddress_part = re.split(r'[:./\s]\s*', str(node))
        # wlan_ipAddress = '192.168.3.' + eth_ipAddress_part[6]
        # UPIfunc = UPI_M.initTest
        # UPIargs = {'interface' : 'wlan0', 'operation' : ['create-network'], 'ssid' : [essid], 'ip_address' : [wlan_ipAddress] }
        # try:
        #     rvalue = self.global_mgr.runAt(node, UPIfunc, UPIargs, exec_time)
        #     self.log.info('Ret value of blocking call is %s' % str(rvalue))
        # except Exception as e:
        #     self.log.fatal("An error occurred : %s" % e)
        #     return False

    def setSTA(self, node, essid):
        """ Associate node to infrastructure BSS

        :param node: elected station node by associate
        :param essid: the SSID
        """

        # # UPI_R function is execute immediately
        # exec_time = None
        #
        # eth_ipAddress_part = re.split(r'[:./\s]\s*', str(node))
        # wlan_ipAddress = '192.168.3.' + eth_ipAddress_part[6]
        # UPIfunc = UPI_M.initTest
        # UPIargs = {'interface' : 'wlan0', 'operation' : ['association'], 'ssid' : [essid], 'ip_address' : [wlan_ipAddress] }
        # try:
        #     rvalue = self.global_mgr.runAt(node, UPIfunc, UPIargs, exec_time)
        #     self.log.info('Ret value of blocking call is %s' % str(rvalue))
        # except Exception as e:
        #     self.log.fatal("An error occurred : %s" % e)
        #     return False

    def initializeTestbedFunctions(self, controller):
        """ Setups all the node in the experiment, executes the follow operation :
                installs the execution environment or execution engine
                restarts module and microcode
                executes the node role

        :return  result: True if the operation are successful execute, False otherwise
        """

        self.log.info(' %s - SETUP NODES' % self.initializeTestbedFunctions.__name__)

        # All the UPI functions are execute immediately
        # UPIargs = {'execution_engine' : ['runtime/connectors/wmp_linux/execution_engine/factory'] }
        # rvalue = controller.nodes(self.ap1).radio.iface("wlan0").install_execution_engine(UPIargs)
        # self.log.debug('Ret value of blocking call is %s' % str(rvalue))
        # UPIargs = {'interface' : 'wlan0', 'operation' : ['module'] }
        # rvalue = controller.nodes(self.ap1).radio.iface("wlan0").init_test(UPIargs)
        # self.log.debug('Ret value of blocking call is %s' % str(rvalue))

        #UPIargs = {'execution_engine' : ['../../../agent_modules/wifi_wmp/execution_engine/wmp'] }
        UPIargs = {'execution_engine' : ['../../../execution_engine/factory'] }
        rvalue = controller.nodes(self.wmp_nodes).radio.iface("wlan0").install_execution_engine(UPIargs)
        self.log.debug('Ret value of blocking call is %s' % str(rvalue))
        UPIargs = {'interface' : 'wlan0', 'operation' : ['module'] }
        rvalue = controller.nodes(self.wmp_nodes).radio.iface("wlan0").init_test(UPIargs)
        self.log.debug('Ret value of blocking call is %s' % str(rvalue))

        self.log.debug('ath_nodes_number : %s - wmp_nodes_number : %s' % (str(self.ath_nodes_number), str(self.wmp_nodes_number) ) )
        self.log.debug('len ath_nodes_number : %s - len wmp_nodes_number : %s' % (str(len(self.athnodes)), str(len(self.wifinodes) ) ) )

        # self.setAP(self.ap1, self.exp_group_name)
        # node_index = 0
        # while node_index < self.wmp_nodes_number :
        #     self.setSTA(self.wifinodes[node_index], self.exp_group_name)
        #     node_index += 1
        #
        # self.log.warning('Configure EDCA parameters for each hardware queue in wireless card (Atheros AR928X)')
        # # queueParam0 = EdcaQueueParameters(aifs=1,  cwmin=1,  cwmax=3,  txop=900)
        # # queueParam1 = EdcaQueueParameters(aifs=50, cwmin=15, cwmax=63, txop=4)
        # # queueParam2 = EdcaQueueParameters(aifs=55, cwmin=63, cwmax=127, txop=2)
        # # queueParam3 = EdcaQueueParameters(aifs=123, cwmin=127, cwmax=511, txop=0)
        # queueParam0 = EdcaQueueParameters(aifs=3,  cwmin=30,  cwmax=30,  txop=1)
        # queueParam1 = EdcaQueueParameters(aifs=3, cwmin=30, cwmax=30, txop=1)
        # queueParam2 = EdcaQueueParameters(aifs=3, cwmin=30, cwmax=30, txop=1)
        # queueParam3 = EdcaQueueParameters(aifs=3, cwmin=30, cwmax=30, txop=1)
        #
        # node_index = 0
        # while node_index < self.ath_nodes_number :
        #     self.setSTA(self.athnodes[node_index], self.exp_group_name)
        #
        #     self.radioHelper.setEdcaParameters(self.athnodes[node_index], ifname='wlan0', queueId=0, qParam=queueParam0)
        #     self.radioHelper.setEdcaParameters(self.athnodes[node_index], ifname='wlan0', queueId=1, qParam=queueParam1)
        #     self.radioHelper.setEdcaParameters(self.athnodes[node_index], ifname='wlan0', queueId=2, qParam=queueParam2)
        #     self.radioHelper.setEdcaParameters(self.athnodes[node_index], ifname='wlan0', queueId=3, qParam=queueParam3)
        #
        #     qParams = self.radioHelper.getEdcaParameters(self.athnodes[node_index], ifname='wlan0')
        #     self.radioHelper.printEdcaParameters(self.athnodes[node_index], ifname='wlan0', qParam=qParams)
        #     node_index += 1

        return True
