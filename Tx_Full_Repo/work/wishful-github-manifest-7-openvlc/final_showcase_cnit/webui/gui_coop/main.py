# -*- coding: utf-8 -*-
import conf

import itertools
import collector
import os
import json
import sys
import time
# import usrp
import zmq

from bokeh.io import curdoc
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource
from bokeh.models import NumeralTickFormatter
from bokeh.models.widgets import DataTable
from bokeh.models.widgets import TableColumn
from bokeh.models.widgets import Panel, Tabs
from bokeh.palettes import Colorblind7 as palette
from bokeh.plotting import figure
from bokeh.models import LinearColorMapper, BasicTicker, ColorBar
from bokeh.models.widgets import Button, RadioButtonGroup, Select, Slider
from bokeh.layouts import widgetbox
from bokeh.models.widgets import Div
from bokeh.models import Range1d
from bokeh.models.layouts import Column, Row
from bokeh.palettes import Spectral4, Spectral6


#channel_trace_ip_address = "10.8.9.3"
channel_trace_ip_address = "172.16.16.12"
channel_trace_directory = ""
ssh_command_string = "ssh -t " + channel_trace_ip_address + " cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal && sudo bash run_usrp.sh 11 &> /dev/null' &"
def set_channel_trace_channel(channel):
    global ssh_command_string

    if channel == 1:
        ssh_command_string = "ssh -t " + channel_trace_ip_address + " 'cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal && sudo bash run_usrp.sh 1 &> /dev/null' &"
    if channel == 2:
        ssh_command_string = "ssh -t " + channel_trace_ip_address + " 'cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal && sudo bash run_usrp.sh 6 &> /dev/null' &"
    if channel == 3:
        ssh_command_string = "ssh -t " + channel_trace_ip_address + " 'cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal && sudo bash run_usrp.sh 11 &> /dev/null' &"
    if channel == 4:
        ssh_command_string = "ssh -t " + channel_trace_ip_address + " 'cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal && sudo bash run_usrp.sh 14 &> /dev/null' &"

    ssh_command_string_kill = "ssh -t " + channel_trace_ip_address + " \"sudo ps aux | grep usrp | awk '{print \$2}' | xargs sudo kill -9 \" "
    print(ssh_command_string_kill)
    os.system(ssh_command_string_kill)
    print("process killed")

    time.sleep(1)
    print("execute command", ssh_command_string)
    os.system(ssh_command_string)
    print("command executed")

    return

def test_callback():
    set_channel_trace_channel(3)




#####################################
#########managing buttun
#####################################

socket_controller = None
def set_wifi(selection):
    global socket_controller
    #print('Radio button option ' + str(selection) + ' selected.')
    msg = { "selection": selection }
    socket_controller.send_multipart([
        b'commandWiFi',
        json.dumps(msg).encode('utf-8'),
    ])

def set_wifi_rate(selection):
    global socket_controller
    #print('Radio button option ' + str(selection) + ' selected.')
    msg = {"selection": selection}
    socket_controller.send_multipart([
        b'commandWiFiRate',
        json.dumps(msg).encode('utf-8'),
    ])


def set_lte(selection):
    global socket_controller
    #print('Radio button option ' + str(selection) + ' selected.')
    msg = { "selection": selection }
    socket_controller.send_multipart([
        b'commandLTE',
        json.dumps(msg).encode('utf-8'),
    ])


def set_zigbee(selection):
    global socket_controller
    #print('Radio button option ' + str(selection) + ' selected.')
    msg = { "selection": selection }
    socket_controller.send_multipart([
        b'commandZigBee',
        json.dumps(msg).encode('utf-8'),
    ])


def set_cooperation(selection):
    global socket_controller
    #print('Radio button option ' + str(selection) + ' selected.')
    msg = { "selection": selection }
    socket_controller.send_multipart([
        b'commandCooperaiton',
        json.dumps(msg).encode('utf-8'),
    ])

# def set_deterministic(selection):
#     global socket_controller
#     #print('Radio button option ' + str(selection) + ' selected.')
#     msg = { "selection": selection }
#     socket_controller.send_multipart([
#         b'commandDeterministic',
#         json.dumps(msg).encode('utf-8'),
#     ])


#####################################
#############managing plot
#####################################

plt_array = []

# Update primary axis function
def update_data(attrname, old, new):
    global plt_array
    #print(slider_y_range.value)
    # plt_array[0].y_range.start = 0
    if slider_y_range.value == 30000000:
        plt_array[0].y_range.end = None
        #plt_array[0].y_range.bounds = 'auto'
    else:
        plt_array[0].y_range.end = slider_y_range.value
    # plt_array[0].y_range = Range1d(start=1, end=1000000)


def update_data_lte(attrname, old, new):
    global plt_array
    #print(slider_y_range_lte.value)
    # plt_array[0].y_range.start = 0
    if slider_y_range_lte.value == 30000000:
        plt_array[2].y_range.end = None
        #plt_array[0].y_range.bounds = 'auto'
    else:
        plt_array[2].y_range.end = slider_y_range_lte.value
    # plt_array[0].y_range = Range1d(start=1, end=1000000)


def set_graphtype(selection):
    global socket_controller
    print('Radio button option ' + str(selection) + ' selected.')
    if selection == 0:
        plt_array[1].yaxis.axis_label = "Performance"
    elif selection == 1:
        plt_array[1].yaxis.axis_label = "Packet Error Rate"
    else:
        pass

#####################################
######START INIZIALIZATION###########
#####################################

socket_controller_port = "5509"
#ip_address = "10.8.9.14"
ip_address = "172.16.17.2"
ctx = zmq.Context()
socket_controller = ctx.socket(zmq.PUB)
socket_controller.connect("tcp://%s:%s" % (ip_address, socket_controller_port))
print("Connecting to controller server %s on port %s ... ready to send information to experiment WEBUI" % (ip_address, socket_controller_port))

doc = curdoc()
colors = itertools.cycle(palette)
fixed_colors = ["Blue", "Red", "Black", "Orange", "Green", "Purple", "Pink"]


#####################
#### Network Table ####
#####################
data = dict(name=[], type=[], channel=[], load=[], active=[])
active_networks = ColumnDataSource(data, name='networkStatusUpdate')

nsu_cols = [
    TableColumn(field="name", title="Name", width=250),
    TableColumn(field="type", title="Type", width=100),
    TableColumn(field="channel", title="Channel", width=180),
    TableColumn(field="load", title="Application Load", width=100),
]
active_networks_table = DataTable(
    source=active_networks,
    columns=nsu_cols,
    fit_columns=False,
    width=690, height=100
)
tab_table = Panel(child=active_networks_table, title="Networks")

##### graph conf ##########
button_group_graph_conf = RadioButtonGroup(labels=["Performance", "PER"], active=0)
button_group_graph_conf.on_click(set_graphtype)

slider_y_range = Slider(value=2000000.0, start=1000000.0, end=30000000.0, step=1000000.0, title="Y range")
for w in [slider_y_range]:
    w.on_change('value', update_data)

slider_y_range_lte = Slider(value=2000000.0, start=1000000.0, end=30000000.0, step=1000000.0, title="Y range")
for w in [slider_y_range_lte]:
    w.on_change('value', update_data_lte)

tab_graph_conf = Panel(child=Row(button_group_graph_conf, Column(slider_y_range, slider_y_range_lte)), title="Conf")

tabs_active_networks_table = Tabs(tabs=[ tab_table, tab_graph_conf ])


#####################
#### Interference Table ####
#####################
# data_spec_2 = { "Interference": [], "LTE" : [], "WIFI":[], "ZIGBEE":[] }
# active_spec_2 = ColumnDataSource(data_spec_2, name='interferenceStatusUpdate')
# nsu_cols_spec_2 = [
#     TableColumn(field="Interference", title="Interference"),
#     TableColumn(field="LTE", title="LTE"),
#     TableColumn(field="WIFI", title="WiFi"),
#     TableColumn(field="ZIGBEE", title="ZigBee"),
# ]

data_spec_2 = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
						"2454": [[], [], [], []], "2462": [[], [], [], []], "2470": [[], [], [], []]}
active_spec_2 = ColumnDataSource(data_spec_2, name='interferenceStatusUpdate')
nsu_cols_spec_2 = [
    TableColumn(field="Interference", title="Interference", width=130),
    TableColumn(field="2454", title="2454MHz", width=130 ),
    TableColumn(field="2462", title="2462MHz", width=130),
    TableColumn(field="2470", title="2470MHz", width=130),
]
spectrum_table_2 = DataTable(
    source=active_spec_2,
    columns=nsu_cols_spec_2,
    index_position=None,
    width=420, height=125
)
tab_table_monitor_service = Panel(child=spectrum_table_2, title="Moitor service")
tabs_monitor_service = Tabs(tabs=[ tab_table_monitor_service ])



#####################
#### Error Table ####
#####################
# data_error_sense = {"error": [], "badplcp": [], "goodplcp": [], "badfcs": [], "goodfcs": []}
# active_error_sense = ColumnDataSource(data_error_sense, name='errorStatusUpdate')
# nsu_cols_error_sense = [
#     TableColumn(field="error", title="Error"),
#     TableColumn(field="badplcp", title="BAD PLCP"),
#     TableColumn(field="goodplcp", title="GOOD PLCP"),
#     TableColumn(field="badfcs", title="BAD FCS"),
#     TableColumn(field="goodfcs", title="GOOD FCS"),
# ]
# error_sense_table = DataTable(
#     source=active_error_sense,
#     columns=nsu_cols_error_sense,
#     index_position=None,
#     width=400, height=50
# )


fruits = ['BAD PLCP', 'GOOD PLCP', 'BAD FCS', 'GOOD FCS']
counts = [50, 40, 30, 20]
#error_plt = figure(x_range=fruits, plot_height=200, plot_width=500, title="Detected Error [%]", tools="", toolbar_location = None)
#source = ColumnDataSource(data=dict(fruits=fruits, counts=counts, color=Spectral4), name='errorStatusBar')
#data_error_sense = {"badplcp": [], "goodplcp": [], "badfcs": [], "goodfcs": []}
value_errot_sense = ColumnDataSource(
    data=dict(
        x=fruits,
        top=counts,
        color=Spectral4,
    ),
    name="errorStatusBar",
)

#source = ColumnDataSource(data=dict(fruits=fruits, counts=counts, color=Spectral6))
error_plt = figure(x_range=fruits, plot_height=350, plot_width=500, title="Detected Error [%]", tools="", toolbar_location = None)
#error_plt.vbar(x=fruits, top=[5, 3, 4, 2, 4, 6], width=0.9)
#error_plt.vbar('x', 'top', width=0.9, color=Spectral4, source=value_errot_sense)
#error_plt.vbar('x', 'top', color=Spectral4, data=value_errot_sense)
error_plt.vbar(x='x', top='top', width=0.9, color='color', legend=None, source=value_errot_sense)

error_plt.xgrid.grid_line_color = None
error_plt.y_range.start = 0
error_plt.y_range.end = 100
div_text = """"""
div_blank_6 = Div(text=div_text, width=140, height=0)
#l0 = layout([[ [tabs_monitor_service], [div_blank_6], [error_plt]]], sizing_mode='fixed', width=100)
l0 = layout([[ [div_blank_6], [tabs_monitor_service] ]], sizing_mode='fixed', width=100)


#iframe_text_2 = """<iframe src="http://10.8.9.3/WishfulWebPortal/only_usrp.html" height="350" width="1000" scrolling="no" frameBorder="0" ></iframe>"""
#iframe_text_2 = """<iframe src="http://127.0.0.1:8001/WishfulWebPortal/only_usrp.html" height="350" width="1000" scrolling="no" frameBorder="0" ></iframe>"""
iframe_text_2 = """<iframe src="http://172.16.16.12/WishfulWebPortal/only_usrp.html" height="350" width="1000" scrolling="no" frameBorder="0" ></iframe>"""
div = Div(text=iframe_text_2, width=600, height=270)

button_group_channel_trace = RadioButtonGroup(labels=["OFF", "2.412MHz", "2.437MHz", "2.462MHz", "2.484MHz"], active=0, width=600)
button_group_channel_trace.on_click(set_channel_trace_channel)
# l1 = layout([[div_blank, button_group_channel_trace], [div]], sizing_mode='fixed')
tab_channel_trace = Panel(child=div, title="Channel Trace")
tabs_channel_trace = Tabs(tabs=[ tab_channel_trace ])


button_group_wifi = RadioButtonGroup(labels=["OFF", "1", "2", "3", "4", "5", "DYNAMIC"], active=0, width=400)
button_group_wifi.on_click(set_wifi)
tab_wifi_button = Panel(child=button_group_wifi, title="WiFi")

# button_group_wifi_rate = RadioButtonGroup(labels=["OFF", "1Mbps", "2Mbps", "12Mbps", "24Mbps"], active=0, width=400)
# button_group_wifi_rate.on_click(set_wifi_rate)
# tab_wifi_rate_button = Panel(child=button_group_wifi_rate, title="Rate")

tabs_wifi = Tabs(tabs=[ tab_wifi_button])

button_group_lte = RadioButtonGroup(labels=["OFF", "ON"], active=0)
button_group_lte.on_click(set_lte)
tab_lte_button = Panel(child=button_group_lte, title="LTE")
tabs_lte = Tabs(tabs=[ tab_lte_button ])

button_group_zigbee = RadioButtonGroup(labels=["OFF", "ON"], active=0)
button_group_zigbee.on_click(set_zigbee)
tab_zigbee_button = Panel(child=button_group_zigbee, title="ZigBee")
tabs_zigbee = Tabs(tabs=[ tab_zigbee_button ])

button_group_cooperation = RadioButtonGroup(labels=["OFF", "ON"], active=0)
button_group_cooperation.on_click(set_cooperation)
tab_cooperaiton = Panel(child=button_group_cooperation, title="Cooperation")
# button_group_deterministic = RadioButtonGroup(labels=["OFF", "TABLE 1", "TABLE2"], active=0)
# button_group_deterministic.on_click(set_deterministic)
# tab_deterministic = Panel(child=button_group_deterministic, title="Deterministic")
tabs_functionality = Tabs(tabs=[ tab_cooperaiton ])

div_text = """"""
div_blank = Div(text=div_text, width=200, height=160)
div_blank_2 = Div(text=div_text, width=400, height=285)
div_blank_3 = Div(text=div_text, width=100, height=160)
div_blank_4 = Div(text=div_text, width=100, height=0)
div_blank_5 = Div(text=div_text, width=100, height=0)
# l1 = layout([[ [tabs_wifi], [tabs_lte], [tabs_cooperation] ]], sizing_mode='fixed', width=100)
l1 = layout([[ [tabs_functionality], [tabs_zigbee]]], sizing_mode='fixed', width=100)
l2 = layout([[ [tabs_lte], [tabs_wifi] ]], sizing_mode='fixed', width=100)
plots = [[ ]]
# plots = [[
#     [tabs_channel_trace,            tabs_wifi],
#     [div_blank_4,                   button_group_channel_trace, div_blank_2, tabs_lte],
#     [div_blank,                     div_blank_5 ],
#     [tabs_active_networks_table,    div_blank_3,                    tabs_cooperation] ]]

plots = [[
    [tabs_channel_trace],
    [div_blank_4,                   button_group_channel_trace, div_blank_2, l1],
    [tabs_active_networks_table,    l0, l2] ]]


####################################
########### PLOT  DATA  ################
####################################
index_color = 0
plot_height_value = 350
plot_width_value = 450

for technology in conf.controllers:
    print(technology)
    y_axis_end = 6000000
    if technology == "LTE-U":
        y_axis_end = 3000000

    thr_plt = figure(
        plot_height=plot_height_value, plot_width=plot_width_value,
        title="{} Received Throughput".format(technology),
        # tools="crosshair,pan,reset,save,wheel_zoom",
        tools="",
        toolbar_location=None,
        x_axis_type="datetime",
        y_range=[0, y_axis_end],
        name = "thr_plt",
    )
    thr_plt.legend.location = "top_left"
    thr_plt.xaxis.axis_label = "Time"
    thr_plt.yaxis.axis_label = "Throughput [B/s]"
    thr_plt.yaxis[0].formatter = NumeralTickFormatter(format='0.0b')

    #thr_plt.y_range.start = 0
    #thr_plt.y_range.end = 10000000


    per_plt = figure(
        plot_height=plot_height_value, plot_width=plot_width_value,
        title="{} Performance".format(technology),
        # tools="crosshair,pan,reset,save,wheel_zoom",
        tools="",
        toolbar_location=None,
        x_axis_type="datetime",
        y_range=[0, 1],
    )
    per_plt.legend.location = "top_left"
    per_plt.xaxis.axis_label = "Time"
    per_plt.yaxis.axis_label = "Performance"

    for k in conf.controllers[technology]:
        data = ColumnDataSource(
            data=dict(
                timestamp=[],
                PER=[],
                THR=[],
            ),
            name=k,
        )
        # color = next(colors)
        # color = next(color_mapper)

        thr_plt.line(
            'timestamp', 'THR',
            source=data,
            legend=conf.controllers[technology][k]['hrn'],
            line_color=fixed_colors[index_color],
            line_width=3, line_alpha=0.6,
        )
        per_plt.line(
            'timestamp', 'PER',
            source=data,
            legend=conf.controllers[technology][k]['hrn'],
            line_color=fixed_colors[index_color],
            line_width=3, line_alpha=0.6,
        )
        index_color += 1

    # plots.append([thr_plt, per_plt])
    thr_plt.x_range.follow = "end"
    thr_plt.x_range.follow_interval = 60000
    thr_plt.legend.location = "top_left"

    per_plt.x_range.follow = "end"
    per_plt.x_range.follow_interval = 60000
    per_plt.legend.location = "top_left"

    print("create plot", technology)
    plt_array.append(thr_plt)
    plt_array.append(per_plt)

#plots.append([plt_array[0], plt_array[1], plt_array[2], plt_array[3]])
tab_spectral_stats = Panel(child=Row(plt_array[0], plt_array[1], plt_array[2], plt_array[3]), title="Statistics")



####################################
########### PLOT  SPECTRAL  ################
####################################
index_color = 0
plot_height_value = 350
plot_width_value = 450

y_axis_end = 1
bw_plt = figure(
    plot_height=plot_height_value, plot_width=plot_width_value,
    title="CDF Bandwidth",
    tools="",
    toolbar_location=None,
    y_range=[0, y_axis_end],
    x_range=[0, 20],
)
bw_plt.xaxis.axis_label = "BW"
bw_plt.yaxis.axis_label = "CDF [MHz]"
data = ColumnDataSource(
    data=dict(
        BW=[],
        BW_CDF=[],
    ),
    name="bw_plt",
)
bw_plt.line(
    'BW', 'BW_CDF',
    source=data,
    line_color=fixed_colors[index_color],
    line_width=3, line_alpha=0.6,
)


freq_plt = figure(
    plot_height=plot_height_value, plot_width=plot_width_value,
    title="CDF Frequency",
    tools="",
    toolbar_location=None,
    y_range=[0, y_axis_end],
    x_range=[2440, 2480],
)
freq_plt.xaxis.axis_label = "Freq [MHz]"
freq_plt.yaxis.axis_label = "CDF"
data = ColumnDataSource(
    data=dict(
        FREQ=[],
        FREQ_CDF=[],
    ),
    name="freq_plt",
)
freq_plt.line(
    'FREQ', 'FREQ_CDF',
    source=data,
    line_color=fixed_colors[index_color],
    line_width=3, line_alpha=0.6,
)


duration_plt = figure(
    plot_height=plot_height_value, plot_width=plot_width_value,
    title="CDF Duration",
    tools="",
    toolbar_location=None,
    y_range=[0, y_axis_end],
    #x_range=[0, 1000],
)
duration_plt.xaxis.axis_label = "Duration [us]"
duration_plt.yaxis.axis_label = "CDF"
data = ColumnDataSource(
    data=dict(
        DURATION=[],
        DURATION_CDF=[],
    ),
    name="duration_plt",
)
duration_plt.line(
    'DURATION', 'DURATION_CDF',
    source=data,
    line_color=fixed_colors[index_color],
    line_width=3, line_alpha=0.6,
)

plt_array.append(bw_plt)
plt_array.append(freq_plt)
plt_array.append(duration_plt)

#plots.append([plt_array[4], plt_array[5], plt_array[6]])
tab_spectral_features = Panel(child=Row(plt_array[4], plt_array[5], plt_array[6], error_plt), title="Classification Features")

tabs_graph = Tabs(tabs=[ tab_spectral_stats, tab_spectral_features ])
plots.append([tabs_graph])



# layout = layout(plots, sizing_mode='scale_width')
layout = layout(children=plots, sizing_mode='fixed')

doc.add_root(layout)
doc.title = 'WiSHFUL'
#doc.add_periodic_callback(set_channel_trace_channel, 60000)
doc.add_periodic_callback(test_callback, 60000)


# # put all the plots in a VBox
# p = HBox(children=[s1, s2])
# # show the results
# div = notebook_div(p)
# display(HTML('<center>'+div+'</center>'))
