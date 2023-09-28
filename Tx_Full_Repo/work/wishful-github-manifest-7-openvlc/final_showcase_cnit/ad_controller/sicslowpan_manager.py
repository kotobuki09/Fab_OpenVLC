import time
import json
import struct
from lib.kvsimple import KVMsg

__author__ = "Jan Bauwens"
__copyright__ = "Copyright (c) 2018, Ghent University - IMEC"
__version__ = "0.1.0"
__email__ = "jan.bauwens2@ugent.be"


class SICSLOWPANNetwork:
    def __init__(self):
        self.network = None
        pass

    def set_network(self, network):
        self.network = network

    def set_publisher(self, publisher):
        self.publisher = publisher

    def send_commands(self,command_list):
        msg = None
        if self.network is not None:
            msg = {
                "type": "publisherUpdate",
                "involvedController": [self.network.name],
                "commandList": {}
            }
            msg["commandList"] = {self.network.solution[0]: {}}            
            msg["commandList"][self.network.solution[0]] = command_list
        if msg:
            print('update message %s' % str(msg))
            # Distribute as key-value message
            # sequence_publisher += 1
            kvmsg = KVMsg(1)
            kvmsg.key = b"generic"
            kvmsg.body = json.dumps(msg).encode('utf-8')
            kvmsg.send(self.publisher)

    def notify_interference_report(self, interfence_message):
        # print(interfence_message)
        # print(interfence_message["monitorValue"])
        #{'networkController': 'WIPLUS_LTE_U_DETECTOR', 'monitorValue': {'WIFI': {'2412': [20, 0.01], '2462': [20, 0.05]}, 'Busy': {'2412': [20, 0.01], '2437': [20, 0.01], '2462': [20, 0.09]}},
        # 'monitorType': 'interference', 'type': 'monitorReport', 'networkType': 'DETECTOR'}
        #{'type': 'publisherUpdate', 'involvedController': ['6lowPAN'],
        # 'commandList': {'blacklisting': {'6LOWPAN_BLACKLIST': {'WIFI': {'2412': [20, 0.01], '2437': [20, 0.06], '2462': [20, 0.3]}, 'Busy': {'2412': [20, 0.02], '2437': [20, 0.07], '2462': [20, 0.48]}}}}}
        #{'type': 'monitorReport', 'monitorValue': {'WIFI': {'2412': [20, 0.01], '2437': [20, 0.06], '2462': [20, 0.3]}, 'Busy': {'2412': [20, 0.02], '2437': [20, 0.07], '2462': [20, 0.48]}},
        # 'networkType': 'DETECTOR', 'monitorType': 'interference', 'networkController': 'WIPLUS_LTE_U_DETECTOR'}

        interfence_message["monitorValue"] = {'WIFI': {'2412': [20, 1.0], '2437': [20, 1.0], '2484': [20, 1.0]}, 'Busy': {'2412': [20, 1.0], '2437': [20, 1.0], '2484': [20, 1.0] }}
        if "Busy" in interfence_message["monitorValue"]:
            if len(interfence_message["monitorValue"]["Busy"])>0:
                print("send 6LOWPAN_BLACKLIST to zigbee")
                command_list = {"6LOWPAN_BLACKLIST": {}}
                command_list["6LOWPAN_BLACKLIST"] = interfence_message["monitorValue"]
                self.send_commands(command_list)

    def start_three_way_tdma(self):
        command_list = {"LTE_WIFI_ZIGBEE": {}}
        command_list["LTE_WIFI_ZIGBEE"] = True
        self.send_commands(command_list)
    
    def stop_three_way_tdma(self):
        command_list = {"LTE_WIFI_ZIGBEE": {}}
        command_list["LTE_WIFI_ZIGBEE"] = False
        self.send_commands(command_list)
