import logging
import datetime
try:
   import cPickle as pickle
except:
   import pickle

from data_filter import *
from rule import *
from event import *
from action import *
from match import *

from wishful_framework import msgs

__author__ = "Piotr Gawlowicz, Anatolij Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, zubow}@tkn.tu-berlin.de"


class Rule(object):
    def __init__(self, manager, rule):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))

        self.manager = manager

        self.event = Event(str(rule.event.type), str(rule.event.func_name), pickle.loads(str(rule.event.repeat_interval)))
        self.filters = Filter(rule.filter.filter_type, rule.filter.filter_window_type, rule.filter.filter_window_size )
        self.match = Match(rule.match.condition, pickle.loads(str(rule.match.value)))
        self.action = Action(rule.action.type, rule.action.func_name, pickle.loads(str(rule.action.args)))
        self.permanence = rule.permanence
        self.callback = rule.callback

        self.triggerEvent()

    def triggerEvent(self):
        group = "LOCAL"
        cmdDesc = msgs.CmdDesc()
        cmdDesc.type = self.event.upi_type
        cmdDesc.func_name = self.event.func_name
        cmdDesc.serialization_type = msgs.CmdDesc.PICKLE
        args = ()

        msgContainter = [group, cmdDesc, args]
        retVal = self.manager.execute_command(self.event.upi_type, msgContainter)

        retVal = retVal[2]
        retVal = pickle.loads(retVal)
        print "RULE RECEIVED RESPONSE:", retVal
        #filter
        #match
        #action if matched
        #call callback
        #remove if transient 

        #schedule next event!
        execTime = datetime.datetime.now() + datetime.timedelta(seconds=self.event.repeat_interval)
        self.manager.schedule_next_event(self, execTime)