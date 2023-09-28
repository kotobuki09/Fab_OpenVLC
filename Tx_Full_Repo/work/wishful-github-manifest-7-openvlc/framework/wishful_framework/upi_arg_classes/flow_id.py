__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


class FlowId(object):
    def __init__(self, srcAddress=None, dstAddress=None, prot=None, srcPort=None, dstPort=None):
        self.srcAddress = srcAddress
        self.dstAddress = dstAddress
        self.prot = prot
        self.srcPort = srcPort
        self.dstPort = dstPort