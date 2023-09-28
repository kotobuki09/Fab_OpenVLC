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

    #enable debug print
    debug = False
    debug_statistics = True
    dryRun = False

    starttime=time.time()
    neigh_list = {}
    pkt_stats= {}
    report_stats= {}

    mon_iface="mon0"

    #UDP_IP = "10.8.9.13"
    UDP_IP = "172.16.16.11"
    UDP_PORT = 8888

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


    def shift(l, n):
        return l[n:] + l[:n]


    def update_pattern(mask_int, L, est_slot):
        mask_sum = 0
        n_shift = 0
        for x in list(mask_int):
            mask_sum += x

        target_mask = [1] * mask_sum + [0] * (L - mask_sum)
        #print("target_mask={}".format(target_mask))
        #print("mask_int={}".format(mask_int))

        while n_shift < L:
            if mask_int != target_mask:
                mask_int = shift(mask_int, -1)
                n_shift = n_shift + 1
            else:
                break

        if n_shift < L:
            if mask_sum < est_slot and est_slot < L:
                """
                print("---------")
                print(mask_int)
                print(mask_sum)
                print(est_slot)
                print("---------")
                """
                for i_mask in range(mask_sum, est_slot):
                    # print(i_mask)
                    mask_int[i_mask] = 1

                mask_int = shift(mask_int, n_shift - (mask_sum - est_slot))
        #print("mask_int={}".format(mask_int))
        return mask_int


    def find_airtime(tdma_mask_output, tdma_mask_array, index_pattern_finded, AIR_TIME, AIR_TIME_LTE, LTE_PATTERN_STATE, enb_lte_pattern_sock, reading_buffer):

        print("AIRTIME : ", AIR_TIME, " AIR_TIME_LTE : ", AIR_TIME_LTE)
        lte_pattern_base = [1, 1, 0, 0, 1, 1, 1, 1, 1, 1]
        lte_pattern_base_array = array.array('B', lte_pattern_base)

        if LTE_PATTERN_STATE == 3:

            if AIR_TIME == 4 and AIR_TIME_LTE == 5 and reading_buffer[2] == 6:
                AIR_TIME_LTE = 0
                AIR_TIME = 0

            if reading_buffer[2] > 0 and reading_buffer[2] < 6:
                AIR_TIME = reading_buffer[2] - 1

            air_time_mask = [1 for i in range(AIR_TIME + 1)]
            jj = 0
            for ii in range(0, len(air_time_mask)):
                if ii == 1:
                    tdma_mask_output[(index_pattern_finded[0] - 1 - jj) % 10] = 0
                    jj += 1
                tdma_mask_output[(index_pattern_finded[0] - 1 - jj) % 10] = air_time_mask[ii]
                jj += 1

            if AIR_TIME_LTE < 5 :
                # for jj in range(10, 3, -1):
                jj = 4
                for ii in range(4, 5+AIR_TIME, 1):
                    if ii == 5:
                        jj += 1
                    lte_pattern_base_array[jj] = 0
                    jj+=1

                if lte_pattern_base_array[0] == 1:
                    tx_pattern = '1'
                else:
                    tx_pattern = '0'
                for kk in range(1, 10):
                    if lte_pattern_base_array[kk] == 1:
                        tx_pattern = tx_pattern + ',' + '1'
                    else:
                        tx_pattern = tx_pattern + ',' + '0'

                print("tx_pattern: ", tx_pattern)
                enb_lte_pattern_sock.sendto(tx_pattern.encode(), (UDP_IP, UDP_PORT))
                if AIR_TIME_LTE < 6 and reading_buffer[2] == 6:
                    AIR_TIME_LTE += 1
                else:
                    AIR_TIME_LTE = 6

            if AIR_TIME < 4 and reading_buffer[2] == 6:
                AIR_TIME += 1

        return([index_pattern_finded, tdma_mask_output, LTE_PATTERN_STATE, AIR_TIME, AIR_TIME_LTE])


    # lte_pattern = [1, 1, 1, 1]
    lte_pattern_3 = [1, 1, 1]
    lte_pattern_3_array = array.array('B', lte_pattern_3)

    # tdma3_pattern_5 = [0, 0, 1, 1, 1]
    tdma3_pattern_5 = [1, 1, 1, 0, 0]
    tdma3_pattern_5_array = array.array('B', tdma3_pattern_5)

    tdma3_pattern_3 = [1, 1, 0]
    tdma3_pattern_3_array = array.array('B', tdma3_pattern_3)
    tdma3_pattern_4 = [1, 1, 0, 0]
    tdma3_pattern_4_array = array.array('B', tdma3_pattern_4)

    lte_pattern_5 = [1, 1, 1, 1, 1]
    tdma_mask_array_full_on = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    tdma_mask_array_full_off = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


    # find pattern
    def find_lte_pos(psuc_mask, LTE_PATTERN_STATE, CORRECTION_DIRECTION, AIR_TIME, AIR_TIME_LTE, enb_lte_pattern_sock, reading_buffer):
        print("STATE = %s - %s " % (str(LTE_PATTERN_STATE) , str(CORRECTION_DIRECTION) ) )

        if len(psuc_mask) != 10:
            return([-1, psuc_mask, LTE_PATTERN_STATE, CORRECTION_DIRECTION, 0, 0])

        tdma_mask = psuc_mask[:]
        tdma_mask.append(tdma_mask[0])
        tdma_mask.append(tdma_mask[1])
        # tdma_mask.append(tdma_mask[2])
        # tdma_mask.append(tdma_mask[3])
        tdma_mask_array = array.array('B', tdma_mask)
        # print(tdma_mask_array)
        num_pattern_3_finded = 0
        index_pattern_3_finded = []
        # find pattern preable 4
        for ii in range(0, 10):
            if tdma3_pattern_3_array == tdma_mask_array[ii:ii + len(tdma3_pattern_3_array)]:
                index_pattern_3_finded.append(ii)
                num_pattern_3_finded += 1
        print(num_pattern_3_finded)
        print(index_pattern_3_finded)

        if num_pattern_3_finded == 0:
            LTE_PATTERN_STATE = 0
            AIR_TIME = 0
            AIR_TIME_LTE = 0
            print("WARNING NO PATTERN3 FINDED")
            return ([0, tdma_mask_array_full_on, LTE_PATTERN_STATE, CORRECTION_DIRECTION, 0, 0])

        elif num_pattern_3_finded == 1 :
            if LTE_PATTERN_STATE < 3:
                LTE_PATTERN_STATE += 1
            else:
                if AIR_TIME > 2:
                    mask_sum = 0
                    for x in list(psuc_mask):
                        mask_sum += x
                    if mask_sum < 4:
                        LTE_PATTERN_STATE = 0
                        AIR_TIME = 0
                        AIR_TIME_LTE = 0
                        tx_pattern = '1,1,0,0,0,1,1,1,1,1'
                        print("tx_pattern: ", tx_pattern)
                        enb_lte_pattern_sock.sendto(tx_pattern.encode(), (UDP_IP, UDP_PORT))
                        print("WARNING NO GOOD PSUCC")
                        return ([0, tdma_mask_array_full_on, LTE_PATTERN_STATE, CORRECTION_DIRECTION, AIR_TIME, AIR_TIME_LTE])

            tdma_mask_output = tdma_mask_array_full_off[:]
            # print(tdma_mask_output)
            # print(index_pattern_3_finded[0])
            # print(lte_pattern_3)

            for ii in range(0, len(lte_pattern_3)):
                tdma_mask_output[(index_pattern_3_finded[0] + ii)%10] = lte_pattern_3[ii]

            [index_pattern_3_finded, tdma_mask_output, LTE_PATTERN_STATE, AIR_TIME, AIR_TIME_LTE] = find_airtime(tdma_mask_output, tdma_mask_array, index_pattern_3_finded, AIR_TIME, AIR_TIME_LTE, LTE_PATTERN_STATE, enb_lte_pattern_sock, reading_buffer)
            return ([index_pattern_3_finded, tdma_mask_output, LTE_PATTERN_STATE, CORRECTION_DIRECTION, AIR_TIME, AIR_TIME_LTE])

        elif (num_pattern_3_finded == 2 and LTE_PATTERN_STATE > 2):
            print("find 2 pattern of 3 elements")
            tdma_mask = psuc_mask[:]
            tdma_mask.append(tdma_mask[0])
            tdma_mask.append(tdma_mask[1])
            tdma_mask.append(tdma_mask[2])
            tdma_mask_array = array.array('B', tdma_mask)
            num_pattern_4_finded = 0
            index_pattern_4_finded = []
            # find pattern preable 4
            for ii in range(0, 10):
                if tdma3_pattern_4_array == tdma_mask_array[ii:ii + len(tdma3_pattern_4_array)]:
                    index_pattern_4_finded.append(ii)
                    num_pattern_4_finded += 1
            print(num_pattern_4_finded)
            print(index_pattern_4_finded)

            if num_pattern_4_finded == 0:
                LTE_PATTERN_STATE = 0
                AIR_TIME = 0
                AIR_TIME_LTE = 0
                print("WARNING NO PATTERN 4 FINDED")
                return ([0, tdma_mask_array_full_on, LTE_PATTERN_STATE, CORRECTION_DIRECTION, 0, 0])

            elif num_pattern_4_finded == 1:
                tdma_mask_output = tdma_mask_array_full_off[:]

                for ii in range(0, len(lte_pattern_3)):
                    tdma_mask_output[(index_pattern_4_finded[0] + ii) % 10] = lte_pattern_3[ii]

                [index_pattern_4_finded, tdma_mask_output, LTE_PATTERN_STATE, AIR_TIME, AIR_TIME_LTE] = find_airtime(tdma_mask_output, tdma_mask_array, index_pattern_4_finded, AIR_TIME, AIR_TIME_LTE, LTE_PATTERN_STATE, enb_lte_pattern_sock, reading_buffer)
                return ([index_pattern_4_finded, tdma_mask_output, LTE_PATTERN_STATE, CORRECTION_DIRECTION, AIR_TIME, AIR_TIME_LTE])

            else:
                LTE_PATTERN_STATE = 3
                AIR_TIME = 0
                AIR_TIME_LTE = 0
                print("WARNING MANY PATTERN 4 FINDED")
                return ([0, tdma_mask_array_full_on, LTE_PATTERN_STATE, CORRECTION_DIRECTION, 0, 0])

        elif num_pattern_3_finded == 2 :
            print("find 2 pattern of 3 elements")
            # if LTE_PATTERN_STATE == 0:
            if True:
                tdma_mask = psuc_mask[:]
                tdma_mask.append(tdma_mask[0])
                tdma_mask.append(tdma_mask[1])
                tdma_mask.append(tdma_mask[2])
                tdma_mask_array = array.array('B', tdma_mask)
                num_pattern_4_finded = 0
                index_pattern_4_finded = []
                # find pattern preable 4
                for ii in range(0, 10):
                    if tdma3_pattern_4_array == tdma_mask_array[ii:ii + len(tdma3_pattern_4_array)]:
                        index_pattern_4_finded.append(ii)
                        num_pattern_4_finded += 1
                print(num_pattern_4_finded)
                print(index_pattern_4_finded)

                if num_pattern_4_finded == 0:
                    LTE_PATTERN_STATE = 0
                    AIR_TIME = 0
                    AIR_TIME_LTE = 0
                    print("WARNING NO PATTERN 4 FINDED")
                    return ([0, tdma_mask_array_full_on, LTE_PATTERN_STATE, CORRECTION_DIRECTION, 0, 0])

                elif num_pattern_4_finded == 1:
                    # return position of the pattern 4
                    LTE_PATTERN_STATE = 1
                    AIR_TIME = 0
                    AIR_TIME_LTE = 0
                    tdma_mask_output = tdma_mask_array_full_off[:]
                    # print(tdma_mask_output)
                    # tdma_mask_output[index_pattern_5_finded:index_pattern_5_finded+5] = lte_pattern_5
                    for ii in range(0, len(lte_pattern_3)):
                        tdma_mask_output[(index_pattern_4_finded[0] + ii) % 10] = lte_pattern_3[ii]
                    return ([index_pattern_4_finded, tdma_mask_output, LTE_PATTERN_STATE, CORRECTION_DIRECTION, 0, 0])
                else:
                    LTE_PATTERN_STATE = 3
                    AIR_TIME = 0
                    AIR_TIME_LTE = 0
                    print("WARNING MANY PATTERN 4 FINDED")
                    return ([0, tdma_mask_array_full_on, LTE_PATTERN_STATE, CORRECTION_DIRECTION, 0, 0])

            else:
                print("WARNING 2 PATTERN3 FINDED")
                LTE_PATTERN_STATE = 0
                AIR_TIME = 0
                AIR_TIME_LTE = 0
                return ([0, tdma_mask_array_full_on, LTE_PATTERN_STATE, CORRECTION_DIRECTION, 0, 0])

        else:
            LTE_PATTERN_STATE = 3
            AIR_TIME = 0
            AIR_TIME_LTE = 0
            tx_pattern = '1,1,0,0,0,1,1,1,1,1'
            print("tx_pattern: ", tx_pattern)
            enb_lte_pattern_sock.sendto(tx_pattern.encode(), (UDP_IP, UDP_PORT))
            print("WARNING MANY PATTERN3 FINDED")
            return ([0, tdma_mask_array_full_on, LTE_PATTERN_STATE, CORRECTION_DIRECTION, 0, 0])

        print("WARNING IN PATTERN3 FINDED")
        LTE_PATTERN_STATE = 0
        AIR_TIME = 0
        AIR_TIME_LTE = 0
        return ([0, tdma_mask_array_full_on, LTE_PATTERN_STATE, CORRECTION_DIRECTION, 0, 0])

    def tune_wifi_pattern(reading_buffer):
        reading_buffer_thread = threading.currentThread()
        """
        This function collects the reading buffer information
        """
        # reading_thread = threading.currentThread()
        # print('start socket reading_program')
        # reading_port = "8901"
        # reading_server_ip_address = "127.0.0.1"
        # context = zmq.Context()
        # reading_socket = context.socket(zmq.SUB)
        # print("tcp://%s:%s" % (reading_server_ip_address, reading_port))
        # reading_socket.connect("tcp://%s:%s" % (reading_server_ip_address, reading_port))
        # reading_socket.setsockopt_string(zmq.SUBSCRIBE, '')
        # print('socket reading_program started')

        """
        This function collects the reading buffer information from shared memory
        """
        b43_phy = None
        b43 = B43(b43_phy)
        print("Starting psuc reading...")
        reading_time = time.time()
        local_starttime = reading_time
        reading_interval = 7
        tx_count_ = 0
        rx_ack_count_ = 0
        # count_round = 0


        #UDP_IP = "10.8.9.13"
        UDP_IP = "172.16.16.11"
        UDP_PORT = 8888
        print("UDP target IP: ", UDP_IP)
        print("UDP target port: ", UDP_PORT)
        enb_lte_pattern_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        tx_pattern =  '1,0,0,0,0,1,1,1,1,1'
        print("tx_pattern: ", tx_pattern)
        enb_lte_pattern_sock.sendto(tx_pattern.encode(), (UDP_IP, UDP_PORT))

        AIR_TIME = 0
        AIR_TIME_LTE = 0
        mask_int = [1,1,1,1,1,1,1,1,1,1]

        # 0 : IDLE; 1 SYNC; 2 PATTERN4_ESTIMATE; 3 PATTERN3_OK
        LTE_PATTERN_STATE = 0

        # 1 RIGHT or -1 LEFT
        CORRECTION_DIRECTION = 0
        lte_start_index = None

        while getattr(reading_buffer_thread, "do_run", True):
            tx_count = []
            rx_ack_count = []
            for i in [216, 220, 224, 228, 232]:
                val = b43.shmRead32(b43.B43_SHM_SHARED, i)
                # outString = outString + str((val & 0x00FF) + ((val & 0xFF00))) + "," + str(((val >> 16) & 0x00FF) + ((val >> 16) & 0xFF00)) + ","
                tx_count.append((val & 0x00FF) + ((val & 0xFF00)))
                tx_count.append(((val >> 16) & 0x00FF) + ((val >> 16) & 0xFF00))

                val = b43.shmRead32(b43.B43_SHM_SHARED, i + 20)
                rx_ack_count.append((val & 0x00FF) + ((val & 0xFF00)))
                rx_ack_count.append(((val >> 16) & 0x00FF) + ((val >> 16) & 0xFF00))

            tx_count = [float(i) for i in tx_count]
            rx_ack_count = [float(i) for i in rx_ack_count]

            tx_count = np.array(tx_count)
            rx_ack_count = np.array(rx_ack_count)

            dtx = np.mod(tx_count - tx_count_, 0xFFFF)
            dack = np.mod(rx_ack_count - rx_ack_count_, 0xFFFF)
            tx_count_ = tx_count
            rx_ack_count_ = rx_ack_count
            psucc = np.divide(dack, dtx)

            for i in range(0, len(psucc)):
                if np.isinf(psucc[i]):
                    psucc[i] = 0
                    continue
                if np.isnan(psucc[i]):
                    psucc[i] = 0
                    continue
            psucc_tot = np.divide(np.sum(dack), np.sum(dtx))

            # print("rx_ack = {}".format(dack))
            # print("tx     = {}".format(dtx))
            # np.set_printoptions(precision=1)
            # print("psucc  = {}".format(psucc))
            # print("psucc_tot={}".format(psucc_tot))
            # print("count_round={}".format(count_round))

            # cycle = 0
            # while getattr(reading_thread, "do_run", True):
            #     parsed_json = reading_socket.recv_json()
            #     print( str(cycle) +  '  parsed_json : %s' % ( str(parsed_json)))
            #     cycle += 1
            #
            #     psucc = parsed_json['measure']

            mask = ""
            for x in psucc:
                if x > 0.5:
                    maskval = 1
                elif np.isinf(x):
                    maskval = 0
                else:
                    maskval = 0

                mask = "{}{}".format(maskval, mask)
                mask_psucc_int = [int(x) for x in list(mask)]

            # if mask == "0000000000":
            #     mask = "1111111111"

            # mask_sum = 0
            # for x in list(mask_psucc_int):
            #     mask_sum += x
            # EST_SLOT = 4
            # L = 10
            # if mask_sum < EST_SLOT:
            #     mask_int = update_pattern(mask_psucc_int, L, mask_sum + 1)
            # else:
            #     mask_int=update_pattern(mask_psucc_int, L, mask_sum + 1)

            print("----------")
            print("fixed airtime : ", reading_buffer[2])
            if reading_buffer[3]:
                AIR_TIME = 0
                AIR_TIME_LTE = 0
                tx_pattern = '1,1,0,0,0,1,1,1,1,1'
                print("tx_pattern: ", tx_pattern)
                enb_lte_pattern_sock.sendto(tx_pattern.encode(), (UDP_IP, UDP_PORT))
                reading_buffer[3] = False
            print(mask_psucc_int)
            print(mask_int)

            reading_buffer[0] = round(np.mean(mask_psucc_int) / np.mean(mask_int), 2)
            if  math.isnan(reading_buffer[0]):
                reading_buffer[0] = 0
            if reading_buffer[0] > 1:
                reading_buffer[0] = 0.8

            print("call find_lte_pos")
            [index_start_pattern, mask_int, LTE_PATTERN_STATE, CORRECTION_DIRECTION, AIR_TIME, AIR_TIME_LTE] = find_lte_pos(mask_psucc_int, LTE_PATTERN_STATE, CORRECTION_DIRECTION, AIR_TIME, AIR_TIME_LTE, enb_lte_pattern_sock, reading_buffer)

            print(mask_int)
            if reading_buffer[4]:
                print("rotate mask")
                mask_int = [mask_int[-1]] + mask_int[0:-1]
                print(mask_int)
                reading_buffer[4]=False

            print("**********")

            if index_start_pattern == -1:
                print("Error in find_lte_pos")

            else:
                print(index_start_pattern)

                mask = ""
                for x in mask_int:
                    mask = "{}{}".format(mask, x)

                if not dryRun:
                    UPIargs = {'interface': 'wlan0', UPI_R.TDMA_ALLOCATED_MASK_SLOT: int(mask,2)}
                    # rvalue = controller.nodes(node).radio.set_parameters(UPIargs)
                    rvalue = controller.radio.set_parameters(UPIargs)
                    if rvalue[0] == SUCCESS:
                        log.warning('Radio program configuration succesfull')
                    else:
                        log.warning('Error in radio program configuration')
                        do_run = False

            reading_buffer[1] = mask
            time.sleep(reading_interval - ((time.time() - local_starttime) % reading_interval))

        enb_lte_pattern_sock.close()
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
                print('my address %s - parsed_json : %s' % (str(wlan_ip_address), str(parsed_json)))
                rcv_ip_address = parsed_json['ip_address']
                if rcv_ip_address == wlan_ip_address:
                    # print('parsed_json : %s' % str(parsed_json))
                    iperf_througputh[0] = float(parsed_json['throughput'])
                    iperf_througputh[1] = float(float(parsed_json['per']) / 100)
            else:
                # raise IOError("Timeout processing auth request")
                iperf_througputh[0] = float(0)
                iperf_througputh[1] = float(0)


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
            #try:
            if True:
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

                reading_buffer = []
                reading_buffer.append(0.0)
                reading_buffer.append("0000000000")
                reading_buffer.append(1)
                reading_buffer.append(False)
                reading_buffer.append(False)
                reading_buffer_thread = threading.Thread(target=tune_wifi_pattern, args=(reading_buffer,))
                reading_buffer_thread.do_run = True
                reading_buffer_thread.start()

            # except (Exception) as err:
            #     if debug:
            #         print ( "exception", err)
            #         print ("Error: unable to start thread")
            #     pass
            break

    #CONTROLLER MAIN LOOP
    while not controller.is_stopped():
        msg = controller.recv(timeout=2)
        if msg:
            log.info("Receive message %s" % str(msg))

            if 'i_time' in msg:
                i_time[0] = msg['i_time']

            if "airtime_fixed" in msg:
                reading_buffer[2] = msg["airtime_fixed"]
                reading_buffer[3] = True

            if "rs_tdma" in msg:
                reading_buffer[4] = True

        controller.send_upstream({"measure": [time.time(), iperf_througputh[0], reading_buffer[0], reading_buffer[1]], "mac_address": (my_mac)})

    iperf_thread.do_run = False
    iperf_thread.join()
    reading_buffer_thread.do_run = False
    reading_buffer_thread.join()
    time.sleep(2)
