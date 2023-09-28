#!/usr/bin/python

import sys
import getopt
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

try:
    opts, args = getopt.getopt(sys.argv[1:], 'j:h', ['jsonfile=', 'help'])
except getopt.GetoptError:
    print("Usage: %s -j jsonfile_name" % sys.argv[0])
    sys.exit(2)

jsonfile = None
for opt, arg in opts:
    if opt in ('-h', '--help'):
        print("Usage: %s -j jsonfile_name" % sys.argv[0])
        sys.exit(2)
    elif opt in ('-j', '--jsonfile'):
        jsonfile = arg
    else:
        print("Usage: %s -j jsonfile_name" % sys.argv[0])
        sys.exit(2)

with open(jsonfile) as data_file:
    data = json.load(data_file)

measurement_types = ['TIME', 'CONFIGURATION', 'THR', 'POWER']
protocols_labels = ['', 'TDMA 0 (slot 0)', 'TDMA 1 (slot 1)', 'TDMA 2 (slot 2)', 'TDMA 3 (slot 3)', 'ALOHA p=0.9']
protocols_tick = [0, 1, 2, 3, 4]

x = array(data.get(list(sort(data.keys()))[0]))
dim = x.shape
yaxis = [0] * dim[0]
my_dpi = 100
width = 1024
height = 768
min_x = 15
max_x = 65

node_num = 0
for node in list(sort(data.keys())):

    nodeIp = node
    node_num += 1
    x = array(data.get(nodeIp))
    # print("%s" % str(x))

    dim = x.shape
    xaxis = []

    if len(dim) > 2:
        number_type_measurements = dim[2]
    else:
        number_type_measurements = 1

    for meas_type_id in range(number_type_measurements):

        if measurement_types[meas_type_id] == "TIME":
            min_time = np.min(x[:, 0, meas_type_id])
            for ii in range(dim[0]):
                xaxis.append(x[ii][0][meas_type_id])

        if measurement_types[meas_type_id] == "CONFIGURATION":
            protocol_yaxis = []

            if nodeIp == "192.168.3.140":
                print(" node : " + nodeIp + " ( plot --> " + measurement_types[meas_type_id] + " )")

                for ii in range(dim[0]):
                    protocol_yaxis.append(x[ii][0][meas_type_id])

                figure_id = 0
                fig = plt.figure(figure_id)
                ax = fig.add_subplot(311)
                # nodeIp_label=nodeIp.replace("192.168.3.","sta")
                #nodeIp_label = 'sta' + str(node_num)
                nodeIp_label = 'TX NODE'
                ax.plot((xaxis - min_time), protocol_yaxis, '-', label=nodeIp_label, linewidth=2.0);

                ax.grid(True)
                #ax.set_xlim([0, (np.max(xaxis) - np.min(xaxis))])
                ax.set_xlim([min_x, max_x])
                ax.set_ylim([-0.5, 8.5])

                ax.set_ylabel('RAS ANTENNA \n CONFIGURATION');
                ax.set_xlabel('time [s]')

                # ax.yticks(protocols_tick, protocols_labels)
                # locs, labels = ax.yticks()
                # ax.set_yticklabels(protocols_labels)

                fig.set_size_inches(width / my_dpi, height / my_dpi)
                plt.tight_layout()
                legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1), ncol=5, fancybox=True, shadow=True)

        if measurement_types[meas_type_id] == "THR":
            num_thr_yaxis = []
            if nodeIp == "192.168.3.140":
                print(" node : " + nodeIp + " ( plot --> " + measurement_types[meas_type_id] + " )")

                for ii in range(dim[0]):
                    num_thr_yaxis.append(x[ii][0][meas_type_id]/1000)

                figure_id = 0
                fig = plt.figure(figure_id)
                ax = fig.add_subplot(312)
                # nodeIp_label=nodeIp.replace("10.8.8.1","sta")
                #nodeIp_label = 'sta' + str(node_num)
                nodeIp_label = 'RX NODE'
                # ax.plot((xaxis-min_time), num_thr_yaxis, color='k', label=nodeIp_label);
                ax.plot((xaxis - min_time), num_thr_yaxis, '-', color='k', label=nodeIp_label, linewidth=2.0);

                ax.grid(True)
                #ax.set_xlim([0, (np.max(xaxis) - np.min(xaxis))])
                ax.set_xlim([min_x, max_x])
                ax.set_ylim([20, 30])

                fig.set_size_inches(width / my_dpi, height / my_dpi)
                plt.tight_layout()
                legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1), ncol=5, fancybox=True, shadow=True)

                ax.set_ylabel('THR Mbps');
                ax.set_xlabel('time [s]')

        if measurement_types[meas_type_id] == "POWER":
            num_thr_yaxis = []
            if nodeIp == "192.168.3.140":
                print(" node : " + nodeIp + " ( plot --> " + measurement_types[meas_type_id] + " )")

                for ii in range(dim[0]):
                    num_thr_yaxis.append(x[ii][0][meas_type_id])

                figure_id = 0
                fig = plt.figure(figure_id)
                ax = fig.add_subplot(313)
                # nodeIp_label=nodeIp.replace("10.8.8.1","sta")
                #nodeIp_label = 'sta' + str(node_num)
                nodeIp_label = 'RX NODE'
                # ax.plot((xaxis-min_time), num_thr_yaxis, color='k', label=nodeIp_label);
                ax.plot((xaxis - min_time), num_thr_yaxis, '-', color='r', label=nodeIp_label, linewidth=2.0);

                ax.grid(True)
                #ax.set_xlim([0, (np.max(xaxis) - np.min(xaxis))])
                ax.set_xlim([min_x, max_x])
                ax.set_ylim([-71, -62])

                fig.set_size_inches(width / my_dpi, height / my_dpi)
                plt.tight_layout()
                legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1), ncol=5, fancybox=True, shadow=True)

                ax.set_ylabel('POWER dBm');
                ax.set_xlabel('time [s]')

fig.set_size_inches(width / my_dpi, height / my_dpi)
plt.tight_layout()
# plt.show()
fig_filename = "fig_%s.pdf" % 'ras_antenna'  # measurement_types[meas_type_id]
fig.savefig(fig_filename, format='pdf')
