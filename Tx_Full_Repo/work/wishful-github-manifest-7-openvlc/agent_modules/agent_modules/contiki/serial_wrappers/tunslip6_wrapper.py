from .serial_wrappers.lib_serial import *
import logging

class Tunslip6Wrapper(SerialWrapper):
	
	def __init__(self,serial_dev,rx_callback,interface):
		self.log = logging.getLogger()
		self.serial_dev = serial_dev
		self.__interface = interface
		self.__rx_callback = rx_callback
		self.log.fatal("Not yet implememented")

	def __print_byte_array(self,b):
		print ' '.join('{:02x}'.format(x) for x in b)
	
	def set_serial_rxcallback(rx_callback):
		self.__rx_callback = rx_callback

	def serial_send(self,payload, payload_len):
		self.log.fatal("Not yet implememented")			
	
	def __serial_listen(self):
		self.log.fatal("Not yet implememented")

