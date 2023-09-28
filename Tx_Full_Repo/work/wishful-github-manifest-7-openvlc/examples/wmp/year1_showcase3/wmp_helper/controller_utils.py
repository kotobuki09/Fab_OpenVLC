#!/usr/bin/python
__author__ = 'Domenico Garlisi'
"""
EU project WISHFUL
"""
import types
from agent_modules.wifi_wmp.wmp_structure import UPI_R
from agent_modules.wifi_wmp.wmp_structure import execution_engine_t
from agent_modules.wifi_wmp.wmp_structure import radio_platform_t
from agent_modules.wifi_wmp.wmp_structure import radio_info_t
from agent_modules.wifi_wmp.wmp_structure import radio_program_t
import time

SUCCESS = 0
FAILURE = 2

def get_platform_information(node, log, controller):
    """ Gives the node platform information and instantiates a object of radio_info_t class related to the node passed by argument parameter
        Uses UPI_RN.getRadioPlatforms to check if WMP platform is available for node
        Uses UPI_RN.getRadioInfo to
             Extracts the ip address of the sender node and uses it to find appropriate object in WiFiNode list.
                 Stores the bunch of measurements in last_bunch_measurement WiFinode attribute.

    :param node: node from get platform supported and capabilities
    :param log: experiment logging module attribute
    :param global_mgr: experiment global manager attribute
    :return current_platform_info: return an object of class radio_info_t with all the node capabilities, false if the WMP
                              platform is not supported by node or an error occurred.
    """

    log.debug('***************** %s ***************' % get_platform_information.__name__)

    # all UPI_R functions are execute immediately
    exec_time = None

    #object inizialization
    current_radio_list = None
    current_radio_list = [radio_platform_t() for i in range(2)]

    current_platform_info = radio_info_t()
    current_platform_info.platform_info = radio_platform_t()
    current_platform_info.execution_engine_list = [execution_engine_t() for i in range(2) ]
    current_platform_info.radio_program_list = [ radio_program_t() for i in range(2) ]

    log.info("Platform information for %s " % str(node))
    wmp_platform_index = None
    current_radio_list_string = controller.nodes(node).radio.get_radio_platforms()

    log.debug("returned information %s " % str(current_radio_list_string))
    current_radio_list[0].platform_id =  current_radio_list_string[0]
    current_radio_list[0].platform_type =  current_radio_list_string[1]

    for ii in range(len(current_radio_list)):
        log.info('INTERFACE : %s : SUPPORTED PLATFORM : %s' % (current_radio_list[ii].platform_id, current_radio_list[ii].platform_type) )
        if current_radio_list[ii].platform_type == "WMP" :
            wmp_platform_index = ii
            break

    # Check if the Node NIC support the WMP platform
    if wmp_platform_index == None :
        log.debug('No WMP platform is supported')
        return False

    # Gets available NIC capabilities on boards that support WMP platform
    current_platform_info_str = controller.nodes(node).radio.get_radio_info(current_radio_list[wmp_platform_index].platform_id)
    log.debug('current_platform_str %s' % current_platform_info_str)
    #current_platform_info_str = current_platform_info_str

    current_platform_info.platform_info.platform_id = current_platform_info_str['radio_info'][0]
    current_platform_info.platform_info.platform_type = current_platform_info_str['radio_info'][1]

    log.debug("Radio capabilities for %s " % str(node))
    log.debug(" RADIO : %s - PLATFORM : %s" % (str(current_platform_info.platform_info.platform_id), str(current_platform_info.platform_info.platform_type) ) )

    # Gets monitor measurements and parameters supported
    current_platform_info.monitor_list = current_platform_info_str['monitor_list']
    current_platform_info.param_list = current_platform_info_str['param_list']

    # Gets execution environment supported
    execution_engine_list_name = current_platform_info_str['exec_engine_list_name']
    execution_engine_list_name = execution_engine_list_name[0]
    execution_engine_list_pointer = current_platform_info_str['exec_engine_list_pointer']
    execution_engine_list_pointer = execution_engine_list_pointer[0]
    for ii in range( len(execution_engine_list_name) ) :
        current_platform_info.execution_engine_list[ii].execution_engine_name = execution_engine_list_name[ii]
        current_platform_info.execution_engine_list[ii].execution_engine_pointer = execution_engine_list_pointer[ii]

    # Gets radio program supported
    radio_prg_list_name = current_platform_info_str['radio_prg_list_name']
    radio_prg_list_name = radio_prg_list_name [0]
    radio_prg_list_pointer = current_platform_info_str['radio_prg_list_pointer']
    radio_prg_list_pointer = radio_prg_list_pointer[0]
    for ii in range(len(radio_prg_list_name)):
        current_platform_info.radio_program_list[ii].radio_prg_name = radio_prg_list_name[ii]
        current_platform_info.radio_program_list[ii].radio_prg_pointer = radio_prg_list_pointer[ii]

    return current_platform_info


def active_CSMA_radio_program(node, log, global_mgr, current_platform_info):
    """ Active CSMA radio program to the node passed by argument parameter.
        To enable a radio program on WMP platform we need two different action, inject the radio program and activate it.

    :param node: Node or Nodes list in which active CSMA radio program
    :param log: experiment logging module attribute
    :param global_mgr: experiment global manager attribute
    :param current_platform_info: the radio capabilities of the NIC in Node
    :return result: result of activation (True = successful, False = failure)
    """
    log.debug('***************** %s ***************' % active_CSMA_radio_program.__name__)

    radio_program_pointer_CSMA = ""
    position = ""

    # Find CSMA radio program pointer in current_platform_info capability list
    for ii in range(len(current_platform_info.radio_program_list)):
        if current_platform_info.radio_program_list[ii].radio_prg_name == "CSMA" :
            radio_program_pointer_CSMA = current_platform_info.radio_program_list[ii].radio_prg_pointer
            #force the radio memory slot position in which store the radio program description
            #the WMP platform on broadcom vard has only two memory slot
            position = '2'

    if radio_program_pointer_CSMA == "" :
        log.debug("CSMA radio program not found in node capabilities list")
        return False

    # Active CSMA radio program
    UPIargs = {'position' : position, 'radio_program_name' : 'CSMA', 'path' : radio_program_pointer_CSMA, 'interface' : 'wlan0' }
    rvalue = controller.nodes(node).radio.activate_radio_program(UPIargs)#     if rvalue == SUCCESS :
    if rvalue == SUCCESS:
        log.warning('Radio program activation successful')
    else :
        log.warning('Error in radio program activation')
        return False

    return True


def active_CSMA_radio_program_slot_1(node, log, controller):
    """ Active CSMA radio program to the node passed by argument parameter.
        To enable a radio program on WMP platform we need two different action, inject the radio program and activate it.

    :param node: Node or Nodes list in which active CSMA radio program
    :param log: experiment logging module attribute
    :param global_mgr: experiment global manager attribute
    :param current_platform_info: the radio capabilities of the NIC in Node
    :return result: result of activation (True = successful, False = failure)
    """
    log.debug('***************** %s ***************' % active_CSMA_radio_program.__name__)

    radio_program_pointer_CSMA = ""
    position = ""
    # # Find CSMA radio program pointer in current_platform_info capability list
    # for ii in range(len(current_platform_info.radio_program_list)):
    #     if current_platform_info.radio_program_list[ii].radio_prg_name == "CSMA" :
    #         radio_program_pointer_CSMA = current_platform_info.radio_program_list[ii].radio_prg_pointer
    #         #force the radio memory slot position in which store the radio program description
    #         #the WMP platform on broadcom vard has only two memory slot
    #         position = '2'
    #
    # if radio_program_pointer_CSMA == "" :
    #     log.debug("CSMA radio program not found in node capabilities list")
    #     return False
    position = '1'
    # Active CSMA radio program
    UPIargs = {'position' : position, 'interface' : 'wlan0' }
    rvalue = controller.nodes(node).radio.activate_radio_program(UPIargs)
    if rvalue == SUCCESS :
        log.warning('Radio program activation successful')
    else :
        log.warning('Error in radio program activation')
        return False
    return True

def active_TDMA_radio_program_slot_2(node, log, controller):
    """ Active TDMA radio program to the node passed by argument parameter.
        To enable a radio program on WMP platform we need two different action, inject the radio program and activate it.

    :param node: Node or Nodes list in which active CSMA radio program
    :param log: experiment logging module attribute
    :param global_mgr: experiment global manager attribute
    :param current_platform_info: the radio capabilities of the NIC in Node
    :return result: result of activation (True = successful, False = failure)
    """
    log.debug('***************** %s ***************' % active_TDMA_radio_program.__name__)
    position = '2'
    # # Active CSMA radio program
    UPIargs = {'position' : position, 'interface' : 'wlan0' }
    rvalue = controller.nodes(node).radio.activate_radio_program(UPIargs)
    if rvalue == SUCCESS :
        log.warning('Radio program activation successful')
    else :
        log.warning('Error in radio program activation')
        return False

    return True



def active_TDMA_radio_program(node, log, controller, current_platform_info):
    """ Active TDMA radio program to the node passed by argument parameter.
        To enable a radio program on WMP platform we need two different action, inject the radio program and activate it.

    :param node: Node or Nodes list in which active TDMA radio program
    :param log: experiment logging module attribute
    :param global_mgr: experiment global manager attribute
    :param current_platform_info: the radio capabilities of the NIC in Node
    :return result: Result of activation (True = successful, False = failure)
    """
    log.debug('***************** %s ***************' % active_TDMA_radio_program.__name__)

    radio_program_pointer_TDMA = ""
    position = ""

    # Find TDMA radio program pointer in current_platform_info capability list
    for ii in range(len(current_platform_info.radio_program_list)):
        if current_platform_info.radio_program_list[ii].radio_prg_name == "TDMA" :
            log.debug("we will active radio program (path) : %s", current_platform_info.radio_program_list[ii].radio_prg_pointer )
            radio_program_pointer_TDMA = current_platform_info.radio_program_list[ii].radio_prg_pointer
            #force the radio memory slot position in which store the radio program description
            #the WMP platform on broadcom card has only two memory slot
            position = '2'

    if radio_program_pointer_TDMA == "" :
        log.warning("TDMA radio program not found in node capabilities list")
        return False

    # Active TDMA radio program
    UPIargs = {'position' : position, 'radio_program_name' : 'TDMA', 'path' : radio_program_pointer_TDMA, 'interface' : 'wlan0' }
    rvalue = controller.nodes(node).radio.activate_radio_program(UPIargs)
    if rvalue == SUCCESS :
        log.warning('Radio program activation succesfull')
    else :
        log.warning('Error in radio program activation')
        return False

    return True

def set_TDMA_parameters(node, log, controller, tdma_params):
    """ Set TDMA radio program  parameters to the node passed by argument parameter.
        The TDMA radio program  has three parameter to enable the setting of superframe size, number of sync slot and
        allocated slot, this function set them together.

    :param node: Node or Nodes list in which set the parameters
    :param log: experiment logging module attribute
    :param global_mgr: experiment global manager attribute
    :param tdma_params: a dictionary data type (list of key: value) in which the key are TDMA_SUPER_FRAME_SIZE TDMA_NUMBER_OF_SYNC_SLOT TDMA_ALLOCATED_SLOT
    :return result: Result of setting (True = successful, False = failure)
    """

    # Set the TDMA parameter
    log.warning('TDMA parameters = %s' %(str(tdma_params)))
    UPIargs = { 'interface' : 'wlan0', UPI_R.TDMA_SUPER_FRAME_SIZE: tdma_params['TDMA_SUPER_FRAME_SIZE'], UPI_R.TDMA_NUMBER_OF_SYNC_SLOT : tdma_params['TDMA_NUMBER_OF_SYNC_SLOT'], UPI_R.TDMA_ALLOCATED_SLOT : tdma_params['TDMA_ALLOCATED_SLOT'] }
    rvalue = controller.nodes(node).radio.set_parameters(UPIargs)

    log.warning('The change parameter result is %s  (O for SUCCESS)' % str(rvalue))
    time.sleep(1)
    # Active new configuration
    UPIargs = {'radio_program_name' : 'TDMA' }
    rvalue = controller.nodes(node).radio.activate_radio_program(UPIargs)
    if rvalue == SUCCESS :
        log.warning('Radio program activation succesfull')
    else :
        log.debug('Error in radio program activation')
        return False

    return True
