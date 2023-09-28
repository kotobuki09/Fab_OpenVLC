import json
import logging
import zmq
import numpy as np
import conf
import time

from datetime import datetime
from functools import partial
from tornado import gen
from bokeh.models import Range1d, Plot, LinearAxis, Grid
from bokeh.models import ColumnDataSource
from bokeh.models.glyphs import ImageURL





@gen.coroutine
def plt_update(source, timestamp, THR, PER):
    source.stream(dict(
        timestamp=[datetime.fromtimestamp(timestamp)],
        THR=[THR],
        PER=[PER],
    ), 120)


@gen.coroutine
def tab_update(source, data):
    source.data = data


def stats_listener(endpoint, server_context):
    logging.info('Starting statistics listener on %s', endpoint)

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, b'monitorReport')
    socket.setsockopt(zmq.SUBSCRIBE, b'networkStatusUpdate')
    socket.setsockopt(zmq.SUBSCRIBE, b'specStatusUpdate')
    socket.setsockopt(zmq.SUBSCRIBE, b'specStatusUpdate_2')
    socket.bind(endpoint)

    while True:
        full_msg = socket.recv_multipart()

        msg = json.loads(full_msg[1].decode('utf-8'), encoding='utf-8')

        #print(msg)

        if full_msg[0] == b'monitorReport':
            for ses in server_context.application_context.sessions:
                ses._document.add_next_tick_callback(partial(
                    plt_update,
                    source=ses._document.select_one(
                        {'name': msg['networkController']}),
                    timestamp=msg['monitorValue']['timestamp'],
                    THR=msg['monitorValue']['THR'],
                    PER=msg['monitorValue']['PER'],
                ))

        if full_msg[0] == b'networkStatusUpdate':
            for ses in server_context.application_context.sessions:
                ses._document.add_next_tick_callback(partial(
                    tab_update,
                    source=ses._document.select_one(
                        {'name': 'networkStatusUpdate'}),
                    data=dict(
                        name=[x['name'] for x in msg if x['active'] is True],
                        type=[x['type'] for x in msg if x['active'] is True],
                        channel=[x['channel'] for x in msg
                            if x['active'] is True],
                        load=[x['load'] for x in msg if x['active'] is True],
                    ),
                ))


        # msg = {'type': 'monitorReport',‘networkController': controllerName,	' monitorType ': ‘interference’, 'monitorValue': { “LTE”: { “2467”: [BW, duty]}
        #                  “ZigBee”: { “2484”: [BW, duty]} “Busy”: { “2484”: [BW, duty]} }, }
        # "LTE" "Busy" "ZigBee" "WiFi"
        # dict(f254=[], f2457=[], f2459=[], f2462=[], f2464=[], f2467=[], f2470=[])
        if full_msg[0] == b'specStatusUpdate':
            #print("receive specStatusUpdate")
            msg_monitor_value = msg["monitorValue"]
            data = {"Interference": [], "2454": [], "2457": [], "2459": [], "2462": [], "2464": [], "2467": [], "2470": []}
            all_interference_detected = []
            # if "Busy" in msg_monitor_value:
            #     msg_monitor_value_busy = msg_monitor_value["Busy"]
            #     data["Interference"].append("Busy")
            #     for key, value in data.items():
            #         if key in msg_monitor_value_busy:
            #             data[key].append(msg_monitor_value_busy[key])

            if "LTE" in msg_monitor_value:
                msg_monitor_value_busy = msg_monitor_value["LTE"]
                all_interference_detected.append("LTE")
                for key, value in data.items():
                    if key in msg_monitor_value_busy:
                        data[key].append(msg_monitor_value_busy[key])

            if "ZigBee" in msg_monitor_value:
                msg_monitor_value_busy = msg_monitor_value["ZigBee"]
                all_interference_detected.append("ZigBee")
                for key, value in data.items():
                    if key in msg_monitor_value_busy:
                        data[key].append(msg_monitor_value_busy[key])

            if "WiFi" in msg_monitor_value:
                msg_monitor_value_busy = msg_monitor_value["WiFi"]
                all_interference_detected.append("WiFi")
                for key, value in data.items():
                    if key in msg_monitor_value_busy:
                        data[key].append(msg_monitor_value_busy[key])

            data["Interference"].append(all_interference_detected)
            #print(data)
            # {'Interference': ['ZigBee'], '2454': [], '2457': [], '2459': [], '2462': [], '2464': [['2.0', 0.0]], '2467': [], '2470': []}
            max_len = 0
            for key, value in data.items():
                if len(data[key]) > max_len:
                    max_len = len(data[key])
            for key, value in data.items():
                if len(data[key]) < max_len:
                    current_len = len(data[key])
                    for ii in range(max_len - current_len):
                        data[key].append([])
            #print(data)
            for ses in server_context.application_context.sessions:
                ses._document.add_next_tick_callback(partial(
                    tab_update,
                    source=ses._document.select_one(
                        {'name': 'specStatusUpdate'}),
                    data = data,
                ))



        # {'monitorValue': {'Busy': {'2412': [20, 0.06], '2437': [20, 0.01], '2462': [20, 0.03]}, 'WIFI': {'2412': [20, 0.05], '2437': [20, 0.01], '2462': [20, 0.02]}},
        #  'monitorType': 'interference', 'type': 'monitorReport', 'networkController': 'WIPLUS_LTE_U_DETECTOR', 'networkType': 'DETECTOR'}

        #{'Interference': [['Busy', 'WIFI']], '2412': [[20, 0.06], [20, 0.04]], '2437': [[20, 0.02], [20, 0.01]], '2462': [[20, 0.04], [20, 0.02]], '2484': []}
        #{'Interference': [['Busy', 'WIFI'], []], '2412': [[20, 0.06], [20, 0.04]], '2437': [[20, 0.02], [20, 0.01]], '2462': [[20, 0.04], [20, 0.02]], '2484': [[], []]}

        if full_msg[0] == b'specStatusUpdate_2':
            #print("receive specStatusUpdate")
            #print(msg)
            data = {"Interference": [], "2412": [], "2437": [], "2462": [], "2484": []}
            msg_monitor_value = msg["monitorValue"]
            all_interference_detected = []
            # if "Busy" in msg_monitor_value:
            #     msg_monitor_value_busy = msg_monitor_value["Busy"]
            #     data["Interference"].append("Busy")
            #     for key, value in data.items():
            #         if key in msg_monitor_value_busy:
            #             data[key].append(msg_monitor_value_busy[key])

            if "Busy" in msg_monitor_value:
                msg_monitor_value_busy = msg_monitor_value["Busy"]
                all_interference_detected.append("Busy")
                for key, value in data.items():
                    if key in msg_monitor_value_busy:
                        data[key].append(msg_monitor_value_busy[key])

            if "LTE" in msg_monitor_value:
                msg_monitor_value_busy = msg_monitor_value["LTE"]
                all_interference_detected.append("LTE")
                for key, value in data.items():
                    if key in msg_monitor_value_busy:
                        data[key].append(msg_monitor_value_busy[key])

            if "ZigBee" in msg_monitor_value:
                msg_monitor_value_busy = msg_monitor_value["ZigBee"]
                all_interference_detected.append("ZigBee")
                for key, value in data.items():
                    if key in msg_monitor_value_busy:
                        data[key].append(msg_monitor_value_busy[key])

            if "WIFI" in msg_monitor_value:
                msg_monitor_value_busy = msg_monitor_value["WIFI"]
                all_interference_detected.append("WIFI")
                for key, value in data.items():
                    if key in msg_monitor_value_busy:
                        data[key].append(msg_monitor_value_busy[key])

            #data["Interference"].append(all_interference_detected)
            for ii in range(0, len(all_interference_detected)):
                #print(all_interference_detected[ii])
                data["Interference"].append(all_interference_detected[ii])

            #print(data)
            max_len = 0
            for key, value in data.items():
                if len(data[key]) > max_len:
                    max_len = len(data[key])
            for key, value in data.items():
                if len(data[key]) < max_len:
                    current_len = len(data[key])
                    for ii in range(max_len - current_len):
                        data[key].append([])
            #print(data)
            for ses in server_context.application_context.sessions:
                ses._document.add_next_tick_callback(partial(
                    tab_update,
                    source=ses._document.select_one(
                        {'name': 'specStatusUpdate_2'}),
                    data=data,
                ))


@gen.coroutine
def usrp_plot_update(source, spectrogram):
    source.update(data=dict(spectrogram=[spectrogram]))


@gen.coroutine
def usrp_fig_update(source, fc, bw, size):
    source.update(data=dict(fc=[fc], bw=[bw], size=[size]))


def usrp_listener(endpoint, server_context, name="spectrogram"):
    logging.info('Starting USRP listener on %s', endpoint)

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, b'gnuradio.spectrogram')
    socket.bind(endpoint)

    while True:
        full_msg = socket.recv_multipart()

        info = json.loads(full_msg[1])
        spectrogram = np.frombuffer(full_msg[2], dtype=np.float32).reshape(
            int(info['l']), int(info['w']))

        for ses in server_context.application_context.sessions:
            ses._document.add_next_tick_callback(partial(
                usrp_plot_update,
                source=ses._document.select_one({'name': name}),
                spectrogram=spectrogram,
            ))

            fc = int(info['fc'])
            bw = int(info['bw'])
            size = int(info['l'])

            ses._document.add_next_tick_callback(partial(
                usrp_fig_update,
                source=ses._document.select_one(
                    {'name': name + '_vars'}),
                fc=fc,
                bw=bw,
                size=size,
            ))



@gen.coroutine
def channel_trace_update(source, data):
    source.data = data
    image3 = ImageURL(url="url", x="x1", y="y1", w=50, h=50, anchor="bottom_right")
    #channel_trace_plot.add_glyph(source, image3)


def channel_trace_reload(server_context, name):
    logging.info('Starting channel trace reload')

    cycle_count = 1
    while True:
        time.sleep(1)
        print("CHANNEL TRACE THREAD")

        if cycle_count == 0:

            url = "http://172.16.16.12/WishfulWebPortal/plots/usrp.png"
            data_channel_trace = {"url": [url], "x1": [100], "y1": [100]}
            #image3 = ImageURL(url="url", x="x1", y="y1", w=50, h=50, anchor="bottom_right")
            #channel_trace_plot.add_glyph(source, image3)

            # for ses in server_context.application_context.sessions:
            #     ses._document.add_next_tick_callback(partial(
            #         channel_trace_update,
            #         source=ses._document.select_one(
            #             {'name': "channel_trace"}),
            #         data=data_channel_trace,
            #     ))
            cycle_count += 1


