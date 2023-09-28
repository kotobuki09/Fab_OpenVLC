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
    ), 15)


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

    data_monitor_service_1 = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
                              "2404": [[], [], [], []], "2412": [[], [], [], []], "2420": [[], [], [], []],
                              "2429": [[], [], [], []], "2437": [[], [], [], []], "2445": [[], [], [], []],
                              "2454": [[], [], [], []], "2462": [[], [], [], []], "2470": [[], [], [], []],
                              "2476": [[], [], [], []], "2484": [[], [], [], []], "2492": [[], [], [], []]}

    data_monitor_service_2 = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
                              "2404": [[], [], [], []], "2412": [[], [], [], []], "2420": [[], [], [], []],
                              "2429": [[], [], [], []], "2437": [[], [], [], []], "2445": [[], [], [], []],
                              "2454": [[], [], [], []], "2462": [[], [], [], []], "2470": [[], [], [], []],
                              "2476": [[], [], [], []], "2484": [[], [], [], []], "2492": [[], [], [], []]}

    while True:
        full_msg = socket.recv_multipart()
        msg = json.loads(full_msg[1].decode('utf-8'), encoding='utf-8')
        # print(msg)
        if full_msg[0] == b'monitorReport':
            # print(msg)
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


        if full_msg[0] == b'specStatusUpdate_2' or full_msg[0] == b'specStatusUpdate':
            if full_msg[0] == b'specStatusUpdate_2':
                ##############
                ###DATA wiplus
                ##############
                data_monitor_service_1 = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
                                          "2404": [], "2412": [], "2420": [],
                                          "2429": [], "2437": [], "2445": [],
                                          "2454": [], "2462": [], "2470": [],
                                          "2476": [], "2484": [], "2492": []}
                msg_monitor_value = msg["monitorValue"]
                # print(msg_monitor_value)
                # {'WIFI': {'2412': [20, 0.24], '2437': [20, 0.08], '2462': [20, 0.2]}, 'Busy': {'2412': [20, 0.28], '2437': [20, 0.1], '2462': [20, 0.31]}}
                # msg_monitor_value["LTE"]={'2412': [6, 0.7]}
                # print(msg_monitor_value)
                for key_table in data_monitor_service_1["Interference"]:
                    # print(key_table)
                    if key_table in msg_monitor_value:
                        msg_monitor_value_freq = msg_monitor_value[key_table]
                        for key_freq in ["2412", "2437", "2462", "2484"]:
                            if key_freq in msg_monitor_value_freq:
                                data_monitor_service_1[str(int(key_freq) - 8)].append([round(msg_monitor_value_freq[key_freq][0]/3), msg_monitor_value_freq[key_freq][1]])
                                data_monitor_service_1[key_freq].append([round(msg_monitor_value_freq[key_freq][0]/3), msg_monitor_value_freq[key_freq][1]])
                                data_monitor_service_1[str(int(key_freq) + 8)].append([round(msg_monitor_value_freq[key_freq][0]/3), msg_monitor_value_freq[key_freq][1]])
                            else:
                                data_monitor_service_1[str(int(key_freq) - 8)].append([])
                                data_monitor_service_1[key_freq].append([])
                                data_monitor_service_1[str(int(key_freq) + 8)].append([])
                    else:
                        data_monitor_service_1["2404"].append([])
                        data_monitor_service_1["2412"].append([])
                        data_monitor_service_1["2420"].append([])

                        data_monitor_service_1["2429"].append([])
                        data_monitor_service_1["2437"].append([])
                        data_monitor_service_1["2445"].append([])

                        data_monitor_service_1["2454"].append([])
                        data_monitor_service_1["2462"].append([])
                        data_monitor_service_1["2470"].append([])

                        data_monitor_service_1["2476"].append([])
                        data_monitor_service_1["2484"].append([])
                        data_monitor_service_1["2492"].append([])

                # print(data_monitor_service_1)

            if full_msg[0] == b'specStatusUpdate':
                ###################
                ##DATA interference Detection
                ####################
                data_monitor_service_2 = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
                                          "2404": [[], [], [], []], "2412": [[], [], [], []], "2420": [[], [], [], []],
                                          "2429": [[], [], [], []], "2437": [[], [], [], []], "2445": [[], [], [], []],
                                          "2454": [], "2462": [], "2470": [],
                                          "2476": [[], [], [], []], "2484": [[], [], [], []], "2492": [[], [], [], []]}
                msg_monitor_value = msg["monitorValue"]
                for key_table in data_monitor_service_2["Interference"]:
                    if key_table in msg_monitor_value:
                        key = key_table
                        # print(key)
                        data_temp = []
                        for key_freq, value_freq in msg_monitor_value[key].items():
                            if int(key_freq) < 2458:
                                data_temp.append([round(value_freq[0]), value_freq[1]])
                        if len(data_temp) > 0:
                            data_monitor_service_2["2454"].append(np.mean(data_temp, 0).tolist())
                        else:
                            data_monitor_service_2["2454"].append([])

                        data_temp = []
                        for key_freq, value_freq in msg_monitor_value[key].items():
                            if int(key_freq) > 2458 and int(key_freq) < 2465:
                                data_temp.append([round(value_freq[0]), value_freq[1]])
                        if len(data_temp) > 0:
                            data_monitor_service_2["2462"].append(np.mean(data_temp, 0).tolist())
                        else:
                            data_monitor_service_2["2462"].append([])

                        data_temp = []
                        for key_freq, value_freq in msg_monitor_value[key].items():
                            if int(key_freq) > 2465:
                                data_temp.append([round(value_freq[0]), value_freq[1]])
                        if len(data_temp) > 0:
                            data_monitor_service_2["2470"].append(np.mean(data_temp, 0).tolist())
                        else:
                            data_monitor_service_2["2470"].append([])

                    else:
                        data_monitor_service_2["2454"].append([])
                        data_monitor_service_2["2462"].append([])
                        data_monitor_service_2["2470"].append([])

                # print(data_monitor_service_2)

            ############
            ###DATA global monitor service
            ###########
            # data_monitor_service_global = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
            #                                "2404": [], "2412": [], "2420": [],
            #                                "2429": [], "2437": [], "2445": [],
            #                                "2454": [], "2462": [], "2470": [],
            #                                "2476": [], "2484": [], "2492": []}
            # for key_table, value_table in data_monitor_service_global.items():
            #     if not key_table == "Interference":
            #         data_monitor_service_global[key_table].append(data_monitor_service_1[key_table])
            #         data_monitor_service_global[key_table].append(data_monitor_service_2[key_table])
            # print(data_monitor_service_global)

            data_monitor_service_global_2 = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
                                             "2404": [], "2412": [], "2420": [],
                                             "2429": [], "2437": [], "2445": [],
                                             "2454": [], "2462": [], "2470": [],
                                             "2476": [], "2484": [], "2492": []}
            for key_table, value_table in data_monitor_service_global_2.items():
                if not key_table == "Interference":
                    for ii in range(4):
                        # print(key_table, " : ", ii)
                        data_temp = []
                        if len(data_monitor_service_1[key_table][ii]) > 0 and len(data_monitor_service_2[key_table][ii]) > 0:

                            data_temp.append(data_monitor_service_1[key_table][ii])
                            data_temp.append(data_monitor_service_2[key_table][ii])
                            # print(data_temp)
                            data_monitor_service_global_2[key_table].append(np.mean(data_temp, 0).tolist())
                        # print(data_monitor_service_global_2[key_table])
                        elif len(data_monitor_service_1[key_table][ii]) > 0:
                            data_monitor_service_global_2[key_table].append(data_monitor_service_1[key_table][ii])
                        elif len(data_monitor_service_2[key_table][ii]) > 0:
                            data_monitor_service_global_2[key_table].append(data_monitor_service_2[key_table][ii])
                        else:
                            data_monitor_service_global_2[key_table].append([])
            # print(data_monitor_service_global_2)

            for ses in server_context.application_context.sessions:
                ses._document.add_next_tick_callback(partial(
                            tab_update,
                            source=ses._document.select_one(
                                {'name': 'monitorServiceStatusUpdate'}),
                            data = data_monitor_service_global_2,
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

