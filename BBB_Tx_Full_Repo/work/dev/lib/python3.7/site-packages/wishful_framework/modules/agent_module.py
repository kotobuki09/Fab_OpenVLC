import logging
import random
import sys
import time
import threading
from .wishful_module import *
from wishful_framework import msgs

__author__ = "Piotr Gawlowicz, Mikolaj Chwalisz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, chwalisz}@tkn.tu-berlin.de"


class AgentModule(WishfulModule):
    def __init__(self):
        super(AgentModule, self).__init__()
        self.agent = None

    def set_agent(self, agent):
        self.agent = agent

    def send_to_module(self, msgContainer):
        self.log.debug("Module {} received cmd".format(self.__class__.__name__))
        
        assert len(msgContainer) == 3
        dest = msgContainer[0]
        cmdDesc = msgContainer[1]
        kwargs = msgContainer[2]

        self.log.debug("Process msg: {}:{}".format(cmdDesc.type, cmdDesc.func_name))
        command = cmdDesc.func_name

        #set interface before UPI function call, so we can use self.interface in function
        self.interface = None
        if cmdDesc.HasField('interface'):
            self.interface = cmdDesc.interface


        #if first call to module, execute function decorated with before_firtst_call_to_module
        if self.firstCallToModule:
            self.firstCallToModule = False
            self.first_call_to_module()


        #TODO: check if function is available
        func = getattr(self, command)

        #if there is function that has to be called before UPI function, call it
        if hasattr(func, '_beforeCall'):
            before_func = getattr(self, func._beforeCall)
            before_func()

        my_args = ()
        my_kwargs = {}
        if kwargs:
            my_args = kwargs['args']
            my_kwargs = kwargs['kwargs']

        retVal = None
        exception = False
        try:
            retVal = func(*my_args, **my_kwargs)
        except Exception as e:
            self.log.warning("Exception: {}".format(e))
            exception = True
            retVal = e

        #if there is function that has to be called after UPI function, call it
        if hasattr(func, '_afterCall'):
            after_func = getattr(self, func._afterCall)
            after_func()

        dest = "controller"
        respDesc = msgs.CmdDesc()
        respDesc.type = cmdDesc.type
        respDesc.func_name = cmdDesc.func_name
        respDesc.call_id = cmdDesc.call_id

        #TODO: define new protobuf message for return values; currently using repeat_number in CmdDesc 
        #0-executed correctly, 1-exception
        if exception:
            respDesc.repeat_number = 1
        else:
            respDesc.repeat_number = 0

        #Serialize return value
        respDesc.serialization_type = msgs.CmdDesc.PICKLE
        response = [dest, respDesc, retVal]

        return response

    def before_call(self, msgContainer):
        assert len(msgContainer) == 3
        dest = msgContainer[0]
        cmdDesc = msgContainer[1]
        kwargs = msgContainer[2]

        self.log.debug("Before call: {}:{}".format(cmdDesc.type, cmdDesc.func_name))
        command = cmdDesc.func_name
        #TODO: check if function is available
        func = getattr(self, command)

        #set interface before UPI function call, so we can use self.interface in function
        self.interface = None
        if cmdDesc.HasField('interface'):
            self.interface = cmdDesc.interface

        #if first call to module, execute function decorated with before_firtst_call_to_module
        if self.firstCallToModule:
            self.firstCallToModule = False
            self.first_call_to_module()

        #if there is function that has to be called before UPI function, call it
        if hasattr(func, '_beforeCall'):
            before_func = getattr(self, func._beforeCall)
            #execute_function checks if need to run in new thread, and do so if true
            self.execute_function(before_func)


    def execute_call(self, msgContainer):
        assert len(msgContainer) == 3
        dest = msgContainer[0]
        cmdDesc = msgContainer[1]
        kwargs = msgContainer[2]

        self.log.debug("Execute call: {}:{}".format(cmdDesc.type, cmdDesc.func_name))
        command = cmdDesc.func_name
        #TODO: check if function is available
        func = getattr(self, command)

        #set interface before UPI function call, so we can use self.interface in function
        self.interface = None
        if cmdDesc.HasField('interface'):
            self.interface = cmdDesc.interface

        my_args = ()
        my_kwargs = {}
        if kwargs:
            my_args = kwargs['args']
            my_kwargs = kwargs['kwargs']

        retVal = None
        exception = False
        try:
            retVal = func(*my_args, **my_kwargs)
        except Exception as e:
            self.log.warning("Exception: {}".format(e))
            exception = True
            retVal = e

        dest = "controller"
        respDesc = msgs.CmdDesc()
        respDesc.type = cmdDesc.type
        respDesc.func_name = cmdDesc.func_name
        respDesc.call_id = cmdDesc.call_id

        #TODO: define new protobuf message for return values; currently using repeat_number in CmdDesc 
        #0-executed correctly, 1-exception
        if exception:
            respDesc.repeat_number = 1
        else:
            respDesc.repeat_number = 0

        #Serialize return value
        respDesc.serialization_type = msgs.CmdDesc.PICKLE
        response = [dest, respDesc, retVal]

        return response

    def after_call(self, msgContainer):
        assert len(msgContainer) == 3
        dest = msgContainer[0]
        cmdDesc = msgContainer[1]
        kwargs = msgContainer[2]

        self.log.debug("Execute call: {}:{}".format(cmdDesc.type, cmdDesc.func_name))
        command = cmdDesc.func_name
        #TODO: check if function is available
        func = getattr(self, command)

        #set interface before UPI function call, so we can use self.interface in function
        self.interface = None
        if cmdDesc.HasField('interface'):
            self.interface = cmdDesc.interface

        #if there is function that has to be called after UPI function, call it
        if hasattr(func, '_afterCall'):
            after_func = getattr(self, func._afterCall)
            #execute_function checks if need to run in new thread, and do so if true
            self.execute_function(after_func)