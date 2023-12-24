import logging

__author__ = "Piotr Gawlowicz, Anatolij Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, zubow}@tkn.tu-berlin.de"


class Filter(object):
    def __init__(self, filter_type):
        self.filter_type = filter_type


class MovAvgFilter(Filter):
    def __init__(self, window_size):
        super(MovAvgFilter, self).__init__("MovAvgFilter")
        self.window_size = window_size


class PeakDetector(Filter):
    def __init__(self, threshold):
        super(PeakDetector, self).__init__("PeakDetector")      
        self.threshold = threshold