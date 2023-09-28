#!/usr/bin/python

__author__ = "Domenico Garlisi"
__copyright__ = "Copyright (c) 2016, CNIT"
__version__ = "0.1.0"
__email__ = "domenico.garlisi@cnit.it"

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
sys.path.append("../../../../agent_modules/net_linux")

# To enable / disable comments 
VERBOSE = False

class WiFiNode():
    """
    This class defines an WiFi node and takes the most appropriate actions in order to :
        Set wireless lan interface ip address and network role (Station/AccessPoint)
        Stores/Removes low level measurements
        Store the low level measurements type
    """
    def __init__(self, node):
        """ Creates a new WiFiNode object
        """
        self.node = node
        self.wlan_ipAddress = '192.168.3.' + node.ip.split('.')[3]
        self.measurements = []
        self.measurements_types = []
        self.role = None
        self.platform = None
        self.interface = None

    def add_measure(self, measure):
        """ Adds a measure or a list of measurable in the list of node measurement
        :param measure: list of measure to add at measurements object attribute
        """
        self.measurements.append(measure)

    def get_available_measures(self):
        """ Gets the available measure of the node
        :return measure_list: the list of measure stored until now
        """
        return self.measurements


class TestbedTopology:
    """
    This class defines an experiment topology and takes the most appropriate actions in order to :
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
        self.wifinodes = []  #list with all experiment WiFiNode object
        self.iface = "wlan0" #nodes interface

        #used to run UPI function on node
        self.nodes = []     #list with all experiment nodes
        self.ap_node = None
        self.ap_node1 = None
        self.wmp_nodes = []  #list with wmp nodes
        self.wmp_nodes1 = []  #list with wmp nodes1
        self.ath_nodes = []  #list with ath nodes

        self.modrate1 = 1
        self.modrate2 = 36

        self.channel1 = 11 #originally 11
        self.channel2 = 6  #originally 6

        #used to save the total number of node present in the experiment
        self.experiment_nodes_number = 0
        self.wmp_nodes_number = 0
        self.wmp_nodes_number1 = 0
        self.ath_nodes_number = 0


    def add_discovered_node(self, node):
        """ append node to nodes list
        """
        self.nodes.append(node)


    def getExperimentNodesNumber(self):
        """
        Get the number of nodes of the experiment. The experiment nodes configuration can be configured by editing of
        the file testbed_nodes.csv present in the experiment directory.

        :return: experiment_nodes_number : number of nodes in the experiment
        """
        with open('testbed_nodes.csv') as csvfile:
            reader = csv.DictReader(filter(lambda row: row[0]!='#', csvfile))
            for row in reader:
                self.experiment_nodes_number += 1
        return self.experiment_nodes_number


    def initializeTestbedTopology(self):
        """ Initializes testbed setup one AP and STA nodes, this function finds the nodes rules, and creates the nodes
            list used to call the UPI function.
        """
        #get available nodes on testbed
        nodes_ip_list = []
        nodes_role_list = []
        nodes_platform_list = []

        with open('testbed_nodes.csv') as csvfile:
            reader = csv.DictReader(filter(lambda row: row[0]!='#', csvfile))
            for row in reader:
                for ii in range(0, len(self.nodes)):
                    if self.nodes[ii].ip == row['ip']:
                        nodes_ip_list.append(row['ip'])
                        nodes_role_list.append(row['role'])
                        nodes_platform_list.append(row['platform'])

                        if row['role'] == 'AP':
                            self.ap_node = self.nodes[ii]

                        if row['role'] == 'AP1':
                            self.ap_node1 = self.nodes[ii]

                        if row['role'] == 'STA':
                            self.wmp_nodes.append(self.nodes[ii])
                            self.wmp_nodes_number += 1

                        if row['role'] == 'STA1':
                            self.wmp_nodes1.append(self.nodes[ii])
                            self.wmp_nodes_number1 += 1

                        if row['platform'] == 'ath' and row['role'] != 'AP':
                            self.ath_nodes.append(self.nodes[ii])
                            self.ath_nodes_number += 1

                        if row['platform'] == 'ath' or row['platform'] == 'wmp' or row['role'] == 'AP' or row['role'] == 'AP1':
                            self.wifinodes.append(WiFiNode(self.nodes[ii]))
        if VERBOSE:
            self.log.debug('ath_nodes_number : %s - wmp_nodes_number : %s' % (str(len(self.ath_nodes)), str(len(self.wmp_nodes)) ) )
            self.log.debug('len wifinodes : %s' % (str(len(self.wifinodes) ) ) )

    def initializeTestbedFunctions(self, controller):
        """ Setups all the node in the experiment according with the nodes rule, executes the follow operation :
                 going up the access point on node AP
                 associate the STA nodes to the AP

        :return  result: True if the operation are successful execute, False otherwise
        """
        self.setAP(self.ap_node, 'WiFiNet_1', self.modrate1, self.channel1, 1) # modare1 is the modulation rate, 1 for 192.168.3.
        self.setAP(self.ap_node1, 'WiFiNet_2', self.modrate2, self.channel2, 2) # modrate2 is the modulation rate, 2 for 192.168.4.
        node_index = 0
        node_index1 = 0
        while node_index < self.wmp_nodes_number :
            if VERBOSE:
                print("\n\n***** " + str(self.wmp_nodes[node_index].ip) + " *****\n")
            connected = self.setSTA(self.wmp_nodes[node_index], 'WiFiNet_1', self.modrate1, 1) # 1 for 192.168.3.
            print('Node %s of %s connected %s' % (str( self.wmp_nodes[node_index].ip), 'WiFiNet_1', str(connected) ))
            if not connected:
                return False
            node_index += 1
        
        while node_index1 < self.wmp_nodes_number1 :
            if VERBOSE:
                print("\n\n***** " + str(self.wmp_nodes1[node_index1].ip) + " *****\n")
            connected1 = self.setSTA(self.wmp_nodes1[node_index1], 'WiFiNet_2', self.modrate2, 2) # 2 for 192.168.4.
            print('Node %s of %s connected %s' % (str( self.wmp_nodes1[node_index1].ip), 'WiFiNet_2', str(connected1) ))
            if not connected1:
                return False
            node_index1 += 1
        
        return True

    def setAP(self, node, essid, modrate, channel, subnet):
        """ Creates infrastructure BSS, uses node such as Access Point
        :param node: elected Access Point Node
        :param essid: the SSID
        """

        if subnet == 1 :
            wlan_ipAddress = '192.168.3.' + node.ip.split('.')[3]
        elif subnet == 2 :
            wlan_ipAddress = '192.168.4.' + node.ip.split('.')[3]
        #stop hostpad
        rvalue = self.controller.nodes(node).net.stop_hostapd()
        #set ip address
        rvalue = self.controller.nodes(node).net.set_ip_address(self.iface, wlan_ipAddress)
        #set hostapd configuration
        rvalue = self.controller.nodes(node).net.set_hostapd_conf(self.iface, './wmp_helper/hostapd.conf', channel, essid)
        #start hostapd
        rvalue = self.controller.nodes(node).net.start_hostapd('./wmp_helper/hostapd.conf')
        #set power
        rvalue = self.controller.nodes(node).radio.set_tx_power(15)
        #set modulation rate
        rvalue = self.controller.nodes(node).radio.set_modulation_rate(modrate)


    def setSTA(self, node, essid, modrate, subnet):
        """ Associate node to infrastructure BSS
        :param node: elected station node by associate
        :param essid: the SSID
        """
        if subnet == 1 :
            wlan_ipAddress = '192.168.3.' + node.ip.split('.')[3]
        elif subnet == 2 :
            wlan_ipAddress = '192.168.4.' + node.ip.split('.')[3]
        if VERBOSE:
            print("\n+++ wlan_ipAddress: " + str(wlan_ipAddress) + " +++\n")
        #stop hostpad
        rvalue = self.controller.nodes(node).net.stop_hostapd()
        #set ip address
        rvalue = self.controller.nodes(node).net.set_ip_address(self.iface, wlan_ipAddress)
        #set power
        rvalue = self.controller.nodes(node).radio.set_tx_power(15)
        #set modulation rate
        # modifica per rate di modulazione
        # rvalue = self.controller.nodes(node).radio.set_modulation_rate(6)
        rvalue = self.controller.nodes(node).radio.set_modulation_rate(modrate)

        connected = False
        for ii in range(10):
            #associate station
            rvalue = self.controller.nodes(node).net.connect_to_network(self.iface, essid)
            time.sleep(2)
            #dump connection
            rvalue = self.controller.nodes(node).net.network_dump(self.iface)
            #self.log.debug('dump connection :\n%s\n'  % (str(rvalue) ))
            flow_info_lines = rvalue.rstrip().split('\n')

            if VERBOSE:
                print('\n### ' + str(flow_info_lines[0][0:9]) + ' ###')
            if flow_info_lines[0][0:9] == "Connected" :
                connected = True
                break

        return connected
