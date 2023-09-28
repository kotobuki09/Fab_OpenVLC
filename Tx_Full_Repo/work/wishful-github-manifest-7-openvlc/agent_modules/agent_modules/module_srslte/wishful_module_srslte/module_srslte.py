import logging
import socket
import subprocess
import threading
import select
import os 
import glob
import time
from threading import Thread
import sys
import signal
from array import array
import json
import queue
import sys
from enum import Enum
import zmq

import wishful_upis as upis
import wishful_framework as wishful_module

__author__ = "Justin Tallon"
__copyright__ = "Copyright (c) 2017, Software Radio Systems Ltd."
__version__ = "0.0.1"
__email__ = "Justin Tallon"


which_metric_dict = {'CFO' : 0 ,'SNR' : 1, 'RSRP' : 2, 'RSRQ' : 3, 'NOISE' : 4, 'CSI' : 5, 'N_FRAMES': 6, 'PDSCH_MISS':7, 'PDCCH_MISS':8, 'MOD':9, 'TBS':10}
which_metric_dict_rev = {0 :'CFO'  ,1 :'SNR' , 2 :'RSRP' , 3 : 'RSRQ', 4 :'NOISE', 5 : 'CSI', 6 : 'N_FRAMES',7:'PDSCH_MISS', 8:'PDCCH_MISS', 9:'MOD',10:'TBS'}

which_parameter_dict = {'MCS':0, 'PRBS':1, 'FREQ':2, 'GAIN':3}
which_parameter_dict_rev = {0:'MCS', 1: 'PRBS',2:'FREQ',3:'GAIN'}

sss_algorithm_dict = {'SSS_DIFF':0, 'SSS_FULL': 1, 'SSS_PARTIAL_3' :2}

class RadioProgramState(Enum):
    IDLE = 1
    RUNNING = 2

class srslte_iface:
    def __init__(self,
                 ip='127.0.0.1',
                 ue_port_server = 4321,
                 ue_port_client = 2222,
                 eNb_port_server = 4321,
                 eNb_port_client = 2222,
                 # directory = "/home/tallonj/srsLTE"
                 # directory = "/home/domenico/work/srsLTE_Wishful/"
                 # directory = "/home/domenico/work/srsLTE_origin/srsLTE/"
				 #directory = "/groups/portable-ilabt-imec-be/wish/cnit/srsLTE_origin/srsLTE/"
                 directory = "/groups/portable-ilabt-imec-be/wish/cnit/srsLTE_origin-v2/srsLTE/"
                 ):
        self.ip = ip
        self.ue_port_server = ue_port_server
        self.ue_port_client = ue_port_client
        self.eNb_port_server = eNb_port_server
        self.eNb_port_client = eNb_port_client
        self.threads = []
        self.killpill = threading.Event()
        self.metric_buffer = queue.Queue()
        self.config_buffer = queue.Queue()
        self.directory = directory
        self.is_ue = False

        self.srsradio_state = RadioProgramState.IDLE

        # self.ue_filename = './build/lib/examples/pdsch_ue_wishful'
        self.ue_filename = "./build/srslte/examples/pdsch_ue"
        self.ue_is_running = False
        self.ue_pid = -1

        # self.eNb_filename = './build/lib/examples/pdsch_enodeb_wishful'
        self.eNb_filename = "./build/srslte/examples/pdsch_enodeb"
        self.eNb_is_running = False
        self.eNb_pid = -1

        #input parameters for the UE
        self.ue_frequency = 806000000
        self.ue_gain = 70
        self.ue_equalizer = 'mmse'
        self.ue_nof_antennas ="172.16.16.6"
        self.ue_max_turbo_decoder_its = 4
        self.ue_noise_est_alg = 0
        self.ue_sss_algorithm = sss_algorithm_dict['SSS_DIFF']
        self.ue_snr_ema_coeff = 0.1
        self.ue_cfo_tol = 50.0
        #input parameters for the eNb
        self.eNb_frequency = 2491000000
        self.eNb_rf_amp = 0.8
        self.eNb_gain  = 70
        self.eNb_no_of_frames = 100000
        self.eNb_no_of_prbs = 25
        self.eNb_which_prbs = 0xFFFF
        self.eNb_MCS = 1
        self.eNb_send_pdsch_data = 1
        self.eNb_net_port = 2000

        self.sta_id = {}
        self.sta_ip_address = {}
        self.sta_id_max = 0

        self.iperf_process = None
        self.eNb_loop = False
        self.eU_loop = False

        self.iperf_port = "8301"
        context = zmq.Context()
        self.socket_zmq = context.socket(zmq.PUB)
        self.socket_zmq.bind("tcp://*:%s" % self.iperf_port)
        self.sta_id = {}
        self.sta_ip_address = {}
        self.sta_id_max = 0

        print("srs interface object has been initialized\n")

    def throw_signal_function(self,frame, event, arg):
        raise SigFinish()

    def interrupt_thread(self,thread):
        for thread_id, frame in sys._current_frames().items():
            if thread_id == thread.ident:  # Note: Python 2.6 onwards
                self.set_trace_for_frame_and_parents(frame, self.throw_signal_function)

    def set_trace_for_frame_and_parents(self, frame, trace_func):
        # Note: this only really works if there's a tracing function set in this
        # thread (i.e.: sys.settrace or threading.settrace must have set the
        # function before)
        while frame:
            if frame.f_trace is None:
                frame.f_trace = trace_func
            frame = frame.f_back
        del frame

    def do_nothing_trace_function(frame, event, arg):
        return None

    def set_ue_frequency(self,frequency):
        self.ue_frequency = frequency
        if self.ue_is_running:
            return self.send_command(True, self.ue_frequency, -4, 0, 1, which_parameter_dict['FREQ'])
        else:
            return self.ue_frequency

    def set_ue_gain(self, gain):
        self.ue_gain = gain
        if self.ue_is_running:
            return self.send_command(True, self.ue_gain, -4, 0, 1, which_parameter_dict['GAIN'])
        else:
            return self.ue_gain

    def set_ue_nof_antennas(self,nof_antennas):
        self.ue_nof_antennas = nof_antennas
        return self.ue_nof_antennas

    def set_ue_equalizer(self,equalizer_mode):
        self.ue_equalizer = equalizer_mode
        return self.ue_equalizer

    def set_ue_max_turbo_decoder_its(self,max_turbo_decoder_its):
        self.ue_max_turbo_decoder_its = max_turbo_decoder_its
        return self.ue_max_turbo_decoder_its

    def set_ue_noise_est_alg(self,noise_est_algorithm):
        self.ue_noise_est_alg = noise_est_algorithm
        return self.ue_noise_est_alg

    def set_ue_sss_algorithm(self,sss_algorithm):
        self.ue_sss_algorithm = sss_algorithm
        return self.ue_sss_algorithm

    def set_ue_snr_ema_coeff(self,snr_ema_coeff):
        self.ue_snr_ema_coeff = snr_ema_coeff
        return self.ue_snr_ema_coeff

    def set_ue_cfo_tol(self,cfo_tol):
        self.ue_cfo_tol = cfo_tol
        return self.ue_cfo_tol

    def print_parameter_values(self):
        print ("UE frequency :", self.ue_frequency)
        print ("UE equalizer :", self.ue_equalizer)
        print ("max turbodecoder its :", self.ue_max_turbo_decoder_its)
        print ("noise estimation algorithm :", self.ue_noise_est_alg)
        print ("ue sss algorithm : ", self.ue_sss_algorithm)
        print ("SNR moving average coefficient ", self.ue_snr_ema_coeff)
        print ("CFO tolerence :", self.ue_cfo_tol)

    def get_ue_cfo(self):
        cfo = self.send_command(True,0,which_metric_dict['CFO'],1,0,0)
        return cfo

    def get_ue_snr(self):
        snr = self.send_command(True, 0, which_metric_dict['SNR'], 1, 0, 0)
        return snr

    def get_ue_rsrp(self):
        rsrp = self.send_command(True, 0, which_metric_dict['RSRP'], 1, 0, 0)
        return rsrp

    def get_ue_rsrq(self):
        rsrq = self.send_command(True, 0, which_metric_dict['RSRQ'], 1, 0, 0)
        return rsrq

    def get_ue_noise(self):
        noise = self.send_command(True, 0, which_metric_dict['NOISE'], 1, 0, 0)
        return noise

    def get_ue_pdsch_miss(self):
        noise = self.send_command(True, 0, which_metric_dict['PDSCH'], 1, 0, 0)
        return noise

    def get_ue_CSI(self):
        have_CSI = self.send_command(True, 0, which_metric_dict['CSI'], 1, 0, 0)
        return have_CSI

    def get_ue_nFrames(self):
        N_FRAMES = self.send_command(True, 0, which_metric_dict['N_FRAMES'], 1, 0, 0)
        return N_FRAMES

    def get_ue_pdsch_miss(self):
        pdsch_miss = self.send_command(True, 0, which_metric_dict['PDSCH_MISS'], 1, 0, 0)
        return pdsch_miss

    def get_ue_pdcch_miss(self):
        pdcch_miss = self.send_command(True, 0, which_metric_dict['PDCCH_MISS'], 1, 0, 0)
        return pdcch_miss

    def get_ue_mod(self):
        MCS = self.send_command(True, 0, which_metric_dict['MOD'], 1, 0, 0)
        return MCS

    def get_ue_tbs(self):
        TBS = self.send_command(True, 0, which_metric_dict['TBS'], 1, 0, 0)
        return TBS


    def start_ue(self):
        self.is_ue = True

        # self.launch_response_reception_thread(True)
        # time.sleep(5)

        self.launch_iperf_reception_thread(True)

        os.chdir(self.directory)

        # self.ue_filename = self.ue_filename + ' -f ' + str(self.ue_frequency)  + ' -y ' + str(self.ue_cfo_tol) + ' -E ' + str(self.ue_snr_ema_coeff)  + ' -X ' + str(self.ue_sss_algorithm)  + ' -N ' + str(self.ue_noise_est_alg)  + ' -T ' + str(self.ue_max_turbo_decoder_its)   + ' -e ' + self.ue_equalizer
        #./ srsLTE / build / srslte / examples / pdsch_ue -f 2437e6 -r 1234 -u 2001 -U 127.0.0.1 -H 127.0.0.1
        self.ue_filename = self.ue_filename + ' -f ' + str(self.ue_frequency)  +  " -r 1234 -u 2001 -U 127.0.0.1 -H 127.0.0.1"

        f_duece = self.ue_filename.split()
        print("UE")
        print(f_duece)
        # process = subprocess.Popen(f_duece, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process = subprocess.Popen(f_duece, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        pid1 = process.pid
        self.ue_is_running = True
        self.ue_pid = pid1
        # self.ue_filename = './build/lib/examples/pdsch_ue_wishful'
        self.ue_filename = "./build/srslte/examples/pdsch_ue"
        print("[agent] UE up and running\n")


        lines_iterator = iter(process.stdout.readline, b"")
        for line in lines_iterator:
            print(line)




    def stop_ue(self):

        print("Stops iperf client.")
        self.eU_loop = False
        self.iperf_process.kill()
        # self.threads[0].join()
        # time.sleep(1)
        print("1")
        os.kill(self.ue_pid, signal.SIGINT)
        print("killing srslte UE process/n")
        time.sleep(3)
        self.ue_is_running = False


        # for t in self.threads:
        #     t.join

        print("[agent] UE successfully stopped")

    def set_enb_frequency(self,frequency):
        self.eNb_frequency = frequency
        if self.eNb_is_running:
            return self.send_command(False, self.eNb_frequency, -4, 0, 1, which_parameter_dict['FREQ'])
        else:
            return self.eNb_frequency

    def set_enb_rf_amp(self,rf_amp):
        self.eNb_rf_amp = rf_amp
        return self.eNb_rf_amp

    def set_enb_net_port(self,net_port):
        self.eNb_net_port = net_port
        return net_port


    def set_enb_gain(self,gain):
        self.eNb_gain = gain
        if self.eNb_is_running:
            return self.send_command(False, self.eNb_gain, -4, 0, 1, which_parameter_dict['GAIN'])
        else:
            return self.eNb_gain

    def set_enb_no_of_frames(self,no_of_frames):
        self.eNb_no_of_frames = no_of_frames
        self.eNb_filename = self.eNb_filename + ' -n ' + str(self.eNb_no_of_frames) 
        return no_of_frames

 
    def set_enb_no_of_prbs(self,no_of_prbs):
        self.eNb_no_of_prbs = no_of_prbs
        return self.eNb_no_of_prbs

    def set_enb_which_prbs(self,which_prbs):
        self.eNb_which_prbs = which_prbs
        if self.eNb_is_running:
            return self.send_command(False, self.eNb_which_prbs , -4, 0, 1, which_parameter_dict['PRBS'])
        else:
            return self.eNb_which_prbs

    def set_enb_select_MCS(self,mcs):
        self.eNb_MCS = mcs
        if self.eNb_is_running:
            return self.send_command(False,self.eNb_MCS , -4, 0, 1, which_parameter_dict['MCS'])
        else:
            return self.eNb_MCS

    def set_enb_send_pdsch_data(self,send_pdsch_data):
        self.eNb_send_pdsch_data = send_pdsch_data
        return send_pdsch_data

    
    def start_enb(self):
        self.is_ue = False

        # self.launch_response_reception_thread(False)
        # time.sleep(5)


        os.chdir(self.directory)
        # self.eNb_filename = self.eNb_filename + ' -f ' + str(self.eNb_frequency) + ' -p ' + str(self.eNb_no_of_prbs)  + ' -w ' + str(self.eNb_which_prbs) + ' -g ' + str(self.eNb_gain)  + ' -l ' + str(self.eNb_rf_amp) + ' -m ' + str(self.eNb_MCS) + ' -u ' + str(self.eNb_net_port) + ' -P  '   + str(self.eNb_send_pdsch_data)
        self.eNb_filename = self.eNb_filename + ' -f ' + str(self.eNb_frequency) + ' -p ' + str(self.eNb_no_of_prbs)  + ' -w 1,0,0,0,0,1,1,1,1,1 -b f -g ' + str(self.eNb_gain)  + ' -l ' + str(self.eNb_rf_amp) + ' -m ' + str(self.eNb_MCS) + ' -u ' + str(self.eNb_net_port)
        f_duece = self.eNb_filename.split()
        print(f_duece)
        process = subprocess.Popen(f_duece)
        pid1 = process.pid
        self.eNb_pid = pid1
        # self.eNb_filename = './build/lib/examples/pdsch_enodeb_wishful'
        self.eNb_filename = "./build/srslte/examples/pdsch_enodeb"
        self.eNb_is_running = True
        print("[agent] eNodeB is up and running\n")

        # return pid1
        time.sleep(8)

        # iperf - c 127.0.0.1 - p 2000 - i 1 - t 10000
        throughput = None
        dest_ip = "127.0.0.1"
        port = "2000"
        cmd = ['/usr/bin/iperf', '-c', dest_ip, '-p', port, '-f', 'k']
        time_duration = "10000"
        logging_interval = "1"
        cmd += ['-t', time_duration]
        cmd += ['-i', logging_interval]

        self.eNb_loop = True
        while self.eNb_loop:
            print('START Client Side iperf cmd: %s' + str(cmd))
            self.iperf_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            lines_iterator = iter(self.iperf_process.stdout.readline, b"")
            for line in lines_iterator:
                throughput = self.helper_parseIperf(line)
                # print(throughput)
                if throughput:
                    throughputFloat = float(throughput.rstrip().split(' ')[0])
                    # print(throughputFloat)
                    if throughputFloat > 50000 :
                        self.iperf_process.kill()
                        time.sleep(0.5)
                        break
                    else:
                        # th = report[1]
                        # delta = report[0]
                        # if delta > float(logging_interval) + 0.1:
                        #     throughput = th
                        #     self.log.info("one o more stations disconnected close iperf server")
                        #     break
                        # ip_address = report[2]
                        message = {"delta": 1, "throughput": throughputFloat*1000, "ip_address": "172.16.16.11"}
                        # print("%s" % (message))
                        self.socket_zmq.send_json(message)

        self.iperf_process.kill()
        print("iperf killed and exit ENB")

        # for line in lines_iterator:
        #     report = self.helper_parseIperfLogging(line)
        #     if report:
        #         th = report[1]
        #         delta = report[0]
        #         if delta > float(logging_interval) + 0.1:
        #             throughput = th
        #             print("one o more stations disconnected close iperf server")
        #             break
        #         ip_address = report[2]
        #         message = {"delta": delta, "throughput": th, "ip_address": ip_address}
        #         print("%s" % (message))
        #         # self.socket_zmq.send_json(message)

        return pid1

    def stop_enb(self):

        print("Stops iperf client.")
        self.iperf_process.kill()

        self.eNb_loop = False
        time.sleep(1)

        print("[agent] killing srslte eNodeB process with ctrl C/n")
        os.kill(self.eNb_pid, signal.SIGINT)
        time.sleep(1)

        self.eNb_is_running = False

        # for t in self.threads:
        #     t.join

        print("[agent] eNb successfully stopped")

    def send_command(self, is_ue, config_value, which_metric, wants_metric, make_config, which_config):
        try:
            if is_ue and self.ue_is_running == False:
                raise ValueError("the UE is not running")

            if not is_ue and not self.eNb_is_running:
                raise ValueError("the eNodeB is not running")
            send_stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if is_ue:
                server = self.ue_port_server
            else:
                server = self.eNb_port_server
            send_stream.connect((self.ip, server))
            if wants_metric:
                print('[agent] : getting ', which_metric_dict_rev[which_metric] , '......')
            else:
                print('[agent] : setting ', which_parameter_dict_rev[which_config], '.....')
            j = json.dumps({'config_value':config_value, 'which_metric':which_metric,'wants_metric': wants_metric, 'make_config':make_config,'which_config':which_config})
            MESSAGE = j

            send_stream.send(MESSAGE.encode())
            send_stream.close()
            if wants_metric:
                metric = self.metric_buffer.get()
                print  (which_metric_dict_rev[which_metric] ,' is : ', metric)
                return metric
            else:
                reconfig = self.config_buffer.get()
                print("[agent] parameter : ", which_parameter_dict_rev[which_config], "has been reconfigured to ", reconfig)
                return reconfig

            time.sleep(10)

        except ValueError as msg:
            print (msg)

    def start_server(self, is_ue ,stop_event, timeout):

        rece_stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print ('[agent] Starting  Server ... \n')

        if is_ue:
            client_port = self.ue_port_client
            print('[agent] UE server\n')
        else:
            client_port = self.eNb_port_client
            print('[agent] enb server\n')

        rece_stream.bind((self.ip, client_port))
        rece_stream.listen(1)

        conn, addr = rece_stream.accept()
        try:
            while 1:
                data = conn.recv(150)
                if not data:
                    conn.close()
                    print('[agent] Restarting server ...\n')
                    break
                else:
                    data = data.decode('utf-8')
                    if data == 'hello':
                        print("TEST of receive connection complete")
                    else:
                        res = json.loads(data)
                        if not res['is_reconfig']:
                            self.metric_buffer.put(res['metric_value'])
                        else:
                            self.config_buffer.put(res['reconfig_value'])

        except KeyboardInterrupt:
            print('closing python server\n')

    def launch_response_reception_thread(self, is_ue):
        rece_thread = threading.Thread(target=self.start_server,args=(is_ue,self.killpill,0))
        rece_thread.start()
        self.threads.append(rece_thread)

    def start_server_iperf(self, is_ue, timeout):
        # iperf -s -p 2001 -i 1
        throughput = None
        dest_ip = "127.0.0.1"
        port = "2001"
        cmd = ['/usr/bin/iperf', '-s', '-p', port, '-f', 'k']
        time_duration = "10000"
        logging_interval = "1"
        cmd += ['-t', time_duration]
        cmd += ['-i', logging_interval]

        self.eU_loop = True
        while self.eU_loop:
            print('START Client Side iperf cmd: %s' + str(cmd))
            self.iperf_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            lines_iterator = iter(self.iperf_process.stdout.readline, b"")
            for line in lines_iterator:
                throughput = self.helper_parseIperf(line)
                # print(throughput)
                if throughput:
                    throughputFloat = float(throughput.rstrip().split(' ')[0])
                    # print(throughputFloat)
                    # message = {"delta": 1, "throughput": throughputFloat * 1000, "ip_address": "172.16.16.6"}
                    message = {"delta": 1, "throughput": throughputFloat * 1000, "ip_address": self.ue_nof_antennas}

                    # print("%s" % (message))
                    self.socket_zmq.send_json(message)

        self.iperf_process.kill()

    def launch_iperf_reception_thread(self, is_ue):
        rece_thread = threading.Thread(target=self.start_server_iperf, args=(is_ue, 0))
        rece_thread.start()
        self.threads.append(rece_thread)

    def helper_parseIperf(self, iperfOutput):
        """Parse iperf output and return bandwidth.
        iperfOutput: string
        returns: result string
        """
        import re

        iperfOutput = iperfOutput.decode('ascii')
        # print("iperfOutput : %s " % iperfOutput)

        r = r'([\d\.]+ \w+/sec)'
        m = re.findall( r, iperfOutput )
        # print("m : %s " % m)

        if m:
            return m[-1]
        else:
            return None


    def helper_parseIperfLogging(self, iperfOutput):
        """Parse iperf output and return (deltat, bandwdith).
        Expects Kbit/s in report
        iperfOutput: strig
        returns: result tuple
        """

        import re
        iperfOutput = iperfOutput.decode('ascii')
        # print("iperfOutput : %s " % iperfOutput)

        #[  5]  8.0- 9.0 sec   121 KBytes   988 Kbits/sec   2.449 ms    0/   84 (0%)
        r1 = r'\[\s+(\d)\]\s+(\d+\.\d)\-\s*(\d+\.\d)\s*sec\s*(\d+)\s*KBytes\s*(\d+)\s*Kbits\/sec'
        #[  3] local 192.168.3.102 port 1234 connected with 192.168.3.105 port 53446
        r2 = r'\[\s+(\d)\].*?with\s*(.*?)\s*port'
        #[  6] 24.0-25.0 sec  31.6 KBytes   259 Kbits/sec   2.829 ms    4/   26 (15%)
        r3 = r'\[\s+(\d)\]\s+(\d+\.\d)\-\s*(\d+\.\d)\s*sec\s*(\d+\.\d)\s*KBytes\s*(\d+)\s*Kbits\/sec'
        #[  6] 12.0-13.0 sec   306 Kbits   306 Kbits/sec   7.900 ms    0/   26 (0%)
        r4 = r'\[\s+(\d)\]\s+(\d+\.\d)\-\s*(\d+\.\d)\s*sec\s*(\d+)\s*Kbits\s*(\d+)\s*Kbits\/sec'

        m = re.findall( r2, iperfOutput )
        if m:
            m0 = m[0]
            self.sta_id[self.sta_id_max] = m0[0]
            self.sta_ip_address[self.sta_id_max] = m0[1]
            self.sta_id_max += 1
            return None

        mr1 = re.findall( r1, iperfOutput )
        mr3 = re.findall( r3, iperfOutput )
        mr4 = re.findall( r4, iperfOutput )
        m = None
        if mr1:
            m=mr1
        if mr3:
            m=mr3
        if mr4:
            m=mr4
        if m:
            m0 = m[0]
            local_sta_id = m0[0]
            t0 = float(m0[1])
            t1 = float(m0[2])
            th = float(m0[4])
            delta = t1 - t0

            sta_found = False
            local_sta_ip_address = None
            for jj in range(self.sta_id_max):
                if self.sta_id[jj] == local_sta_id :
                    local_sta_ip_address = self.sta_ip_address[jj]
                    sta_found = True

            if sta_found :
                return (delta, th, local_sta_ip_address)
            else:
                return None

        else:
            return None


@wishful_module.build_module
class SrslteModule(wishful_module.AgentModule):
    def __init__(self):
        super(SrslteModule, self).__init__()
        self.srs = srslte_iface()
        self.srs.srsradio_state = RadioProgramState.IDLE

    @wishful_module.bind_function(upis.radio.set_parameters)
    def srslte_set_var(self,param_key_values_dict):

        for k, v in param_key_values_dict.items():
            if k == 'IS_UE':
                self.srs.is_ue = v

        if self.srs.is_ue:
            self.srslte_set_ue_var(param_key_values_dict)
        else:
            self.srslte_set_enb_var(param_key_values_dict)

    @wishful_module.bind_function(upis.radio.get_parameters)
    def srslte_get_var(self, param_key_list):
        if self.srs.is_ue:
            return self.srslte_get_ue_var(param_key_list)
        else:
            return self.srslte_get_enb_var(param_key_list)

    @wishful_module.bind_function(upis.radio.get_measurements)
    def srslte_get_measurements(self,measurement_key_list):
        out  = {}
        for k in measurement_key_list:
            if k == 'CFO':
                out = {'CFO': self.srs.get_ue_cfo()}
            elif k == 'SNR':
                out = {'SNR': self.srs.get_ue_snr()}
            elif k == 'RSRP':
                out = {'RSRP': self.srs.get_ue_rsrp()}
            elif k == 'RSRQ':
                out = {'RSRQ': self.srs.get_ue_rsrq()}
            elif k == 'NOISE':
                out = {'NOISE': self.srs.get_ue_noise()}
            elif k == 'CSI':
                out = {'CSI': self.srs.get_ue_CSI()}
            elif k == 'N_FRAMES':
                out = {'N_FRAMES': self.srs.get_ue_nFrames()}
            elif k == 'PDSCH_MISS':
                out = {'PDSCH_MISS': self.srs.get_ue_pdsch_miss()}
            elif k == 'PDCCH_MISS':
                out = {'PDCCH_MISS': self.srs.get_ue_pdcch_miss()}
            elif k == 'MOD':
                out = {'MOD': self.srs.get_ue_mod()}
            elif k == 'TBS':
                out = {'TBS': self.srs.get_ue_tbs()}
            else:
                print("invalid metric\n")
        return out

    @wishful_module.bind_function(upis.radio.activate_radio_program)
    def srslte_start_radio(self,name):
        if name == 'UE':
            self.srs.is_ue = True
            self.srs.start_ue()
        elif name == 'ENB':
            self.srs.is_ue = False
            self.srs.start_enb()
        else:
            print("invalid radio mode, choose either UE or ENB")

    @wishful_module.bind_function(upis.radio.get_running_radio_program)
    def srslte_is_running(self):
        if self.srs.eNb_is_running or self.srs.ue_is_running:
            return True
        else:
            return False


    @wishful_module.bind_function(upis.radio.deactivate_radio_program)
    def srslte_stop_radio(self,name):
        if self.srs.is_ue == True:
            self.srs.stop_ue()
        else:
            self.srs.stop_enb()



    def srslte_set_ue_var(self, param_key_values_dict):
        for k, v in param_key_values_dict.items():
            if k  == 'FREQ':
                self.srs.set_ue_frequency(v)
            elif k == 'EQUALIZER_MODE':
                self.srs.set_ue_equalizer(v)
            elif k == 'MAX_TURBO_ITS':
                self.srs.set_ue_max_turbo_decoder_its(v)
            elif k == 'NOISE_EST_ALG':
                self.srs.set_ue_noise_est_alg(v)
            elif k == 'SSS_ALGORITHM':
                self.srs.set_ue_sss_algorithm(v)
            elif k == 'SNR_EMA_COEFF':
                self.srs.set_ue_snr_ema_coeff(v)
            elif k == 'CFO_TOL':
                self.srs.set_ue_cfo_tol(v)
            elif k == 'GAIN':
                self.srs.set_ue_gain(v)
            elif k == 'NO_OF_ANTENNAS':
                self.srs.set_ue_nof_antennas(v)
            else :
                print("invalid parameter\n")

    def srslte_set_enb_var(self, param_key_values_dict):
        print("param_key_values_dict",param_key_values_dict)
        for k, v in param_key_values_dict.items():
            if k == 'FREQ':
                self.srs.set_enb_frequency(v)
            elif k == 'RF_AMP':
                self.srs.set_enb_rf_amp(v)
            elif k == 'GAIN':
                self.srs.set_enb_gain(v)
            elif k == 'NO_OF_FRAMES':
                self.srs.set_enb_no_of_frames(v)
            elif k == 'NO_OF_PRBS':
                self.srs.set_enb_no_of_prbs(v)
            elif k == 'WHICH_PRBS':
                self.srs.set_enb_which_prbs(v)
            elif k == 'MCS':
                self.srs.set_enb_select_MCS(v)
            else:
                print("invalid parameter\n")

    def srslte_get_ue_var(self, param_key_list):
        ret = {}
        for k in param_key_list:
            if k == 'FREQ':
                ret.update({'FREQ': self.srs.ue_frequency})
            elif k == 'EQUALIZER_MODE':
                ret.update({'EQUALIZER_MODE':self.srs.ue_equalizer})
            elif k == 'MAX_TURBO_ITS':
                ret.update({'MAX_TURBO_ITS':self.srs.ue_max_turbo_decoder_its})
            elif k == 'NOISE_EST_ALG':
                ret.update({'NOISE_EST_ALG':self.srs.ue_noise_est_alg})
            elif k == 'SSS_ALGORITHM':
                ret.update({'SSS_ALGORITHM':self.srs.ue_sss_algorithm})
            elif k == 'SNR_EMA_COEFF':
                ret.update({'SNR_EMA_COEFF':self.srs.ue_snr_ema_coeff})
            elif k == 'CFO_TOL':
                ret.update({'CFO_TOL':self.srs.ue_cfo_tol})
            elif k == 'GAIN':
                ret.update({'GAIN':self.srs.ue_gain})
            elif k == 'NO_OF_ANTENNAS':
                ret.update({'NO_OF_ANTENNAS':self.srs.ue_nof_antennas})
            else:
                print("invalid parameter\n")
        return ret

    def srslte_get_enb_var(self, param_key_list):
        ret = {}
        for k  in param_key_list:
            if k == 'FREQ':
                ret.update({'FREQ': self.srs.eNb_frequency})
            elif k == 'RF_AMP':
                ret.update({'RF_AMP':self.srs.eNb_rf_amp})
            elif k == 'GAIN':
                ret.update({'GAIN':self.srs.eNb_gain})
            elif k == 'NO_OF_FRAMES':
                ret.update({'NO_OF_FRAMES':self.srs.eNb_no_of_frames})
            elif k == 'NO_OF_PRBS':
                ret.update({'NO_OF_PRBS':self.srs.eNb_no_of_prbs})
            elif k == 'WHICH_PRBS':
                ret.update({'WHICH_PRBS':self.srs.eNb_which_prbs})
            elif k == 'MCS':
                ret.update({'MCS': self.srs.eNb_MCS})
            elif k == 'NET_PORT':
                ret.update({'NET_PORT': self.srs.eNb_net_port})
            elif k == 'NO_OF_PRBS':
                ret.update({'NO_OF_PRBS': self.srs.eNb_no_of_prbs})
            elif k == 'WHICH_PRBS':
                ret.update({'WHICH_PRBS': self.srs.eNb_which_prbs})
            elif k == 'NO_OF_FRAMES':
                ret.update({'NO_OF_FRAMES': self.srs.eNb_no_of_frames})
            else:
                print("invalid parameter\n")
        return ret