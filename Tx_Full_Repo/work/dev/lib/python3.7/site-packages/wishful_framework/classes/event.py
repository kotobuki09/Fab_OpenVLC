import logging

__author__ = "Piotr Gawlowicz, Anatolij Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, zubow}@tkn.tu-berlin.de"


class Event(object):
    def __init__(self, etype):
        self.type = etype
        pass


class TimeEvent(Event):
    def __init__(self, func, args=(), kwargs={}, interval=1, iface=None):
        super(TimeEvent, self).__init__("TimeEvent")
        upiType = func.__module__
        upiType = upiType.split(".")
        upiType = upiType[len(upiType)-1]
        self.upi_type = upiType
        self.upi_func = func.__name__
        
        self.kwargs = {}
        self.kwargs["args"] = ()
        self.kwargs["kwargs"] = {}
        if args:
            self.kwargs["args"] = args
        if kwargs:
            self.kwargs["kwargs"] = kwargs

        self.interval = interval
        self.iface = iface


class PktEvent(Event):
    def __init__(self, iface):
        super(PktEvent, self).__init__("PktEvent")
        self.iface = iface

class PktMatch(object):
    def __init__(self, matchStr):
        self.matchStr = matchStr

class FieldSelector(object):
    def __init__(self, field):
        self.field = field