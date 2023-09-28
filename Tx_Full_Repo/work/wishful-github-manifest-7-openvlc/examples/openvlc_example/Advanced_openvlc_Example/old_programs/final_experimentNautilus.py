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
import subprocess
import random

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
    print('Running system command: {0}'.format(' '.join(args_list)))
    proc = subprocess.Popen(args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    s_output = proc.stdout.readlines()
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
    global mod_rate1
    mod_rate1 = 0
    global mod_rate2
    mod_rate2 = 0
    receive_thread = threading.currentThread()
    while getattr(receive_thread, "do_run", True):
        #receive messages
        msg = lcpDescriptor_node.recv(timeout=0.1)
        if msg:
            log.info("Recv ctrl message from remote local control program : %s" % str(msg))

            if msg['measure'][0][2] != 0.0 and str(msg['wlan_ip_address']) != '192.168.4.107':
                if str(msg['wlan_ip_address']) == '192.168.3.10' and counter_net1 < MONITOR_TIME_DURATION:
                    arrData.append([msg['wlan_ip_address'], msg['measure'][0][2]])
                    counter_net1 = counter_net1 +1
                    if mod_rate1 == 0 or mod_rate1 != msg['measure'][1][0]:
                        #log.info("***** " +  str(msg['measure'][1][0]) + " *****")
                        mod_rate1 = msg['measure'][1][0]

                elif str(msg['wlan_ip_address']) == '192.168.4.1' and counter_net2 < MONITOR_TIME_DURATION:
                    arrData.append([msg['wlan_ip_address'], msg['measure'][0][2]])
                    counter_net2 = counter_net2 +1
                    if mod_rate2 == 0 or mod_rate2 != msg['measure'][1][0]:
                        #log.info("***** " + str(msg['measure'][1][0]) + " *****")
                        mod_rate2 = msg['measure'][1][0]

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

def get_nodes_num():
    global node_num
    out, proc = subprocess.Popen(['yarn', 'node', '-list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    lines = out.splitlines()
    node_num = lines[0][12:]
    SYSTEM_STATE[0] = 'APPLICATION_EXECUTION'

# Reset to default node params
def reset_nodes_params(nodesID):
    for node_id in nodesID:
        out = run_shell_cmd(['yarn', 'rmadmin', '-updateNodeResource', str(node_id), str(1536), str(2)])

# Put nodeName params down  
def node_params_down(nodesID, nodeName):
    for node_id in nodesID:
        if nodeName in node_id:
            log.info("\nNodeName to down: " + node_id)
            out = run_shell_cmd(['yarn', 'rmadmin', '-updateNodeResource', str(node_id), str(256), str(1)])
            break

def deactivate_node(nodeName, wmp_node_tot):
    # Insert node name to remove
    outF = open("/home/hadoop/hadoop/etc/hadoop/excludes", "w")
    print(nodeName, file=outF)
    outF.close()    
    out = run_shell_cmd(['hdfs', 'dfsadmin', '-refreshNodes'])
    log.info(str(out))

    index = 0
    for ii in range(len(wmp_node_tot)):
        if (nodeName == 'extensa' and wmp_node_tot[ii].ip == '192.168.2.10') or (nodeName == 'nautilus' and wmp_node_tot[ii].ip == '192.168.2.1'):
            log.info("** node_ip: " + str(wmp_node_tot[ii].ip) + " ** " + "index: " + str(index))
            break
        index += 1

    log.info("Ready to send deactivation message . . .")
    lcpDescriptor_wmp_nodes[index].send({"activation": 0})

    out = run_shell_cmd(['sh', '/home/hadoop/hadoop/sbin/start-balancer.sh'])
    log.info("Node Deactivated: " + str(nodeName))
    SYSTEM_STATE[0] = 'NODE_NUMBER'

def reactivate_node(nodeName, wmp_node_tot):
    # Open/Close file to activate nodes
    outF = open("/home/hadoop/hadoop/etc/hadoop/excludes", "w")
    outF.close()
    out = run_shell_cmd(['hdfs', 'dfsadmin', '-refreshNodes'])
    log.info(str(out))

    index = 0
    for ii in range(len(wmp_node_tot)):
        if (nodeName == 'extensa' and wmp_node_tot[ii].ip == '192.168.2.10') or (nodeName == 'nautilus' and wmp_node_tot[ii].ip == '192.168.2.1'):
            log.info("** node_ip: " + str(wmp_node_tot[ii].ip) + " ** " + "index: " + str(index))
            break
        index += 1

    log.info("Ready to send activation message . . .")
    lcpDescriptor_wmp_nodes[index].send({"activation": 1})

    out = run_shell_cmd(['sh', '/home/hadoop/hadoop/sbin/start-balancer.sh'])
    SYSTEM_STATE[0] = 'END'

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

def run_application():
    out = subprocess.call(['sh','/home/hadoop/script_time_hdfs.sh'])
    log.info(str(out))
    if deactivated:
        SYSTEM_STATE[0] = 'RESTORATION_NODES'
    else:
        SYSTEM_STATE[0] = 'END'

def hadoop_start():
    log.info(" ***** Hadoop Activation ***** ")
    out = subprocess.call(['hdfs', 'namenode', '-format'])
    out = subprocess.call(['./../../../../../hadoop/hadoop/sbin/start-dfs.sh'])
    log.info(str(out))
    out = subprocess.call(['./../../../../../hadoop/hadoop/sbin/start-yarn.sh'])
    log.info(str(out))
    out = subprocess.call(['hdfs', 'dfs', '-mkdir', '-p', '/user/hadoop'])
    out = subprocess.call(['hdfs', 'dfs', '-mkdir', 'books'])
    out = subprocess.call(['hdfs', 'dfs', '-put', '/home/hadoop/alice.txt', 'books'])
    out = subprocess.call(['hdfs', 'dfs', '-put', '/home/hadoop/frankenstein.txt', 'books'])
    log.info(str(out))
"""
def hadoop_stop():
    log.info(" ***** Hadoop Deactivation ***** ")
    out = subprocess.call(['./../../../../../hadoop/hadoop/sbin/stop-yarn.sh'])
    log.info(str(out))
    out = subprocess.call(['./../../../../../hadoop/hadoop/sbin/stop-dfs.sh'])
    log.info(str(out))
    out = subprocess.call(['rm', '-r', '../../../../../hadoop/data', '../../../../../hadoop/hadoop/tmp/', '../../../../../hadoop/hadoop/logs/*'])
"""


def main(args):
    log.debug(args)

    #open controller module file configuration
    config_file_path = args['--config']
    config = None
    with open(config_file_path, 'r') as f:
        config = yaml.load(f)

    # Hadoop activation
    hadoop_start()

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

            # #start connection to real time visualizzer - Demo GUI
            socket_visualizer = start_visualizer_connection()
            socket_command = start_command_connection()

            EXPERIMENT_DURATION = 1000
            dt=0

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
            WITH_BACK_TRAFFIC = False #random.choice([True, False])
            NODES_STATE_IPERF = ['TRAFFIC_OFF', 'TRAFFIC_OFF', 'TRAFFIC_OFF'] # TRAFFIC_ON, TRAFFIC_OFF
            NODES_STATE_HADOOP = ['HADOOP_ON', 'HADOOP_ON'] # HADOOP_ON, HADOOP_OFF
            global SYSTEM_STATE
            SYSTEM_STATE = ['MONITOR_NETWORK_ACTIVATION'] # MONITOR_NETWORK_ON, MONITOR_NETWORK_OFF, MONITOR_NETWORK_ACTIVATION, THOUGHPUT_ANALYSIS, DEACTIVATION_NODES
            MONITOR_TIME = 0
            global MONITOR_TIME_DURATION 
            MONITOR_TIME_DURATION = 10
            global deactivated 
            deactivated = False
            global node_deactivated
            node_deactivated = []
            global node_num
            node_num = 0

            while do_run:

                # WISHFUL STUFF
                socket_list = poller.poll(1000)
                #need to keep alive the control program, if do not present the remote control program will been closed
                lcpDescriptor_wmp_nodes[0].send({"alive": 1})
                #lcpDescriptor_wmp_nodes[1].send({"alive": 1})

                # TRAFFIC ACTIVATION PROCEDURE
                if SYSTEM_STATE[0] == 'MONITOR_NETWORK_ACTIVATION':
                    log.info(" ### MONITOR_NETWORK_ACTIVATION ###")
                    #blocking(False)
                    controller.delay(2).nodes(mytestbed.wmp_nodes[0]).net.start_packetflow('192.168.3.' + mytestbed.ap_node.ip.split('.')[3],
                                                                    '1234', '3000', '100M', '1300')
                    NODES_STATE_IPERF[0] = 'TRAFFIC_ON'
                    for i in range(2):
                        if WITH_BACK_TRAFFIC:
                            controller.delay(2).nodes(mytestbed.wmp_nodes1[i]).net.start_packetflow('192.168.4.' + mytestbed.ap_node1.ip.split('.')[3],
                                                                        '1234', '3000', '100M', '1300')
                            NODES_STATE_IPERF[1] = 'TRAFFIC_ON'
                            NODES_STATE_IPERF[2] = 'TRAFFIC_ON'

                        else:
                            if str(mytestbed.wmp_nodes1[i].ip) == '192.168.2.1':
                                controller.delay(2).nodes(mytestbed.wmp_nodes1[i]).net.start_packetflow('192.168.4.' + mytestbed.ap_node1.ip.split('.')[3],
                                                                        '1234', '3000', '100M', '1300')
                                NODES_STATE_IPERF[1] = 'TRAFFIC_ON'

                    SYSTEM_STATE[0] = 'MONITOR_NETWORK_ON'
                
                if SYSTEM_STATE[0] == 'MONITOR_NETWORK_ON' and counter_net1 > 5 and counter_net2 > 5 and MONITOR_TIME > MONITOR_TIME_DURATION:
                    # TRAFFIC DEACTIVATION
                    log.info("\nStop Client iperf traffic WiFiNet_1 . . .")
                    controller.nodes(mytestbed.wmp_nodes).net.stop_packetflow()
                    NODES_STATE_IPERF[0] = 'TRAFFIC_OFF'
                    
                    for i in range(2):
                        if WITH_BACK_TRAFFIC == False:
                            log.info("\nStop Client iperf traffic WiFiNet_2 . . .")
                            controller.nodes(mytestbed.wmp_nodes1).net.stop_packetflow()
                            NODES_STATE_IPERF[1] = 'TRAFFIC_OFF'
                            NODES_STATE_IPERF[2] = 'TRAFFIC_OFF'
                            break
                        else:
                            if str(mytestbed.wmp_nodes1[i].ip) == '192.168.2.1':
                                log.info("\nStop iperf traffic WiFiNet_2 . . .")
                                controller.nodes(mytestbed.wmp_nodes1[i]).net.stop_packetflow()
                                NODES_STATE_IPERF[1] = 'TRAFFIC_OFF'
                                break
                    
                    time.sleep(2)
                    SYSTEM_STATE[0] = 'THOUGHPUT_ANALYSIS'
                    

                # SYSTEM LOGIC
                if SYSTEM_STATE[0] == 'THOUGHPUT_ANALYSIS':
                    log.info(" ### THOUGHPUT_ANALYSIS ###")
                    # Take throughputs
                    (node1_throughput, node2_throughput) = get_nodes_throughputs()

                    log.info("\nThroughput extensa: " + str(node1_throughput[1]) + "\nThroughput nautilus: " + str(node2_throughput[1]))
                    log.info("\nModulation rate extensa: " + str(mod_rate1) + "\nModulation rate nautilus: " + str(mod_rate2))

                    # Nodes go down so they can't execute App tasks
                    if float(node1_throughput[1]) < (float(mod_rate1) / 2 * 0.70):
                        node_deactivated.append('nautilus')

                    if float(node2_throughput[1]) < (float(mod_rate2) / 2 * 0.70):
                        node_deactivated.append('extensa')

                    if len(node_deactivated) != 0:
                        SYSTEM_STATE[0] = 'DEACTIVATION_NODES'
                        deactivated = True
                    else:
                         SYSTEM_STATE[0] = 'NODE_NUMBER'
                    
                if SYSTEM_STATE[0] == 'DEACTIVATION_NODES':
                    log.info(" ### DEACTIVATION_NODES ###")
                    SYSTEM_STATE[0] = 'WORKING'
                    log.info("Deactivation nodes . . .")
                    for i in node_deactivated:
                        deactivate_node(i, wmp_node_tot)

                if SYSTEM_STATE[0] == 'NODE_NUMBER':
                    log.info(" ### NODE_NUMBER ###")
                    SYSTEM_STATE[0] = 'WORKING'
                    take_nodes_num = threading.Thread(target=get_nodes_num, args=())
                    take_nodes_num.start()

                if SYSTEM_STATE[0] == 'APPLICATION_EXECUTION':
                    # start thread for collect measurements from node
                    SYSTEM_STATE[0] = 'WORKING'
                    log.info("* ** * ** * ** START APPLICATION ** * ** * ** *")
                    current_running_applicatiton = threading.Thread(target=run_application, args=())
                    current_running_applicatiton.start()

                if SYSTEM_STATE[0] == 'RESTORATION_NODES':
                    log.info(" ### RESTORATION_NODES ###")
                    # Reset params
                    SYSTEM_STATE[0] = 'WORKING'

                    log.info("Restoartion nodes . . .")
                    for i in node_deactivated:
                        reactivate_node(i, wmp_node_tot)

                    node_deactivated = []

                #gevent.sleep(1)
                time.sleep(1)
               
                dt += 1
                MONITOR_TIME += 1
                if dt > EXPERIMENT_DURATION or SYSTEM_STATE[0] == 'END':
                    log.info("- - - - - - END - - - - - -")
                    log.info("- - - - - - - - - - - - - -")
                    log.info("WITH_BACK_TRAFFIC: " + str(WITH_BACK_TRAFFIC))
                    log.info("Throughput nodo 1: " + str(node1_throughput[1]))
                    log.info("Throughput nodo 2: " + str(node2_throughput[1]))
                    log.info("Modulation Rate nodo 1: " + str(mod_rate1))
                    log.info("Modulation Rate nodo 2: " + str(mod_rate2))
                    log.info("Numero di nodi: " + str(node_num))
                    break

            #destroy active traffic
            log.info("\nStop iperf traffic WiFiNet_1 . . .")
            controller.delay(2).nodes(mytestbed.ap_node).net.destroy_packetflow_sink()
            controller.delay(3).nodes(mytestbed.wmp_nodes).net.stop_packetflow()

            controller.delay(2).nodes(mytestbed.ap_node1).net.destroy_packetflow_sink()
            controller.delay(3).nodes(mytestbed.wmp_nodes1).net.stop_packetflow()
            
            #close remote local control program
            for ii in range(0,len(mytestbed.wmp_nodes)):
                print("Terminate remote local control program")
                lcpDescriptor_wmp_nodes[ii].close()

                print("Terminate receive thread")
                reading_thread[ii].do_run = False
                reading_thread[ii].join()

            break
        
    #hadoop_stop()




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