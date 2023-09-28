#!/usr/bin/python
import subprocess
import pygame
import time
import sys
import re
import sys
import zmq
import os
import csv
import numpy
import json
from socket import *    # import *, but we'll avoid name conflict
from sys import argv
from thread import start_new_thread

HELP_MSG	= sys.argv[0]+" --address <IP> [--interval <X.Y>] [--max-ping <X>] [--history <X>] [--window-height <X>] [--window-width <X>] [--fullscreen] [--ping-threshold <X>]"

CLOCK_DELTA	= 0.1 #0.02 # Minimal refresh rate
MAX_SCALE_VALUE	= 150.0 # The visualization will automatically scale to display 0 ping on top and MAX_SCALE_VALUE ping at the bottom

MAX_DRAW_LINE = 10
MAX_STA1_CONFIGURATION = MAX_DRAW_LINE
MAX_STA2_CONFIGURATION = MAX_DRAW_LINE
MAX_STA3_CONFIGURATION = MAX_DRAW_LINE
MAX_STA4_CONFIGURATION = MAX_DRAW_LINE

MAX_DRAW_LINE = 25000
MAX_STA1_THR = MAX_DRAW_LINE
MAX_STA2_THR = MAX_DRAW_LINE
MAX_STA3_THR = MAX_DRAW_LINE
MAX_STA4_THR = MAX_DRAW_LINE

MAX_DRAW_LINE = 80
DRAW_LINE_ZOOM = 2
MAX_STA1_PWR = MAX_DRAW_LINE
MAX_STA2_PWR = MAX_DRAW_LINE
MAX_STA3_PWR = MAX_DRAW_LINE
MAX_STA4_PWR = MAX_DRAW_LINE


HISTORY_SIZE	= 1200.0 # Number of history values to display
COORD_MULT	= {"X": 1, "Y": 1} # Coord scaler, automatically determined based on window size, MAX_SCALE_VALUE and HISTORY_SIZE
RESOLUTION	= (1560, 450) # Default window size
#RESOLUTION	= (1024, 800) # Default window size
#RESOLUTION	= (1920, 500) # Default window size
STA1_CONFIGURATION = []
STA2_CONFIGURATION = []
STA3_CONFIGURATION = []
STA4_CONFIGURATION = []
STA1_THR = []
STA2_THR = []
STA3_THR = []
STA4_THR = []
STA1_PWR = []
STA2_PWR = []
STA3_PWR = []
STA4_PWR = []


RX_MATCH_LINE	= []
HISTORY		= []
SWITCH 		= []
PLOSS 		= []

TEXT_COLOR	= (180, 180, 180) # Infotext color
RED_COLOR	= (255, 0, 0)
YELLOW_COLOR	= (255, 255, 0)
#BLUE_COLOR	= (0, 0, 255)
BLUE_COLOR	= (146, 146, 146)
WITHE_COLOR = (255, 255, 255)
GRID_COLOR = (100, 100, 100)


#TABLE node informations
# ip_adderss, name, THR, configuration, power
stations_dump = [["10.11.16.126", "apuT1", 25.0, 1.0, 70.0, 1, 1 ,1, 1],
                ["10.11.16.130", "apuU1", 25.0, 1.0, 70.0, 1, 1 ,1, 1],
                ["10.11.16.108", "apuO4", 25.0, 1.0, 70.0, 1, 1 ,1, 1],
                ["10.11.16.112", "node4", 25.0, 1.0, 70.0, 1, 1 ,1, 1]]

node_measurements = []

#num_active_traffic = 0
#old_num_active_traffic = 0

def getNextArg():
	getNextArg.n = getNextArg.n + 1
	return sys.argv[getNextArg.n]
getNextArg.n = 0

def parseArgs():
	global HELP_MSG
	global ZMQ_PORT
	global MAX_SCALE_VALUE
	global CLOCK_DELTA
	global HISTORY_SIZE
	global RESOLUTION

	try:
		while (True):
			a = getNextArg()
			if   ((a == "--help") or (a == "-h")):
				print HELP_MSG
				exit()
			elif (a == "--port"):
				ZMQ_PORT = getNextArg()
			elif (a == "--max-scale-value"):
				MAX_SCALE_VALUE = float(getNextArg())
			elif (a == "--interval"):
				CLOCK_DELTA = float(getNextArg())
			elif (a == "--history"):
				HISTORY_SIZE = float(getNextArg())
			elif (a == "--fullscreen"):
				RESOLUTION = (0, 0)
			elif (a == "--window-width"):
				RESOLUTION = (int(getNextArg()), RESOLUTION[1])
			elif (a == "--window-height"):
				RESOLUTION = (RESOLUTION[0], int(getNextArg()))
	except IndexError:
		pass

def normalizePoints(p):
	i = 0
	ret = []
	for point in p:
		ret.append((i*COORD_MULT["X"], point*COORD_MULT["Y"]))
		i = i+1
	return ret

def save_measurements(node_wlan_ip_address, node_measurements, directory):
		""" Uses matplotlib library to plot all the measurements stored in WiFiNode object.
            The measurements are stored in the last_bunch_measurement attribute of WiFiNode class.

        """
		out_measure={}
		print("node : %s - measurements : %s" % (str(node_wlan_ip_address), node_measurements))

		file_path = directory + '/measure.json'
		#save experiments log
		with open(file_path, 'w') as outfile:
			out_measure.update({node_wlan_ip_address : node_measurements})
			json.dump(out_measure, outfile)

		return

def main():
	global CLOCK_DELTA
	global HISTORY_SIZE
	global HISTORY
	global STA1_CONFIGURATION
	global STA2_CONFIGURATION
	global STA3_CONFIGURATION
	global STA4_CONFIGURATION
	global STA1_THR
	global STA2_THR
	global STA3_THR
	global STA4_THR
	global STA1_PWR
	global STA2_PWR
	global STA3_PWR
	global STA4_PWR
	global MAX_SCALE_VALUE
	global RESOLUTION
	global COORD_MULT
	global HELP_MSG

	#if (len(sys.argv) < 2):
	#	print HELP_MSG
	#	exit()

	parseArgs()

	CLOCK = -10.0
	OFFSET = 0
	OFFSET_LINE = 0

	pygame.init()
	pygame.display.set_caption("WISHFUL SHOWCASE 3")
	if (RESOLUTION == (0, 0)):
		screen = pygame.display.set_mode(RESOLUTION, pygame.FULLSCREEN)
	else:
		screen = pygame.display.set_mode(RESOLUTION)

	font = pygame.font.SysFont("monospace", 17)
	font2 = pygame.font.SysFont("monospace", 18)
	font1 = pygame.font.SysFont("monospace", 18)

	screen.blit(font.render("LOADING", True, (255, 255, 255)), (10, 10))
	pygame.display.update()

	#cnit image
	myimage1 = pygame.image.load("CNIT.GIF")
	imagerect1 = myimage1.get_rect()
	imagerect1.x = imagerect1.x + screen.get_width()-400
	imagerect1.y = imagerect1.y + screen.get_height()-150

	COORD_MULT["X"] = screen.get_width() / HISTORY_SIZE
	COORD_MULT["Y"] = screen.get_height() / MAX_SCALE_VALUE

	std_cumulative_tx_frame_interval_start = 0
	std_cumulative_tx_frame = 0

	NUM_CONFIGURATION = 9

	#for x in range(HISTORY_SIZE):
	#	SWITCH.append()

	while True:

		for e in pygame.event.get():
			if (e.type == pygame.QUIT):
				pygame.quit()
				exit()
			if (e.type == pygame.KEYDOWN):
				if ((e.key == pygame.K_q) or (e.key == 113)):
					pygame.quit()
					print('exit control key')
					save_measurements('192.168.3.140', node_measurements, './')
					exit()

		if (time.clock() > (CLOCK + CLOCK_DELTA)):
			CLOCK = time.clock()
			if (len(STA1_CONFIGURATION) >= HISTORY_SIZE):
				STA1_CONFIGURATION.pop(0)
				STA2_CONFIGURATION.pop(0)
				STA3_CONFIGURATION.pop(0)
				STA4_CONFIGURATION.pop(0)
				STA1_THR.pop(0)
				STA2_THR.pop(0)
				STA3_THR.pop(0)
				STA4_THR.pop(0)
				STA1_PWR.pop(0)
				STA2_PWR.pop(0)
				STA3_PWR.pop(0)
				STA4_PWR.pop(0)

			STA1_CONFIGURATION.append( MAX_SCALE_VALUE - (( stations_dump[0][3]/MAX_STA1_CONFIGURATION)*MAX_SCALE_VALUE ) )
			STA2_CONFIGURATION.append( MAX_SCALE_VALUE - (( stations_dump[1][3]/MAX_STA2_CONFIGURATION)*MAX_SCALE_VALUE ) )
			STA3_CONFIGURATION.append( MAX_SCALE_VALUE - (( stations_dump[2][3]/MAX_STA3_CONFIGURATION)*MAX_SCALE_VALUE ) )
			STA4_CONFIGURATION.append( MAX_SCALE_VALUE - (( stations_dump[3][3]/MAX_STA4_CONFIGURATION)*MAX_SCALE_VALUE ) )

			STA1_THR.append( MAX_SCALE_VALUE - 1 + OFFSET_LINE - (( stations_dump[0][2]/MAX_STA1_THR)*MAX_SCALE_VALUE ) )
			STA2_THR.append( MAX_SCALE_VALUE - 2 + OFFSET_LINE - (( stations_dump[1][2]/MAX_STA2_THR)*MAX_SCALE_VALUE ) )
			STA3_THR.append( MAX_SCALE_VALUE + 1 + OFFSET_LINE - (( stations_dump[2][2]/MAX_STA3_THR)*MAX_SCALE_VALUE ) )
			STA4_THR.append( MAX_SCALE_VALUE + 2 + OFFSET_LINE - (( stations_dump[3][2]/MAX_STA4_THR)*MAX_SCALE_VALUE ) )

			# STA1_PWR.append( MAX_SCALE_VALUE - 1 + OFFSET_LINE - (( stations_dump[0][4]/MAX_STA1_PWR)*MAX_SCALE_VALUE ) )
			# STA2_PWR.append( MAX_SCALE_VALUE - 2 + OFFSET_LINE - (( stations_dump[1][4]/MAX_STA2_PWR)*MAX_SCALE_VALUE ) )
			# STA3_PWR.append( MAX_SCALE_VALUE + 1 + OFFSET_LINE - (( stations_dump[2][4]/MAX_STA3_PWR)*MAX_SCALE_VALUE ) )
			# STA4_PWR.append( MAX_SCALE_VALUE + 2 + OFFSET_LINE - (( stations_dump[3][4]/MAX_STA4_PWR)*MAX_SCALE_VALUE ) )

			if stations_dump[0][4] > 60:
				STA1_PWR_CURRENT = (stations_dump[0][4] - 60)*4
			else:
				STA1_PWR_CURRENT = 0
			if stations_dump[1][4] > 60:
				STA2_PWR_CURRENT = (stations_dump[1][4] - 60)*4
			else:
				STA2_PWR_CURRENT = 0
			if stations_dump[2][4] > 60:
				STA3_PWR_CURRENT = (stations_dump[2][4] - 60)*4
			else:
				STA3_PWR_CURRENT = 0
			if stations_dump[3][4] > 60:
				STA4_PWR_CURRENT = (stations_dump[3][4] - 60)*4
			else:
				STA4_PWR_CURRENT = 0
			STA1_PWR.append( (( STA1_PWR_CURRENT/MAX_STA1_PWR)*MAX_SCALE_VALUE ) )
			STA2_PWR.append( (( STA2_PWR_CURRENT/MAX_STA2_PWR)*MAX_SCALE_VALUE ) )
			STA3_PWR.append( (( STA3_PWR_CURRENT/MAX_STA3_PWR)*MAX_SCALE_VALUE ) )
			STA4_PWR.append( (( STA4_PWR_CURRENT/MAX_STA4_PWR)*MAX_SCALE_VALUE ) )

			#add received measurements to the node measurements list
			node_measurements.append([[CLOCK, stations_dump[2][3], stations_dump[0][2], (stations_dump[0][4]*-1)]])


			if (len(STA1_CONFIGURATION) > 1):

				#set background color
				#screen.fill((78, 74, 76))
				screen.fill((63, 39, 96))

				#screen.blit(font.render("MULT_X: "+str(COORD_MULT["X"])+", MULT_Y: "+str(COORD_MULT["Y"]), 1, TEXT_COLOR), (5, screen.get_height()-20))
				screen.blit(font.render("Clock: "+str(CLOCK), 1, TEXT_COLOR), (5, screen.get_height()-20))
				#screen.blit(font.render("History size: "+str(HISTORY_SIZE), 1, TEXT_COLOR), (5, screen.get_height()-60))

				# screen.blit(font.render("CONFIGURATION station 1 : " + str(stations_dump[0][3]), 1, RED_COLOR), (800, screen.get_height()-20))
				# screen.blit(font.render("CONFIGURATION station 2 : " + str(stations_dump[1][3]) + "", 1, YELLOW_COLOR), (800, screen.get_height()-40))
                #
				screen.blit(font.render("RAS CONF : " + str(stations_dump[2][3]) + "", 1, WITHE_COLOR), (400, screen.get_height()-20))
				# screen.blit(font.render("CONFIGURATION station 4 : " + str(stations_dump[3][3]) + "", 1, BLUE_COLOR), (400, screen.get_height()-40))
				screen.blit(font.render("STATION THR : " + str(stations_dump[0][2]) + "Kbps", 1, RED_COLOR), (600, screen.get_height()-20))
				screen.blit(font.render("STATION PWR : -" + str(stations_dump[0][4]) + "dBm", 1, YELLOW_COLOR), (900, screen.get_height()-20))


				#PRINT IMAGES
				screen.blit(myimage1, imagerect1)

				#screen.blit(font1.render("RAS CONFIGURATION " + str(MAX_STA1_CONFIGURATION  - (MAX_STA1_CONFIGURATION/(NUM_CONFIGURATION+1)) ) , 1, WITHE_COLOR), (screen.get_width() - 400, screen.get_height()/(NUM_CONFIGURATION+1)-20+OFFSET))
				#pygame.draw.line(screen, GRID_COLOR, (5, (screen.get_height()/(NUM_CONFIGURATION+1))+OFFSET), (screen.get_width()-(NUM_CONFIGURATION+1), (screen.get_height()/(NUM_CONFIGURATION+1))+OFFSET))

				screen.blit(font1.render("RAS CONFIGURATION " + str(MAX_STA1_CONFIGURATION  - (MAX_STA1_CONFIGURATION/(NUM_CONFIGURATION+1)*2) ) , 1, WITHE_COLOR), (screen.get_width() - 400, screen.get_height()/(NUM_CONFIGURATION+1)*2-20+OFFSET))
				pygame.draw.line(screen, GRID_COLOR, (5, (screen.get_height()/(NUM_CONFIGURATION+1)*2)+OFFSET), (screen.get_width()-(NUM_CONFIGURATION+1), (screen.get_height()/(NUM_CONFIGURATION+1)*2)+OFFSET))

				#screen.blit(font1.render("RAS CONFIGURATION " + str(MAX_STA1_CONFIGURATION  - ((MAX_STA1_CONFIGURATION/(NUM_CONFIGURATION+1))*3) ) , 1, WITHE_COLOR), (screen.get_width() - 400, screen.get_height()/(NUM_CONFIGURATION+1)*3-20+OFFSET))
				#pygame.draw.line(screen, GRID_COLOR, (5, (screen.get_height()/(NUM_CONFIGURATION+1)*3)+OFFSET), (screen.get_width()-(NUM_CONFIGURATION+1), (screen.get_height()/(NUM_CONFIGURATION+1)*3)+OFFSET))

				screen.blit(font1.render("RAS CONFIGURATION " + str(MAX_STA1_CONFIGURATION  - ((MAX_STA1_CONFIGURATION/(NUM_CONFIGURATION+1))*4) ) , 1, WITHE_COLOR), (screen.get_width() - 400, screen.get_height()/(NUM_CONFIGURATION+1)*4-20+OFFSET))
				pygame.draw.line(screen, GRID_COLOR, (5, (screen.get_height()/(NUM_CONFIGURATION+1)*4)+OFFSET), (screen.get_width()-(NUM_CONFIGURATION+1), (screen.get_height()/(NUM_CONFIGURATION+1)*4)+OFFSET))

				#screen.blit(font1.render("RAS CONFIGURATION " + str(MAX_STA1_CONFIGURATION  - ((MAX_STA1_CONFIGURATION/(NUM_CONFIGURATION+1))*5) ) , 1, WITHE_COLOR), (screen.get_width() - 400, screen.get_height()/(NUM_CONFIGURATION+1)*5-20+OFFSET))
				#pygame.draw.line(screen, GRID_COLOR, (5, (screen.get_height()/(NUM_CONFIGURATION+1)*5)+OFFSET), (screen.get_width()-(NUM_CONFIGURATION+1), (screen.get_height()/(NUM_CONFIGURATION+1)*5)+OFFSET))

				screen.blit(font1.render("RAS CONFIGURATION " + str(MAX_STA1_CONFIGURATION  - ((MAX_STA1_CONFIGURATION/(NUM_CONFIGURATION+1))*6) ) , 1, WITHE_COLOR), (screen.get_width() - 400, screen.get_height()/(NUM_CONFIGURATION+1)*6-20+OFFSET))
				pygame.draw.line(screen, GRID_COLOR, (5, (screen.get_height()/(NUM_CONFIGURATION+1)*6)+OFFSET), (screen.get_width()-(NUM_CONFIGURATION+1), (screen.get_height()/(NUM_CONFIGURATION+1)*6)+OFFSET))

				#screen.blit(font1.render("RAS CONFIGURATION " + str(MAX_STA1_CONFIGURATION  - ((MAX_STA1_CONFIGURATION/(NUM_CONFIGURATION+1))*7) ) , 1, WITHE_COLOR), (screen.get_width() - 400, screen.get_height()/(NUM_CONFIGURATION+1)*7-20+OFFSET))
				#pygame.draw.line(screen, GRID_COLOR, (5, (screen.get_height()/(NUM_CONFIGURATION+1)*7)+OFFSET), (screen.get_width()-(NUM_CONFIGURATION+1), (screen.get_height()/(NUM_CONFIGURATION+1)*7)+OFFSET))

				screen.blit(font1.render("RAS CONFIGURATION " + str(MAX_STA1_CONFIGURATION  - ((MAX_STA1_CONFIGURATION/(NUM_CONFIGURATION+1))*8) ) , 1, WITHE_COLOR), (screen.get_width() - 400, screen.get_height()/(NUM_CONFIGURATION+1)*8-20+OFFSET))
				pygame.draw.line(screen, GRID_COLOR, (5, (screen.get_height()/(NUM_CONFIGURATION+1)*8)+OFFSET), (screen.get_width()-(NUM_CONFIGURATION+1), (screen.get_height()/(NUM_CONFIGURATION+1)*8)+OFFSET))

				#screen.blit(font1.render("RAS CONFIGURATION " + str(MAX_STA1_CONFIGURATION  - ((MAX_STA1_CONFIGURATION/(NUM_CONFIGURATION+1))*9) ) , 1, WITHE_COLOR), (screen.get_width() - 400, screen.get_height()/(NUM_CONFIGURATION+1)*9-20+OFFSET))
				#pygame.draw.line(screen, GRID_COLOR, (5, (screen.get_height()/(NUM_CONFIGURATION+1)*9)+OFFSET), (screen.get_width()-(NUM_CONFIGURATION+1), (screen.get_height()/(NUM_CONFIGURATION+1)*9)+OFFSET))

				screen.blit(font1.render("-" + str(60) + "dBm", 1, YELLOW_COLOR), (screen.get_width() - 200, 10 + OFFSET))
				pygame.draw.line(screen, WITHE_COLOR, (5, (10)+OFFSET), (screen.get_width(), (10)+OFFSET))

				screen.blit(font1.render(str(MAX_STA1_THR  - (MAX_STA1_THR/2)) + "Kbps" , 1, RED_COLOR), (screen.get_width() - 400, (screen.get_height()/2) -20 + OFFSET))
				#screen.blit(font1.render("-" + str(MAX_STA1_PWR  - (MAX_STA1_PWR/2) ) + "dBm", 1, YELLOW_COLOR), (screen.get_width() - 200, (screen.get_height()/2) -20 + OFFSET))
				screen.blit(font1.render("-" + str(70) + "dBm", 1, YELLOW_COLOR), (screen.get_width() - 200, (screen.get_height()/2) -20 + OFFSET))
				pygame.draw.line(screen, WITHE_COLOR, (5, (screen.get_height()/2)+OFFSET), (screen.get_width(), (screen.get_height()/2)+OFFSET))

				#pygame.draw.lines(screen, BLUE_COLOR, False, normalizePoints(STA1_CONFIGURATION), 5)
				#pygame.draw.lines(screen, YELLOW_COLOR, False, normalizePoints(STA2_CONFIGURATION), 5)
				pygame.draw.lines(screen, WITHE_COLOR, False, normalizePoints(STA3_CONFIGURATION), 5)
				#pygame.draw.lines(screen, RED_COLOR, False, normalizePoints(STA4_CONFIGURATION), 5)

				pygame.draw.lines(screen, RED_COLOR, False, normalizePoints(STA1_THR), 5)

				pygame.draw.lines(screen, YELLOW_COLOR, False, normalizePoints(STA1_PWR), 5)


				pygame.display.update()

########################################################################




def ho_event(x):




	global ZMQ_PORT
	# Socket to talk to server
	context = zmq.Context()
	port1 = 8300
	socket_zmq1 = context.socket(zmq.SUB)
	socket_zmq1.connect ("tcp://localhost:%s" % port1)
	socket_zmq1.setsockopt(zmq.SUBSCRIBE, '')
	port2 = 8301
	socket_zmq2 = context.socket(zmq.SUB)
	socket_zmq2.connect ("tcp://localhost:%s" % port2)
	socket_zmq2.setsockopt(zmq.SUBSCRIBE, '')
	port3 = 8302
	socket_zmq3 = context.socket(zmq.SUB)
	socket_zmq3.connect ("tcp://localhost:%s" % port3)
	socket_zmq3.setsockopt(zmq.SUBSCRIBE, '')

	poller = zmq.Poller()
	poller.register(socket_zmq1, flags=zmq.POLLIN)
	poller.register(socket_zmq2, flags=zmq.POLLIN)
	poller.register(socket_zmq3, flags=zmq.POLLIN)

	print('Server started wait for messages (polling)')
	while True:
		#print('polling')
		socket_list = poller.poll(1000)
		if socket_list:
			for socket_info in socket_list:
				if socket_info[1] == zmq.POLLIN:
					parsed_json = socket_info[0].recv_json()
					# print('parsed_json : %s' % str(parsed_json))

					remote_ipAddress = parsed_json['node_ip_address']
					len_station_dump = len(stations_dump)

					# add measurement on nodes element
					for i in range(0,len_station_dump):
						#print 'stations_dump[i][0] (%s) == remote_wlan_ipAddress (%s)' % (str(stations_dump[i][0]), str(remote_ipAddress) )
						if stations_dump[i][0] == remote_ipAddress :
							#parsed_json : {u'throughput': 7867.0, u'node_ip_address': u'10.11.16.126', u'delta': 1.0}
							if 'throughput' in parsed_json:
								delta = parsed_json['delta']
								# end_thr = parsed_json['throughput'].find('Mbits/sec')
								# thr = parsed_json['throughput'][0:end_thr-1]
								#stations_dump[i][2] = float(thr)	#active CONFIGURATION
								stations_dump[i][2] = float(parsed_json['throughput'])	#active CONFIGURATION

							#parsed_json : {u'ras_configuration': 8, u'node_ip_address': u'10.11.16.108'}
							if 'ras_configuration' in parsed_json:
								stations_dump[i][3] = float(parsed_json['ras_configuration'])

							#parsed_json : {u'avgpower': -72.47540983606558, u'node_ip_address': u'10.11.16.126'}
							if 'avg_power' in parsed_json:
								stations_dump[i][4] = (float(parsed_json['avg_power'])*-1)


start_new_thread(ho_event,(99,))
#ho_event(99)

# main loop
main()
#start_new_thread(main,(99,))
