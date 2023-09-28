#!/usr/bin/python
__author__ = "Pierluigi Gallo, Domenico Garlisi"
__copyright__ = "Copyright (c) 2016, CNIT"
__version__ = "0.1.0"
__email__ = "domenico.garlisi@cnit.it"

"""
EU project WISHFUL
"""

import sys
import subprocess
import time
import multiprocessing
from time import gmtime, strftime
from numpy import *
from datetime import datetime, date, timedelta
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
        self.measurements_types = []


    def clear_nodes_measurements(self, nodes):
        """ Clear all the measurement stored in WiFiNode object.
            The measurements are stored in the measurements attribute of WiFiNode class.

        :param nodes: list of WiFiNode.
        """
        for node in nodes:
            node.measurements = []
        return


    def save_measurements(self, nodes, directory):
        """ This function extract measurement from measurements object attribute for each node and store them in a json
            file.

        :param nodes: list of WiFiNode.
        :param directory: directory in which store the json file.
        """

        out_measure={}
        #print nodes measurements
        for node in nodes:
            self.log.info("node : %s - measurements : %s" % (str(node), node.measurements))

        file_path = directory + '/measure.json'
        #save experiments measurements
        with open(file_path, 'w') as outfile:
            for node in nodes:
                out_measure.update({node.wlan_ipAddress : node.measurements})
            json.dump(out_measure, outfile)
        return


    def generate_measurement_report(self, nodes, filename="experiment_report.pdf"):
        """ Uses matplotlib library to plot all the measurements stored in WiFiNode object.
            Uses PdfPages to create a pdf with graphical plot.
            The measurements are stored in the measurements attribute of WiFiNode class.

        :param nodes: list of WiFiNode.
        :param filename: file name of the pdf report.
        """
        if self.measurements_types == None:
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
                    if self.measurements_types[meas_type_id] == "TSF" :
                        for ii in range(dim[0]):
                            for jj in range(dim[1]):
                                xaxis.append(x[ii][jj][meas_type_id])

                for meas_type_id in range(dim[2]):
                    if self.measurements_types[meas_type_id] != "TSF" :
                        yaxis = []
                        figure_id += 1
                        for ii in range(dim[0]):
                            for jj in range(dim[1]):
                                yaxis.append(x[ii][jj][meas_type_id])
                        plt.figure(figure_id)
                        plt.plot(xaxis, yaxis)
                        plt.title(self.measurements_types[meas_type_id])
                        plt.grid()
                        plt.draw()
                        time.sleep(1)
                        pdf.savefig(cover)
            plt.show()

        return
