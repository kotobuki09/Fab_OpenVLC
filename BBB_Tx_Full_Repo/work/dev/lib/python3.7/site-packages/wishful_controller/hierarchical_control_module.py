import logging
import inspect
import gevent
from gevent.queue import Queue
import wishful_framework as wishful_module
import wishful_upis as upis


__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


class LocalControlProgramDescriptor(object):
    def __init__(self, hc, agentUuid, program_id):
        self.log = logging.getLogger('LocalControlProgramDescriptor_{}'.format(program_id))
        self.agentUuid = agentUuid
        self.id = program_id
        self.hc = hc
        self.queue = Queue()

    def _receive_msg(self, msg):
        self.queue.put(msg)

    def recv(self, block=True, timeout=None):
        try:
            self.log.debug("Waiting for msg in blocking call")
            msg = self.queue.get(block=True, timeout=timeout)
            return msg
        except gevent.timeout.Timeout as e:
            return None
        except gevent.queue.Empty as e:
            return None

    def send(self, msg):
        return self.hc.send_msg_to_local_control_program(self.id, msg, self.agentUuid)

    def close(self):
        return self.hc.stop_local_control_program(self.id, self.agentUuid)


@wishful_module.build_module
class HierarchicalControlModule(wishful_module.ControllerModule):
    def __init__(self, controller):
        super(HierarchicalControlModule, self).__init__(controller)
        self.log = logging.getLogger('HierarchicalControlModule')

        self.local_progs_by_node = {}


    def receive_from_local_ctr_program(self, msg):
        node_uuid = msg["node_uuid"]
        control_program_id = msg["control_program_id"]
        msg = msg["msg"]

        localPrograms = []
        if node_uuid in self.local_progs_by_node:
            localPrograms = self.local_progs_by_node[node_uuid]

        myProg = None
        for program in localPrograms:
            if control_program_id == program.id:
                myProg = program
                break

        if myProg:
            myProg._receive_msg(msg)


    @wishful_module.bind_function(upis.mgmt.add_rule)
    def add_rule(self):
        self.log.debug("add_rule".format())
        #do some stuff here
        pass


    @wishful_module.bind_function(upis.mgmt.delete_rule)
    def delete_rule(self):
        self.log.debug("delete_rule".format())
        #do some stuff here
        retVal = "OK"
        return retVal


    @wishful_module.bind_function(upis.mgmt.start_local_control_program)
    def start_local_control_program(self, program):
        self.log.debug("start_local_control_program".format())
        funcCode = inspect.getsourcelines(program)
        funcCode = funcCode[0]
        funcCode = ''.join(funcCode)
        funcName = program.__name__

        destNode = self.controller._scope
        destNode = self.controller.nodeManager.get_node_by_str(destNode)
        destNodeUuid = destNode.id

        #do not need to set context, it is already set??
        local_id = self.controller.blocking(True).mgmt.start_local_control_program(program_name=funcName, program_code=funcCode)
        descriptor = LocalControlProgramDescriptor(self, destNodeUuid, local_id)

        if destNodeUuid in self.local_progs_by_node:
            self.local_progs_by_node[destNodeUuid].append(descriptor)
        else:
            self.local_progs_by_node[destNodeUuid] = [descriptor]

        return descriptor

    @wishful_module.bind_function(upis.mgmt.stop_local_control_program)
    def stop_local_control_program(self, fid, agentUuid=None):
        self.log.debug("stop_local_control_program".format())
        if agentUuid:
            retVal = self.controller.blocking(True).node(agentUuid).mgmt.stop_local_control_program(fid)
        else:
            retVal = self.controller.blocking(True).mgmt.stop_local_control_program(fid)
        return retVal

    def send_msg_to_local_control_program(self, fid, msg, agentUuid=None):
        self.log.debug("send_msg_to_local_control_program".format())
        if agentUuid:
            retVal = self.controller.blocking(True).node(agentUuid).mgmt.send_msg_to_local_control_program(fid, msg)
        else:
            retVal = self.controller.blocking(True).mgmt.send_msg_to_local_control_program(fid, msg)
        return retVal