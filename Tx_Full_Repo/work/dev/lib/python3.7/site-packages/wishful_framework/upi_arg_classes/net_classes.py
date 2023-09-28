__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, Ghent University, iMinds"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"

class NetworkInfo(object):
    def __init__(self, ip_addr, parameters, measurements, events):
        self.ip_addr = ip_addr
        self.parameters = parameters
        self.measurements = measurements
        self.events = events
