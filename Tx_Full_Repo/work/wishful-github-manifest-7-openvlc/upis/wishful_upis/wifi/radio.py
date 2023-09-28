__author__ = "Piotr Gawlowicz, Mikolaj Chwalisz, Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, chwalisz, zubow}@tkn.tu-berlin.de"

'''
    The protocol-specific definition of the WiSHFUL radio control interface, UPI_R, for configuration/monitoring of the
    lower layers of the network protocol stack (lower MAC and PHY).

    IEEE 802.11 protocol family
'''

'''
    MAC layer
'''

def set_mac_access_parameters(queueId, qParam):
    '''MAC access parameters in 802.11e: the configuration of the access categories
    '''
    pass


def get_mac_access_parameters(queueId):
    '''MAC access parameters: in 802.11e: the configuration of the access categories
    '''
    pass


'''
    PHY layer
'''


def get_airtime_utilization():
    '''Returns the relative time the spectrum is empty.
    '''
    pass


def perform_spectral_scanning(iface, freq_list, mode):
    '''Perform spectral scanning.

    Returns:
        Power value for each frequency bin.
    '''
    pass


def set_channel(iface, channel):
    '''Set channel, i.e. center frequency of the primary band.

    Args:
        channel: channel to set
    '''
    pass


def get_channel():
    '''Get channel, i.e. center frequency of the primary band.
    '''
    pass


def set_modulation_rate(rate_Mbps):
    '''Set rate modulation
    '''
    pass


def configure_radio_sensitivity(phy_dev, **kwargs):
    '''Configuring the receiving sensitivity of the IEEE 802.11 radio.
    '''
    pass


''' Per flow transmit power control '''

def set_per_flow_tx_power(flowId, txPower):
    """Sets for a flow identified by an 5-tuple (IP header) the transmit power to be used.
    """
    return


def clean_per_flow_tx_power_table():
    """Remove any entries in the transmit power table.
    """
    return


def get_per_flow_tx_power(flowId):
    """Return the transmit power level used for the given flow.
    """
    return


def get_per_flow_tx_power_table():
    """Return the whole transmit power table.
    """
    return


def install_mac_processor(interface, mac_profile):
    """
    Install new WiFi MAC Processor
    """
    return


def update_mac_processor(interface, mac_profile):
    """
    Update WiFi MAC Processor
    """
    pass


def uninstall_mac_processor(interface, mac_profile):
    """
    Uninstall WiFi MAC Processor
    """
    pass


'''
    Channel state information and spectrum scanning capabilities.
'''

def receive_csi(runt):
    '''Receives CSI samples from the ath9k driver.
    '''
    pass


def scan_psd(runt):
    '''Receives PSD samples from the ath9k driver.
    '''
    pass
