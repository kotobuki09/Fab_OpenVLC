import logging
import random
import pickle
import os
import inspect
import subprocess
import zmq
import time
import platform
import csv
import shutil

import wishful_module_wifi
import wishful_upis as upis

from agent_modules.wifi_wmp.wmp_structure import execution_engine_t
from agent_modules.wifi_wmp.wmp_structure import radio_platform_t
from agent_modules.wifi_wmp.wmp_structure import radio_info_t
from agent_modules.wifi_wmp.wmp_structure import radio_program_t
from agent_modules.wifi_wmp.wmp_structure import UPI_R
from agent_modules.wifi_wmp.adaptation_module.libb43 import *

import wishful_framework as wishful_module
from wishful_framework.classes import exceptions
#import wishful_framework.upi_arg_classes.edca as edca #<----!!!!! Important to include it here; otherwise cannot be pickled!!!!
#import wishful_framework.upi_arg_classes.flow_id as FlowId


__author__ = "Domenico Garlisi"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gomenico.garlisi@cnit.it"

# Used by local controller for communication with mac processor
LOCAL_MAC_PROCESSOR_CTRL_PORT = 1217



""" Store the current radio program information for WMP """
class memory_slot_info_t:

    radio_program_name = ''
    """ The radio program name"""

    radio_program_pointer = ''
    """ The radio program pointer """



""" Store the current radio program information for WMP """
class WMP_info_t:
    platform_info = "WMP"
    """ platform specification"""

    interface_id = "wlan0"

    memory_slot_number = 2
    """ number of memory slot for the platform """

    memory_slot_active = 1
    """ the memory slot active """

    memory_slot_list = []



@wishful_module.build_module
class WmpModule(wishful_module_wifi.WifiModule):
    def __init__(self, executionEngine="factory", iface="wlan0"):
        super(WmpModule, self).__init__()
        self.log = logging.getLogger('WmpModule')
        self.channel = 6
        self.power = 15
        self.modulation_rate = 24
        self.wlan_interface = iface

        self.SUCCESS = 0
        self.PARTIAL_SUCCESS = 1
        self.FAILURE = 2

        #global b43_phy
        self.b43_phy = None
        global NIC_list
        global radio_info
        self.WMP_status = WMP_info_t()
        self.WMP_status.memory_slot_list = [memory_slot_info_t() for i in range(self.WMP_status.memory_slot_number)]
        self.executionEngine = executionEngine

        self.relative_path = "../"


    @wishful_module.on_start()
    def start_WMP_module(self):
        self.log.info("Start WMP agent".format())

        current_path=os.getcwd()
        current_list_path=current_path.split('/')
        ii=0
        path_position=len(current_list_path)-1
        for ii in range(1, 20):
            if current_list_path[path_position][0:23] == "wishful-github-manifest":
                self.relative_path = self.relative_path  + current_list_path[path_position] + "/"
                break
            self.relative_path = self.relative_path + "../"
            path_position -= 1


        args = {'execution_engine' : [self.relative_path + 'agent_modules/wifi_wmp/execution_engine/' + self.executionEngine] }
        rvalue = self.install_execution_engine(args)
        self.log.debug('Ret value of blocking call is %s' % str(rvalue))

        args = {'interface' : self.wlan_interface, 'operation' : ['module'] }
        rvalue = self.init_test(args)
        self.log.debug('Ret value of blocking call is %s' % str(rvalue))


    """
    UPI_M implementation
    """

    #@wishful_module.bind_function(upis.wmp.radio.install_execution_engine)
    def install_execution_engine(self, myargs):
        execution_engine_value = None
        module_value = None
        execution_engine_value = myargs['execution_engine']
        execution_engine_value = execution_engine_value[0]

        #self.log.warning('install_execution_engine(): %s' % (str(execution_engine_value)))

        dst = ""
        module_dst = "/lib/modules/3.13.11-ckt19-custom/kernel/drivers/net/wireless/b43/"
        microcode_dst = "/lib/firmware/b43/"

        #self.log.debug('copy file on : %s' % key[ii])
        if execution_engine_value != None:
            dst = microcode_dst
            path_1 = execution_engine_value + '/ucode5.fw'
            path_2 = execution_engine_value + '/b0g0initvals5.fw'
            path_3 = execution_engine_value + '/b0g0bsinitvals5.fw'
            try:
                #self.log.debug('copy file path_1 : %s on dest : %s' % (path_1, dst) )
                shutil.copy(path_1, dst)
                shutil.copy(path_2, dst)
                shutil.copy(path_3, dst)
            except Exception as e:
                self.log.debug('Unable to copy file. %s' % e)
                return False

        if module_value != None:
            dst = module_dst
            path_1 = module_value + '/b43.ko'
            try:
                shutil.copy(path_1, dst)
            except Exception as e:
                self.log.debug('Unable to copy file. %s' % e)
                return False

        return True

    #@wishful_module.bind_function(upis.wmp.radio.init_test)
    def init_test(self, myargs):
        import subprocess
        self.log.warning('init_test(): %s' % str(myargs) )
        key = myargs['operation']
        interface = myargs['interface']
        try:
            for ii in range(0,len(key)):
                self.log.debug('key: %s' % str(key[ii]) )

                if key[ii] == "module":
                    #check if hostapd running
                    cmd_str = 'ps aux | grep hostapd | wc -l'
                    cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)
                    cmd_output = cmd_output.decode('ascii')
                    flow_info_lines = cmd_output.rstrip().split('\n')
                    if (int(flow_info_lines[0])>2):
                        #kill hostapd
                        cmd_str = 'sudo killall -9 hostapd'
                        cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)

                    #check if b43 module running
                    cmd_str = 'lsmod | grep b43 | wc -l'
                    cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)
                    cmd_output = cmd_output.decode('ascii')
                    flow_info_lines = cmd_output.rstrip().split('\n')
                    #self.log.debug('cmd_output 1 : %s' % flow_info_lines[0])
                    time.sleep(0.5)
                    if (int(flow_info_lines[0])>0):
                        #kill b43 module
                        cmd_str = 'rmmod b43'
                        cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)
                        cmd_output = cmd_output.decode('ascii')
                        #self.log.debug('cmd_output 2 : %s' % cmd_output)
                        time.sleep(0.5)

                    #insert b43 module
                    cmd_str = 'modprobe b43 qos=0 && sleep 0.5 && ifconfig ' + self.wlan_interface + ' 192.168.0.3'
                    cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)
                    #self.log.debug('cmd_output 3: %s' % cmd_output)

                if key[ii] == "monitor":
                    value_1 = myargs['channel']
                    cmd_str = self.relative_path  + 'agent_modules/wifi_wmp/network_script/setup_monitor.sh ' + value_1[ii]
                    subprocess.call(cmd_str, shell=True)
                    self.log.info('------------------------------ end STA monitor ------------------------')

        except B43Exception as e:
            self.log.debug('initTest raised an exception:  %s' % e)

        return True


    """
    UPI_R implementation
    """
    @wishful_module.bind_function(upis.radio.get_radio_platforms)
    def get_radio_platforms(self):
        self.log.warning('get_radio_platforms()')

        cmd_str = 'lsmod | grep b43 | wc -l'
        cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)
        time.sleep(1)
        if (int(cmd_output)==0):
            cmd_str = 'modprobe b43 qos=0'
            cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)
        time.sleep(1)
        #self.log.debug('output %s', command)

        command = self.relative_path + 'agent_modules/wifi_wmp/adaptation_module/src/bytecode-manager --get-interface-name'
        nl_output = ""

        try:
            nl_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        except: # catch *all* exceptions
            self.log.debug('Error on subprocess call %s', nl_output)

        nl_output = nl_output.decode('ascii')
        self.log.debug('command output %s', str(nl_output))
        flow_info_lines = nl_output.rstrip().split('\n')
        NIC_list = [radio_platform_t() for i in range(len(flow_info_lines))]

        for ii in range(len(flow_info_lines)):
            tmp = flow_info_lines[ii]
            items = tmp.split(",")
            NIC_list[ii].platform_info = items[0]
            NIC_list[ii].platform = items[1]

        NIC_list_string = [NIC_list[ii].platform_info, NIC_list[ii].platform]
        self.log.debug('NIC_list_string %s', str(NIC_list_string))
        return NIC_list_string

    @wishful_module.bind_function(upis.radio.get_radio_info)
    def get_radio_info(self, interface):
        radio_id = interface
        platform = "WMP"
        self.log.warning('get_radio_info(): %s : %s' % ( str(radio_id), str(platform) ) )

        radio_info = radio_info_t()
        radio_info.platform_info = radio_platform_t()

        radio_info.platform_info.platform_id = radio_id
        radio_info.platform_info.platform = platform

        #get available engines
        exec_engine_current_list_name = []
        exec_engine_current_list_pointer = []
        with open( self.relative_path + 'agent_modules/wifi_wmp/wmp_repository/execution_engine_repository.csv') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                #filter for WMP platform
                #self.log.debug(" %s " %  str(row['execution_engine_name']) )
                exec_engine_current_list_name.append(row['execution_engine_name'])
                exec_engine_current_list_pointer.append(row['execution_engine_pointer'])
            radio_info.execution_engine_list = [execution_engine_t() for i in range(len(exec_engine_current_list_name))]
            for ii in range(len(exec_engine_current_list_name)):
                radio_info.execution_engine_list[ii].execution_engine_name = exec_engine_current_list_name[ii]
                radio_info.execution_engine_list[ii].execution_engine_pointer = exec_engine_current_list_pointer[ii]
                #self.log.debug(" execution engine %s " %  radio_info.execution_engine_list[ii].execution_engine_pointer )


        #get available repository
        radio_prg_current_list_name = []
        radio_prg_current_list_pointer = []
        with open( self.relative_path  + 'agent_modules/wifi_wmp/wmp_repository/radio_program_repository.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                #filter for WMP platform
                #self.log.debug(" radio prg name : %s " %  str(row['radio_prg_name']) )
                radio_prg_current_list_name.append(row['radio_prg_name'])
                radio_prg_current_list_pointer.append(row['radio_prg_pointer'])
            radio_info.radio_program_list = [radio_program_t() for i in range(len(radio_prg_current_list_name))]
            for ii in range(len(radio_prg_current_list_name)):
                radio_info.radio_program_list[ii].radio_prg_name = radio_prg_current_list_name[ii]
                radio_info.radio_program_list[ii].radio_prg_pointer = radio_prg_current_list_pointer[ii]

        b43 = B43(self.b43_phy)
        radio_info.monitor_list = b43.monitor_list
        radio_info.param_list = b43.param_list
        ret_lst = []
        ret_lst = {'radio_info' : [radio_info.platform_info.platform_id, radio_info.platform_info.platform],
                   'event_list' : [''], 'monitor_list' : [b43.monitor_list], 'param_list' : [b43.param_list],
                   'radio_prg_list_name' : [radio_prg_current_list_name], 'radio_prg_list_pointer' : [radio_prg_current_list_pointer],
                   'exec_engine_list_name' : [exec_engine_current_list_name], 'exec_engine_list_pointer' : [exec_engine_current_list_pointer],
                   }
        #execution_engine_list = None
        self.log.debug("ret_lst %s " %  ret_lst )
        return ret_lst

    @wishful_module.bind_function(upis.radio.get_parameters)
    def get_parameters(self, myargs):
        self.log.warning('get_parameter(): %s' % str(myargs))
        ret_lst = []

        # if myargs.has_key('cmd'):
        #     cmd = myargs['cmd']
        #     if cmd == UPI_R.NETWORK_INTERFACE_HW_ADDRESS:
        #         return self.getHwAddr(myargs)
        #     elif cmd == UPI_R.IEEE80211_L2_BCAST_TRANSMIT_RATE:
        #         return self.genBacklogged80211L2BcastTraffic(myargs)
        #     elif cmd == UPI_R.IEEE80211_L2_GEN_LINK_PROBING:
        #         return self.gen80211L2LinkProbing(myargs)
        #     elif cmd == UPI_R.IEEE80211_L2_SNIFF_LINK_PROBING:
        #         return self.sniff80211L2LinkProbing(myargs)
        #     else:
        #         self.log.error('getParameterLowerLayer(): unknown parameter with command (cmd)')

        if 'parameters' in myargs:
            key_parameter = myargs['parameters']
            for ii in range(0,len(key_parameter)):
                if key_parameter[ii] == UPI_R.CSMA_CW:
                    ret_lst.append( self.readRadioProgramParameters(UPI_R.CSMA_CW) )
                elif key_parameter[ii] == UPI_R.CSMA_CW_MIN:
                    ret_lst.append( self.readRadioProgramParameters(UPI_R.CSMA_CW_MIN) )
                elif key_parameter[ii] == UPI_R.CSMA_CW_MAX:
                    ret_lst.append( self.readRadioProgramParameters(UPI_R.CSMA_CW_MAX) )
                elif key_parameter[ii] == UPI_R.TDMA_SUPER_FRAME_SIZE:
                    ret_lst.append( self.readRadioProgramParameters(UPI_R.TDMA_SUPER_FRAME_SIZE) )
                elif key_parameter[ii] == UPI_R.TDMA_NUMBER_OF_SYNC_SLOT:
                    ret_lst.append( self.readRadioProgramParameters(UPI_R.TDMA_NUMBER_OF_SYNC_SLOT) )
                elif key_parameter[ii] == UPI_R.TDMA_ALLOCATED_SLOT:
                    ret_lst.append( self.readRadioProgramParameters(UPI_R.TDMA_ALLOCATED_SLOT) )
                else:
                    self.log.error('get_parameters(): unknown parameter with parameters (parameters)')

        self.log.debug('get_parameters() exit : %s' % str(ret_lst))
        return ret_lst

    # def defineEvent(self, myargs):
    #     raise ValueError('Not yet implemented')
    #

    @wishful_module.bind_function(upis.radio.set_parameters)
    def set_parameters(self, myargs):
        self.log.warning('set_parameter: %s' % (str(myargs)))
        ret_lst = []

        #manage TDMA slot parameter
        super_frame_size = 0
        number_of_sync_slot = 0
        if UPI_R.TDMA_SUPER_FRAME_SIZE in myargs:
            super_frame_size = myargs[UPI_R.TDMA_SUPER_FRAME_SIZE]
        if UPI_R.TDMA_NUMBER_OF_SYNC_SLOT in myargs:
            number_of_sync_slot = myargs[UPI_R.TDMA_NUMBER_OF_SYNC_SLOT]
        if super_frame_size != 0 or number_of_sync_slot !=0 :
            if super_frame_size != 0 and number_of_sync_slot != 0 :
                self.log.debug('setting superframe and number_of_sync_slot slot')
                slot_duration = super_frame_size /  number_of_sync_slot
                ret_lst.append( self.setRadioProgramParameters(UPI_R.TDMA_SUPER_FRAME_SIZE, slot_duration ) )
                ret_lst.append( self.setRadioProgramParameters(UPI_R.TDMA_NUMBER_OF_SYNC_SLOT, number_of_sync_slot ) )
            if super_frame_size == 0 and number_of_sync_slot != 0 :
                self.log.debug('setting number_of_sync_slot slot')
                slot_duration = self.readRadioProgramParameters(UPI_R.TDMA_SUPER_FRAME_SIZE)
                old_number_of_allocated_slot = self.readRadioProgramParameters(UPI_R.TDMA_NUMBER_OF_SYNC_SLOT)
                slot_duration = (slot_duration * old_number_of_allocated_slot) /  number_of_sync_slot
                ret_lst.append( self.setRadioProgramParameters(UPI_R.TDMA_SUPER_FRAME_SIZE, slot_duration ) )
                ret_lst.append( self.setRadioProgramParameters(UPI_R.TDMA_NUMBER_OF_SYNC_SLOT, number_of_sync_slot ) )
            if super_frame_size != 0 and number_of_sync_slot == 0 :
                self.log.debug('setting superframe')
                number_of_sync_slot = self.readRadioProgramParameters(UPI_R.TDMA_NUMBER_OF_SYNC_SLOT)
                slot_duration = super_frame_size /  number_of_sync_slot
                ret_lst.append( self.setRadioProgramParameters(UPI_R.TDMA_SUPER_FRAME_SIZE, slot_duration ) )
            self.startBootStrapOperation()


        #manage other parameter
        # if  UPI_R.IEEE80211_CHANNEL in myargs:
        #     ret_lst.append( self.setRfChannel(myargs) )
        # if  UPI_R.IEEE80211_CONNECT_TO_AP in myargs:
        #     ret_lst.append( self.connectToAP(myargs) )
        if  UPI_R.CSMA_CW in myargs:
            ret_lst.append( self.setRadioProgramParameters(UPI_R.CSMA_CW, myargs[UPI_R.CSMA_CW]) )
        if  UPI_R.CSMA_CW_MIN in myargs:
            ret_lst.append( self.setRadioProgramParameters(UPI_R.CSMA_CW_MIN, myargs[UPI_R.CSMA_CW_MIN]) )
        if  UPI_R.CSMA_CW_MAX in myargs:
            ret_lst.append( self.setRadioProgramParameters(UPI_R.CSMA_CW_MAX, myargs[UPI_R.CSMA_CW_MAX]) )
        if  UPI_R.TDMA_ALLOCATED_SLOT in myargs:
            ret_lst.append( self.setRadioProgramParameters(UPI_R.TDMA_ALLOCATED_SLOT, myargs[UPI_R.TDMA_ALLOCATED_SLOT] ) )
        if  UPI_R.TDMA_ALLOCATED_MASK_SLOT in myargs:
            ret_lst.append( self.setRadioProgramParameters(UPI_R.TDMA_ALLOCATED_MASK_SLOT, myargs[UPI_R.TDMA_ALLOCATED_MASK_SLOT] ) )
        if  UPI_R.MAC_ADDR_SYNCHRONIZATION_AP in myargs:
                mac_address_end = myargs[UPI_R.MAC_ADDR_SYNCHRONIZATION_AP]
                self.log.debug('ADDRESS 1: %s' % mac_address_end)
                mac_address_end = mac_address_end.replace(':', '')
                self.log.debug('ADDRESS 2: %s' % mac_address_end)
                mac_address_end = mac_address_end[-2:] + mac_address_end[-4:-2]
                self.log.debug('ADDRESS 3: %s' % mac_address_end)
                int_mac_address_end = int(mac_address_end, 16)
                ret_lst.append( self.setRadioProgramParameters(UPI_R.MAC_ADDR_SYNCHRONIZATION_AP, int_mac_address_end ) )

        return ret_lst

    @wishful_module.bind_function(upis.radio.get_running_radio_program)
    def get_running_radio_program(self):
        self.log.warning('get_running_radio_program(): ')
        command = self.relative_path + 'agent_modules/wifi_wmp/adaptation_module/src/bytecode-manager -v'
        nl_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        nl_output = nl_output.decode('ascii')
        flow_info_lines = nl_output.rstrip().split('\n')
        items = flow_info_lines[1].split(" ")
        active_radio_program = items[4]
        self.log.debug('active_radio_program : %s' % str(active_radio_program))
        return active_radio_program

    """ we join this function with set active """
    # def inject(self,  interface, radioProgramName, param_key_value):
    #     import subprocess
    #     self.log.debug('inject(): %s ' %  str(param_key_value))
    #     radio_program_path = ''
    #     position = None
    #
    #     radio_program_path = param_key_value['PATH']
    #     position = param_key_value['POSITION']
    #
    #     if position == None :
    #         position = 1
    #
    #     command = self.relative_path + 'agent_modules/wifi_wmp/adaptation_module/src/bytecode-manager -l ' + position + ' -m ' + radio_program_path
    #     #self.log.debug('output %s ', command)
    #
    #     nl_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    #     self.log.debug('output %s ', nl_output)
    #
    #     flow_info_lines = nl_output.rstrip().split('\n')
    #     #items = flow_info_lines[1].split(" ")
    #     if flow_info_lines[5] == 'end load file' :
    #         self.log.debug('Radio program successfully injected!')
    #         return True
    #     else :
    #         self.log.debug('Radio program inject error')
    #         return False

    @wishful_module.bind_function(upis.radio.activate_radio_program)
    def activate_radio_program(self,  myargs):
        position = None
        radio_program_path = ''
        radio_program_name = ''
        self.log.warning('activate_radio_program(): %s ' %  str(myargs))

        if 'position' in myargs:
            if (myargs['position'] == '1'):
                position = 1
            elif (myargs['position'] == '2'):
                position = 2
            else :
                return self.FAILURE

        if 'radio_program_name' in myargs:
            radio_program_name = myargs['radio_program_name']
        if 'path' in myargs:
            radio_program_path = myargs['path']

        #get the current radio program injected
        #injected_radio_program = getInjectedRadioProgram()

        #identification the operation
        # 1 = activation by position
        # 2 = activation by name
        # 3 = activation by position and name
        # 4 = injection + activation by position
        # 5 = injection + activation by name
        # 6 = injection + activation by position and name
        if radio_program_path == '' :
            if position == None and radio_program_name == '':
                return self.FAILURE

            elif position != None and radio_program_name == '':
                operation = 1

            elif position == None and radio_program_name != '':
                for i in range(self.WMP_status.memory_slot_number):
                    if self.WMP_status.memory_slot_list[i].radio_program_name == radio_program_name :
                        position = i+1

                if position == None :
                    return self.FAILURE
                else :
                    operation = 2

            else :
                operation = 3

        else :
            if position == None and radio_program_name == '':
                return self.FAILURE

            elif position != None and radio_program_name == '':
                operation = 4
                radio_program_name = "NO-NAME"

            elif position == None and radio_program_name != '':
                for i in range(self.WMP_status.memory_slot_number):
                    if self.WMP_status.memory_slot_list[i].radio_program_name == radio_program_name :
                        position = i+1

                    if position == None :
                        if self.WMP_status.memory_slot_active == 1 :
                            position = 2
                        else :
                            position = 1

                    operation = 5

            else:
                operation = 6

        """ radio program injection on WMP platform """
        #handled only if operation number is great of 3
        self.log.debug('operation : %d - radio_program_name = %s - position = %d - radio_program_path = %s' %  (operation, radio_program_name, position, radio_program_path) )
        if operation > 3 :
            command = self.relative_path + 'agent_modules/wifi_wmp/adaptation_module/src/bytecode-manager -l ' + str(position) + ' -m ' + self.relative_path + radio_program_path
            nl_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            nl_output = nl_output.decode('ascii')
            self.log.debug(' bytecode-manager command result : %s' % nl_output)
            flow_info_lines = nl_output.rstrip().split('\n')
            if not(flow_info_lines[5] == 'end load file') :
                return self.FAILURE
            else :
                self.WMP_status.memory_slot_list[(position-1)].radio_program_name = radio_program_name
                self.WMP_status.memory_slot_list[(position-1)].radio_program_pointer = radio_program_path

        """ radio program activation """
        command = self.relative_path + 'agent_modules/wifi_wmp/adaptation_module/src/bytecode-manager -a ' + str(position)
        nl_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        nl_output = nl_output.decode('ascii')
        self.log.debug(' bytecode-manager command result : %s' % nl_output)
        flow_info_lines = nl_output.rstrip().split('\n')
        if (position == 1 and flow_info_lines[0] == 'Active byte-code 1') or (position == 2 and flow_info_lines[0] == 'Active byte-code 2') :
            self.WMP_status.memory_slot_active = position
            return self.SUCCESS
        else :
            return self.FAILURE

    @wishful_module.bind_function(upis.radio.deactivate_radio_program)
    def deactivate_radio_program(self, myargs):
        """ radio program activation """
        radio_program_name = myargs['radio_program_name']
        command = self.relative_path + 'agent_modules/wifi_wmp/adaptation_module/src/bytecode-manager -d ' + radio_program_name
        nl_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        nl_output = nl_output.decode('ascii')
        flow_info_lines = nl_output.rstrip().split('\n')
        if flow_info_lines[0] == 'InActive byte-code 1' :
            return self.SUCCESS
        elif flow_info_lines[0] == 'InActive byte-code 2' :
            return self.SUCCESS
        else :
            return self.FAILURE


    #******
    #read
    #******
    def readRadioProgramParameters(self, offset_parameter=0):

        b43 = B43(self.b43_phy)
        val = 0
        val_2 = 0

        gpr_byte_code_value = b43.shmRead16(b43.B43_SHM_REGS, b43.BYTECODE_ADDR_OFFSET)
        active_slot=0
        if not (offset_parameter==UPI_R.CSMA_CW or offset_parameter==UPI_R.CSMA_CW_MIN or offset_parameter== UPI_R.CSMA_CW_MAX or offset_parameter == UPI_R.REGISTER_1 or offset_parameter == UPI_R.REGISTER_2):
            if gpr_byte_code_value == b43.PARAMETER_ADDR_OFFSET_BYTECODE_1 :
                active_slot = 1
            elif gpr_byte_code_value == b43.PARAMETER_ADDR_OFFSET_BYTECODE_2 :
                active_slot = 2
            else :
                self.log.error('readRadioProgramParameters(): no active slot')
                return val

        if offset_parameter == UPI_R.CSMA_CW:
            val = b43.shmRead16(b43.B43_SHM_REGS, b43.GPR_CUR_CONTENTION_WIN)
        elif offset_parameter == UPI_R.CSMA_CW_MIN:
            val = b43.shmRead16(b43.B43_SHM_REGS, b43.GPR_MIN_CONTENTION_WIN)
        elif offset_parameter == UPI_R.CSMA_CW_MAX:
            val = b43.shmRead16(b43.B43_SHM_REGS, b43.GPR_MAX_CONTENTION_WIN)
        elif offset_parameter == UPI_R.REGISTER_1:
            val = b43.shmRead16(b43.B43_SHM_REGS, b43.PROCEDURE_REGISTER_1)
        elif offset_parameter == UPI_R.REGISTER_2:
            val = b43.shmRead16(b43.B43_SHM_REGS, b43.PROCEDURE_REGISTER_2)
        elif offset_parameter == UPI_R.TDMA_SUPER_FRAME_SIZE :
            if active_slot == 1 :
                val = b43.shmRead16(b43.B43_SHM_SHARED, b43.SHM_SLOT_1_TDMA_SUPER_FRAME_SIZE)
                val_2 = b43.shmRead16(b43.B43_SHM_SHARED, b43.SHM_SLOT_1_TDMA_NUMBER_OF_SYNC_SLOT)
            else :
                val = b43.shmRead16(b43.B43_SHM_SHARED, b43.SHM_SLOT_2_TDMA_SUPER_FRAME_SIZE)
                val_2 = b43.shmRead16(b43.B43_SHM_SHARED, b43.SHM_SLOT_2_TDMA_NUMBER_OF_SYNC_SLOT)

            self.log.error('readRadioProgramParameters(): val %s : val_2 %s' % (str(val), str(val_2)))
            val = val * val_2
        elif offset_parameter == UPI_R.TDMA_NUMBER_OF_SYNC_SLOT :
            if active_slot == 1 :
                val = b43.shmRead16(b43.B43_SHM_SHARED, b43.SHM_SLOT_1_TDMA_NUMBER_OF_SYNC_SLOT)
            else :
                val = b43.shmRead16(b43.B43_SHM_SHARED, b43.SHM_SLOT_2_TDMA_NUMBER_OF_SYNC_SLOT)
        elif offset_parameter == UPI_R.TDMA_ALLOCATED_SLOT :
            if active_slot == 1 :
                val = b43.shmRead16(b43.B43_SHM_SHARED, b43.SHM_SLOT_1_TDMA_ALLOCATED_SLOT)
            else :
                val = b43.shmRead16(b43.B43_SHM_SHARED, b43.SHM_SLOT_2_TDMA_ALLOCATED_SLOT)
        else:
            self.log.error('readRadioProgramParameters(): unknown parameter')

        #self.log.debug('B43 control ret value %d' % val)
        return val

    #******
    #set
    #******
    def setRadioProgramParameters(self, offset_parameter=0, value=0):
        b43 = B43(self.b43_phy)
        write_share = False
        write_gpr = False

        value = int(value)
        self.log.debug('setRadioProgramParameters(): offset = %s - value = %s' % (str(offset_parameter), str(value)))
        gpr_byte_code_value = b43.shmRead16(b43.B43_SHM_REGS, b43.BYTECODE_ADDR_OFFSET);
        active_slot=0

        if  not (offset_parameter==UPI_R.CSMA_CW or offset_parameter==UPI_R.CSMA_CW_MIN or offset_parameter== UPI_R.CSMA_CW_MAX or offset_parameter == UPI_R.REGISTER_1 or offset_parameter == UPI_R.REGISTER_2 or offset_parameter == UPI_R.MAC_ADDR_SYNCHRONIZATION_AP):
            if gpr_byte_code_value == b43.PARAMETER_ADDR_OFFSET_BYTECODE_1 :
                active_slot = 1
                #self.log.debug('detected active slot 1')
            elif gpr_byte_code_value == b43.PARAMETER_ADDR_OFFSET_BYTECODE_2 :
                active_slot = 2
                #self.log.debug('detected active slot 2')
            else :
                self.log.error('readRadioProgramParameters(): no active slot')
                return False

        if offset_parameter == UPI_R.MAC_ADDR_SYNCHRONIZATION_AP:
            offset_parameter_gpr= b43.MAC_ADDR_SYNCHRONIZATION_AP_GPR
            write_gpr = True
        elif offset_parameter == UPI_R.CSMA_CW:
            offset_parameter_share= b43.SHM_EDCFQCUR + b43.SHM_EDCFQ_CWCUR
            offset_parameter_gpr= b43.GPR_CUR_CONTENTION_WIN
            write_share = True
            write_gpr = True
        elif offset_parameter == UPI_R.CSMA_CW_MIN:
            offset_parameter_share= b43.SHM_EDCFQCUR + b43.SHM_EDCFQ_CWMIN
            offset_parameter_gpr= b43.GPR_MIN_CONTENTION_WIN
            write_share = True
            write_gpr = True
        elif offset_parameter == UPI_R.CSMA_CW_MAX:
            offset_parameter_share= b43.SHM_EDCFQCUR + b43.SHM_EDCFQ_CWMAX
            offset_parameter_gpr= b43.GPR_MAX_CONTENTION_WIN
            write_share = True
            write_gpr = True
        elif offset_parameter == UPI_R.REGISTER_1:
            offset_parameter_gpr= b43.PROCEDURE_REGISTER_1
            write_gpr = True
        elif offset_parameter == UPI_R.REGISTER_2:
            offset_parameter_gpr= b43.PROCEDURE_REGISTER_2
            write_gpr = True
        elif offset_parameter == UPI_R.TDMA_SUPER_FRAME_SIZE :
            #self.log.debug('start : write super frame size %d' % value)
            if active_slot == 1 :
                b43.shmWrite16(b43.B43_SHM_SHARED, b43.SHM_SLOT_1_TDMA_SUPER_FRAME_SIZE, value)
                #self.log.debug('slot 1 : write super frame size %d' % value)
            else :
                b43.shmWrite16(b43.B43_SHM_SHARED, b43.SHM_SLOT_2_TDMA_SUPER_FRAME_SIZE, value)
                #self.log.debug('slot 2 : write super frame size %d' % value)
        elif offset_parameter == UPI_R.TDMA_NUMBER_OF_SYNC_SLOT:
            if active_slot == 1 :
                b43.shmWrite16(b43.B43_SHM_SHARED, b43.SHM_SLOT_1_TDMA_NUMBER_OF_SYNC_SLOT, value)
            else :
                b43.shmWrite16(b43.B43_SHM_SHARED, b43.SHM_SLOT_2_TDMA_NUMBER_OF_SYNC_SLOT, value)
        elif offset_parameter == UPI_R.TDMA_ALLOCATED_SLOT  :
            if active_slot == 1 :
                b43.shmWrite16(b43.B43_SHM_SHARED, b43.SHM_SLOT_1_TDMA_ALLOCATED_SLOT, value)
            else :
                b43.shmWrite16(b43.B43_SHM_SHARED, b43.SHM_SLOT_2_TDMA_ALLOCATED_SLOT, value)
        elif offset_parameter == UPI_R.TDMA_ALLOCATED_MASK_SLOT  :
            if active_slot == 1 :
                b43.shmWrite32(b43.B43_SHM_SHARED, b43.SHM_SLOT_1_TDMA_ALLOCATED_MASK_SLOT, value)
            else :
                b43.shmWrite32(b43.B43_SHM_SHARED, b43.SHM_SLOT_2_TDMA_ALLOCATED_MASK_SLOT, value)
        else :
            self.log.error('setRadioProgramParameters(): unknown parameter')
            return self.FAILURE

        if write_share :
            b43.shmWrite16(b43.B43_SHM_SHARED, offset_parameter_share, value)
        if write_gpr :
            b43.shmWrite16(b43.B43_SHM_REGS, offset_parameter_gpr, value)

        return self.SUCCESS

    @wishful_module.bind_function(upis.radio.get_measurements)
    def get_measurements(self, myargs):
        iw_command_monitor = False
        microcode_monitor = False
        key = myargs['measurements']
        interface = myargs['interface']
        self.log.debug('get_measurements(): %s len : %d' % (str(key), len(key)))
        ret_lst = []

        for ii in range(0,len(key)):
            if key[ii] == UPI_R.NUM_TX_SUCCESS:
                iw_command_monitor = True
            if key[ii] == UPI_R.NUM_TX:
                microcode_monitor = True
            if key[ii] == UPI_R.NUM_TX_DATA_FRAME:
                microcode_monitor = True
            if key[ii] == UPI_R.BUSY_TYME:
                microcode_monitor = True
            if key[ii] == UPI_R.NUM_FREEZING_COUNT:
                microcode_monitor = True
            if key[ii] == UPI_R.TX_ACTIVITY:
                microcode_monitor = True
            if key[ii] == UPI_R.NUM_RX:
                microcode_monitor = True
            if key[ii] == UPI_R.NUM_RX_SUCCESS:
                microcode_monitor = True
            if key[ii] == UPI_R.NUM_RX_MATCH:
                microcode_monitor = True
            if key[ii] == UPI_R.TSF:
                microcode_monitor = True
            if key[ii] == UPI_R.REGISTER_1:
                microcode_monitor = True
            if key[ii] == UPI_R.REGISTER_2:
                microcode_monitor = True
            if key[ii] == UPI_R.COUNT_SLOT:
                microcode_monitor = True
            if key[ii] == UPI_R.PACKET_TO_TRANSMIT:
                microcode_monitor = True
            if key[ii] == UPI_R.MY_TRANSMISSION:
                microcode_monitor = True
            if key[ii] == UPI_R.SUCCES_TRANSMISSION:
                microcode_monitor = True
            if key[ii] == UPI_R.OTHER_TRANSMISSION:
                microcode_monitor = True
            if key[ii] == UPI_R.BAD_RECEPTION:
                microcode_monitor = True
            if key[ii] == UPI_R.BUSY_SLOT:
                microcode_monitor = True

        if  microcode_monitor:
            b43 = B43(self.b43_phy)

        if  iw_command_monitor:
            cmd_str = 'iw dev ' + interface + ' station dump'
            #self.log.debug('cmd_str: %s' % cmd_str)
            cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)
            cmd_output = cmd_output.decode('ascii')
            #self.log.debug('cmd_output: %s' % cmd_output)
            # parse serialized data and create data structures
            flow_info_lines = cmd_output.rstrip().split('\n')
            #self.log.debug(' row number %d' % len(flow_info_lines))
            if len(flow_info_lines) < 3 :
                self.log.error('getMonitor(): iw command error')
                return False

            for ii in range(len(flow_info_lines)):
                tmp = flow_info_lines[ii]
                #self.log.debug('%d ) getMonitor(): %s' % (ii, tmp))
                items = tmp.split("\t")
                if ii == 3:
                    rx_packet = items[2]
                elif ii == 5:
                    tx_packet = items[2]
                elif ii == 6:
                    tx_retries = items[2]
                elif ii == 7:
                    tx_failed = items[2]
                else:
                    continue
            tx_packet_success = int(tx_packet)
            tx_packet = int(tx_packet) + int(tx_retries) + int(tx_failed)
            if tx_packet_success < 0 :
                tx_packet_success = 0

        for ii in range(0,len(key)):
            if key[ii] == UPI_R.TSF:
                while True :
                        v3 = b43.read16(b43.B43_MMIO_TSF_3)
                        v2 = b43.read16(b43.B43_MMIO_TSF_2)
                        v1 = b43.read16(b43.B43_MMIO_TSF_1)
                        v0 = b43.read16(b43.B43_MMIO_TSF_0)
                        test3 = b43.read16(b43.B43_MMIO_TSF_3)
                        test2 = b43.read16(b43.B43_MMIO_TSF_2)
                        test1 = b43.read16(b43.B43_MMIO_TSF_1)
                        if v3 == test3 and v2 == test2 and v1 == test1 :
                            break
                ret_lst.append( (v3 << 48) + (v2 << 32) + (v1 << 16) + v0 )
            if key[ii] == UPI_R.BUSY_TYME:
                ret_lst.append( b43.shmRead32(b43.B43_SHM_SHARED, b43.BUSY_TIME_CHANNEL) )
                #self.log.debug('getMonitor(): value 1 : %s ' % value_1)
            if key[ii] == UPI_R.NUM_FREEZING_COUNT:
                ret_lst.append( b43.shmRead16(b43.B43_SHM_SHARED, b43.NUM_FREEZING_COUNT) )
                #self.log.debug('getMonitor(): value 1 : %s ' % value_1)
            if key[ii] == UPI_R.TX_ACTIVITY:
                ret_lst.append( b43.shmRead32(b43.B43_SHM_SHARED, b43.TX_ACTIVITY) )
                #self.log.debug('getMonitor(): value 2 : %s ' % value_2)
            if key[ii] == UPI_R.NUM_RX:
                total_receive = b43.shmRead16(b43.B43_SHM_SHARED, b43.BAD_PLCP_COUNTER)             #trace failure
                total_receive += b43.shmRead16(b43.B43_SHM_SHARED, b43.INVALID_MACHEADER_COUNTER)   #trace failure
                total_receive += b43.shmRead16(b43.B43_SHM_SHARED, b43.BAD_FCS_COUNTER)             #trace failure
                total_receive += b43.shmRead16(b43.B43_SHM_SHARED, b43.RX_TOO_LONG_COUNTER)         #trace failure
                total_receive += b43.shmRead16(b43.B43_SHM_SHARED, b43.RX_TOO_SHORT_COUNTER)        #trace failure
                total_receive += b43.shmRead16(b43.B43_SHM_SHARED, b43.RX_CRS_GLITCH_COUNTER)       #trace failure
                total_receive += b43.shmRead16(b43.B43_SHM_SHARED, b43.GOOD_FCS_COUNTER)            #trace success
                ret_lst.append(total_receive)
                #self.log.debug('getMonitor(): value num_rx : %s ' % total_receive)
            if key[ii] == UPI_R.NUM_RX_SUCCESS:
                ret_lst.append(b43.shmRead16(b43.B43_SHM_SHARED, b43.GOOD_FCS_COUNTER))
                #value_3 = b43.shmRead32(b43.B43_SHM_SHARED, b43.GOOD_FCS_COUNTER)
                #self.log.debug('getMonitor(): value 2 : %s ' % value_3)
            if key[ii] == UPI_R.NUM_RX_MATCH:
                #ret_lst.append(b43.shmRead16(b43.B43_SHM_SHARED, b43.GOOD_FCS_MATCH_RA_COUNTER))
                ret_lst.append(b43.shmRead16(b43.B43_SHM_REGS, b43.GOOD_FCS_MATCH_RA_COUNTER))
                #ret_lst.append(rx_packet)
            if key[ii] == UPI_R.NUM_TX:
               ret_lst.append(b43.shmRead16(b43.B43_SHM_SHARED, b43.TX_COUNTER))
            #   ret_lst.append(tx_packet)
            if key[ii] == UPI_R.NUM_TX_DATA_FRAME:
                ret_lst.append(b43.shmRead16(b43.B43_SHM_REGS, b43.TX_DATA_FRAME_COUNTER))
            #    ret_lst.append(b43.shmRead16(b43.B43_SHM_SHARED, b43.TX_DATA_FRAME_COUNTER))
            if key[ii] == UPI_R.NUM_RX_ACK:
                ret_lst.append(b43.shmRead16(b43.B43_SHM_REGS, b43.RX_ACK_COUNTER))
            #    ret_lst.append(b43.shmRead16(b43.B43_SHM_SHARED, b43.RX_ACK_COUNTER))
            if key[ii] == UPI_R.NUM_RX_ACK_RAMATCH:
                ret_lst.append(b43.shmRead16(b43.B43_SHM_REGS, b43.RX_ACK_COUNTER_RAMATCH))
            if key[ii] == UPI_R.NUM_TX_SUCCESS:
                ret_lst.append(tx_packet_success)
            if key[ii] == UPI_R.REGISTER_1:
                ret_lst.append(b43.shmRead16(b43.B43_SHM_REGS, b43.PROCEDURE_REGISTER_1))
            if key[ii] == UPI_R.REGISTER_2:
                ret_lst.append(b43.shmRead16(b43.B43_SHM_REGS, b43.PROCEDURE_REGISTER_2))
            if key[ii] == UPI_R.COUNT_SLOT:
                ret_lst.append(b43.shmRead16(b43.B43_SHM_REGS, b43.COUNT_SLOT))
            if key[ii] == UPI_R.PACKET_TO_TRANSMIT:
               ret_lst.append(b43.shmRead16(b43.B43_SHM_SHARED, b43.PACKET_TO_TRANSMIT))
            if key[ii] == UPI_R.MY_TRANSMISSION:
               ret_lst.append(b43.shmRead16(b43.B43_SHM_SHARED, b43.MY_TRANSMISSION))
            if key[ii] == UPI_R.SUCCES_TRANSMISSION:
               ret_lst.append(b43.shmRead16(b43.B43_SHM_SHARED, b43.SUCCES_TRANSMISSION))
            if key[ii] == UPI_R.OTHER_TRANSMISSION:
               ret_lst.append(b43.shmRead16(b43.B43_SHM_SHARED, b43.OTHER_TRANSMISSION))
            if key[ii] == UPI_R.BAD_RECEPTION:
               ret_lst.append(b43.shmRead16(b43.B43_SHM_SHARED, b43.BAD_RECEPTION))
            if key[ii] == UPI_R.BUSY_SLOT:
               ret_lst.append(b43.shmRead16(b43.B43_SHM_SHARED, b43.BUSY_SLOT))


        self.log.debug('call result: %s' % ret_lst)
        return ret_lst


    @wishful_module.bind_function(upis.radio.get_measurements_periodic)
    def get_measurements_periodic(self, myargs, collect_period, report_period, num_iterations, report_callback):
        key = myargs['measurements']
        interface = myargs['interface']
        self.log.debug('get_measurements_periodic(): %s len : %d' % (str(key), len(key)))
        return self.get_measurements(myargs)



#
#
#
#     def getMonitorBounce(self, myargs):
#         import subprocess
#
#         iw_command_monitor = False
#         microcode_monitor = False
#
#         self.log.debug('getMonitorBounce(): %s len : %d' % (str(myargs), len(myargs)))
#         key = myargs['measurements']
#         slot_period = myargs['slot_period']
#         frame_period = myargs['frame_period']
#         interface = myargs['interface']
#         cumulative_reading = []
#         reading = []
#
#         for ii in range(0,len(key)):
#             if key[ii] == UPI_R.NUM_TX:
#                 iw_command_monitor = True
#             if key[ii] == UPI_R.NUM_TX_SUCCESS:
#                 iw_command_monitor = True
#             if key[ii] == UPI_RN.BUSY_TYME:
#                 microcode_monitor = True
#             if key[ii] == UPI_RN.NUM_FREEZING_COUNT:
#                 microcode_monitor = True
#             if key[ii] == UPI_RN.TX_ACTIVITY:
#                 microcode_monitor = True
#             if key[ii] == UPI_R.NUM_RX:
#                 microcode_monitor = True
#             if key[ii] == UPI_RN.NUM_RX_SUCCESS:
#                 microcode_monitor = True
#             if key[ii] == UPI_RN.NUM_RX_MATCH:
#                 microcode_monitor = True
#             if key[ii] == UPI_RN.TSF:
#                 microcode_monitor = True
#
#
#         if  microcode_monitor:
#             b43 = B43(b43_phy)
#
#         num_sampling_total = frame_period / slot_period
#         num_sampling = 0
#         while True :
#
#             if  iw_command_monitor:
#                 cmd_str = 'iw dev ' + interface + ' station dump'
#                 #self.log.debug('cmd_str: %s' % cmd_str)
#                 cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)
#                 #self.log.debug('cmd_output: %s' % cmd_output)
#                 # parse serialized data and create data structures
#                 flow_info_lines = cmd_output.rstrip().split('\n')
#                 #self.log.debug(' row number %d' % len(flow_info_lines))
#                 if len(flow_info_lines) < 3 :
#                     self.log.error('getMonitorBounce(): iw command error')
#                     return False
#
#                 for ii in range(len(flow_info_lines)):
#                     tmp = flow_info_lines[ii]
#                     #self.log.debug('%d ) getMonitor(): %s' % (ii, tmp))
#                     items = tmp.split("\t")
#                     if ii == 3:
#                         rx_packet = items[2]
#                     elif ii == 5:
#                         tx_packet = items[2]
#                     elif ii == 6:
#                         tx_retries = items[2]
#                     elif ii == 7:
#                         tx_failed = items[2]
#                     else:
#                         continue
#                 tx_packet_success = int(tx_packet)
#                 tx_packet = int(tx_packet) + int(tx_retries) + int(tx_failed)
#
#
#                 if tx_packet_success < 0 :
#                     tx_packet_success = 0
#
#             for ii in range(0,len(key)):
#                 if key[ii] == UPI_RN.TSF:
#                     while True :
#                             v3 = b43.read16(b43.B43_MMIO_TSF_3)
#                             v2 = b43.read16(b43.B43_MMIO_TSF_2)
#                             v1 = b43.read16(b43.B43_MMIO_TSF_1)
#                             v0 = b43.read16(b43.B43_MMIO_TSF_0)
#                             test3 = b43.read16(b43.B43_MMIO_TSF_3)
#                             test2 = b43.read16(b43.B43_MMIO_TSF_2)
#                             test1 = b43.read16(b43.B43_MMIO_TSF_1)
#                             if v3 == test3 and v2 == test2 and v1 == test1 :
#                                 break
#                     reading.append( ((v3 << 48) + (v2 << 32) + (v1 << 16) + v0) )
#                 if key[ii] == UPI_RN.BUSY_TYME:
#                     reading.append( b43.shmRead32(b43.B43_SHM_SHARED, b43.BUSY_TIME_CHANNEL) )
#                     #self.log.debug('getMonitorBounce: BUSY_TIME_CHANNEL : %s ' % reading)
#                 if key[ii] == UPI_RN.NUM_FREEZING_COUNT:
#                     reading.append( b43.shmRead16(b43.B43_SHM_SHARED, b43.NUM_FREEZING_COUNT) )
#                     #self.log.debug('getMonitorBounce: BUSY_TIME_CHANNEL : %s ' % reading)
#                 if key[ii] == UPI_RN.TX_ACTIVITY:
#                     reading.append( b43.shmRead32(b43.B43_SHM_SHARED, b43.TX_ACTIVITY_CHANNEL) )
#                     #self.log.debug('getMonitorBounce(): TX_ACTIVITY_CHANNEL : %s ' % reading)
#                 if key[ii] == UPI_RN.NUM_RX:
#                     total_receive = b43.shmRead16(b43.B43_SHM_SHARED, b43.BAD_PLCP_COUNTER)             #trace failure
#                     total_receive += b43.shmRead16(b43.B43_SHM_SHARED, b43.INVALID_MACHEADER_COUNTER)   #trace failure
#                     total_receive += b43.shmRead16(b43.B43_SHM_SHARED, b43.BAD_FCS_COUNTER)             #trace failure
#                     total_receive += b43.shmRead16(b43.B43_SHM_SHARED, b43.RX_TOO_LONG_COUNTER)         #trace failure
#                     total_receive += b43.shmRead16(b43.B43_SHM_SHARED, b43.RX_TOO_SHORT_COUNTER)        #trace failure
#                     total_receive += b43.shmRead16(b43.B43_SHM_SHARED, b43.RX_CRS_GLITCH_COUNTER)       #trace failure
#                     total_receive += b43.shmRead16(b43.B43_SHM_SHARED, b43.GOOD_FCS_COUNTER)            #trace success
#                     reading.append(total_receive)
#                     #self.log.debug('getMonitor(): value num_rx : %s ' % total_receive)
#                 if key[ii] == UPI_RN.NUM_RX_SUCCESS:
#                     reading.append(b43.shmRead16(b43.B43_SHM_SHARED, b43.GOOD_FCS_COUNTER))
#                     #value_3 = b43.shmRead32(b43.B43_SHM_SHARED, b43.GOOD_FCS_COUNTER)
#                     #self.log.debug('getMonitor(): value 2 : %s ' % value_3)
#                 if key[ii] == UPI_RN.NUM_RX_MATCH:
#                     reading.append(b43.shmRead16(b43.B43_SHM_SHARED, b43.GOOD_FCS_MATCH_RA_COUNTER))
#                     #value_3 = b43.shmRead32(b43.B43_SHM_SHARED, b43.GOOD_FCS_COUNTER)
#                     #self.log.debug('getMonitor(): value 2 : %s ' % value_3)
#                 if key[ii] == UPI_R.NUM_TX:
#                     reading.append( tx_packet )
#                 if key[ii] == UPI_R.NUM_TX_SUCCESS:
#                     reading.append( tx_packet_success )
#
#             cumulative_reading.append(reading)
#             reading = []
#             num_sampling += 1
#             if num_sampling == num_sampling_total :
#                 #self.log.debug('sampling num %d' % num_sampling)
#                 #self.log.debug('call result: %s' % str(cumulative_reading))
#                 return cumulative_reading
#             time.sleep(slot_period/1000000.0)
#
#         return cumulative_reading
#
    """
    Manage operation
    """
    def startBootStrapOperation(self):
        b43 = B43(self.b43_phy)
        gpr_byte_code_value = b43.shmRead16(b43.B43_SHM_REGS, b43.BYTECODE_ADDR_OFFSET)
        active_slot=0
        if gpr_byte_code_value == b43.PARAMETER_ADDR_OFFSET_BYTECODE_1 :
            active_slot = 1
        elif gpr_byte_code_value == b43.PARAMETER_ADDR_OFFSET_BYTECODE_2 :
            active_slot = 2
        else :
            self.log.error('startBootStrapOperation(): no active slot')
            return False

        if active_slot == 1 :
            b43.shmMaskSet16(b43.B43_SHM_REGS, b43.GPR_CONTROL, 0xF0FF, 0x0100)
        else :
            b43.shmMaskSet16(b43.B43_SHM_REGS, b43.GPR_CONTROL, 0xF0FF, 0x0200)
        while 1 :
            control_return = b43.shmRead16(b43.B43_SHM_REGS, b43.GPR_CONTROL)
            if (control_return & 0x0F00) == 0 :
                break

        return True
