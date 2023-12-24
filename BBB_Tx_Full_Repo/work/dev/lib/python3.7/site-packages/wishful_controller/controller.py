import logging
import time
import sys
import zmq.green as zmq
import uuid
import datetime
import gevent
from gevent import Greenlet
from gevent.event import AsyncResult
from gevent.local import local

import wishful_framework as msgs
from wishful_framework import upis_builder
from wishful_framework import rule_manager
from wishful_framework import generator_manager
from .transport_channel import TransportChannel
from .node_manager import NodeManager, Node
from .module_manager import ModuleManager
from .hierarchical_control_module import HierarchicalControlModule


__author__ = "Piotr Gawlowicz, Mikolaj Chwalisz"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, chwalisz}@tkn.tu-berlin.de"


class CallIdCallback(object):
    def __init__(self, cb, callNum):
        self.cb = cb
        self.callNum = callNum
        self.callbackFireNum = 0
        self.readyToRemove = False

    def get_callback(self):
        self.callbackFireNum = self.callbackFireNum + 1
        if self.callbackFireNum == self.callNum:
            self.readyToRemove = True
        return self.cb

    def ready_to_remove(self):
        return self.readyToRemove


class AsyncResultCollector(object):
    def __init__(self, callNum):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))
        self.callNum = callNum
        self.results = {}
        self.ready = False
        self.exception = None
        self.asyncResult = AsyncResult()

    def return_response(self):
        if self.exception:
            raise self.exception

        if len(list(self.results.values())) > 1:
            return self.results
        else:
            key, value = self.results.popitem()
            return value       

    def get(self, block=True, timeout=None):
        if len(list(self.results.values())) == self.callNum:
            return self.return_response()

        try:
            self.log.debug("Waiting for result in blocking call")
            self.asyncResult.get(timeout=timeout)
        except gevent.timeout.Timeout as e:
            return None
        return self.return_response()

    def set_exception(self, node, e):
        self.exception = e
        self.results[node] = e

        if len(list(self.results.values())) == self.callNum:
            self.ready = True
            self.asyncResult.set()

    def set(self, node, msg):
        self.results[node] = msg

        if len(list(self.results.values())) == self.callNum:
            self.ready = True
            self.asyncResult.set()


local_func_call_context = local()

class Controller(Greenlet):
    def __init__(self, dl=None, ul=None):
        Greenlet.__init__(self)
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))

        self.uuid = str(uuid.uuid4())
        self.name = "Controller"
        self.info = "WiSHFUL COntroller"
        self.config = None

        self.default_callback = None
        self.callbacks = {}
        self.call_id_gen = 0

        self.moduleManager = ModuleManager(self)
        self.nodeManager = NodeManager(self)

        self.transport = TransportChannel(ul, dl)
        self.transport.subscribe_to(self.uuid)
        self.transport.set_recv_callback(self.process_msgs)

        #Hierarchical Control Module
        self.hc = HierarchicalControlModule(self)
        self.hc.set_controller(self)

        #UPIs
        builder = upis_builder.UpiBuilder(self)
        self.radio = builder.create_radio()
        self.net = builder.create_net()
        self.mgmt = builder.create_mgmt()
        self.context = builder.create_context()

        #Rule manager
        self.rule = rule_manager.RuleManager(self)

        #Generator manager
        self.generator = generator_manager.GeneratorManager(self)

        #function call context
        self._scope = None
        self._iface = None
        self._exec_time = None
        self._delay = None
        self._timeout = None
        self._blocking = True
        self._callback = None

        #fill thread local variable with default values
        self._clear_call_context()
        
        #container for blocking calls
        self._asyncResults = {}

    def stop(self):
        self.running = False
        self.log.debug("Nofity EXIT to all modules")
        self.moduleManager.exit()
        self.transport.stop()
        self.kill()

    def _run(self):
        #fill thread local variable with default values
        self._clear_call_context()

        self.log.debug("Controller starts".format())
        self.log.debug("Nofity START to all modules")
        self.moduleManager.start()
        self.transport.start()

        self.running = True
        while self.running:
            self.transport.start_receiving()

    def group(self, group):
        self._scope = group
        local_func_call_context._scope = group
        return self

    def node(self, node):
        self._scope = node
        local_func_call_context._scope = node
        return self        

    def nodes(self, nodelist):
        self._scope = nodelist
        local_func_call_context._scope = nodelist
        return self

    def iface(self, iface):
        self._iface = iface
        local_func_call_context._iface = iface
        return self

    def exec_time(self, exec_time):
        self._exec_time = exec_time
        local_func_call_context._exec_time = exec_time
        return self

    def delay(self, delay):
        self._delay = delay
        local_func_call_context._delay = delay
        return self

    def timeout(self, value):
        self._timeout = value
        local_func_call_context._timeout = value
        return self

    def blocking(self, value=True):
        self._blocking = value
        local_func_call_context._blocking = value
        return self

    def callback(self, callback):
        self._callback = callback
        local_func_call_context._callback = callback
        return self


    def _clear_call_context(self):
        self._scope = None
        self._iface = None
        self._exec_time = None
        self._delay = None
        self._timeout = None
        self._blocking = True
        self._callback = None

        local_func_call_context._scope = None
        local_func_call_context._iface = None
        local_func_call_context._exec_time = None
        local_func_call_context._delay = None
        local_func_call_context._timeout = None
        local_func_call_context._blocking = True
        local_func_call_context._callback = None


    def fire_callback(self, callback, *args, **kwargs):
        self._clear_call_context()
        callback(*args, **kwargs)


    def set_controller_info(self, name=None, info=None):
        self.name = name
        self.info = info


    def add_module(self, moduleName, pyModuleName, className, kwargs={}, importAs=None):
        self.log.debug("Adding module: {}:{}:{}:{}".format(moduleName, pyModuleName, className, kwargs))
        upiModule = self.moduleManager.add_module(moduleName, pyModuleName, className, kwargs)
        if importAs:
            setattr(self, importAs, upiModule)


    def load_config(self, config):
        self.log.debug("Config: {}".format(config))

        if "controller" in config:
            controllerInfo = config["controller"]
            self.log.debug("Controller info from config file: {}".format(controllerInfo))

            if "name" in controllerInfo:
                self.name = controllerInfo["name"]

            if "info" in controllerInfo:
                self.info = controllerInfo["info"]

            if "dl" in controllerInfo:
                self.transport.set_downlink(controllerInfo["dl"])

            if "downlink" in controllerInfo:
                self.transport.set_downlink(controllerInfo["downlink"])

            if "ul" in controllerInfo:
                self.transport.set_uplink(controllerInfo["ul"])

            if "uplink" in controllerInfo:
                self.transport.set_uplink(controllerInfo["uplink"])

        #load modules
        if 'modules' in config:
            moduleDesc = config['modules']
            for m_name, m_params in moduleDesc.items():
                kwargs = {}
                importAs = None
                if 'kwargs' in m_params:
                    kwargs = m_params['kwargs']

                if "import_as" in m_params:
                    importAs = m_params['import_as']

                self.add_module(m_name, m_params['module'], m_params['class_name'], kwargs, importAs)


    def new_node_callback(self, **options):
        def decorator(callback):
            self.nodeManager.add_new_node_callback(callback)
            return callback
        return decorator


    def node_exit_callback(self, **options):
        def decorator(callback):
            self.nodeManager.add_node_exit_callback(callback)
            return callback
        return decorator


    def add_callback(self, function, **options):
        def decorator(callback):
            self.log.debug("Register callback for: {}".format(function.__name__))
            self.callbacks[function.__name__] = callback
            return callback
        return decorator


    def set_default_callback(self, **options):
        def decorator(callback):
            self.log.debug("Setting default callback")
            self.default_callback = callback
            return callback
        return decorator


    def generate_call_id(self):
        self.call_id_gen = self.call_id_gen + 1
        return self.call_id_gen


    def send_cmd_to_node(self, destNode, callId, msgContainer):
        #translate to node if needed
        if not isinstance(destNode, Node):
            destNode = self.nodeManager.get_node_by_str(destNode)


        #check if function is supported by agent, if not raise exception
        cmdDesc = msgContainer[0]
        upi_type = cmdDesc.type
        fname = cmdDesc.func_name
        iface = cmdDesc.interface

        if not destNode:
            raise Exception("Node for UPI function: {}:{} is not available".format(upi_type, fname))

        if not destNode.is_upi_supported(iface=iface, upi_type=upi_type, fname=fname):
            raise Exception("Node: {} does not support UPI Function: {}:{} \
                for iface: {}, please install proper modules".format(destNode.name, upi_type, fname, iface))


        #set destination
        myMsgContainter = [destNode.id]
        myMsgContainter.extend(msgContainer)
        self.log.debug("Controller sends cmd message to node: {}".format(destNode.id))
        self.transport.send_downlink_msg(myMsgContainter)


    def exec_cmd(self, upi_type, fname, *args, **kwargs):
        self.log.debug("Controller builds cmd message: {}.{} with args:{}, kwargs:{}".format(upi_type, fname, args, kwargs))
        
        #get function call context
        scope = local_func_call_context._scope
        iface = local_func_call_context._iface
        exec_time = local_func_call_context._exec_time
        delay = local_func_call_context._delay
        timeout = local_func_call_context._timeout
        blocking = local_func_call_context._blocking
        callback = local_func_call_context._callback

        self._clear_call_context()

        nodeNum = None
        callId = str(self.generate_call_id())

        #build cmd desc message
        cmdDesc = msgs.CmdDesc()
        cmdDesc.type = upi_type
        cmdDesc.func_name = fname
        cmdDesc.call_id = callId

        if iface:
            cmdDesc.interface = iface

        if delay:
            exec_time = datetime.datetime.now() + datetime.timedelta(seconds=delay)
            blocking = False

        if exec_time:
            cmdDesc.exec_time = str(exec_time)
            blocking = False

        #call check
        if exec_time and exec_time < datetime.datetime.now():
            raise Exception("Scheduling function: {}:{} call in past".format(upi_type,fname))

        #count nodes if list passed
        if hasattr(scope, '__iter__') and not isinstance(scope, str):
            nodeNum = len(scope)
        else:
            nodeNum = 1

        #set callback for this function call 
        if callback:
            self.callbacks[callId] = CallIdCallback(callback, nodeNum)
            blocking = False

        #if blocking call, wait for response
        if blocking:
            asyncResultCollector = AsyncResultCollector(nodeNum)
            self._asyncResults[callId] = asyncResultCollector

        #Serialize kwargs (they contrain args)
        cmdDesc.serialization_type = msgs.CmdDesc.PICKLE
        msgContainer = [cmdDesc, kwargs]
        

        #TODO: currently sending cmd msg to each node separately;
        #it would be more efficient to exploit PUB/SUB zmq mechanism
        #create group with uuid and tell nodes to subscribe to this uuid
        #then send msg to group
        if hasattr(scope, '__iter__') and not isinstance(scope, str):
            for node in scope:
                self.send_cmd_to_node(node, callId, msgContainer)
        else:
            node = scope
            self.send_cmd_to_node(node, callId, msgContainer)


        #if blocking call, wait for response
        if blocking:
            response = asyncResultCollector.get(timeout=timeout)
            del self._asyncResults[callId]
            return response

        return None


    def process_msgs(self, msgContainer):
        dest = msgContainer[0]
        cmdDesc = msgContainer[1]
        msg = msgContainer[2]

        self.log.debug("Controller received message: {} from agent".format(cmdDesc.type))

        if cmdDesc.type == msgs.get_msg_type(msgs.NewNodeMsg):
            self.nodeManager.add_node(msgContainer)

        elif cmdDesc.type == msgs.get_msg_type(msgs.HelloMsg):
            self.nodeManager.serve_hello_msg(msgContainer)

        elif cmdDesc.type == msgs.get_msg_type(msgs.NodeExitMsg):
            self.nodeManager.remove_node(msgContainer)

        elif cmdDesc.type == "hierarchical_control":
            self.hc.receive_from_local_ctr_program(msg)

        elif cmdDesc.type == "wishful_rule":
            self.rule._receive("all", self.nodeManager.get_node_by_id(cmdDesc.caller_id), msg)

        elif cmdDesc.type == "wishful_generator":
            self.generator._receive("all", self.nodeManager.get_node_by_id(cmdDesc.caller_id), msg)

        else:
            self.log.debug("Controller received message: {}:{} from agent".format(cmdDesc.type, cmdDesc.func_name))

            callId = cmdDesc.call_id
            if callId in self._asyncResults:
                #TODO: define new protobuf message for return values; currently using repeat_number in CmdDesc 
                #0-executed correctly, 1-exception
                if cmdDesc.repeat_number == 0:
                    self._asyncResults[callId].set(self.nodeManager.get_node_by_id(cmdDesc.caller_id), msg)
                else:
                    self._asyncResults[callId].set_exception(self.nodeManager.get_node_by_id(cmdDesc.caller_id), msg)

            else:
                if cmdDesc.call_id in self.callbacks:
                    callbackObj = self.callbacks[cmdDesc.call_id]
                    callback = callbackObj.get_callback()
                    gevent.spawn(self.fire_callback, callback, "all", self.nodeManager.get_node_by_id(cmdDesc.caller_id), msg)
                    if callbackObj.ready_to_remove():
                        del self.callbacks[cmdDesc.call_id]

                elif cmdDesc.func_name in self.callbacks:
                    callback = self.callbacks[cmdDesc.func_name]
                    gevent.spawn(self.fire_callback, callback, "all", self.nodeManager.get_node_by_id(cmdDesc.caller_id), msg)

                elif self.default_callback:
                    gevent.spawn(self.fire_callback, self.default_callback, "all", self.nodeManager.get_node_by_id(cmdDesc.caller_id), cmdDesc.func_name, msg)

                else:
                    self.log.debug("Response to: {}:{} not served".format(cmdDesc.type, cmdDesc.func_name))
