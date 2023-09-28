#!/usr/bin/python
__author__ = 'Pierluigi Gallo'
"""
EU project WISHFUL
"""

import sys
import subprocess
import time
import multiprocessing
from time import gmtime, strftime

from master.master import *
from numpy import *
from datetime import datetime, date, timedelta

from common.upihelper import unix_time_as_tuple, get_now_full_second, dumpFuncName

import matplotlib
import json
import numpy as np

# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt, os, fnmatch
from matplotlib.backends.backend_pdf import PdfPages

class MeasurementCollector:
    """
    This class defines a collector that takes measurements and parameters from several nodes involved in the
    experiment and takes the most appropriate actions in answer to the collected values. Beware, this have a
    network-wide view, unlike any single node that has a local view.
    """

    def __init__(self, mytestbed, log):
        self.mytestbed = mytestbed
        self.log = log
        self.measurement_types = []

    def column(self, matrix, i):
        return [row[i] for row in matrix]

    def collect_values_from_nodes(self, nodes, node_list, measurement_types, ucallback=None, sampling_time=0, reporting_period=0, iterations=1):
        """ Defines the function that is called when a bunch of measurements are received from nodes.
            Than, executes the UPI_R.getMonitorBounce function on nodes, passed by argument.

        :param nodes: list of WiFiNode.
        :param node_list: list of Node.
        :param measurement_types: list of measurements name.
        :param ucallback: user-defined callback to be called after any reporting period
        :param sampling_time: the sampling time in [us] which the measurement is taken in the NIC
        :param reporting_period: period in [us] between two consecutive measurement reporting
        :param iterations: number of consecutive measurement reporting
        """

        res_measurements = []

        def monitorCallback(json_message):
            """  Is called when a bunch of measurements are received from nodes.
                 Extracts the ip address of the sender node and uses it to find appropriate object in WiFiNode list.
                 Stores the bunch of measurements in last_bunch_measurement WiFinode attribute.

            :param json_message: message received from node every iterations.
            """

            time_val = json_message['time']
            peer_node = json_message['peer']
            messagedata = json_message['msg']
            callback_id = json_message['callbackId']
            res_measurements.append(1)

            # add every response in a wifinode element
            for node in nodes:
                if node.getIpAddress() == callback_id.split('//')[1].split(':')[0] and messagedata != False:
                    node.last_bunch_measurement.append(messagedata)

            # call user-defined callback (the controller logic)
            ucallback(messagedata)

            return

        self.log.info('CALL getMonitor bunch  ....')
        now = get_now_full_second()
        UPIfunc = UPI_RN.getMonitorBounce
        UPIargs = {'measurements': measurement_types, 'slot_period': sampling_time, 'frame_period': reporting_period,
                   'interface': 'wlan0', 'iterator': iterations}
        print "UPIargs are ", UPIargs

        exec_time = now + timedelta(seconds=2)
        callback = monitorCallback
        try:
            self.mytestbed.global_mgr.runAt(node_list, UPIfunc, UPIargs, unix_time_as_tuple(exec_time), callback)
        except Exception as e:
            self.log.warning("An error occurred (e.g. scheduling events in the past): %s" % e)

        # plot data
        self.measurement_types = measurement_types

        return

    def clear_nodes_measurements(self, nodes):
        """ Clear all the measurement stored in WiFiNode object.
            The measurements are stored in the last_bunch_measurement attribute of WiFiNode class.

        :param nodes: list of WiFiNode.
        """
        for node in nodes:
            node.last_bunch_measurement = []
        return

    def plot_last_measurements(self, nodes, measurement_types, plot_title, plot_directory):
        """ Uses matplotlib library to plot all the measurements stored in WiFiNode object.
            The measurements are stored in the last_bunch_measurement attribute of WiFiNode class.

        :param nodes: list of WiFiNode.
        :param measurement_types: list of measurements name.
        :param plot_title: the title to write on graphic plot.
        """

        def show_plot(nodes, measurement_types, plot_title, plot_directory):

            out_measure={};
	    #measurement_types=['FREEZING_NUMBER', 'CW', 'TSF','IPT', 'TX_DATA', 'RX_ACK', 'RX_ACK_RAMATCH', 'NUM_RX_MATCH']
	    measurement_types=['FREEZING_NUMBER', 'TSF', 'RX_ACK_RAMATCH', 'CW', 'IPT', 'TX_DATA', 'RX_ACK', 'BUSY_TIME', 'delta_TSF', 'NUM_RX_MATCH']

            for node in nodes[0]:
                self.log.info("node : %s - measurements : %s" % (str(node), node.last_bunch_measurement))
            for node in nodes[1]:
                self.log.info("node : %s - measurements : %s" % (str(node), node.last_bunch_measurement))
            for node in nodes[2]:
                self.log.info("node : %s - measurements : %s" % (str(node), node.last_bunch_measurement))


	    #save experiments log
            with open('measure.json', 'w') as outfile:
                for node in nodes[0]:
                    self.log.warning("DOMENCIO : %s" % str(node.getIpAddress()))
                    out_measure.update({node.getIpAddress() : node.last_bunch_measurement});

                for node in nodes[1]:
                    out_measure.update({node.getIpAddress() : node.last_bunch_measurement});

                for node in nodes[2]:
                    out_measure.update({node.getIpAddress() : node.last_bunch_measurement});

                json.dump(out_measure, outfile)



	    #get experiment log
            with open('measure.json') as data_file:
                data = json.load(data_file)

            #for node in data.keys():
            for node in list(sort(data.keys())):
            
                    nodeIp=node;
                    x = array(data.get(nodeIp));
                    dim = x.shape
                    figure_id = 0
                    xaxis = []
            
                    if len(dim) > 2:
                            number_type_measurements = dim[2]
                    else:
                            number_type_measurements = 1
            
                    if number_type_measurements > 1 :
                            for meas_type_id in range(number_type_measurements):
                                    if measurement_types[meas_type_id] == "TSF" :
                                            min_TSF=np.min(x[:,0,meas_type_id])
                                            for ii in range(dim[0]):
                                                    for jj in range(dim[1]):
                                                            xaxis.append(x[ii][jj][meas_type_id])
            
                    for meas_type_id in range(number_type_measurements):
                            if not ((measurement_types[meas_type_id] == "TSF") and (number_type_measurements > 1)) :
                                    my_dpi=100
                                    width=1024
                                    height=768
            
                                    yaxis = []
                                    figure_id += 1
            
                                    #if nodeIp=="10.8.8.102" :
                                    #if nodeIp=="10.8.8.102" or nodeIp=="10.8.8.105" or nodeIp=="10.8.8.107" or nodeIp=="10.8.8.110" or nodeIp=="10.8.8.111" or nodeIp=="10.8.8.112" or nodeIp=="10.8.8.113" or nodeIp=="10.8.8.114" or nodeIp=="10.8.8.5":
                                    if nodeIp=="10.8.8.102" or nodeIp=="10.8.8.105" or nodeIp=="10.8.8.107" or nodeIp=="10.8.8.110" or nodeIp=="10.8.8.111" or nodeIp=="10.8.8.112" or nodeIp=="10.8.8.113" or nodeIp=="10.8.8.114" or nodeIp=="10.8.8.5":

                                            print " node : " + nodeIp + " ( plot --> " + measurement_types[meas_type_id] + " )"
                                            for ii in range(dim[0]):
                                                    for jj in range(dim[1]):
                                                            yaxis.append(x[ii][jj][meas_type_id])
            
                                            fig=plt.figure(figure_id)
                                            ax = fig.add_subplot(111)
                                            #if nodeIp=="10.8.8.105" or nodeIp=="10.8.8.107" or nodeIp=="10.8.8.110":
                                            #if nodeIp!="10.8.8.102":
                                            nodeIp_label=nodeIp.replace("10.8.8.","sta")
                                            ax.plot((xaxis-min_TSF)/1e6,yaxis,label=nodeIp_label);
                                            ax.grid(True)
                                            ax.set_xlim([0, (np.max(xaxis)-np.min(xaxis))/1e6])
                                            if (measurement_types[meas_type_id] == "IPT"):
                                                    ax.set_ylim([0, 25])
            
                                            if (measurement_types[meas_type_id] == "TX_DATA"):
                                                    ax.set_ylim([0, 400])
            
                                            if (measurement_types[meas_type_id] == "RX_ACK"):
                                                    ax.set_ylim([0, 400])
            
                                            if (measurement_types[meas_type_id] == "RX_ACK_RAMATCH"):
                                                    ax.set_ylim([0, 400])
            
                                            if (measurement_types[meas_type_id] == "BUSY_TIME"):
                                                    ax.set_ylim([0, 150000])
            
                                            if (measurement_types[meas_type_id] == "NUM_RX_MATCH"):
                                                    ax.set_ylim([0, 400])

                                            fig.set_size_inches(width/my_dpi,height/my_dpi)
                                            plt.tight_layout()
                                            legend = ax.legend()

                                            #plt.show()
                                            fig_filename="%s/fig_%s.pdf" % (plot_directory, measurement_types[meas_type_id])
                                            ax.set_ylabel(measurement_types[meas_type_id]);
                                            ax.set_xlabel('time [s]')
                                            fig.savefig(fig_filename, format='pdf')


        self.log.info("*********** Plot measurement *************")
        p = multiprocessing.Process(target=show_plot, args=(nodes, measurement_types, plot_title, plot_directory))
        p.start()





    def generate_measurement_report(self, nodes, filename="experiment_report.pdf"):
        """ Uses matplotlib library to plot all the measurements stored in WiFiNode object.
            Uses PdfPages to create a pdf with graphical plot.
            The measurements are stored in the last_bunch_measurement attribute of WiFiNode class.

        :param nodes: list of WiFiNode.
        :param filename: file name of the pdf report.
        """
        if self.measurement_types == None:
            self.log.info("no measurement to include in the report. Report has not been created!")
            return
        for node in nodes:
            self.log.info("node : %s - measurements : %s" % (str(node), node.last_bunch_measurement))
            if node.last_bunch_measurement == []:
                self.log.info("no measurement to include in the report. Report has not been created!")
                return

        with PdfPages(filename) as pdf:
            cover = plt.figure(0)
            textstring = "WiSHFUL experiment report \n" \
                         "Experiment finished at \n " \
                         " " + strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

            cover.text(0.5, 0.5, textstring,
                       fontweight='bold',
                       verticalalignment='center',
                       horizontalalignment='center',
                       color='green', fontsize=15)
            pdf.savefig(cover)

            for node in nodes:
                x = array(node.last_bunch_measurement)
                dim = x.shape
                figure_id = 1
                xaxis = []

                for meas_type_id in range(dim[2]):
                    if self.measurement_types[meas_type_id] == "TSF" :
                        for ii in range(dim[0]):
                            for jj in range(dim[1]):
                                xaxis.append(x[ii][jj][meas_type_id])

                for meas_type_id in range(dim[2]):
                    if self.measurement_types[meas_type_id] != "TSF" :
                        yaxis = []
                        figure_id += 1
                        for ii in range(dim[0]):
                            for jj in range(dim[1]):
                                yaxis.append(x[ii][jj][meas_type_id])
                        plt.figure(figure_id)
                        plt.plot(xaxis, yaxis)
                        plt.title(self.measurement_types[meas_type_id])
                        plt.grid()
                        plt.draw()
                        time.sleep(1)
                        pdf.savefig(cover)
            plt.show()

        return
