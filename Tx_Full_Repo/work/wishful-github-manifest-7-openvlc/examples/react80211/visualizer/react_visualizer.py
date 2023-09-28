__author__ = 'domenico'

from Tkinter import *
from PIL import Image, ImageTk

import random
from socket import *    # import *, but we'll avoid name conflict
from sys import argv, exit
import demjson
import json

import subprocess
#import webbrowser
import urllib2
import base64
import StringIO
import io
import urllib
import zmq
from urllib2 import urlopen, Request, URLError
import time
from thread import start_new_thread
import ttk


SUNKABLE_BUTTON1 = 'SunkableButton.TButton'
SUNKABLE_BUTTON2 = 'SunkableButton.TButton'
SUNKABLE_BUTTON3 = 'SunkableButton.TButton'

DELAY = 1000

class Adder(ttk.Frame):
    """The adders gui and functions."""
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.init_gui()

    def on_quit(self):
        """Exits program."""
        quit()

    def calculate(self):
        """Calculates the sum of the two inputted numbers."""
        num1 = int(self.num1_entry.get())
        num2 = int(self.num2_entry.get())
        num3 = num1 + num2
        self.answer_label['text'] = num3

    def centreWindow(self):
        w = 1500
        h = 800
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        #x = (sw - w)/2
        #y = (sh - h)/2
        x = (sw - w)
        y = (sh - h)
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def selectTopologyImage1(self):
        image_name = 'wilab2-topology-1.png'
        img=Image.open(image_name)
        wpercent=100
        basewidth = 490
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        im = ImageTk.PhotoImage(img)

        self.label_topo_img = Label(self.topo_frame, image=im)
        self.label_topo_img.image = im
        self.label_topo_img.grid(row=0, column=0, sticky='nesw')


    def selectTopologyImage2(self):
        image_name = 'wilab2-topology-2bis.png'
        img=Image.open(image_name)
        wpercent=100
        basewidth = 490
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        im = ImageTk.PhotoImage(img)

        self.label_topo_img = Label(self.topo_frame, image=im)
        self.label_topo_img.image = im
        self.label_topo_img.grid(row=0, column=0, sticky='nesw')

    def selectTopologyImagePortableTestbed(self):
        image_name = 'ptestbed-review-topology.png'
        img=Image.open(image_name)
        wpercent=100
        basewidth = 490
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        im = ImageTk.PhotoImage(img)

        self.label_topo_img = Label(self.topo_frame, image=im)
        self.label_topo_img.image = im
        self.label_topo_img.grid(row=0, column=0, sticky='nesw')

    def stopReact(self):
        command = 'stop_react'
        json_command = {'type': 'algorithm', 'command': command}
        print(json_command)
        if self.local_network:
            self.socket_command_local_network.send_json(json_command)
        else:
            self.socket_command_remote_network.send_json(json_command)

        self.stopReactBtn.state(['pressed', 'disabled'])
        self.style.configure(SUNKABLE_BUTTON1, relief=SUNKEN, foreground='red')

        self.startReactBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON2, relief=RAISED, foreground='green')

    def startReact(self):
        command = 'start_react'
        json_command = {'type': 'algorithm', 'command': command}
        print(json_command)
        if self.local_network:
            self.socket_command_local_network.send_json(json_command)
        else:
            self.socket_command_remote_network.send_json(json_command)

        self.startReactBtn.state(['pressed', 'disabled'])
        self.style.configure(SUNKABLE_BUTTON2, relief=SUNKEN, foreground='red')

        self.stopReactBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON1, relief=RAISED, foreground='green')


    def setTraffic(self, src, val):
        val = int(val)
        if src == 'A':
            dst = self.countryVarA.get()
            if 500 < val and val <= 6000:
                self.sta1val_traffic_activation = True
            else:
                self.sta1val_traffic_activation = False
        elif src == 'B':
            dst = self.countryVarB.get()
            if 500 < val and val <= 6000:
                self.sta2val_traffic_activation = True
            else:
                self.sta2val_traffic_activation = False
        elif src == 'C':
            dst = self.countryVarC.get()
            if 500 < val and val <= 6000:
                self.sta3val_traffic_activation = True
            else:
                self.sta3val_traffic_activation = False
        elif src == 'D':
            dst = self.countryVarD.get()
            if 500 < val and val <= 6000:
                self.sta4val_traffic_activation = True
            else:
                self.sta4val_traffic_activation = False
        elif src == 'E':
            dst = self.countryVarE.get()
            if 500 < val and val <= 6000:
                self.sta5val_traffic_activation = True
            else:
                self.sta5val_traffic_activation = False
        elif src == 'F':
            dst = self.countryVarF.get()
            if 500 < val and val <= 6000:
                self.sta6val_traffic_activation = True
            else:
                self.sta6val_traffic_activation = False
        else:
            print('bad source node')
            return

        if 500 < val and val <= 6000:
            command = 'set_traffic'
            round_val = round(val/1000)*1000
            if (val - round_val) > 500 :
                round_val += 1000
            self.command_list = {'type': 'traffic', 'command': command, 'src' : src, 'dst' : dst, 'value' : round_val}
        else:
            round_val = 0
            command = 'off_traffic'
            self.command_list = {'type': 'traffic', 'command': command, 'src' : src, 'dst' : dst}

        self.last_traffic_update_time = time.time()
        self.traffic_update_command = self.command_list

        print(self.command_list)
        #self.socket_command.send_json(self.command_list)

    def traffic_command_handles(self,x):
        while True:
            if time.time() - self.last_traffic_update_time > 1.3 and self.traffic_update_command != self.last_traffic_update_command:
                print('command sent %s' % str(self.command_list))
                if self.local_network:
                    self.socket_command_local_network.send_json(self.command_list)
                else:
                    self.socket_command_remote_network.send_json(self.command_list)
                self.last_traffic_update_time = time.time()
                self.last_traffic_update_command = self.traffic_update_command
                self.LabelTraffic.config(text="Select nodes traffic : (UPI executed!)")

            time.sleep(1)
            self.LabelTraffic.config(text="Select nodes traffic : ")

    line1_psucc = None
    line2_psucc = None
    line3_psucc = None
    line4_psucc = None
    line5_psucc = None
    line6_psucc = None
    figure_psucc = None
    def plotpsucc(self,x):
        global line1_psucc
        global line2_psucc
        global line3_psucc
        global line4_psucc
        global line5_psucc
        global line6_psucc
        global figure_psucc
        init = 1
        while True:
            if init:
                try:
                    import matplotlib.pyplot as plt
                    import matplotlib
                    matplotlib.use("TkAgg")
                    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
                    from matplotlib.figure import Figure
                    import numpy
                    from matplotlib import rcParams
                    rcParams.update({'figure.autolayout': True})

                    plt.ion()
                    figure_psucc = Figure()
                    figure_psucc.set_facecolor('white')
                    ax = figure_psucc.add_subplot(111)

                    # self.yval.append( numpy.nan_to_num( stats.get('psucc') ) )
                    # yy=self.yval[::-1]
                    # yy=yy[0:self.Nplot]
                    # self.yval=yy[::-1]
                    ax.grid(True)
                    ax.set_xlabel('Time [s]', fontsize=12)
                    ax.set_ylabel('Success probability')

                    line1_psucc, = ax.plot(self.xval_psucc, self.sta1val_psucc, label='Node A')
                    line2_psucc, = ax.plot(self.xval_psucc, self.sta2val_psucc, label='Node B')
                    line3_psucc, = ax.plot(self.xval_psucc, self.sta3val_psucc, label='Node C')
                    line4_psucc, = ax.plot(self.xval_psucc, self.sta4val_psucc, label='Node D')
                    line5_psucc, = ax.plot(self.xval_psucc, self.sta5val_psucc, label='Node E')
                    line6_psucc, = ax.plot(self.xval_psucc, self.sta6val_psucc, label='Node F')

                    ax.set_ylim([-0.05, 1.05])
                    ax.patch.set_facecolor('white')
                    #legend = ax.legend(loc='upper center', shadow=True, ncol=3)

                    my_dpi = self.my_dpi
                    width = self.width
                    height = self.height
                    figure_psucc.set_size_inches(width/my_dpi, height/my_dpi)

                    canvas = FigureCanvasTkAgg(figure_psucc, self.statistics_psucc_frame)
                    canvas.show()
                    canvas.get_tk_widget().configure(background='white',  highlightcolor='white', highlightbackground='white')
                    canvas.get_tk_widget().grid(column=0, row=0, columnspan=1, sticky='nesw')

                except Exception as e:
                    print e
                    pass

                init = 0

            else:
                line1_psucc.set_ydata(self.sta1val_psucc)
                line2_psucc.set_ydata(self.sta2val_psucc)
                line3_psucc.set_ydata(self.sta3val_psucc)
                line4_psucc.set_ydata(self.sta4val_psucc)
                line5_psucc.set_ydata(self.sta5val_psucc)
                line6_psucc.set_ydata(self.sta6val_psucc)
                figure_psucc.canvas.draw()
            time.sleep(1)


    line1_airtime = None
    line2_airtime = None
    line3_airtime = None
    line4_airtime = None
    line5_airtime = None
    line6_airtime = None
    figure_airtime = None
    def plotairtime(self,x):
        global line1_airtime
        global line2_airtime
        global line3_airtime
        global line4_airtime
        global line5_airtime
        global line6_airtime
        global figure_airtime
        init = 1
        while True:
            if init:
                try:
                    import matplotlib.pyplot as plt
                    import matplotlib
                    matplotlib.use("TkAgg")
                    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
                    from matplotlib.figure import Figure
                    import numpy
                    from matplotlib import rcParams
                    rcParams.update({'figure.autolayout': True})

                    plt.ion()
                    figure_airtime = Figure()
                    figure_airtime.set_facecolor('white')
                    ax = figure_airtime.add_subplot(111)

                    # self.yval.append( numpy.nan_to_num( stats.get('airtime') ) )
                    # yy=self.yval[::-1]
                    # yy=yy[0:self.Nplot]
                    # self.yval=yy[::-1]
                    ax.grid(True)
                    ax.set_xlabel('Time [s]', fontsize=12)
                    ax.set_ylabel('Airtime')

                    line1_airtime, = ax.plot(self.xval_airtime, self.sta1val_airtime, label='Node A')
                    line2_airtime, = ax.plot(self.xval_airtime, self.sta2val_airtime, label='Node B')
                    line3_airtime, = ax.plot(self.xval_airtime, self.sta3val_airtime, label='Node C')
                    line4_airtime, = ax.plot(self.xval_airtime, self.sta4val_airtime, label='Node D')
                    line5_airtime, = ax.plot(self.xval_airtime, self.sta5val_airtime, label='Node E')
                    line6_airtime, = ax.plot(self.xval_airtime, self.sta6val_airtime, label='Node F')

                    labels = ['',  '0.0', '', '0.5', '', '1', '']
                    # set the tick labels
                    ax.set_yticklabels(labels, rotation=0)

                    ax.set_ylim([-0.05, 0.85])
                    ax.patch.set_facecolor('white')
                    #legend = ax.legend(loc='upper center', shadow=True, ncol=3)

                    my_dpi = self.my_dpi
                    width = self.width
                    height = self.height
                    figure_airtime.set_size_inches(width/my_dpi,height/my_dpi)
                    canvas = FigureCanvasTkAgg(figure_airtime, self.statistics_airtime_frame)
                    canvas.show()
                    canvas.get_tk_widget().configure(background='white',  highlightcolor='white', highlightbackground='white')
                    canvas.get_tk_widget().grid(column=0, row=0, columnspan=1, sticky='nesw')

                except Exception as e:
                    print e
                    pass

                init = 0

            else:
                line1_airtime.set_ydata(self.sta1val_airtime)
                line2_airtime.set_ydata(self.sta2val_airtime)
                line3_airtime.set_ydata(self.sta3val_airtime)
                line4_airtime.set_ydata(self.sta4val_airtime)
                line5_airtime.set_ydata(self.sta5val_airtime)
                line6_airtime.set_ydata(self.sta6val_airtime)
                figure_airtime.canvas.draw()

            time.sleep(1)


    line1_cw = None
    line2_cw = None
    line3_cw = None
    line4_cw = None
    line5_cw = None
    line6_cw = None
    figure_cw = None
    def plotcw(self,x):
        global line1_cw
        global line2_cw
        global line3_cw
        global line4_cw
        global line5_cw
        global line6_cw
        global figure_cw
        init = 1
        while True:
            if init:
                try:
                    import matplotlib.pyplot as plt
                    import matplotlib
                    matplotlib.use("TkAgg")
                    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
                    from matplotlib.figure import Figure
                    import numpy
                    from matplotlib import rcParams
                    rcParams.update({'figure.autolayout': True})

                    plt.ion()
                    figure_cw = Figure()
                    figure_cw.set_facecolor('white')
                    ax = figure_cw.add_subplot(111)

                    # self.yval.append( numpy.nan_to_num( stats.get('cw') ) )
                    # yy=self.yval[::-1]
                    # yy=yy[0:self.Nplot]
                    # self.yval=yy[::-1]
                    ax.grid(True)
                    ax.set_xlabel('Time [s]', fontsize=12)
                    ax.set_ylabel('Contention window')

                    line1_cw, = ax.semilogy(self.xval_cw, self.sta1val_cw, label='Node A')
                    line2_cw, = ax.semilogy(self.xval_cw, self.sta2val_cw, label='Node B')
                    line3_cw, = ax.semilogy(self.xval_cw, self.sta3val_cw, label='Node C')
                    line4_cw, = ax.semilogy(self.xval_cw, self.sta4val_cw, label='Node D')
                    line5_cw, = ax.semilogy(self.xval_cw, self.sta5val_cw, label='Node E')
                    line6_cw, = ax.semilogy(self.xval_cw, self.sta6val_cw, label='Node F')

                    # line1_cw, = ax.plot(self.xval_cw, self.sta1val_cw, label='Node A')
                    # line2_cw, = ax.plot(self.xval_cw, self.sta2val_cw, label='Node B')
                    # line3_cw, = ax.plot(self.xval_cw, self.sta3val_cw, label='Node C')
                    # line4_cw, = ax.plot(self.xval_cw, self.sta4val_cw, label='Node D')
                    # line5_cw, = ax.plot(self.xval_cw, self.sta5val_cw, label='Node E')
                    # line6_cw, = ax.plot(self.xval_cw, self.sta6val_cw, label='Node F')

                    ax.set_ylim([10, 10000])
                    ax.patch.set_facecolor('white')
                    legend = ax.legend(loc='upper center', shadow=True, ncol=3)

                    my_dpi = self.my_dpi
                    width = self.width
                    height = self.height
                    figure_cw.set_size_inches(width/my_dpi,height/my_dpi)
                    canvas = FigureCanvasTkAgg(figure_cw, self.statistics_cw_frame)
                    canvas.show()
                    canvas.get_tk_widget().configure(background='white',  highlightcolor='white', highlightbackground='white')
                    canvas.get_tk_widget().grid(column=0, row=0, columnspan=1, sticky='nesw')

                except Exception as e:
                    print e
                    pass

                init = 0

            else:
                line1_cw.set_ydata(self.sta1val_cw)
                line2_cw.set_ydata(self.sta2val_cw)
                line3_cw.set_ydata(self.sta3val_cw)
                line4_cw.set_ydata(self.sta4val_cw)
                line5_cw.set_ydata(self.sta5val_cw)
                line6_cw.set_ydata(self.sta6val_cw)
                figure_cw.canvas.draw()
            time.sleep(1)




    #*****************
    #reveive data plot from controller
    #*****************
    def receive_data_plot(self,x):

         # use poll for timeouts:
        poller = zmq.Poller()
        poller.register(self.socket_plot_local_network, zmq.POLLIN)
        poller.register(self.socket_plot_remote_network, zmq.POLLIN)

        while True:    # Run until cancelled
            socks = dict(poller.poll(1000))
            if self.socket_plot_local_network in socks:
                parsed_json = self.socket_plot_local_network.recv_json()
                if not self.local_network:
                    continue
            elif self.socket_plot_remote_network in socks:
                parsed_json = self.socket_plot_remote_network.recv_json()
                if self.local_network:
                    continue
            else:
                continue

            print('parsed_json : %s' % str(parsed_json))
            #parsed_json : {u'label': u'C', u'measure': [[1484644417.3528204, 0.0, 0.0, 1.0, 0.0, 1023, 0, 0]], u'mac_address': u'00:0e:8e:30:9d:ee'}
            label = parsed_json['label']
            if label :
                measure = parsed_json['measure'][0]
                if float(measure[8]) > 100:
                    measure[8] = 100

                if label == 'A':
                    item = 'I001'

                    # if not self.sta1val_traffic_activation:
                    #     measure[5] = 0
                    #     measure[6] = 0

                    self.sta1val_cw.pop(0)
                    self.sta1val_cw.append( float(measure[5]) )

                    self.sta1val_psucc.pop(0)
                    self.sta1val_psucc.append( float(measure[6]) )

                    self.sta1val_airtime.pop(0)
                    self.sta1val_airtime.append( float(measure[7]) )

                    self.LabelBusyA.config(text="{}%".format(float(measure[8])))

                    #self.sta1_log_Label.config(text="STA1 PROTOCOL={}".format(float(measure[1]) + 1))

                elif label == 'B':
                    item = 'I002'

                    # if not self.sta2val_traffic_activation:
                    #     measure[5] = 0
                    #     measure[6] = 0

                    self.sta2val_cw.pop(0)
                    self.sta2val_cw.append( float(measure[5]) )

                    self.sta2val_psucc.pop(0)
                    self.sta2val_psucc.append( float(measure[6]) )

                    self.sta2val_airtime.pop(0)
                    self.sta2val_airtime.append( float(measure[7]) )

                    self.LabelBusyB.config(text="{}%".format(float(measure[8])))

                elif label == 'C':
                    item = 'I003'

                    # if not self.sta3val_traffic_activation:
                    #     measure[5] = 0
                    #     measure[6] = 0

                    self.sta3val_cw.pop(0)
                    self.sta3val_cw.append( float(measure[5]) )

                    self.sta3val_psucc.pop(0)
                    self.sta3val_psucc.append( float(measure[6]) )

                    self.sta3val_airtime.pop(0)
                    self.sta3val_airtime.append( float(measure[7]) )

                    self.LabelBusyC.config(text="{}%".format(float(measure[8])))


                elif label == 'D':
                    item = 'I004'

                    if not self.sta4val_traffic_activation:
                        measure[5] = 0
                        measure[6] = 0

                    self.sta4val_cw.pop(0)
                    self.sta4val_cw.append( float(measure[5]) )

                    self.sta4val_psucc.pop(0)
                    self.sta4val_psucc.append( float(measure[6]) )

                    self.sta4val_airtime.pop(0)
                    self.sta4val_airtime.append( float(measure[7]) )

                    self.LabelBusyD.config(text="{}%".format(float(measure[8])))


                elif label == 'E':
                    item = 'I005'

                    if not self.sta5val_traffic_activation:
                        measure[5] = 0
                        measure[6] = 0

                    self.sta5val_cw.pop(0)
                    self.sta5val_cw.append( float(measure[5]) )

                    self.sta5val_psucc.pop(0)
                    self.sta5val_psucc.append( float(measure[6]) )

                    self.sta5val_airtime.pop(0)
                    self.sta5val_airtime.append( float(measure[7]) )

                    self.LabelBusyE.config(text="{}%".format(float(measure[8])))


                elif label == 'F':
                    item = 'I006'

                    if not self.sta6val_traffic_activation:
                        measure[5] = 0
                        measure[6] = 0

                    self.sta6val_cw.pop(0)
                    self.sta6val_cw.append( float(measure[5]) )

                    self.sta6val_psucc.pop(0)
                    self.sta6val_psucc.append( float(measure[6]) )

                    self.sta6val_airtime.pop(0)
                    self.sta6val_airtime.append( float(measure[7]) )

                    self.LabelBusyF.config(text="{}%".format(float(measure[8])))


                else:
                    print('Error in plot receive, wrong label present')
                    continue

                self.tv.item(item, text=label, values=(round(measure[1]*100)/100, round(measure[2]*100)/100, round(measure[3]*100)/100))
            else:
                print('Error in plot receive, no label present')

    def select_ptestbed(self):
        self.local_network = 0
        print('switch to portable testbed')


    def select_wilab2(self):
        self.local_network = 1
        print('switch to wilab')


    def init_gui(self):

        #VISUALIZER CONFIGURATION
        self.Nplot=100

        self.my_dpi = 100
        self.width = 600
        self.height = 400

        self.last_traffic_update_time = time.time()
        self.last_traffic_update_command = None
        self.traffic_update_command = None

        #traffic active
        self.sta1val_traffic_activation = False
        self.sta2val_traffic_activation = False
        self.sta3val_traffic_activation = False
        self.sta4val_traffic_activation = False
        self.sta5val_traffic_activation = False
        self.sta6val_traffic_activation = False

        #psucc
        self.sta1val_psucc=[1 for x in range(0,self.Nplot)]
        self.sta2val_psucc=[2 for x in range(0,self.Nplot)]
        self.sta3val_psucc=[3 for x in range(0,self.Nplot)]
        self.sta4val_psucc=[4 for x in range(0,self.Nplot)]
        self.sta5val_psucc=[4 for x in range(0,self.Nplot)]
        self.sta6val_psucc=[4 for x in range(0,self.Nplot)]
        self.xval_psucc=[x for x in range(-self.Nplot, 0)]

        #airtime
        self.sta1val_airtime=[1 for x in range(0,self.Nplot)]
        self.sta2val_airtime=[2 for x in range(0,self.Nplot)]
        self.sta3val_airtime=[3 for x in range(0,self.Nplot)]
        self.sta4val_airtime=[4 for x in range(0,self.Nplot)]
        self.sta5val_airtime=[4 for x in range(0,self.Nplot)]
        self.sta6val_airtime=[4 for x in range(0,self.Nplot)]
        self.xval_airtime=[x for x in range(-self.Nplot, 0)]

        #cw
        self.sta1val_cw=[1 for x in range(0,self.Nplot)]
        self.sta2val_cw=[2 for x in range(0,self.Nplot)]
        self.sta3val_cw=[3 for x in range(0,self.Nplot)]
        self.sta4val_cw=[4 for x in range(0,self.Nplot)]
        self.sta5val_cw=[4 for x in range(0,self.Nplot)]
        self.sta6val_cw=[4 for x in range(0,self.Nplot)]
        self.xval_cw=[x for x in range(-self.Nplot, 0)]


        #NETWORK SOCKET SETUP
        print('Network socket setup')
        self.command_list = {}
        self.local_network = 1

        #connect to the wilabtestbed
        self.socket_command_local_network_port = 8500
        self.context1_local_network = zmq.Context()
        print("Connecting to server on port 8500 ... ready to send command to demo experiment node")
        self.socket_command_local_network = self.context1_local_network.socket(zmq.PAIR)
        self.socket_command_local_network.connect ("tcp://localhost:%s" % self.socket_command_local_network_port)

        self.socket_plot_local_network_port  = 8501
        self.context2__local_network = zmq.Context()
        print("Connecting to server on port 8501 ... ready to receive protocol information from demo experiment node")
        self.socket_plot_local_network = self.context2__local_network.socket(zmq.SUB)
        self.socket_plot_local_network.connect ("tcp://localhost:%s" % self.socket_plot_local_network_port)
        self.socket_plot_local_network.setsockopt(zmq.SUBSCRIBE, '')

        #connect to the portable testbed
        self.socket_command_remote_network_port = 8600
        self.context1_remote_network = zmq.Context()
        print("Connecting to server on port 8600 ... ready to send command to demo experiment node")
        self.socket_command_remote_network = self.context1_remote_network.socket(zmq.PAIR)
        self.socket_command_remote_network.connect ("tcp://localhost:%s" % self.socket_command_remote_network_port)

        self.socket_plot_remote_network_port  = 8601
        self.context2_remote_network = zmq.Context()
        print("Connecting to server on port 8601 ... ready to receive protocol information from demo experiment node")
        self.socket_plot_remote_network = self.context2_remote_network.socket(zmq.SUB)
        self.socket_plot_remote_network.connect ("tcp://localhost:%s" % self.socket_plot_remote_network_port)
        self.socket_plot_remote_network.setsockopt(zmq.SUBSCRIBE, '')

        start_new_thread(self.receive_data_plot,(99,))


        """GUI SETUP"""
        print('GUI setup')
        self.root.title('WISHFUL DEMO YEAR 2')
        #self.root.option_add('*tearOff', 'FALSE')

        self.parent = self.root
        self.root.title("WISHFUL DEMO YEAR 2")
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.centreWindow()
        self.pack(fill=BOTH, expand=1)
        self.grid(column=0, row=0, sticky='nsew')

        self.menubar = Menu(self.root)
        #menu file
        self.menu_file = Menu(self.menubar)

        self.menu_file.add_command(label='PTESTBED', command=self.select_ptestbed)
        self.menu_file.add_command(label='WILAB2', command=self.select_wilab2)

        self.menu_file.add_command(label='Exit', command=self.on_quit)
        #menu edit topology
        self.menu_edit_topology = Menu(self.menubar)
        self.menu_edit_topology.add_command(label='Topology 1 w-iLab', command=self.selectTopologyImage1)
        self.menu_edit_topology.add_command(label='Topology 2 w-iLab', command=self.selectTopologyImage2)
        self.menu_edit_topology.add_command(label='Topology portable testbed', command=self.selectTopologyImagePortableTestbed)
        #show menu
        self.menubar.add_cascade(menu=self.menu_file, label='File')
        self.menubar.add_cascade(menu=self.menu_edit_topology, label='Topology')

        self.root.config(menu=self.menubar)

        #PLOT TOPOLOGY IMAGE
        self.topo_frame=ttk.LabelFrame(self, text="Network Scenario", height=50, width=50)
        self.topo_frame.grid(column=0, row=1, columnspan=1, sticky='nesw')

        #img=Image.open('topology-3full.png')
        #wpercent=50
        #basewidth = 350
        #img=Image.open('topology-3chain.png')
        #image_name = 'wilab2-map.png'
        image_name = 'wilab2-topology-2bis.png'
        img=Image.open(image_name)
        wpercent=100
        basewidth = 490
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        im = ImageTk.PhotoImage(img)

        self.label_topo_img = Label(self.topo_frame, image=im)
        self.label_topo_img.image = im
        self.label_topo_img.grid(row=0, column=0, sticky='nesw')


        img=Image.open('logo.png')
        wpercent=100
        basewidth = 490
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        im = ImageTk.PhotoImage(img)

        label_logo_img = Label(self.topo_frame, image=im)
        label_logo_img.image = im
        label_logo_img.grid(row=1,column=0, sticky=W+E)


        #TRAFFIC FRAME
        self.traffic_frame = ttk.LabelFrame(self, text='Traffic', height=50, width=50)
        self.traffic_frame.grid(column=1, row=1, columnspan=1, sticky='nesw')

        self.LabelTraffic = Label(self.traffic_frame, text="Selector nodes traffic")
        self.LabelTraffic.grid(row=0, column=0, columnspan=3, padx=1, pady=1, sticky=W)
        self.LabelBusy = Label(self.traffic_frame, text="busy-time")
        self.LabelBusy.grid(row=0, column=3, columnspan=1, padx=1, pady=1, sticky=W)

        #traffic node A
        self.LabelTrafficA = Label(self.traffic_frame, text="A --> ")
        self.LabelTrafficA.grid(row=1, column=0, padx=2, pady=2, sticky=W)
        self.countryVarA = StringVar()
        self.countryComboA = ttk.Combobox(self.traffic_frame, textvariable=self.countryVarA, width=5)
        self.countryComboA['values'] = ('B', 'C', 'D', 'E', 'F')
        self.countryComboA.current(0)
        self.countryComboA.grid(row=1, column=1, padx=2, pady=2, sticky=W)
        self.TrafficA = Scale(self.traffic_frame, from_=0, to=6000, length=300, resolution=1000, tickinterval=3000, orient='horizontal', command= lambda value, src='A': self.setTraffic(src, value))
        self.TrafficA.grid(row=1, column=2, padx=2, pady=2, sticky=W)
        self.LabelBusyA = Label(self.traffic_frame, text="0%", background='white')
        self.LabelBusyA.grid(row=1, column=3, padx=1, pady=1, sticky=W)

        #traffic node B
        self.LabelTrafficB = Label(self.traffic_frame, text="B --> ")
        self.LabelTrafficB.grid(row=2, column=0, padx=1, pady=1, sticky=W)

        self.countryVarB = StringVar()
        self.countryComboB = ttk.Combobox(self.traffic_frame, textvariable=self.countryVarB, width=5)
        self.countryComboB['values'] = ('A', 'C', 'D', 'E', 'F')
        self.countryComboB.current(0)
        self.countryComboB.grid(row=2, column=1, padx=2, pady=2, sticky=W)
        self.TrafficB = Scale(self.traffic_frame, from_=0, to=6000, length=300, resolution=1000, tickinterval=3000, orient='horizontal', command= lambda value, src='B': self.setTraffic(src, value))
        self.TrafficB.grid(row=2, column=2, padx=2, pady=2, sticky=W)
        self.LabelBusyB = Label(self.traffic_frame, text="0%", background='white')
        self.LabelBusyB.grid(row=2, column=3, padx=1, pady=1, sticky=W)

        # #traffic node C
        self.LabelTrafficC = Label(self.traffic_frame, text="C --> ")
        self.LabelTrafficC.grid(row=3, column=0, padx=1, pady=1, sticky=W)
        self.countryVarC = StringVar()
        self.countryComboC = ttk.Combobox(self.traffic_frame, textvariable=self.countryVarC, width=5)
        self.countryComboC['values'] = ('A', 'B', 'D', 'E', 'F')
        self.countryComboC.current(0)
        self.countryComboC.grid(row=3, column=1, padx=2, pady=2, sticky=W)
        self.TrafficC = Scale(self.traffic_frame, from_=0, to=6000, length=300, resolution=1000, tickinterval=3000, orient='horizontal', command= lambda value, src='C': self.setTraffic(src, value))
        self.TrafficC.grid(row=3, column=2, padx=2, pady=2, sticky=W)
        self.LabelBusyC = Label(self.traffic_frame, text="0%", background='white')
        self.LabelBusyC.grid(row=3, column=3, padx=1, pady=1, sticky=W)

        # #traffic node D
        self.LabelTrafficD = Label(self.traffic_frame, text="D --> ")
        self.LabelTrafficD.grid(row=4, column=0, padx=1, pady=1, sticky=W)
        self.countryVarD = StringVar()
        self.countryComboD = ttk.Combobox(self.traffic_frame, textvariable=self.countryVarD, width=5)
        self.countryComboD['values'] = ('A', 'B', 'C', 'E', 'F')
        self.countryComboD.current(0)
        self.countryComboD.grid(row=4, column=1, padx=2, pady=2, sticky=W)
        self.TrafficD = Scale(self.traffic_frame, from_=0, to=6000, length=300, resolution=1000, tickinterval=3000, orient='horizontal', command= lambda value, src='D': self.setTraffic(src, value))
        self.TrafficD.grid(row=4, column=2, padx=2, pady=2, sticky=W)
        self.LabelBusyD = Label(self.traffic_frame, text="0%", background='white')
        self.LabelBusyD.grid(row=4, column=3, padx=1, pady=1, sticky=W)

        # #traffic node E
        self.LabelTrafficE = Label(self.traffic_frame, text="E --> ")
        self.LabelTrafficE.grid(row=5, column=0, padx=1, pady=1, sticky=W)
        self.countryVarE = StringVar()
        self.countryComboE = ttk.Combobox(self.traffic_frame, textvariable=self.countryVarE, width=5)
        self.countryComboE['values'] = ('A', 'B', 'D', 'F', 'C')
        self.countryComboE.current(0)
        self.countryComboE.grid(row=5, column=1, padx=2, pady=2, sticky=W)
        self.TrafficE = Scale(self.traffic_frame, from_=0, to=6000, length=300, resolution=1000, tickinterval=3000, orient='horizontal', command= lambda value, src='E': self.setTraffic(src, value))
        self.TrafficE.grid(row=5, column=2, padx=2, pady=2, sticky=W)
        self.LabelBusyE = Label(self.traffic_frame, text="0%", background='white')
        self.LabelBusyE.grid(row=5, column=3, padx=1, pady=1, sticky=W)

        # #traffic node F
        self.LabelTrafficF = Label(self.traffic_frame, text="F --> ")
        self.LabelTrafficF.grid(row=6, column=0, padx=1, pady=1, sticky=W)
        self.countryVarF = StringVar()
        self.countryComboF = ttk.Combobox(self.traffic_frame, textvariable=self.countryVarF, width=5)
        self.countryComboF['values'] = ('A', 'B', 'C', 'D', 'E')
        self.countryComboF.current(0)
        self.countryComboF.grid(row=6, column=1, padx=2, pady=2, sticky=W)
        self.TrafficF = Scale(self.traffic_frame, from_=0, to=6000, length=300, resolution=1000, tickinterval=3000, orient='horizontal', command= lambda value, src='F': self.setTraffic(src, value))
        self.TrafficF.grid(row=6, column=2, padx=2, pady=2, sticky=W)
        self.LabelBusyF = Label(self.traffic_frame, text="0%", background='white')
        self.LabelBusyF.grid(row=6, column=3, padx=1, pady=1, sticky=W)

        #PROTOCOL INFORMATION
        self.stats_frame = ttk.LabelFrame(self, text='Monitor REACT values (Normalized)', height=50, width=50)
        self.stats_frame.grid(column=2, row=1, columnspan=1, sticky='nesw')

        self.tv = ttk.Treeview(self.stats_frame)
        self.tv['columns'] = ('starttime', 'endtime', 'status')
        self.tv.heading("#0", text='', anchor='w')
        self.tv.column("#0", anchor="w", width=50)
        self.tv.heading('starttime', text='SOURCE')
        self.tv.column('starttime', anchor='center', width=100)
        self.tv.heading('endtime', text='CLAIM')
        self.tv.column('endtime', anchor='center', width=100)
        self.tv.heading('status', text='OFFER')
        self.tv.column('status', anchor='center', width=100)
        self.tv.grid(row=0, column=0, columnspan=2, padx=5, pady=5, ipady=2, sticky ='nesw')

        self.tv.insert('', '0', text="A", values=('0', '0', '0'))
        self.tv.insert('', '1', text="B", values=('0', '0', '0'))
        self.tv.insert('', '2', text="C", values=('0', '0', '0'))
        self.tv.insert('', '3', text="D", values=('0', '0', '0'))
        self.tv.insert('', '4', text="E", values=('0', '0', '0'))
        self.tv.insert('', '5', text="F", values=('0', '0', '0'))

        # cells = self.tv.get_children()
        # for item in cells: ## Changing all children from root item
        #     print(item)

        #self.tv.item('I001', text="A", values=('1', '1', '1'))

        self.startReactBtn = ttk.Button(self.stats_frame, text="START REACT", width=10, command=lambda : self.startReact(),  style=SUNKABLE_BUTTON2)
        self.startReactBtn.grid(row=1, column=0, padx=5, pady=5, ipady=2, sticky='nesw')
        self.stopReactBtn = ttk.Button(self.stats_frame, text="STOP REACT", width=10, command=lambda : self.stopReact(),  style=SUNKABLE_BUTTON1)
        self.stopReactBtn.grid(row=1, column=1, padx=5, pady=5, ipady=2, sticky='nesw')

        self.LabelSourceDescription = Label(self.stats_frame, text="REACT algorithm: ")
        self.LabelSourceDescription.grid(row=2, column=0, columnspan=1, padx=1, pady=1, sticky=W)
        self.LabelClaimDescription = Label(self.stats_frame, justify=LEFT, text="Each node runs an auctioneer that maintains an offer,\n\
the maximum airtime consumed by any adjacent bidder.\n\
Similarly, each node also runs a bidder that maintains a claim, \n\
the airtime the bidder intends to consume at adjacent auctions.\n\
Through updates of offers and claims, the auctioneers and\n\
bidders converge on an allocation of airtime.")
        self.LabelClaimDescription.grid(row=3, column=0, columnspan=3, padx=1, pady=1, sticky='nesw')
        # self.LabelOfferDescription = Label(self.stats_frame, text="The OFFER ")
        # self.LabelOfferDescription.grid(row=4, column=0, columnspan=1, padx=1, pady=1, sticky=W)


        #PLOTTER psucc
        self.statistics_psucc_frame=ttk.LabelFrame(self, text="Plot success probability", height=50, width=50)
        self.statistics_psucc_frame.grid(column=0, row=2, columnspan=1, sticky='nesw')
        start_new_thread(self.plotpsucc,(99,))

        #PLOTTER airtime
        self.statistics_airtime_frame=ttk.LabelFrame(self, text="Plot Airtime", height=50, width=50)
        self.statistics_airtime_frame.grid(column=1, row=2, columnspan=1, sticky='nesw')
        start_new_thread(self.plotairtime,(99,))

        #PLOTTER cw
        self.statistics_cw_frame=ttk.LabelFrame(self, text="Plot Contention window", height=50, width=50)
        self.statistics_cw_frame.grid(column=2, row=2, columnspan=1, sticky='nesw')
        start_new_thread(self.plotcw,(99,))

        #LOOP command traffic
        start_new_thread(self.traffic_command_handles,(99,))

        # ttk.Separator(self, orient='horizontal').grid(column=0, row=1, columnspan=4, sticky='ew')
        #
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

if __name__ == '__main__':
    root = Tk()
    Adder(root)
    root.mainloop()