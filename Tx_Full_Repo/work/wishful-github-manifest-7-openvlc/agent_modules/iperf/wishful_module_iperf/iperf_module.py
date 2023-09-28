import logging
import os, sys, time, subprocess
import wishful_upis as upis
import wishful_framework as wishful_module
import datetime
import zmq
import netifaces as ni
import ctypes

libc = ctypes.CDLL('libc.so.6')
usleep = lambda x: time.sleep(x/1000000.0)

CLOCK_MONOTONIC_RAW = 4 # see <linux/time.h>
class timespec(ctypes.Structure):
    _fields_ = [
	('tv_sec', ctypes.c_long),
	('tv_nsec', ctypes.c_long)
]

librt = ctypes.CDLL('librt.so.1', use_errno=True)
clock_gettime = librt.clock_gettime
clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]

__author__ = "Piotr Gawlowicz, Mikolaj Chwalisz, Domenico Garlisi"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, chwalisz}@tkn.tu-berlin.de, domenico.garlisi@cnit.it"

'''
    Packet flows are generated using IPerf tool.
'''



@wishful_module.build_module
class IperfModule(wishful_module.AgentModule):
    def __init__(self):
        super(IperfModule, self).__init__()
        self.log = logging.getLogger('IperfModule.main')
        self.iperf_port = "8301"
        context = zmq.Context()
        self.socket_zmq = context.socket(zmq.PUB)
        self.socket_zmq.bind("tcp://*:%s" % self.iperf_port)
        self.sta_id = {}
        self.sta_ip_address = {}
        self.sta_id_max = 0




    @wishful_module.bind_function(upis.net.create_packetflow_sink)
    def create_packetflow_sink(self, port, logging_interval, use_udp, bind_interface):
        self.log.info("Starts iperf server on port {}".format(port))

        import subprocess
        cmd_str = "ps aux | awk '/[i]perf -s/{print $2}'"
        cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)
        cmd_output = cmd_output.decode('ascii')
        if cmd_output :
            flow_info_lines = cmd_output.rstrip().split('\n')
            for ii in range(0, len(flow_info_lines)):
                cmd_str = 'kill -9 ' + str(flow_info_lines[ii])
                cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)

        throughput = None
        multicast_traffic = False
        if multicast_traffic :
            cmd = ['/usr/bin/iperf', '-s', '-B', '239.255.1.3', '-i', logging_interval, '-f', 'k', '-p', port]
        else:
            cmd = ['/usr/bin/iperf', '-s', '-i', logging_interval, '-f', 'k', '-p', port]

        if use_udp:
            cmd += ['-u']
        # if bind_interface:
        #     cmd += ['-B', bind_interface]

        self.log.info('START server Side iperf cmd: %s' + str(cmd))

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        lines_iterator = iter(process.stdout.readline, b"")

        for line in lines_iterator:
            report = self.helper_parseIperfLogging(line)
            if report:
                per = report[3]
                th = report[1]
                delta = report[0]
                #print(th, " - ", per)
                if delta > float(logging_interval) + 0.1:
                    throughput = th
                    self.log.info("one o more stations disconnected close iperf server" )
                    break
                ip_address = report[2]
                message = {"delta": delta, "throughput": th*1000, "ip_address": ip_address, "per":per}
                self.log.debug("%s" % (message))
                self.socket_zmq.send_json(message)

        process.kill()

        self.log.info('Server side Throughput : ' + str(throughput))
        sys.stdout.flush()
        msg = {"type": "Server", "throughput" : throughput}

        return msg

    @wishful_module.bind_function(upis.net.register_packetflow_logging)
    def register_packetflow_logging(self, traffic_logger_port, sink_ip_address, traffic_ip_address):
        context = zmq.Context()
        traffic_logging_socket = context.socket(zmq.SUB)
        self.log.info("tcp://%s:%s" % (sink_ip_address, traffic_logger_port))
        traffic_logging_socket.connect("tcp://%s:%s" % (sink_ip_address, traffic_logger_port))
        traffic_logging_socket.setsockopt_string(zmq.SUBSCRIBE, '')
        localControllerId = self.get_local_controller_id()

        current_time =  self.monotonic_time()
        last_time_message = current_time
        timeout = 30
        while current_time - last_time_message < timeout:
            traffic_message = traffic_logging_socket.recv_json()
            current_time =  self.monotonic_time()
            rcv_ip_address = traffic_message['ip_address']
            if rcv_ip_address == traffic_ip_address:
                self.log.debug('traffic_message : %s' % str(traffic_message))
                last_time_message = current_time
                if not localControllerId:
                    self.agent.send_upstream(traffic_message)
                else:
                    self.agent.send_to_local_ctr_program(traffic_message)


    @wishful_module.bind_function(upis.net.destroy_packetflow_sink)
    def destroy_packetflow_sink(self):
        self.log.info("Stops iperf server.")
        import subprocess
        cmd_str = "ps aux | awk '/[i]perf -s/{print $2}'"
        cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)
        cmd_output = cmd_output.decode('ascii')
        if cmd_output :
            flow_info_lines = cmd_output.rstrip().split('\n')
            for ii in range(0, len(flow_info_lines)):
                cmd_str = 'kill -9 ' + str(flow_info_lines[ii])
                cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)
        return "Server stopped"


    @wishful_module.bind_function(upis.net.start_packetflow)
    def start_packetflow(self, dest_ip, port, time_duration, bandwidth, frame_length):
        self.log.info("Start iperf client.")

        import subprocess
        cmd_str = "ps aux | awk '/[i]perf -c/{print $2}'"
        cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)
        cmd_output = cmd_output.decode('ascii')
        if cmd_output :
            flow_info_lines = cmd_output.rstrip().split('\n')
            for ii in range(0, len(flow_info_lines)):
                cmd_str = 'kill -9 ' + str(flow_info_lines[ii])
                cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)

        throughput = None
        multicast_traffic = False
        if multicast_traffic:
            cmd = ['/usr/bin/iperf', '-c', '239.255.1.3', '-p', port]
        else:
            cmd = ['/usr/bin/iperf', '-c', dest_ip, '-p', port]
        if time_duration:
            cmd += ['-t', time_duration]
        if bandwidth:
            cmd += ['-b', bandwidth]
        if frame_length:
            cmd += ['-l', frame_length]

        self.log.info('START Client Side iperf cmd: %s' + str(cmd))

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        lines_iterator = iter(process.stdout.readline, b"")
        for line in lines_iterator:
            throughput = self.helper_parseIperf(line)
            if throughput:
                break

        process.kill()
        self.log.info('Client Side Throughput : ' + str(throughput))
        sys.stdout.flush()
        msg = {"type": "Client", "throughput" : throughput}
        return msg


    @wishful_module.bind_function(upis.net.stop_packetflow)
    def stop_packetflow(self):
        self.log.info("Stops iperf client.")
        import subprocess
        cmd_str = "ps aux | awk '/[i]perf -c/{print $2}'"
        cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)
        cmd_output = cmd_output.decode('ascii')
        if cmd_output :
            flow_info_lines = cmd_output.rstrip().split('\n')
            for ii in range(0, len(flow_info_lines)):
                self.log.info("STOP IPERF pid " +  str(flow_info_lines[ii]))
                cmd_str = 'sudo kill -9 ' + str(flow_info_lines[ii])
                cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)

        return "* Client stopped"


    def helper_parseIperf(self, iperfOutput):
        """Parse iperf output and return bandwidth.
        iperfOutput: string
        returns: result string
        """
        import re

        iperfOutput = iperfOutput.decode('ascii')
        self.log.debug("iperfOutput : %s " % iperfOutput)

        r = r'([\d\.]+ \w+/sec)'
        m = re.findall( r, iperfOutput )
        self.log.debug("m : %s " % m)

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
        # self.log.debug("iperfOutput : %s " % iperfOutput)
        # print(iperfOutput)

        #[  5]  8.0- 9.0 sec   121 KBytes   988 Kbits/sec   2.449 ms    0/   84 (0%)
        # r1 = r'\[\s+(\d)\]\s+(\d+\.\d)\-\s*(\d+\.\d)\s*sec\s*(\d+)\s*KBytes\s*(\d+)\s*Kbits\/sec'
        r1 = r'\[\s+(\d+)\]\s+(\d+\.\d)\-\s*(\d+\.\d)\s*sec\s*(\d+)\s*KBytes\s*(\d+)\s*Kbits\/sec.*?\((\d+\.?\d*?)%\)'

        #"[ 10] local 192.168.0.2 port 1234 connected with 192.168.0.14 port 38868"
        #[  3] local 192.168.3.102 port 1234 connected with 192.168.3.105 port 53446
        r2 = r'\[\s+(\d+)\].*?with\s*(.*?)\s*port'

        #[  6] 24.0-25.0 sec  31.6 KBytes   259 Kbits/sec   2.829 ms    4/   26 (15%)
        # r3 = r'\[\s+(\d)\]\s+(\d+\.\d)\-\s*(\d+\.\d)\s*sec\s*(\d+\.\d)\s*KBytes\s*(\d+)\s*Kbits\/sec'
        r3 = r'\[\s+(\d+)\]\s+(\d+\.\d)\-\s*(\d+\.\d)\s*sec\s*(\d+\.\d)\s*KBytes\s*(\d+)\s*Kbits\/sec.*?\((\d+\.?\d*?)%\)'
        #[  6] 12.0-13.0 sec   306 Kbits   306 Kbits/sec   7.900 ms    0/   26 (0%)
        # r4 = r'\[\s+(\d)\]\s+(\d+\.\d)\-\s*(\d+\.\d)\s*sec\s*(\d+)\s*Kbits\s*(\d+)\s*Kbits\/sec'
        r4 = r'\[\s+(\d+)\]\s+(\d+\.\d)\-\s*(\d+\.\d)\s*sec\s*(\d+)\s*Kbits\s*(\d+)\s*Kbits\/sec.*?\((\d+\.?\d*?)%\)'

        m = re.findall( r2, iperfOutput )
        if m:
            # print(m)
            m0 = m[0]
            self.sta_id[self.sta_id_max] = m0[0]
            self.sta_ip_address[self.sta_id_max] = m0[1]
            self.sta_id_max += 1
            return None

        mr1 = re.findall( r1, iperfOutput )
        mr3 = re.findall( r3, iperfOutput )
        mr4 = re.findall( r4, iperfOutput )
        # print(mr1)
        # print(mr3)
        # print(mr4)

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
            per = float(m0[5])
            delta = t1 - t0

            sta_found = False
            local_sta_ip_address = None
            for jj in range(self.sta_id_max):
                if self.sta_id[jj] == local_sta_id :
                    local_sta_ip_address = self.sta_ip_address[jj]
                    sta_found = True

            if sta_found :
                return (delta, th, local_sta_ip_address, per)
            else:
                return None

        else:
            return None


    def monotonic_time():
        t = timespec()
        if clock_gettime(CLOCK_MONOTONIC_RAW , ctypes.pointer(t)) != 0:
            errno_ = ctypes.get_errno()
            raise OSError(errno_, os.strerror(errno_))
        return t