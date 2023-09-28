#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
global_controller.py: Contiki global control program

Usage:
   global_controller.py [options] [-q | -v]

Options:
   --config configFile Config directory path
   --cca_threshold cca_threshold CCA threshold of the sensor nodes
   --tx_power tx_power Tx power of the sensor nodes
   --solution_controller solution_controller IP address of the solution controller

Example:
   python global_controller.py --config config/portable

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""

__author__ = "Jan Bauwens & Peter Ruckebusch"
__copyright__ = "Copyright (c) ugent - idlab - imec"
__version__ = "0.1.0"
__email__ = "jan.bauwens2@ugent.be; peter.ruckebusch@ugent.be"

import datetime
import time
import logging
import gevent
import yaml
import sys
import math

from contiki.contiki_helpers.global_node_manager import *
from contiki.contiki_helpers.taisc_manager import *
from contiki.contiki_helpers.app_manager import *
from lib.global_controller_proxy import GlobalSolutionControllerProxy

## GLOBALS:
taisc_manager = None
app_manager = None
global_node_manager = None
solutionCtrProxy = None
tdma_channel = 23
channel_update = tdma_channel
cca_threshold = -80
cca_threshold_update = cca_threshold
blacklisted_channels = []
blacklisted_channels_timestamps = [0] * 16
wifi_to_tsch_channels_dct = {}
per_dictionary = {}
number_of_packets_received = 0
traffic_type = {"TYPE":"OFF"}
mac_mode = "TSCH"
lte_wifi_coexistence_enabled = 0
hopping_sequence = []
expected_throughput = sys.maxsize
payload = 128
software_reset = 0

# Adapt this to change the minimal duty cycle of external interference, 
# before the corresponding frequency range will be blacklisted
interference_blacklist_threshold = 0.25
# 0 = OFF
# 1 = LOW
# 2 = MEDIUM
# 3 = HIGH

## CALLBACKS:
def default_callback(group, node, cmd, data):
    print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(datetime.datetime.now(), group, node.name, cmd, data))

def print_response(group, node, data):
    print("{} Print response : Group:{}, NodeIP:{}, Result:{}".format(datetime.datetime.now(), group, node.ip, data))

# PER:
# Keep track on the number of failed packets
# Dictionary with:
# - keys = node id's
# - values = [ number_of_packets_requested_prev, number_of_packets_success_prev, number_of_packets_requested, number_of_packets_success,  ]
per_value_prev = 0
watchdog_counter = {}
def macstats_event_cb(mac_address, event_name, event_value):
    global solutionCtrProxy, number_of_packets_received, per_value_prev, \
        expected_throughput, payload, watch_dog, traffic_type, mac_mode
    print(mac_address, event_name, event_value)
    if mac_address == 1:
        number_of_packets_received_cur = event_value[10]
        number_of_packets_requested = 0
        number_of_packets_transmitted = 0
        for node_id in per_dictionary.keys():
            number_of_packets_requested += per_dictionary[node_id][2] - per_dictionary[node_id][0]
            number_of_packets_transmitted += per_dictionary[node_id][3] - per_dictionary[node_id][1]
        if number_of_packets_requested != 0:
            per_value = (
                (expected_throughput - number_of_packets_transmitted) 
                / expected_throughput
                + per_value_prev) * 1.0
            if per_value < 0:
                per_value_prev = 0
                per_value = 0
            else:
                per_value_prev = 0
        else:
            per_value = 0

        value = { 
            "THR":  (number_of_packets_received_cur - number_of_packets_received) * payload * 8 * 1000000 / event_value[0],
            "PER":  1 - per_value,
            "timestamp" : time.time()
        }
        solutionCtrProxy.send_monitor_report("performance", "6lowPAN", value)
        number_of_packets_received = number_of_packets_received_cur
        throughput_measurement = value["THR"]
    else:
        if mac_address not in per_dictionary:
            per_dictionary[mac_address] = [0,0,0,0]
        per_dictionary[mac_address][0] = per_dictionary[mac_address][2] 
        per_dictionary[mac_address][2] = event_value[1]
        if per_dictionary[mac_address][3] != event_value[4]:
            per_dictionary[mac_address][1] = per_dictionary[mac_address][3] 
            per_dictionary[mac_address][3] = event_value[4]
        throughput_measurement = per_dictionary[mac_address][2] - per_dictionary[mac_address][0]

    # Watchdog implementation:   
    if (mac_address in watchdog_counter 
            and throughput_measurement == 0
            and traffic_type["TYPE"].lower() != "off"):
        watchdog_counter[mac_address] +=1
        if mac_mode != "LTE_COEXISTENCE": # or mac_address == 1:
            print("WDT {}".format(watchdog_counter[mac_address]))
            if watchdog_counter[mac_address] == 60:
                watchdog_counter[mac_address] = 0
                reset()
    else:
        watchdog_counter[mac_address] = 0            

## HELPER functions:
def get_new_hopping_sequence(default_hopping_sequence, blacklisted_channels):
    new_hopping_sequence = []
    index = 0
    for channel in default_hopping_sequence:
        if channel not in blacklisted_channels:
            new_hopping_sequence.append(channel)
    return new_hopping_sequence

def mapWifiOnZigbeeChannels(log, channel_mapping):
    dct = {}
    try:
        file_n = open(channel_mapping, 'rt')
        import csv
        reader = csv.DictReader(file_n)
        for row in reader:
            dct[int(row["ieee80211"])] = []
            for x in row["ieee802154"].split('-'):
                dct[int(row["ieee80211"])].append(int(x))
    except Exception as e:
        logging.fatal("An error occurred while reading nodes: %s" % e)
    finally:
        file_n.close()
    return dct

def send_channel_update(channels):
    channelisation = { 
        11: { "2405" : "2" },
        12: { "2410" : "2" },
        13: { "2415" : "2" },
        14: { "2420" : "2" },
        15: { "2425" : "2" },
        16: { "2430" : "2" },
        17: { "2435" : "2" },
        18: { "2440" : "2" },
        19: { "2445" : "2" },
        20: { "2450" : "2" },
        21: { "2455" : "2" },
        22: { "2460" : "2" },
        23: { "2465" : "2" },
        24: { "2470" : "2" },
        25: { "2475" : "2" },
        26: { "2480" : "2" }
    }
    
    update_value = {
        "channels" : [],
        "frequencies" : {}
    }
    
    for channel in channels:
        update_value["channels"].extend([channel])
        update_value["frequencies"].update(channelisation[channel])
    update_value["channels"].sort()
    print(update_value)
       
    solutionCtrProxy.send_monitor_report("channelUsage", "6lowPAN", update_value)

def control_traffic(traffic_type):  
    global mac_mode, taisc_manager, expected_throughput, payload
    
    traffic_types = {
        "LOW": 1,
        "MEDIUM": 5,
        "HIGH": 10,
    }

    # Disable all applications:    
    taisc_manager.update_macconfiguration({'TAISC_PG_ACTIVE' : 0})

    if traffic_type["TYPE"] in traffic_types:
        traffic_amount = traffic_types[traffic_type["TYPE"]]
        # Select the server and client nodes based on MAC mode + calculate the maximum possible inter packet delay per node
        if mac_mode == "TSCH":
            server_nodes = [1]
            client_nodes = range(2,len(global_node_manager.get_mac_address_list())+1)
            slot_length = taisc_manager.read_macconfiguration(["IEEE802154e_macTsTimeslotLength"], 1)
            logging.error(slot_length)
            send_interval = int(math.floor(
                slot_length[1]["IEEE802154e_macTsTimeslotLength"] 
                * (len(global_node_manager.get_mac_address_list()) + 2) # Superframe size (beacon, upstream, downstream+)
                / 1000 * max(traffic_types.values()) / traffic_amount))
            expected_throughput = 1000/send_interval * (len(global_node_manager.get_mac_address_list()) - 1)
            payload = 128

            print(taisc_manager.update_macconfiguration(
                {"TAISC_PG_INTERVAL": send_interval,
                "TAISC_PG_PAYLOAD": payload - 25,
                'TAISC_PG_ACTIVE' : 1}, client_nodes))
           
        elif mac_mode == "LTE_COEXISTENCE":
            server_nodes = [1]
            idle_nodes = [2]
            client_nodes = [3]
            send_interval = int(5 * max(traffic_types.values()) / traffic_amount)
            expected_throughput = 100
            payload = 50
            print(taisc_manager.update_macconfiguration(
                {"TAISC_PG_INTERVAL": send_interval,
                "TAISC_PG_PAYLOAD": payload - 25,
                'TAISC_PG_ACTIVE' : 1}, client_nodes))
            print(taisc_manager.update_macconfiguration(
                {"TAISC_PG_INTERVAL": 0,
                "TAISC_PG_PAYLOAD": payload - 25,
                'TAISC_PG_ACTIVE' : 0}, idle_nodes))
        print("Send interval is {}".format(send_interval))
        print("Expected packet rate {}".format(expected_throughput))

    else:
        # De-activate:
        logging.info("Stopping   {}".format(global_node_manager.get_mac_address_list()))
        app_manager.update_configuration({"app_activate": 0},global_node_manager.get_mac_address_list())
        
def reset():
    app_manager.update_configuration({"PERFORM_NODE_RESET" : 1}, global_node_manager.get_mac_address_list())
    gevent.sleep(5)
    app_manager.rpl_set_border_router([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01],1)
    gevent.sleep(1)
    # Update the TSCH configuration:
    contiki_nodes = global_node_manager.get_mac_address_list()
    logging.info("Connected nodes {}".format([str(node) for node in contiki_nodes]))

    mac_mode = "TSCH"
    taisc_manager.activate_radio_program(mac_mode)
    taisc_manager.update_slotframe('taisc_slotframe.csv', mac_mode)
    taisc_manager.update_macconfiguration({'IEEE802154e_macSlotframeSize': len(contiki_nodes) + 1})
    taisc_manager.subscribe_events(["IEEE802154_event_macStats"], macstats_event_cb, 0)
    taisc_manager.update_hopping_sequence_from_list(hopping_sequence)
    taisc_manager.update_macconfiguration({'IEEE802154_phyCurrentChannel': tdma_channel})
    taisc_manager.update_macconfiguration({'TAISC_ccaThres': cca_threshold}) 
    control_traffic(traffic_type)

## Commands implementation:
channel_update_counter = 0
def blacklist(spectrum_scan):
    global blacklisted_channels, blacklisted_channels_timestamps, \
        channel_update_counter, interference_blacklist_threshold
    blacklisted_channels_prev = blacklisted_channels
    blacklisted_channels = []
    
    # This next part will periodically the blacklisted_channels_prev in 
    # an attempt to stop the blacklisting getting stuck
    channel_update_counter += 1
    if channel_update_counter == 60:
        blacklisted_channels_prev = []
    
    for technology in spectrum_scan:
        if technology != "ZigBee":
            interference = spectrum_scan[technology]
            for interference_center, interference_information in interference.items():
                interference_center = float(interference_center)
                interference_bandwidth = float(interference_information[0])
                interference_dutycycle = float(interference_information[1])
                #~ logging.info("INTERFERENCE ({}): {} {} {}".format(technology,interference_center, interference_bandwidth, interference_dutycycle))
                if interference_dutycycle > interference_blacklist_threshold:
                    for sicslowpan_channel in range(11,27):
                        center_frequency = 2350 + sicslowpan_channel * 5
                        if (center_frequency > interference_center - interference_bandwidth/2
                                and center_frequency < interference_center + interference_bandwidth/2):
                            if sicslowpan_channel not in blacklisted_channels:
                                blacklisted_channels.append(sicslowpan_channel)
                                blacklisted_channels_timestamps[sicslowpan_channel - 11] = time.time() 
    logging.info("New blacklist {}".format(blacklisted_channels))
    for channel in blacklisted_channels_prev:
        if channel not in blacklisted_channels:
            if time.time() < blacklisted_channels_timestamps[channel - 11] + 20:
                blacklisted_channels.append(channel)      
    logging.info("BLACKLIST {}".format(blacklisted_channels))

def sicslowpan_traffic(traffic_type_value):
    global traffic_type
    traffic_type = traffic_type_value

def sicslowpan_traffic_enable(NO_PARAM):
    sicslowpan_traffic({"TYPE": "HIGH"})
    
def sicslowpan_traffic_disable(NO_PARAM):
    sicslowpan_traffic({"TYPE": "OFF"})

def lte_wifi_coexistence(NO_PARAM):
    global lte_wifi_coexistence_enabled
    lte_wifi_coexistence_enabled = True
    logging.info("ZIGBEE-LTE-WIFI coexistence enabled")
    
def enable_tsch(NO_PARAM):
    global lte_wifi_coexistence_enabled
    lte_wifi_coexistence_enabled = False
    logging.info("TSCH enabled")
    
    
def set_channel(channel):
    global channel_update
    channel_update = channel
    
def set_cca_threshold(cca_threshold):
    global cca_threshold_update
    cca_threshold_update = cca_threshold 
 
    
def set_tx_power(tx_power):
    global tx_power_update
    tx_power_update = tx_power

def perform_software_reset(NO_PARAM):
    global software_reset
    software_reset = 1
    
## MAIN functionality:
def main(args):
    global solutionCtrProxy, blacklisted_channels, \
        mac_mode, channel_update, tdma_channel, cca_threshold_update, \
        cca_threshold, tx_power_update, hopping_sequence, software_reset
    # Init logging
    logging.debug(args)
    logging.info('******     WISHFUL  *****')
    logging.info('****** Starting solution (network_zigbee) ******')


    # Update the TSCH configuration:
    contiki_nodes = global_node_manager.get_mac_address_list()
    logging.info("Connected nodes {}".format([str(node) for node in contiki_nodes]))
    
    mac_mode = "TSCH"
    taisc_manager.activate_radio_program(mac_mode)
    taisc_manager.update_slotframe('taisc_slotframe.csv', mac_mode)
    taisc_manager.update_macconfiguration({'IEEE802154e_macSlotframeSize': len(contiki_nodes) + 1})
    
    # Read the default hopping sequence:
    hopping_sequence = read_taisc_hoppingsequence("default_tsch_hopping_sequence.csv")
    taisc_manager.update_hopping_sequence_from_list(hopping_sequence)
    logging.info("Hopping sequence is {}".format(hopping_sequence))
    logging.info("Finished configuring TSCH")
    
    current_traffic_type = traffic_type
    
    """
    ****** setup the communication with the solution global controller ******
    """

    networkName = "6lowPAN"
    networkType = 'IEEE 802.15.4'
    solutionName = ["blacklisting"]
    commands = {
        "6LOWPAN_BLACKLIST": blacklist,
        "ENABLE_TRAFFIC": sicslowpan_traffic_enable,
        "DISABLE_TRAFFIC": sicslowpan_traffic_disable,
        "LTE_WIFI_ZIGBEE": lte_wifi_coexistence,
        "ENABLE_TSCH" : enable_tsch,
        "CHANNEL" : set_channel,
        "SOFTWARE_RESET" : perform_software_reset,
        "CCA_THRESHOLD" : set_cca_threshold
    }
    monitorList = ["6lowpan-THR", "6lowpan-PER"]
    solutionCtrProxy.set_solution_attributes(networkName, networkType, solutionName, commands, monitorList)

    # Register network_zigbee solution to global solution controller
    response = solutionCtrProxy.register_solution()
    if response:
        logging.info("Solution was correctly registered to GlobalSolutionController")
        solutionCtrProxy.start_command_listener()
    else:
        logging.error("Solution was not registered to Global Solution Controller")
        
    send_channel_update(hopping_sequence)
    current_hopping_sequence = hopping_sequence
    new_hopping_sequence = hopping_sequence

    """
    ****** MAIN LOOP ******
    """
    while True:
        if software_reset:
            reset()
            software_reset = 0
        else:
            new_hopping_sequence = get_new_hopping_sequence(hopping_sequence, blacklisted_channels)
            if set(new_hopping_sequence) != set(current_hopping_sequence):
                if len(new_hopping_sequence) == 0:
                    # If all channels are blacklisted --> use the channel for TDMA purposes 
                    #(TSCH becomes TDMA with a single channel)
                    new_hopping_sequence.append(tdma_channel)
                taisc_manager.update_hopping_sequence_from_list(new_hopping_sequence)
                current_hopping_sequence = new_hopping_sequence
                send_channel_update(current_hopping_sequence)
            if current_traffic_type != traffic_type:
                control_traffic(traffic_type)
                current_traffic_type = traffic_type
            if lte_wifi_coexistence_enabled and mac_mode != "LTE_COEXISTENCE":
                mac_mode = "LTE_COEXISTENCE"
                taisc_manager.update_macconfiguration({'IEEE802154_phyCurrentChannel': tdma_channel})
                taisc_manager.activate_radio_program(mac_mode)
                send_channel_update([tdma_channel])
                control_traffic(current_traffic_type)
            if not lte_wifi_coexistence_enabled and mac_mode == "LTE_COEXISTENCE":
                mac_mode = "TSCH"
                send_channel_update([11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26])
                taisc_manager.activate_radio_program(mac_mode)
                control_traffic(current_traffic_type)
            if channel_update != tdma_channel:
                tdma_channel = channel_update
                taisc_manager.update_macconfiguration({'IEEE802154_phyCurrentChannel': tdma_channel})
                if mac_mode == "LTE_COEXISTENCE":
                    send_channel_update([tdma_channel])
            if cca_threshold_update != cca_threshold:
                cca_threshold = cca_threshold_update
                taisc_manager.update_macconfiguration({'TAISC_ccaThres': cca_threshold})            

        gevent.sleep(1)
    logging.info('Controller Exiting')
    sys.exit()

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

    args = docopt(__doc__, version=__version__)
    
    # Logging:
    if args['--verbose']:
        log_level = logging.DEBUG
    elif args['--quiet']:
        log_level = logging.ERROR
    else:
        log_level = logging.INFO  # default

    logfile = None

    if '--logfile' in args:
        logfile = args['--logfile']

    if "--cca_threshold" in args and args["--cca_threshold"] is not None:
        cca_threshold = int(args['--cca_threshold'])
    else:
        cca_threshold = -75
        
    
    if "--tx_power" in args and args["--tx_power"] is not None:
        tx_power = int(args['--tx_power'])
    else:
        tx_power = 20
        
    if "--solution_controller" in args and args["--solution_controller"] is not None:
        solution_controller = args['--solution_controller']
    else:
        solution_controller = "172.16.16.12"
    print(solution_controller)
    solutionCtrProxy = GlobalSolutionControllerProxy(ip_address=solution_controller, requestPort=7001, subPort=7000)
        

    logging.basicConfig(filename=logfile, level=log_level,
        format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

    # Set the paths:
    config_file_path = "{}/global_config.yaml".format(args['--config'])
    nodes_file_path = "{}/nodes.yaml".format(args['--config'])

    # Load the config file:
    global_controller_config = None
    with open(config_file_path, 'r') as file_handler:
        global_controller_config = yaml.load(file_handler)
    
    # Configure the node manager:
    global_node_manager = GlobalNodeManager(global_controller_config)
    global_node_manager.set_default_callback(default_callback)

    # Wait for all agents to connect to the global controller:
    with open(nodes_file_path, 'r') as file_handler:
        node_config = yaml.load(file_handler)
    global_node_manager.wait_for_agents(node_config['ip_address_list'])
    
    # Configure the helpers:   
    taisc_manager = TAISCMACManager(global_node_manager, mac_mode)
    app_manager = AppManager(global_node_manager)
    
    # Create blacklisting dict:
    wifi_to_tsch_channels_dct = mapWifiOnZigbeeChannels(logging, 'ieee80211_to_ieee802154_channels.csv')
    
    # Set RPL border router:
    app_manager.rpl_set_border_router([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01],1)
    
    # Setting the transmission power and cca threshold:
    taisc_manager.update_macconfiguration({
        'IEEE802154_phyTXPower' : tx_power,
        'TAISC_ccaThres' : cca_threshold
    })

    # Set the event callback:
    logging.info("Start local monitoring cp and events")
    global_node_manager.start_local_monitoring_cp()
    gevent.sleep(1)
    taisc_manager.subscribe_events(["IEEE802154_event_macStats"], macstats_event_cb, 0)

    # Start MAIN functionality:
    try:
        main(args)
        print('End main')
    except KeyboardInterrupt:
        logging.debug("Controller exits")
    finally:
        logging.debug("Exit")
        global_node_manager.stop()
