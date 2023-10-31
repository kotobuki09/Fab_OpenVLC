#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Usage:
   experiment_controller [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --config configFile Config file path

Example:
   ./metamac_experiment_controller -v --config ./controller_config.yaml

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""
__author__ = "Domenico Garlisi"
__copyright__ = "Copyright (c) 2016, CNIT"
__version__ = "0.1.0"
__email__ = "domenico.garlisi@cnit.it"

import sys
import datetime
import logging
import time
import threading
import csv
import shutil
import signal

import gevent
import yaml
import zmq

sys.path.append('../../../')
sys.path.append("../../../agent_modules/wifi_ath")
sys.path.append("../../../agent_modules/wifi_wmp")
sys.path.append("../../../agent_modules/wifi")
sys.path.append('../../../upis')
sys.path.append('../../../framework')
sys.path.append('../../../agent')
sys.path.append('../../../controller')
sys.path.append("../../../agent_modules/net_linux")

import wishful_controller
from examples.Get_Started_Examples.Advanced_WMP_Example.wmp_helper.controller_utils import *
from examples.Get_Started_Examples.Advanced_WMP_Example.wmp_helper.TestbedTopology import TestbedTopology
from examples.Get_Started_Examples.Advanced_WMP_Example.wmp_helper.MeasurementManager import MeasurementCollector
from metamac_local_control_program import *

#set controller logging
log = logging.getLogger('wishful_agent.main')

#run WiSHFUL controller module
controller = wishful_controller.Controller()
nodes = []
do_run = None

#create TestbedTopology object, to keep information about WiFiNode in terms of:
# list of nodes, measurement and acapabilities
mytestbed = TestbedTopology("wmp_metamac", log, controller)

#create MeasurementCollector object, to keep information about WiFiNode measurements and perform plotting result
meas_collector = MeasurementCollector(mytestbed, log)

#calling when a new node is discovered on network
@controller.new_node_callback()
def new_node(node):
    print("New node appeared:")
    print(node)
    nodes.append(node)
    mytestbed.add_discovered_node(node)

#calling when a experiment node leave the netwrok
@controller.node_exit_callback()
def node_exit(node, reason):
    if node in nodes:
        nodes.remove(node);
    print("NodeExit : NodeID : {} Reason : {}".format(node.id, reason))

#UPI default callback, calling when a no blocking UPI call without defined callback has been completed
@controller.set_default_callback()
def default_callback(group, node, cmd, data):
    print("DEFAULT CALLBACK : Group: {}, NodeId: {}, Cmd: {}, Returns: {}".format(group, node.id, cmd, data))

def signal_handler(signal, frame):
    """
    #set the control for program exit

    :param signal:
    :param frame:
    :return:
    """
    global do_run
    do_run = False
signal.signal(signal.SIGINT, signal_handler)


def start_visualizer_connection():
    """
        this function starts socket for send protocol information to realtime visualizer, demo GUI
    """
    print(controller.name)
    if controller.name == 'Controller nova':
        socket_visualizer_port = "8301"
    else:
        socket_visualizer_port = "8401"

    context = zmq.Context()
    socket_visualizer = context.socket(zmq.PUB)
    socket_visualizer.bind("tcp://*:%s" % socket_visualizer_port)
    print("Connecting to server on port %s ... ready to send information to visualizer" % socket_visualizer_port)

    ''' implement OML database setup for realtime visualizer '''
    # #global omlInst
    # #omlInst = oml4py.OMLBase("LocalControlProgram", "WiSHFUL", socket.gethostname(),"tcp:am.wilab2.ilabt.iminds.be:3004")
    # #omlInst.addmp("IEEE802154_MACSTATS", "timestamp:int32 nodeID:int32 packetSize:int32 activeRadioprogram:string timeDiff:int32 numTxRequest:int32 numTxRequestFail:int32 numTxAttempt:int32 numTxSuccess:int32 numTxFail:int32 numTxBusy:int32 numTxNoAck:int32 numTxCollision:int32 numRx:int32 avgBackoffExponent:int32")
    # #omlInst.start()

    return socket_visualizer


def start_command_connection():
    """
        this function starts zmq socket for receive command from realtime visualizer, demo GUI
    """
    print(controller.name)
    if controller.name == 'Controller nova':
        socket_command_port  = '8300'
    else:
        socket_command_port  = '8400'
    context = zmq.Context()
    socket_command = context.socket(zmq.PAIR)
    socket_command.bind("tcp://*:%s" % socket_command_port)
    print("Connecting to server on port %s ... ready to receive command from demo visualizer" % socket_command_port)

    return socket_command

def collect_remote_messages(lcpDescriptor_node, socket_visualizer):
    """
        This function implement the process that receive message information from nodes experiment. The messages are
        sent to the demo GUI through the socket_visualizer. The function also perform the storage of the nodes
        measurements
    :param lcpDescriptor_node: pointer to node local control program description
    :param socket_visualizer: socket connection to demo GUI visualizer
    """
    receive_thread = threading.currentThread()
    while getattr(receive_thread, "do_run", True):
        #receive messages
        msg = lcpDescriptor_node.recv(timeout=0.1)
        if msg:
            log.info("Recv ctrl message from remote local control program : %s" % str(msg))
            #send messages to real time visualizer
            # socket_visualizer.send_json(msg)

            #add received measurements to the node measurements list
            # for node in mytestbed.wifinodes:
            #     if msg['wlan_ip_address'] == node.wlan_ipAddress:
            #         node.add_measure(msg['measure'])
        gevent.sleep(1)


def main(args):
    log.debug(args)

    #open controller module file configuration
    config_file_path = args['--config']
    config = None
    with open(config_file_path, 'r') as f:
        config = yaml.load(f)

    #load controller module configuration
    controller.load_config(config)

    #start WiSHFUL controller
    controller.start()

    #get experiment node number
    num_testbed_nodes = mytestbed.getExperimentNodesNumber()

    global do_run
    do_run = True

    # nodes_platform_info = [] #list of WMP nodes capabilities

    #control loop
    while do_run:
        gevent.sleep(10)
        print("\n")
        print("Connected nodes", [str(node.name) for node in nodes])

        if len(nodes) == num_testbed_nodes:

            #find node rules
            mytestbed.initializeTestbedTopology()

            #get node capabilities, get capabilities from the first WMP detected node, all nodes are the same
            # nodes_platform_info.append(get_platform_information( nodes[0], log, controller))

            # #start connection to real time visualizzer - Demo GUI
            socket_visualizer = start_visualizer_connection()
            socket_command = start_command_connection()


            EXPERIMENT_DURATION= 3000
            dt=0

            controller.delay(1).nodes(mytestbed.ap_node).net.create_packetflow_sink('1234', '1', True, 'wlan0')
            controller.delay(1).nodes(mytestbed.ap_node1).net.create_packetflow_sink('1234', '1', True, 'wlan0')
            time.sleep(2)

            for node in mytestbed.wmp_nodes:
                wmp_node_tot.append(node)
            for node in mytestbed.wmp_nodes1:
                wmp_node_tot.append(node)

            lcpDescriptor_wmp_nodes = []
            reading_thread = []
            for ii in range(len(wmp_node_tot)):
                # start local control program on node
                lcpDescriptor_wmp_nodes.append(controller.node(wmp_node_tot[ii]).hc.start_local_control_program(
                    program=metamac_local_control_program))
                # start thread for collect measurements from node
                reading_thread.append(threading.Thread(target=collect_remote_messages,
                                                       args=(lcpDescriptor_wmp_nodes[ii], socket_visualizer,)))
                reading_thread[ii].start()

            #create message poller
            poller = zmq.Poller()
            poller.register(socket_command, flags=zmq.POLLIN)

            #start server traffic
            controller.delay(5).nodes(mytestbed.wmp_nodes[0]).net.start_packetflow('192.168.3.' + mytestbed.ap_node.ip.split('.')[3],
                                                                 '1234', '3000', '100M', '1300')
            controller.delay(5).nodes(mytestbed.wmp_nodes1[0]).net.start_packetflow('192.168.4.' + mytestbed.ap_node1.ip.split('.')[3],
                                                                 '1234', '3000', '100M', '1300')
            while do_run:
                socket_list = poller.poll(1000)
                if socket_list:
                    for socket_info in socket_list:
                        if socket_info[1] == zmq.POLLIN:
                            #receive message command from demo GUI
                            parsed_json = socket_command.recv_json()

                            print('parsed_json : %s' % str(parsed_json))
                            #extract message type
                            type = parsed_json['type']

                            #process traffic command message (deactive or active (low / high) traffic)
                            if type == 'traffic':
                                command = parsed_json['command']
                                if command == 'stop':
                                    #stop client traffic
                                    controller.nodes(mytestbed.wmp_nodes).net.stop_packetflow()
                                    controller.nodes(mytestbed.wmp_nodes1).net.stop_packetflow()
                                if command == 'start_low':
                                    #start client traffic
                                    for node in mytestbed.wmp_nodes:
                                        controller.delay(1).nodes(node).net.start_packetflow( '192.168.3.' + mytestbed.ap_node.ip.split('.')[3], '1234', '3000', parsed_json['source_rate']+'k', '1300')
                                    for node1 in mytestbed.wmp_nodes1:
                                        controller.delay(1).nodes(node1).net.start_packetflow( '192.168.4.' + mytestbed.ap_node1.ip.split('.')[3], '1234', '3000', parsed_json['source_rate']+'k', '1300')
                                if command == 'start_high':
                                    #start client traffic
                                    for node in mytestbed.wmp_nodes:
                                        controller.delay(1).nodes(node).net.start_packetflow( '192.168.3.'+ mytestbed.ap_node.ip.split('.')[3], '1234', '3000', parsed_json['source_rate']+'k', '1300')
                                    for node1 in mytestbed.wmp_nodes1:
                                        controller.delay(1).nodes(node1).net.start_packetflow( '192.168.4.'+ mytestbed.ap_node1.ip.split('.')[3], '1234', '3000', parsed_json['source_rate']+'k', '1300')


                #need to keep alive the control program, if do not present the remote control program will been closed
                lcpDescriptor_wmp_nodes[0].send({"alive": 1})

                log.warning('waiting for ... (%d sec / %d)' % (dt, EXPERIMENT_DURATION) )
                dt += 1

                #gevent.sleep(1)
                time.sleep(1)

                if dt > EXPERIMENT_DURATION:
                    break

            #destroy active traffic
            controller.delay(2).nodes(mytestbed.ap_node).net.destroy_packetflow_sink()
            controller.delay(3).nodes(mytestbed.wmp_nodes).net.stop_packetflow()

            controller.delay(2).nodes(mytestbed.ap_node1).net.destroy_packetflow_sink()
            controller.delay(3).nodes(mytestbed.wmp_nodes1).net.stop_packetflow()

            """
            Plot/Save collect measurement of phase 1
            """
            #meas_collector.save_measurements(nodes=mytestbed.wifinodes, directory="showcase_data")
            break




if __name__ == "__main__":
    try:
        from docopt import docopt
    except:
        print("""
        Please install docopt using:
            pip install docopt==0.6.1
        For more refer to:
        https://github.com/docopt/docopt
        """)
        raise

    wmp_node_tot = []

    #loading agent option command
    args = docopt(__doc__, version=__version__)
    log_level = logging.INFO  # default
    if args['--verbose']:
        log_level = logging.DEBUG
    elif args['--quiet']:
        log_level = logging.ERROR

    #read agent file configuration
    logfile = None
    if args['--logfile']:
        logfile = args['--logfile']

    #load controller file configuration
    logging.basicConfig(filename=logfile, level=log_level,
        format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

    try:
        main(args)
    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        controller.stop()