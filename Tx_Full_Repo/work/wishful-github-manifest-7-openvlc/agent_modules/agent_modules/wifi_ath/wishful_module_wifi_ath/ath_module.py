import logging
import random
import pickle
import os
import inspect
import subprocess
import zmq
import time
import platform
import numpy as np
import iptc
from pytc.TrafficControl import TrafficControl

import wishful_module_wifi
import wishful_upis as upis
import wishful_framework as wishful_module
from wishful_framework.classes import exceptions
import wishful_framework.upi_arg_classes.edca as edca #<----!!!!! Important to include it here; otherwise cannot be pickled!!!!
import wishful_framework.upi_arg_classes.flow_id as FlowId


__author__ = "Piotr Gawlowicz, Mikolaj Chwalisz, Anatolij Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, chwalisz, zubow}@tkn.tu-berlin.de"

# Used by local controller for communication with mac processor
LOCAL_MAC_PROCESSOR_CTRL_PORT = 1217

@wishful_module.build_module
class AthModule(wishful_module_wifi.WifiModule):
    def __init__(self):
        super(AthModule, self).__init__()
        self.log = logging.getLogger('AthModule')
        self.channel = 1
        self.power = 1


    @wishful_module.bind_function(upis.radio.set_mac_access_parameters)
    def setEdcaParameters(self, iface=None,queueId, queueParams):
        self.log.info("ATH9K sets EDCA parameters for queue: {} on interface: {}".format(queueId, self.interface))

        self.log.debug("AIFS: {}".format(queueParams.getAifs()))
        self.log.debug("CwMin: {}".format(queueParams.getCwMin()))
        self.log.debug("CwMax: {}".format(queueParams.getCwMax()))
        self.log.debug("TxOp: {}".format(queueParams.getTxOp()))

        cmd_str = ('sudo iw ' + self.interface + ' info')
	if iface:
		cmd_str = ('sudo iw ' + iface + ' info')
        cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)
        cmd_output = cmd_output.decode("utf-8")
        for item in cmd_output.split("\n"):
             if "wiphy" in item:
                line = item.strip()

        phyId = [int(s) for s in line.split() if s.isdigit()][0]

        try:
            myfile = open('/sys/kernel/debug/ieee80211/phy'+str(phyId)+'/ath9k/txq_params', 'w')
            value = str(queueId) + " " + str(queueParams.getAifs()) + " " + str(queueParams.getCwMin()) + " " + str(queueParams.getCwMax()) + " " + str(queueParams.getTxOp())
            myfile.write(value)
            myfile.close()
            return "OK"
        except Exception as e:
            self.log.fatal("Operation not supported: %s" % e)
            raise exceptions.UPIFunctionExecutionFailedException(func_name='radio.set_mac_access_parameters', err_msg='cannot open file')



    @wishful_module.bind_function(upis.radio.get_mac_access_parameters)
    def getEdcaParameters(self):
        self.log.debug("ATH9K gets EDCA parameters for interface: {}".format(self.interface))

        cmd_str = ('sudo iw ' + self.interface + ' info')
        cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)

        for item in cmd_output.split("\n"):
             if "wiphy" in item:
                line = item.strip()

        phyId = [int(s) for s in line.split() if s.isdigit()][0]

        try:
            myfile = open('/sys/kernel/debug/ieee80211/phy'+str(phyId)+'/ath9k/txq_params', 'r')
            data = myfile.read()
            myfile.close()
            return data
        except Exception as e:
            self.log.fatal("Operation not supported: %s" % e)
            raise exceptions.UPIFunctionExecutionFailedException(func_name='radio.get_mac_access_parameters', err_msg='cannot open file')


    @wishful_module.bind_function(upis.radio.set_per_flow_tx_power)
    def set_per_flow_tx_power(self, flowId, txPower):
        self.log.debug('set_per_flow_tx_power on iface: {}'.format(self.interface))

        tcMgr = TrafficControl()
        markId = tcMgr.generateMark()
        self.setMarking(flowId, table="mangle", chain="POSTROUTING", markId=markId)

        cmd_str = ('sudo iw ' + self.interface + ' info')
        cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)

        for item in cmd_output.split("\n"):
             if "wiphy" in item:
                line = item.strip()

        phyId = [int(s) for s in line.split() if s.isdigit()][0]

        try:
            myfile = open('/sys/kernel/debug/ieee80211/phy'+str(phyId)+'/ath9k/per_flow_tx_power', 'w')
            value = str(markId) + " " + str(txPower) + " 0"
            myfile.write(value)
            myfile.close()
            return "OK"
        except Exception as e:
            self.log.fatal("Operation not supported: %s" % e)
            raise exceptions.UPIFunctionExecutionFailedException(func_name='radio.set_per_flow_tx_power', err_msg='cannot open file')


    def setMarking(self, flowId, table="mangle", chain="POSTROUTING", markId=None):
        
        if not markId:
            tcMgr = TrafficControl()
            markId = tcMgr.generateMark()

        rule = iptc.Rule()

        if flowId.srcAddress:
            rule.src = flowId.srcAddress

        if flowId.dstAddress:
            rule.dst = flowId.dstAddress

        if flowId.prot:
            rule.protocol = flowId.prot
            match = iptc.Match(rule, flowId.prot)

            if flowId.srcPort:
                match.sport = flowId.srcPort

            if flowId.dstPort:
                match.dport = flowId.dstPort

            rule.add_match(match)

        target = iptc.Target(rule, "MARK")
        target.set_mark = str(markId)
        rule.target = target
        chain = iptc.Chain(iptc.Table(table), chain)
        chain.insert_rule(rule)


    @wishful_module.bind_function(upis.radio.clean_per_flow_tx_power_table)
    def clean_per_flow_tx_power_table(self):
        self.log.debug('clean_per_flow_tx_power_table on iface: {}'.format(self.interface))

        cmd_str = ('sudo iw ' + self.interface + ' info')
        cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)

        for item in cmd_output.split("\n"):
             if "wiphy" in item:
                line = item.strip()

        phyId = [int(s) for s in line.split() if s.isdigit()][0]

        try:
            myfile = open('/sys/kernel/debug/ieee80211/phy'+str(phyId)+'/ath9k/per_flow_tx_power', 'w')
            value = "0 0 0"
            myfile.write(value)
            myfile.close()
            return "OK"
        except Exception as e:
            self.log.fatal("Operation not supported: %s" % e)
            raise exceptions.UPIFunctionExecutionFailedException(func_name='radio.clean_per_flow_tx_power_table', err_msg='cannot open file')


    @wishful_module.bind_function(upis.radio.get_per_flow_tx_power_table)
    def get_per_flow_tx_power_table(self):
        self.log.debug('get_per_flow_tx_power_table on iface: {}'.format(self.interface))

        cmd_str = ('sudo iw ' + self.interface + ' info')
        cmd_output = subprocess.check_output(cmd_str, shell=True, stderr=subprocess.STDOUT)

        for item in cmd_output.split("\n"):
             if "wiphy" in item:
                line = item.strip()

        phyId = [int(s) for s in line.split() if s.isdigit()][0]

        try:
            myfile = open('/sys/kernel/debug/ieee80211/phy'+str(phyId)+'/ath9k/per_flow_tx_power', 'r')
            data = myfile.read()
            myfile.close()
            return data
        except Exception as e:
            self.log.fatal("Operation not supported: %s" % e)
            raise exceptions.UPIFunctionExecutionFailedException(func_name='radio.get_per_flow_tx_power_table', err_msg='cannot open file')


    @wishful_module.bind_function(upis.radio.get_noise)
    def get_noise(self):
        self.log.debug("Get Noise".format())
        return random.randint(-120, -30)


    @wishful_module.bind_function(upis.radio.get_airtime_utilization)
    def get_airtime_utilization(self):
        self.log.debug("Get Airtime Utilization".format())
        return random.random()


    @wishful_module.bind_function(upis.radio.perform_spectral_scanning)
    def perform_spectral_scanning(self, iface, freq_list, mode):
        """
            Perform active spectral scanning
        """

        self.log.debug('performActiveSpectralScanning on iface %s for freq=%s' % (iface, freq_list))

        exec_file = str(os.path.join(self.getPlatformPathSpectralScan())) + '/scan.sh'
        command = exec_file + " " + iface + " /tmp/out \"" + freq_list + "\""

        self.log.debug('command: %s' % command)

        try:
            # perform scanning
            [rcode, sout, serr] = self.run_command(command)

            if serr:
                self.log.warn("standard error of subprocess:")
                self.log.warn(serr)
                raise Exception("Error occured during spectrum scanning: %s" % serr)

            # perform parsing results
            self.log.debug('parsing scan results ...')

            tmpfile = '/tmp/out.dat'
            res = []
            with open(tmpfile) as f:
                content = f.readlines()

                for line in content:
                    arr = line.split(',')
                    res.append(arr)

            # cleanup
            os.remove(tmpfile)

            self.log.info('spec scan size %d' % len(res))

            if mode == 0:
                # return just raw samples
                return res
            elif mode == 1:
                # return the max/mean signal for each frequency bin only
                y = np.array(res)
                y = y.astype(np.float)
                uniq_freq = np.unique(y[:,0])
                uniq_freq.sort(axis=0)
                ret = []
                for v in np.nditer(uniq_freq.T):
                    v2 = np.asscalar(v)

                    a = y[np.logical_or.reduce([y[:,0] == x for x in (v2,)])]
                    sig = a[:,7].astype(np.float)
                    max_sig = 100
                    sig = sig[sig < max_sig]

                    max_v = np.ndarray.max(sig)
                    mean_v = np.ndarray.mean(sig)

                    #print('max: ', max_v)
                    #print('mean: ', mean_v)
                    ret.append([np.asscalar(v), max_v, mean_v])

                return ret
            else:
                raise Exception("Unknown mode type %s" % str(mode))

        except Exception as e:
            self.log.fatal("An error occurred in Dot80211Linux: %s" % e)
            raise Exception("An error occurred in Dot80211Linux: %s" % e)


    #################################################
    # Helper functions
    #################################################

    def getPlatformPathSpectralScan(self):
        """
        Path to platform dependent (native) binaries: here spectral scanning
        """
        PLATFORM_PATH = os.path.join(".", "runtime", "connectors", "dot80211_linux", "ath_spec_scan", "bin")
        pl = platform.architecture()
        sys = platform.system()
        machine = platform.machine()
        return os.path.join(PLATFORM_PATH, sys, pl[0], machine)
