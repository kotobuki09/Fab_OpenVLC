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
    sys.path.append('../../')
    sys.path.append("../../agent_modules/wifi_ath")
    sys.path.append("../../agent_modules/wifi_wmp")
    sys.path.append("../../agent_modules/wifi")
    sys.path.append("../../agent_modules/net_linux")
    sys.path.append('../../upis')
    sys.path.append('../../framework')
    sys.path.append('../../framework/wishful_framework/upi_arg_classes/')
    sys.path.append('../../agent')
    import math
    import scapy
    import binascii
    import getopt, sys
    import time
    import json
    import netifaces
    import zmq
    import re
    import signal

    import string, random
    import glob
    import subprocess
    import _thread
    import threading
    import logging
    import wishful_framework.upi_arg_classes.edca as edca
    from wishful_framework.classes import exceptions
    import upis.wishful_upis.meta_radio as radio
    import inspect

    #enable debug print
    debug = False
    debug_statistics = True

    starttime=time.time()

    neigh_list = {}
    pkt_stats= {}
    report_stats= {}


    mon_iface="mon0"

    MAX_THR=5140 #kbps
    #rate=0; #APP RATE

    """
    interference recognition initialization
    """
    def init(iface):
        global my_mac
        my_mac=str(netifaces.ifaddresses(iface)[netifaces.AF_LINK][0]['addr'])
        #setCW(iface,1,2,15,1023,0)
        #setCW(iface,3,1,3,7,0)

        report_stats['thr'] = 0
        report_stats['tx_attempts'] = 0
        report_stats['busy_time'] = 0
        report_stats['reading_time'] = 0

        report_stats['tx_activity'] = 0
        report_stats['num_tx'] = 0
        report_stats['num_tx_success'] = 0

    """
    get PHY name for current device
    """
    def getPHY(iface="wlan0"):
        phy="phy" + iface[4]
        return phy

    def rcv_from_reading_program(reading_buffer):
        """
        This function collects the reading buffer information
        """
        reading_thread = threading.currentThread()
        print('start socket reading_program')
        reading_port = "8901"
        reading_server_ip_address = "127.0.0.1"
        context = zmq.Context()
        reading_socket = context.socket(zmq.SUB)
        print("tcp://%s:%s" % (reading_server_ip_address, reading_port))
        reading_socket.connect("tcp://%s:%s" % (reading_server_ip_address, reading_port))
        reading_socket.setsockopt_string(zmq.SUBSCRIBE, '')

        print('socket reading_program started')
        while getattr(reading_thread, "do_run", True):
            parsed_json = reading_socket.recv_json()
            #print('parsed_json : %s' % ( str(parsed_json)))
            reading_buffer[0] = parsed_json['measure']

    # socket iperf pointer
    iperf_socket = None

    def rcv_from_iperf_socket(iperf_througputh):
        """
        This function collects the throughput information result
        """
        iperf_thread = threading.currentThread()
        print('start socket iperf')
        iperf_port = "8301"
        iperf_server_ip_address = "10.8.8.104"
        context = zmq.Context()
        iperf_socket = context.socket(zmq.SUB)
        print("tcp://%s:%s" % (iperf_server_ip_address, iperf_port))
        iperf_socket.connect("tcp://%s:%s" % (iperf_server_ip_address, iperf_port))
        iperf_socket.setsockopt_string(zmq.SUBSCRIBE, '')

        print('socket iperf started')
        while getattr(iperf_thread, "do_run", True):
            parsed_json = iperf_socket.recv_json()
            # print('my address %s - parsed_json : %s' % (str(wlan_ip_address), str(parsed_json)))
            rcv_ip_address = parsed_json['ip_address']
            if rcv_ip_address == wlan_ip_address:
                print('parsed_json : %s' % str(parsed_json))
                iperf_througputh[0] = float(parsed_json['throughput'])


    def reading_function(iface, time_interval):
        reading_thread = threading.currentThread()
        print('start reading_function')

        # CWMIN = 2
        # CWMAX = 1023
        # cw_ = 32

        busy_time = 0
        busy_time_ = 0
        tx_activity = 0
        tx_activity_ = 0
        num_tx = 0
        num_tx_ = 0
        num_tx_success = 0
        num_tx_success_ = 0
        rx_activity = 0
        rx_activity_ = 0
        ext_busy_time = 0
        ext_busy_time_ = 0

        # QUEUE CW SETTING
        qumId = 1  # BE
        #qumId = 2  # VI
        aifs = 2
        burst = 0

        phy = getPHY(iface)
        reading_interval = time_interval[0] # * 5
        #dd = time_interval[0]
        reading_time_ = 0

        reading_time = time.time()
        while (round(reading_time*10)%100) != 0:
            time.sleep(0.1)
            reading_time = time.time()
        local_starttime = reading_time

        while getattr(reading_thread, "do_run", True):
            #[pkt_stats, reading_time] = get_ieee80211_stats(phy)
            # UPIargs = {'parameters': [radio.BUSY_TIME.key, radio.EXT_BUSY_TIME.key, radio.TX_ACTIVITY.key, radio.NUM_TX.key, radio.NUM_TX_SUCCESS.key, radio.RX_ACTIVITY.key]}
            # UPIargs = {'parameters': [radio.BUSY_TIME.key, radio.EXT_BUSY_TIME.key, radio.TX_ACTIVITY.key, radio.RX_ACTIVITY.key]}
            UPIargs = {'parameters': [radio.NUM_TX_SUCCESS.key, radio.NUM_TX.key]}
            #pkt_stats = controller.radio.get_parameters(UPIargs)
            #print(pkt_stats)
            reading_time = time.time()
            if pkt_stats:
                if True:
                    dd = float(reading_time - reading_time_)

                    # busy_time = pkt_stats[radio.BUSY_TIME.key] - busy_time_
                    # ext_busy_time = pkt_stats[radio.EXT_BUSY_TIME.key] - ext_busy_time_
                    # tx_activity = pkt_stats[radio.TX_ACTIVITY.key] - tx_activity_
                    # rx_activity = pkt_stats[radio.RX_ACTIVITY.key] - rx_activity_
                    # num_tx = pkt_stats[radio.NUM_TX.key] - num_tx_
                    # num_tx_success = pkt_stats[radio.NUM_TX_SUCCESS.key] - num_tx_success_
                    #
                    # busy_time_ = pkt_stats[radio.BUSY_TIME.key]
                    # ext_busy_time_ = pkt_stats[radio.EXT_BUSY_TIME.key]
                    # tx_activity_ = pkt_stats[radio.TX_ACTIVITY.key]
                    # rx_activity_ = pkt_stats[radio.RX_ACTIVITY.key]
                    # num_tx_ = pkt_stats[radio.NUM_TX.key]
                    # num_tx_success_ = pkt_stats[radio.NUM_TX_SUCCESS.key]

                    busy_time_ = 0
                    ext_busy_time_ = 0
                    tx_activity_ = 0
                    rx_activity_ = 0
                    num_tx_ = 0
                    num_tx_success_ = 0

                if debug or debug_statistics:
                    # if debug_cycle > 3:
                    if True:
                        print(
                            "%.6f - busytime=%.4f ext_busy_time=%.4f tx_activity=%.4f rx_activity=%.4f num_tx=%.4f num_tx_success=%.4f\n" % (
                            reading_time, busy_time, ext_busy_time, tx_activity, rx_activity, num_tx, num_tx_success))
                        debug_cycle = 0
                    else:
                        debug_cycle += 1

                # store statistics for report
                report_stats['reading_time'] = reading_time

                report_stats['busy_time'] = busy_time
                report_stats['tx_activity'] = tx_activity
                report_stats['num_tx'] = num_tx
                report_stats['num_tx_success'] = num_tx_success

            time.sleep(reading_interval - ((time.time() - local_starttime) % reading_interval))

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


    log = logging.getLogger()
    log.info('*********** WISHFUL *************')
    log.info('*********** starting local WiSHFUL controller **********************')
    msg={}

    print("Local ctrl program started: {}".format(controller.name))
    distributed = False
    cycle_1 = 0
    while not controller.is_stopped():
        msg = controller.recv(timeout=1)
        if msg:
            print("START main function")
            #INIT
            init(msg["iface"])
            try:

                i_time = []
                if 'i_time' in msg:
                    i_time.append(msg['i_time'])

                interface = []
                interface.append(msg['iface'])
                if interface[0] == 'wlan2':
                    interface[0] = 'eth1'
                wlan_ip_address = controller.net.get_iface_ip_addr(interface[0])
                wlan_ip_address = wlan_ip_address[0]

                #read function starting
                # reading_thread = threading.Thread(target=reading_function, args=(msg['iface'], i_time))
                # reading_thread.do_run = True
                # reading_thread.start()

                iperf_througputh = []
                iperf_througputh.append(0.0)
                # iperf_thread = threading.Thread(target=rcv_from_iperf_socket, args=(iperf_througputh,))
                # iperf_thread.do_run = True
                # iperf_thread.start()

                reading_buffer = []
                reading_buffer.append([[0.0]])
                reading_buffer_thread = threading.Thread(target=rcv_from_reading_program, args=(reading_buffer,))
                reading_buffer_thread.do_run = True
                reading_buffer_thread.start()

            except (Exception) as err:
                if debug:
                    print ( "exception", err)
                    print ("Error: unable to start thread")
                pass
            break

    #CONTROLLER MAIN LOOP
    while not controller.is_stopped():
        msg = controller.recv(timeout=1)
        if msg:
            print('0')
            log.info("Receive message %s" % str(msg))
            if 'i_time' in msg:
                i_time[0] = msg['i_time']
            # {'command': 'set_wave', 'type': 'microwave'}
            if 'type' in msg:
                if msg['type'] == 'microwave' and 'command' in msg:
                    if msg['command'] == 'set_wave':
                        cmd_string = "./station-conf/writing-tool/send_uwave.py &"
                    else:
                        cmd_string = "killall -9 python2"
                    print(cmd_string)
                    try:
                        # [rcode, sout, serr] = run_command(cmd_string)
                        # cmd_result = json.loads(sout)
                        run_command(cmd_string)
                    except Exception as e:
                        fname = inspect.currentframe().f_code.co_name
                        print("An error occurred in %s: %s survey_enable error" % (fname, e))
                        raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))

        #send statistics to controller
        if 'reading_time' in report_stats:
            # controller.send_upstream({"measure": [[report_stats['reading_time'], report_stats['busy_time'], report_stats['tx_activity'], report_stats['num_tx'], report_stats['num_tx_success']]], "mac_address": (my_mac)})
            # controller.send_upstream({"measure": [[report_stats['reading_time'], reading_buffer[0], report_stats['num_tx'], report_stats['num_tx_success']]], "mac_address": (my_mac)})
            controller.send_upstream({"measure": [reading_buffer[0], iperf_througputh[0]], "mac_address": (my_mac)})

    # reading_thread.do_run = False
    # reading_thread.join()
    reading_buffer_thread.do_run = False
    reading_buffer_thread.join()
    time.sleep(2)
