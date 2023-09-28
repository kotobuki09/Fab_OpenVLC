import json
import logging
import zmq
import numpy as np

from datetime import datetime
from functools import partial
from tornado import gen


@gen.coroutine
def plt_update(source, timestamp, THR, PER, TX_FRAME):
    source.stream(dict(
        timestamp=[datetime.fromtimestamp(timestamp)],
        THR=[THR],
        PER=[PER],
        TX_FRAME=[TX_FRAME],
    ), 30)


@gen.coroutine
def plt_update_cumulative(source, timestamp, THR):
    source.stream(dict(
        timestamp=[datetime.fromtimestamp(timestamp)],
        THR=[THR],
    ), 30)


@gen.coroutine
def tab_update(source, data):
    source.data = data


def stats_listener(endpoint, server_context):
    logging.info('Starting statistics listener on %s', endpoint)

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, b'monitorReport')
    socket.setsockopt(zmq.SUBSCRIBE, b'cumulativeMonitorReport')
    socket.setsockopt(zmq.SUBSCRIBE, b'networkStatusUpdate')
    #socket.setsockopt(zmq.SUBSCRIBE, b'specStatusUpdate')
    #socket.setsockopt(zmq.SUBSCRIBE, b'specStatusUpdate_2')
    socket.bind(endpoint)

    while True:
        full_msg = socket.recv_multipart()
        #print(full_msg)
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
                    TX_FRAME=msg['monitorValue']['TX_FRAME'],
                ))
                # print(msg['networkController'])
                # plot_object = ses._document.select_one({'name': msg['networkController']})
                # print(plot_object.name)

        if full_msg[0] == b'cumulativeMonitorReport':
            for ses in server_context.application_context.sessions:
                ses._document.add_next_tick_callback(partial(
                    plt_update_cumulative,
                    source=ses._document.select_one(
                        {'name': msg['networkController']}),
                    timestamp=msg['monitorValue']['timestamp'],
                    THR=msg['monitorValue']['THR'],
                ))
                # print(msg['networkController'])
                # plot_object = ses._document.select_one({'name': msg['networkController']})
                # print(plot_object.name)

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


        # if full_msg[0] == b'specStatusUpdate':
        #     ######### SpectrumMonitoring
        #     ######## ErrorMonitoring
		#
        #     if msg['networkType'] == "ErrorMonitoring":
        #         # {u'monitorValue': {u'error': {u'badfcs': 0.0, u'goodfcs': 1.0, u'badplcp': 0.0, u'goodplcp': 1.0}}, u'networkController': u'MONITOR_SERVICE_CNIT', u'type': u'monitorReport',
        #         # u'monitorType': u'interference', u'networkType': u'ErrorMonitoring'}
        #         # {u'badfcs': 0.0, u'goodfcs': 1.0, u'badplcp': 0.0, u'goodplcp': 1.0}
        #         data_error_sense = {"error": [], "badplcp": [], "goodplcp": [], "badfcs": [], "goodfcs": []}
        #         data_monitor_service = {"Interference": ['WIFI', 'LTE', 'ZigBee'], "2454": [], "2462": [], "2470": []}
		#
        #         if "error" in msg['monitorValue']:
        #             error_num = msg['monitorValue']["error"]
        #             #print(error_num)
		#
        #             for key_table, value_table in data_error_sense.items():
        #                 if key_table == "error":
        #                     data_error_sense[key_table].append("NUM")
        #                 else:
        #                     data_error_sense[key_table].append(error_num[key_table])
		#
        #             for ses in server_context.application_context.sessions:
        #                 ses._document.add_next_tick_callback(partial(
        #                             tab_update,
        #                             source=ses._document.select_one(
        #                                 {'name': 'errorStatusUpdate'}),
        #                             data = data_error_sense,
        #                         ))
		#
        #         #u'WiFi': {u'2462': [20, 33.58]}
        #         for key_table, value_table in data_monitor_service.items():
        #             if not key_table == "Interference":
        #                 for interfLabel in ["WiFi", "LTE", "ZigBee"]:
        #                     if interfLabel in msg['monitorValue']:
        #                         receivedFreq = msg['monitorValue'][interfLabel]
        #                         if key_table in receivedFreq:
        #                             data_monitor_service[key_table].append(receivedFreq[key_table])
        #                         else:
        #                             data_monitor_service[key_table].append([])
        #                     else:
        #                         data_monitor_service[key_table].append([])
		#
        #         for ses in server_context.application_context.sessions:
        #             ses._document.add_next_tick_callback(partial(
        #                 tab_update,
        #                 source=ses._document.select_one(
        #                     {'name': 'interferenceStatusUpdate'}),
        #                 data=data_monitor_service,
        #             ))


                    # if full_msg[0] == b'specStatusUpdate_2':
            #     ##############
            #     ###DATA wiplus
            #     ##############
            #     data_monitor_service_1 = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
            #                               "2404": [], "2412": [], "2420": [],
            #                               "2429": [], "2437": [], "2445": [],
            #                               "2454": [], "2462": [], "2470": [],
            #                               "2476": [], "2484": [], "2492": []}
            #     msg_monitor_value = msg["monitorValue"]
            #     for key_table in data_monitor_service_1["Interference"]:
            #         # print(key_table)
            #         if key_table in msg_monitor_value:
            #             msg_monitor_value_freq = msg_monitor_value[key_table]
            #             for key_freq in ["2412", "2437", "2462", "2484"]:
            #                 if key_freq in msg_monitor_value_freq:
            #                     data_monitor_service_1[str(int(key_freq) - 8)].append([round(msg_monitor_value_freq[key_freq][0]/3), msg_monitor_value_freq[key_freq][1]])
            #                     data_monitor_service_1[key_freq].append([round(msg_monitor_value_freq[key_freq][0]/3), msg_monitor_value_freq[key_freq][1]])
            #                     data_monitor_service_1[str(int(key_freq) + 8)].append([round(msg_monitor_value_freq[key_freq][0]/3), msg_monitor_value_freq[key_freq][1]])
            #                 else:
            #                     data_monitor_service_1[str(int(key_freq) - 8)].append([])
            #                     data_monitor_service_1[key_freq].append([])
            #                     data_monitor_service_1[str(int(key_freq) + 8)].append([])
            #         else:
            #             data_monitor_service_1["2404"].append([])
            #             data_monitor_service_1["2412"].append([])
            #             data_monitor_service_1["2420"].append([])
			#
            #             data_monitor_service_1["2429"].append([])
            #             data_monitor_service_1["2437"].append([])
            #             data_monitor_service_1["2445"].append([])
			#
            #             data_monitor_service_1["2454"].append([])
            #             data_monitor_service_1["2462"].append([])
            #             data_monitor_service_1["2470"].append([])
			#
            #             data_monitor_service_1["2476"].append([])
            #             data_monitor_service_1["2484"].append([])
            #             data_monitor_service_1["2492"].append([])
			#
            #     # print(data_monitor_service_1)
			#
            # if full_msg[0] == b'specStatusUpdate':
            #     ###################
            #     ##DATA interference Detection
            #     ####################
            #     data_monitor_service_2 = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
            #                               "2404": [[], [], [], []], "2412": [[], [], [], []], "2420": [[], [], [], []],
            #                               "2429": [[], [], [], []], "2437": [[], [], [], []], "2445": [[], [], [], []],
            #                               "2454": [], "2462": [], "2470": [],
            #                               "2476": [[], [], [], []], "2484": [[], [], [], []], "2492": [[], [], [], []]}
            #     msg_monitor_value = msg["monitorValue"]
            #     for key_table in data_monitor_service_2["Interference"]:
            #         if key_table in msg_monitor_value:
            #             key = key_table
            #             # print(key)
            #             data_temp = []
            #             for key_freq, value_freq in msg_monitor_value[key].items():
            #                 if int(key_freq) < 2458:
            #                     data_temp.append([round(value_freq[0]), value_freq[1]])
            #             if len(data_temp) > 0:
            #                 data_monitor_service_2["2454"].append(np.mean(data_temp, 0).tolist())
            #             else:
            #                 data_monitor_service_2["2454"].append([])
			#
            #             data_temp = []
            #             for key_freq, value_freq in msg_monitor_value[key].items():
            #                 if int(key_freq) > 2458 and int(key_freq) < 2465:
            #                     data_temp.append([round(value_freq[0]), value_freq[1]])
            #             if len(data_temp) > 0:
            #                 data_monitor_service_2["2462"].append(np.mean(data_temp, 0).tolist())
            #             else:
            #                 data_monitor_service_2["2462"].append([])
			#
            #             data_temp = []
            #             for key_freq, value_freq in msg_monitor_value[key].items():
            #                 if int(key_freq) > 2465:
            #                     data_temp.append([round(value_freq[0]), value_freq[1]])
            #             if len(data_temp) > 0:
            #                 data_monitor_service_2["2470"].append(np.mean(data_temp, 0).tolist())
            #             else:
            #                 data_monitor_service_2["2470"].append([])
			#
            #         else:
            #             data_monitor_service_2["2454"].append([])
            #             data_monitor_service_2["2462"].append([])
            #             data_monitor_service_2["2470"].append([])
			#
            #     # print(data_monitor_service_2)
			#
            # ############
            # ###DATA global monitor service
            # ###########
            # # data_monitor_service_global = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
            # #                                "2404": [], "2412": [], "2420": [],
            # #                                "2429": [], "2437": [], "2445": [],
            # #                                "2454": [], "2462": [], "2470": [],
            # #                                "2476": [], "2484": [], "2492": []}
            # # for key_table, value_table in data_monitor_service_global.items():
            # #     if not key_table == "Interference":
            # #         data_monitor_service_global[key_table].append(data_monitor_service_1[key_table])
            # #         data_monitor_service_global[key_table].append(data_monitor_service_2[key_table])
            # # print(data_monitor_service_global)
			#
            # data_monitor_service_global_2 = {"Interference": ['Busy', 'WIFI', 'LTE', 'ZigBee'],
            #                                  "2404": [], "2412": [], "2420": [],
            #                                  "2429": [], "2437": [], "2445": [],
            #                                  "2454": [], "2462": [], "2470": [],
            #                                  "2476": [], "2484": [], "2492": []}
            # for key_table, value_table in data_monitor_service_global_2.items():
            #     if not key_table == "Interference":
            #         for ii in range(4):
            #             # print(key_table, " : ", ii)
            #             data_temp = []
            #             if len(data_monitor_service_1[key_table][ii]) > 0 and len(data_monitor_service_2[key_table][ii]) > 0:
			#
            #                 data_temp.append(data_monitor_service_1[key_table][ii])
            #                 data_temp.append(data_monitor_service_2[key_table][ii])
            #                 # print(data_temp)
            #                 data_monitor_service_global_2[key_table].append(np.mean(data_temp, 0).tolist())
            #             # print(data_monitor_service_global_2[key_table])
            #             elif len(data_monitor_service_1[key_table][ii]) > 0:
            #                 data_monitor_service_global_2[key_table].append(data_monitor_service_1[key_table][ii])
            #             elif len(data_monitor_service_2[key_table][ii]) > 0:
            #                 data_monitor_service_global_2[key_table].append(data_monitor_service_2[key_table][ii])
            #             else:
            #                 data_monitor_service_global_2[key_table].append([])
            # # print(data_monitor_service_global_2)
			#
            # for ses in server_context.application_context.sessions:
            #     ses._document.add_next_tick_callback(partial(
            #                 tab_update,
            #                 source=ses._document.select_one(
            #                     {'name': 'monitorServiceStatusUpdate'}),
            #                 data = data_monitor_service_global_2,
            #             ))




# @gen.coroutine
# def usrp_plot_update(source, spectrogram):
#     source.update(data=dict(spectrogram=[spectrogram]))
#
#
# @gen.coroutine
# def usrp_fig_update(source, fc, bw, size):
#     source.update(data=dict(fc=[fc], bw=[bw], size=[size]))
#
#
# def usrp_listener(endpoint, server_context, name="spectrogram"):
#     logging.info('Starting USRP listener on %s', endpoint)
#
#     context = zmq.Context()
#     socket = context.socket(zmq.SUB)
#     socket.setsockopt(zmq.SUBSCRIBE, b'gnuradio.spectrogram')
#     socket.bind(endpoint)
#
#     while True:
#         full_msg = socket.recv_multipart()
#
#         info = json.loads(full_msg[1])
#         spectrogram = np.frombuffer(full_msg[2], dtype=np.float32).reshape(
#             int(info['l']), int(info['w']))
#
#         for ses in server_context.application_context.sessions:
#             ses._document.add_next_tick_callback(partial(
#                 usrp_plot_update,
#                 source=ses._document.select_one({'name': name}),
#                 spectrogram=spectrogram,
#             ))
#
#             fc = int(info['fc'])
#             bw = int(info['bw'])
#             size = int(info['l'])
#             ses._document.add_next_tick_callback(partial(
#                 usrp_fig_update,
#                 source=ses._document.select_one(
#                     {'name': name + '_vars'}),
#                 fc=fc,
#                 bw=bw,
#                 size=size,
#             ))

