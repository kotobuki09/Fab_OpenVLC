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

	CLOCK_MONOTONIC_RAW = 4 # see <linux/time.h>
	class timespec(ctypes.Structure):
		_fields_ = [
		('tv_sec', ctypes.c_long),
		('tv_nsec', ctypes.c_long)
		]

	librt = ctypes.CDLL('librt.so.1', use_errno=True)
	clock_gettime = librt.clock_gettime
	clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]

	def monotonic_time():
		"""
		Get monotonic refence time
		"""
		t = timespec()
		if clock_gettime(CLOCK_MONOTONIC_RAW , ctypes.pointer(t)) != 0:
			errno_ = ctypes.get_errno()
			raise OSError(errno_, os.strerror(errno_))
		return t

	#Flags
	FLAG_USE_BUSY = 0
	FLAG_READONLY = 0
	FLAG_VERBOSE = 1
	FLAG_LOG_FILE = 0
	read_interval = 7000 #12000 #(us)

	PACKET_TO_TRANSMIT	=0x00F0
	MY_TRANSMISSION		=0x00F2
	SUCCES_TRANSMISSION	=0x00F4
	OTHER_TRANSMISSION	=0x00F6
	BAD_RECEPTION		=0x00FA
	BUSY_SLOT           =0x00FC

	NEAR_SLOT	=	43
	COUNT_SLOT	=	43
	SINC_SLOT_2	=	40
	SINC_SLOT_1	=	41
	SINC_SLOT_0	=	42

	#define suit protocol structures to contain TDMA and ALOHA in order to store configuration  and emulate transmission
	# on channel
	#define structures to save channel slot measurement and decision
	class emulator_param(ctypes.Structure):
		_fields_= [
			('frame_offset', ctypes.c_int),
			('frame_length', ctypes.c_int),
			('slot_assignment', ctypes.c_int),
			('persistence', ctypes.c_float)
		]

	class fsm_param(ctypes.Structure):
		_fields_= [
			#Parameter number.
			('num', ctypes.c_int),
			#Parameter value.
			('value', ctypes.c_int)
			#Linked list.
			#struct fsm_param *next;
		]

	class protocol(ctypes.Structure) :
		_fields_ = [
			#Unique identifier
			('id', ctypes.c_int),
			#Readable name, such as "TDMA (slot 1)"
			('name', ctypes.c_char_p),
			#Path to the radio program
			('fsm_path', ctypes.c_char_p),
			#Parameters for the FSM
			('fsm_params', fsm_param * 2),
			#Protocol emulator for determining decisions of protocol locally
			#protocol_emulator emulator;
			('emulator', ctypes.c_char_p),
			#Parameter for protocol emulator
			#void *parameter;
			('parameter', emulator_param)
		]

	class metamac_slot(ctypes.Structure):
		_fields_ = [
			('slot_num', ctypes.c_ulong),
			('read_num', ctypes.c_ulong),
			('host_time', ctypes.c_uint64),
			('host_time', ctypes.c_uint64),
			('tsf_time', ctypes.c_uint64 ),
			('slot_index', ctypes.c_int),
			('slots_passed', ctypes.c_int),

			#Indicates if this slot was filled in because of a delay in	reading from the board.
			('filler', ctypes.c_ubyte), #	uchar filler : 1;
			#Indicates that a packet was waiting to be transmitted in this slot.
			('packet_queued', ctypes.c_ubyte), #uchar packet_queued : 1;
			#Indicates that a transmission was attempted in this slot.
			('transmitted', ctypes.c_ubyte), #uchar transmitted : 1;
			#Indicates that a transmission was successful in this slot.
			('transmit_success', ctypes.c_ubyte), #uchar transmit_success : 1;
			#Various measures for whether another node attempted to transmit.
			('transmit_other', ctypes.c_ubyte), #uchar transmit_other : 1;
			('bad_reception', ctypes.c_ubyte), #uchar bad_reception : 1;
			('busy_slot', ctypes.c_ubyte), #uchar busy_slot : 1;
			#Indicates that either a transmission attempt was unsuccessful
			#in this slot or another node attempted a transmission.
			('channel_busy', ctypes.c_ubyte) #uchar channel_busy : 1;
		]

	class protocol_suite(ctypes.Structure) :
		_fields_ = [
			#Total number of protocols
			('num_protocols', ctypes.c_int),
			#Index of best protocol. Initially -1.
			('active_protocol', ctypes.c_int),
			#Index of protocols in slots. -1 Indicated invalid
			('slots', ctypes.c_int * 2),
			#Which slot is active. 0 indicates neither are active.
			('active_slot', ctypes.c_int),
			#Offset of slots numbering from read loop to slot numbering for TDMA.
			('slot_offset', ctypes.c_int),
			#Array of all protocols.
			('protocols', protocol * 5),
			#Array of weights corresponding to protocols.
			('weights', ctypes.c_double * 5),	#weights;
			#Factor used in computing weights.
			('eta', ctypes.c_double),
			#Slot information for last to be emulated.
			('last_slot', metamac_slot),
			#Indicates whether protocols should be cycled.
			('cycle', ctypes.c_int),
		]

	SUCCESS = 0
	FAILURE = 2

	def tdma_emulate(param, slot_num, offset):
		"""
		This function emulate the tdma protocol
		"""
		slot_num += offset
		tdma_params = param
		#print('slot_num %d - tdma_params.frame_offset %d - tdma_params.frame_length %d - tdma_params.slot_assignment %d' \
		#	  % ( slot_num, tdma_params.frame_offset, tdma_params.frame_length, tdma_params.slot_assignment))

		if ((slot_num - tdma_params.frame_offset) % tdma_params.frame_length) == tdma_params.slot_assignment :
			result = 1.0
		else :
			result = 0.0

		return result


	def aloha_emulate(param, slot_num, offset):
		"""
		This function emulate the aloha protocol
		"""
		aloha_params = param
		return aloha_params.persistence


	def configure_params(slot, param):
		"""
		This function use UPI to configure radio program parameters
		"""
		UPIargs = { 'interface' : 'wlan0', UPI_R.TDMA_ALLOCATED_SLOT : param[1].value }
		rvalue = controller.radio.set_parameters(UPIargs)
		if rvalue[0] == SUCCESS:
			log.warning('Parameter writing successful')
		else :
			log.warning('Error in parameter writing')


	def load_protocol(suite, protocol):
		"""
		This function load a specific radio program according with the Meta-MAC decision
		"""
		active = suite.active_slot # Always 0 or 1 since metamac_init will already have run.
		inactive = 1 - active

		if (protocol == suite.slots[active]) :
			#This protocol is already running.
			pass

		elif (protocol < (suite.num_protocols - 1) and suite.slots[active] < (suite.num_protocols - 1)) :
			#The protocol loading is TDMA and the protocol running is TDMA but they use different slot
			#Protocol in active slot shares same radio program, but is not the same protocol
			#(already checked). Write the parameters for this protocol.
			configure_params(active, suite.protocols[protocol].fsm_params)
			suite.slots[active] = protocol
			#print('load protocol : change only tdma param')

		elif (protocol == suite.slots[inactive]):
			#Switch to other slot.
			if inactive == 0:
				position = '1'
			else:
				position = '2'

			UPIargs = {'position' : position, 'interface' : 'wlan0' }
			rvalue = controller.radio.activate_radio_program(UPIargs)
			if rvalue == SUCCESS:
				log.warning('Radio program activation successful')
			else :
				log.warning('Error in radio program activation')
			suite.active_slot = inactive
			suite.slots[suite.active_slot] = protocol
			#print('load protocol : change slot')

		elif (protocol < (suite.num_protocols - 1)):
			#Switch to other slot.
			if inactive == 0:
				position = '1'
			else:
				position = '2'

			UPIargs = {'position' : position, 'interface' : 'wlan0' }
			rvalue = controller.radio.activate_radio_program(UPIargs)
			if rvalue == SUCCESS:
				log.warning('Radio program activation successful')
			else :
				log.warning('Error in radio program activation')
			suite.active_slot = inactive

			configure_params(active, suite.protocols[protocol].fsm_params)
			suite.slots[suite.active_slot] = protocol
			#print('load protocol : change slot and TDMA param')

		else:
			#Load into inactive slot.
			log.warning('Error in protocol activation or switching')

		suite.active_protocol = protocol
		log.info('active protocol %d' % suite.active_protocol)
		suite.last_update = monotonic_time()


	def metamac_evaluate(suite):
		"""
		This funciotn identify the best protocol between the protocols in the Meta-MAC suite
		"""
		best = 0
		for i in range(suite.num_protocols):
			if (suite.weights[i] > suite.weights[best]) :
				best = i
		load_protocol(suite, best)

	def metamac_display(loop, suite):
		"""
		This funciton display in real time the weight of all the protocol
		"""
		for i in range(0, suite.num_protocols):
			active_string = ' '
			if suite.active_protocol == i:
				active_string = '*'

			#print("%c %5.3f %s\n" % (active_string, suite.weights[i], suite.protocols[i].name))
			if i == 0 :
				stdout.write("\r%c%5.3f%s--" % (active_string, suite.weights[i], suite.protocols[i].name))
			elif i == suite.num_protocols-1 :
				stdout.write("%c%5.3f%s\n" % (active_string, suite.weights[i], suite.protocols[i].name))
			else:
				stdout.write("%c%5.3f%s--" % (active_string, suite.weights[i], suite.protocols[i].name))
			stdout.flush()


	def queue_multipush(story_channel, story_file, story_channel_len, story_channel_len_diff):
		"""
		This function collect the measurements on queue, in order to keep their available for different process
		"""
		ai = story_channel_len - story_channel_len_diff
		while ai < story_channel_len :

			# print("%d - %d : %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d" %
			# ( ai, story_channel_len_diff, int(story_channel[ai].slot_num), int(story_channel[ai].read_num), int(story_channel[ai].host_time),
			# story_channel[ai].tsf_time, story_channel[ai].slot_index, story_channel[ai].slots_passed,
			# (story_channel[ai].filler), (story_channel[ai].packet_queued), (story_channel[ai].transmitted),
			# (story_channel[ai].transmit_success), (story_channel[ai].transmit_other),
			# (story_channel[ai].bad_reception), (story_channel[ai].busy_slot), (story_channel[ai].channel_busy) ))

			story_file.write("%d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d\n" %
			( int(story_channel[ai].slot_num), int(story_channel[ai].read_num), int(story_channel[ai].host_time),
			story_channel[ai].tsf_time, story_channel[ai].slot_index, story_channel[ai].slots_passed,
			(story_channel[ai].filler), (story_channel[ai].packet_queued), (story_channel[ai].transmitted),
			(story_channel[ai].transmit_success), (story_channel[ai].transmit_other),
			(story_channel[ai].bad_reception), (story_channel[ai].busy_slot), (story_channel[ai].channel_busy) ))

			ai += 1


	def acquire_slots_channel(story_channel):
		"""
		This function acquire the measurement about the channel slots
		"""
		reading_thread = threading.currentThread()
		slot_time = 2200 #(us)

		slot_num = 0
		read_num = 0
		slot_index = 0 #(int)
		last_slot_index = 0 #(int)
		tsf = 0 #(uint64_t)
		last_tsf = 0 #(uint64_t)
		initial_tsf = 0 #(uint64_t)

		start_time = monotonic_time() #(timespec)
		loop_end = 0 #(uint64_t)

		UPI_myargs = {'interface' : 'wlan0', 'measurements' : [UPI_R.TSF, UPI_R.COUNT_SLOT] }
		node_measures = controller.radio.get_measurements(UPI_myargs)

		initial_tsf = node_measures[0]
		tsf = initial_tsf
		slot_index = node_measures[1] & 0x7
		slot_num = (slot_index + 1) % 8

		# metamac control loop
		collect_period = 2 #ms
		report_period = 16 #ms
		num_iterations = 1

		while getattr(reading_thread, "do_run", True):

			current_time =  monotonic_time() #(timespec)
			loop_start = int((current_time.tv_sec - start_time.tv_sec) * 1000000 + (current_time.tv_nsec - start_time.tv_nsec) / 1000) #(uint64_t )
			last_tsf = tsf
			last_slot_index = slot_index

			#call UPI to get channel slots measurements
			UPI_myargs = {'interface' : 'wlan0', 'measurements' : [UPI_R.TSF, UPI_R.COUNT_SLOT, UPI_R.PACKET_TO_TRANSMIT, UPI_R.MY_TRANSMISSION, UPI_R.SUCCES_TRANSMISSION, UPI_R.OTHER_TRANSMISSION, UPI_R.BAD_RECEPTION , UPI_R.BUSY_SLOT, UPI_R.COUNT_SLOT] }
			node_measures = controller.radio.get_measurements_periodic(UPI_myargs, collect_period, report_period, num_iterations, None )

			tsf =node_measures[0]
			slot_index = node_measures[1]& 0x7
			packet_queued = node_measures[2]
			transmitted = node_measures[3]
			transmit_success = node_measures[4]
			transmit_other = node_measures[5]
			bad_reception = node_measures[6]
			busy_slot = node_measures[7]
			end_slot_index = node_measures[8] & 0x7

			channel_busy = 0 #(uint)
			if (FLAG_USE_BUSY) :
				channel_busy = (transmitted & ~transmit_success) |((transmit_other | bad_reception | busy_slot) & ~(transmitted & transmit_success))
			else:
				channel_busy = (transmitted & ~transmit_success) |((transmit_other | bad_reception) & ~(transmitted & transmit_success))

			slots_passed = slot_index - last_slot_index #(int)
			if slots_passed < 0:
				slots_passed = slots_passed + 8

			actual = tsf - last_tsf #int64_t actual = ((int64_t)tsf) - ((int64_t)last_tsf);
			#print(" read %d - last_tsf %d - tsf %d - diff %d: %x, %x, %x, %x, %x, %x, %x" % (read_num, last_tsf, tsf, actual, packet_queued, transmitted, transmit_success, transmit_other, bad_reception, busy_slot, end_slot_index))
			slot_offset = slots_passed #(int)
			slots = [ metamac_slot() for i in range(8)] #(struct metamac_slot) |!!! warning for memory leak
			ai = 0
			#we need extract single slot informaiton from UPI call result, each call report 8 slots information
			while slot_offset > 0 :
				slot_offset-=1
				si = slot_index - slot_offset #(int)
				if  si < 0 :
					si = si + 8

				slot_num+=1
				slots[ai].slot_num = slot_num
				slots[ai].read_num = read_num
				slots[ai].host_time = loop_start
				slots[ai].tsf_time = tsf
				slots[ai].slot_index = slot_index
				slots[ai].slots_passed = slots_passed
				slots[ai].filler = 0
				slots[ai].packet_queued = (packet_queued >> si) & 1
				slots[ai].transmitted = (transmitted >> si) & 1
				slots[ai].transmit_success = (transmit_success >> si) & 1
				slots[ai].transmit_other = (transmit_other >> si) & 1
				slots[ai].bad_reception = (bad_reception >> si) & 1
				slots[ai].busy_slot = (busy_slot >> si) & 1
				slots[ai].channel_busy = (channel_busy >> si) & 1
				ai+=1

			#save slot information in list
			for i in range(ai):
				story_channel.append(slots[i])

			#debug
			# for i in range(ai):
			# 	print("%d, %d, %d, " %   ( int(story_channel[i].slot_num), int(story_channel[i].read_num), int(story_channel[i].host_time) ))

			current_time =  monotonic_time() #(timespec)
			loop_end = int((current_time.tv_sec - start_time.tv_sec) * 1000000 + (current_time.tv_nsec - start_time.tv_nsec) / 1000)
			delay = (loop_start + read_interval - loop_end) #(int64_t) #delay = ((int64_t)loop_start) + read_interval - ((int64_t)loop_end) #(int64_t)
			#print("ai %d - loop_start %d - loop_end %d - diff %d - delay %d - story_channel_len %d" % (ai, loop_start, loop_end, loop_end-loop_start, delay, len(story_channel) ))

			# we cant make dalay minor of ~7ms, processing limit
			if (delay > 0):
				libc.usleep(int(delay))

			read_num+=1



	def update_weights(suite, current_slot, ai):
		"""
		This funtion performs the computation for emulating the suite of protocols for a single slot,
		and adjusting the weights.
		"""
		# print("%d - %d : %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d" %
		# 	( ai, story_channel_len_diff, int(story_channel[ai].slot_num), int(story_channel[ai].read_num), int(story_channel[ai].host_time),
		# 	story_channel[ai].tsf_time, story_channel[ai].slot_index, story_channel[ai].slots_passed,
		# 	(story_channel[ai].filler), (story_channel[ai].packet_queued), (story_channel[ai].transmitted),
		# 	(story_channel[ai].transmit_success), (story_channel[ai].transmit_other),
		# 	(story_channel[ai].bad_reception), (story_channel[ai].busy_slot), (story_channel[ai].channel_busy) ))

		if (suite.protocols[suite.active_protocol].emulator == b'tdma' and current_slot.transmitted):
			#Update slot_offset
			params = suite.protocols[suite.active_protocol].parameter
			neg_offset = (current_slot.slot_num - params.frame_offset - params.slot_assignment) % params.frame_length
			suite.slot_offset = (params.frame_length - neg_offset) % params.frame_length

		z = 0.0
		uu = 0.0
		d = 0.0

		#If there is no packet queued for this slot, consider all protocols to be correct
		#and thus the weights will not change
		if (current_slot.packet_queued) :
			#z represents the correct decision for this slot - transmit if the channel
			#is idle (1.0) or defer if it is busy (0.0)

			if (suite.protocols[suite.active_protocol].emulator == b'tdma') :
				if (not current_slot.channel_busy):
					z = 1.0

			if (suite.protocols[suite.active_protocol].emulator == b'aloha'):
				# // transmission AND success: GOOD
				# // no trasmission AND slot busy - GOOD
				# // trasmission AND NOT success - WRONG
				# // trasmission  AND slot empty - WRONG
				# //if GOOD
				# //	z = p_current
				# //else
				# //	z = 1 - p_current

				p_curr = suite.protocols[suite.active_protocol].parameter.persistence
				if (not current_slot.channel_busy):
					z = p_curr
				else :
					z = 1-p_curr

			#evaluate protocols weights
			for p in range(suite.num_protocols) :
				# d is the decision of this component protocol - between 0 and 1
				if (suite.protocols[p].emulator == b'tdma') :
					d = tdma_emulate(suite.protocols[p].parameter, current_slot.slot_num, suite.slot_offset)
				else :
					d = aloha_emulate(suite.protocols[p].parameter, current_slot.slot_num, suite.slot_offset)

				#weight evaluate
				exponent = suite.eta * math.fabs(d - z)
				suite.weights[p] *= math.exp(-exponent)

				if suite.weights[p]<0.01:
					suite.weights[p]=0.01

			# Normalize the weights
			s = 0
			for p in range(suite.num_protocols):
				s += suite.weights[p]
			for p in range(suite.num_protocols):
				suite.weights[p] /= s

			# for p in range(suite.num_protocols):
			# 	stdout.write("%5.3f\n" % (suite.weights[p]))

		suite.last_slot = current_slot

	#socket iperf pointer
	iperf_socket = None

	def rcv_from_iperf_socket(iperf_througputh):
		"""
		This function collects the throughput information result
		"""
		iperf_thread = threading.currentThread()
		print('start socket iperf')
		iperf_port = "8301"
		iperf_server_ip_address = "10.8.8.102"
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

	suite = protocol_suite()
	num_protocols = 5
	eta = 0.5
	protocols = [protocol() for i in range(num_protocols)]

	#eta = float(arg)
	log.info('eta = %f' % eta)

	#setting TDMA 1 protocol
	protocols[0].id = 1
	protocols[0].name =b'TDMA  (slot 0)'
	protocols[0].fsm_path = b'tdma-4.txt'
	protocols[0].fsm_params[0].num = 12
	protocols[0].fsm_params[0].value = 4
	protocols[0].fsm_params[1].num = 11
	protocols[0].fsm_params[1].value = 0
	protocols[0].emulator = b'tdma'
	protocols[0].parameter.frame_offset = 0
	protocols[0].parameter.frame_length = 4
	protocols[0].parameter.slot_assignment = 0

	#setting TDMA 2 protocol
	protocols[1].id = 2
	protocols[1].name = b'TDMA  (slot 1)'
	protocols[1].fsm_path = b'tdma-4.txt'
	protocols[1].fsm_params[0].num = 12
	protocols[1].fsm_params[0].value = 4
	protocols[1].fsm_params[1].num = 11
	protocols[1].fsm_params[1].value = 1
	protocols[1].emulator = b'tdma'
	protocols[1].parameter.frame_offset = 0
	protocols[1].parameter.frame_length = 4
	protocols[1].parameter.slot_assignment = 1

	#setting TDMA 3 protocol
	protocols[2].id = 3
	protocols[2].name = b'TDMA  (slot 2)'
	protocols[2].fsm_path = b'tdma-4.txt'
	protocols[2].fsm_params[0].num = 12
	protocols[2].fsm_params[0].value = 4
	protocols[2].fsm_params[1].num = 11
	protocols[2].fsm_params[1].value = 2
	protocols[2].emulator = b'tdma'
	protocols[2].parameter.frame_offset = 0
	protocols[2].parameter.frame_length = 4
	protocols[2].parameter.slot_assignment = 2

	#setting TDMA 4 protocol
	protocols[3].id = 4
	protocols[3].name = b'TDMA  (slot 3)'
	protocols[3].fsm_path = b'tdma-4.txt'
	protocols[3].fsm_params[0].num = 12
	protocols[3].fsm_params[0].value = 4
	protocols[3].fsm_params[1].num = 11
	protocols[3].fsm_params[1].value = 3
	protocols[3].emulator = b'tdma'
	protocols[3].parameter.frame_offset = 0
	protocols[3].parameter.frame_length = 4
	protocols[3].parameter.slot_assignment = 3

	#setting ALOHA protocol
	protocols[4].id = 5
	protocols[4].name = b'Aloha (p=0.9)'
	protocols[4].fsm_path = b'aloha-slot-probability-always.txt'
	protocols[4].fsm_params[0].num = 14
	protocols[4].fsm_params[0].value = 6553
	protocols[4].emulator = b'aloha'
	protocols[4].parameter.persistence = 0.9


	#protocols suite INIT VALUES
	suite.num_protocols = num_protocols

	#number of current active slot
	suite.active_slot = 0
	#number of current active protocol from protocol structure
	suite.active_protocol = 4
	#number of protocol present in the specified slot
	suite.slots[0] = 4
	suite.slots[1] = 0

	suite.slot_offset = 0

	#TDMA 1
	suite.protocols[0] = protocols[0]
	#TDMA 2
	suite.protocols[1] = protocols[1]
	#TDMA 3
	suite.protocols[2] = protocols[2]
	#TDMA 4
	suite.protocols[3] = protocols[3]
	#ALOHA
	suite.protocols[4] = protocols[4]

	for p in range(num_protocols) :
		suite.weights[p] = 1.0 / num_protocols

	suite.eta = eta
	suite.last_slot.slot_num = -1
	suite.last_slot.packet_queued = 0
	suite.last_slot.transmitted = 0
	suite.last_slot.channel_busy = 0
	suite.cycle = 0

	interface = 'wlan0'
	wlan_ip_address = controller.net.get_iface_ip_addr(interface)
	wlan_ip_address = wlan_ip_address[0]

	story_channel = []
	reading_thread = threading.Thread(target=acquire_slots_channel, args=(story_channel,))
	reading_thread.start()

	iperf_througputh = []
	iperf_througputh.append(0.0)
	iperf_thread = threading.Thread(target=rcv_from_iperf_socket, args=(iperf_througputh,))
	iperf_thread.start()

	time.sleep(2)

	story_file = open("story.csv", "w")
	story_file.write("slot_num, read_num, host_time, tsf_time, slot_index, slots_passed, \
	 filler, packet_queued, transmitted, transmit_success, transmit_other, \
	 bad_reception, busy_slot, channel_busy \n")

	story_channel_len = 0

	last_update_time = monotonic_time()
	loop = 0

	print("Local ctrl program started: {}".format(controller.name))
	# metamac control loop
	while not controller.is_stopped():
		msg = controller.recv(timeout=1)
		if msg:
			print("Receive message %s" % str(msg))
			if msg.get('protocol'):
				protocol = msg['protocol']
				print("in %s" % str(protocol))
				if protocol == 'TDMA 1':
					load_protocol(suite, 0)
					FLAG_READONLY = 1
				if protocol == 'TDMA 2':
					load_protocol(suite, 1)
					FLAG_READONLY = 1
				if protocol == 'TDMA 3':
					load_protocol(suite, 2)
					FLAG_READONLY = 1
				if protocol == 'TDMA 4':
					load_protocol(suite, 3)
					FLAG_READONLY = 1
				if protocol == 'ALOHA':
					load_protocol(suite, 4)
					FLAG_READONLY = 1
				if protocol == 'METAMAC':
					FLAG_READONLY = 0

		if( (len(story_channel) - story_channel_len) > 60):
			story_channel_len_old = len(story_channel)-60
		else:
			story_channel_len_old = story_channel_len

		story_channel_len = len(story_channel)
		story_channel_len_diff = story_channel_len - story_channel_len_old
		#print('\n\nstory_channel len %d - diff %d - last slot num %d' % (story_channel_len, story_channel_len_diff, story_channel[story_channel_len-1].slot_num))

		#store channel evolution on file
		if story_channel_len_diff > 0 :

			if FLAG_LOG_FILE:
				queue_multipush(story_channel, story_file, story_channel_len, story_channel_len_diff)

			for i in range((story_channel_len - story_channel_len_diff), story_channel_len ):
				#print('\n\n i %d -story_channel len %d - diff %d - last slot num %d' % (i, story_channel_len, story_channel_len_diff, story_channel[story_channel_len-1].slot_num))
				update_weights(suite, story_channel[i], i)

		#Update running protocol
		if (not FLAG_READONLY):
			metamac_evaluate(suite)

		#Print protocols weights
		if FLAG_VERBOSE :
			current_time =  monotonic_time() #(timespec)
			timediff = (current_time.tv_sec - last_update_time.tv_sec) * 1000000 + (current_time.tv_nsec - last_update_time.tv_nsec) / 1000
			# Update display every 1 second
			if (timediff > 1000000) :
				metamac_display(loop, suite)
				loop+=1
				last_update_time = current_time

		#Send information to global controller
		# TIME (seconds) - ACTIVE_PROTOCOL - THR_STATION
		current_time =  monotonic_time() #(timespec)
		controller.send_upstream({ "measure" : [[current_time.tv_sec, suite.active_protocol, iperf_througputh[0]]], "wlan_ip_address" : (wlan_ip_address) })


	print("Local ctrl program stopping: {}".format(controller.name))
	story_file.close()
	reading_thread.do_run = False
	reading_thread.join()
	iperf_thread.do_run = False
	iperf_thread.join()
	time.sleep(2)


