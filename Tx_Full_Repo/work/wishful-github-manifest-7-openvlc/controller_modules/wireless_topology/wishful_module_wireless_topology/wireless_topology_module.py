import logging
import wishful_framework as wishful_module
import wishful_upis as upis
import upis.wishful_upis.meta_radio as radio
from wishful_framework.classes import exceptions
import itertools
import time
import datetime
import gevent

__author__ = "Piotr Gawlowicz, Anatolij Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, zubow}@tkn.tu-berlin.de"


@wishful_module.build_module
class WirelessTopologyModule(wishful_module.ControllerModule):
    def __init__(self, controller):
        super(WirelessTopologyModule, self).__init__(controller)
        self.log = logging.getLogger('wireless_topology_module.main')

    def print_response(self, group, node, data):
        """ This function implements a callback to print generic UPI function calling result

        :param group: Experiment group name
        :param node: Node used to execute the UPI
        :param data: Execution time
        """
        print("\n{} Print response : Group:{}, NodeIP:{}, Result:{}".format(datetime.datetime.now(), group, node.ip, data))

    @wishful_module.bind_function(upis.net_func.estimate_nodes_in_carrier_sensing_range)
    def estimate_nodes_in_carrier_sensing_range(self, nodes, iface, **kwargs):
        """
        Test to find out whether two nodes in the network are in carrier sensing range using UPIs.
        For a network with N nodes all combinations are evaluated, i.e. N over 2.
        Note: make sure ptpd is running: sudo /etc/init.d/ptp-daemon
        @return a list of triples (node1, node2, True/False) True/False if nodes are in carrier sensing range
        """

        #self.log.info("is_in_carrier_sensing_range for nodes: %s" % str(nodes))

        TAU = kwargs.get('TAU')

        if (len(nodes) < 2):
            self.log.error('For this test we need at least two nodes.')
            return None

        res = []
        nodeIds = list(range(0, len(nodes)))
        groups = itertools.combinations(nodeIds, 2)
        for subgroup in groups:
            #print(subgroup)
            # testing scenario
            node1 = nodes[subgroup[0]]
            node2 = nodes[subgroup[1]]

            # exec experiment for each pair of nodes
            isInCs = self.is_in_carrier_sensing_range(node1, node2, iface, TAU=TAU)
            res.append([node1,node2,isInCs])

        return res


    @wishful_module.bind_function(upis.net_func.is_in_carrier_sensing_range)
    def is_in_carrier_sensing_range(self, node1, node2, mon_dev, **kwargs):
        """
        Helper functions to find out whether two nodes are in carrier sensing range or not.
        The following algorithm is used here. The maximum transmit rate of each node is compared to the
        transmission rate which can be achieved by both nodes if they transmit at the same time. If this
        rate is lower than some threshold it is assumed that the nodes can sense each other.
        @return True if nodes are in carrier sensing range
        """

        TAU = kwargs.get('TAU')
        nodes = []
        nodes.append(node1)
        nodes.append(node2)
        if (len(nodes) < 2):
            self.log.error('For this test we need at least two nodes.')
            return None

        self.log.info('Testing carrier sensing range between %s and %s' % (str(node1.ip), str(node2.ip)))
        single_tx_rate_stats = {}
        parallel_tx_rate_stats = {}
        rel_rate_cmp_single = {}
        isInCs = {}
        result = False

        # def csResultCollector(group, nodeId, data):
        #     self.log.info('CS callback %d: receives data msg from %s : %s' % (group, nodeId, data))
        #
        #     parallel_tx_rate_stats[peer_node] = float(data)
        #     rel_rate_cmp_single[peer_node] = parallel_tx_rate_stats[peer_node] / single_tx_rate_stats[peer_node]
        #     self.log.info('Relative rate cmp to single for %s is %.2f' % (peer_node, rel_rate_cmp_single[peer_node]))
        #
        #     self.log.info('')
        #     if (len(rel_rate_cmp_single) == 2):
        #         # done
        #         if min(rel_rate_cmp_single.values()) <= float(TAU):
        #             isInCs['res'] = True
        #         else:
        #             isInCs['res'] = False
        try:

            UPIargs = {'parameters': [radio.BUSY_TIME.key]}

            pkt_stats = self.controller.nodes(node2).blocking(True).radio.get_parameters(UPIargs)
            start_busy_time_node_2 = pkt_stats[radio.BUSY_TIME.key]
            self.log.info('(1) single flow at %s get busytime at node %s' % (str(node1.ip),str(node2.ip)))
            rv = self.controller.nodes(node1).blocking(True).net.gen_layer2_traffic(mon_dev, 1000, None, 12, ipPayloadSize=1350, ipdst="1.1.1.1", ipsrc="2.2.2.2", use_tcpreplay=True)
            peer_node = node1
            single_tx_rate_stats[peer_node] = rv
            pkt_stats = self.controller.nodes(node2).blocking(True).radio.get_parameters(UPIargs)
            busy_time_node_2 = pkt_stats[radio.BUSY_TIME.key] - start_busy_time_node_2

            pkt_stats = self.controller.nodes(node1).blocking(True).radio.get_parameters(UPIargs)
            start_busy_time_node_1 = pkt_stats[radio.BUSY_TIME.key]
            self.log.info('(2) single flow at %s get busytime at node %s' % (str(node2.ip), str(node1.ip)))
            rv = self.controller.nodes(node2).blocking(True).net.gen_layer2_traffic(mon_dev, 1000, None, 12, ipPayloadSize=1350, ipdst="1.1.1.1", ipsrc="2.2.2.2", use_tcpreplay=True)
            peer_node = node2
            single_tx_rate_stats[peer_node] = rv
            pkt_stats = self.controller.nodes(node1).blocking(True).radio.get_parameters(UPIargs)
            busy_time_node_1 = pkt_stats[radio.BUSY_TIME.key] - start_busy_time_node_1

            # time.sleep(2)
            # self.log.info('(3) two flows at same time %s' % str(nodes))
            # exec_time = datetime.datetime.now() + datetime.timedelta(seconds=3)
            # rv = self.controller.exec_time(exec_time).callback(csResultCollector).node(nodes).net.gen_layer2_traffic(mon_dev, 100, 1000, 12, ipPayloadSize=1350, ipdst="1.1.1.1", ipsrc="2.2.2.2", use_tcpreplay=True)
            # while len(isInCs)==0:
            #     self.log.info('waiting for results ...')
            #     time.sleep(1)

            self.log.info('(3) busytime at node %s : %s [ms]' % (str(node1.ip), str(busy_time_node_1)))
            self.log.info('(4) busytime at node %s : %s [ms]' % (str(node2.ip), str(busy_time_node_2)))
            if busy_time_node_1>200 and  busy_time_node_2>200:
                result = True

        except Exception as e:
            self.log.fatal("An error occurred in is_in_carrier_sensing_range : %s" % e)

        #return isInCs['res']
        return result

    @wishful_module.bind_function(upis.net_func.estimate_nodes_in_communication_range)
    def estimate_nodes_in_communication_range(self, nodes, iface, **kwargs):
        """
        Test to find out whether two nodes in the network are in communication range using UPIs.
        For a network with N nodes all combinations are evaluated, i.e. N over 2.
        Note: make sure ptpd is running: sudo /etc/init.d/ptp-daemon
        @return a list of triples (node1, node2, True/False) True/False if nodes are in communication range
        """

        #self.log.info('Nodes to tested for comm. range %s' % str(nodes))

        MINPDR = kwargs.get('MINPDR')

        if (len(nodes) < 2):
            self.log.error('For this test we need at least two nodes.')
            return None

        res = []
        nodeIds = list(range(0, len(nodes)))
        groups = itertools.combinations(nodeIds, 2)
        for subgroup in groups:
            #print(subgroup)
            # testing scenario
            node1 = nodes[subgroup[0]]
            node2 = nodes[subgroup[1]]

            # exec experiment for each pair of nodes
            isInComm = self.is_in_communication_range(node1, node2, iface, MINPDR=MINPDR)
            res.append([node1,node2,isInComm])

        return res

    @wishful_module.bind_function(upis.net_func.is_in_communication_range)
    def is_in_communication_range(self, node1, node2, mon_dev, **kwargs):

        """
        Helper functions to find out whether two nodes are in communication range using UPIs.
        @return True if nodes are in communication range
        """
        MINPDR = kwargs.get('MINPDR')

        nodes = []
        nodes.append(node1)
        nodes.append(node2)
        if (len(nodes) < 2):
            self.log.error('For this test we need at least two nodes.')
            return None

        self.log.info('Testing communication range between %s and %s' % (str(node1.ip), str(node2.ip)))
        rxPkts = {}

        def csResultCollector(group, node, data):
            #print("\n{} Print csResultCollector response : Group:{}, NodeIP:{}, Result:{}".format(datetime.datetime.now(), group, node.ip, data))
            time_val = datetime.datetime.now()
            peer_node = node.ip
            messagedata = data
            self.log.info('CommRange callback receives data msg at %s from %s : %s' % (str(time_val), peer_node, messagedata))
            if messagedata is None:

                rxPkts['res'] = 0
            else:
                rxPkts['res'] = int(messagedata)


        try:
            self.log.info('(1) sniff traffic at %s' % str(node1.ip))
            exec_time = datetime.datetime.now() + datetime.timedelta(seconds=2)
            rv = self.controller.exec_time(exec_time).callback(csResultCollector).node(node1).net.sniff_layer2_traffic(mon_dev, 5, ipdst="1.1.1.1", ipsrc="2.2.2.2")

            self.log.info('(2) gen traffic at %s' % str(node2.ip))
            exec_time = datetime.datetime.now() + datetime.timedelta(seconds=3)
            rv = self.controller.exec_time(exec_time).node(node2).net.gen_layer2_traffic(mon_dev, 255, 0.01, 12, ipPayloadSize=1350, ipdst="1.1.1.1", ipsrc="2.2.2.2", use_tcpreplay=True)

            time_out = 10
            while len(rxPkts)==0 or time_out>0:
                self.log.info('commrange waiting for results ...')
                gevent.sleep(1)
                time_out -= 1

        except Exception as e:
            self.log.fatal("An error occurred in is_in_communication_range : %s" % e)

        if len(rxPkts)==0:
            self.log.info('An error occurred in is_in_communication_range' )
            return False

        # calc PDR
        pdr = rxPkts['res'] / float(255)
        minPdrFloat = float(MINPDR)
        self.log.info('PDR between %s and %s is %.2f (%.2f)' % (str(node1.ip), str(node2.ip), pdr, minPdrFloat))

        if pdr >= minPdrFloat:
            return True
        else:
            return False