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

    def set_channel(self, channel):
        command_list = {"CHANNEL": {}}
        command_list["CHANNEL"] = channel
        self.send_commands(command_list)

    def set_cca_threshold(self, cca_threshold):
        command_list = {"CCA_THRESHOLD": {}}
        command_list["CCA_THRESHOLD"] = cca_threshold
        self.send_commands(command_list)

