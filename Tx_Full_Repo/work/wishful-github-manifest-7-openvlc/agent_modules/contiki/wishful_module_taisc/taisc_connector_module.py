import wishful_upis as upis
import wishful_framework as wishful_module
from wishful_framework.classes import exceptions
# <----!!!!! Important to include it here; otherwise cannot be pickled!!!!
from wishful_framework.upi_arg_classes.radio_info import RadioInfo
# <----!!!!! Important to include it here; otherwise cannot be pickled!!!!
from wishful_framework.upi_arg_classes.radio_info import RadioPlatform
from wishful_module_gitar.lib_gitar import SensorNode
from wishful_module_gitar.lib_gitar import SensorNodeFactory

import logging
import inspect
import _thread as thread
import time


@wishful_module.build_module
class TAISCConnector(wishful_module.AgentModule):

    def __init__(self, **kwargs):
        super(TAISCConnector, self).__init__()
        self.log = logging.getLogger('TAISConnector')
        self.node_factory = SensorNodeFactory()
        self.radio_programs = kwargs['RadioPrograms']
        self.radio_program_names = {}
        for rp_name in self.radio_programs.keys():
            self.radio_program_names[self.radio_programs[rp_name]] = rp_name
        self.supported_interfaces = kwargs['SupportedInterfaces']

    @wishful_module.bind_function(upis.radio.set_parameters)
    def set_radio_parameter(self, param_key_values_dict):
        node = self.node_factory.get_node(self.interface)
        if node is not None:
            return node.write_parameters('taisc', param_key_values_dict)
        else:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("%s Interface %s does not exist!" %
                           (self.interface, fname))
            raise exceptions.InvalidArgumentException(
                func_name=fname, err_msg="Interface does not exist")

    @wishful_module.bind_function(upis.radio.get_parameters)
    def get_radio_parameters(self, param_key_list):
        node = self.node_factory.get_node(self.interface)
        if node is not None:
            return node.read_parameters('taisc', param_key_list)
        else:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("%s Interface %s does not exist!" %
                           (self.interface, fname))
            raise exceptions.InvalidArgumentException(
                func_name=fname, err_msg="Interface does not exist")

    @wishful_module.bind_function(upis.radio.get_measurements)
    def get_radio_measurements(self, measurement_key_list):
        node = self.node_factory.get_node(self.interface)
        if node is not None:
            return node.read_measurements('taisc', measurement_key_list)
        else:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("%s Interface %s does not exist!" %
                           (self.interface, fname))
            raise exceptions.InvalidArgumentException(
                func_name=fname, err_msg="Interface does not exist")

    def get_radio_measurements_periodic_worker(self, node, measurement_keys, collect_period, report_period, num_iterations, report_callback):
        num_collects_report = report_period / collect_period
        for i in xrange(0, num_iterations):
            measurement_report = {}
            for key in measurement_keys:
                measurement_report[key] = []
            for i in xrange(0, num_collects_report):
                time.sleep(collect_period)
                ret = node.read_measurements('taisc', measurement_keys)
                for key in ret.keys():
                    measurement_report[key].append(ret[key])
            report_callback(node.interface, measurement_report)
        pass

    @wishful_module.bind_function(upis.radio.get_measurements_periodic)
    def get_radio_measurements_periodic(self, measurement_key_list, collect_period, report_period, num_iterations, report_callback):
        node = self.node_factory.get_node(self.interface)
        if node is not None:
            thread.start_new_thread(self.get_radio_measurements_periodic_worker, (
                node, measurement_key_list, collect_period, report_period, num_iterations, report_callback,))
        else:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("%s Interface %s does not exist!" %
                           (self.interface, fname))
            raise exceptions.InvalidArgumentException(
                func_name=fname, err_msg="Interface does not exist")

    @wishful_module.bind_function(upis.radio.subscribe_events)
    def define_radio_event(self, event_key_list, event_callback, event_duration):
        node = self.node_factory.get_node(self.interface)
        if node is not None:
            return node.add_events_subscriber('taisc', event_key_list, event_callback, event_duration)
        else:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("%s Interface %s does not exist!" %
                           (self.interface, fname))
            raise exceptions.InvalidArgumentException(
                func_name=fname, err_msg="Interface does not exist")

    @wishful_module.bind_function(upis.radio.activate_radio_program)
    def set_active(self, name):
        param_key_values = {}
        if name in self.radio_programs:
            param_key_values["TAISC_ACTIVERADIOPROGRAM"] = self.radio_programs[name]
            node = self.node_factory.get_node(self.interface)
            if node is not None:
                ret = node.write_parameters('taisc', param_key_values)
                if type(ret) == dict:
                    return ret["TAISC_ACTIVERADIOPROGRAM"]
                else:
                    fname = inspect.currentframe().f_code.co_name
                    self.log.fatal(
                        "Error executing function %s: %s!" % (fname, ret))
                    raise exceptions.UPIFunctionExecutionFailedException(
                        func_name=fname, err_msg="Error executing function")
            else:
                fname = inspect.currentframe().f_code.co_name
                self.log.fatal("%s Interface %s does not exist!" %
                               (self.interface, fname))
                raise exceptions.InvalidArgumentException(
                    func_name=fname, err_msg="Interface does not exist")
        else:
            fname = inspect.currentframe().f_code.co_name
            self.log.warn("Wrong radio program name: %s" % name)
            raise exceptions.InvalidArgumentException(
                func_name=fname, err_msg="Radio Program does not exist")

    @wishful_module.bind_function(upis.radio.deactivate_radio_program)
    def set_inactive(self, name):
        param_key_values = {}
        if name in self.radio_programs:
            param_key_values[
                "TAISC_ACTIVERADIOPROGRAM"] = self.radio_programs['CSMA']
            node = self.node_factory.get_node(self.interface)
            if node is not None:
                ret = node.write_parameters('taisc', param_key_values)
                if type(ret) == dict:
                    return ret["TAISC_ACTIVERADIOPROGRAM"]
                else:
                    fname = inspect.currentframe().f_code.co_name
                    self.log.fatal(
                        "Error executing function %s: %s!" % (fname, ret))
                    raise exceptions.UPIFunctionExecutionFailedException(
                        func_name=fname, err_msg="Error executing function")
            else:
                fname = inspect.currentframe().f_code.co_name
                self.log.fatal("%s Interface %s does not exist!" %
                               (self.interface, fname))
                raise exceptions.InvalidArgumentException(
                    func_name=fname, err_msg="Interface does not exist")
        else:
            fname = inspect.currentframe().f_code.co_name
            self.log.warn("Wrong radio program name: %s" % name)
            raise exceptions.InvalidArgumentException(
                func_name=fname, err_msg="Radio Program does not exist")

    @wishful_module.bind_function(upis.radio.get_running_radio_program)
    def get_active(self):
        param_keys = []
        param_keys = ["TAISC_ACTIVERADIOPROGRAM"]
        node = self.node_factory.get_node(self.interface)
        if node is not None:
            ret = node.read_parameters('taisc', param_keys)
            if type(ret) == dict:
                return self.radio_program_names[ret["TAISC_ACTIVERADIOPROGRAM"]]
            else:
                fname = inspect.currentframe().f_code.co_name
                self.log.fatal("Error executing function %s: %s!" %
                               (fname, ret))
                raise exceptions.UPIFunctionExecutionFailedException(
                    func_name=fname, err_msg="Error executing function")
        else:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("%s Interface %s does not exist!" %
                           (self.interface, fname))
            raise exceptions.InvalidArgumentException(
                func_name=fname, err_msg="Interface does not exist")

    @wishful_module.bind_function(upis.radio.get_hwaddr)
    def get_hwaddr(self):
        param_keys = []
        param_keys = ["IEEE802154_macShortAddress"]
        node = self.node_factory.get_node(self.interface)
        self.log.info("get_hw_addr")
        if node is not None:
            ret = node.read_parameters('taisc', param_keys)
            if type(ret) == dict:
                return ret["IEEE802154_macShortAddress"]
            else:
                fname = inspect.currentframe().f_code.co_name
                self.log.fatal("Error executing function %s: %s!" %
                               (fname, ret))
                raise exceptions.UPIFunctionExecutionFailedException(
                    func_name=fname, err_msg="Error executing function")
        else:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("%s Interface %s does not exist!" %
                           (self.interface, fname))
            raise exceptions.InvalidArgumentException(
                func_name=fname, err_msg="Interface does not exist")

    @wishful_module.bind_function(upis.radio.set_tx_power)
    def set_txpower(self, power_dBm):
        param_key_values = {}
        param_key_values['IEEE802154_phyTXPower'] = power_dBm
        node = self.node_factory.get_node(self.interface)
        if node is not None:
            ret = node.write_parameters('taisc', param_key_values)
            if type(ret) == dict:
                return ret["IEEE802154_phyTXPower"]
            else:
                fname = inspect.currentframe().f_code.co_name
                self.log.fatal("Error executing function %s: %s!" %
                               (fname, ret))
                raise exceptions.UPIFunctionExecutionFailedException(
                    func_name=fname, err_msg="Error executing function")
        else:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("%s Interface %s does not exist!" %
                           (self.interface, fname))
            raise exceptions.InvalidArgumentException(
                func_name=fname, err_msg="Interface does not exist")

    @wishful_module.bind_function(upis.radio.get_tx_power)
    def get_txpower(self):
        param_keys = []
        param_keys = ["IEEE802154_phyTXPower"]
        node = self.node_factory.get_node(self.interface)
        if node is not None:
            ret = node.read_parameters('taisc', param_keys)
            if type(ret) == dict:
                return ret["IEEE802154_phyTXPower"]
            else:
                fname = inspect.currentframe().f_code.co_name
                self.log.fatal("Error executing function %s: %s!" %
                               (fname, ret))
                raise exceptions.UPIFunctionExecutionFailedException(
                    func_name=fname, err_msg="Error executing function")
        else:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("%s Interface %s does not exist!" %
                           (self.interface, fname))
            raise exceptions.InvalidArgumentException(
                func_name=fname, err_msg="Interface does not exist")

    @wishful_module.bind_function(upis.radio.set_rxchannel)
    def set_rxchannel(self, freq_Hz, bandwidth):
        param_key_values = {}
        param_key_values['IEEE802154_phyCurrentChannel'] = freq_Hz
        node = self.node_factory.get_node(self.interface)
        if node is not None:
            ret = node.write_parameters('taisc', param_key_values)
            self.log.info(ret)
            if type(ret) == dict:
                return ret["IEEE802154_phyCurrentChannel"]
            else:
                fname = inspect.currentframe().f_code.co_name
                self.log.fatal("Error executing function %s: %s!" %
                               (fname, ret))
                raise exceptions.UPIFunctionExecutionFailedException(
                    func_name=fname, err_msg="Error executing function")
        else:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("%s Interface %s does not exist!" %
                           (self.interface, fname))
            raise exceptions.InvalidArgumentException(
                func_name=fname, err_msg="Interface does not exist")

    @wishful_module.bind_function(upis.radio.get_rxchannel)
    def get_rxchannel(self):
        param_keys = []
        param_keys = ["IEEE802154_phyCurrentChannel"]
        node = self.node_factory.get_node(self.interface)
        if node is not None:
            ret = node.read_parameters('taisc', param_keys)
            self.log.info(ret)
            if type(ret) == dict:
                return ret["IEEE802154_phyCurrentChannel"]
            else:
                fname = inspect.currentframe().f_code.co_name
                self.log.fatal("Error executing function %s: %s!" %
                               (fname, ret))
                raise exceptions.UPIFunctionExecutionFailedException(
                    func_name=fname, err_msg="Error executing function")
        else:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("%s Interface %s does not exist!" %
                           (self.interface, fname))
            raise exceptions.InvalidArgumentException(
                func_name=fname, err_msg="Interface does not exist")

    @wishful_module.bind_function(upis.radio.set_txchannel)
    def set_txchannel(self, freq_Hz, bandwidth):
        param_key_values = {}
        param_key_values['IEEE802154_phyCurrentChannel'] = freq_Hz
        node = self.node_factory.get_node(self.interface)
        if node is not None:
            ret = node.write_parameters('taisc', param_key_values)
            if type(ret) == dict:
                return ret["IEEE802154_phyCurrentChannel"]
            else:
                fname = inspect.currentframe().f_code.co_name
                self.log.fatal("Error executing function %s: %s!" %
                               (fname, ret))
                raise exceptions.UPIFunctionExecutionFailedException(
                    func_name=fname, err_msg="Error executing function")
        else:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("%s Interface %s does not exist!" %
                           (self.interface, fname))
            raise exceptions.InvalidArgumentException(
                func_name=fname, err_msg="Interface does not exist")

    @wishful_module.bind_function(upis.radio.get_txchannel)
    def get_txchannel(self):
        param_keys = []
        param_keys = ["IEEE802154_phyCurrentChannel"]
        node = self.node_factory.get_node(self.interface)
        if node is not None:
            ret = node.read_parameters('taisc', param_keys)
            if type(ret) == dict:
                return ret["IEEE802154_phyCurrentChannel"]
            else:
                fname = inspect.currentframe().f_code.co_name
                self.log.fatal("Error executing function %s: %s!" %
                               (fname, ret))
                raise exceptions.UPIFunctionExecutionFailedException(
                    func_name=fname, err_msg="Error executing function")
        else:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("%s Interface %s does not exist!" %
                           (self.interface, fname))
            raise exceptions.InvalidArgumentException(
                func_name=fname, err_msg="Interface does not exist")

    @wishful_module.bind_function(upis.radio.get_radio_info)
    def get_radio_info(self):
        node = self.node_factory.get_node(self.interface)
        if node is not None:
            return RadioInfo(node.mac_addr, node.params_name_dct['taisc'].keys(), node.measurements_name_dct['taisc'].keys(), node.events_name_dct['taisc'].keys(), self.radio_programs.keys())
        else:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("%s Interface %s does not exist!" %
                           (self.interface, fname))
            raise exceptions.InvalidArgumentException(
                func_name=fname, err_msg="Interface does not exist")

    @wishful_module.bind_function(upis.radio.get_radio_platforms)
    def get_radio_platform(self):
        # retList = []
        # for interface in self.supported_interfaces:
        #    retList.append(RadioPlatform(interface, "TAISC"))
        # return retList
        return self.supported_interfaces
