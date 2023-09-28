__author__ = 'A. Zubow'

import abc

"""
EU project WISHFUL

The WISHFUL interface definitions - UPIs (UPI_R/UPI_N) for device control.

The north interface between Application and the Wishful controller framework.
"""

"""
The UPI_R - UPI for radio control at device level.
"""

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

class UPIError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

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

class UPI_R(object):
    __metaclass__ = abc.ABCMeta

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

    @abc.abstractmethod
    def getRadioPlatforms(self):
        """ Gets available NIC on board and type of supported platforms. The information elements used by the UPI_R
        interface, to manage parameters, measurements and radio program, are organized into data structures,
        which provide information on the platform type and radio capabilities.
        When executed, this function return information about available interfaces on node, the name or the identifier
        of the interface and the supported platform type.

        :return current_NIC_list: a list of pair value, the first value is the interface identifier and the second is the supported platforms.

        example:
            >> current_NIC_list = RadioPlatform_t()
            >> current_NIC_list_string = UPI_RN.getRadioPlatforms()
            >> current_NIC_list.platform_info =  current_NIC_list_string[0]
            >> current_NIC_list.platform =  current_NIC_list_string[1]
        """
        return

    @abc.abstractmethod
    def getRadioInfo(self, interface):
        """Gets the radio capabilities of a given network card RadioPlatform_t in terms of supported measurement and supported
        parameter and list of supported radio program. The information elements used by the UPI_R interface, to manage
        parameters, measurements and radio program, are organized into data structures, which provide information
        on the platform type and radio capabilities. When executed, this function return information about available
        radio capabilities (measurements and parameters) of each interface (RadioPlatform_t) on the available radio programs
        (radio_prg_t) available for transmissions over the radio interface.

        :param interface: network interfaces to use
        :return result: return a list in term of a dictionary data type (list of key: value). in which are present the key showed below:
            'radio_info' --> a list of pair value, the first value is the interface identifier and the second is the supported platforms.
            'monitor_list' --> a list of supported measurements between the attribute of the class UPI_R
            'param_list' --> a list of supported Parameters between the attribute of the class UPI_R
            'exec_engine_list_name' --> a list of supported execution environment name
            'exec_engine_list_pointer' --> a list of supported execution environment path
            'radio_prg_list_name'--> a list of supported radio program name
            'radio_prg_list_pointer' --> a list of supported radio program path

        example:
            >> interface = 'wlan0'\n
            >> current_platform_info = radio_info_t()\n
            >> param_key = {'platform' : 'wmp'}\n
            >> current_platform_info_str = UPI_RN.getRadioInfo(interface, param_key)\n
            >> current_platform_info.platform_info.platform_id = current_platform_info_str['radio_info'][0]\n
            >> current_platform_info.platform_info.platform = current_platform_info_str['radio_info'][1]\n
            >> current_platform_info.monitor_list = current_platform_info_str['monitor_list']\n
            >> current_platform_info.param_list = current_platform_info_str['param_list']\n
            >> current_platform_info.execution_engine_list_name = current_platform_info_str['exec_engine_list_name']\n
            >> current_platform_info.execution_engine_list_pointer = current_platform_info_str['exec_engine_list_pointer']\n
            >> current_platform_info.radio_program_list_name = current_platform_info_str['radio_prg_list_name']\n
            >> current_platform_info.radio_program_list_path = current_platform_info_str['radio_prg_list_pointer']\n
        """
        return

    @abc.abstractmethod
    def setParameterLowerLayer(self, myargs):
        """ The UPI_R interface is able to configure the radio behavior thanks to the abstraction of the hardware
        platform and radio programs in terms of Radio Capabilities. A subset of radio capabilities are the parameter.
        Parameters correspond to the configuration registers of the hardware platform and to the variables used in
        the radio programs. This function (re)set the value(s) of the Parameters Radio Capabilities specified in
        the dictionary argument. The list of available parameters is defined as attributes of the UPI_R class,
        you can use the UPI_RN.getRadioInfo function to find the platform supported parameters.

        :param myargs: list of parameters and values to set, in term of a dictionary data type (list of key: value) in which keys is the interface ('interface') to specify network interface to be uses and the desired UPI_R attribute, and value is the value to set. An example of argument dictionary data type is {UPI_RN.CSMA_CW : 15, UPI_RN.CSMA_CW_MIN : 15, UPI_RN.CSMA_CW_MAX : 15}.
        :return result: return 0 if the parameter setting call was successfully performed, 1 partial success, 2 error.

        :example:
            >> args = {'interface' : 'wlan0', UPI_RN.CSMA_CW : 15, UPI_RN.CSMA_CW_MIN : 15, UPI_RN.CSMA_CW_MAX : 15}\n
            >> result = UPI_RN.setParameterLowerLayer(args)\n
            >> print result\n
            [0, 0, 0]\n
        """
        return

    @abc.abstractmethod
    def getParameterLowerLayer(self, myargs):
        """ The UPI_R interface is able to configure the radio behavior thanks to the abstraction of the hardware
        platform and radio programs in terms of Radio Capabilities. A subset of radio capabilities are the parameters.
        Parameters correspond to the configuration registers of the hardware platform and to the variables used in the
        radio programs.
        This function get the value(s) of the Parameters Radio Capabilities specified in the dictionary argument.
        The available parameters are defined as attributes of the UPI_R clas, you can use the UPI_RN.getRadioInfo function
        to find the platform supported parameters.

        :param myargs: list of parameters, in term of a dictionary data type (list of key: value) in which:the key is 'parameters' and the value is a list of UPI_R attributes for parameters, the key in 'interface' specify network interface to be uses. An argument dictionary example is {'interface' : 'wlan0', 'PARAMETERS' : [UPI_RN.CSMA_CW, UPI_RN.CSMA_CW_MIN, UPI_RN.CSMA_CW_MAX]}.
        :return result: list of parameters and values, in term of a dictionary data type (list of key: value) in which the key is the UPI_R class attribute, and value is the current setting of the attribute. An example of argument dictionary data type is {UPI_RN.CSMA_CW : 15, UPI_RN.CSMA_CW_MIN : 15, UPI_RN.CSMA_CW_MAX : 15}.

        :example:
            >> args = {'interface' : 'wlan0', 'parameters' : [UPI_RN.CSMA_CW] }\n
            >> result = UPI_RN.getParameterLowerLayer(args)\n
            >> print result\n
            {UPI_RN.CSMA_CW : 15}\n
        """
        return

    @abc.abstractmethod
    def getMonitor(self, myargs):
        """ The UPI_R interface is able to get the radio measurements thanks to the abstraction of the hardware
        platform and radio programs in terms of Radio Capabilities. A subset of radio capabilities are the low-level
        measurements. The low-level measurements are continuously monitored by the hardware platform and by the
        radio programs. The measurement capabilities can be used to get information and statistics about the state of
        the physical links or the internal state of the node.
        This function get the value(s) of the Measurements Radio Capabilities specified in the dictionary
        argument. The list of available measurements are defined as attribute of the UPI_R class, you can use the
        UPI_RN.getRadioInfo function to find the platform supported measurements.

        :param myargs: list of parameters, in term of a dictionary data type (list of key: value) in which: the key is 'measurements' and the value is a list of UPI_R attributes for measurements, the key in 'interface' specify network interface to be uses. An example of argument dictionary is {"measurements" : [UPI_RN.NUM_FREEZING_COUNT, UPI_RN.TX_ACTIVITY]}.
        :return result: list of parameters and values, in term of a dictionary data type (list of key: value) in which the key are the UPI_R attributes for measurements, and value is the reading of the measurement. An example of argument dictionary data type is {UPI_RN.NUM_FREEZING_COUNT : 150, UPI_RN.TX_ACTIVITY : 45670}.

        :example:
            >> args = {'interface' : 'wlan0', 'measurements' : [UPI_RN.NUM_FREEZING_COUNT] }\n
            >> result = UPI_RN.getMonitor(args)\n
            >> print result\n
            {UPI_RN.NUM_FREEZING_COUNT : 150}\n
        """
        return

    @abc.abstractmethod
    def getMonitorBounce(self, myargs):
        """ The UPI_R interface is able to get the radio measurements thanks to the abstraction of the hardware
        platform and radio programs in terms of Radio Capabilities. A subset of radio capabilities are the low-level
        measurements.The low-level measurements are continuously monitored by the hardware platform and by the
        radio programs. The measurement capabilities can be used to get information and statistics about the state of
        the physical links or the internal state of the node.
        This function works similarly to  getMonitor, it gets the value(s) of the Measurements Radio Capabilities
        specified in the dictionary argument, but in cycling mode.
        The function gets the measurements every SLOT_PERIOD and stores them on node memory. Every FRAME_PERIOD all
        measurements are reported to the controller, and this operation is performed a number of times specified by
        ITERATION. A callback function is used to receive the measurements results. The list of available measurements
        are defined as attribute of the UPI_R class, you can use the UPI_RN.getRadioInfo function to find the platform
        supported measurements.

        :param myargs: list of parameters, in term of a dictionary data type (list of key: value) in which: The key 'interface' specify the network interface to be used. The key 'measurements' is used to give the list of UPI_R attributes for measurements. The key 'slot_period' is used to define the time between two consecutive measurement readings, in microsecond. The key 'frame_period' is used to define the time between two consecutive reports to the controller, in microseconds. The key 'iterator' is used to define how many times the measurements have to be performed.
        :return result: list of parameters and values, in term of a dictionary data type (list of key: value) in which the key are the UPI_R attributes for measurements, and value is the measurement reading. An example of argument dictionary data type  is {UPI_RN.TX_ACTIVITY : 45670}.

        :example:
            >> args = {'interface' : 'wlan0', 'measurements': [UPI_RN.BUSY_TIME, UPI_RN.TX_ACTIVITY], 'slot_period': 500000,\n
            'frame_period': 2000000, 'iterator': 60}\n
            >> result = UPI_RN.getMonitorBounce(args)\n
            >> print result\n
            {UPI_RN.BUSY_TIME : 1505, UPI_RN.TX_ACTIVITY: 45670}\n
        """
        return

    @abc.abstractmethod
    def setActive(self, myargs):
        """ This function activates the passed radio program, one the platform. When executed, this function stops the
        current radio program and enables the execution of the radio program specified in the parameter
        radioProgramName. Two additional parameters can be used, one of these is required.The path of the radio program
        description is required. The optionally parameter specify the index, in order to associate an index to the radio
        program.

        :param myargs: a dictionary data type (key: value) where the keys are: The key 'interface' specify the network interface to use. The key 'radio_program_name'specify the name of radio program. The key 'path' in which the value specify the path of radio program description, and 'position' in which the value specify the radio program index associated.
        :return result:  return 0 if the parameter setting call was successfully performed, 1 partial success, 2 error.

        :example:
            >> args = {'interface' : 'wlan0', 'radio_program_name' : 'CSMA', 'path': './radio_program/csma.txt'} \n
            >> result = UPI_RN.setActive(args) \n
            >> print result
            0
        """
        return

    @abc.abstractmethod
    def setInactive(self, myargs):
        """ When executed, this function stops the radio program specified in the parameter radio_program_name.

        :param myargs: a dictionary data type (key: value) where the keys are: The key "interface" specify the network interface to use and the key 'radio_program_name' in which the value specify the name of radio program,
        :return result:  return 0 if the parameter setting call was successfully performed, 1 partial success, 2 error.

        :example:
            >> args = {'interface' : 'wlan0', 'radio_program_name' : 'CSMA'} \n
            >> result = UPI_RN.setInactive(args) \n
            >> print result \n
            0 \n
        """
        return

    @abc.abstractmethod
    def getActive(self, myargs):
        """ Each radio program is associated with a name and an index. When executed, this function return the index of the radio program active.

        :param myargs: a dictionary data type (key: value) where the keys are: The key "interface" specify the network interface to use.
        :return result: the index of the active radio program.

        :example:
            >> args = {'interface' : 'wlan0'} \n
            >> result = UPI_RN.getActive(args) \n
            >> print result \n
            2 \n
        """
        return

    @abc.abstractmethod
    def setEdcaParameters(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def getEdcaParameters(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def setPerFlowTxPower(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def cleanPerFlowTxPowerList(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def getPerFlowTxPowerList(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def genBacklogged80211L2BcastTraffic(self, param_key):
        """
        Sends as fast as possible L2 broadcast traffic. Note: all transmitted packets are identical.
        @return: the achieved transmit frame rate
        """

    @abc.abstractmethod
    def getHwAddr(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def setRfChannel(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def getAvgSigPowerOfAssociatedSTAs(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def transmitDisassociationRequestToSTA(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def sendCSABeaconToSTA(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def performActiveSpectralScanning(self, param_key):
        """
        Performs on-demand spectrum scanning on the given channels. The results is a matrix where the rows are
        freq, startfreq, noise, rssi, data, datasquaresum, highlight, signal
        """
        return

    @abc.abstractmethod
    def startContinousSignal(self, param_key):
        """
        Generates a continous signal
        """
        return

    @abc.abstractmethod
    def stopContinousSignal(self, param_key):
        """
        Generates a continous signal
        """
        return
"""
The UPI_N - UPI for network control at device level, i.e. upper MAC and higher layers of the network protocol stack
"""
class UPI_N(object):
    __metaclass__ = abc.ABCMeta

    """
        Low-level API
        Generic functions for configuration/monitoring
    """

    """
        Supported parameters
    """

    # get IP address of a network interface
    IFACE_IP_ADDR = "IFACE_IP_ADDR"

    @abc.abstractmethod
    def setParameterHigherLayer(self, param_key_value):
        """Set the parameter on higher layers of protocol stack (higher MAC and above)
        :param param_key_value: key and value of this parameter
        """
        return

    @abc.abstractmethod
    def getParameterHigherLayer(self, param_key):
        """Get the parameter on higher layers of protocol stack (higher MAC and above)
        :param param_key: the parameter identified by this key.
        :return the parameter value
        """
        return

    """
        High-level API
        Custom functions for configuration/monitoring. Note, they are not always available on each platform.
    """

    @abc.abstractmethod
    def startIperfServer(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def startIperfClient(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def startPing(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def setProfile(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def updateProfile(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def removeProfile(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def setPerLinkProfile(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def updatePerLinkProfile(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def removePerLinkProfile(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def installEgressScheduler(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def removeEgressScheduler(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def clearIpTables(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def getIpTable(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def setMarking(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def delMarking(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def setTos(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def delTos(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def installApplication(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def getInactivityTimeOfAssociatedSTAs(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def getInfoOfAssociatedSTAs(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def setARPEntry(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def removeSTAFromAPBlacklist(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def addSTAtoAPBlacklist(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def registerNewSTAInAP(self, param_key):
        """
        Func Desc
        """
        return

    @abc.abstractmethod
    def changeRouting(self, param_key):
        """
        Func Desc
        """
        return


class UPI_RN(UPI_R, UPI_N):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def stopFunc(self):
        """Helper to stop execution of local controller
        """
        return

    @abc.abstractmethod
    def msgFromController(self):
        """Helper to stop execution of local controller
        """
        return

    #@abc.abstractmethod
    #def getMsgFromController(self):
    #    """Helper to stop execution of local controller
    #    """
    #    return
