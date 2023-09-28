"""The WiSHFUL radio control interface, UPI_R.
Used for configuration/monitoring of the lower
layers of the network protocol stack (lower MAC and PHY).

Note, here all generic functions are defined, i.e. those which can be
supported by any wireless networking node (IEEE 802.11, LTE, ZigBee).

All protocol-dependent functions are defined in separate folder,
e.g. ``wifi/``, ``lowpan/`` or ``lte/``.
"""
__author__ = "Piotr Gawlowicz, Mikolaj Chwalisz, Anatolij Zubow, Peter Ruckebusch, Domenico Garlisi"
__copyright__ = "Copyright (c) 2016, Technische Universitat Berlin, iMinds, CNIT"
__version__ = "0.1.0"
__email__ = "{gawlowicz, chwalisz, zubow}@tkn.tu-berlin.de, peter.ruckebusch@intec.ugent.be, "

from .meta_models import ValueDoc, Attribute, Measurement, Event, Action

# # ATTRIBUTES
TX_POWER = Attribute(key='TX_POWER', type=int, isReadOnly=False) #:Transmission power in dBm
TX_ANTENNA = Attribute(key='TX_ANTENNA', type=int, isReadOnly=False) #:Antenna number selected for transmission
RX_ANTENNA = Attribute(key='RX_ANTENNA', type=int, isReadOnly=False) #:Antenna number selected for reception

NETWORK_INTERFACE_HW_ADDRESS = Attribute(key='NETWORK_INTERFACE_HW_ADDRESS', type=int, isReadOnly=False) #:MAC address of wireless network interface card

TDMA_SUPER_FRAME_SIZE = Attribute(key='TDMA_SUPER_FRAME_SIZE', type=int, isReadOnly=False) #:TDMA protocol. Duration of periodic frames used for slot allocations in us
TDMA_NUMBER_OF_SYNC_SLOT = Attribute(key='TDMA_NUMBER_OF_SYNC_SLOT', type=int, isReadOnly=False) #:TDMA protocol. Number of slots included in a super frame
TDMA_ALLOCATED_SLOT = Attribute(key='TDMA_ALLOCATED_SLOT', type=int, isReadOnly=False) #:TDMA protocol. Assigned slot in a super frame
TDMA_MAC_PRIORITY_CLASS = Attribute(key='TDMA_MAC_PRIORITY_CLASS', type=int, isReadOnly=False) #:TDMA protocol. QUEUE class service associated with TDMA radio program

CSMA_BACKOFF_VALUE = Attribute(key='CSMA_BACKOFF_VALUE', type=int, isReadOnly=False) #:CSMA protocol. Backoff value
CSMA_CW = Attribute(key='CSMA_CW', type=int, isReadOnly=False) #:CSMA protocol.current value of the Contention Window
CSMA_CW_MIN = Attribute(key='CSMA_CW_MIN', type=int, isReadOnly=False) #:CSMA protocol. Minimum value of the Contention Window
CSMA_CW_MAX = Attribute(key='CSMA_CW_MAX', type=int, isReadOnly=False) #:CSMA protocol. Maximum value of the Contention Window
CSMA_TIMESLOT = Attribute(key='CSMA_TIMESLOT', type=int, isReadOnly=False) #:CSMA protocol.Duration of the backoff slot
CSMA_EIFS = Attribute(key='CSMA_EIFS', type=int, isReadOnly=False) #:CSMA protocol.Duration of the EIFS time
CSMA_DIFS = Attribute(key='CSMA_DIFS', type=int, isReadOnly=False) #:CSMA protocol.Duration of the DIFS time
CSMA_SIFS = Attribute(key='CSMA_SIFS', type=int, isReadOnly=False) #:CSMA protocol.Duration of the SIFS time
CSMA_MAC_PRIORITY_CLASS = Attribute(key='CSMA_MAC_PRIORITY_CLASS', type=int, isReadOnly=False) #:CSMA protocol.QUEUE class service associated with CSMA radio program
CSMA_NUM_FREEZING_COUNT = Attribute(key='CSMA_NUM_FREEZING_COUNT', type=int, isReadOnly=True) #:CSMA protocol.Total number of freezing during the backoff phase


# MEASUREMENTS
NOISE = Measurement(key='NOISE', type=int) #: Level of noise in dBm
CSI = Measurement(key='CSA', type=int) #: Channel State Information' last measured value
RSSI = Measurement(key='RSSI', type=int) #:Received Signal Strength Indication (RSSI); it refers to the last received frame in dBm.
SNR = Measurement(key='SNR', type=int) #:Signal-to-noise ratio (SNR) of the last received frame in dB.
LQI = Measurement(key='LQI', type=int) #:Link Quality Indicator (LQI)
FER = Measurement(key='FER', type=int) #:Frame Erasure Rate (FER)
BER = Measurement(key='BER', type=int) #:Bit Error Rate (BER)
BUSY_TIME = Measurement(key='BUSY_TIME', type=int) #:Time interval in which the transceiver has been active (including reception, transmission and carrier sense)
EXT_BUSY_TIME = Measurement(key='EXT_BUSY_TIME', type=int) #:Time interval in which the transceiver has been active (including reception, transmission and carrier sense)
TX_ACTIVITY = Measurement(key='TX_ACTIVITY', type=int) #:Time interval in which the transceiver has been involved in transmission.
RX_ACTIVITY = Measurement(key='RX_ACTIVITY', type=int) #:Time interval in which the transceiver has been involved in transmission.
LOW_LEVEL_TIME = Measurement(key='LOW LEVEL TIME', type=int) #:Time provided by platform chipset

NUM_GOOD_PREAMBLE = Measurement(key='NUM_GOOD_PREAMBLE', type=int) #:Number of preambles correctly synchronized by the receiver.
NUM_BAD_PREAMBLE = Measurement(key='NUM_BAD_PREAMBLE', type=int) #:Number of receiver errors in synchronizing a valid preamble.
NUM_GOOD_PLCP = Measurement(key='NUM_GOOD_PLCP', type=int) #:Number of valid PLCP synchronized by the receiver
NUM_BAD_PLCP = Measurement(key='NUM_BAD_PLCP', type=int) #:Number of wrong PLCP errors triggered by the receiver
NUM_GOOD_CRC = Measurement(key='NUM_GOOD_CRC', type=int) #:Number of success of CRC checks
NUM_BAD_CRC = Measurement(key='NUM_BAD_CRC', type=int) #:Number of failures of CRC checks
NUM_TX_RTS = Measurement(key='NUM_TX_RTS', type=int) #:Total number of transmitted frames measured since the interface has been started
NUM_TX = Measurement(key='NUM_TX', type=int) #:Total number of transmitted frames measured since the interface has been started
NUM_TX_DATA_FRAME = Measurement(key='NUM_TX_DATA_FRAME', type=int) #:Total number of transmitted frames measured since the interface has been started
NUM_TX_SUCCESS = Measurement(key='NUM_TX_SUCCESS', type=int) #:Total number of successfully transmitted frame measured since the interface has been started
NUM_RX = Measurement(key='NUM_RX', type=int) #:Total number of received frames since the interface has been started
NUM_RX_ACK_RAMATCH = Measurement(key='NUM_RX_ACK_RAMATCH', type=int) #:Total number of received frames addressed to the node since the interface has been started. This measurement traces the number of received frame in which the receiver address field matches with the network interface card MAC address
NUM_RX_ACK = Measurement(key='NUM_RX_ACK', type=int) #:Total receive ack frame measured since the interface has been started
NUM_RX_SUCCESS = Measurement(key='NUM_RX_SUCCESS', type=int) #:Total number of successfully transmitted frame measured since the interface has been started
NUM_ACK_FAILURE = Measurement(key='NUM_ACK_FAILURE', type=int) #:Total number of successfully transmitted frame measured since the interface has been started
NUM_TX_MULTICAST_FRAME = Measurement(key='NUM_TX_MULTICAST_FRAME', type=int) #:Total number of successfully transmitted frame measured since the interface has been started
NUM_RTS_SUCCESS_COUNT = Measurement(key='NUM_RTS_SUCCESS_COUNT', type=int)
NUM_RTS_FAILURE_COUNT = Measurement(key='NUM_RTS_FAILURE_COUNT', type=int)

# EVENTS
CHANNEL_UP = Event(key='CHANNEL_UP', type=None) #:Triggered when the wireless channel switches from idle to busy
CHANNEL_DOWN = Event(key='CHANNEL_DOWN', type=None) #:Triggered when the wireless channel switches from busy to idle
QUEUE_OUT_UP = Event(key='QUEUE_OUT_UP', type=None) #:Triggered when the frame is injected into the physical queue of the platform from the upper MAC
RX_END = Event(key='RX_END', type=None) #:Triggered when that receiver operation is finished
RX_PLCP_END = Event(key='RX_PLCP_END', type=None) #:Triggered at the end of PLCP reception
RX_ERROR_BAD_PLCP = Event(key='RX_ERROR_BAD_PLCP', type=None) #:Triggered at the occurrence of a receiver error due a PLCP check failure
RX_ERROR_BAD_CRC = Event(key='RX_ERROR_BAD_CRC', type=None) #:Triggered at the occurrence of a receiver error due a CRC failure
TDMA_SLOT_START = Event(key='TDMA_SLOT_START', type=None) #:Triggered at the beginning of a TDMA slot
TDMA_SLOT_END = Event(key='TDMA_SLOT_END', type=None) #:Triggered at the end of a TDMA slot