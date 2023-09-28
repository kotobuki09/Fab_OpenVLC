import logging
import random
import wishful_upis as upis
import wishful_framework as wishful_module
import time
import logging
import socket
import datetime
import thread

__author__ = "Piotr Gawlowicz, Anatolij Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, zubow}@tkn.tu-berlin.de"

"""
Implementation of UPI_R and UPI_N interfaces for the IEEE 802.11 SDR platform from National Instruments (NI).

TODO:
- automatic bitfile downloading
"""

@wishful_module.build_module
class NiSdrModule(wishful_module.AgentModule):
    def __init__(self):
        super(NiSdrModule, self).__init__()
        self.log = logging.getLogger('wifi_module.main')
        self.MSG_UDP_IP = "127.0.0.1"
        self.MSG_UDP_TX_PORT = 12345
        self.MSG_UDP_RX_PORT = 12346

    @wishful_module.bind_function(upis.net.gen_layer2_traffic)
    def gen_layer2_traffic(self, iface, num_packets, pinter, **kwargs):

        #iface = myargs["iface"]

        self.log.info('gen80211L2LinkProbing()')
        # get my MAC HW address
        #myMacAddr = self.getHwAddr({'iface': iface})
        #dstMacAddr = 'ff:ff:ff:ff:ff:ff'

        if num_packets > 255:
            num_packets = 255

        MSG_SIZE = 128
        MESSAGE = bytearray(MSG_SIZE)

        self.log.info("UDP target IP: %s " % self.MSG_UDP_IP)
        self.log.info("UDP target port: %d" % self.MSG_UDP_TX_PORT)
        self.log.info("message len: %d" % len(MESSAGE))

        sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP

        for pi in range(num_packets):
            sock.sendto(MESSAGE, (self.MSG_UDP_IP, self.MSG_UDP_TX_PORT))
            time.sleep(pinter)

    @wishful_module.bind_function(upis.net.sniff_layer2_traffic)
    def sniff_layer2_traffic(self, iface, sniff_timeout, **kwargs):

        #iface = myargs["iface"]

        self.log.info('sniff_layer2_traffic()')

        BUFFER_SZ = 4096

        rx_pkts = {}
        rx_pkts['res'] = 0
        def ip_monitor_callback():
            sock = socket.socket(socket.AF_INET, # Internet
                                 socket.SOCK_DGRAM) # UDP
            sock.bind((self.MSG_UDP_IP, self.MSG_UDP_RX_PORT))

            while True:
                data, addr = sock.recvfrom(BUFFER_SZ) # buffer size is 1024 bytes
                rx_pkts['res'] = rx_pkts['res'] + 1

        thread.start_new_thread(ip_monitor_callback, ())

        # wait until timeout
        start = datetime.datetime.now()
        while True:
            now = datetime.datetime.now()
            if (now - start).seconds < sniff_timeout:
                time.sleep(0.1)
            else:
                break

        numRxPkts = rx_pkts['res']
        self.log.info('sniff80211L2LinkProbing(): rxpackets= %d' % numRxPkts)
        return numRxPkts