import struct
from ctypes import *
from enum import IntEnum
import abc
import configparser as ConfigParser
import logging
import time
import csv

UINT8_T = struct.Struct("B")
INT8_T = struct.Struct("b")
UINT16_T = struct.Struct("H")
INT16_T = struct.Struct("h")
UINT32_T = struct.Struct("I")
INT32_T = struct.Struct("i")
UINT64_T = struct.Struct("L")
INT64_T = struct.Struct("l")
BOOL_T = struct.Struct("?")
CHAR_T = struct.Struct("c")
STRING_T = struct.Struct("<s")
STRUCT_T = struct.Struct("<p")
DYN_STRUCT_T = struct.Struct("<p")


class CommandOpCode(IntEnum):
    PARAM_GET = 0
    PARAM_SET = 1
    EVENT_REGISTER = 2
    EVENT_PUSH = 3
    ERROR_RESPONSE = 127


class ControlMsgHeader():
    fm_control_msg_header = struct.Struct('<B B I')

    def __init__(self, opcode, num_args, seq_nr):
        self.opcode = opcode
        self.num_args = num_args
        self.seq_nr = seq_nr

    def __eq__(self, other):
        return (self.opcode == other.opcode) and \
            (self.num_args == other.num_args) and \
            (self.seq_nr == other.seq_nr)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return struct.calcsize(ControlMsgHeader.fm_control_msg_header.format)

    @staticmethod
    def from_buf(buf):
        tup = ControlMsgHeader.fm_control_msg_header.unpack(buf[0:6])
        return ControlMsgHeader(tup[0], tup[1], tup[2])

    def to_bin(self):
        b = bytearray()
        b.extend(uint8_data_type.value_to_bin(self.opcode))
        b.extend(uint8_data_type.value_to_bin(self.num_args))
        b.extend(uint32_data_type.value_to_bin(self.seq_nr))
        return b


class CommandHeader():

    fm_command_header = struct.Struct('<B B H I')

    def __init__(self, opcode, num_args, args_len, seq_nr):
        self.opcode = opcode
        self.num_args = num_args
        self.args_len = args_len
        self.seq_nr = seq_nr

    def __eq__(self, other):
        return (self.opcode == other.opcode) and \
            (self.num_args == other.num_args) and \
            (self.args_len == other.args_len) and \
            (self.seq_nr == other.seq_nr)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return struct.calcsize(CommandHeader.fm_command_header.format)

    @staticmethod
    def from_buf(buf):
        tup = CommandHeader.fm_command_header.unpack(buf[0:8])
        return CommandHeader(tup[0], tup[1], tup[2], tup[3])

    def to_bin(self):
        b = bytearray()
        b.extend(uint8_data_type.value_to_bin(self.opcode))
        b.extend(uint8_data_type.value_to_bin(self.num_args))
        b.extend(uint16_data_type.value_to_bin(self.args_len))
        b.extend(uint32_data_type.value_to_bin(self.seq_nr))
        return b


class SensorDataType():
    typeSize = {"UINT8_T": 1, "INT8_T": 1, "UINT16_T": 2, "INT16_T": 2,
                "UINT32_T": 4, "INT32_T": 4, "UINT64_T": 8, "INT64_T": 8,
                "BOOL_T": 1, "CHAR_T": 1}
    typeID = {"UINT8_T": 0, "INT8_T": 1, "UINT16_T": 2, "INT16_T": 3,
              "UINT32_T": 4, "INT32_T": 5, "UINT64_T": 6, "INT64_T": 7,
              "BOOL_T": 8, "CHAR_T": 9, "STRING_T": 10, "STRUCT_T": 11,
              "DYN_STRUCT_T": 12}
    typeName = {0: "UINT8_T", 1: "INT8_T", 2: "UINT16_T", 3: "INT16_T",
                4: "UINT32_T", 5: "INT32_T", 6: "UINT64_T", 7: "INT64_T",
                8: "BOOL_T", 9: "CHAR_T", 10: "STRING_T", 11: "STRUCT_T",
                12: "DYN_STRUCT_T"}
    typeAsDType = {"UINT8_T": 'u1', "INT8_T": 'i1', "UINT16_T": 'u2',
                   "INT16_T": 'i2', "UINT32_T": 'u4', "INT32_T": 'i4',
                   "UINT64_T": 'u8', "INT64_T": 'i8', "BOOL_T": 'b',
                   "CHAR_T": 'U', "STRING_T": 'S', "STRUCT_T": 'O',
                   "DYN_STRUCT_T": 'O'}
    typeAsStruct = [UINT8_T, INT8_T, UINT16_T, INT16_T, UINT32_T, INT32_T,
                    UINT64_T, INT64_T, BOOL_T, CHAR_T, STRING_T, STRUCT_T,
                    DYN_STRUCT_T]

    def __init__(self, type_name, type_len=-1, np_format="", np_sub_format=""):
        self.type_name = type_name
        self.type_id = SensorDataType.typeID[type_name]
        if type_len != -1:
            self.type_len = type_len
        else:
            self.type_len = SensorDataType.typeSize[type_name]
        if np_format != "":
            self.np_format = np_format
        else:
            self.np_format = SensorDataType.typeAsDType[self.type_name]
        if self.type_name == "DYN_STRUCT_T":
            self.np_sub_format = np_sub_format
        self.struct_format = SensorDataType.typeAsStruct[self.type_id]

    def value_to_bin(self, value):
        bin_val = bytearray()
        if self.type_id < 11:
            s = struct.Struct(b'<' + self.struct_format.format)
            # print s.pack(value)
            bin_val.extend(s.pack(value))
        elif self.type_id == 11:
            import numpy as np
            dt = np.dtype(self.np_format).newbyteorder('>')
            s = bytearray(np.array(tuple(value,), dt))
            bin_val.extend(s)
        else:
            import numpy as np
            dt = np.dtype(self.np_format).newbyteorder('>')
            s = bytearray(np.array(tuple(value,), dt))
            bin_val.extend(s)
            offset = self.type_len
            while offset < len(value):
                dt = np.dtype(self.np_sub_format).newbyteorder('>')
                s = bytearray(np.array(tuple(value[offset:offset + dt.itemsize],), dt))
                bin_val.extend(s)
                offset = offset + dt.itemsize
        return bin_val

    def value_from_buf(self, buf):
        import numpy as np
        dt = np.dtype(self.np_format)
        if self.type_name == "DYN_STRUCT_T":
            ret_tpl = np.frombuffer(np.ndarray(shape=(), dtype=dt, buffer=buf[0:dt.itemsize]).byteswap(), dt)[0]
            offset = dt.itemsize
            while offset < len(buf):
                dt = np.dtype(self.np_sub_format)
                ret_tpl = ret_tpl + np.frombuffer(np.ndarray(shape=(), dtype=dt, buffer=buf[offset:dt.itemsize]).byteswap(), dt)[0]
                offset = offset + dt.itemsize
            return ret_tpl
        return np.frombuffer(np.ndarray(shape=(), dtype=dt,
                                        buffer=buf).byteswap(), dt)[0]


uint32_data_type = SensorDataType("UINT32_T")
uint16_data_type = SensorDataType("UINT16_T")
uint8_data_type = SensorDataType("UINT8_T")
int8_data_type = SensorDataType("INT8_T")


class GenericControlHeader():

    fm_header = struct.Struct('<H B B')

    def __init__(self, uname, uid, type_name, type_len=-1, type_np_format="", type_np_subformat=""):
        self.unique_name = uname
        self.unique_id = uid
        self.data_type = SensorDataType(type_name, type_len, type_np_format, type_np_subformat)

    def __len__(self):
        return struct.calcsize(GenericControlHeader.fm_header.format)

    def hdr_to_bin(self):
        b = bytearray()
        b.extend(uint16_data_type.value_to_bin(self.unique_id))
        b.extend(uint8_data_type.value_to_bin(self.data_type.type_id))
        b.extend(uint8_data_type.value_to_bin(self.data_type.type_len))
        return b

    @staticmethod
    def hdr_from_buf(buf):
        tup = GenericControlHeader.fm_header.unpack(buf[0:4])
        return GenericControlHeader("STUB", tup[0],
                                    SensorDataType.typeName[tup[1]], tup[2])


class SensorEvent(GenericControlHeader):

    def __init__(self, uname, uid, type_name, type_len=-1, type_np_format="", type_np_subformat=""):
        GenericControlHeader.__init__(self, uname, uid, type_name, type_len,
                                      type_np_format, type_np_subformat)
        self.event_duration = 0
        self.subscriber_callbacks = []


class SensorParameter(GenericControlHeader):

    def __init__(self, uname, uid, type_name, type_len=-1, type_np_format="", type_np_subformat=""):
        GenericControlHeader.__init__(self, uname, uid, type_name, type_len,
                                      type_np_format, type_np_subformat)
        self.change_list = []


class SensorMeasurement(GenericControlHeader):

    def __init__(self, uname, uid, type_name, type_len=-1, type_np_format="", type_np_subformat=""):
        GenericControlHeader.__init__(self, uname, uid, type_name, type_len,
                                      type_np_format, type_np_subformat)
        self.is_periodic = False
        self.read_interval = 0
        self.report_interval = 0
        self.num_iterations = 0
        self.report_callback = None


class SensorNode():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def register_parameters(self, connector_module, param_defs):
        pass

    @abc.abstractmethod
    def write_parameters(self, connector_module, param_key_values):
        pass

    @abc.abstractmethod
    def read_parameters(self, connector_module, param_keys):
        pass

    @abc.abstractmethod
    def register_measurements(self, connector_module, measurement_defs):
        pass

    @abc.abstractmethod
    def read_measurements(self, connector_module, measurement_keys):
        pass

    @abc.abstractmethod
    def register_events(self, connector_module, event_defs):
        pass

    @abc.abstractmethod
    def add_events_subscriber(self, connector_module, event_names,
                              event_callback):
        pass

    @abc.abstractmethod
    def reset(self):
        pass


def ConfigSectionMap(config, section):
    dict1 = {}
    options = config.options(section)
    for option in options:
        dict1[option] = config.get(section, option)
    return dict1


def singleton(cls):
    instance = cls()
    instance.__call__ = lambda: instance
    return instance


class SensorNodeFactory():

    class __SensorNodeFactory:

        def __init__(self):
            self.log = logging.getLogger('SensorNodeFactory')
            self.__nodes = {}

        def __str__(self):
            return repr(self) + self.val
    instance = None

    def __init__(self):
        if not SensorNodeFactory.instance:
            SensorNodeFactory.instance = SensorNodeFactory.__SensorNodeFactory()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def create_nodes(self, config_file, supported_interfaces,
                     control_extensions):
        from wishful_module_gitar.lib_contiki import ContikiNode
        config = ConfigParser.ConfigParser()
        config.optionxform = str
        config.read(config_file)
        self.log.info('Creating contiki instances %s', config.sections())
        for interface in config.sections():
            if interface in supported_interfaces:
                mac_addr = config.get(interface, 'MacAddress')
                ip_addr = config.get(interface, 'IpAddress')
                serial_wrapper = config.get(interface, 'SerialWrapper')
                serial_wrapper_obj = None
                if serial_wrapper == 'ContikiSerialdump':
                    from serial_wrappers.serialdump_wrapper import SerialdumpWrapper
                    serial_wrapper_obj = SerialdumpWrapper(config.get(interface, 'SerialDev'), interface)
                else:
                    self.log.fatal('invalid serial wrapper')
                self.__nodes[interface] = ContikiNode(mac_addr, ip_addr, interface, serial_wrapper_obj)
            else:
                self.log.info('Skipping interface %s', section)

        for connector_module in control_extensions.keys():
            try:
                file_rp = open(control_extensions[connector_module], 'rt')
                reader = csv.DictReader(file_rp)
                param_defs = []
                measurement_defs = []
                event_defs = []
                for row in reader:
                    r_def = {'unique_name': row["unique_name"], 'unique_id': row["unique_id"], 'type_name': row[
                        "type"], 'type_len': row["length"], 'type_format': row["struct_format"], 'type_subformat': row["struct_subformat"]}
                    if row['category'] == "PARAMETER":
                        param_defs.append(r_def)
                    elif row['category'] == "MEASUREMENT":
                        measurement_defs.append(r_def)
                    elif row['category'] == "EVENT":
                        event_defs.append(r_def)
                    else:
                        self.log.info("Illegal parameter category: %s" % row['category'])

                for iface in self.__nodes.keys():
                    self.__nodes[iface].register_parameters(connector_module, param_defs)
                    self.__nodes[iface].register_measurements(connector_module, measurement_defs)
                    self.__nodes[iface].register_events(connector_module, event_defs)

            except Exception as e:
                self.log.fatal("Could not read parameters for %s, from %s error: %s" %
                               (connector_module, control_extensions[connector_module], e))

    def get_nodes(self):
        return self.__nodes

    def get_node(self, interface_name):
        return self.__nodes[interface_name]
