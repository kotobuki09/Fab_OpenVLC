__author__ = "Piotr Gawlowicz, Anatolij Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, zubow}@tkn.tu-berlin.de"

'''
    The protocol-specific definition of WiSHFUL global control interface, UPI_G, for performing network-wide operations
    which go beyond just remote UPI_R/N calls

    IEEE 802.11 protocol family
'''

def perform_handover(interface, servingNode, targetNode, device_mac_addr, **kwargs):
    '''Performing an handover operation.

    Note: this is not supported on any wireless technology.

    - 802.11 - in infrastructure mode an STA can be handovered; not supported in 802.11 adhoc
    '''
    pass


def is_associated_with(nodes, interface, device_mac_addr):
    '''Estimate the AP/BS with which a given device is associated.

    Note: this is not supported on any wireless technology.

    - enabled on 802.11 infrastructure mode
    '''
    pass
