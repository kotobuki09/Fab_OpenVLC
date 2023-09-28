__author__ = "Domenico Garlisi"
__copyright__ = "Copyright (c) 2016, CNIT"
__version__ = "0.1.0"
__email__ = "domenico.garlisi@cnit.it"

from Tkinter import *
import ttk
from PIL import Image, ImageTk

import random
from socket import *    # import *, but we'll avoid name conflict
from sys import argv, exit
import demjson
import json

import subprocess
import urllib2
import base64
import StringIO
import io
import urllib
import numpy
import cStringIO
import zmq
from urllib2 import urlopen, Request, URLError
import time
from thread import start_new_thread
import tkMessageBox
import tkSimpleDialog

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
matplotlib.use("TkAgg")

from matplotlib import rcParams
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

SUNKABLE_BUTTON1 = 'SunkableButton.TButton'
SUNKABLE_BUTTON2 = 'SunkableButton.TButton'
SUNKABLE_BUTTON3 = 'SunkableButton.TButton'

"""
This program implement a python gui to control and to plot result of the WiSHFUL metamac demo showcase.
It requires a connection to the demo global controller, to receive protocol information and to send demo command.

usage:
    python metamac_visualizer.py

"""

class Dialog(Toplevel):

    def __init__(self, parent, title = None):

        Toplevel.__init__(self, parent)
        self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent
        self.result = None
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
        self.buttonbox()
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
        self.initial_focus.focus_set()
        self.wait_window(self)

    #
    # construction hooks
    def body(self, master):
        Label(master, text="SHIFT STA1:").grid(row=0)
        Label(master, text="SHIFT STA2:").grid(row=1)
        Label(master, text="SHIFT STA3:").grid(row=2)
        Label(master, text="SHIFT STA4:").grid(row=3)

        v1 = StringVar(root, value='0')
        v2 = StringVar(root, value='0')
        v3 = StringVar(root, value='0')
        v4 = StringVar(root, value='0')
        self.e1 = Entry(master, textvariable=v1)
        self.e2 = Entry(master, textvariable=v2)
        self.e3 = Entry(master, textvariable=v3)
        self.e4 = Entry(master, textvariable=v4)
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)
        self.e4.grid(row=3, column=1)

        Label(master, text="LOW RATE:").grid(row=4)
        Label(master, text="HIGH RATE:").grid(row=5)
        self.low_rate = Entry(master)
        self.high_rate = Entry(master)
        self.low_rate.grid(row=4, column=1)
        self.high_rate.grid(row=5, column=1)


    def buttonbox(self):
        # standard buttons
        box = Frame(self)
        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()


    # standard button semantics
    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    # command hooks
    def validate(self):
        return 1

    def apply(self):
        first = int(self.e1.get())
        second = int(self.e2.get())
        self.result = [int(self.e1.get()), int(self.e2.get()), int(self.e3.get()), int(self.e4.get())]


class Adder(ttk.Frame):
    """The adders gui and functions."""
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.init_gui()

    def on_quit(self):
        """Exits program."""
        quit()

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

    def send_command_sta1(self, event):
        command_list = {'type': 'protocol', 'command': self.countryVarSta1.get(), 'ip_address': self.sta1_ipaddress}
        json_command = command_list
        print(json_command)
        if self.local_network :
            self.socket_command_local_network.send_json(json_command)
        else:
            self.socket_command_remote_network.send_json(json_command)

    def send_command_sta2(self, event):
        command_list = {'type': 'protocol', 'command': self.countryVarSta2.get(), 'ip_address': self.sta2_ipaddress}
        json_command = command_list
        print(json_command)
        if self.local_network :
            self.socket_command_local_network.send_json(json_command)
        else:
            self.socket_command_remote_network.send_json(json_command)

    def send_command_sta3(self, event):
        command_list = {'type': 'protocol', 'command': self.countryVarSta3.get(), 'ip_address': self.sta3_ipaddress}
        json_command = command_list
        print(json_command)
        if self.local_network :
            self.socket_command_local_network.send_json(json_command)
        else:
            self.socket_command_remote_network.send_json(json_command)

    def send_command_sta4(self, event):
        command_list = {'type': 'protocol', 'command': self.countryVarSta4.get(), 'ip_address': self.sta4_ipaddress}
        json_command = command_list
        print(json_command)
        if self.local_network :
            self.socket_command_local_network.send_json(json_command)
        else:
            self.socket_command_remote_network.send_json(json_command)

    def select_source_rate(self):
        d = Dialog(self.root)
        print('%s' % str(d.result))
        self.sta1_shift = int(d.result[0])
        self.sta2_shift = int(d.result[1])
        self.sta3_shift = int(d.result[2])
        self.sta4_shift = int(d.result[3])

    def select_ttilab(self):
        self.sta1_ipaddress = '10.8.8.103'
        self.sta2_ipaddress = '10.8.8.111'
        self.sta3_ipaddress = '10.8.8.110'
        self.sta4_ipaddress = '10.8.8.118'
        self.local_network = 0
        #self.location='http://10.8.9.3/crewdemo/plots/usrp.png'
        self.location='http://127.0.0.1:8310/crewdemo/plots/usrp.png'
        self.init_loop_capture = 1
        self.static = 0
        print('switch to ttilab')

    def select_wilab2(self):
        self.sta1_ipaddress = '172.16.0.9'
        self.sta2_ipaddress = '172.16.0.10'
        self.sta3_ipaddress = '172.16.0.12'
        self.sta4_ipaddress = '172.16.0.13'
        self.local_network = 1
        self.location='http://127.0.0.1:8410/crewdemo/plots/usrp.png'
        self.init_loop_capture = 1
        self.static = 0
        print('switch to wilab')

    def stopTraffic(self):
        command = 'stop'
        command_list = {'type': 'traffic', 'command': command}
        json_command = command_list
        print(json_command)
        if self.local_network :
            self.socket_command_local_network.send_json(json_command)
        else:
            self.socket_command_remote_network.send_json(json_command)

        self.stopTrafficBtn.state(['pressed', 'disabled'])
        self.style.configure(SUNKABLE_BUTTON1, relief=SUNKEN, foreground='green')

        self.lowTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON2, relief=RAISED, foreground='red')

        self.highTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON3, relief=RAISED, foreground='red')

    def startTrafficLow(self):
        command = 'start_low'
        command_list = {'type': 'traffic', 'command': command, 'source_rate':'100'}
        json_command = command_list
        print(json_command)
        if self.local_network :
            self.socket_command_local_network.send_json(json_command)
        else:
            self.socket_command_remote_network.send_json(json_command)

        self.lowTrafficBtn.state(['pressed', 'disabled'])
        self.style.configure(SUNKABLE_BUTTON2, relief=SUNKEN, foreground='green')

        self.stopTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON1, relief=RAISED, foreground='red')

        self.highTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON3, relief=RAISED, foreground='red')

    def startTrafficHigh(self):
        command = 'start_high'
        command_list = {'type': 'traffic', 'command': command, 'source_rate':'1500'}
        json_command = command_list
        print(json_command)
        if self.local_network :
            self.socket_command_local_network.send_json(json_command)
        else:
            self.socket_command_remote_network.send_json(json_command)

        self.highTrafficBtn.state(['pressed', 'disabled'])
        self.style.configure(SUNKABLE_BUTTON3, relief=SUNKEN, foreground='green')

        self.stopTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON1, relief=RAISED, foreground='red')

        self.lowTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON2, relief=RAISED, foreground='red')

    def loopCapture(self,x):
        rcParams.update({'figure.autolayout': True})
        plt.ion()
        f = Figure(frameon=False)
        ax = f.add_subplot(111)
        im = None

        while True:
            if not self.static:
                if self.init_loop_capture:
                    print('start usrp request')
                    try:
                        urllib2.urlopen(self.location)
                        file = cStringIO.StringIO(urllib.urlopen(self.location).read())
                        img = Image.open(file)
                        wpercent=100
                        basewidth = 800
                        wpercent = (basewidth/float(img.size[0]))
                        hsize = int((float(img.size[1])*float(wpercent)))
                        img = img.resize((basewidth,hsize), Image.ANTIALIAS)

                    except Exception as e:
                        print(e)
                        try:
                            img = mpimg.imread("image.png")
                            self.static = 1
                        except Exception as e:
                            print(e)

                    #ax.imshow(img, aspect = 'normal')
                    im = ax.imshow(img)
                    ax.axis("off")

                    # my_dpi=100
                    # width=1100
                    # height=400
                    # f.set_size_inches(width/my_dpi, height/my_dpi)
                    f.set_size_inches(11.7,4.5)

                    canvas = FigureCanvasTkAgg(f, self.channel_frame)
                    canvas.show()
                    canvas.get_tk_widget().grid(column=0, row=0, columnspan=1, sticky='nesw')

                    self.init_loop_capture = 0

                else:
                    try:
                        file = cStringIO.StringIO(urllib.urlopen(self.location).read())
                        if file:
                            try:
                                img = Image.open(file)
                                im.set_data(img)
                                f.canvas.draw()
                            except Exception as e:
                                print(e)
                                print('ERRORE open image')
                        else:
                            print('ERRORE download image')
                    except Exception as e:
                        print(e)
                        print('ERRORE request image')


            time.sleep(1)



    line1 = None
    line2 = None
    line3 = None
    line4 = None
    f = None
    def loop_statistics(self,x):
        global line1
        global f

        init = 1
        while True:
            if init:
                try:
                    rcParams.update({'figure.autolayout': True})
                    plt.ion()
                    #f = Figure(figsize=(5,2.9), dpi=100)
                    f = Figure()
                    ax = f.add_subplot(111)

                    # self.yval.append( numpy.nan_to_num( stats.get('psucc') ) )
                    # yy=self.yval[::-1]
                    # yy=yy[0:self.Nplot]
                    # self.yval=yy[::-1]
                    ax.grid(True)
                    ax.set_xlabel('Time [s]', fontsize=12)
                    ax.set_ylabel('Protocol')

                    #self.tick=(self.tick+1) % self.Nplot

                    #ax.plot(self.xval,self.yval[::-1])
                    line1, = ax.plot(self.xval, self.sta1val, label='Node A')
                    line2, = ax.plot(self.xval, self.sta2val, label='Node B')
                    line3, = ax.plot(self.xval, self.sta3val, label='Node C')
                    line4, = ax.plot(self.xval, self.sta4val, label='Node D')

                    labels = ['',  'TDMA 1', 'TDMA 2', 'TDMA 3', 'TDMA 4', 'ALOHA', '']
                    # set the tick labels
                    ax.set_yticklabels(labels, rotation=45)

                    ax.set_ylim([0, 6])
                    ax.patch.set_facecolor('white')
                    f.set_facecolor('white')
                    legend = ax.legend(loc='upper center', shadow=True, ncol=4)

                    my_dpi=100
                    width=1080
                    height=400
                    f.set_size_inches(width/my_dpi,height/my_dpi)
                    #plt.tight_layout()

                    canvas = FigureCanvasTkAgg(f, self.statistics_frame)
                    canvas.show()
                    canvas.get_tk_widget().configure(background='white',  highlightcolor='white', highlightbackground='white')
                    canvas.get_tk_widget().grid(column=0, row=0, columnspan=1, sticky='nesw')

                except Exception as e:
                    print e
                    pass

                init = 0

            else:
                line1.set_ydata(self.sta1val)
                line2.set_ydata(self.sta2val)
                line3.set_ydata(self.sta3val)
                line4.set_ydata(self.sta4val)
                f.canvas.draw()


            time.sleep(1)


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

            #print('parsed_json : %s' % str(parsed_json))
            #parsed_json : {u'wlan_ip_address': u'192.168.3.110', u'measure': [[2668741, 4, 0.0]]}
            remote_ipAddress = parsed_json['wlan_ip_address']
            measure = parsed_json['measure'][0]

            if self.sta1_ipaddress.split('.')[3] == remote_ipAddress.split('.')[3] :
                self.sta1val.pop(0)
                if int(measure[1]) < 5:
                    self.sta1val.append( float(measure[1]) + 1 - 0.1  + self.sta1_shift )
                    self.sta1_log_Label.config(text="A => {}".format(self.protocol_list[int(measure[1]) + 1 + self.sta1_shift]))
                else:
                    self.sta1val.append( float(measure[1]) + 1 - 0.1  )
                    self.sta1_log_Label.config(text="A => {}".format(self.protocol_list[int(measure[1]) + 1] ))

            if self.sta2_ipaddress.split('.')[3] == remote_ipAddress.split('.')[3] :
                self.sta2val.pop(0)
                if int(measure[1]) < 5:
                    self.sta2val.append( float(measure[1]) + 1 - 0.2  + self.sta2_shift )
                    self.sta2_log_Label.config(text="B => {}".format(self.protocol_list[int(measure[1]) + 1 + self.sta2_shift]))
                else:
                    self.sta2val.append( float(measure[1]) + 1 - 0.2   )
                    self.sta2_log_Label.config(text="B => {}".format(self.protocol_list[int(measure[1]) + 1 ]))

            if self.sta3_ipaddress.split('.')[3] == remote_ipAddress.split('.')[3] :
                self.sta3val.pop(0)
                if int(measure[1]) < 5:
                    self.sta3val.append( float(measure[1]) + 1 + 0.1 + self.sta3_shift )
                    self.sta3_log_Label.config(text="C => {}".format(self.protocol_list[int(measure[1]) + 1 + self.sta3_shift]))
                else:
                    self.sta3val.append( float(measure[1]) + 1 + 0.1 )
                    self.sta3_log_Label.config(text="C => {}".format(self.protocol_list[int(measure[1]) + 1 ]))

            if self.sta4_ipaddress.split('.')[3] == remote_ipAddress.split('.')[3] :
                self.sta4val.pop(0)
                if int(measure[1]) < 5:
                    self.sta4val.append( float(measure[1]) + 1 + 0.2 + self.sta4_shift )
                    self.sta4_log_Label.config(text="D => {}".format(self.protocol_list[int(measure[1]) + 1 + self.sta4_shift]))
                else:
                    self.sta4val.append( float(measure[1]) + 1 + 0.2 )
                    self.sta4_log_Label.config(text="D => {}".format(self.protocol_list[int(measure[1]) + 1 ]))


    def init_gui(self):

        #VISUALIZER CONFIGURATION
        self.local_network = 1
        self.Nplot=100
        #self.yval=[0 for x in range(0,self.Nplot)]
        self.sta1val=[1 for x in range(0,self.Nplot)]
        self.sta2val=[2 for x in range(0,self.Nplot)]
        self.sta3val=[3 for x in range(0,self.Nplot)]
        self.sta4val=[4 for x in range(0,self.Nplot)]
        self.xval=[x for x in range(-self.Nplot, 0)]
        self.tick=0

        self.protocol_list = ['', 'TDMA 1', 'TDMA 2', 'TDMA 3', 'TDMA 4', 'ALOHA']

        """GUI SETUP"""
        print('GUI setup')
        self.root.title('WiSHFUL Meta-MAC showcase')
        self.root.option_add('*tearOff', 'FALSE')

        self.parent = self.root
        self.root.title("WiSHFUL Meta-MAC showcase")
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.centreWindow()
        self.pack(fill=BOTH, expand=1)

        self.grid(column=0, row=0, sticky='nsew')

        self.menubar = Menu(self.root)

        #menu edit quit
        self.menu_file = Menu(self.menubar)
        self.menu_file.add_command(label='Exit', command=self.on_quit)
        #menu edit traffic source
        self.menu_edit_traffic = Menu(self.menubar)
        self.menu_edit_traffic.add_command(label='Select station rate', command=self.select_source_rate)
        self.menu_edit_traffic.add_command(label='Reset plot', command=self.select_ttilab)
        self.menu_edit_traffic.add_command(label='Reset rate', command=self.select_wilab2)
        #create menu
        self.menubar.add_cascade(menu=self.menu_file, label='File')
        self.menubar.add_cascade(menu=self.menu_edit_traffic, label='Edit')
        self.root.config(menu=self.menubar)


        #NETWORK SOCKET SETUP
        print('Network socket setup')

        self.location='http://127.0.0.1:8410/crewdemo/plots/usrp.png'
        self.init_loop_capture = 1
        self.static = 0

        self.sta1_shift = 0
        self.sta2_shift = 0
        self.sta3_shift = 0
        self.sta4_shift = 0

        #default local network selected (wilab2)
        self.sta1_ipaddress = '172.16.0.9'
        self.sta2_ipaddress = '172.16.0.10'
        self.sta3_ipaddress = '172.16.0.12'
        self.sta4_ipaddress = '172.16.0.13'

        self.socket_command_port_local_network = 8400
        self.context1 = zmq.Context()
        print("Connecting to server on port 8400 ... ready to send command to demo experiment node")
        self.socket_command_local_network = self.context1.socket(zmq.PAIR)
        self.socket_command_local_network.connect ("tcp://localhost:%s" % self.socket_command_port_local_network)

        self.socket_plot_port_local_network  = 8401
        self.context2 = zmq.Context()
        print("Connecting to server on port 8401 ... ready to receive protocol information from demo experiment node")
        self.socket_plot_local_network = self.context2.socket(zmq.SUB)
        self.socket_plot_local_network.connect ("tcp://localhost:%s" % self.socket_plot_port_local_network)
        self.socket_plot_local_network.setsockopt(zmq.SUBSCRIBE, '')

        #open connection to remote network (ttilab)
        self.socket_command_port_remote_network = 8300
        self.context3 = zmq.Context()
        print("Connecting to server on port 8300 ... ready to send command to demo experiment node")
        self.socket_command_remote_network = self.context3.socket(zmq.PAIR)
        self.socket_command_remote_network.connect ("tcp://localhost:%s" % self.socket_command_port_remote_network)

        self.socket_plot_port_remote_network  = 8301
        self.context4 = zmq.Context()
        print("Connecting to server on port 8301 ... ready to receive protocol information from demo experiment node")
        self.socket_plot_remote_network = self.context4.socket(zmq.SUB)
        self.socket_plot_remote_network.connect ("tcp://localhost:%s" % self.socket_plot_port_remote_network)
        self.socket_plot_remote_network.setsockopt(zmq.SUBSCRIBE, '')

        #PLOT TOPOLOGY IMAGE
        self.topo_frame=ttk.LabelFrame(self, text="Network Scenario", height=100, width=100)
        self.topo_frame.grid(column=0, row=1, columnspan=2, sticky='nesw')

        img=Image.open('topology-4nodes.png')
        wpercent=100
        basewidth = 490
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        im = ImageTk.PhotoImage(img)

        label_topo_img = Label(self.topo_frame, image=im)
        label_topo_img.image = im
        label_topo_img.grid(row=0,column=0, sticky=W+E)

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


        #USRP FRAME
        self.channel_frame=ttk.LabelFrame(self, text="Channel occupation", height=20, width=100)
        self.channel_frame.grid(column=2, row=1, columnspan=2, rowspan=2, sticky='nw')
        start_new_thread(self.loopCapture,(99,))


        #Protocol FRAME
        self.protocol_frame = ttk.LabelFrame(self, text='Protocol', height=100, width=100)
        self.protocol_frame.grid(column=0, row=2, columnspan=1, sticky='nesw')

        self.LabelProtocol = Label(self.protocol_frame, text="Select Protocol")
        #self.LabelProtocol.pack(side=TOP, anchor=CENTER, expand=NO)
        self.LabelProtocol.grid(row=0, column=0, padx=5, pady=5, ipady=2, sticky=W)

        #station1
        countryLabelSta1 = Label(self.protocol_frame, text="Node A")
        countryLabelSta1.grid(row=1, column=0, sticky=W+E)
        self.countryVarSta1 = StringVar()
        self.countryComboSta1 = ttk.Combobox(self.protocol_frame, textvariable=self.countryVarSta1)
        self.countryComboSta1['values'] = ('METAMAC', 'TDMA 1', 'TDMA 2', 'TDMA 3', 'TDMA 4', 'ALOHA')
        self.countryComboSta1.current(0)
        #self.countryComboSta1.bind("<<ComboboxSelected>>", self.send_command(self.sta1_ipaddress, self.countryVarSta1.get()))
        self.countryComboSta1.bind("<<ComboboxSelected>>", self.send_command_sta1)
        self.countryComboSta1.grid(row=1, column=1, padx=5, pady=5, ipady=2, sticky=W)
        #self.countryComboSta1.pack(side=TOP, anchor=CENTER, expand=NO)

        #station2
        countryLabelSta2 = Label(self.protocol_frame, text="Node B")
        countryLabelSta2.grid(row=2, column=0, sticky=W+E)
        self.countryVarSta2 = StringVar()
        self.countryComboSta2 = ttk.Combobox(self.protocol_frame, textvariable=self.countryVarSta2)
        self.countryComboSta2['values'] = ('METAMAC', 'TDMA 1', 'TDMA 2', 'TDMA 3', 'TDMA 4', 'ALOHA')
        self.countryComboSta2.current(0)
        #self.countryComboSta2.bind("<<ComboboxSelected>>", self.send_command(self.sta2_ipaddress, self.countryVarSta2.get()))
        self.countryComboSta2.bind("<<ComboboxSelected>>", self.send_command_sta2)
        self.countryComboSta2.grid(row=2, column=1, padx=5, pady=5, ipady=2, sticky=W)
        #self.countryComboSta2.pack(side=TOP, anchor=CENTER, expand=NO)

        #station3
        countryLabelSta3 = Label(self.protocol_frame, text="Node C")
        countryLabelSta3.grid(row=3, column=0, sticky=W+E)
        self.countryVarSta3 = StringVar()
        self.countryComboSta3 = ttk.Combobox(self.protocol_frame, textvariable=self.countryVarSta3)
        self.countryComboSta3['values'] = ('METAMAC', 'TDMA 1', 'TDMA 2', 'TDMA 3', 'TDMA 4', 'ALOHA')
        self.countryComboSta3.current(0)
        #self.countryComboSta3.bind("<<ComboboxSelected>>", self.send_command(self.sta3_ipaddress, self.countryVarSta3.get()))
        self.countryComboSta3.bind("<<ComboboxSelected>>", self.send_command_sta3)
        self.countryComboSta3.grid(row=3, column=1, padx=5, pady=5, ipady=2, sticky=W)
        #self.countryComboSta3.pack(side=TOP, anchor=CENTER, expand=NO)

        #station4
        countryLabelSta4 = Label(self.protocol_frame, text="Node D")
        countryLabelSta4.grid(row=4, column=0, sticky=W+E)
        self.countryVarSta4 = StringVar()
        self.countryComboSta4 = ttk.Combobox(self.protocol_frame, textvariable=self.countryVarSta4)
        self.countryComboSta4['values'] = ('METAMAC', 'TDMA 1', 'TDMA 2', 'TDMA 3', 'TDMA 4', 'ALOHA')
        self.countryComboSta4.current(0)
        #self.countryComboSta4.bind("<<ComboboxSelected>>", self.send_command(self.sta4_ipaddress, self.countryVarSta4.get()))
        self.countryComboSta4.bind("<<ComboboxSelected>>", self.send_command_sta4)
        self.countryComboSta4.grid(row=4, column=1, padx=5, pady=5, ipady=2, sticky=W)
        #self.countryComboSta4.pack(side=TOP, anchor=CENTER, expand=NO)


        #TRAFFIC FRAME
        self.traffic_frame = ttk.LabelFrame(self, text='Traffic', height=100, width=50)
        self.traffic_frame.grid(column=1, row=2, columnspan=1, sticky='nesw')

        traffic_pady = 15
        traffic_padx = 40

        self.LabelTraffic = Label(self.traffic_frame, text="Select traffic")
        #self.LabelTraffic.pack(side=TOP, anchor=CENTER, expand=NO)
        self.LabelTraffic.grid(row=0, column=0, padx=traffic_padx, pady=traffic_pady, ipady=2, sticky=W)

        self.stopTrafficBtn = ttk.Button(self.traffic_frame, text="STOP", width=10, command=self.stopTraffic,  style=SUNKABLE_BUTTON1)
        #self.stopTrafficBtn.pack(side=TOP, anchor=CENTER, expand=NO)
        self.stopTrafficBtn.grid(row=1, column=0, padx=traffic_padx, pady=traffic_pady, ipady=2, sticky='nesw')
        self.lowTrafficBtn = ttk.Button(self.traffic_frame, text="LOW", width=10, command=self.startTrafficLow,  style=SUNKABLE_BUTTON2)
        #self.lowTrafficBtn.pack(side=TOP, anchor=CENTER, expand=NO)
        self.lowTrafficBtn.grid(row=2, column=0, padx=traffic_padx, pady=traffic_pady, ipady=2, sticky='nesw')
        self.highTrafficBtn = ttk.Button(self.traffic_frame, text="HIGH", width=10, command=self.startTrafficHigh,  style=SUNKABLE_BUTTON3)
        #self.highTrafficBtn.pack(side=TOP, anchor=CENTER, expand=NO)
        self.highTrafficBtn.grid(row=3, column=0, padx=traffic_padx, pady=traffic_pady, ipady=2, sticky='nesw')


        #PROTOCOL INFORMATION
        self.stats_frame = ttk.LabelFrame(self, text='Monitor Protocol', height=100, width=50)
        self.stats_frame.grid(column=2, row=2, columnspan=1, sticky='nesw')
        self.sta1_log_Label=Label(self.stats_frame, text="A => {}".format( self.protocol_list[self.sta1val[self.Nplot-1]] ))
        self.sta1_log_Label.grid(column=0, row=1, sticky='nesw', padx=15, pady=15, ipady=2)
        self.sta2_log_Label=Label(self.stats_frame, text="B => {}".format( self.protocol_list[self.sta2val[self.Nplot-1]] ))
        self.sta2_log_Label.grid(column=0,row=2,sticky='nesw', padx=15, pady=15, ipady=2)
        self.sta3_log_Label=Label(self.stats_frame, text="C => {}".format( self.protocol_list[self.sta3val[self.Nplot-1]]) )
        self.sta3_log_Label.grid(column=0,row=3,sticky='nesw', padx=15, pady=15, ipady=2)
        self.sta4_log_Label=Label(self.stats_frame, text="D => {}".format( self.protocol_list[self.sta4val[self.Nplot-1]] ))
        self.sta4_log_Label.grid(column=0,row=4,sticky='nesw', padx=15, pady=15, ipady=2)

        #start statistic receiver thread
        start_new_thread(self.receive_data_plot,(99,))

        self.statistics_frame=ttk.LabelFrame(self, text="Plot statistics", height=100, width=300)
        self.statistics_frame.grid(column=3, row=2, columnspan=1, sticky='nesw')
        start_new_thread(self.loop_statistics,(99,))

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

if __name__ == '__main__':
    root = Tk()
    Adder(root)
    root.mainloop()