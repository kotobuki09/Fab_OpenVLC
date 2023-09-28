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
    import binascii
    import getopt, sys
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
    import socket
    import select
    import wishful_framework.upi_arg_classes.edca as edca
    from wishful_framework.classes import exceptions
    import upis.wishful_upis.meta_radio as radio
    from agent_modules.wifi_wmp.wmp_structure import UPI_R
    from agent_modules.wifi_wmp.wmp_structure import execution_engine_t
    from agent_modules.wifi_wmp.wmp_structure import radio_platform_t
    from agent_modules.wifi_wmp.wmp_structure import radio_info_t
    from agent_modules.wifi_wmp.wmp_structure import radio_program_t

    SUCCESS = 0
    FAILURE = 2

    #enable debug print
    debug = True
    debug_statistics = True
    dryRun = False

    starttime=time.time()
    neigh_list = {}
    pkt_stats= {}


    """
    interference recognition initialization
    """
    def init(iface):
        global my_mac
        my_mac=str(netifaces.ifaddresses(iface)[netifaces.AF_LINK][0]['addr'])

    def rcv_from_reading_program(reading_buffer):
        """
        This function collects the reading buffer information
        """
        reading_thread = threading.currentThread()
        print('start socket reading_program')

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        timeout = 1
        sock.setblocking(0)
        sock.bind(("127.0.0.1", 10001))
        # sock.bind(("10.8.9.13", 10001))

        # poller = select.epoll()
        # pollmask = select.EPOLLIN | select.EPOLLHUP | select.EPOLLERR
        # poller.register(sock, pollmask)
		#
        # while getattr(reading_thread, "do_run", True):
        #     # poll sockets
        #     try:
        #         fds = poller.poll(timeout=1)
        #     except:
        #         return
        #     for (fd, event) in fds:
        #         # handle errors
        #         if event & (select.POLLHUP | select.POLLERR):
        #             print("Error in SOCKET")
        #             continue
        #         # handle the server socket
        #         if fd == sock.fileno():
        #             try:
        #                 data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        #                 stats = json.loads(data.decode('utf-8'))
        #                 print(stats)
        #                 if "PDSCH-BLER" in stats:
        #                     reading_buffer[0] = (1 - (stats["PDSCH-BLER"]/100))
        #             except Exception as e:
        #                 print(e)
        #             continue
        #         reading_buffer[0] = 1

        while getattr(reading_thread, "do_run", True):
            # {'UE_ID': 0, 'type': 'ue0_stats', 'CFO': -0.624144, 'SNR': 21.99383, 'PDCCH-Miss': 39.999996, 'PDSCH-BLER': 21.0, 'timestamp': 1524493482.429576}
            # {'UE_ID': 0, 'type': 'ue0_stats', 'CFO': -0.442906, 'SNR': 17.325897, 'PDCCH-Miss': 39.999996, 'PDSCH-BLER': 21.1, 'timestamp': 1524493483.429576}
            # {'UE_ID': 0, 'type': 'ue0_stats', 'CFO': -0.698449, 'SNR': 29.657462, 'PDCCH-Miss': 39.999996, 'PDSCH-BLER': 20.5, 'timestamp': 1524493484.429552}
            try:
                ready = select.select([sock], [], [], timeout)
                if ready[0]:
                    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
                    stats = json.loads(data.decode('utf-8'))
                    print(stats)
                    if "PDCCH-Miss" in stats:
                        reading_buffer[0] = (1 - (stats["PDCCH-Miss"] / 100))
            except Exception as e:
                print(e)

        sock.close()
        print("stop socket reading_program")
        return



    # socket iperf pointer
    iperf_socket = None
    def rcv_from_iperf_socket(iperf_througputh):
        """
        This function collects the throughput information result
        """
        iperf_thread = threading.currentThread()
        print('start socket iperf')
        iperf_port = "8301"
        iperf_server_ip_address = "172.16.16.6"
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
            # parsed_json = iperf_socket.recv_json()
            if poller.poll(1000):  # 1s timeout in milliseconds
                parsed_json = iperf_socket.recv_json()
                # print('my address %s - parsed_json : %s' % (str(wlan_ip_address), str(parsed_json)))
                rcv_ip_address = parsed_json['ip_address']
                if rcv_ip_address == wlan_ip_address:
                    # print('parsed_json : %s' % str(parsed_json))
                    iperf_througputh[0] = float(parsed_json['throughput'])
            else:
                # raise IOError("Timeout processing auth request")
                iperf_througputh[0] = float(0)
                reading_buffer[0] = float(0)

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
                wlan_ip_address = controller.net.get_iface_ip_addr(interface[0])
                wlan_ip_address = wlan_ip_address[0]
                iperf_througputh = []
                iperf_througputh.append(0.0)
                iperf_thread = threading.Thread(target=rcv_from_iperf_socket, args=(iperf_througputh,))
                iperf_thread.do_run = True
                iperf_thread.start()
                # print(iperf_througputh)
                reading_buffer = []
                #reading_buffer.append([0.0])
                reading_buffer.append(0.0)
                reading_buffer_thread = threading.Thread(target=rcv_from_reading_program, args=(reading_buffer,))
                reading_buffer_thread.do_run = True
                reading_buffer_thread.start()

            except (Exception) as err:
                 if debug:
                     print( "exception", err)
                     print("Error: unable to start thread")
                 return
            break

    #CONTROLLER MAIN LOOP
    while not controller.is_stopped():
        msg = controller.recv(timeout=2)
        if msg:
            log.info("Receive message %s" % str(msg))
            if 'i_time' in msg:
                i_time[0] = msg['i_time']

        #send statistics to controller
        # if 'reading_time' in report_stats:
        if True:
            controller.send_upstream({"measure": [time.time(), iperf_througputh[0], reading_buffer[0] ],  "mac_address": (my_mac)})

    iperf_thread.do_run = False
    iperf_thread.join()

    reading_buffer_thread.do_run = False
    reading_buffer_thread.join()

    print("Local control program closed")
    time.sleep(1)
