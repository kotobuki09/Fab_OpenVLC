import socket
import subprocess
from serial_wrappers.lib_serial import *
import threading
import logging
import base64
import ctypes
import binascii
import traceback
import sys

class SerialdumpWrapper(SerialWrapper):

    def __init__(self, serial_dev, interface):
        self.log = logging.getLogger('SerialdumpWrapper.' + serial_dev)
        self.__interface = interface
        self.__serial_dev = serial_dev
        if socket.gethostname().find("wilab2") == -1:
            self.serialdump_process = subprocess.Popen(['../../agent_modules/contiki/serial_wrappers/bin/serialdump-linux',
                                                        '-b115200', serial_dev], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        else:
            self.serialdump_process = subprocess.Popen(['sudo', '../../agent_modules/contiki/serial_wrappers/bin/serialdump-linux',
                                                        '-b115200', '/dev/rm090'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.__rx_thread = None
        self.__rx_callback = None
        self.__thread_stop = None

    def __print_byte_array(self, b):
        print(' '.join('{:02x}'.format(x) for x in b))

    def set_serial_rxcallback(self, rx_callback):
        if self.__rx_thread != None:
            self.__thread_stop.set()
        self.__thread_stop = threading.Event()
        self.__rx_callback = rx_callback
        self.__rx_thread = threading.Thread(target=self.__serial_listen, args=(self.__rx_callback, self.__thread_stop,))
        self.__rx_thread.daemon = True
        self.__rx_thread.start()

    def serial_send(self, payload, payload_len):
        # self.__print_byte_array(payload)
        #self.log.info("trying encoding data base64 string %s", binascii.b2a_base64(payload))
        encoded_line = base64.b64encode(payload)
        serial_hdr = SerialHeader()
        serial_hdr.decoded_len = payload_len + ctypes.sizeof(SerialHeader)
        serial_hdr.encoded_len = len(encoded_line) + ctypes.sizeof(SerialHeader)
        for i in range(0, ctypes.sizeof(SerialHeader) - 2):
            serial_hdr.padding[i] = 70
        msg = bytearray()
        msg.extend(serial_hdr)
        msg.extend(encoded_line)
        msg.append(0x0a)
        #self.log.info("full encoded line %s%s",bytearray(serial_hdr).decode(), binascii.b2a_base64(payload))
        # self.__print_byte_array(msg)
        self.serialdump_process.stdin.write(msg.decode(encoding="utf-8", errors="ignore"))
        self.serialdump_process.stdin.flush()

    def __serial_listen(self, rx_callback, stop_event):
        while not stop_event.is_set():
            line = self.serialdump_process.stdout.readline().strip()
            #u = binascii.hexlify(line)
            #print(line)
            if line != '':
                if line[2:ctypes.sizeof(SerialHeader)] == 'FFFFFFFF':
                    try:
                        enc_len = SerialWrapper.fm_serial_header.unpack(bytearray(line[0:2], 'utf-8'))[1]
                        dec_line = base64.b64decode(line[ctypes.sizeof(SerialHeader):enc_len])
                        #print(dec_line)
                        rx_callback(0, bytearray(dec_line))
                    except (RuntimeError, TypeError, NameError):
                        rx_callback(1, None)
                        traceback.print_exc(file=sys.stdout)
                else:
                    self.log.info("PRINTF: %s", line)
