# -*- coding: utf-8 -*-
import conf
import itertools
import usrp
import numpy as np
import subprocess, threading, time
import os

from bokeh.models.widgets import Div
from bokeh.io import curdoc
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource
from bokeh.models import NumeralTickFormatter
from bokeh.models.widgets import DataTable
from bokeh.models.widgets import TableColumn
from bokeh.palettes import Colorblind7 as palette
from bokeh.plotting import figure
from bokeh.models import LinearColorMapper, BasicTicker, ColorBar
from bokeh.models.widgets import HTMLTemplateFormatter
from bokeh.models.widgets import DateFormatter
from bokeh.models.widgets import Panel, Tabs
from bokeh.models import Range1d, Plot, LinearAxis, Grid
from bokeh.models.glyphs import ImageURL, Image
from bokeh.plotting import output_file, show
from bokeh.models.widgets import Slider, TextInput
from bokeh.models.widgets import Button, RadioButtonGroup, Select, Slider
from bokeh.models import BoxSelectTool


thr_plt = None
def set_visible():
    global thr_plt
    lineA1 = thr_plt.select(name="WIFI_A1")
    lineA1.visible = False


ssh_command_string = "ssh -t 172.16.16.12 'cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal && sudo bash run_usrp.sh 11 &> /dev/null' &"
def set_channel_trace_channel(channel=0):
    global ssh_command_string

    if channel == 1:
        ssh_command_string = "ssh -t 172.16.16.12 'cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal && sudo bash run_usrp.sh 1 &> /dev/null' &"
    if channel == 2:
        ssh_command_string = "ssh -t 172.16.16.12 'cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal && sudo bash run_usrp.sh 6 &> /dev/null' &"
    if channel == 3:
        ssh_command_string = "ssh -t 172.16.16.12 'cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal && sudo bash run_usrp.sh 11 &> /dev/null' &"
    if channel == 4:
        ssh_command_string = "ssh -t 172.16.16.12 'cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal && sudo bash run_usrp.sh 16 &> /dev/null' &"

    ssh_command_string_kill = "ssh -t 172.16.16.12 \"sudo ps aux | grep usrp | awk '{print \$2}' | xargs sudo kill -9 \" "
    print(ssh_command_string_kill)
    os.system(ssh_command_string_kill)
    print("process killed")

    time.sleep(1)
    print("execute command", ssh_command_string)
    os.system(ssh_command_string)
    print("command executed")

    return



doc = curdoc()
colors = itertools.cycle(palette)
fixed_colors = ["Blue", "Red", "Black", "Orange", "Green", "Purple", "Pink"]

data = dict(name=[], type=[], channel=[], load=[], active=[])
active_networks = ColumnDataSource(data, name='networkStatusUpdate')

nsu_cols = [
    TableColumn(field="name", title="Name", width=120),
    TableColumn(field="type", title="Type", width=120),
    TableColumn(field="channel", title="Channel", width=350),
    TableColumn(field="load", title="Application Load", width=60),
]

# Frequencies : 		2454 		2457 		2459 		2462 		2464 		2467 		2470
# Occurances : 		0 		10 		0 		63 		75 		1 		0
# Bandwidth : 		0 		0.0 		0 		16.0 		5.0 		8.0 		0
data_spec = { "Interference": [], "2454" : [], "2457":[], "2459":[], "2462":[], "2464":[], "2467":[], "2470":[] }
active_spec = ColumnDataSource(data_spec, name='specStatusUpdate')
nsu_cols_spec = [
    TableColumn(field="Interference", title="Interference"),
    TableColumn(field="2454", title="2454"),
    TableColumn(field="2457", title="2457"),
    TableColumn(field="2459", title="2459"),
    TableColumn(field="2462", title="2462"),
    TableColumn(field="2464", title="2464"),
    TableColumn(field="2467", title="2467"),
    TableColumn(field="2470", title="2470"),
]

# {'monitorValue': {'Busy': {'2412': [20, 0.06], '2437': [20, 0.01], '2462': [20, 0.03]}, 'WIFI': {'2412': [20, 0.05], '2437': [20, 0.01], '2462': [20, 0.02]}},
data_spec_2 = { "Interference": [], "2412" : [], "2437":[], "2462":[], "2484":[] }
active_spec_2 = ColumnDataSource(data_spec, name='specStatusUpdate_2')
nsu_cols_spec_2 = [
    TableColumn(field="Interference", title="Interference"),
    TableColumn(field="2412", title="2412"),
    TableColumn(field="2437", title="2437"),
    TableColumn(field="2462", title="2462"),
    TableColumn(field="2484", title="2484"),
]


active_networks_table = DataTable(
    source=active_networks,
    columns=nsu_cols,
    fit_columns=False,
    width=700, height=275
)
tab_table_1 = Panel(child=active_networks_table, title="Networks")
tabs_active_networks_table = Tabs(tabs=[ tab_table_1 ])

spectrum_table = DataTable(
    source=active_spec,
    columns=nsu_cols_spec,
    index_position=None,
    width=600, height=95
)
tab_table_2 = Panel(child=spectrum_table, title="Moitor service")
tabs_spectrum_table = Tabs(tabs=[ tab_table_2 ])

spectrum_table_2 = DataTable(
    source=active_spec_2,
    columns=nsu_cols_spec_2,
    index_position=None,
    width=400, height=95
)
tab_table_3 = Panel(child=spectrum_table_2, title="Moitor service")
tabs_spectrum_table_2 = Tabs(tabs=[ tab_table_3 ])

#################
#monitor service table
#################
# Frequencies : 		2454 		2457 		2459 		2462 		2464 		2467 		2470
# Occurances : 		0 		10 		0 		63 		75 		1 		0
# Bandwidth : 		0 		0.0 		0 		16.0 		5.0 		8.0 		0
# data_monitor_service = { "Interference": [],
#               "2401":[], "2405":[], "2408":[], "2412":[], "2416":[], "2420":[], "2424":[],
#               "2426":[], "2429":[], "2433":[], "2437":[], "2441":[], "2445":[], "2449":[],
#               "2454":[], "2457":[], "2459":[], "2462":[], "2464":[], "2467":[], "2470":[],
#               "2472":[], "2476":[], "2480":[], "2484":[], "2490":[], "2494":[], "2498":[]}
# data_monitor_service = { "Interference": [],
#               "2405":[], "2412":[], "2420":[],
#               "2429":[], "2437":[], "2445":[],
#               "2457":[], "2462":[], "2467":[],
#               "2476":[], "2484":[], "2494":[] }
data_monitor_service = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
                              "2404": [[], [], [], []], "2412": [[], [], [], []], "2420": [[], [], [], []],
                              "2429": [[], [], [], []], "2437": [[], [], [], []], "2445": [[], [], [], []],
                              "2454": [[], [], [], []], "2462": [[], [], [], []], "2470": [[], [], [], []],
                              "2476": [[], [], [], []], "2484": [[], [], [], []], "2492": [[], [], [], []]}
source_monitor_service = ColumnDataSource(data_monitor_service, name='monitorServiceStatusUpdate')
ms_cols_spec = [
    TableColumn(field="Interference", title="Interference"),
    TableColumn(field="2404", title="2.405MHz"),
    TableColumn(field="2412", title="2.412MHz"),
    TableColumn(field="2420", title="2.420MHz"),

    TableColumn(field="2429", title="2.429MHz"),
    TableColumn(field="2437", title="2.437MHz"),
    TableColumn(field="2445", title="2.445MHz"),

    TableColumn(field="2454", title="2.457MHz"),
    TableColumn(field="2462", title="2.462MHz"),
    TableColumn(field="2470", title="2.467MHz"),

#     TableColumn(field="2476", title="2.476MHz"),
#     TableColumn(field="2484", title="2.484MHz"),
#     TableColumn(field="2492", title="2.494MHz"),
 ]

spectrum_table_monitor_service = DataTable(
    source=source_monitor_service,
    columns=ms_cols_spec,
    index_position=None,
    width=1000, height=140
)
tab_table_monitor_service = Panel(child=spectrum_table_monitor_service, title="Moitor service")
tabs_monitor_service = Tabs(tabs=[ tab_table_monitor_service ])


iframe_text_2 = """<iframe src="http://172.16.16.12/WishfulWebPortal/only_usrp.html" height="350" width="1000" scrolling="no" frameBorder="0" ></iframe>"""
div = Div(text=iframe_text_2, width=600, height=270)

div_text = """"""
div_blank = Div(text=div_text, width=600, height=20)

button_group_channel_trace = RadioButtonGroup(labels=["OFF", "2.412MHz", "2.437MHz", "2.462MHz", "2.484MHz"], active=0, width=400)
button_group_channel_trace.on_click(set_channel_trace_channel)
# tab_channel_trace_button = Panel(child=button_group_channel_trace, title="Channel")
# tabs_wifi = Tabs(tabs=[ tab_channel_trace_button ])

l1 = layout([[div_blank, button_group_channel_trace], [div]], sizing_mode='fixed')
tab_channel_trace = Panel(child=div, title="Channel Trace")
tabs_channel_trace = Tabs(tabs=[ tab_channel_trace ])

div_blank_2 = Div(text=div_text, width=100, height=250)
div_blank_3 = Div(text=div_text, width=300, height=250)

plots = [[
    [div_blank_3],
    [tabs_channel_trace ],
    [div_blank, button_group_channel_trace, div_blank_2, tabs_monitor_service],
    [tabs_active_networks_table] ]]

master_range = None

plt_array = []
index_color = 0
for technology in conf.controllers:
    tools = ["pan", "wheel_zoom", "box_zoom", "hover", "reset" ]
    thr_plt = figure(
        plot_height=300, plot_width=450,
        title="{} Received Throughput".format(technology),
        tools=tools,
        toolbar_location="left",
        x_axis_type="datetime",
        # y_range=[0, None],
        # x_range=[0,20000],
    )
    thr_plt.legend.location = "top_left"
    thr_plt.xaxis.axis_label = "Time"
    thr_plt.yaxis.axis_label = "Throughput [B/s]"
    thr_plt.yaxis[0].formatter = NumeralTickFormatter(format='0.0b')
    thr_plt.y_range.start = 0

    per_plt = figure(
        plot_height=300, plot_width=450,
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

    # if master_range is None:
    #     master_range = thr_plt.x_range
    # else:
    #     thr_plt.x_range = master_range
    # per_plt.x_range = master_range


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
            source=data, legend=conf.controllers[technology][k]['hrn'],
            line_color=fixed_colors[index_color],
            line_width=3, line_alpha=0.6,
        )
        per_plt.line(
            'timestamp', 'PER',
            source=data, legend=conf.controllers[technology][k]['hrn'],
            line_color=fixed_colors[index_color],
            line_width=3, line_alpha=0.6,
        )
        index_color += 1

    # plots.append([thr_plt, per_plt])
    thr_plt.legend.location = "top_left"
    # per_plt.x_range = Range1d(0, 30)
    thr_plt.x_range.follow = "end"
    thr_plt.x_range.follow_interval = 30000
    # thr_plt.x_range.flipped = True

    per_plt.legend.location = "top_left"
    per_plt.x_range.follow = "end"
    per_plt.x_range.follow_interval = 30000

    plt_array.append(thr_plt)
    plt_array.append(per_plt)


#plots.append([plt_array[0], plt_array[2], plt_array[4], usrp.get_plot('spec_high')])
#plots.append([plt_array[1], plt_array[3], plt_array[5], usrp.get_plot('spec_low')])

plots.append([plt_array[0], plt_array[2], plt_array[4], plt_array[6], usrp.get_plot('spec_high')])
plots.append([plt_array[1], plt_array[3], plt_array[5], plt_array[7], usrp.get_plot('spec_low')])

layout = layout(children=plots, sizing_mode='fixed', name='mainLayout')

doc.add_root(layout)
doc.title = 'WiSHFUL'
doc.add_periodic_callback(set_channel_trace_channel, 60000)
