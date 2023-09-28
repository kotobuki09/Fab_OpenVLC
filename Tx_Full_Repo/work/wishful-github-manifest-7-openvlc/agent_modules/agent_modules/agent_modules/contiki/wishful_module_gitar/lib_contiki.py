from wishful_module_gitar.lib_gitar import *
from serial_wrappers.lib_serial import SerialWrapper
import errno
import logging
import time
import binascii

class ContikiNode(SensorNode):

    def __init__(self, mac_addr, ip_addr, interface, serial_wrapper, auto_config=False):
        mod_name = 'ContikiNode.' + interface
        self.log = logging.getLogger(mod_name)
        self.mac_addr = mac_addr
        self.ip_addr = ip_addr
        self.interface = interface
        self.serial_wrapper = serial_wrapper
        self.serial_wrapper.set_serial_rxcallback(self.__serial_rx_handler)
        time.sleep(5)
        self.__response_message = bytearray()
        self.sequence_number = 0
        if auto_config is True:
            # read params/events/measurements from sensor
            self.log.warning("Tobe implemented")
        else:
            self.params_id_dct = {}
            self.params_name_dct = {}
            self.measurements_id_dct = {}
            self.measurements_name_dct = {}
            self.events_id_dct = {}
            self.events_name_dct = {}
        pass

    def register_parameters(self, connector_module, param_defs):
        self.params_id_dct[connector_module] = {}
        self.params_name_dct[connector_module] = {}
        for param_def in param_defs:
            if param_def['type_name'] == "STRUCT_T":
                tlen = param_def['type_len']
                tformat = param_def['type_format']
                tsubformat = ""
            elif param_def['type_name'] == "DYN_STRUCT_T":
                tlen = param_def['type_len']
                tformat = param_def['type_format']
                tsubformat = param_def['type_subformat']
            else:
                tlen = -1
                tformat = ""
                tsubformat = ""
            param = SensorParameter(param_def['unique_name'], int(
                param_def['unique_id']), param_def['type_name'], int(tlen), tformat, tsubformat)
            self.params_id_dct[connector_module][int(param_def['unique_id'])] = param
            self.params_name_dct[connector_module][param_def['unique_name']] = param

    def write_parameters(self, connector_module, param_key_values):
        message = bytearray()
        message_hdr = ControlMsgHeader(CommandOpCode.PARAM_SET, 0, ++self.sequence_number)
        for key in param_key_values:
            if connector_module in self.params_name_dct and key in self.params_name_dct[connector_module]:
                p = self.params_name_dct[connector_module][key]
                message.extend(p.hdr_to_bin())
                # message_hdr.args_len+=len(p)
                p.change_list.append(param_key_values[key])
                message.extend(p.data_type.value_to_bin(param_key_values[key]))
                message_hdr.num_args += 1
                # message_hdr.args_len+=p.data_type.type_len
            else:
                self.log.info("ContikiNode %s- write_parameters: parameter \"%s\" not found for connector %s",
                              self.interface, key, connector_module)
        if message_hdr.num_args > 0:
            message = bytearray(message_hdr.to_bin()) + message
            resp_message = self.__send_serial_cmd(4, message, message_hdr)
            if type(resp_message) == bytearray:
                self.serial_wrapper._SerialdumpWrapper__print_byte_array(resp_message)
                param_key_values = {}
                line_ptr = 0
                for i in range(0, message_hdr.num_args):
                    p_hdr = GenericControlHeader.hdr_from_buf(resp_message[line_ptr:])
                    line_ptr += len(p_hdr)
                    error = int8_data_type.value_from_buf(resp_message[line_ptr:])
                    line_ptr += int8_data_type.type_len
                    param_key_values[self.params_id_dct[connector_module][p_hdr.unique_id].unique_name] = error
                # self.log.info('write_parameters returns %s',param_key_values)
                return param_key_values
            else:
                self.log.info('Error %s sending message', resp_message)
                return resp_message
        else:
            self.log.info("ContikiNode %s setParameters: no valid parameters %s", self.interface, param_key_values)
        return errno.EINVAL

    def read_parameters(self, connector_module, param_keys):
        message = bytearray()
        message_hdr = ControlMsgHeader(CommandOpCode.PARAM_GET, 0, ++self.sequence_number)
        for key in param_keys:
            if connector_module in self.params_name_dct and key in self.params_name_dct[connector_module]:
                p = self.params_name_dct[connector_module][key]
                message.extend(p.hdr_to_bin())
                # message_hdr.args_len+=len(p)
                message_hdr.num_args += 1
            else:
                self.log.info("ContikiNode %s- read_parameters: parameter \"%s\" not found for connector %s",
                              self.interface, key, connector_module)
        if message_hdr.num_args > 0:
            message = bytearray(message_hdr.to_bin()) + message
            #self.log.info("Sending %s", binascii.hexlify(message))
            #self.log.info("Sending %s", message.decode("utf-8"))
            resp_message = self.__send_serial_cmd(4, message, message_hdr)
            if type(resp_message) == bytearray:
                self.serial_wrapper._SerialdumpWrapper__print_byte_array(resp_message)
                param_key_values = {}
                line_ptr = 0
                for i in range(0, message_hdr.num_args):
                    p_hdr = GenericControlHeader.hdr_from_buf(resp_message[line_ptr:])
                    line_ptr += len(p_hdr)
                    p = self.params_id_dct[connector_module][p_hdr.unique_id]
                    value = p.data_type.value_from_buf(resp_message[line_ptr:])
                    line_ptr += p.data_type.type_len
                    param_key_values[p.unique_name] = value
                return param_key_values
            else:
                self.log.fatal("NOT BYTE ARRAY")
                return resp_message
        else:
            self.log.info("ContikiNode %s read_parameters: no valid parameters %s", self.interface, param_keys)
        return errno.EINVAL

    def register_measurements(self, connector_module, measurement_defs):
        self.measurements_id_dct[connector_module] = {}
        self.measurements_name_dct[connector_module] = {}
        for measurement_def in measurement_defs:
            if measurement_def['type_name'] == "STRUCT_T":
                tlen = measurement_def['type_len']
                tformat = measurement_def['type_format']
                tsubformat = ""
            elif measurement_def['type_name'] == "DYN_STRUCT_T":
                tlen = measurement_def['type_len']
                tformat = measurement_def['type_format']
                tsubformat = measurement_def['type_subformat']
            else:
                tlen = -1
                tformat = ""
                tsubformat = ""
            measurement = SensorMeasurement(measurement_def['unique_name'], int(
                measurement_def['unique_id']), measurement_def['type_name'], int(tlen), tformat, tsubformat)
            self.measurements_id_dct[connector_module][int(measurement_def['unique_id'])] = measurement
            self.measurements_name_dct[connector_module][measurement_def['unique_name']] = measurement

    def read_measurements(self, connector_module, measurement_keys):
        message = bytearray()
        message_hdr = ControlMsgHeader(CommandOpCode.PARAM_GET, 0, ++self.sequence_number)
        for key in measurement_keys:
            if connector_module in self.measurements_name_dct and key in self.measurements_name_dct[connector_module]:
                m = self.measurements_name_dct[connector_module][key]
                message.extend(m.hdr_to_bin())
                # message_hdr.args_len+=len(m)
                message_hdr.num_args += 1
            else:
                self.log.info("ContikiNode %s- read_measurements: measurement \"%s\" not found for connector %s",
                              self.interface, key, connector_module)
        if message_hdr.num_args > 0:
            message = bytearray(message_hdr.to_bin()) + message
            resp_message = self.__send_serial_cmd(4, message, message_hdr)
            if type(resp_message) == bytearray:
                measurement_key_values = {}
                line_ptr = 0
                for i in range(0, message_hdr.num_args):
                    m_hdr = GenericControlHeader.hdr_from_buf(resp_message[line_ptr:])
                    line_ptr += len(m_hdr)
                    m = self.measurements_id_dct[connector_module][m_hdr.unique_id]
                    value = m.data_type.value_from_buf(resp_message[line_ptr:])
                    line_ptr += m.data_type.type_len
                    measurement_key_values[m.unique_name] = value
                return measurement_key_values
            else:
                return resp_message
        else:
            self.log.info("ContikiNode %s read_measurements: no valid parameters %s", self.interface, measurement_keys)
        return errno.EINVAL

    def register_events(self, connector_module, event_defs):
        self.events_id_dct[connector_module] = {}
        self.events_name_dct[connector_module] = {}
        for event_def in event_defs:
            if event_def['type_name'] == "STRUCT_T":
                tlen = event_def['type_len']
                tformat = event_def['type_format']
                tsubformat = ""
            elif event_def['type_name'] == "DYN_STRUCT_T":
                tlen = event_def['type_len']
                tformat = event_def['type_format']
                tsubformat = event_def['type_subformat']
            else:
                tlen = -1
                tformat = ""
                tsubformat = ""
            event = SensorEvent(event_def['unique_name'], int(event_def['unique_id']),
                                event_def['type_name'], int(tlen), tformat, tsubformat)
            self.events_id_dct[connector_module][int(event_def['unique_id'])] = event
            self.events_name_dct[connector_module][event_def['unique_name']] = event

    def add_events_subscriber(self, connector_module, event_keys, event_callback, event_duration):
        message = bytearray()
        message_hdr = ControlMsgHeader(CommandOpCode.EVENT_REGISTER, 0, ++self.sequence_number)
        for key in event_keys:
            if connector_module in self.events_name_dct and key in self.events_name_dct[connector_module]:
                e = self.events_name_dct[connector_module][key]
                e.event_duration = event_duration
                message.extend(e.hdr_to_bin())
                message.extend(uint16_data_type.value_to_bin(event_duration))
                # message_hdr.args_len+=len(e)
                message_hdr.num_args += 1
                self.log.info("Adding event %s", key)
            else:
                self.log.info("ContikiNode %s- add_events_subscriber: event \"%s\" not found for connector %s",
                              self.interface, key, connector_module)
        if message_hdr.num_args > 0:
            message = bytearray(message_hdr.to_bin()) + message
            #self.log.info("Sending message %s", binascii.hexlify(message))
            #self.log.info("sending message %s", message.decode())
            resp_message = self.__send_serial_cmd(4, message, message_hdr)
            if type(resp_message) == bytearray:
                event_key_errors = {}
                line_ptr = 0
                for i in range(0, message_hdr.num_args):
                    e_hdr = GenericControlHeader.hdr_from_buf(resp_message[line_ptr:])
                    line_ptr += len(e_hdr)
                    e = self.events_id_dct[connector_module][e_hdr.unique_id]
                    error = int8_data_type.value_from_buf(resp_message[line_ptr:])
                    line_ptr += int8_data_type.type_len
                    if error == 0:
                        e.subscriber_callbacks.append(event_callback)
                    event_key_errors[e.unique_name] = error
                return event_key_errors
            else:
                return resp_message
        else:
            self.log.info("ContikiNode %s read_parameters: no valid parameters %s", self.interface, event_key_errors)
        return errno.EINVAL

    def reset(self):
        pass

    def __await_probe_response(self):
        wait_time = 0
        while self.__awaiting_probe_response and wait_time < 1.0:
            time.sleep(0.1)
            wait_time += 0.1
        if self.__awaiting_probe_response:
            self.__awaiting_probe_response = False
            self.log.info("ContikiNode %s: probe response timeout", self.interface)
            return False
        return True

    def __send_serial_cmd(self, max_attempts, message, message_hdr):
        num_attempts = 0
        response_error = 0
        while num_attempts < max_attempts:
            num_attempts += 1
            self.__awaiting_command_response = True
            self.serial_wrapper.serial_send(message, len(message))
            if self.__await_command_response() and self.__response_message is not None:
                response_hdr = ControlMsgHeader.from_buf(self.__response_message)
                if response_hdr.opcode != CommandOpCode.ERROR_RESPONSE and response_hdr == message_hdr:
                    return self.__response_message[len(response_hdr):]
                else:
                    response_error = errno.EPROTO
            else:
                response_error = errno.ETIMEDOUT
        self.log.info("ContikiNode %s sending command failed, error %i ", self.interface, response_error)
        return response_error

    def __await_command_response(self):
        wait_time = 0
        while self.__awaiting_command_response and wait_time < 1.0:
            time.sleep(0.1)
            wait_time += 0.1
        if self.__awaiting_command_response:
            self.__awaiting_command_response = False
            self.log.info("command response timeout")
            return False
        return True

    def __str__(self):
        return "ContikiNode " + self.interface

    def __serial_rx_handler(self, error, response_message):
        if error == 0:
            if response_message[0] == CommandOpCode.EVENT_PUSH:
                event_hdr = ControlMsgHeader.from_buf(response_message)
                line_ptr = 6
                e_hdr = GenericControlHeader.hdr_from_buf(response_message[line_ptr:])
                line_ptr += len(e_hdr)
                for connector in self.events_id_dct.keys():
                    if e_hdr.unique_id in self.events_id_dct[connector]:
                        e = self.events_id_dct[e_hdr.unique_id]
                        value = e.data_type.value_from_buf(response_message[line_ptr:])
                        for cb in e.subscriber_callbacks:
                            cb(e.unique_name, value)
                        return
                self.log.info("ContikiNode %s received unknown event %s %s, dropping", self.interface, event_hdr, e_hdr)
            elif self.__awaiting_command_response:
                self.__awaiting_command_response = False
                self.__response_message = response_message
            else:
                self.serial_wrapper.print_byte_array(response_message)
                self.log.info("ContikiNode %s received response out-of-order, dropping", self.interface)
        else:
            self.log.info("received error message")
            if self.__awaiting_command_response:
                self.__awaiting_command_response = False
                self.__response_message = None
