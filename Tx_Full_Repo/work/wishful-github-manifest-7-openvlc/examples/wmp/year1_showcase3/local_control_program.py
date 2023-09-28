"""
Local control program to be executed on remote nodes.
"""

__author__ = "Domenico Garlisi"
__copyright__ = "Copyright (c) 2016, CNIT"
__version__ = "0.2.0"

# Definition of Local Control Program
def my_local_control_program(controller):
    # do all needed imports here!!!
    import time
    import datetime
    import sys
    sys.path.append('../../../')
    sys.path.append("../../../agent_modules/wifi_ath")
    sys.path.append("../../../agent_modules/wifi_wmp")
    sys.path.append("../../../agent_modules/wifi")
    sys.path.append('../../../upis')
    sys.path.append('../../../framework')
    sys.path.append('../../../agent')
    from agent_modules.wifi_wmp.wmp_structure import UPI_R


    @controller.set_default_callback()
    def default_callback(cmd, data):
        print(("DEFAULT CALLBACK : Cmd: {}, Returns: {}".format(cmd, data)))

    # control loop
    print("Local ctrl program started: {}".format(controller.name))
    while not controller.is_stopped():
        msg = controller.recv(timeout=1)
        if msg:
            ch = msg["new_channel"]
            print("Schedule get monitor to {} in 5s:".format(ch))
            UPI_myargs = {'interface' : 'wlan0', 'measurements' : [UPI_R.REGISTER_1, UPI_R.REGISTER_2, UPI_R.NUM_TX_DATA_FRAME, UPI_R.NUM_RX_ACK, UPI_R.NUM_RX_ACK_RAMATCH, UPI_R.BUSY_TYME , UPI_R.TSF, UPI_R.NUM_RX_MATCH] }
            result = controller.delay(5).radio.get_measurements(UPI_myargs)
            controller.send_upstream({"myResult": result})

    print("Local ctrl program stopped: {}".format(controller.name))


# Definition of Local Control Program for wishful showcase3
def local_control_program(controller):
    # do all needed imports here!!!
    import time
    import datetime
    import sys
    import threading
    import zmq

    sys.path.append('../../../')
    sys.path.append("../../../agent_modules/wifi_ath")
    sys.path.append("../../../agent_modules/wifi_wmp")
    sys.path.append("../../../agent_modules/wifi")
    sys.path.append('../../../upis')
    sys.path.append('../../../framework')
    sys.path.append('../../../agent')
    sys.path.append("../../../agent_modules/net_linux")
    from agent_modules.wifi_wmp.wmp_structure import UPI_R

    #socket iperf pointer
    iperf_socket = None
    iperf_socket = None

    def rcv_from_iperf_socket(iperf_througputh, controller, interface):
        iperf_thread = threading.currentThread()
        print('start socket iperf')
        iperf_port = "8301"
        iperf_server_ip_address = "10.8.8.102"
        context = zmq.Context()
        iperf_socket = context.socket(zmq.SUB)
        print("tcp://%s:%s" % (iperf_server_ip_address, iperf_port))
        iperf_socket.connect("tcp://%s:%s" % (iperf_server_ip_address, iperf_port))
        iperf_socket.setsockopt_string(zmq.SUBSCRIBE, '')

        wlan_ip_address = controller.net.get_iface_ip_addr(interface)
        wlan_ip_address = wlan_ip_address[0]
        print('socket iperf started')
        while getattr(iperf_thread, "do_run", True):
            parsed_json = iperf_socket.recv_json()
            #print('my address %s - parsed_json : %s' % (str(wlan_ip_address), str(parsed_json)))
            rcv_ip_address = parsed_json['ip_address']
            if rcv_ip_address == wlan_ip_address:
            #    print('parsed_json : %s' % str(parsed_json))
            print('my address %s - parsed_json : %s' % (str(wlan_ip_address), str(parsed_json)))
            rcv_ip_address = parsed_json['ip_address']
            if rcv_ip_address == wlan_ip_address:
                print('parsed_json : %s' % str(parsed_json))
                iperf_througputh[0] = float(parsed_json['throughput'])

    """
    Custom function used to implement local WiSHFUL controller
    """
    def customLocalCtrlFunction(controller, interface, tuning_enabler, iperf_througputh):

        import time
        import logging
        import math

        # references to Wishful framework
        #global upiHCImpl # interface used for communication with global controller and control runtime

        log = logging.getLogger()
        log.warning('*********** WISHFUL SC3 *************')
        log.warning('*********** starting local WiSHFUL controller **********************')

        # set start node CW
        # cw = 30
        # UPI_myargs = {'interface' : interface, UPI_RN.CSMA_CW : cw, UPI_RN.CSMA_CW_MIN : cw, UPI_RN.CSMA_CW_MAX : cw }
        # controller.radio.set_parameter(UPI_myargs)

        last_freezing_number = 0
        b = 0.3
        a = 0.1
        last_count_freezing = 0
        CWMIN = 15
        CWMAX = 1023
        T = 1
        ipt = 0
        cw_f = 64 #CWMIN
        cw = cw_f;
        cycle_update = 0
        data_tx=0
        data_tx_=0
        ack_rx = 0
        ack_rx_ = 0
        ack_rx_ramatch = 0
        ack_rx_ramatch_ = 0
        busytime = 0
        busytime_ = 0
        tsf_reg = 0
        tsf_reg_ = 0
        num_rx = 0
        num_rx_ = 0
        num_rx_success = 0
        num_rx_success_ = 0
        num_rx_match = 0
        num_rx_match_ = 0

        ip_address = controller.net.get_iface_ip_addr(interface)
        #UPI_myargs = {'interface' : interface, UPI_R.CSMA_CW : CWMIN, UPI_R.CSMA_CW_MIN : CWMIN, UPI_R.CSMA_CW_MAX : CWMAX }
        #controller.radio.set_parameter(UPI_myargs)

        #station number initializing
        n_tx_sta = 5

        #local controller loop
        while not controller.is_stopped():

            #find linux system time
            tsf=time.time()*1e6;

            #get node statistics
            UPI_myargs = {'interface' : interface, 'measurements' : [UPI_R.REGISTER_1, UPI_R.REGISTER_2, UPI_R.NUM_TX_DATA_FRAME, UPI_R.NUM_RX_ACK, UPI_R.NUM_RX_ACK_RAMATCH, UPI_R.BUSY_TYME , UPI_R.TSF, UPI_R.NUM_RX_MATCH] }
            node_measures = controller.radio.get_measurements(UPI_myargs)

            #IPT
            pos = 0
            ipt=node_measures[pos]
            K = 10
            GOOGLE = 2**K
            ipt = float(ipt) / GOOGLE

            #FREEZING
            pos += 1
            count_freezing=node_measures[pos]
            delta_freezing = count_freezing - last_count_freezing
            if delta_freezing < 0 :
                delta_freezing = 2 ** (16) -1 - last_count_freezing + count_freezing
            last_count_freezing = count_freezing
            delta_freezing=float(delta_freezing)

            #DATA_TX
            pos+=1
            data_tx = node_measures[pos]
            delta_data_tx=data_tx-data_tx_
            if delta_data_tx < 0 :
                 delta_data_tx= 2 ** (16) -1  - data_tx_ + data_tx
            data_tx_ = data_tx

            #ACK TOTAL
            pos += 1
            ack_rx = node_measures[pos]
            delta_ack_rx = ack_rx - ack_rx_
            if delta_ack_rx < 0 :
                 delta_ack_rx = 2 ** (16) -1  - ack_rx_ + ack_rx
            ack_rx_ = ack_rx
            delta_ack_rx=float(delta_ack_rx)

            #ACK WITH RAMATCH (TX_OK_MY_PACKET)
            pos += 1
            ack_rx_ramatch = node_measures[pos]
            delta_ack_rx_ramatch = ack_rx_ramatch - ack_rx_ramatch_
            if delta_ack_rx_ramatch < 0 :
                 delta_ack_rx_ramatch = 2 ** (16) -1  - ack_rx_ramatch_ + ack_rx_ramatch
            ack_rx_ramatch_ = ack_rx_ramatch
            delta_ack_rx_ramatch=float(delta_ack_rx_ramatch)

            #BUSYTIME
            pos += 1
            busytime = node_measures[pos]
            delta_busytime = busytime - busytime_
            if delta_busytime < 0 :
                 delta_busytime = 2 ** (16) -1  - busytime_ + busytime
            busytime_ = busytime
            delta_busytime=float(delta_busytime)

            #TSF
            pos += 1
            tsf_reg = node_measures[pos]
            delta_tsf_reg = tsf_reg - tsf_reg_
            if delta_tsf_reg < 0 :
                 delta_tsf_reg = 2 ** (64) - 1  - tsf_reg_ + tsf_reg
            tsf_reg_ = tsf_reg
            delta_tsf_reg=float(delta_tsf_reg)

            #NUM_RX_MATCH
            pos += 1
            num_rx_match = node_measures[pos]
            delta_num_rx_match = num_rx_match - num_rx_match_
            if delta_num_rx_match < 0 :
                 delta_num_rx_match = 2 ** (16) - 1  - num_rx_match_ + num_rx_match
            num_rx_match_ = num_rx_match
            delta_num_rx_match=float(delta_num_rx_match)

            #PHY
            bw=20
            Tpre=16*20/bw
            Tsig=4*20/bw
            Tsym=4*20/bw
            rate=24 #2 #Mbps
            basic_rate=6 #2 #Mbps

            #MAC
            tslot=9
            SIFS=10
            AIFS=2
            DIFS=AIFS*tslot+SIFS

            #PKT SIZE
            l_ack=14 #byte
<<<<<<< HEAD
            data_size=1470 #200
=======
            data_size=200
>>>>>>> origin/master

            t_data= Tpre + Tsig + math.ceil(Tsym/2+(22+8*(data_size))/rate)
            t_ack=Tpre + Tsig+math.ceil(l_ack*8/basic_rate)
            EIFS= t_ack + SIFS + DIFS

            #select algorithm to tune node CW
            alg="MEDCA"

            if alg == "CW_OPT":
                Tc = t_data + EIFS #Collision time
                cw_f = n_tx_sta * math.sqrt(2*Tc / tslot)
                cw = round(cw_f)
                cw = int(cw)
                cw = max(cw,CWMIN)
                cw = min(cw,CWMAX)

            #MEDCA algorithm
            if alg == "MEDCA" :
                """""""""""""""""""""""""""""""""""""""""""""
                execute MEDCA algorithm and find new CW value
                # ipt = ipt + a * (delta_freezing - ipt);
                # targetcw = -0.0131 * ipt ** 2 + 3.2180 * ipt + 13.9265;  # determine the target CW for this IPT
                """""""""""""""""""""""""""""""""""""""""""""
                targetcw = -0.0106 * ipt ** 2 + 2.9933 * ipt + 18.5519  # determine the target CW for this IPT
                cw_f = cw_f + b * (targetcw - cw_f)
                cw = round(cw_f)
                cw = int(cw)
                cw = max(cw,CWMIN)
                cw = min(cw,CWMAX)

            #set fixed contention windows
            if alg == "FIXED":
                cw = 46

            #update CW
            if tuning_enabler == 1 and alg != "DCF" :
                log.warning(' >>>>>>>> CW setting : ENABLED')
                UPI_myargs = {'interface' : interface, UPI_R.CSMA_CW : cw, UPI_R.CSMA_CW_MIN : cw, UPI_R.CSMA_CW_MAX : cw }
                controller.radio.set_parameters(UPI_myargs)
            else:
                log.warning(' >>>>>>>> CW setting : DISABLED')

            #send value to MASTER
            cycle_update += 1
            if not(cycle_update % 1):
                log.warning("num_tx_nodes=%d" % n_tx_sta )
                #communicate with global controller by passing control message
<<<<<<< HEAD
                log.warning('Sending result message to control program ')
=======
                log.warning('Sending result message to control program ');
>>>>>>> origin/master
                controller.send_upstream({ "measure" : [[delta_freezing, tsf_reg, delta_ack_rx_ramatch, cw, ipt, delta_data_tx, delta_ack_rx,  delta_busytime, delta_tsf_reg, delta_num_rx_match, iperf_througputh[0] ]], "ip_address" : (ip_address) })

            #receive message from controller
            msg = controller.recv(timeout=1)
            if msg:
                    n_tx_sta = msg["traffic_number"]
                    log.warning("num_tx_nodes=%d" % n_tx_sta )
            #time.sleep(T)

        log.warning('Local WiSHFUL Controller END');
        return 'Local WiSHFUL Controller END'


    '''
    Remote execution main part
    '''
    while not controller.is_stopped():
        msg = controller.recv(timeout=1)
        if msg:
            interface = msg["interface"]
            tuning_enabler = msg["tuning_enabler"]
            #controller.send_upstream({"myResult": result})

        iperf_througputh = []
        iperf_througputh.append(0.0)
        iperf_thread = threading.Thread(target=rcv_from_iperf_socket, args=(iperf_througputh, controller, interface))
        iperf_thread.start()

        customLocalCtrlFunction(controller, interface, tuning_enabler, iperf_througputh)