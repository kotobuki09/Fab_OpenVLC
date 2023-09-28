import logging
from collections import deque

from wishful_framework import CmdDesc


__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz}@tkn.tu-berlin.de"


class FilterContainter(object):
    def __init__(self):
        self.log = logging.getLogger('FilterContainter')
        self.filters = []
        self.sampleNum = 0

    def add_filter(self, myfilter):
        self.filters.append(myfilter)

    def __call__(self, sample):
        self.sampleNum = self.sampleNum + 1
        self.log.debug("Before filtering: {}".format(sample))
        #print "Before filtering: {}".format(sample)
        for f in self.filters:
            if sample:
                sample = f(sample)
            else:
                break
        self.log.debug("\tAfter filtering: {}".format(sample))
        #print "\tAfter filtering: {}".format(sample)
        if sample:
            return sample


class PeakDetectorObj(object):
    def __init__(self, threshold=0):
        self.threshold = threshold

    def __call__(self, sample):
        if sample >= self.threshold:
            return sample


class MovAvgFilterObj(object):
    def __init__(self, length=5):
        self.length = length
        self.samples = deque()

    def __call__(self, sample):
        sample = int(sample)
        self.samples.append(sample)

        if len(self.samples) == self.length:
            s = sum(self.samples)
            self.samples.popleft()
            return s / self.length
        return None

class ActionObject(object):
    def __init__(self, agent, actionDesc):
        self.log = logging.getLogger('ActionObject')
        self.agent = agent
        self.upi_type = actionDesc.upi_type
        self.upi_func = actionDesc.upi_func
        self.kwargs = actionDesc.kwargs
        self.iface = actionDesc.iface

    def __call__(self, sample):
        cmdDesc = CmdDesc()
        cmdDesc.type = self.upi_type
        cmdDesc.func_name = self.upi_func
        cmdDesc.call_id = str(0)
        if self.iface:
            cmdDesc.interface = self.iface
        kwargs = self.kwargs
        msgContainer = ["agent", cmdDesc, kwargs]

        self.log.debug("Rule matched, executing action: {}.{}({})".format(self.upi_type,self.upi_func,self.kwargs))
        response = self.agent.moduleManager.send_cmd_to_module_blocking(msgContainer)
        retVal = response[2]
        self.log.debug("Action executed, returned value: {}".format(retVal))
        return sample


class MatchObject(object):
    def __init__(self, matchDesc):
        self.condition = matchDesc.condition
        self.threshold = matchDesc.value

        self.operator_dict = {}
        self.operator_dict["=="] = lambda x,y : x==y
        self.operator_dict["<>"] = lambda x,y : x!=y
        self.operator_dict["!="] = lambda x,y : x!=y
        self.operator_dict["not"]= lambda x,y : x!=y
        self.operator_dict["~="] = lambda x,y : x!=y
        self.operator_dict[">"] = lambda x,y : x>y
        self.operator_dict[">="] = lambda x,y : x>=y
        self.operator_dict["<"] = lambda x,y : x<y
        self.operator_dict["<="] = lambda x,y : x<=y

    def __call__(self, x):
        return self.operator_dict[self.condition](x, self.threshold)