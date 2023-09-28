# -*- coding: utf-8 -*-
import conf
import itertools
import usrp
import time
import numpy as np

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

channel_trace_plot = None
doc = None
source_2 = None
cycle_count = 0
image = None
url_list = []
url_10 = "http://172.16.16.12/WishfulWebPortal/plots/usrp.png"
url_11 = "http://172.16.16.12/WishfulWebPortal/plots/usrp.png"
url_12 = "http://172.16.16.12/WishfulWebPortal/plots/usrp.png"


def usrp_callback():
    global channel_trace_plot
    global doc
    global source_2
    global cycle_count
    global image
    global layout
    print("clallback", cycle_count)
    # the callback
    url_1 = "http://172.16.16.12/WishfulWebPortal/plots/usrp.png"
    url_2 = 'https://bokeh.pydata.org/en/latest/_static/images/logo.png'

    #source_2.data = {'url': [url_1], 'x': [150], 'y': [150]}
    cycle_count += 1

    if cycle_count%3 == 0:
        print("test")
        # source_3 = ColumnDataSource(data=dict(url=[url_1], x=[150], y=[150]))
        # image_3 = ImageURL(url='url', x='x', y='y', w=150, h=150, anchor="bottom_right")
        # channel_trace_plot.add_glyph(source_3, glyph=image_3)

    if cycle_count%3 == 1:
        source_2.data = { 'url':[url_2], 'x': [250], 'y': [100]}

    if cycle_count%3 == 2:
        url = "http://172.16.16.12/WishfulWebPortal/plots/usrp.png"
        xdr = Range1d(start=0, end=300)
        ydr = Range1d(start=0, end=300)
        channel_trace_plot_3 = figure(
            title=None, x_range=xdr, y_range=ydr, plot_width=900, plot_height=340,
            h_symmetry=False, v_symmetry=False, min_border=0, toolbar_location=None)

        source_3 = ColumnDataSource(data=dict(url=[], x=[], y=[]), name="channel_trace")
        image_3 = ImageURL(url='url', x='x', y='y', w=150, h=150, anchor="bottom_right")
        channel_trace_plot_3.add_glyph(source_3, glyph=image_3)
        layout.children[[[0]]] = channel_trace_plot_3


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

# x_range = (-20,-10) # could be anything - e.g.(0,1)
# y_range = (20,30)
# p = figure(x_range=x_range, y_range=y_range)
# img_path = 'https://bokeh.pydata.org/en/latest/_static/images/logo.png'
# # img_path = 'server_folder/static/logo.png'
# p.image_url(url=[img_path],x=x_range[0],y=y_range[1],w=x_range[1]-x_range[0],h=y_range[1]-y_range[0])
# url = "https://bokeh.pydata.org/en/latest/_static/images/logo.png"


# url = "http://172.16.16.12/WishfulWebPortal/plots/usrp.png"
# data_channel_trace = { "url": [url], "x1": [50], "y1": [50]}
# source = ColumnDataSource( data=data_channel_trace, name="channel_trace")
# xdr = Range1d(start=0, end=300)
# ydr = Range1d(start=0, end=300)
# channel_trace_plot = figure(
#     title=None, x_range=xdr, y_range=ydr, plot_width=900, plot_height=340,
#     h_symmetry=False, v_symmetry=False, min_border=0, toolbar_location=None)
#
# # image1 = ImageURL(url="url", x="x1", y="y1", w="w1", h="h1", anchor="center")
# # channel_trace_render = channel_trace_plot.add_glyph(source, image1)
# #
# #image2 = ImageURL(url="url", x="x2", y="y2", w=20, h=20, anchor="top_left")
# # channel_trace_plot.add_glyph(source, image2)
#
# # image3 = ImageURL(url=dict(value=url), x=200, y=-100, anchor="bottom_right")
# #channel_trace_plot.add_glyph(source, image3)
#
# source_2 = ColumnDataSource(data=dict(url=[], x=[], y=[]), name="channel_trace")
# image = ImageURL(url='url', x='x', y='y', w=150, h=150, anchor="bottom_right")
# channel_trace_plot.add_glyph(source_2, glyph=image)

iframe_text_2 = """<iframe src="http://172.16.16.12/WishfulWebPortal/only_usrp.html" height="350" width="1000" scrolling="no" frameBorder="0" ></iframe>"""
div = Div(text=iframe_text_2, width=900, height=335)

# xaxis = LinearAxis()
# p.add_layout(xaxis, 'below')
#
# yaxis = LinearAxis()
# p.add_layout(yaxis,'left')

# p.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
# p.add_layout(Grid(dimension=1, ticker=yaxis.ticker))

plots = [[
    [div, tabs_spectrum_table],
    [tabs_active_networks_table,  tabs_spectrum_table_2] ]]

master_range = None

plt_array = []
index_color = 0
for technology in conf.controllers:
    thr_plt = figure(
        plot_height=300, plot_width=400,
        title="{} Received Throughput".format(technology),
        # tools="crosshair,pan,reset,save,wheel_zoom",
        tools="",
        toolbar_location=None,
        x_axis_type="datetime",
        # y_range=[0, None],
    )
    thr_plt.legend.location = "top_left"
    thr_plt.xaxis.axis_label = "Time"
    thr_plt.yaxis.axis_label = "Throughput [B/s]"
    thr_plt.yaxis[0].formatter = NumeralTickFormatter(format='0.0b')
    thr_plt.y_range.start = 0

    per_plt = figure(
        plot_height=300, plot_width=400,
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

    if master_range is None:
        master_range = thr_plt.x_range
    else:
        thr_plt.x_range = master_range
    per_plt.x_range = master_range

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
    per_plt.legend.location = "top_left"
    plt_array.append(thr_plt)
    plt_array.append(per_plt)

# plots.append([plt_array[0], plt_array[1]])
# plots.append([plt_array[2], plt_array[3]])
# plots.append([plt_array[4], plt_array[5]])

plots.append([plt_array[0], plt_array[2], plt_array[4], usrp.get_plot('spec_high')])
plots.append([plt_array[1], plt_array[3], plt_array[5], usrp.get_plot('spec_low')])

# layout = layout(plots, sizing_mode='scale_width')
layout = layout(children=plots, sizing_mode='fixed', name='mainLayout')

doc.add_root(layout)
doc.title = 'WiSHFUL'
#doc.add_periodic_callback(usrp_callback, 5000)
