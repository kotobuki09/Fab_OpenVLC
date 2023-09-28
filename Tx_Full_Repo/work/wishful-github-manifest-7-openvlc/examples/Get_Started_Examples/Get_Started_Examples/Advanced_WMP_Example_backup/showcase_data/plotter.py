#!/usr/bin/python

__author__ = "Pierluigi Gallo, Domenico Garlisi"
__copyright__ = "Copyright (c) 2016, CNIT"
__version__ = "0.1.0"
__email__ = "domenico.garlisi@cnit.it"

import sys
import subprocess
import time
import multiprocessing
from time import gmtime, strftime

from numpy import *
from datetime import datetime, date, timedelta

import matplotlib

# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt, os, fnmatch
from matplotlib.backends.backend_pdf import PdfPages


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import json

"""
Starting from the stored experiment measurements this script creates 2 plots with protocol and throughput experiment
result.
"""
#loading data
with open('measure.json') as data_file:
	data = json.load(data_file)

#define data field
measurement_types=['TIME', 'PROTOCOL', 'THR']
protocols_labels = ['', 'TDMA 0 (slot 0)', 'TDMA 1 (slot 1)', 'TDMA 2 (slot 2)', 'TDMA 3 (slot 3)', 'ALOHA p=0.9']
protocols_tick = [0, 1, 2, 3, 4]

x = array(data.get(list(sort(data.keys()))[0]))
dim = x.shape
yaxis = [0] * dim[0]
my_dpi=100
width=1024
height=768


node_num = 0
for node in list(sort(data.keys())):

	nodeIp=node
	node_num += 1
	x = array(data.get(nodeIp))
	#print("%s" % str(x))

	dim = x.shape
	xaxis = []

	if len(dim) > 2:
		number_type_measurements = dim[2]
	else:
		number_type_measurements = 1


	for meas_type_id in range(number_type_measurements):
		#extract reference time information
		if measurement_types[meas_type_id] == "TIME" :
			min_time=np.min(x[:,0,meas_type_id])
			for ii in range(dim[0]):
				xaxis.append(x[ii][0][meas_type_id])

		#extract protocol information
		if measurement_types[meas_type_id] == "PROTOCOL" :
			protocol_yaxis = []

			if nodeIp=="192.168.3.110" or nodeIp=="192.168.3.104" or nodeIp=="192.168.3.105" or nodeIp=="192.168.3.114":
				print(" node : " + nodeIp + " ( plot --> " + measurement_types[meas_type_id] + " )")

				for ii in range(dim[0]):
					protocol_yaxis.append(x[ii][0][meas_type_id])

				figure_id = 0
				fig=plt.figure(figure_id)
				ax = fig.add_subplot(211)
				#nodeIp_label=nodeIp.replace("192.168.3.","sta")
				nodeIp_label = 'sta' + str(node_num)
				ax.plot((xaxis-min_time), protocol_yaxis, '-', label=nodeIp_label, linewidth=2.0);

				ax.grid(True)
				ax.set_xlim([0, (np.max(xaxis)-np.min(xaxis))])
				ax.set_ylim([-0.5, 5])

				ax.set_ylabel('PROTOCOL');
				ax.set_xlabel('time [s]')

				#ax.yticks(protocols_tick, protocols_labels)
				#locs, labels = ax.yticks()
				ax.set_yticklabels(protocols_labels)

				fig.set_size_inches(width/my_dpi,height/my_dpi)
				plt.tight_layout()
				legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1), ncol=5, fancybox=True, shadow=True)

		#extract throughput information
		if measurement_types[meas_type_id] == "THR" :
			num_thr_yaxis = []
			if nodeIp=="192.168.3.110" or nodeIp=="192.168.3.104" or nodeIp=="192.168.3.105" or nodeIp=="192.168.3.114":
				print(" node : " + nodeIp + " ( plot --> " + measurement_types[meas_type_id] + " )")

				for ii in range(dim[0]):
					num_thr_yaxis.append(x[ii][0][meas_type_id])

				figure_id = 0
				fig=plt.figure(figure_id)
				ax = fig.add_subplot(212)
				#nodeIp_label=nodeIp.replace("10.8.8.1","sta")
				nodeIp_label = 'sta' + str(node_num)
				#ax.plot((xaxis-min_time), num_thr_yaxis, color='k', label=nodeIp_label);
				ax.plot((xaxis-min_time), num_thr_yaxis, '-', label=nodeIp_label, linewidth=2.0);

				ax.grid(True)
				ax.set_xlim([0, (np.max(xaxis)-np.min(xaxis))])
				ax.set_ylim([0, 1600])

				fig.set_size_inches(width/my_dpi,height/my_dpi)
				plt.tight_layout()
				legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1), ncol=5, fancybox=True, shadow=True)

				ax.set_ylabel('THR Kbps');
				ax.set_xlabel('time [s]')



#generate pdf plot
fig.set_size_inches(width/my_dpi,height/my_dpi)
plt.tight_layout()
#plt.show()
fig_filename="fig_%s.pdf" % 'metamac-experiment-result'
fig.savefig(fig_filename, format='pdf')
