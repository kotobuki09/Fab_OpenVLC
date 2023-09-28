__author__ = "Piotr Gawlowicz, Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, zubow}@tkn.tu-berlin.de"

'''IEEE 802.15.4 protocol family

The protocol-specific definition of the WiSHFUL radio control interface, UPI_R,
for configuration/monitoring of the lower layers of the network protocol stack
(lower MAC and PHY).

'''

PARAMETERS = [
    "IEEE802154_macMaxBE",
    "IEEE802154_macMaxCSMABackoffs",
    "IEEE802154_macMaxFrameRetries",
    "IEEE802154_macMinBE",
    "IEEE802154_macPANId",
    "IEEE802154_macShortAddress",
    "IEEE802154_macExtendedAddress",
    "IEEE802154_phyCurrentChannel",
    "IEEE802154_phyTXPower",
    "IEEE802154e_macHoppingSequenceLength",
    "IEEE802154e_macHoppingSequenceList",
    "IEEE802154e_macSlotframeSize",
    "IEEE802154e_macTimeslot",
    "IEEE802154e_macTsTimeslotLength",
    "TAISC_ACTIVERADIOPROGRAM",
    "IEEE802154_MACSTATS",
    "IEEE802154_event_macStats",
]


def blacklist_channels():
    return
