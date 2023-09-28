#!/usr/bin/python
import socket
import random
import json
import sys, getopt
import select
import signal
import array
import time
import subprocess
do_run = True

def signal_handler(signal, frame):
	global do_run
	print('You pressed Ctrl+C!')
	do_run = False

signal.signal(signal.SIGINT, signal_handler)


def printHelp():
	print('set_lte_tx_pattern.py -w <tx_pattern>')
	print("<tx_pattern> must have the following structure xxxxxxxxxx (x is 0 or 1)")
	print("<tx_pattern> e.g. 1010101010")


def set_pattern():
	global do_run

	tx_pattern = "1,1,1,1,1,1,1,1,1,1"
	# lte_pattern_base = [1, 1, 0, 0, 0, 1, 0, 0, 0, 0]
	# lte_pattern_base_array = array.array('B', lte_pattern_base)

	lte_pattern_base = [1, 1, 0, 0, 1, 1, 1, 1, 1, 1]
	# lte_pattern_base = [1, 1, 0, 0, 0, 1, 0, 0, 0, 0]
	lte_pattern_base_array = array.array('B', lte_pattern_base)

	# # option_pattern = arg
	# if len(option_pattern) == 10:
	# 	if option_pattern[0] == '1' or option_pattern[0] == '0':
	# 		tx_pattern = option_pattern[0]
	# 	else:
	# 		print("option must have the following structure xxxxxxxxxx (x is 0 or 1)")
	# 		print("-------------------------------------------------------------------")
	# 		printHelp()
	# 		sys.exit()
	#
	# 	for ii in range(0, 10):
	# 		if option_pattern[ii] == '1' or option_pattern[ii] == '0':
	# 			tx_pattern = tx_pattern + ',' + option_pattern[ii]
	# 		else:
	# 			print("option must have the following structure xxxxxxxxxx (x is 0 or 1)")
	# 			print("-------------------------------------------------------------------")
	# 			# printHelp()
	# 			sys.exit()
	# 	else:
	# 		print("option is required")
	# 		print("-------------------------------------------------------------------")
	# 		printHelp()
	# 		sys.exit()

	# UDP_IP = "127.0.0.1"
	# UDP_PORT = 8888
	# ue_id = '1'
	# snr=random.randint(-100,0)
	# bler=random.randint(0,100)
	# mjson={'ue_id':ue_id,'snr':snr,'bler':bler}

	UDP_IP = "10.8.9.13"
	UDP_PORT = 8888
	print("UDP target IP: ", UDP_IP)
	print("UDP target port: ", UDP_PORT)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	throughput = None
	multicast_traffic = False
	time_duration = 6000
	bandwidth = 800
	frame_length = 600
	sshprocess = []

	# for jj in range(10, 3, -1):
	for jj in range(3, 10, 1):
		if jj > 3:
			if jj == 5:
				continue
			else:
				lte_pattern_base_array[jj] = 0
				# lte_pattern_base_array[jj] = 1

		if lte_pattern_base_array[0] == 1:
			tx_pattern = '1'
		else:
			tx_pattern = '0'
		for ii in range(1, 10):
			if lte_pattern_base_array[ii] == 1:
				tx_pattern = tx_pattern + ',' + '1'
			else:
				tx_pattern = tx_pattern + ',' + '0'

		print("tx_pattern: ", tx_pattern)
		sock.sendto(tx_pattern.encode(), (UDP_IP, UDP_PORT))

		HOST = "root@10.8.8.114"
		cmd = ["ssh", HOST]
		cmd += ['/usr/bin/iperf', '-c', '192.168.0.2', '-p', '1234']
		if time_duration:
			cmd += ['-t', str(time_duration)]
		if bandwidth:
			cmd += ['-b', str(bandwidth)+'K']
			bandwidth = 400
		if frame_length:
			cmd += ['-l', str(frame_length)]

		# process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
		# lines_iterator = iter(process.stdout.readline, b"")
		# for line in lines_iterator:
		# 	throughput = self.helper_parseIperf(line)
		# 	if throughput:
		# 		break

		print("before command")

		sshprocess.append(subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE))

		print("after command")
		time.sleep(10)

		if not do_run:
			break


	for kk in range(len(sshprocess)):
		sshprocess[kk].kill()

	print("kill iperf process")

	HOST = "root@10.8.8.114"
	cmd_ssh = ["ssh", HOST]
	cmd_str = cmd_ssh + ['killall', '-9', 'iperf']
	killprocess = subprocess.Popen(cmd_str, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	time.sleep(2)
	killprocess.kill()

	# cmd_output = cmd_output.decode('ascii')
	# if cmd_output:
	# 	flow_info_lines = cmd_output.rstrip().split('\n')
	# 	for ii in range(0, len(flow_info_lines)):
	# 		cmd_str = cmd_ssh + ['kill -9 ' + str(flow_info_lines[ii])]
	# 		cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)

	print("iperf process killed")

	sock.close()
	return


def main(argv):
	"""
	This function collects the reading buffer information
	"""
	global do_run

	try:
		opts, args = getopt.getopt(argv, "hiw:", ["tx_pattern="])
	except getopt.GetoptError:
		printHelp()
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			printHelp()
			sys.exit()
		elif opt in ("-w", "--tx_pattern"):
			option_pattern = arg
			if len(option_pattern) == 10:
				if option_pattern[0] == '1' or option_pattern[0] == '0':
					tx_pattern = option_pattern[0]
				else:
					print("option must have the following structure xxxxxxxxxx (x is 0 or 1)")
					print("-------------------------------------------------------------------")
					printHelp()
					sys.exit()

				for ii in range(1, 10):
					if option_pattern[ii] == '1' or option_pattern[ii] == '0':
						tx_pattern = tx_pattern + ',' + option_pattern[ii]
					else:
						print("option must have the following structure xxxxxxxxxx (x is 0 or 1)")
						print("-------------------------------------------------------------------")
						printHelp()
						sys.exit()
			else:
				print("option must been 10 length characters")
				print("-------------------------------------------------------------------")
				printHelp()
				sys.exit()
		else:
			# print("option is required")
			print("-------------------------------------------------------------------")
			# printHelp()
			# sys.exit()


	# print('start socket reading_program')
	# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# timeout = 1
	# sock.setblocking(0)
	# # sock.bind(("127.0.0.1", 10001))
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

	#******************
	#receive statistics
	#******************
	# while (do_run):
	# 	# {'UE_ID': 0, 'type': 'ue0_stats', 'CFO': -0.624144, 'SNR': 21.99383, 'PDCCH-Miss': 39.999996, 'PDSCH-BLER': 21.0, 'timestamp': 1524493482.429576}
	# 	# {'UE_ID': 0, 'type': 'ue0_stats', 'CFO': -0.442906, 'SNR': 17.325897, 'PDCCH-Miss': 39.999996, 'PDSCH-BLER': 21.1, 'timestamp': 1524493483.429576}
	# 	# {'UE_ID': 0, 'type': 'ue0_stats', 'CFO': -0.698449, 'SNR': 29.657462, 'PDCCH-Miss': 39.999996, 'PDSCH-BLER': 20.5, 'timestamp': 1524493484.429552}
	# 	try:
	# 		ready = select.select([sock], [], [], timeout)
	# 		if ready[0]:
	# 			data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
	# 			stats = json.loads(data.decode('utf-8'))
	# 			print(stats)
	# 			# if "PDCCH-Miss" in stats:
	# 			# 	reading_buffer[0] = (1 - (stats["PDCCH-Miss"] / 100))
	# 	except Exception as e:
	# 		print(e)
	#
	# sock.close()
	# print("stop socket reading_program")


	set_pattern()
	return

# python3 set_tx_lte_pattern.py -w 1100010000
if __name__ == "__main__":
	main(sys.argv[1:])
