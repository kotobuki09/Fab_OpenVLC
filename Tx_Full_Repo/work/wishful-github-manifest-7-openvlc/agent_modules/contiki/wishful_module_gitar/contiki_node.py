from runtime.connectors.dot802154_contiki.SensorNode import *
from runtime.connectors.dot802154_contiki.TAISC.libTAISC import *
import csv
import ctypes
from array import *
import time
import base64
import logging
import subprocess
import thread
import serial
import errno
from upis.upi_rn import UPIError
import socket

typeAsInt = {"UINT8_T":0,"INT8_T" : 1,"UINT16_T" : 2,"INT16_T" : 3,"UINT32_T" : 4,"INT32_T" : 5,"UINT64_T" : 6,"INT64_T" : 7,"BOOL_T" : 8,"CHAR_T" : 9,"STRING_T" : 10,"STRUCT_T" : 11};
typeAsDType = {"UINT8_T":'u1',"INT8_T" : 'i1' ,"UINT16_T" : 'u2',"INT16_T" : 'i2',"UINT32_T" : 'u4',"INT32_T" : 'i4',"UINT64_T" : 'u8',"INT64_T" : 'i8',"BOOL_T" : 'b',"CHAR_T" : 'U',"STRING_T" : 'S',"STRUCT_T" : 'O'};

def readResponseHeader(response_message):
    tup = fm_control_header.unpack(response_message[0:6])
    return control_hdr_t(tup[0],tup[1],tup[2])

def readParamHeader(response_message):
    tup = fm_param_header.unpack(response_message[0:ctypes.sizeof(param_hdr_t)])
    return param_hdr_t(tup[0], tup[1], tup[2])


class ContikiNode():
    
    def __init__(self,dct_config):
        self.log = logging.getLogger('contiki_module.ContikiNode')
        # ~ self.netstack_radio = dct_config['NetstackRadio']
        # ~ self.netstack_rdc = dct_config['NetstackRdc']
        # ~ self.netstack_mac = dct_config['NetstackMac']
        # ~ self.netstack_net = dct_config['NetstackNet']
        # ~ self.contiki_apps = dct_config['ContikiApps']
        # ~ self.contiki_examples = dct_config['ContikiExamples']
        self.radio_driver = dct_config['RadioDriver']
        self.radio_ctrl_ext = dct_config['RadioControlExtensions']
        self.radio_interface = dct_config['RadioInterface']
        self.dct_radio_programs = dct_config['RadioPrograms']
        self.network_driver = dct_config['NetworkDriver']
        self.network_ctrl_ext = dct_config['NetworkControlExtensions']
        self.serial_interface = dct_config['SerialInterface']
        self.serial_dev = dct_config['SerialDev']
        self.sensor_platform = dct_config['SensorPlatform']
        
        if self.radio_driver == 'taisc':
            from .libTAISC import TAISCRadio
        elif self.radio_driver == 'contikimac':
            self.log.fatal('Not implemented yet')
        elif self.radio_driver == 'tsch':
            self.log.fatal('Not implemented yet')
        
        
        radio_platform = dct_config['RadioPlatform']
        radio_parameters = dct_config['RadioParameters']
        radio_interface = dct_config['RadioInterface']
        radio_programs = dct_config['RadioPrograms']
        self.mac_address = int(dct_config['MacAddress'])
        network_stack = dct_config['NetworkStack']
        network_parameters = dct_config['NetworkParameters']
        serial_interface = dct_config['SerialInterface']
        serial_port = dct_config['SerialPort']
        sensor_platform = dct_config['SensorPlatform']
        self.radio_platform_str = dct_config['RadioInterface'] + ',' + dct_config['RadioPlatform']
                
        # select the radio platform implementation
        if radio_platform == 'TAISC':
            self.radio_engine = TAISCRadio('./runtime/connectors/dot802154_contiki/TAISC/' + radio_parameters,radio_programs,self.mac_address,self)
        elif radio_platform == 'ContikiMAC':
            self.radio_engine = ContikiMACRadio(radio_parameters,self)
        else:
            self.log.fatal("Radio plaform %s does not exist",radio_platform)
        
        # select the network stack implementation
        if network_stack == 'ContikiIPv6':
            self.network_engine = ContikiIPv6()
        elif network_stack == 'ContikiIPv4':
            self.network_engine = ContikiIPv4()
        elif network_stack == 'ContikiRime':
            self.network_engine = ContikiRime('./runtime/connectors/dot802154_contiki/contiki/' + network_parameters,self)
        else:
            self.log.fatal("Network stack %s does not exist",network_stack)
        
        # select the serial interface   
        if serial_interface == 'ContikiSerialDump':
            self.serial_interface = ContikiSerialDump(serial_port,self.__SerialResponseHandler,self.mac_address)
        elif serial_interface == 'SLIP':
            self.serial_interface = ContikiSLIP(serial_port,self.__SerialResponseHandler,self.mac_address)      
        else:
            self.log.fatal("Serial interface %s does not exist",serial_interface)
        
        #~ self.unique_name_to_id = {}
        self.sequence_number = 0
        self.unique_id_to_name = {}
        self.unique_name_to_param = {}
        self.unique_name_to_eventcb  = {}
        self.__response_message = bytearray()
        self.__awaiting_response = False
        try:
            file_rp = open('./runtime/connectors/dot802154_contiki/TAISC/' + radio_parameters,'rt')
            reader = csv.DictReader(file_rp)
            for row in reader:
                self.unique_id_to_name[int(row['unique_id'])] = row['unique_name']
                if row['type'] == "STRUCT_T":
                    self.unique_name_to_param[row['unique_name']] = SensorParameter(int(row['unique_id']),typeAsInt[row['type']],int(row['length']),row['struct_format'])
                else:
                    self.unique_name_to_param[row['unique_name']] = SensorParameter(int(row['unique_id']),typeAsInt[row['type']],int(row['length']),typeAsDType[row['type']])
            file_np = open('./runtime/connectors/dot802154_contiki/contiki/' + network_parameters,'rt')
            reader = csv.DictReader(file_np)
            for row in reader:
                self.unique_id_to_name[int(row['unique_id'])] = row['unique_name']
                if row['type'] == "STRUCT_T":
                    self.unique_name_to_param[row['unique_name']] = SensorParameter(int(row['unique_id']),typeAsInt[row['type']],int(row['length']),row['struct_format'])
                else:
                    self.unique_name_to_param[row['unique_name']] = SensorParameter(int(row['unique_id']),typeAsInt[row['type']],int(row['length']),typeAsDType[row['type']])
        except Exception as e:
            self.log.fatal("An error occurred while reading parameters: %s" % e)
        finally:
            file_rp.close()
            file_np.close()
        pass
    
    def getParameterUniqueID(uniqueName):
        if uniqueName in self.unique_name_to_param:
            return self.unique_name_to_param[uniqueName].param_uid
        return -1
    
    def getParameterUniqueName(uniqueID):
        if uniqueID in self.unique_id_to_name:
            return self.unique_id_to_name[uniqueID]
        return -1
    
    def setParameters(self,param_key_values):
        message = bytearray()
        control_hdr = control_hdr_t(ControlOpCode.PARAM_SET,0,++self.sequence_number)
        for key in param_key_values:
            if key in self.unique_name_to_param:
                p = self.unique_name_to_param[key]
                message.extend(param_hdr_t(p.param_uid,p.param_type,p.param_len))
                if p.param_type == 11:
                    import numpy as np
                    dt = np.dtype(p.struct_format).newbyteorder('>')
                    a = bytearray(np.array(tuple(param_key_values[key],),dt))
                    message.extend(a)
                else:
                    s = struct.Struct('>' + SensorParameter.PARAM_TYPES[p.param_type].format)
                    message.extend(s.pack(param_key_values[key]))
                control_hdr.num_param+=1
            else:
                self.log.info("ContikiNode%i- setParameters: parameter \"%s\" not found", self.mac_address,key)
        if control_hdr.num_param > 0:
            message = bytearray(control_hdr.to_bin()) + message
            num_attempts = 0
            response_error = 0
            while num_attempts < 4:
                num_attempts += 1
                self.__awaiting_response = True
                self.serial_interface.serial_send(message,len(message))
                if self.__waitForResponse() and self.__response_message != None:
                    response_control_hdr = readResponseHeader(self.__response_message)
                    if response_control_hdr.opcode != ControlOpCode.ERROR_RESPONSE:
                        if response_control_hdr == control_hdr:
                            param_key_values = {}
                            line_ptr = 6
                            for i in range(0,response_control_hdr.num_param):
                                p_hdr = readParamHeader(self.__response_message[line_ptr:])
                                line_ptr+=ctypes.sizeof(param_hdr_t)
                                error = INT8_T.unpack(self.__response_message[line_ptr:line_ptr+1])[0]
                                line_ptr+=1
                                param_key_values[self.unique_id_to_name[p_hdr.uid]] = error
                            return param_key_values
                        else:
                            response_error = errno.EPROTO
                    else:
                        response_error = errno.EPROTO
                else:
                    response_error = errno.ETIMEDOUT
            self.log.info("ContikiNode%i setParameters: could not send request, error %i ", self.mac_address,response_error)
            self.log.info("FAULT PROTOCOL HEADER: %s", str(param_key_values))
            return response_error
        else:
            self.log.info("ContikiNode%i setParameters: no valid parameters %s",self.mac_address, param_key_values)
        return errno.EINVAL
    
    def getParameters(self,param_keys):
        message = bytearray()
        control_hdr = control_hdr_t(ControlOpCode.PARAM_GET,0,++self.sequence_number)
        for key in param_keys:
            if key in self.unique_name_to_param:
                p = self.unique_name_to_param[key]
                message.extend(param_hdr_t(p.param_uid,p.param_type,p.param_len))
                control_hdr.num_param+=1
            else:
                self.log.info("ContikiNode%i- getParameters: parameter \"%s\" not found",self.mac_address, key)
        if control_hdr.num_param > 0:
            message = bytearray(control_hdr.to_bin()) + message
            num_attempts = 0
            response_error = 0
            while num_attempts < 4:
                num_attempts += 1
                self.__awaiting_response = True
                self.serial_interface.serial_send(message,len(message))
                if self.__waitForResponse() and self.__response_message != None:
                    response_control_hdr = readResponseHeader(self.__response_message)
                    if response_control_hdr.opcode != ControlOpCode.ERROR_RESPONSE:
                        if response_control_hdr == control_hdr:
                            param_key_values = {}
                            line_ptr = 6
                            for i in range(0,response_control_hdr.num_param):
                                p_hdr = readParamHeader(self.__response_message[line_ptr:])
                                line_ptr+=ctypes.sizeof(param_hdr_t)
                                import numpy as np
                                frmt = self.unique_name_to_param[self.unique_id_to_name[p_hdr.uid]].struct_format
                                dt = np.dtype(frmt)
                                value = np.frombuffer(np.ndarray(shape=(),dtype=dt,buffer=self.__response_message[line_ptr:line_ptr+p_hdr.len]).byteswap(),dt)[0]
                                line_ptr+=p_hdr.len
                                param_key_values[self.unique_id_to_name[p_hdr.uid]] = value
                            return param_key_values
                        else:
                            response_error = errno.EPROTO
                    else:
                        response_error = errno.EPROTO
                else:
                    response_error = errno.ETIMEDOUT
            self.log.info("ContikiNode%i getParameters: could not send request, error %i ", self.mac_address,response_error)
            return response_error
        else:
            self.log.info("ContikiNode%i getParameters: no valid parameters %s",self.mac_address, param_key_values)
        return errno.EINVAL
    
    def __SerialResponseHandler(self,error,response_message):
        if error == 0:
            if self.__awaiting_response:
                self.__awaiting_response = False
                self.__response_message = response_message
            elif response_message[0] == ControlOpCode.EVENT_PUSH:
                event_control_hdr = readResponseHeader(response_message)
                line_ptr = 6
                #~ event_key_values = {}
                p_hdr = readParamHeader(response_message[line_ptr:])
                #~ self.log.info("event: %u %u %u", p_hdr.uid,p_hdr.type,p_hdr.len)
                line_ptr+=ctypes.sizeof(param_hdr_t)
                import numpy as np
                frmt = self.unique_name_to_param[self.unique_id_to_name[p_hdr.uid]].struct_format
                dt = np.dtype(frmt)
                value = np.frombuffer(np.ndarray(shape=(),dtype=dt,buffer=response_message[line_ptr:line_ptr+p_hdr.len]),dt)[0]
                self.unique_name_to_eventcb[self.unique_id_to_name[p_hdr.uid]](self.unique_id_to_name[p_hdr.uid],value)
            else:
                self.serial_interface.print_byte_array(response_message)
                self.log.info("ContikiNode%i received response out-of-order, dropping",self.mac_address)
        else:
            if self.__awaiting_response:
                self.__awaiting_response = False
                self.__response_message = None

    
    def __waitForResponse(self):
        wait_time = 0
        while self.__awaiting_response and wait_time < 1.0:
            time.sleep(0.1)
            wait_time += 0.1
        if self.__awaiting_response:
            self.__awaiting_response = False
            self.log.info("ContikiNode%i: response timeout",self.mac_address)
            return False
        return True
    
    #~ def getMonitor(monitor_keys):
        #~ return
    #~ 
    #~ def getMonitorBounce(measurement_keys, collect_period,report_period,num_iterations,callback):
        #~ return
    #~ 
    def defineEvent(self, event_key, event_callback):
        if event_key in self.unique_name_to_param:
            message = bytearray()
            control_hdr = control_hdr_t(ControlOpCode.EVENT_REGISTER,0,++self.sequence_number)
            e = self.unique_name_to_param[event_key]
            message.extend(param_hdr_t(e.param_uid,e.param_type,e.param_len))
            control_hdr.num_param+=1
            message = bytearray(control_hdr.to_bin()) + message
            self.__awaiting_response = True
            self.serial_interface.serial_send(message,len(message))
            if self.__waitForResponse() and self.__response_message != None:    
                response_control_hdr = readResponseHeader(self.__response_message)
                line_ptr = 6
                if response_control_hdr == control_hdr:
                    p_hdr = readParamHeader(self.__response_message[line_ptr:])
                    line_ptr+=ctypes.sizeof(param_hdr_t)
                    import numpy as np
                    #~ frmt = self.unique_name_to_param[self.unique_id_to_name[p_hdr.uid]].struct_format
                    #~ dt = np.dtype(frmt)
                    #~ value = np.frombuffer(np.ndarray(shape=(),dtype=dt,buffer=self.__response_message[line_ptr:line_ptr+p_hdr.len]).byteswap(),dt)[0]
                    error = UINT8_T.unpack(self.__response_message[line_ptr:line_ptr+1])[0]
                    line_ptr+=1
                    self.unique_name_to_eventcb[event_key] = event_callback
                    #~ print self.unique_name_to_eventcb
                    return error
                else:
                    self.log.info("ContikiNode%i defineEvent wrong response header, dropping",self.mac_address)
                    return errno.EPROTO
            else:
                self.log.info("ContikiNode%i- defineEvent: could not send request",self.mac_address)
                return errno.ETIMEDOUT
        else:
            self.log.info("ContikiNode%i- defineEvent: event \"%s\" not found",self.mac_address, key)
        return errno.EINVAL

class ContikiIPv6(dot802154Network):
    
    def getSupportedNetworkParameters():
        return
    
    def getSupportedNetworkEvents():
        return
    
    def getSupportedNetworkMeasurements():
        return

class ContikiIPv4(dot802154Network):
    
    def getSupportedNetworkParameters():
        return
    
    def getSupportedNetworkEvents():
        return
    
    def getSupportedNetworkMeasurements():
        return

class ContikiRime(dot802154Network):
    
    def __init__(self, network_parameters, node):
        self.log = logging.getLogger()
        self.node = node
        self.parameter_names = []
        self.measurement_names = []
        self.event_names = []
        try:
            file_rp = open(network_parameters,'rt')
            reader = csv.DictReader(file_rp)
            for row in reader:
                if row['category'] == "PARAMETER":
                    self.parameter_names.append(row['unique_name'])
                elif row['category'] == "MEASUREMENT":
                    self.measurement_names.append(row['unique_name'])
                elif row['category'] == "EVENT":
                    self.event_names.append(row['unique_name'])
                else:
                    self.log.info("Illegal parameter category: %s" % row['category'])
        except Exception as e:
            self.log.fatal("An error occurred while initializing TAISC: %s" % e)
        finally:
            file_rp.close()
        pass
    
    def getSupportedNetworkParameters(self):
        return self.parameter_names
    
    def getSupportedNetworkEvents(self):
        return self.event_names
    
    def getSupportedNetworkMeasurements(self):
        return self.measurement_names
    
    def getParameterHigherLayer(self,param_keys):
        ret = self.node.getParameters(param_keys)
        if type(ret) == dict:
            return ret
        else:
            raise UPIError(ret)
    
    def setParameterHigherLayer(self,param_key_values):
        ret = self.node.setParameters(param_key_values)
        if type(ret) == dict:
            return ret
        else:
            raise UPIError(ret)

class serial_hdr_t(Structure):
    _fields_ = [("decoded_len",c_ubyte),("encoded_len",c_ubyte),("padding",c_ubyte*8)]


#~ class PythonSerial(LineReader):
#~ 
    #~ receiver_callback = None
#~ 
    #~ def connection_made(self, transport):
        #~ super(PrintLines, self).connection_made(transport)
        #~ sys.stdout.write('port opened\n')
        #~ self.write_line('hello world')
#~ 
    #~ def handle_line(self, data):
        #~ sys.stdout.write('line received: {}\n'.format(repr(data)))
        #~ if line != '':
            #~ if line[2:ctypes.sizeof(serial_hdr_t)] == 'FFFFFFFF':
                #~ enc_len = fm_serial_header.unpack(line[0:2])[1]
                #~ receiver_callback(bytearray(base64.b64decode(line[ctypes.sizeof(serial_hdr_t):enc_len])))
            #~ else:
                #~ sys.stdout.write("Contiki Node %u, printf output: %s",self.mac_address, line)
#~ 
    #~ def connection_lost(self, exc):
        #~ if exc:
            #~ traceback.print_exc(exc)
        #~ sys.stdout.write('port closed\n')
    
class ContikiSerialDump(SerialInterface):
    
    def __init__(self,serial_port,SerialResponseHandler,mac_address):
        self.log = logging.getLogger()
        self.mac_address = mac_address
        if socket.gethostname().find("wilab2") == -1:
            self.serialdump_process = subprocess.Popen(['./runtime/connectors/dot802154_contiki/contiki/serialdump-linux', '-b115200', serial_port],stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        else:
            self.serialdump_process = subprocess.Popen(['sudo','./runtime/connectors/dot802154_contiki/contiki/serialdump-linux', '-b115200', '/dev/rm090'],stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        #~ self.serialdump_process = subprocess.Popen(['/home/user/taisc-contiki-3.0/tools/sky/serialdump-linux', '-b115200', serial_port],stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        thread.start_new_thread(self.serial_listen, (SerialResponseHandler,))
        #~ ser = serial.serial_for_url('/dev/ttyUSB0', baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS, timeout=1)
        #~ with ReaderThread(ser, PythonSerial) as protocol:
            #~ self.protocol = protocol
            #~ self.protocol.TERMINATOR = b'\n'
            #~ self.protocol.receiver_callback = SerialResponseHandler
            #~ protocol.write_line('hello')
            #~ time.sleep(2)

    def print_byte_array(self,b):
        print(' '.join('{:02x}'.format(x) for x in b))
        #~ print ' '.join(str(x) for x in b)
        #~ for c in b: print(c)

    def serial_send(self,payload, payload_len):
        #~ self.print_byte_array(payload) 
        encoded_line = base64.b64encode(payload)
        serial_hdr = serial_hdr_t()
        serial_hdr.decoded_len = payload_len + ctypes.sizeof(serial_hdr_t)
        serial_hdr.encoded_len = len(encoded_line) + ctypes.sizeof(serial_hdr_t)
        for i in range(0,ctypes.sizeof(serial_hdr_t)-2):
            serial_hdr.padding[i] = 70
        msg = bytearray()
        msg.extend(serial_hdr)
        msg.extend(encoded_line)
        msg.append(0x0a)
        #~ self.print_byte_array(msg)
        self.serialdump_process.stdin.write(msg)
        self.serialdump_process.stdin.flush()
        #~ self.protocol.write_line(msg)                
    
    def serial_listen(self,receiver_callback):
        while True:
            line = self.serialdump_process.stdout.readline().strip()
            if line != '':
                if line[2:ctypes.sizeof(serial_hdr_t)] == 'FFFFFFFF':
                    try:
                        enc_len = fm_serial_header.unpack(line[0:2])[1]
                        receiver_callback(0,bytearray(base64.b64decode(line[ctypes.sizeof(serial_hdr_t):enc_len])))
                    except (RuntimeError, TypeError, NameError):
                        receiver_callback(1,None)
                else:
                    self.log.info("Contiki Node %u, printf output: %s",self.mac_address, line)





