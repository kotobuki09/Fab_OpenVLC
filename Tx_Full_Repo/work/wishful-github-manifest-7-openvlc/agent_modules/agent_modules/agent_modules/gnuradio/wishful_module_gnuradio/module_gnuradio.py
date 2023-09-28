import os
import time
import logging
import random
import wishful_upis as upis
import wishful_framework as wishful_module
import subprocess
import pprint
import xmlrpc.client
from enum import Enum
import xml.etree.ElementTree as ET
from numpy import arange
from numpy import log10

# GLOBAL VARIABLES DEFINITION

UNII_low_band = arange(5.170 * 10 ** 9, 5.250 * 10 ** 9,0.010 * 10 ** 9)        # UNII_low_band = [5170,5180,5190,5200,5210,5220,5230,5240 MHz]
UNII_2_middle_band = arange(5.260 * 10 ** 9, 5.330 * 10 ** 9,0.020 * 10 ** 9)   # UNII_2_middle_band = [5260,5280,5300,5320 MHz]
UNII_2_extended_band = arange(5.500 * 10 ** 9, 5.720 * 10 ** 9,0.02 * 10 ** 9)  # UNII_2_extended_band = [5500,5520,5540,5560,5580,5600,5620,5640,5660,5680,5700 MHz]
UNII_3_upper_band = arange(5.745 * 10 ** 9, 5.845 * 10 ** 9,0.02 * 10 ** 9)     # UNII_3_upper_band = [5745,5765,5785,5805,5825 MHz]
MAX_UNII_low_band_indoor_output_power = 16                                      # power limited to 16 dBm in indoor use
MAX_UNII_2_middle_band_output_power = 23                                        # power limited to 23 dBm in both indoor and outdoor use
MAX_UNII_2_extended_band_output_power = 23                                      # power limited to 23 dBm in both indoor and outdoor use
MAX_UNII_3_upper_band_antenna_gain = 23                                         # antenna gain limited to 23 dBi

from generator.rp_combiner import RadioProgramCombiner

__author__ = "A. Zubow"
__author__ = "F. Di Stolfa"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{zubow}@tkn.tu-berlin.de"
__email__ = "{distolfa}@tkn.tu-berlin.de"


""" tracking the state of the radio program """
class RadioProgramState(Enum):
    INACTIVE = 1
    RUNNING = 2
    PAUSED = 3
    STOPPED = 4

"""
    Basic GNURadio connector module.
"""
@wishful_module.build_module
class GnuRadioModule(wishful_module.AgentModule):
    def __init__(self):
        super(GnuRadioModule, self).__init__()

        self.log = logging.getLogger('gnuradio_module.main')

        self.gr_radio_programs = {}
        self.gr_process = None
        self.gr_process_io = None
        self.gr_radio_programs_path = os.path.join(os.path.expanduser("~"), ".wishful", "radio")
        if not os.path.exists(self.gr_radio_programs_path):
            os.makedirs(self.gr_radio_programs_path)
            self.build_radio_program_dict()

        # config values
        self.ctrl_socket_host = "localhost"
        self.ctrl_socket_port = 8080
        self.ctrl_socket = None

        self.gr_state = RadioProgramState.INACTIVE

        self.combiner = None
        self.log.debug('initialized ...')


    @wishful_module.bind_function(upis.radio.add_program)
    def add_program(self, **kwargs):
        """ Serialize radio program to local repository """

        # params
        grc_radio_program_name = kwargs['grc_radio_program_name']  # name of the radio program
        grc_radio_program_code = kwargs['grc_radio_program_code']  # radio program XML flowgraph


        self.log.info("Add radio program %s to local repository" % grc_radio_program_name)

        # serialize radio program XML flowgraph to file
        fid = open(os.path.join(self.gr_radio_programs_path, grc_radio_program_name + '.grc'), 'w')
        fid.write(grc_radio_program_code)
        fid.close()

        # rebuild radio program dictionary
        self.build_radio_program_dict()


    @wishful_module.bind_function(upis.radio.merge_programs)
    def merge_programs(self, **kwargs):
        '''
            Given a set of Gnuradio programs (described as GRC flowgraph) this program combines all
            those radio programs in a single meta radio program which allows very fast switching from
            one protocol to another.
        '''

        # params
        grc_radio_program_names = kwargs['grc_radio_program_names']  # list of radio program names

        self.combiner = RadioProgramCombiner(self.gr_radio_programs_path)

        # make sure all radio programms are already uploaded
        for rp in grc_radio_program_names:
            if rp not in self.gr_radio_programs:
                self.log.warn('Cannot merge missing radio program!!!')
                raise AttributeError("Unknown radio program %s" % rp)
            self.combiner.add_radio_program(rp + '_', rp + '.grc')

        # run generator
        rp_fname = self.combiner.generate()

        # rebuild radio program dictionary
        self.build_radio_program_dict()

        return rp_fname


    @wishful_module.bind_function(upis.radio.switch_program)
    def switch_program(self, target_program_name, **kwargs):
        '''
            Run-time control of meta radio program which allows very fast switching from
            one protocol to another:
            - context switching
        '''

        # open proxy
        proxy = xmlrpc.client.ServerProxy("http://localhost:8080/")

        # load metadata
        proto_usrp_src_dicts = eval(open(os.path.join(self.gr_radio_programs_path, 'meta_rp_proto_dict.txt'), 'r').read())
        usrp_source_fields = eval(open(os.path.join(self.gr_radio_programs_path, 'meta_rp_fields.txt'), 'r').read())

        res = getattr(proxy, "get_session_var")()
        self.log.info('Current proto: %s' % str(res))
        #last_proto = res[0]

        # get IDX of new radio program
        new_proto_idx = self.combiner.get_proto_idx(target_program_name)

        # read variables of new protocol
        init_session_value = []
        init_session_value.append(new_proto_idx)
        for field in usrp_source_fields:
            res = getattr(proxy, "get_%s" % proto_usrp_src_dicts[new_proto_idx][field])()
            init_session_value.append(float(res))

        self.log.info('Switch to protocol %d with cfg %s' % (new_proto_idx, str(init_session_value)))
        getattr(proxy, "set_session_var")(init_session_value)


    @wishful_module.bind_function(upis.radio.remove_program)
    def remove_program(self, **kwargs):
        """ Remove radio program from local repository """

        grc_radio_program_name = kwargs['grc_radio_program_name']  # name of the radio program

        if self.gr_radio_programs is not None and grc_radio_program_name in self.gr_radio_programs:
            os.remove(self.gr_radio_programs[grc_radio_program_name])
            os.rmdir(os.path.join(self.gr_radio_programs_path, grc_radio_program_name))
            os.remove(os.path.join(self.gr_radio_programs_path, grc_radio_program_name + '.grc'))


    @wishful_module.bind_function(upis.radio.set_active)
    def set_active(self, **kwargs):

        # params
        grc_radio_program_name = kwargs['grc_radio_program_name'] # name of the radio program

        if self.gr_state == RadioProgramState.INACTIVE:
            self.log.info("Start new radio program")
            self.ctrl_socket = None

            """Launches Gnuradio in background"""
            if self.gr_radio_programs is None or grc_radio_program_name not in self.gr_radio_programs:
                # serialize radio program to local repository
               self.add_program(**kwargs)
            if self.gr_process_io is None:
                self.gr_process_io = {'stdout': open('/tmp/gnuradio.log', 'w+'), 'stderr': open('/tmp/gnuradio-err.log', 'w+')}
            if grc_radio_program_name not in self.gr_radio_programs:
                self.log.error("Available layers: %s" % ", ".join(self.gr_radio_programs.keys()))
                raise AttributeError("Unknown radio program %s" % grc_radio_program_name)
            if self.gr_process is not None:
                # An instance is already running
                self.gr_process.kill()
                self.gr_process = None
            try:
                # start GNURadio process
                self.gr_radio_program_name = grc_radio_program_name
                self.gr_process = subprocess.Popen(["env", "python2", self.gr_radio_programs[grc_radio_program_name]],
                                                   stdout=self.gr_process_io['stdout'], stderr=self.gr_process_io['stderr'])
                self.gr_state = RadioProgramState.RUNNING
            except OSError:
                return False
            return True

        elif self.gr_state == RadioProgramState.PAUSED and self.gr_radio_program_name == grc_radio_program_name:
            # wakeup
            self.log.info('Wakeup radio program')
            self.init_proxy()
            try:
                self.ctrl_socket.start()
                self.gr_state = RadioProgramState.RUNNING
            except xmlrpc.Fault as e:
                self.log.error("ERROR: %s" % e.faultString)
        else:
            self.log.warn('Please deactive old radio program before activating a new one.')


    @wishful_module.bind_function(upis.radio.set_inactive)
    def set_inactive(self, **kwargs):

        pause_rp =  bool(kwargs['do_pause'])

        if self.gr_state == RadioProgramState.RUNNING or self.gr_state == RadioProgramState.PAUSED:

            if pause_rp:
                self.log.info("pausing radio program")

                self.init_proxy()
                self.ctrl_socket.stop()
                self.ctrl_socket.wait()
                self.gr_state = RadioProgramState.PAUSED

            else:
                self.log.info("stopping radio program")

                if self.gr_process is not None and hasattr(self.gr_process, "kill"):
                    self.gr_process.kill()
                if self.gr_process_io is not None and self.gr_process_io is dict:
                    for k in self.gr_process_io.keys():
                        #if self.gr_process_io[k] is file and not self.gr_process_io[k].closed:
                        if not self.gr_process_io[k].closed:
                            self.gr_process_io[k].close()
                            self.gr_process_io[k] = None
                self.gr_state = RadioProgramState.INACTIVE
        else:
            self.log.warn("no running or paused radio program; ignore command")


    @wishful_module.bind_function(upis.radio.set_parameter_lower_layer)
    def gnuradio_set_vars(self, **kwargs):
        if self.gr_state == RadioProgramState.RUNNING or self.gr_state == RadioProgramState.PAUSED:
            self.init_proxy()
            for k, v in kwargs.items():
                try:
                    getattr(self.ctrl_socket, "set_%s" % k)(v)
                except Exception as e:
                    self.log.error("Unknown variable '%s -> %s'" % (k, e))
        else:
            self.log.warn("no running or paused radio program; ignore command")


    @wishful_module.bind_function(upis.radio.get_parameter_lower_layer)
    def gnuradio_get_vars(self, **kwargs):
        if self.gr_state == RadioProgramState.RUNNING or self.gr_state == RadioProgramState.PAUSED:
            rv = {}
            self.init_proxy()
            for k, v in kwargs.items():

                try:
                    res = getattr(self.ctrl_socket, "get_%s" % k)()
                    rv[k] = res
                except Exception as e:
                    self.log.error("Unknown variable '%s -> %s'" % (k, e))
            return rv
        else:
            self.log.warn("no running or paused radio program; ignore command")
            return None


    """ Helper functions """

    def build_radio_program_dict(self):
        """
            Converts the radio program XML flowgraphs into executable python scripts
        """
        self.gr_radio_programs = {}
        grc_files = dict.fromkeys([x.rstrip(".grc") for x in os.listdir(self.gr_radio_programs_path) if x.endswith(".grc")], 0)
        topblocks = dict.fromkeys(
            [x for x in os.listdir(self.gr_radio_programs_path) if os.path.isdir(os.path.join(self.gr_radio_programs_path, x))], 0)
        for x in grc_files.keys():
            grc_files[x] = os.stat(os.path.join(self.gr_radio_programs_path, x + ".grc")).st_mtime
            try:
                os.mkdir(os.path.join(self.gr_radio_programs_path, x))
                topblocks[x] = 0
            except OSError:
                pass
        for x in topblocks.keys():
            topblocks[x] = os.stat(os.path.join(self.gr_radio_programs_path, x, 'top_block.py')).st_mtime if os.path.isfile(
                os.path.join(self.gr_radio_programs_path, x, 'top_block.py')) else 0
        for x in grc_files.keys():
            if grc_files[x] > topblocks[x]:
                outdir = "--directory=%s" % os.path.join(self.gr_radio_programs_path, x)
                input_grc = os.path.join(self.gr_radio_programs_path, x + ".grc")
                try:
                    subprocess.check_call(["grcc", outdir, input_grc])
                except:
                    pass
        for x in topblocks.keys():
            if os.path.isfile(os.path.join(self.gr_radio_programs_path, x, 'top_block.py')):
                self.gr_radio_programs[x] = os.path.join(self.gr_radio_programs_path, x, 'top_block.py')

        self.log.info('gr_radio_programs:\n{}'.format(pprint.pformat(self.gr_radio_programs)))


    def init_proxy(self):
        if self.ctrl_socket == None:
            self.ctrl_socket = xmlrpc.client.ServerProxy("http://%s:%d" % (self.ctrl_socket_host, self.ctrl_socket_port))

"""
    Secure GNURadio connector module which checks whether configuration meets regulation requirements, i.e. used frequency,
    transmit power, ...
"""

class SecureGnuRadioModule(GnuRadioModule):
    def __init__(self):
        super(SecureGnuRadioModule, self).__init__()
        self.log = logging.getLogger('SecureGnuRadioModule')


    @wishful_module.bind_function(upis.radio.set_active)
    def set_active(self, **kwargs):

        grc_radio_program_name = kwargs['grc_radio_program_name']
        tree = ET.ElementTree(file = os.path.join(os.path.expanduser("."), "testdata", grc_radio_program_name + '.grc'))
        root = tree.getroot()
        for block in root.findall('block'):
            if block.findtext('key') == 'uhd_usrp_sink':
                for param in block.findall('param'):
                    for x in range(0, 32):
                        if param.findtext('key') == 'center_freq%s' % x and param.findtext('value') != '0':
                            frequency_sink = float(param.findtext('value'))
                        if param.findtext('key') == 'gain%s' % x and param.findtext('value') != '0':
                            uhd_gain_sink = float(param.findtext('value'))
            if block.findtext('key') == 'uhd_usrp_source':
                for param in block.findall('param'):
                    for x in range(0, 32):
                        if param.findtext('key') == 'center_freq%s' % x and param.findtext('value') != '0':
                            frequency_source = float(param.findtext('value'))
                        if param.findtext('key') == 'gain%s' % x and param.findtext('value') != '0':
                            uhd_gain_source = float(param.findtext('value'))
       
        #--------------------------------------------------------------------------------------------------------------------------------------------------------
        # LINK BETWEEN UHD GAIN SET BY THE USER AND THE EFFECTIVE OUTPUT POWER
        # BASED ON THIS PAPER: An empirical model of the sbx daughterboard output power driven by USRP N210 adn GNURADIO - R. Zitouni, S.Ataman
        # I've implemented their concepts to link the gain of the antenna on the sbx daughterboard and the effective output power
        #------------------------------------------------------------------------------------------------------------------------------------------------------
        DAC_value = 1                                                     
        beta_zero = -5.586*10**(-3)
        alpha_zero = 10*log10(4.57)
        # UHD_USRP_SINK BLOCK
        P1 = 20*log10(DAC_value) + uhd_gain_sink
        actual_output_power_sink = P1 + alpha_zero + beta_zero*(frequency_sink/10**(6))
        
        # UHD_USRP_SOURCE BLOCK
        P1 = 20*log10(DAC_value) + uhd_gain_source
        actual_output_power_source = P1 + alpha_zero + beta_zero*(frequency_source/10**(6))
        
        #----------------------------------------------------------------------------------------------------------------------------------------------------------
        # Check if the user's programm follows the FCC's rules for UHD_USRP_SINK block
        if frequency_sink in UNII_low_band and actual_output_power_sink < MAX_UNII_low_band_indoor_output_power:
            return super(SecureGnuRadioModule, self).set_active(**kwargs)
        elif frequency_sink in UNII_2_middle_band and actual_output_power_sink < MAX_UNII_2_middle_band_output_power:
            return super(SecureGnuRadioModule, self).set_active(**kwargs)
        elif frequency_sink in UNII_2_extended_band and actual_output_power_sink < MAX_UNII_2_extended_band_output_power:
            return super(SecureGnuRadioModule, self).set_active(**kwargs)
        elif frequency_sink in UNII_3_upper_band and uhd_gain_sink < MAX_UNII_3_upper_band_antenna_gain:
            return super(SecureGnuRadioModule, self).set_active(**kwargs)
        else:
            self.log.warn('ERROR: Frequency and/or Power in UHD_USRP_SINK block not allowed')
        # Check if the user's programm follows the FCC's rules for UHD_USRP_SOURCE block
        if frequency_source in UNII_low_band and actual_output_power_source < MAX_UNII_low_band_indoor_output_power:
            return super(SecureGnuRadioModule, self).set_active(**kwargs)
        elif frequency_source in UNII_2_middle_band and actual_output_power_source < MAX_UNII_2_middle_band_output_power:
            return super(SecureGnuRadioModule, self).set_active(**kwargs)
        elif frequency_source in UNII_2_extended_band and actual_output_power_source < MAX_UNII_2_extended_band_output_power:
            return super(SecureGnuRadioModule, self).set_active(**kwargs)
        elif frequency_source in UNII_3_upper_band and uhd_gain_source < MAX_UNII_3_upper_band_antenna_gain:
            return super(SecureGnuRadioModule, self).set_active(**kwargs)
        else:
            self.log.warn('ERROR: Frequency and/or Power in UHD_USRP_SOURCE block not allowed')



    @wishful_module.bind_function(upis.radio.set_inactive)
    def set_inactive(self, **kwargs):
        pass
     #TO COMPLETE




    @wishful_module.bind_function(upis.radio.set_parameter_lower_layer)
    def gnuradio_set_vars(self, **kwargs):

        if self.gr_state == RadioProgramState.RUNNING or self.gr_state == RadioProgramState.PAUSED:
                try:
                    grc_radio_program_name = kwargs['grc_radio_program_name']
                    root = ET.ElementTree(file=os.path.join(os.path.expanduser("."), "testdata", grc_radio_program_name + '.grc')).getroot()
                    for block in root.findall('block'):
                        if block.findtext('key') == 'uhd_usrp_sink':
                            for param in block.findall('param'):
                                for x in range(0, 32):
                                    if param.findtext('key') == 'center_freq%s' % x and param.findtext('value') != '0':
                                        param.find('value').text = kwargs['frequency_sink_update']
                                    if param.findtext('key') == 'gain%s' % x and param.findtext('value') != '0':
                                        param.find('value').text = kwargs['uhd_gain_sink_update']
                        if block.findtext('key') == 'uhd_usrp_source':
                            for param in block.findall('param'):
                                for x in range(0, 32):
                                    if param.findtext('key') == 'center_freq%s' % x and param.findtext('value') != '0':
                                        param.find('value').text = kwargs['frequency_source_update']
                                    if param.findtext('key') == 'gain%s' % x and param.findtext('value') != '0':
                                        param.find('value').text = kwargs['uhd_gain_source_update']
                    tree = ET.ElementTree(root)
                    tree.write(os.path.join(os.path.expanduser("."), "testdata", grc_radio_program_name + '.grc'))

                except Exception as e:
                    self.log.error("Unknown variable '%s -> %s'" )
        else:
            self.log.warn("no running or paused radio program; ignore command")
            return None

    @wishful_module.bind_function(upis.radio.get_parameter_lower_layer)
    def gnuradio_get_vars(self, **kwargs):
        gvals={}
        if self.gr_state == RadioProgramState.RUNNING or self.gr_state == RadioProgramState.PAUSED:
            rv = {}
            self.init_proxy()
            for k in kwargs.items():
                try:
                 grc_radio_program_name = kwargs['grc_radio_program_name']
                 tree = ET.ElementTree(file=os.path.join(os.path.expanduser("."), "testdata", grc_radio_program_name + '.grc'))
                 root = tree.getroot()
                 for block in root.findall('block'):
                    if block.findtext('key') == 'uhd_usrp_sink':
                        for param in block.findall('param'):
                            for x in range(0, 32):
                                if param.findtext('key') == 'center_freq%s' % x and param.findtext('value') != '0':
                                    frequency_sink = float(param.findtext('value'))
                                if param.findtext('key') == 'gain%s' % x and param.findtext('value') != '0':
                                    uhd_gain_sink = float(param.findtext('value'))
                    if block.findtext('key') == 'uhd_usrp_source':
                        for param in block.findall('param'):
                            for x in range(0, 32):
                                if param.findtext('key') == 'center_freq%s' % x and param.findtext('value') != '0':
                                    frequency_source = float(param.findtext('value'))
                                if param.findtext('key') == 'gain%s' % x and param.findtext('value') != '0':
                                    uhd_gain_source = float(param.findtext('value'))
                except Exception as e:
                    self.log.error("Unknown variable '%s -> %s'" %(k,e))

            gvals['frequency_sink']=frequency_sink
            gvals['uhd_gain_sink']=uhd_gain_sink
            gvals['frequency_source']=frequency_source
            gvals['uhd_gain_source']=uhd_gain_source
            return gvals

        else:
            self.log.warn("no running or paused radio program; ignore command")
            return None



