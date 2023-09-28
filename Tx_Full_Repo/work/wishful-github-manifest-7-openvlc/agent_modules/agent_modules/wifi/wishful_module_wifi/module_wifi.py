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
import fcntl, socket, struct
import netifaces as ni
from scapy.all import *
from datetime import date, datetime
import json

import wishful_upis as upis
import wishful_upis.meta_radio as radio
import wishful_framework as wishful_module
from wishful_framework.classes import exceptions

__author__ = "Piotr Gawlowicz, Mikolaj Chwalisz, Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, chwalisz, zubow}@tkn.tu-berlin.de"

@wishful_module.build_module
class WifiModule(wishful_module.AgentModule):
    def __init__(self):
        super(WifiModule, self).__init__()
        self.log = logging.getLogger('wifi_module.main')
        self.interface = "wlan0"
        self.wlan_interface = "wlan0"
        self.phy = "phy0"
        self.channel = 1
        self.power = 1
        self.rts_threshold = 'off'
        self.modulation_rate = 1


    @wishful_module.bind_function(upis.radio.get_parameters)
    def get_parameters(self, myargs):
        self.log.debug('get_parameter(): %s' % str(myargs))
        ret_lst = {}

        if 'parameters' in myargs:
            key_parameter = myargs['parameters']
            survey_enable = False
            for ii in range(0,len(key_parameter)):
                if key_parameter[ii] == radio.BUSY_TIME.key or key_parameter[ii] == radio.EXT_BUSY_TIME.key or key_parameter[ii] == radio.TX_ACTIVITY.key or key_parameter[ii] == radio.RX_ACTIVITY.key:
                    survey_enable = True
                    break
            if survey_enable:
                exec_file = str(os.path.join(self.get_platform_path_iw())) + '/iw'
                cmd_string = str(exec_file) + " dev " + self.wlan_interface + " surveyfreq dump"
                #{"NOISE":-91,"TIME":308148,"BUSY_TIME":83831,"EXT_BUSY_TIME":47539,"RX_ACTIVITY":47539,"TX_ACTIVITY":1475}
                try:
                    [rcode, sout, serr] = self.run_command(cmd_string)
                    survey_result=json.loads(sout)
                except Exception as e:
                    fname = inspect.currentframe().f_code.co_name
                    self.log.fatal("An error occurred in %s: %s survey_enable error" % (fname, e))
                    raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))

            statistic_enable = False
            for ii in range(0,len(key_parameter)):
                if key_parameter[ii] == radio.NUM_TX_RTS.key or key_parameter[ii] == radio.NUM_TX_SUCCESS.key or key_parameter[ii] == radio.NUM_ACK_FAILURE.key or \
                        key_parameter[ii] == radio.NUM_TX_MULTICAST_FRAME.key or key_parameter[ii] == radio.NUM_RTS_FAILURE_COUNT.key or key_parameter[ii] == radio.NUM_RTS_SUCCESS_COUNT.key:
                    statistic_enable = True
                    break
            if statistic_enable:
                exec_file =  str(os.path.join(self.get_platform_path_iw())) + '/ieee_stats.sh '
                cmd_string = "bash " + str(exec_file) + self.phy
                try:
                    #{"busy_time" : 25, "dot11ACKFailureCount" : 0, "dot11FailedCount" : 306, "dot11FCSErrorCount" : 3972, "dot11FrameDuplicateCount" : 0, "dot11MulticastReceivedFrameCount" : 11933, "dot11MulticastTransmittedFrameCount" : 33774, "dot11MultipleRetryCount" : 0, "dot11ReceivedFragmentCount" : 21945, "dot11RetryCount" : 0, "dot11RTSFailureCount" : 0, "dot11RTSSuccessCount" : 0, "dot11TransmittedFragmentCount" : 33774, "dot11TransmittedFrameCount" : 33774, "rx_expand_skb_head_defrag" : 0, "rx_handlers_drop" : 0, "rx_handlers_drop_defrag" : 0, "rx_handlers_drop_nullfunc" : 0, "rx_handlers_drop_short" : 0, "rx_handlers_fragments" : 0, "rx_handlers_queued" : 21945, "tx_expand_skb_head" : 0, "tx_expand_skb_head_cloned" : 0, "tx_handlers_drop" : 0, "tx_handlers_drop_not_assoc" : 0, "tx_handlers_drop_unauth_port" : 0, "tx_handlers_drop_wep" : 0, "tx_handlers_queued" : 0, "tx_status_drop" : 0 }                try:
                    [rcode, sout, serr] = self.run_command(cmd_string)
                    statistic_result=json.loads(sout)
                except Exception as e:
                    fname = inspect.currentframe().f_code.co_name
                    self.log.fatal("An error occurred in %s: %s statistic_enable error" % (fname, e))
                    raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))

            ath_statistic_enable = False
            for ii in range(0,len(key_parameter)):
                if key_parameter[ii] == radio.NUM_TX.key:
                    ath_statistic_enable = True
                    break
            if ath_statistic_enable:
                cmd_string = "sudo cat /sys/kernel/debug/ieee80211/" + self.phy + "/ath9k/xmit | grep TX-Pkts"
                try:
                    #['TX-Pkts-All:', '361665', '0', '0', '30209']
                    [rcode, sout, serr] = self.run_command(cmd_string)
                    ath_statistic_result=sout.split('\n')
                except Exception as e:
                    fname = inspect.currentframe().f_code.co_name
                    self.log.fatal("An error occurred in %s: %s ath_statistic_enable error" % (fname, e))
                    raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))

            for ii in range(0,len(key_parameter)):
                if key_parameter[ii] == radio.CSMA_CW_MAX.key:
                    pass
                elif key_parameter[ii] == radio.CSMA_CW_MIN.key:
                    pass
                elif key_parameter[ii] == radio.CSMA_CW.key:
                    pass
                elif key_parameter[ii] == radio.BUSY_TIME.key:
                    ret_lst[radio.BUSY_TIME.key] = survey_result['BUSY_TIME']
                elif key_parameter[ii] == radio.EXT_BUSY_TIME.key:
                    ret_lst[radio.EXT_BUSY_TIME.key] = survey_result['EXT_BUSY_TIME']
                elif key_parameter[ii] == radio.TX_ACTIVITY.key:
                    ret_lst[radio.TX_ACTIVITY.key]=survey_result['TX_ACTIVITY']
                elif key_parameter[ii] == radio.RX_ACTIVITY.key:
                    ret_lst[radio.RX_ACTIVITY.key]=survey_result['RX_ACTIVITY']
                elif key_parameter[ii] == radio.NUM_TX_RTS.key:
                    ret_lst[radio.NUM_TX_RTS.key] = statistic_result['dot11RTSSuccessCount']
                elif key_parameter[ii] == radio.NUM_TX_SUCCESS.key:
                    ret_lst[radio.NUM_TX_SUCCESS.key] = statistic_result['dot11TransmittedFragmentCount']
                elif key_parameter[ii] == radio.NUM_ACK_FAILURE.key:
                    ret_lst[radio.NUM_ACK_FAILURE.key] = statistic_result['dot11ACKFailureCount']
                elif key_parameter[ii] == radio.NUM_TX_MULTICAST_FRAME.key:
                    ret_lst[radio.NUM_TX_MULTICAST_FRAME.key] = statistic_result['dot11MulticastTransmittedFrameCount']
                elif key_parameter[ii] == radio.NUM_RTS_SUCCESS_COUNT.key:
                    ret_lst[radio.NUM_RTS_SUCCESS_COUNT.key] = statistic_result['dot11RTSSuccessCount']
                elif key_parameter[ii] == radio.NUM_RTS_FAILURE_COUNT.key:
                    ret_lst[radio.NUM_RTS_FAILURE_COUNT.key] = statistic_result['dot11RTSFailureCount']
                elif key_parameter[ii] == radio.NUM_TX.key:
                    result_dict = ath_statistic_result[0].split()
                    ret_lst[radio.NUM_TX.key] = int(result_dict[1]) + int(result_dict[4])
                else:
                    self.log.info('get_parameters(): unknown parameter with parameters (parameters)')

        self.log.debug('get_parameters() exit : %s' % str(ret_lst))
        return ret_lst

    @wishful_module.bind_function(upis.radio.set_parameters)
    def set_parameters(self, myargs):
        self.log.warning('set_parameter: %s' % (str(myargs)))
        ret_lst = []

        # if  UPI_R.CSMA_CW in myargs:
        #     ret_lst.append( self.setRadioProgramParameters(UPI_R.CSMA_CW, myargs[UPI_R.CSMA_CW]) )
        # if  UPI_R.CSMA_CW_MIN in myargs:
        #     ret_lst.append( self.setRadioProgramParameters(UPI_R.CSMA_CW_MIN, myargs[UPI_R.CSMA_CW_MIN]) )
        # if  UPI_R.CSMA_CW_MAX in myargs:
        #     ret_lst.append( self.setRadioProgramParameters(UPI_R.CSMA_CW_MAX, myargs[UPI_R.CSMA_CW_MAX]) )
        # if  UPI_R.TDMA_ALLOCATED_SLOT in myargs:
        #     ret_lst.append( self.setRadioProgramParameters(UPI_R.TDMA_ALLOCATED_SLOT, myargs[UPI_R.TDMA_ALLOCATED_SLOT] ) )
        # if  UPI_R.TDMA_ALLOCATED_MASK_SLOT in myargs:
        #     ret_lst.append( self.setRadioProgramParameters(UPI_R.TDMA_ALLOCATED_MASK_SLOT, myargs[UPI_R.TDMA_ALLOCATED_MASK_SLOT] ) )
        # if  UPI_R.MAC_ADDR_SYNCHRONIZATION_AP in myargs:
        #         mac_address_end = myargs[UPI_R.MAC_ADDR_SYNCHRONIZATION_AP]
        #         self.log.debug('ADDRESS 1: %s' % mac_address_end)
        #         mac_address_end = mac_address_end.replace(':', '')
        #         self.log.debug('ADDRESS 2: %s' % mac_address_end)
        #         mac_address_end = mac_address_end[-2:] + mac_address_end[-4:-2]
        #         self.log.debug('ADDRESS 3: %s' % mac_address_end)
        #         int_mac_address_end = int(mac_address_end, 16)
        #         ret_lst.append( self.setRadioProgramParameters(UPI_R.MAC_ADDR_SYNCHRONIZATION_AP, int_mac_address_end ) )

        return ret_lst


    @wishful_module.bind_function(upis.radio.set_rts_threshold)
    def set_rts_threshold(self, rts_threshold):
        self.log.info('setting set_rts_threshold(): %s->%s' % (str(self.wlan_interface), str(rts_threshold)))
        try:
            [rcode, sout, serr] = self.run_command('sudo iwconfig {0} rts {1}'.format(self.wlan_interface, rts_threshold))
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))
        self.power = rts_threshold


    @wishful_module.bind_function(upis.radio.set_tx_power)
    def set_tx_power(self, power_dBm):

        self.log.info('setting set_power(): %s->%s' % (str(self.wlan_interface), str(power_dBm)))

        cmd_str = 'iw dev ' + self.wlan_interface + ' set txpower fixed ' + str(power_dBm) + 'dbm'

        try:
            [rcode, sout, serr] = self.run_command(cmd_str)
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))

        self.power = power_dBm


    @wishful_module.bind_function(upis.radio.get_tx_power)
    def get_tx_power(self):
        self.log.debug("WIFI Module gets power of interface: {}".format(self.interface))
        return self.power


    @wishful_module.bind_function(upis.wifi.radio.set_channel)
    def set_channel(self, iface, channel):
        self.log.info('setting channel(): %s->%s' % (str(iface), str(channel)))
        cmd_str = 'sudo iwconfig ' + str(iface) + ' channel ' + str(channel)
        try:
            [rcode, sout, serr] = self.run_command(cmd_str)
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))

        return True


    @wishful_module.bind_function(upis.wifi.radio.get_channel)
    def get_channel(self):
        self.log.debug("WIFI Module gets channel of interface: {}".format(self.interface))
        return self.channel

    @wishful_module.bind_function(upis.radio.set_modulation_rate)
    def set_modulation_rate(self, rate_Mbps):

        self.log.info('setting modulation rate(): %s->%s' % (str(self.wlan_interface), str(rate_Mbps)))

        cmd_str = 'iwconfig ' + self.wlan_interface + ' rate ' + str(rate_Mbps) + 'M' + ' fixed'

        try:
            [rcode, sout, serr] = self.run_command(cmd_str)
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))

        self.modulation_rate = rate_Mbps

    """
    Monitor iface creation
    """
    @wishful_module.bind_function(upis.wifi.net.start_monitor)
    def start_monitor(self, driver, iface):
        self.log.info('start monitor setup')
        try:
                if driver=="ath9k":
                        iface_mon='mon0'
                        [rcode, sout, serr] = self.run_command('sudo iw dev {0} interface add {1} type monitor'.format(iface,iface_mon))
                        [rcode, sout, serr] = self.run_command('sudo ifconfig {0} up'.format(iface_mon))
                elif driver=="b43":
                        iface_mon='mon0'
                        [rcode, sout, serr] = self.run_command('sudo iw dev {0} interface add {1} type monitor'.format(iface,iface_mon))
                        [rcode, sout, serr] = self.run_command('sudo ifconfig {0} down'.format(iface))
                        [rcode, sout, serr] = self.run_command('sudo ifconfig {0} up'.format(iface_mon))
                else:
                        self.log.info('driver not supported yet')
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))
        self.log.info('setup monitor completed')


    """
    Ad-hoc node association
    """
    @wishful_module.bind_function(upis.wifi.net.start_adhoc)
    def start_adhoc(self, driver, iface,essid, freq,txpower, rate, ip_addr, rts='off', mac_address="aa:bb:cc:dd:ee:ff", skip_reload=False):
        self.log.info('start adhoc setup')
        try:
                if driver=="ath9k":
                        if skip_reload == False:
                                [rcode, sout, serr] = self.run_command('sudo rmmod ath9k ath9k_common ath9k_hw ath mac80211 cfg80211; sleep 1')
                                [rcode, sout, serr] = self.run_command('sudo modprobe ath9k; sleep 1')
                        else:
                                [rcode, sout, serr] = self.run_command('sudo iw {0} ibss leave'.format(iface))
                        [rcode, sout, serr] = self.run_command('sudo iwconfig {0} mode ad-hoc; sudo ifconfig {0} {5} up;sudo iwconfig {0} txpower {3} fixed; sudo iwconfig {0} rate {4}M fixed; sudo iw dev {0} ibss join {1} {2} fixed-freq {6} '.format(iface,essid,freq,txpower,rate,ip_addr,mac_address))
                        [rcode, sout, serr] = self.run_command('sudo iwconfig {0} rts {1}'.format(iface,rts))

                if driver=="b43":
                        if skip_reload == False:
                                [rcode, sout, serr] = self.run_command('sudo rmmod b43')
                                [rcode, sout, serr] = self.run_command('sudo modprobe b43 qos=0')
                        else:
                                [rcode, sout, serr] = self.run_command('sudo iw {0} ibss leave'.format(iface))
                        [rcode, sout, serr] = self.run_command('sudo iwconfig {0} mode ad-hoc; sudo ifconfig {0} {5} up;sudo iwconfig {0} txpower {3}; sudo iwconfig {0} rate {4}M fixed;sudo iw dev {0} ibss join {1} {2} fixed-freq {6}'.format(iface,essid,freq,txpower,rate,ip_addr,mac_address))

        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))

        self.log.info('adhoc setup completed')


    @wishful_module.bind_function(upis.wifi.net.set_hostapd_conf)
    def set_hostapd_conf(self, iface, file_path, channel, essid):
        self.log.debug("WIFI Module set hostapd configuratin file: {}".format(self.wlan_interface))

        from hostapdconf.parser import HostapdConf
        from hostapdconf import helpers as ha
        #read start configuration file
        conf = HostapdConf(file_path)
        #set wireless interface
        ha.set_iface(conf, iface)
        #set wireless channel
        if (channel > 0 and channel < 166):
            ha.set_channel(conf, channel)
        #set ESSID
        ha.set_ssid(conf, essid)
        #write new configuraiton
        conf.write()

        return True

    @wishful_module.bind_function(upis.wifi.net.start_hostapd)
    def start_hostapd(self, file_path):
        self.log.info('start hostapd()')

        cmd_str = 'sudo hostapd -B ' + str(file_path)
        try:
            [rcode, sout, serr] = self.run_command(cmd_str)
            #sp = subprocess.Popen(cmd_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            #out, err = sp.communicate()
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))

        self.log.info('start hostapd() completed')

        return True

    @wishful_module.bind_function(upis.wifi.net.stop_hostapd)
    def stop_hostapd(self):
        self.log.info('stop hostapd()')

        cmd_str = 'ps aux | grep hostapd | wc -l'
        try:
            [rcode, sout, serr] = self.run_command(cmd_str)
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))

        if (int(sout)>2):
            cmd_str = 'killall -9 hostapd'
            try:
                [rcode, sout, serr] = self.run_command(cmd_str)
            except Exception as e:
                fname = inspect.currentframe().f_code.co_name
                self.log.fatal("An error occurred in %s: %s" % (fname, e))
                raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))

        cmd_str = 'ifconfig wlan0 down; ifconfig wlan0 up'
        try:
            [rcode, sout, serr] = self.run_command(cmd_str)
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))

        self.log.info('stop hostapd() completed')

        return True

    @wishful_module.bind_function(upis.wifi.net.get_info_of_connected_devices)
    def get_info_of_connected_devices(self):
        '''
            Returns information about associated STAs for a node running in AP mode
            tbd: use Netlink API
        '''

        self.log.info("WIFI Module get info on associated clients on interface: {}".format(self.interface))

        try:
            [rcode, sout, serr] = self.run_command('iw dev ' + self.interface + ' station dump')

            # mac_addr -> stat_key -> list of (value, unit)
            res = {}
            sout_arr = sout.split("\n")

            for line in sout_arr:
                s = line.strip()
                if s == '':
                    continue
                if "Station" in s:
                    arr = s.split()
                    mac_addr = arr[1].strip()
                    res[mac_addr] = {}
                else:
                    arr = s.split(":")
                    key = arr[0].strip()
                    val = arr[1].strip()

                    arr2 = val.split()
                    val2 = arr2[0].strip()

                    if len(arr2) > 1:
                        unit = arr2[1].strip()
                    else:
                        unit = None

                    res[mac_addr][key] = (val2, unit)
            return res
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))


    @wishful_module.bind_function(upis.wifi.net.get_inactivity_time_of_connected_devices)
    def get_inactivity_time_of_connected_devices(self):
        return self.get_entry_of_connected_devices('inactive time')


    @wishful_module.bind_function(upis.wifi.net.get_avg_sigpower_of_connected_devices)
    def get_avg_sigpower_of_connected_devices(self):
        return self.get_entry_of_connected_devices('signal avg')


    @wishful_module.bind_function(upis.wifi.net.get_sigpower_of_connected_devices)
    def get_sigpower_of_connected_devices(self):
        return self.get_entry_of_connected_devices('signal')


    @wishful_module.bind_function(upis.wifi.net.get_tx_retries_of_connected_devices)
    def get_tx_retries_of_connected_devices(self):
        return self.get_entry_of_connected_devices('tx retries')


    @wishful_module.bind_function(upis.wifi.net.get_tx_packets_of_connected_devices)
    def get_tx_packets_of_connected_devices(self):
        return self.get_entry_of_connected_devices('tx packets')


    @wishful_module.bind_function(upis.wifi.net.get_tx_failed_of_connected_devices)
    def get_tx_failed_of_connected_devices(self):
        return self.get_entry_of_connected_devices('tx failed')


    @wishful_module.bind_function(upis.wifi.net.get_tx_bytes_of_connected_devices)
    def get_tx_bytes_of_connected_devices(self):
        return self.get_entry_of_connected_devices('tx bytes')


    @wishful_module.bind_function(upis.wifi.net.get_tx_bitrate_of_connected_devices)
    def get_tx_bitrate_of_connected_devices(self):
        return self.get_entry_of_connected_devices('tx bitrate')


    @wishful_module.bind_function(upis.wifi.net.get_rx_bytes_of_connected_devices)
    def get_rx_bytes_of_connected_devices(self):
        return self.get_entry_of_connected_devices('rx bytes')


    @wishful_module.bind_function(upis.wifi.net.get_rx_packets_of_connected_devices)
    def get_rx_packets_of_connected_devices(self):
        return self.get_entry_of_connected_devices('rx packets')


    @wishful_module.bind_function(upis.wifi.net.get_authorized_connected_device)
    def get_authorized_connected_device(self):
        return self.get_entry_of_connected_devices('authorized')


    @wishful_module.bind_function(upis.wifi.net.get_authenticated_connected_device)
    def get_authenticated_connected_device(self):
        return self.get_entry_of_connected_devices('authenticated')


    @wishful_module.bind_function(upis.wifi.net.get_used_preamble_connected_device)
    def get_used_preamble_connected_device(self):
        return self.get_entry_of_connected_devices('preamble')


    @wishful_module.bind_function(upis.wifi.net.get_mfp_connected_device)
    def get_mfp_connected_device(self):
        return self.get_entry_of_connected_devices('MFP')


    @wishful_module.bind_function(upis.wifi.net.get_wmm_wme_connected_device)
    def get_wmm_wme_connected_device(self):
        return self.get_entry_of_connected_devices('WMM/WME')


    @wishful_module.bind_function(upis.wifi.net.get_tdls_peer_connected_device)
    def get_tdls_peer_connected_device(self):
        return self.get_entry_of_connected_devices('TDLS peer')


    @wishful_module.bind_function(upis.wifi.net.connect_to_network)
    def connect_to_network(self, iface, ssid):

        self.log.info('connecting via to AP with SSID: %s->%s' % (str(self.wlan_interface), str(ssid)))

        cmd_str = 'sudo iwconfig ' + str(iface) + ' essid ' + str(ssid)

        try:
            [rcode, sout, serr] = self.run_command(cmd_str)
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))

        return True

    @wishful_module.bind_function(upis.wifi.net.network_dump)
    def network_dump(self, iface):

        self.log.info('dump_network on interface %s' % (str(iface)))

        cmd_str = 'sudo iw dev ' + str(iface) + ' link'

        try:
            [rcode, sout, serr] = self.run_command(cmd_str)
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))

        return sout

    @wishful_module.bind_function(upis.net.set_ip_address)
    def set_ip_address(self, iface, ip_address):

        self.log.info('setting ip address(): %s->%s' % (str(self.wlan_interface), str(ip_address)))

        cmd_str = 'sudo ifconfig ' + str(iface) + ' ' + str(ip_address)

        try:
            [rcode, sout, serr] = self.run_command(cmd_str)
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))

        return True

    @wishful_module.bind_function(upis.net.gen_layer2_traffic)
    #def gen_layer2_traffic(self, iface, num_packets, pinter, max_phy_broadcast_rate_mbps, **kwargs):
    #def gen_layer2_traffic(self, iface, num_packets, pinter, max_phy_broadcast_rate_mbps, ipdst, ipsrc):
    def gen_layer2_traffic(self, iface, num_packets, pinter, max_phy_broadcast_rate_mbps, ipPayloadSize=1350, ipdst="1.1.1.1", ipsrc="2.2.2.2", use_tcpreplay=True):

        self.log.info('gen_layer2_traffic ... here 802.11()')

        # ipdst = kwargs.get('ipdst')
        # ipsrc = kwargs.get('ipsrc')

        # get my MAC HW address
        myMacAddr = self.getHwAddr(iface)
        dstMacAddr = 'ff:ff:ff:ff:ff:ff'


        self.log.info('gen80211L2LinkProbing(): srcmacaddress %s - dstmacaddress %s - pinter %s' % (str(myMacAddr), str(dstMacAddr), str(pinter) ))

        if pinter is not None:

            # generate with some packet interval
            if num_packets > 255:
                num_packets = 255


            data = RadioTap() / Dot11(type=2, subtype=0, addr1=dstMacAddr, addr2=myMacAddr, addr3=myMacAddr) / LLC() / SNAP() / IP(dst=ipdst, src=ipsrc, ttl=(1,num_packets))

            #json_data = 'test'
            #data = Ether(dst="ff:ff:ff:ff:ff:ff",src=myMacAddr)/json_data

            self.log.info('gen80211L2LinkProbing(): start sent')

            sendp(data, iface=iface, inter=pinter)

            #my_mac=str(netifaces.ifaddresses(iface)[netifaces.AF_LINK][0]['addr'])
            #a=RadioTap()/Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=my_mac, addr3="ff:ff:ff:ff:ff:ff")/json_data
            # hexdump(a)
            # sendp(a, iface=iface, verbose=1)

            self.log.info('gen80211L2LinkProbing(): sent : return %f' % (1.0 / pinter))

            return 1.0 / pinter
        else:


            #assert max_phy_broadcast_rate_mbps is not None

            #use_tcpreplay = kwargs.get('use_tcpreplay')
            use_tcpreplay = True
            phyBroadcastMbps = max_phy_broadcast_rate_mbps

            ipPayloadSize=1450
            # craft packet to be transmitted
            payload = 'Z' * ipPayloadSize
            data = RadioTap() / Dot11(type=2, subtype=0, addr1=dstMacAddr, addr2=myMacAddr, addr3=myMacAddr) \
                   / LLC() / SNAP() / IP(dst=ipdst, src=ipsrc) / payload

            self.log.info('phyBroadcastMbps %d' % (phyBroadcastMbps))
            self.log.info('data %s ' % (str(data)))
            self.log.info('data len %d ' % (len(data)))

            now = datetime.now()

            if use_tcpreplay:
                # use tcprelay
                sendpfast(data, iface=iface, mbps=phyBroadcastMbps, loop=num_packets, file_cache=True)
            else:

                piter = (len(data) * 8) / (phyBroadcastMbps * 1e6)
                sendp(data, iface=iface, loop=1, inter=piter, realtime=True, count=num_packets, verbose=0)

            delta = datetime.now()-now
            # calc achieved transmit data rate
            self.log.info('delta sec %d - usec %d' % (delta.seconds, delta.microseconds))
            tx_frame_rate = 1.0 / ((delta.seconds + delta.microseconds / 1000000.0) / num_packets)

            self.log.info('gen80211L2LinkProbing(): tx_frame_rate=%d' % int(tx_frame_rate))

            return tx_frame_rate


    @wishful_module.bind_function(upis.net.sniff_layer2_traffic)
    def sniff_layer2_traffic(self, iface, sniff_timeout, ipdst=None, ipsrc=None):
#        self.log.info('sniff layer 2 traffic ... here 802.11')

        """
        call_count=2000
        pktlist = sniff(iface=iface, timeout=sniff_timeout, count=call_count, store=1)
        return pktlist
        """

        # some additional filtering ...todo!!!!!!!
        # ipdst = kwargs.get('ipdst')
        # ipsrc = kwargs.get('ipsrc')

        rx_pkts = {}
        rx_pkts['num'] = 0
        rx_pkts['avg_power'] = 0
        rx_power_list = []

        def ip_monitor_callback(pkt):
            #self.log.info('%s' % pkt.sprintf("{IP:%IP.src% -> %IP.dst% -> %IP.ttl%\n}"))
            if IP in pkt and pkt[IP].src == ipsrc and pkt[IP].dst == ipdst:
                radio_tap = pkt.sprintf("%notdecoded%")
                radio_tap_len = len(radio_tap)
                #extract power
                power = radio_tap[radio_tap_len-15:radio_tap_len-13]
                #print('radio_tap = %s - power %s' % (radio_tap, power))
                int_power=int(power,16)
                if int_power>0x7F:
                    int_power-= 0x100

                rx_power_list.append(int_power)
                rx_pkts['num'] = rx_pkts['num'] + 1
                self.log.debug('sniff80211L2LinkProbing(): rxpackets= %d' % rx_pkts['num'])
                #self.log.debug('radio_tap = %s - power %s - int_power %d' % (radio_tap, power, int_power))
                #return pkt.sprintf("{IP:%IP.src% -> %IP.dst% -> %IP.ttl%\n}")

        self.log.info('start sniffing on %s for %d sec' % (iface, sniff_timeout))
        sniff(iface=iface, prn=ip_monitor_callback, timeout=sniff_timeout)

        if len(rx_power_list)>0:
            rx_pkts['avg_power'] = sum(rx_power_list) / float(len(rx_power_list))
        else:
            rx_pkts['avg_power'] = 0
        self.log.info('sniff80211L2LinkProbing(): rxpackets= %d - avg_power %f' % (rx_pkts['num'], rx_pkts['avg_power']) )

        numRxPkts = rx_pkts['num']
        return numRxPkts
        #return rx_pkts

    @wishful_module.bind_function(upis.net.inject_frame)
    def inject_frame(self, iface, frame, is_layer_2_packet, tx_count=1, pkt_interval=1):
        self.log.debug("Inject frame".format())

        if is_layer_2_packet:
            sendp(frame, iface=iface, inter=pkt_interval, realtime=True, count=tx_count, verbose=0)
            #self.log.info("sent frame %s" % str(frame))
        else:
            send(frame, iface=iface, inter=pkt_interval, realtime=True, count=tx_count, verbose=0)

        return True


    @wishful_module.bind_function(upis.wifi.net.disconnect_device)
    def disconnect_device(self, iface, sta_mac_addr):
        """
            Send a disaccociation request frame to a client STA associated with this AP.
            tbd: what is -p ?? Please simplify
        """

        exec_file = str(os.path.join(self.getPlatformPathHandover())) + '/hostapd_cli'
        args = '-p /tmp/hostapd-' + iface + ' disassociate'

        command = exec_file + ' ' + args + ' ' + sta_mac_addr
        self.log.debug('Disassociate STA %s on iface %s' % (sta_mac_addr, iface))
        self.log.debug('exe: %s' % command)

        try:
            [rcode, sout, serr] = self.run_command(command)
            return sout
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))


    @wishful_module.bind_function(upis.wifi.net.remove_device_from_blacklist)
    def remove_device_from_blacklist(self, iface, sta_mac_addr):
        """
            Unblacklist a given STA in the AP, i.e. the STA is able to associate with this AP afterwards.
            tbd: what is -p ?? Please simplify
        """

        exec_file = str(os.path.join(self.getPlatformPathHandover())) + '/hostapd_cli'
        args = '-p /tmp/hostapd-' + iface + ' unblacklist_sta'

        command = exec_file + ' ' + args + ' ' + sta_mac_addr
        self.log.debug('exe: %s' % command)
        self.log.debug('Unblacklist node %s on iface %s' % (sta_mac_addr, iface))

        try:
            [rcode, sout, serr] = self.run_command(command)
            return sout
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))


    @wishful_module.bind_function(upis.wifi.net.add_device_to_blacklist)
    def add_device_to_blacklist(self, iface, sta_mac_addr):
        """
            Blacklist a given STA in the AP, i.e. any request for association by the STA will be ignored by the AP.
            tbd: what is -p ?? Please simplify
        """

        exec_file = str(os.path.join(self.getPlatformPathHandover())) + '/hostapd_cli'
        args = '-p /tmp/hostapd-' + iface + ' blacklist_sta'

        command = exec_file + ' ' + args + ' ' + sta_mac_addr
        self.log.debug('Blacklist node %s on iface %s' % (sta_mac_addr, iface))
        self.log.debug('exec %s' % command)

        try:
            [rcode, sout, serr] = self.run_command(command)
            return sout
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))


    @wishful_module.bind_function(upis.wifi.net.register_new_device)
    def register_new_device(self, iface, sta_mac_addr):
        """
            Register a new STA within the AP, i.e. afterwards the STA is able to exchange data frames.
            tbd: consider client capabilities
        """

        self.log.debug('Add new STA %s on iface %s' % (sta_mac_addr, iface))

        exec_file = str(os.path.join(self.getPlatformPathHandover())) + '/hostapd_cli'

        self.log.debug('exec path: %s' % exec_file)

        try:
            [rcode, sout, serr] = self.run_command(exec_file + " -p /tmp/hostapd-" + iface + " new_sta " + sta_mac_addr)
            return sout
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))


    @wishful_module.bind_function(upis.wifi.net.trigger_channel_switch_in_device)
    def trigger_channel_switch_in_device(self, iface, sta_mac_addr, target_channel, serving_channel, **kwargs):
        """
            Transmit Channel Switch Announcement (CSA) beacon to the given STA.
        """

        bssid = kwargs.get('bssid')
        self.log.debug('Sending CSA to %s on iface %s with BSSID %s switch STA to channel %s' % (sta_mac_addr, iface, bssid, str(target_channel)))

        # tbd: clean up this mess
        beacon = RadioTap() / Dot11(type=0, subtype=8, addr1=sta_mac_addr, addr2=bssid, addr3=bssid) / binascii.unhexlify(
                '3bc0904f00000000640001000005424947415001088c129824b048606c0301'+ hex(
                    serving_channel).replace("0x", "")+'050400020000070c44452024081464051a84031a2d1a0c001bffff0000000000000000000001000000000000000000003d162c0004000000000000000000000000000000000000007f080000000000000040dd180050f2020101800003a4000027a4000042435d0062322e00dd06aaaaaa3f4325dd14aaaaaa8020544b4e2d4c6f57532d53797374656ddd06aaaaaa215a01250300' + hex(
                    target_channel).replace("0x", "") + '00')

        # tbd: do we really need this
        BEACON_ARQ = 3
        for ii in range(BEACON_ARQ):
            # repetitive transmission
            sendp(beacon, iface=iface)
        return True


    #################################################
    # Helper functions
    #################################################

    def get_entry_of_connected_devices(self, key):

        try:
            res = self.get_info_of_connected_devices()

            rv = {}
            for mac_addr in res:
                value = res[mac_addr][key]
                self.log.info('%s -> %s' % (mac_addr, value))
                rv[mac_addr] = value

            # dict of mac_addr -> value
            return rv
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))

    def run_command(self, command):
        '''
            Method to start the shell commands and get the output as iterater object
        '''
        sp = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = sp.communicate()

        if True:
            if out:
                self.log.debug("standard output of subprocess:")
                self.log.debug(out)
            if err:
                self.log.debug("standard error of subprocess:")
                self.log.debug(err)

        #if err:
        #    raise Exception("An error occurred in Dot80211Linux: %s" % err)

        return [sp.returncode, out.decode("utf-8"), err.decode("utf-8")]

    def run_timeout_command(self, command, timeout):
        """
            Call shell-command and either return its output or kill it
            if it doesn't normally exit within timeout seconds and return None
        """
        cmd = command.split(" ")
        start = datetime.datetime.now()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while process.poll() is None:
            time.sleep(0.1)
            now = datetime.datetime.now()
            if (now - start).seconds > timeout:
                os.kill(process.pid, signal.SIGKILL)
                os.waitpid(-1, os.WNOHANG)
                return process.stdout.read()
        return process.stdout.read()


    def getHwAddr(self, iface):
        self.log.debug('getHwAddr() called {}'.format(iface))
        retVal = ni.ifaddresses(iface)[ni.AF_LINK]
        #retVal = list(retVal[0].values())[1]
        retVal = retVal[0]
        retVal = retVal['addr']
        self.log.debug('getHwAddr() retVal %s' % str(retVal))
        return retVal


    def get_platform_path_iw(self):
        '''
        Path to platform dependent (native) binaries: iw
        '''
        PLATFORM_PATH = os.path.join("..", "..", "agent_modules", "wifi", "tool", "bin")
        # pl = platform.architecture()
        # sys = platform.system()
        # machine = platform.machine()
        #return os.path.join(PLATFORM_PATH, sys, pl[0], machine)
        return PLATFORM_PATH