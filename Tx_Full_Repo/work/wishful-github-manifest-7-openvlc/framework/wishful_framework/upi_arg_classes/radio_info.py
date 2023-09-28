__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, Ghent University, iMinds"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"

class RadioInfo(object):
    def __init__(self, hw_addr, parameters, events, measurements, radio_programs):
        self.hw_addr = hw_addr
        self.parameters = parameters
        self.events = events
        self.measurements = measurements
        self.radio_programs = radio_programs

class RadioPlatform(object):
    def __init__(self, interface, driver):
        self.interface = interface
        self.driver = driver
