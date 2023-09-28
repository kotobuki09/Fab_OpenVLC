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
import subprocess
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

# Bidimensional variable to collect IPs and Throughputs 
global arrData
arrData = []
nodesID = []

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

#subprocess.Popen doesn't block
def run_shell_cmd(args_list):
        """
        run linux commands
        """
        # import subprocess
        print('Running system command: {0}'.format(' '.join(args_list)))
        proc = subprocess.Popen(args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #s_output = proc.communicate()
        s_output = proc.stdout.readlines()
        #s_return =  proc.returncode
        #return s_return, s_output, s_err
        return s_output

def collect_remote_messages(lcpDescriptor_node, socket_visualizer):
    """
        This function implement the process that receive message information from nodes experiment. The messages are
        sent to the demo GUI through the socket_visualizer. The function also perform the storage of the nodes
        measurements
    :param lcpDescriptor_node: pointer to node local control program description
    :param socket_visualizer: socket connection to demo GUI visualizer
    """
    global counter_net1 
    counter_net1 = 0
    global counter_net2
    counter_net2 = 0
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
            if msg['measure'][0][2] != 0.0 and str(msg['wlan_ip_address']) != '192.168.4.107':
                if str(msg['wlan_ip_address']) == '192.168.3.10' and counter_net1 < EXPERIMENT_DURATION:
                    #log.info("\n########## " + str(msg['measure'][0][2]) + " ##########\n")
                    arrData.append([msg['wlan_ip_address'], msg['measure'][0][2]])
                    counter_net1 += 1
                    #log.info("\n########## APPENDED, new counter: " + str(counter_net1) + " ##########\n")
                elif str(msg['wlan_ip_address']) == '192.168.4.1' and counter_net2 < EXPERIMENT_DURATION:
                    #log.info("\n########## " + str(msg['measure'][0][2]) + " ##########\n")
                    arrData.append([msg['wlan_ip_address'], msg['measure'][0][2]])
                    counter_net2 += 1
                    #log.info("\n########## APPENDED, new counter: " + str(counter_net2) + " ##########\n")

        gevent.sleep(1)

# Return array with the two nodeID
def get_nodesID():
    out = run_shell_cmd(['yarn', 'node', '-list'])

    a = ''.join(str(out[2]))
    a_splitted = a.split('  ')
    a_splitted = a_splitted[1][:-2]
    nodesID.append(a_splitted)
 
    b = ''.join(str(out[3]))
    b_splitted = b.split('  ')
    b_splitted = b_splitted[1][:-2]
    nodesID.append(b_splitted)

    return nodesID

def get_nodes_throughputs():
    midWiFi1_Throughput = 0
    midWiFi2_Throughput = 0
    countWiFi1 = 0
    countWiFi2 = 0
    result = []
    for tupla in arrData:
        # extensa
        if tupla[0] == '192.168.3.10':
            countWiFi1 = countWiFi1 +1
            midWiFi1_Throughput += tupla[1]
        # nautilus
        elif tupla[0] == '192.168.4.1':
            midWiFi2_Throughput += tupla[1]
            countWiFi2 = countWiFi2 +1

    if countWiFi1 != 0 and countWiFi2 != 0:
        midWiFi1_Throughput = midWiFi1_Throughput/countWiFi1
        midWiFi2_Throughput = midWiFi2_Throughput/countWiFi2

    networkStatistic1 = ['extensa', midWiFi1_Throughput]
    networkStatistic2 = ['nautilus', midWiFi2_Throughput]

    return networkStatistic1, networkStatistic2

def deactivate_node(nodeName, wmp_node_tot):
    # Insert node name to remove
    outF = open("/home/hadoop/hadoop/etc/hadoop/excludes", "w")
    print(nodeName, file=outF)
    outF.close()
    out = run_shell_cmd(['hdfs', 'dfsadmin', '-refreshNodes'])
    log.info(str(out))

    count = 0
    for ii in range(len(wmp_node_tot)):
        if nodeName == 'extensa' and wmp_node_tot[ii].ip == '192.168.2.10' or nodeName == 'nautilus' and wmp_node_tot[ii].ip == '192.168.2.1':
            break
        count += 1

    log.info("Ready to send deactivation message . . .")
    lcpDescriptor_wmp_nodes[count].send({"activation": 0})

    out = subprocess.call(['sh', '/home/hadoop/hadoop/sbin/start-balancer.sh'])

def reactivate_node(nodeName, wmp_node_tot):
    # Open/Close file to activate nodes
    outF = open("/home/hadoop/hadoop/etc/hadoop/excludes", "w")
    outF.close()
    out = run_shell_cmd(['hdfs', 'dfsadmin', '-refreshNodes'])
    log.info(str(out))

    count = 0
    for ii in range(len(wmp_node_tot)):
        if nodeName == 'extensa' and wmp_node_tot[ii].ip == '192.168.2.10' or nodeName == 'nautilus' and wmp_node_tot[ii].ip == '192.168.2.1':
            break
        count += 1

    log.info("Ready to send activation message . . .")
    lcpDescriptor_wmp_nodes[count].send({"activation": 1})

    out = subprocess.call(['sh', '/home/hadoop/hadoop/sbin/start-balancer.sh'])

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


            global EXPERIMENT_DURATION
            EXPERIMENT_DURATION = 5
            #dt=0

            controller.delay(1).nodes(mytestbed.ap_node).net.create_packetflow_sink('1234', '1', True, 'wlan0')
            controller.delay(1).nodes(mytestbed.ap_node1).net.create_packetflow_sink('1234', '1', True, 'wlan0')
            time.sleep(2)

            for node in mytestbed.wmp_nodes:
                wmp_node_tot.append(node)
            for node in mytestbed.wmp_nodes1:
                wmp_node_tot.append(node)

            global lcpDescriptor_wmp_nodes
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
            global WITH_BACK_TRAFFIC
            WITH_BACK_TRAFFIC = False

            controller.delay(5).nodes(mytestbed.wmp_nodes[0]).net.start_packetflow('192.168.3.' + mytestbed.ap_node.ip.split('.')[3],
                                                                 '1234', '3000', '100M', '1300')
            for i in range(2):
                if WITH_BACK_TRAFFIC:
                    controller.delay(5).nodes(mytestbed.wmp_nodes1[i]).net.start_packetflow('192.168.4.' + mytestbed.ap_node1.ip.split('.')[3],
                                                                 '1234', '3000', '100M', '1300')
                else:
                    if str(mytestbed.wmp_nodes1[i].ip) == '192.168.2.1':
                        controller.delay(5).nodes(mytestbed.wmp_nodes1[i]).net.start_packetflow('192.168.4.' + mytestbed.ap_node1.ip.split('.')[3],
                                                                 '1234', '3000', '100M', '1300')
            while do_run:
                socket_list = poller.poll(1000)
                """
                if socket_list:
                    for socket_info in socket_list:
                        if socket_info[1] == zmq.POLLIN:
                            #receive message command from demo GUI
                            parsed_json = socket_command.recv_json()
                            #message format : {'ip_address': '192.168.3.104', 'command': 'TDMA 2', 'type': 'protocol'}

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
                """

                #need to keep alive the control program, if do not present the remote control program will been closed
                lcpDescriptor_wmp_nodes[0].send({"alive": 1})
                lcpDescriptor_wmp_nodes[1].send({"alive": 1})


                log.info("\n\n *** " + str(counter_net1) + " ***** " + str(counter_net2) + " ***\n")

                if counter_net1 == EXPERIMENT_DURATION and counter_net2 == EXPERIMENT_DURATION:
                    """
                    # Destroy Client traffic
                    log.info("\nStop Client iperf traffic WiFiNet_1 . . .")
                    controller.nodes(mytestbed.wmp_nodes).net.stop_packetflow()
                    for i in range(2):
                        if WITH_BACK_TRAFFIC == False:
                            log.info("\nStop Clients iperf traffic WiFiNet_2 . . .")
                            controller.nodes(mytestbed.wmp_nodes1[i]).net.stop_packetflow()
                        else:
                            if str(mytestbed.wmp_nodes1[i].ip) == '192.168.2.1':
                                log.info("\nStop Client_1 iperf traffic WiFiNet_2 . . .")
                                controller.nodes(mytestbed.wmp_nodes1[i]).net.stop_packetflow()
                    """
                    break 

                time.sleep(1)

            (node1_throughput, node2_throughput) = get_nodes_throughputs()

            # Take nodeIDs
            nodesID = get_nodesID()
            log.info("\nThroughput extensa: " + str(node1_throughput[1]) + "\nThroughput nautilus: " + str(node2_throughput[1]))

            # Deactivate worst node
            node_deactivated = ''
            if float(node1_throughput[1]) > float(node2_throughput[1]):
                node_deactivated = 'nautilus'
            elif float(node1_throughput[1]) < float(node2_throughput[1]):
                node_deactivated = 'extensa'

            log.info("\nDeactivation of node: " + str(node_deactivated))
            deactivate_node(node_deactivated, wmp_node_tot)

            log.info("\nStart the application. . ."))
            out = subprocess.call(['sh','/home/hadoop/script_time_hdfs.sh'])
            log.info(str(out))

            out = subprocess.call(['hdfs', 'dfs', '-rm', '-r', 'output'])
            log.info(str(out))

            """
            # Destroy active traffic
            log.info("\nStop Server iperf traffic WiFiNet_1 . . .")
            controller.delay(2).nodes(mytestbed.ap_node).net.destroy_packetflow_sink()

            for i in range(2):
                if WITH_BACK_TRAFFIC and str(mytestbed.wmp_nodes1[i].ip) == '192.168.2.107':
                    log.info("\nStop Client_2 iperf traffic WiFiNet_2 . . .")
                    controller.nodes(mytestbed.wmp_nodes1[i]).net.stop_packetflow()                        

            log.info("\nStop Server iperf traffic WiFiNet_2 . . .")
            controller.delay(2).nodes(mytestbed.ap_node1).net.destroy_packetflow_sink()
            """

            """
            # Reset params
            reactivate_node(node_deactivated)
            """

            #destroy active traffic
            controller.delay(2).nodes(mytestbed.ap_node).net.destroy_packetflow_sink()
            controller.delay(3).nodes(mytestbed.wmp_nodes).net.stop_packetflow()

            controller.delay(2).nodes(mytestbed.ap_node1).net.destroy_packetflow_sink()
            controller.delay(3).nodes(mytestbed.wmp_nodes1).net.stop_packetflow()

            """
            Plot/Save collect measurement of phase 1
            """
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