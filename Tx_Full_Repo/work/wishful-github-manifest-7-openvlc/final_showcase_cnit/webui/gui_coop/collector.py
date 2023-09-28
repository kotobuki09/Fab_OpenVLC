import json
import logging
import zmq
import numpy as np
import conf

from datetime import datetime
from functools import partial
from tornado import gen
from bokeh.palettes import Spectral4, Spectral6



@gen.coroutine
def plt_update(source, timestamp, THR, PER):
    source.stream(dict(
        timestamp=[datetime.fromtimestamp(timestamp)],
        THR=[THR],
        PER=[PER],
    ), 30)


@gen.coroutine
def tab_update(source, data):
    source.data = data


@gen.coroutine
def plot_features_update(source, data):
    source.data = data


def stats_listener(endpoint, server_context):
    logging.info('Starting statistics listener on %s', endpoint)

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, b'monitorReport')
    socket.setsockopt(zmq.SUBSCRIBE, b'networkStatusUpdate')
    socket.setsockopt(zmq.SUBSCRIBE, b'spectralScanFeatures')
    socket.setsockopt(zmq.SUBSCRIBE, b'errorStatusUpdate')
    socket.setsockopt(zmq.SUBSCRIBE, b'specStatusUpdate')
    socket.setsockopt(zmq.SUBSCRIBE, b'specStatusUpdate_2')
    socket.bind(endpoint)

    data_monitor_service_1 = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
#                              "2404": [[], [], [], []], "2412": [[], [], [], []], "2420": [[], [], [], []],
#                              "2429": [[], [], [], []], "2437": [[], [], [], []], "2445": [[], [], [], []],
                              "2454": [[], [], [], []], "2462": [[], [], [], []], "2470": [[], [], [], []] }

    data_monitor_service_2 = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
#                              "2404": [[], [], [], []], "2412": [[], [], [], []], "2420": [[], [], [], []],
#                              "2429": [[], [], [], []], "2437": [[], [], [], []], "2445": [[], [], [], []],
                              "2454": [[], [], [], []], "2462": [[], [], [], []], "2470": [[], [], [], []] }

    data_monitor_service_3 = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
                              #                              "2404": [[], [], [], []], "2412": [[], [], [], []], "2420": [[], [], [], []],
                              #                              "2429": [[], [], [], []], "2437": [[], [], [], []], "2445": [[], [], [], []],
                              "2454": [[], [], [], []], "2462": [[], [], [], []], "2470": [[], [], [], []]}

    fruits = ['BAD PLCP', 'GOOD PLCP', 'BAD FCS', 'GOOD FCS']

    while True:
        full_msg = socket.recv_multipart()
        msg = json.loads(full_msg[1].decode('utf-8'), encoding='utf-8')
        #print(msg)

        ######## Statistcs update
        if full_msg[0] == b'monitorReport':
            #{'networkController': '6lowPAN', 'monitorValue': {'PER': 1, 'timestamp': 1530053712.205597, 'THR': 0.0}, 'type': 'monitorReport', 'networkType': '6lowPAN', 'monitorType': 'performance'}
            if not msg['networkController'] == '6lowPAN':
                for ses in server_context.application_context.sessions:
                    ses._document.add_next_tick_callback(partial(
                        plt_update,
                        source=ses._document.select_one(
                            {'name': msg['networkController']}),
                        timestamp=msg['monitorValue']['timestamp'],
                        THR=msg['monitorValue']['THR'],
                        PER=msg['monitorValue']['PER'],
                    ))

        ######## Network status update
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

        ######## Spectral scan features
        if full_msg[0] == b'spectralScanFeatures':
            # monitorValue["dd_s_energy_detection"] = dd_s_energy_detection
            # monitorValue["yvals_energy_detection"] = yvals_energy_detection
            # monitorValue["dd_s_bw"] = dd_s_bw
            # monitorValue["yvals_bw"] = yvals_bw
            # monitorValue["dd_s_freq"] = dd_s_freq
            # monitorValue["yvals_freq"] = yvals_freq

            if msg['networkType'] == "SpectrumFeaturesMonitoring":

                for ses in server_context.application_context.sessions:
                    ses._document.add_next_tick_callback(partial(
                        plot_features_update,
                        source=ses._document.select_one(
                            {'name': 'bw_plt'}),
                        data=dict(
                            BW=msg['monitorValue']['dd_s_bw'],
                            BW_CDF=msg['monitorValue']['yvals_bw'],
                        )
                    ))

                for ses in server_context.application_context.sessions:
                    ses._document.add_next_tick_callback(partial(
                        plot_features_update,
                        source=ses._document.select_one(
                            {'name': 'freq_plt'}),
                        data=dict(
                            FREQ=msg['monitorValue']['dd_s_freq'],
                            FREQ_CDF=msg['monitorValue']['yvals_freq'],
                        )
                    ))

                for ses in server_context.application_context.sessions:
                    ses._document.add_next_tick_callback(partial(
                        plot_features_update,
                        source=ses._document.select_one(
                            {'name': 'duration_plt'}),
                        data=dict(
                            DURATION=msg['monitorValue']['dd_s_energy_detection'],
                            DURATION_CDF=msg['monitorValue']['yvals_energy_detection'],
                        )
                    ))

        ######## ErrorMonitoring
        if full_msg[0] == b'errorStatusUpdate':
            # {u'networkType': u'ErrorMonitoring', u'networkController': u'MONITOR_SERVICE_ERROR', u'type': u'monitorReport', u'monitorType': u'interference',
            # u'monitorValue': {u'error': {u'badfcs': 0.0, u'goodfcs': 34.0, u'badplcp': 0.0, u'goodplcp': 34.0}}}
            if msg['networkType'] == "ErrorMonitoring":
                data_monitor_service_3 = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
                                          "2454": [], "2462": [], "2470": []}
                # {u'badfcs': 0.0, u'goodfcs': 1.0, u'badplcp': 0.0, u'goodplcp': 1.0}
                data_error_sense = {"error": [], "badplcp": [], "goodplcp": [], "badfcs": [], "goodfcs": []}
                counts = []
                if "error" in msg['monitorValue']:
                    error_num = msg['monitorValue']["error"]
                    #print(error_num)

                    for key_table, value_table in data_error_sense.items():
                        if not key_table == "error":
                            counts.append(error_num[key_table])

                    if sum(counts)>0:
                        for ii in range(4):
                            counts[ii] = counts[ii]/sum(counts)*100

                    #print(counts)
                    for ses in server_context.application_context.sessions:
                        ses._document.add_next_tick_callback(partial(
                                    tab_update,
                                    source=ses._document.select_one(
                                        {'name': 'errorStatusBar'}),
                                    data = dict(
                                        x=fruits,
                                        top=counts,
                                        color=Spectral4,
                                        ),
                        ))

                    #{'type': 'monitorReport', 'networkController': 'MONITOR_SERVICE_ERROR', 'monitorType': 'interference', 'networkType': 'ErrorMonitoring',
                    # 'monitorValue': {'error': {'badplcp': 35.0, 'goodplcp': 36.0, 'badfcs': 9.0, 'goodfcs': 22.0}, 'ZigBee': {'2462': [2, 237.41300000000007]}}}
                # #u'WiFi': {u'2462': [20, 33.58]}
                for key_table, value_table in data_monitor_service_3.items():
                    if not key_table == "Interference":
                        for interfLabel in ["Busy", "WIFI", "LTE", "ZigBee"]:
                            if interfLabel in msg['monitorValue']:
                                receivedFreq = msg['monitorValue'][interfLabel]
                                if key_table in receivedFreq:
                                    data_monitor_service_3[key_table].append(receivedFreq[key_table])
                                else:
                                    data_monitor_service_3[key_table].append([])
                            else:
                                data_monitor_service_3[key_table].append([])

                #print(data_monitor_service_3)

        ##############
        ###DATA wiplus
        ##############
        if full_msg[0] == b'specStatusUpdate_2':
            data_monitor_service_1 = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
                                      "2454": [], "2462": [], "2470": []}
            msg_monitor_value = msg["monitorValue"]
            #print(msg_monitor_value)
            for key_table in data_monitor_service_1["Interference"]:
                # print(key_table)
                if key_table in msg_monitor_value:
                    msg_monitor_value_freq = msg_monitor_value[key_table]
                    for key_freq in ["2462"]:
                        if key_freq in msg_monitor_value_freq:
                            data_monitor_service_1[str(int(key_freq) - 8)].append([round(msg_monitor_value_freq[key_freq][0]/3), msg_monitor_value_freq[key_freq][1]])
                            data_monitor_service_1[key_freq].append([round(msg_monitor_value_freq[key_freq][0]/3), msg_monitor_value_freq[key_freq][1]])
                            data_monitor_service_1[str(int(key_freq) + 8)].append([round(msg_monitor_value_freq[key_freq][0]/3), msg_monitor_value_freq[key_freq][1]])
                        else:
                            data_monitor_service_1[str(int(key_freq) - 8)].append([])
                            data_monitor_service_1[key_freq].append([])
                            data_monitor_service_1[str(int(key_freq) + 8)].append([])
                else:
                    data_monitor_service_1["2454"].append([])
                    data_monitor_service_1["2462"].append([])
                    data_monitor_service_1["2470"].append([])
            # print(data_monitor_service_1)

        ###################
        ##DATA interference Detection
        ####################
        if full_msg[0] == b'specStatusUpdate':
            data_monitor_service_2 = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
                                      "2454": [], "2462": [], "2470": []}
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
        if full_msg[0] == b'specStatusUpdate' or full_msg[0] == b'specStatusUpdate_2' or full_msg[0] == b'errorStatusUpdate':
            data_monitor_service_global_2 = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
                                             "2454": [], "2462": [], "2470": []}
            for key_table, value_table in data_monitor_service_global_2.items():
                if not key_table == "Interference":
                    for ii in range(3):
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
                    if len(data_monitor_service_3[key_table][3]) > 0 :
                        data_monitor_service_global_2[key_table].append(data_monitor_service_3[key_table][3])
                    else:
                        data_monitor_service_global_2[key_table].append([])
            #print(data_monitor_service_global_2)

            for ses in server_context.application_context.sessions:
                ses._document.add_next_tick_callback(partial(
                            tab_update,
                            source=ses._document.select_one(
                                {'name': 'interferenceStatusUpdate'}),
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

