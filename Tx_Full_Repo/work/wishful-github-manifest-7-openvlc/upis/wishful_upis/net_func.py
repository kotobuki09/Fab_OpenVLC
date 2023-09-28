from .lte.net_func import *
from .wifi.net_func import *
from .lowpan.net_func import *


__author__ = "Piotr Gawlowicz, Anatolij Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, zubow}@tkn.tu-berlin.de"

'''The WiSHFUL global control interface, UPI_G.

Used for performing network-wide operations which go beyond just remote
UPI_R/N calls. Example are estimating the nodes in carrier sensing range.
'''

# Generic functionality which should be supported by most of the platforms.

def estimate_nodes_in_carrier_sensing_range(nodes, interface, **kwargs):
    """Estimate which nodes are in carrier sensing range using UPIs.

    For a network with N nodes all combinations are evaluated, i.e. N over 2.

    Note:
       make sure that all nodes are time synchronized.

    Returns:
        list of tuples: In form of (node1, node2, True/False), where True/False if nodes are in
        carrier sensing range
    """
    pass


def is_in_carrier_sensing_range(node1, node2, interface, **kwargs):
    """Estimate whether two nodes are in carrier sensing range or not.

    Note:
        it is implemented differently on different platforms
    """
    pass


def estimate_nodes_in_communication_range(self, nodes, interface, **kwargs):
    """Estimate which nodes are in communication range using UPIs.

    For a network with N nodes all combinations are evaluated, i.e. N over 2.

    Note:
        make sure that all nodes are time synchronized.

    Returns:
        list of tuples: In form of (node1, node2, True/False), where True/False if nodes are in
        communication range
    """
    pass


def is_in_communication_range(node1, node2, interface, **kwargs):
    """Estimate whether two nodes are in communication range or not.
    """
    pass
