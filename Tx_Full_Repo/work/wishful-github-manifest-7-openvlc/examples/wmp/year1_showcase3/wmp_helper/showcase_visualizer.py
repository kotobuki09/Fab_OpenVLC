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
from thread import start_new_thread

HELP_MSG	= sys.argv[0]+" --address <IP> [--interval <X.Y>] [--max-ping <X>] [--history <X>] [--window-height <X>] [--window-width <X>] [--fullscreen] [--ping-threshold <X>]"

IP_ADDR		= "192.168.5.222" # Default IP
CLOCK_DELTA	= 0.1 #0.02 # Minimal refresh rate
MAX_PING	= 150.0 # The visualization will automatically scale to display 0 ping on top and MAX_PING ping at the bottom

MAX_DRAW_LINE = 1000
MAX_RX_ACK_LINE = MAX_DRAW_LINE
MAX_FREEZING = MAX_DRAW_LINE
MAX_RX_MATCH_LINE = MAX_DRAW_LINE
MAX_TX_FRAME_LINE = MAX_DRAW_LINE
MAX_TX_FRAME_LINE_2 = MAX_DRAW_LINE
MAX_STD_TX_FRAME_CUMULATIVE = MAX_DRAW_LINE
MAX_IPT = MAX_DRAW_LINE

HISTORY_SIZE	= 1200.0 # Number of history values to display
COORD_MULT	= {"X": 1, "Y": 1} # Coord scaler, automatically determined based on window size, MAX_PING and HISTORY_SIZE
RESOLUTION	= (1400, 800) # Default window size
#RESOLUTION	= (1024, 800) # Default window size
#RESOLUTION	= (1920, 500) # Default window size
RX_ACK_LINE	= []
FREEZING = []
TX_FRAME_LINE = []
TX_FRAME_LINE_2 = []
IPT_LINE = []
STD_TX_FRAME_CUMULATIVE = []
RX_MATCH_LINE	= []
HISTORY		= []
SWITCH 		= []
PLOSS 		= []

TEXT_COLOR	= (180, 180, 180) # Infotext color
RED_COLOR	= (255, 0, 0)
YELLOW_COLOR	= (255, 255, 0)

PING_THRESHOLD	= 250 # Ping above this value will raise the INTERNET DYING warning
LAG_THRESHOLD	= [ # You can define custom ping thresholds that will display lines across the screen
			{"ping": 40,  "color": (0, 120, 0), "desc": "AP1"},
			{"ping": 35, "color": (0, 120, 0), "desc": "AP2"}
		]


stations_dump = [["192.168.3.1", "alix1", 0, 0, 0, 0, 0 ,0, 0],
                # ["192.168.3.2", "alix2", 0, 0, 0, 0, 0, 0, 0],
                # ["192.168.3.3", "alix3", 0, 0, 0, 0, 0, 0, 0],
                # ["192.168.3.4", "alix4", 0, 0, 0, 0, 0, 0, 0],
                # ["192.168.3.5", "alix5", 0, 0, 0, 0, 0, 0, 0],
                # ["192.168.3.6", "alix6", 0, 0, 0, 0, 0, 0, 0],
                # ["192.168.3.7", "alix7", 0, 0, 0, 0, 0, 0, 0],
                # ["192.168.3.8", "alix8", 0, 0, 0, 0, 0, 0, 0],
                # ["192.168.3.9", "alix9", 0, 0, 0, 0, 0, 0, 0],
                # ["192.168.3.10", "alix10", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.11", "alix11", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.12", "alix12", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.13", "alix13", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.14", "alix14", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.102", "alix2", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.103", "alix3", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.104", "alix4", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.105", "alix5", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.110", "alix10", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.111", "alix11", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.112", "alix12", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.113", "alix13", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.114", "alix14", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.221", "dssnode1", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.222", "dssnode2", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.223", "dssnode3", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.224", "dssnode4", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.225", "dssnode5", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.226", "dssnode6", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.23", "zotacnode1", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.34", "zotacnode2", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.53", "zotacnode3", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.24", "zotacnode4", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.35", "zotacnode5", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.54", "zotacnode6", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.26", "zotacnode7", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.37", "zotacnode8", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.55", "zotacnode9", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.27", "zotacnode10", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.38", "zotacnode11", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.56", "zotacnode12", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.29", "zotacnode13", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.29", "zotacnode14", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.28", "zotacnode18", 0, 0, 0, 0, 0, 0, 0],
                ["192.168.3.1", "zotacnode19", 0, 0, 0, 0, 0, 0, 0]]

num_active_traffic = 0
old_num_active_traffic = 0

def getNextArg():
	getNextArg.n = getNextArg.n + 1
	return sys.argv[getNextArg.n]
getNextArg.n = 0

def parseArgs():
	global HELP_MSG
	global IP_ADDR
	global ZMQ_PORT
	global MAX_PING
	global CLOCK_DELTA
	global HISTORY_SIZE
	global RESOLUTION
	global PING_THRESHOLD

	try:
		while (True):
			a = getNextArg()
			if   ((a == "--help") or (a == "-h")):
				print HELP_MSG
				exit()
			elif (a == "--address"):
				IP_ADDR = getNextArg()
			elif (a == "--port"):
				ZMQ_PORT = getNextArg()
			elif (a == "--max-ping"):
				MAX_PING = float(getNextArg())
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
			elif (a == "--ping-threshold"):
				PING_THRESHOLD = float(getNextArg())
	except IndexError:
		pass

def normalizePoints(p):
	i = 0
	ret = []
	for point in p:
		ret.append((i*COORD_MULT["X"], point*COORD_MULT["Y"]))
		i = i+1
	return ret

def getPing(ip):
	try:
		r = subprocess.check_output("/usr/bin/timeout 0.05 /bin/ping -qc 1 -W 1 -s 240 "+ip, shell=True)
		rg = re.search("(\d+\.\d+)/\d+\.\d+/\d+\.\d+/\d+\.\d+", r)
		if (rg):
			return float(rg.group(1))
		else:
			print "Unexpected error:", sys.exc_info()[0]
			return 500.0
	except:
	#	print "Unexpected error:", sys.exc_info()[0]
	#	return 100.0
	#except subprocess.CalledProcessError, e:
		#print "Ping stdout output:\n", e.output
		return 50.0
		
def main():
	global IP_ADDR
	global CLOCK_DELTA
	global HISTORY_SIZE
	global HISTORY
	global RX_ACK_LINE
	global FREEZING
	global RX_MATCH_LINE
	global TX_FRAME_LINE
	global TX_FRAME_LINE_2
	global IPT_LINE
	global STD_TX_FRAME_CUMULATIVE
	global MAX_PING
	global RESOLUTION
	global COORD_MULT
	global HELP_MSG
	global num_active_traffic
	global old_num_active_traffic

	#if (len(sys.argv) < 2):
	#	print HELP_MSG
	#	exit()

	parseArgs()

	CLOCK = -10.0

	pygame.init()
	pygame.display.set_caption("WISHFUL SHOWCASE 3")
	if (RESOLUTION == (0, 0)):
		screen = pygame.display.set_mode(RESOLUTION, pygame.FULLSCREEN)
	else:
		screen = pygame.display.set_mode(RESOLUTION)

	font = pygame.font.SysFont("monospace", 15)
	font2 = pygame.font.SysFont("monospace", 18)
	font1 = pygame.font.SysFont("monospace", 10)

	screen.blit(font.render("LOADING", True, (255, 255, 255)), (10, 10))
	pygame.display.update()

	myimage = pygame.image.load("CNIT.GIF")
	#myimage = pygame.image.load("wishful.png")
	imagerect = myimage.get_rect()
	imagerect.x = imagerect.x + screen.get_width()-400
	imagerect.y = imagerect.y + screen.get_height()-150
	
	COORD_MULT["X"] = screen.get_width() / HISTORY_SIZE
	COORD_MULT["Y"] = screen.get_height() / MAX_PING


	std_cumulative_tx_frame_interval_start = 0
	std_cumulative_tx_frame = 0



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
					exit()

		if (time.clock() > (CLOCK + CLOCK_DELTA)):
			CLOCK = time.clock()
			if (len(HISTORY) >= HISTORY_SIZE):
				RX_ACK_LINE.pop(0)
				FREEZING.pop(0)
				TX_FRAME_LINE.pop(0)
				TX_FRAME_LINE_2.pop(0)
				STD_TX_FRAME_CUMULATIVE.pop(0)
				RX_MATCH_LINE.pop(0)
				IPT_LINE.pop(0)
				HISTORY.pop(0)
				#SWITCH.pop(0)
				#PLOSS.pop(0)


			#n = getPing(IP_ADDR)
			# n = stations_dump[0][3]
			# if n == 50.0 and len(HISTORY) >= 1:
			# 	n = HISTORY[-1]
			# 	PLOSS.append(27.0)
			# 	#PLOSS.append(30.0)
			# else:
			# 	PLOSS.append(30.0)
            #

			cumulative_tx_frame = 0
			cumulative_freezing = 0
			cumulative_ipt = 0
			cumulative_rx_frame = 0

			#print "RX FRAME"
			AP_index=0
			for row in stations_dump:
				#for col in row:
				if row[1] == "alix2":
					break
				AP_index += 1
			cumulative_rx_frame = stations_dump[AP_index][7]
			#print cumulative_rx_frame

			#print "TX FRAME"
			for ii in range(1, len(stations_dump), 1):
				#print "%s - %d" % (stations_dump[ii][1], stations_dump[ii][4])
				cumulative_tx_frame += stations_dump[ii][4]
				cumulative_freezing += stations_dump[ii][2]
				cumulative_ipt += stations_dump[ii][8]
			TX_FRAME_LINE_2.append( MAX_PING - 0.5 - (( cumulative_tx_frame/MAX_RX_MATCH_LINE)*MAX_PING ) )

			if num_active_traffic != 0:
				cumulative_freezing = cumulative_freezing / num_active_traffic
				#cumulative_ipt = cumulative_ipt / num_active_traffic
			else:
				cumulative_freezing = 0
				#cumulative_ipt = 0

			FREEZING.append( MAX_PING - 0.5 - (( cumulative_freezing / MAX_RX_MATCH_LINE) * MAX_PING ) )
			IPT_LINE.append( MAX_PING - cumulative_ipt )
			HISTORY.append( MAX_PING - stations_dump[2][3] ) #CW
			RX_ACK_LINE.append( MAX_PING - 1 - (( stations_dump[0][5]/MAX_RX_ACK_LINE)*MAX_PING ) )
			RX_MATCH_LINE.append( MAX_PING - 0.5 - (( cumulative_rx_frame/MAX_RX_MATCH_LINE)*MAX_PING ) )
			TX_FRAME_LINE.append( MAX_PING - 0.5 - (( stations_dump[1][4]/MAX_RX_MATCH_LINE)*MAX_PING ) )
			#TX_FRAME_LINE_2.append( MAX_PING - 0.5 - (( stations_dump[2][4]/MAX_RX_MATCH_LINE)*MAX_PING ) )

			if num_active_traffic != old_num_active_traffic :
				std_cumulative_tx_frame = numpy.std(TX_FRAME_LINE_2[std_cumulative_tx_frame_interval_start:len(TX_FRAME_LINE_2)])
				#print "New interval with len : " +  str(len(TX_FRAME_LINE_2) - std_cumulative_tx_frame_interval_start)
				#print TX_FRAME_LINE_2[std_cumulative_tx_frame_interval_start:len(TX_FRAME_LINE_2)]
				#print "STD = " + str(std_cumulative_tx_frame) + "\n"
				old_num_active_traffic = num_active_traffic
				std_cumulative_tx_frame_interval_start = len(TX_FRAME_LINE_2) + 5
			STD_TX_FRAME_CUMULATIVE.append(MAX_PING - 0.5 - (( std_cumulative_tx_frame/MAX_RX_MATCH_LINE)*MAX_PING ))



			if (len(HISTORY) > 1):

				#set background color
				screen.fill((78, 74, 76))

				screen.blit(font.render("MULT_X: "+str(COORD_MULT["X"])+", MULT_Y: "+str(COORD_MULT["Y"]), 1, TEXT_COLOR), (5, screen.get_height()-40))
				#screen.blit(font.render("IP Address: "+stations_dump[0][0], 1, TEXT_COLOR), (5, screen.get_height()-60))
				screen.blit(font.render("Clock: "+str(CLOCK), 1, TEXT_COLOR), (5, screen.get_height()-60))
				screen.blit(font.render("History size: "+str(HISTORY_SIZE), 1, TEXT_COLOR), (5, screen.get_height()-80))
				#num_active_traffic = stations_dump[0][8] + stations_dump[1][8] + stations_dump[2][8] + stations_dump[3][8] + stations_dump[4][8] + stations_dump[5][8] + stations_dump[6][8] + stations_dump[7][8]
				screen.blit(font.render("Num active traffic: "+str(num_active_traffic), 1, TEXT_COLOR), (5, screen.get_height()-100))
				screen.blit(font.render("Contention Window: "+str(stations_dump[0][3]), 1, (255, 0, 0)), (5, screen.get_height()-120))
				screen.blit(font.render("Successful RX frames : " + str(cumulative_rx_frame) + "/s", 1, (0, 255, 0)), (5, screen.get_height()-140))
				screen.blit(font.render("Cumulative TX frames : " + str(cumulative_tx_frame) + "/s", 1, (255, 255, 255)), (5, screen.get_height()-160))
				screen.blit(font.render("STD(Cumulative TX frames) : " + str(std_cumulative_tx_frame) + "/10s", 1, (255, 255, 255)), (5, screen.get_height()-180))
				screen.blit(font.render("Cumulative freezing : " + str(cumulative_freezing) + "/.5s", 1, (255, 255, 255)), (5, screen.get_height()-200))
				screen.blit(font.render("Cumulative ipt : " + str(cumulative_ipt) + "/.5s", 1, (255, 255, 255)), (5, screen.get_height()-220))



				# new stuff
			#	screen.blit(font2.render("Ping RTT", 1, TEXT_COLOR), (5, 10))
				screen.blit(font1.render("" + str(MAX_PING - (MAX_PING/4) ) + " ", 1, (255, 0, 0) ), (5, screen.get_height()/4-10))
				screen.blit(font1.render("" + str(MAX_RX_MATCH_LINE  - (MAX_RX_MATCH_LINE/4) ) + " ", 1, (0, 255, 0)), (screen.get_width() - 40, screen.get_height()/4-10))
				pygame.draw.line(screen, (100, 100, 100), (5, screen.get_height()/4), (screen.get_width()-5, screen.get_height()/4))
				screen.blit(font1.render("" + str(MAX_PING/2) + " ", 1, (255, 0, 0)), (5, screen.get_height()/2-10))
				screen.blit(font1.render("" + str(MAX_RX_MATCH_LINE/2) + " ", 1, (0,255,0)), (screen.get_width() - 40, screen.get_height()/2-10))
				pygame.draw.line(screen, (100, 100, 100), (5, screen.get_height()/2), (screen.get_width()-5, screen.get_height()/2))
				
				#screen.blit(font2.render("Packet loss", 1, TEXT_COLOR), (5, screen.get_height()-440))
				#screen.blit(font2.render("Serving AP", 1, TEXT_COLOR), (5, screen.get_height()-340))
				#screen.blit(font2.render("Telecommunication Networks Group (TKN)", 1, RED_COLOR), (screen.get_width()-800, screen.get_height()-90))
				#screen.blit(font2.render("Technische Universitaet Berlin", 1, RED_COLOR), (screen.get_width()-700, screen.get_height()-60))
				
				#screen.blit(font2.render("x", 1, RED_COLOR), (500, 500))
				
				screen.blit(myimage, imagerect)
 
				pygame.draw.lines(screen, (255, 0, 0), False, normalizePoints(HISTORY), 1)
				#pygame.draw.lines(screen, (255, 0, 0), False, normalizePoints(RX_ACK_LINE), 1)
				#pygame.draw.lines(screen, (0, 0, 255), False, normalizePoints(TX_FRAME_LINE), 1)
				pygame.draw.lines(screen, (255, 255, 255), False, normalizePoints(TX_FRAME_LINE_2), 1)
				pygame.draw.lines(screen, (0, 255, 0), False, normalizePoints(RX_MATCH_LINE), 1)
				#pygame.draw.lines(screen, (0, 255, 0), False, normalizePoints(SWITCH), 1)
				#pygame.draw.lines(screen, (0, 255, 255), False, normalizePoints(PLOSS), 1)
				
				# for kk in range(len(HISTORY)):
				# 	if PLOSS[kk] is not 30.0:
				# 		xx = int(kk*COORD_MULT["X"])
				# 		yy = int(1*COORD_MULT["Y"])
				# 		#pygame.draw.circle(screen, (0, 255, 0), (xx,yy), 10, 2)
				# 		screen.blit(font.render("X", 1, YELLOW_COLOR), (xx,yy))
				
				pygame.display.update()

########################################################################




def ho_event(x):
	global servingAP
	global ZMQ_PORT
	global num_active_traffic

	context = zmq.Context()
	port  = 12345
	# Socket to talk to server
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.connect ("tcp://localhost:%s" % port)
	socket.setsockopt(zmq.SUBSCRIBE, '')

	while True:

		# json_message = socket.recv_json()
        # #print 'json_message : %s' % str(json_message)
        # msg_data = json_message['msg']

		msg_data = socket.recv_json()
		print 'msg_data : %s' % str(msg_data)

		remote_wlan_ipAddress = msg_data['ip_address']
		measurement_types = 'MEASURE'
		measurement = msg_data['measure']
		num_active_traffic = msg_data['traffic']

		len_station_dump = len(stations_dump)
		#print 'len_station_dump %d' % len_station_dump
		# add measurement on nodes element
		#measurement_types=['FREEZING_NUMBER', 'TSF', 'RX_ACK_RAMATCH', 'CW', 'IPT', 'TX_DATA', 'RX_ACK', 'BUSY_TIME', 'delta_TSF', 'NUM_RX_MATCH']
		for i in range(0,len_station_dump):
			#print 'stations_dump[i][0] (%s) == remote_wlan_ipAddress (%s)' % (str(stations_dump[i][0]), str(remote_wlan_ipAddress) )

			if stations_dump[i][0] == remote_wlan_ipAddress and measurement != False:
				stations_dump[i][2] = measurement[0][0]				#'FREEZING_NUMBER'
				stations_dump[i][3] = round(measurement[0][3], 1)	#'CW'
				stations_dump[i][4] = round(measurement[0][5], 1)	#'TX_DATA'
				stations_dump[i][5] = round(measurement[0][2], 1)	#'TSF'
				stations_dump[i][6] = round((measurement[0][2] * 200 * 8 * 10 ), 1) #(I use frame of 200byte collected every 100ms)
				stations_dump[i][7] = round((measurement[0][9]), 1) #(I use frame of 200byte collected every 100ms)


#start_new_thread(main,(99,))
start_new_thread(ho_event,(99,))
#ho_event(99)

# main loop
main()
#start_new_thread(main,(99,))
