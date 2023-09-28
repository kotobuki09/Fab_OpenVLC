import abc
import struct
from ctypes import *

class SerialHeader(Structure):
	_fields_ = [("decoded_len",c_ubyte),("encoded_len",c_ubyte),("padding",c_ubyte*8)]

class SerialWrapper():
	__metaclass__ = abc.ABCMeta
	
	fm_serial_header = struct.Struct('B B')
	
	@abc.abstractmethod
	def serial_send(payload, payload_len):
		return
	
	@abc.abstractmethod
	def set_serial_rxcallback(rx_callback):
		return
