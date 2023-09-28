#!/usr/bin/python
__author__ = 'Pierluigi Gallo'
"""
EU project WISHFUL
"""
from controller.wishful_controller.node_manager import *
from datetime import date, datetime, timedelta
import re
import time
import sys
import csv

sys.path.append('../../../../')
sys.path.append("../../../../agent_modules/wifi_ath")
sys.path.append("../../../../agent_modules/wifi_wmp")
sys.path.append("../../../../agent_modules/wifi")
sys.path.append('../../../../upis')
sys.path.append('../../../../framework')
sys.path.append('../../../../agent')
sys.path.append('../../../../controller')

class WiFiNode():
    """
    This class defines an WiFi node and takes the most appropriate actions in order to :
        Set wireless lan interface ip address and network role (Station/AccessPoint)
        Stores/Removes low level measurements
        Store the low level measurements type
    """
    def __init__(self, node):
        """ Creates a new WiFiNode
        """
        self.node = node
        # eth_ipAddress_part = re.split(r'[:./\s]\s*', str(node))
        # self.wlan_ipAddress = '192.168.3.' + eth_ipAddress_part[3]
        self.wlan_ipAddress = '192.168.3.' + str(node.ip[7:10])
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

    def __init__(self, testbed_name, log, controller):
        """ create a new testbed topology whose nodes belong to the same group
        """
        # name of the experiment group; only nodes of this group can be controlled
        self.exp_group_name=testbed_name
        self.log = log
        self.controller = controller

        #used to save specific information for WiFi node
        self.wifinodes = [] #

        #used to run UPI function on node
        self.nodes = []     #
        #self.ap_node
        self.wmp_nodes = []  #
        self.ath_nodes = []  #
        self.legacy_nodes = []  #

        #used to save the total number of node present in the experiment
        self.experiment_nodes_number = 0
        self.wmp_nodes_number = 0
        self.ath_nodes_number = 0
        self.legacy_nodes_number = 0

        self.iface = "wlan0"

    def add_discovered_node(self, node):
        self.nodes.append(node)

    def getExperimentNodesNumber(self):
        with open('testbed_nodes.csv') as csvfile:
            reader = csv.DictReader(filter(lambda row: row[0]!='#', csvfile))
            for row in reader:
                self.experiment_nodes_number += 1
        return self.experiment_nodes_number

    def initializeTestbedTopology(self):
        """ Initializes testbed setup one AP and one STA
        """
        #get available nodes on testbed
        nodes_ip_list = []
        nodes_role_list = []
        nodes_platform_list = []
        with open('testbed_nodes.csv') as csvfile:
            #reader = csv.DictReader(csvfile)
            reader = csv.DictReader(filter(lambda row: row[0]!='#', csvfile))
            for row in reader:
                for ii in range(0, len(self.nodes)):
                    if self.nodes[ii].ip == row['ip']:
                        nodes_ip_list.append(row['ip'])
                        nodes_role_list.append(row['role'])
                        nodes_platform_list.append(row['platform'])

                        if row['role'] == 'AP':
                            self.ap_node = self.nodes[ii]

                        if row['platform'] == 'wmp' and row['role'] != 'AP':
                            self.wmp_nodes.append(self.nodes[ii])
                            self.wmp_nodes_number += 1

                        if row['platform'] == 'ath' and row['role'] != 'AP':
                            self.ath_nodes.append(self.nodes[ii])
                            self.ath_nodes_number += 1

                        if row['platform'] == 'legacy' and row['role'] != 'AP':
                            self.legacy_nodes.append(self.nodes[ii])
                            self.legacy_nodes_number += 1

                        if row['platform'] == 'ath' or row['platform'] == 'wmp' or row['platform'] == 'legacy' or row['role'] == 'AP':
                            self.wifinodes.append(WiFiNode(self.nodes[ii]))

        self.log.debug('ath_nodes_number : %s - wmp_nodes_number : %s - legacy_nodes_number : %s' % (str(len(self.ath_nodes)), str(len(self.wmp_nodes)), str(len(self.legacy_nodes)) ) )
        self.log.debug('len wifinodes : %s' % (str(len(self.wifinodes) ) ) )


        """ Check if all expected nodes are present in the testbed
        """
        # if experiment_nodes_number != testbed_node_number :
        #         return FAILURE

    def initializeTestbedFunctions(self, controller):
        """ Setups all the node in the experiment, executes the follow operation :
                installs the execution environment or execution engine
                restarts module and microcode
                executes the node role

        :return  result: True if the operation are successful execute, False otherwise
        """

        self.setAP(self.ap_node, self.exp_group_name)

        # node_index = 0
        # while node_index < self.wmp_nodes_number :
        #     connected = self.setSTA(self.wmp_nodes[node_index], self.exp_group_name)
        #     print('Node %s connected %s' % (str( self.wmp_nodes[node_index].ip), str(connected) ))
        #     node_index += 1

        for node in self.wmp_nodes:
            connected = self.setSTA(node, self.exp_group_name)
            print('Node %s connected %s' % (str( node.ip), str(connected) ))

        for node in self.legacy_nodes:
            connected = self.setSTA(node, self.exp_group_name)
            print('Node %s connected %s' % (str( node.ip), str(connected) ))

        for node in self.ath_nodes:
            connected = self.setSTA(node, self.exp_group_name)
            print('Node %s connected %s' % (str( node.ip), str(connected) ))

        return True

    def setAP(self, node, essid):
        """ Creates infrastructure BSS, uses node such as Access Point
        :param node: elected Access Point Node
        :param essid: the SSID
        """
        wlan_ipAddress = '192.168.3.' + node.ip.split('.')[3]

        #stop hostpad
        rvalue = self.controller.nodes(node).net.stop_hostapd()
        #set ip address
        rvalue = self.controller.nodes(node).net.set_ip_address(self.iface, wlan_ipAddress)
        #set hostapd configuration
        rvalue = self.controller.nodes(node).net.set_hostapd_conf(self.iface, './wmp_helper/hostapd.conf', 6, essid)
        #start hostapd
        rvalue = self.controller.nodes(node).net.start_hostapd('./wmp_helper/hostapd.conf')
        #set power
        rvalue = self.controller.nodes(node).radio.set_tx_power(15)
        #set modulation rate
        #rvalue = self.controller.nodes(node).radio.set_modulation_rate(2)
        rvalue = self.controller.nodes(node).radio.set_modulation_rate(24)


    def setSTA(self, node, essid):
        """ Associate node to infrastructure BSS
        :param node: elected station node by associate
        :param essid: the SSID
        """
        # eth_ipAddress_part = re.split(r'[:./\s]\s*', str(node))
        # wlan_ipAddress = '192.168.3.' + eth_ipAddress_part[6]
        wlan_ipAddress = '192.168.3.' + node.ip.split('.')[3]

        #stop hostpad
        rvalue = self.controller.nodes(node).net.stop_hostapd()
        #set ip address
        rvalue = self.controller.nodes(node).net.set_ip_address(self.iface, wlan_ipAddress)
        #set power
        rvalue = self.controller.nodes(node).radio.set_tx_power(15)
        #set modulation rate
        #rvalue = self.controller.nodes(node).radio.set_modulation_rate(2)
        rvalue = self.controller.nodes(node).radio.set_modulation_rate(24)
        connected = False
        for ii in range(10):
            #associate station
            rvalue = self.controller.nodes(node).net.connect_to_network(self.iface, essid)
            time.sleep(2)
            #dump connection
            rvalue = self.controller.nodes(node).net.network_dump(self.iface)
            #self.log.debug('dump connection :\n%s\n'  % (str(rvalue) ))
            flow_info_lines = rvalue.rstrip().split('\n')
            if flow_info_lines[0][0:9] == "Connected" :
                connected = True
                break

        return connected