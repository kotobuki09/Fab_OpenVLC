__author__ = 'domenico'

# Generic API to control the lower layers, i.e. key-value configuration.

class execution_engine_t:
    """
    The information elements used by the UPI_R interface are organized into data structures, which provide information
    on a specific execution environment. This class representing the data structure that contains the execution
    environment information.
    """

    execution_engine_id = ""
    """ Identifier of the execution environment """

    execution_engine_name = ""
    """ Name of the execution environment """

    supported_platform = ""
    """ Platform of the execution environment """

    execution_engine_pointer = ""
    """ Path of the execution environment """

class radio_program_t:
    """
    The information elements used by the UPI_R interface are organized into data structures, which provide information
    on a specific radio program. This class representing the data structure that contains the radio program
    information.
    """

    radio_prg_id = ""
    """ Identifier of the radio program """

    radio_prg_name = ""
    """ Name of the radio program """

    supported_platform = ""
    """ Platform of the radio program """

    radio_prg_pointer = ""
    """ Path of the radio program """

class radio_platform_t(object):
	"""
	The information elements used by the UPI_R interface are organized into data structures, which provide information
	on the platform type of each interface,over the radio interface.
	This class representing the data structure information of a radio interface, it contains an identifier and the
	platform type.
	"""
	def __init__(self,platform_id="",platform_type=""):
		self.platform_id = platform_id
		""" interface identifier or interface name """
		self.platform_type = platform_type
		""" platform interface """
		pass

	def __str__(self):
		return ""+self.platform_id+","+self.platform_type

class radio_info_t:
    """
    The information elements used by the UPI_R interface are organized into data structures, which provide information
    on radio capabilities (monitor_t, param_t) of each interface (RadioPlatform_t) on the available radio programs (radio_prg_t),
    over the radio interface.
    This class representing the radio capabilities of a given network card RadioPlatform_t in terms of measurement list,
    parameters lists, execution environment list and radio program list.

    """
    platform_info = None
    """ Interface information structured such as RadioPlatform_t object """

    monitor_list = []
    """ The list of supported measurements """

    param_list = []
    """ The list of supported parameters """

    radio_program_list = None
    """ The list of supported radio program """

    execution_engine_list = None
    """ The list of supported execution environment """


 # class UPI_R(object):
 #    __metaclass__ = abc.ABCMeta
class UPI_R():

    """
    PHY PARAMETERS
    """
    # get/set rf channel on a wireless network interface
    IEEE80211_CHANNEL = "IEEE80211_CHANNEL"
    # get MAC address of network interface card
    NETWORK_INTERFACE_HW_ADDRESS = "NETWORK_INTERFACE_HW_ADDRESS"
    # measure the transmit rate of generated 802.11 broadcast traffic at full rate
    IEEE80211_L2_BCAST_TRANSMIT_RATE = "IEEE80211_L2_BCAST_TRANSMIT_RATE"
    # send out 802.11 broadcast link probes
    IEEE80211_L2_GEN_LINK_PROBING = "IEEE80211_L2_GEN_LINK_PROBING"
    # receive 802.11 broadcast link probes

    IEEE80211_L2_SNIFF_LINK_PROBING = "IEEE80211_L2_SNIFF_LINK_PROBING"
    """ To Receive 802.11 broadcast link probes """

    IEEE80211_CONNECT_TO_AP = "IEEE80211_CONNECT_TO_AP"
    """ Connect to ap """

    IEEE80211_AP_CHANNEL = "IEEE80211_AP_CHANNEL"
    """ IEEE 802.11 PHY channel """

    IEEE80211_CHANNEL = "IEEE80211_CHANNEL"
    """ IEEE 802.11 PHY channel """

    IEEE80211_MCS = "IEEE80211_MCS"
    """ IEEE 802.11 Modulation and Coding Scheme (MCS) index value """

    IEEE80211_CCA = "IEEE80211_CCA"
    """ IEEE 802.11 Clear channel assessment (CCA) threshold """

    TX_POWER = "TX_POWER"
    """ Transmission power in dBm """

    TX_ANTENNA = "TX_ANTENNA"
    """ Antenna number selected for transmission """

    RX_ANTENNA = "RX_ANTENNA"
    """ Antenna number selected for reception """

    MAC_ADDR_SYNCHRONIZATION_AP = "MAC_ADDR_SYNCHRONIZATION_AP"
    """ To set the Access Point MAC address used for synchronizing the TSF timer """
    """
    END PHY PARAMETERS
    """

    """
    TDMA RADIO PROGRAM PARAMETERS
    """
    TDMA_SUPER_FRAME_SIZE = "TDMA_SUPER_FRAME_SIZE"
    """ Duration of a periodic TDMA frame """

    TDMA_NUMBER_OF_SYNC_SLOT = "TDMA_NUMBER_OF_SYNC_SLOT"
    """ Number of temporal slots included in a TDMA frame """

    TDMA_ALLOCATED_SLOT = "TDMA_ALLOCATED_SLOT"
    """ Slot number allocated to the NIC"""

    TDMA_ALLOCATED_MASK_SLOT = "TDMA_ALLOCATED_MASK_SLOT"
    """ Mask Slot number allocated to the NIC"""

    TDMA_MAC_PRIORITY_CLASS = "TDMA_MAC_PRIORITY_CLASS"
    """ Service class QUEUE associated to the TDMA radio program """
    """
    END TDMA RADIO PROGRAM PARAMETERS
    """

    """
    CSMA RADIO PROGRAM PARAMETERS
    """
    CSMA_CW = "CSMA_CW"
    """ Current value of the Contention Window used by the CSMA radio program"""

    CSMA_CW_MIN = "CSMA_CW_MIN"
    """ Minimum value of the Contention Window used by the CSMA radio program"""

    CSMA_CW_MAX = "CSMA_CW_MAX"
    """ Maximum value of the Contention Window used by the CSMA radio program"""

    CSMA_TIMESLOT = "CSMA_TIMESLOT"
    """ Duration of the backoff slot used by the CSMA radio program"""

    CSMA_MAC_PRIORITY_CLASS = "CSMA_MAC_PRIORITY_CLASS"
    """ Service class QUEUE c associated to the CSMA radio program """

    CSMA_BACKOFF_VALUE = "CSMA_BACKOFF_VALUE"
    """ Current backoff value used by the CSMA radio program"""
    """
    END CSMA RADIO PROGRAM PARAMETERS
    """

    """
    RADIO MEASURAMENT
    """
    NUM_TX = "NUM_TX"
    """ Total number of transmitted frames measured since the interface has been started"""

    NUM_TX_UNIT = "samples"
    """ Unit of measurement of NUM_TX """

    NUM_TX_DATA_FRAME = "NUM_TX_DATA_FRAME"
    """ Total number of transmitted frames measured since the interface has been started"""

    NUM_RX_ACK_RAMATCH = "NUM_RX_ACK_RAMATCH"
    """ Total receive ack frame with receive address match measured since the interface has been started"""

    NUM_RX_ACK = "NUM_RX_ACK"
    """ Total receive ack frame measured since the interface has been started"""

    NUM_TX_DATA_FRAME_UNIT = "samples"
    """ Unit of measurement of NUM_TX """

    NUM_TX_SUCCESS = "NUM_TX_SUCCESS"
    """ Total number of successfully transmitted frame measured since the interface has been started """

    NUM_TX_SUCCESS_UNIT = "samples"
    """ Unit of measurement of NUM_TX_SUCCESS """

    NUM_RX = "NUM_RX"
    """ Total number of received frames since the interface has been started """

    NUM_RX_UNIT = "samples"
    """ Unit of measurement of NUM_RX """

    NUM_RX_SUCCESS = "NUM_RX_SUCCESS"
    """ Total number of successfully received frames since the interface has been started """

    NUM_RX_SUCCESS_UNIT = "samples"
    """ Unit of measurement of NUM_RX_SUCCESS """

    NUM_RX_MATCH = "NUM_RX_MATCH"
    """ Total number of received frames addressed to the node since the interface has been started.
    This measurement traces the number of received frame in which the receiver address field matches with the
    network interface card MAC address """

    NUM_RX_MATCH_UNIT = "samples"
    """ Unit of measurement of NUM_RX_MATCH """

    NUM_FREEZING_COUNT = "NUM_FREEZING_COUNT"
    """ Total number of backoff freezes since the interface has been started """

    NUM_FREEZING_COUNT_UNIT = "samples"
    """ Unit of measurement of NUM_FREEZING_COUNT """

    BUSY_TYME = "BUSY_TIME"
    """ Time interval in which the transceiver has been active (including reception, transmission and carrier sense).
    The unit of measurement is microseconds since the interface has been started, the register size is 32bit
    (cycle on 4294 sec)"""

    BUSY_TYME_UNIT = "us"
    """ Unit of measurement of BUSY_TIME """

    TX_ACTIVITY = "TX_ACTIVITY"
    """ Time interval in which the transceiver has been involved in transmission.
    The unit of measurement is microseconds since the interface has been started, the register size is 32bit
    (cycle on 4294 sec)"""

    TX_ACTIVITY_UNIT = "us"
    """ Unit of measurement of TX_ACTIVITY """

    TSF = "TSF"
    """ The Time Synchronization Function (TSF), i.e. the timer that all stations in the same Basic Service Set (BSS) use
    for the synchronization """

    TSF_UNIT = "us"
    """ Unit of measurement of TSF """

    REGISTER_1 = "REGISTER_1"
    REGISTER_2 = "REGISTER_2"

    COUNT_SLOT = "COUNT_SLOT"
    "number or current slot, incremental from the interface started"

    PACKET_TO_TRANSMIT = "PACKET_TO_TRANSMIT"
    "8 bit register that give information about last 8 time slot, any bit in register get information about the presence of packet in queue for the correspondent time slot"

    MY_TRANSMISSION = "MY_TRANSMISSION"
    "8 bit register that give information about last 8 time slot, any bit in register get information about of attempt transmission in the correspondent time slot"

    SUCCES_TRANSMISSION = "SUCCES_TRANSMISSION"
    "8 bit register that give information about last 8 time slot, any bit in register get information about the success of transmission in the correspondent time slot"

    OTHER_TRANSMISSION = "OTHER_TRANSMISSION"
    "8 bit register that give information about last 8 time slot, any bit in register get information about other transmission in the correspondent time slot"

    BAD_RECEPTION = "BAD_RECEPTION"
    "8 bit register that give information about last 8 time slot, any bit in register get information about the presence of a bad receiption in the correspondent time slot"

    BUSY_SLOT = "BUSY_SLOT"
    "8 bit register that give information about last 8 time slot, any bit in register get information about the busy in the correspondent time slot"

