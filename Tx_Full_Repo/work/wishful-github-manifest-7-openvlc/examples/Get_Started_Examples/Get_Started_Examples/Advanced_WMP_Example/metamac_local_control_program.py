"""
Local control program to be executed on remote nodes.
"""

__author__ = "Domenico Garlisi"
__copyright__ = "Copyright (c) 2016, CNIT"
__version__ = "0.1.0"
__email__ = "domenico.garlisi@cnit.it"

# Definition of Meta-MAC Local Control Program
def metamac_local_control_program(controller):

	#import
	import time
	import datetime
	import sys
	from sys import stdout
	import ctypes
	import os
	import csv
	import threading
	import math
	import zmq
	import netifaces as ni
	import logging
	#references to Wishful framework
	global upiHCImpl # interface used for communication with global controller and control runtime

	sys.path.append('../../../')
	sys.path.append("../../../agent_modules/wifi_ath")
	sys.path.append("../../../agent_modules/wifi_wmp")
	sys.path.append("../../../agent_modules/wifi")
	sys.path.append("../../../agent_modules/net_linux")
	sys.path.append('../../../upis')
	sys.path.append('../../../framework')
	sys.path.append('../../../agent')
	from agent_modules.wifi_wmp.wmp_structure import UPI_R

	libc = ctypes.CDLL('libc.so.6')
	usleep = lambda x: time.sleep(x/1000000.0)

	SUCCESS = 0
	FAILURE = 2


	#socket iperf pointer
	iperf_socket = None

	def rcv_from_iperf_socket(iperf_througputh, iperf_server_ip_address):
		"""
		This function collects the throughput information result
		"""
		iperf_thread = threading.currentThread()
		print('start socket iperf')
		iperf_port = "8301"
		context = zmq.Context()
		iperf_socket = context.socket(zmq.SUB)
		print("tcp://%s:%s" % (iperf_server_ip_address, iperf_port))
		iperf_socket.connect("tcp://%s:%s" % (iperf_server_ip_address, iperf_port))
		iperf_socket.setsockopt_string(zmq.SUBSCRIBE, '')

		print('socket iperf started')
		while getattr(iperf_thread, "do_run", True):
			parsed_json = iperf_socket.recv_json()
			print('my address %s - parsed_json : %s' % (str(wlan_ip_address), str(parsed_json)))
			rcv_ip_address = parsed_json['ip_address']
			if rcv_ip_address == wlan_ip_address:
				print('parsed_json : %s' % str(parsed_json))
				iperf_througputh[0] = float(parsed_json['throughput'])


	"""				************				"""
	"""				MAIN PROGRAM				"""
	"""				************				"""

	log = logging.getLogger()
	log.info('*********** WISHFUL *************')
	log.info('*********** starting local WiSHFUL controller **********************')



	interface = 'wlan0'
	wlan_ip_address = controller.net.get_iface_ip_addr(interface)
	wlan_ip_address = wlan_ip_address[0]


	if wlan_ip_address == "192.168.3.111":
		iperf_server_ip_address = "10.8.8.112"
	else:
		iperf_server_ip_address = "10.8.8.102"
	print('my ip ' + wlan_ip_address + ' : server ' + iperf_server_ip_address)


	iperf_througputh = []
	iperf_througputh.append(0.0)
	iperf_thread = threading.Thread(target=rcv_from_iperf_socket, args=(iperf_througputh,iperf_server_ip_address))
	iperf_thread.do_run = True
	iperf_thread.start()

	time.sleep(2)



	print("Local ctrl program started: {}".format(controller.name))
	# metamac control loop
	while not controller.is_stopped():
		msg = controller.recv(timeout=1)
		if msg:
			print("Receive message %s" % str(msg))
			if msg.get('protocol'):
				protocol = msg['protocol']
				print("in %s" % str(protocol))

		controller.send_upstream({ "measure" : [[0,0,iperf_througputh[0]]], "wlan_ip_address" : (wlan_ip_address) })


	print("Local ctrl program stopping: {}".format(controller.name))
	iperf_thread.do_run = False
	iperf_thread.join()
	time.sleep(2)


