import SocketServer
import subprocess
import os
import netifaces as ni
import socket
import os
import datetime
import json
import time
import numpy
import thread
import signal
import sys
from ctrl_config import *

msg_data = "{}"
EST_SLOT = 4

perl_cmd = "\
#!/usr/bin/perl \n\
use strict; \n\
use warnings; \n\
use Time::HiRes; \n\
my $reporting_interval = 1.0; # seconds \n\
my $bytes_this_interval = 0; \n\
my $start_time = [Time::HiRes::gettimeofday()]; \n\
STDOUT->autoflush(1); \n\
while (<>) { \n\
  if (/ length (\d+):/) { \n\
    $bytes_this_interval += $1; \n\
    my $elapsed_seconds = Time::HiRes::tv_interval($start_time); \n\
    if ($elapsed_seconds > $reporting_interval) { \n\
       my $bps = $bytes_this_interval / $elapsed_seconds; \n\
       $bps*=8; \n\
       printf \"%10.2f\n\",$bps; \n\
       $start_time = [Time::HiRes::gettimeofday()]; \n\
       $bytes_this_interval = 0; \n\
    }\n\
  }\n\
}"
perl_script = open("/tmp/netbps", "w")
perl_script.write(perl_cmd)
perl_script.close()


class MyTCPHandler(SocketServer.BaseRequestHandler):
	def send_to_controller(self, ip_ctrl, port_ctrl, msg):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		ip_ctrl = socket.gethostbyname(ip_ctrl)
		jmsg = json.loads(msg)
		msg = json.dumps(jmsg)
		sock.sendto(msg, (ip_ctrl, port_ctrl))

	def handle(self):
		global msg_data
		# self.request is the TCP socket connected to the client
		msg_data = self.request.recv(1024).strip()
		# print "{} wrote:".format(self.client_address[0])
		print(msg_data)

	# self.send_to_controller(IP_CONTROLLER,AP_TO_CTRL_PORT,msg_data)


def shift(l, n):
	return l[n:] + l[:n]


def get_last_psucc(psucc_list, L, est_slot):
	mask = ""
	for x in psucc_list:
		if x > 0.5:
			maskval = 1
		elif numpy.isinf(x):
			maskval = 0
		else:
			maskval = 0
		mask = "{}{}".format(mask, maskval)

	mask_int = [int(x) for x in list(mask)]
	mask_sum = 0
	n_shift = 0
	for x in list(mask_int):
		mask_sum += x

	target_mask = [1] * mask_sum + [0] * (L - mask_sum)

	while n_shift < L:
		if mask_int != target_mask:
			mask_int = shift(mask_int, -1)
			psucc_list = shift(psucc_list, -1)
			n_shift = n_shift + 1;
		else:
			break;
	psucc = psucc_list[mask_sum - 1]
	return psucc;


def syncAP(psucc_thresh=0.75):
	psucc_ = 0;
	while True:
		try:
			# if True:

			stats = json.loads(msg_data)
			if stats:
				psucc = float(stats.get('psucc'))
				mask_sum = float(stats.get('mask_sum'))
				psucc_list = stats.get('psucc_list')
				psucc = get_last_psucc(psucc_list, 10, EST_SLOT)
				if numpy.isnan(psucc):
					psucc = float(0);

				val = 0
				if int(stats.get('enable_controller')) > 1:
					print("mask_sum={}, EST_SLOT={}, psucc={}".format(mask_sum, EST_SLOT, psucc))
					if (mask_sum < EST_SLOT) or (psucc < float(psucc_thresh)):
						val = 10
				if val != 0:
					print("TSF compensation")
					os.system('bytecode-manager --set-tsf {} > /dev/null'.format(val))
		except Exception, e:  # Hack to effect skip-on-prompt using abort-on-prompt setting provided by Fabric.
			print(e)
		time.sleep(0.1)


def enforceXFSM(msg):
	sock = socket.socket(socket.AF_INET,  # Internet
						 socket.SOCK_DGRAM)  # UDP
	sock.bind((IP_ETH_AP, STATS_PORT))
	global EST_SLOT
	while True:
		data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
		try:
			tmp_data = json.loads(data)
			if 'EST_SLOT' in data:
				if tmp_data['EST_SLOT']:
					EST_SLOT = int(tmp_data['EST_SLOT'])
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((IP_WIFI_UE3, AP_TO_UE_PORT))
			s.send(data)
			s.close()
		except Exception, e:
			print
			e


def execute_cmd(cmd, sh=False):
	if sh:
		popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
	else:
		popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)

	for stdout_line in iter(popen.stdout.readline, ""):
		yield stdout_line
	popen.stdout.close()
	return_code = popen.wait()
	if return_code:
		raise subprocess.CalledProcessError(return_code, cmd)


def sniffer_server(x):
	iperf_port = 5001
	#	cmd = ['iperf', '-s', '-u', '-p',str(iperf_port),'-i','1','-y', 'C']
	cmd = "tcpdump -i wlan0 udp port 5001 -tt -l -n -e | perl /tmp/netbps"
	msg = {}
	for path in execute_cmd(cmd, True):
		iperf_res = path.split(',')
		print
		iperf_res
		msg['type'] = 'iperf_wmp'
		msg['thr'] = iperf_res[0]
		jmsg = json.dumps(msg)

		# forward to UDP socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendto(jmsg, (IP_CONTROLLER, AP_TO_CTRL_PORT))


def iperf_server(x):
	iperf_port = 5001
	cmd = ['iperf', '-s', '-u', '-p', str(iperf_port), '-i', '1', '-y', 'C']
	msg = {}
	for path in execute_cmd(cmd):
		iperf_res = path.split(',')
		msg['type'] = 'iperf_wmp'
		msg['thr'] = iperf_res[8]
		jmsg = json.dumps(msg)

	# forward to UDP socket


#		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#		sock.sendto(jmsg, (IP_CONTROLLER,AP_TO_CTRL_PORT))

server = None


def handle_ctrl_c(signal, frame):
	print("Got ctrl+c, going down!")
	try:
		server.server_close()
		os.system('killall -9 iperf')
	except Exception, e:
		print(e)
	sys.exit(0)


if __name__ == "__main__":
	iface = 'wlan0'
	ni.ifaddresses(iface)
	signal.signal(signal.SIGINT, handle_ctrl_c)
	HOST = ni.ifaddresses(iface)[2][0]['addr']

	# Create the server, binding to localhost on port 9999
	thread.start_new_thread(syncAP, (0.85,))
	thread.start_new_thread(enforceXFSM, (1,))
	thread.start_new_thread(sniffer_server, (1,))
	thread.start_new_thread(iperf_server, (1,))
	SocketServer.TCPServer.allow_reuse_address = True
	server = SocketServer.TCPServer((HOST, UE_TO_AP_PORT), MyTCPHandler)

	# Activate the server; this will keep running until you
	# interrupt the program with Ctrl-C
	server.serve_forever()