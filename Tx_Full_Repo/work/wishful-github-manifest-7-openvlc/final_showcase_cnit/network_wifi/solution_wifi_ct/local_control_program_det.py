"""
Local control program to be executed on remote nodes.
"""
__author__ = "Domenico Garlisi, Pierluigi Gallo"
__copyright__ = "Copyright (c) 2016, CNIT"
__version__ = "0.1.0"
__email__ = "domenico.garlisi@cnit.it; pierluigi.gallo@unipa.it"


# Definition of Local Control Program
def remote_control_program(controller):
    import sys
    import math
    sys.path.append('../../')
    sys.path.append("../../agent_modules/wifi_ath")
    sys.path.append("../../agent_modules/wifi_wmp")
    sys.path.append("../../agent_modules/wifi")
    sys.path.append("../../agent_modules/net_linux")
    sys.path.append('../../upis')
    sys.path.append('../../framework')
    sys.path.append('../../framework/wishful_framework/upi_arg_classes/')
    sys.path.append('../../agent')
    import binascii
    import getopt
    import time
    import json
    import netifaces
    import zmq
    import string, random
    import subprocess
    import _thread
    import threading
    import logging
    import numpy as np
    import array
    import socket

    import wishful_framework.upi_arg_classes.edca as edca
    from wishful_framework.classes import exceptions
    import upis.wishful_upis.meta_radio as radio
    from agent_modules.wifi_wmp.wmp_structure import UPI_R
    from agent_modules.wifi_wmp.wmp_structure import execution_engine_t
    from agent_modules.wifi_wmp.wmp_structure import radio_platform_t
    from agent_modules.wifi_wmp.wmp_structure import radio_info_t
    from agent_modules.wifi_wmp.wmp_structure import radio_program_t
    from helper.b43_library.libb43 import B43

    SUCCESS = 0
    FAILURE = 2

    MAC_TABLE_4	= 53
    MAC_TABLE_3	= 52
    MAC_TABLE_2	= 51
    MAC_TABLE_1	= 50
    MAC_TABLE_0	= 49

    """
    interference recognition initialization
    """
    def init(iface):
        global my_mac
        my_mac=str(netifaces.ifaddresses(iface)[netifaces.AF_LINK][0]['addr'])

    """
    get PHY name for current device
    """
    def getPHY(iface="wlan0"):
        phy="phy" + iface[4]
        return phy


    # socket iperf pointer
    iperf_socket = None
    def rcv_from_iperf_socket(iperf_througputh):
        """
        This function collects the throughput information result
        """
        iperf_thread = threading.currentThread()
        print('start socket iperf')
        iperf_port = "8301"
        #iperf_server_ip_address = "10.8.8.102"
        iperf_server_ip_address = "172.16.16.31"
        context = zmq.Context()
        iperf_socket = context.socket(zmq.SUB)
        print("tcp://%s:%s" % (iperf_server_ip_address, iperf_port))
        iperf_socket.connect("tcp://%s:%s" % (iperf_server_ip_address, iperf_port))
        iperf_socket.setsockopt_string(zmq.SUBSCRIBE, '')

        # use poll for timeouts:
        poller = zmq.Poller()
        poller.register(iperf_socket, zmq.POLLIN)

        print('socket iperf started')
        while getattr(iperf_thread, "do_run", True):
            if poller.poll(1000):  # 1s timeout in milliseconds
                parsed_json = iperf_socket.recv_json()
                #print('my address %s - parsed_json : %s' % (str(wlan_ip_address), str(parsed_json)))
                rcv_ip_address = parsed_json['ip_address']
                if rcv_ip_address == wlan_ip_address:
                    # print('parsed_json : %s' % str(parsed_json))
                    iperf_througputh[0] = float(parsed_json['throughput'])
                    iperf_througputh[1] = float(float(parsed_json['per'])/100)
            else:
                # raise IOError("Timeout processing auth request")
                iperf_througputh[0] = float(0)
                iperf_througputh[1] = float(0)


    def set_mactable(b43, table_id):
        #print(table_id)
        b43.shmWrite16(b43.B43_SHM_REGS, MAC_TABLE_2, table_id[0])
        b43.shmWrite16(b43.B43_SHM_REGS, MAC_TABLE_3, table_id[1])
        b43.shmWrite16(b43.B43_SHM_REGS, MAC_TABLE_4, table_id[2])


    def run_command(command):
        '''
            Method to start the shell commands and get the output as iterater object
        '''
        sp = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # sp = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # out, err = sp.communicate()
        # if True:
        #     if out:
        #         log.debug("standard output of subprocess:")
        #         log.debug(out)
        #     if err:
        #         log.debug("standard error of subprocess:")
        #         log.debug(err)
        # return [sp.returncode, out.decode("utf-8"), err.decode("utf-8")]
        return

    """
    MAIN
    """
    log = logging.getLogger()
    log.info('*********** WISHFUL *************')
    log.info('*********** starting local WiSHFUL controller **********************')
    msg={}

    print("Local ctrl program started: {}".format(controller.name))

    b43_phy = None
    b43 = B43(b43_phy)
    num_tx_ = 0
    num_tx_success_ = 0

    while not controller.is_stopped():
        msg = controller.recv(timeout=1)
        if msg:
            print("START main function")
            #INIT
            init(msg["iface"])

            i_time = []
            if 'i_time' in msg:
                i_time.append(msg['i_time'])

            interface = []
            interface.append(msg['iface'])
            if interface[0] == 'wlan2':
                interface[0] = 'eth1'
            wlan_ip_address = controller.net.get_iface_ip_addr(interface[0])
            wlan_ip_address = wlan_ip_address[0]

            iperf_througputh = []
            iperf_througputh.append(0.0)
            iperf_througputh.append(0.0)
            iperf_thread = threading.Thread(target=rcv_from_iperf_socket, args=(iperf_througputh,))
            iperf_thread.do_run = True
            iperf_thread.start()

            break

    #CONTROLLER MAIN LOOP
    while not controller.is_stopped():
        msg = controller.recv(timeout=2)
        if msg:
            log.info("Receive message %s" % str(msg))
            if 'i_time' in msg:
                i_time[0] = msg['i_time']

            if 'table_id' in msg:
                table_id = msg["table_id"]
                set_mactable(b43, table_id)

        #send statistics to controller
        UPI_myargs = {'interface': interface, 'measurements': [UPI_R.NUM_TX_DATA_FRAME, UPI_R.NUM_RX_ACK_RAMATCH]}
        node_measures = controller.radio.get_measurements(UPI_myargs)
        num_tx = node_measures[0] - num_tx_
        num_tx_success = node_measures[1] - num_tx_success_
        num_tx_ = node_measures[0]
        num_tx_success_ = node_measures[1]
        # print(pkt_stats)
        controller.send_upstream({"measure": [time.time(), iperf_througputh[0], iperf_througputh[1], num_tx, num_tx_success], "mac_address": (my_mac)})

    iperf_thread.do_run = False
    iperf_thread.join()
    time.sleep(2)