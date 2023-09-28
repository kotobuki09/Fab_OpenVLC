__author__ = "Domenico Garlisi"
__copyright__ = "Copyright (c) 2015"
__version__ = "0.1.0"
__email__ = "{domenico.garlisi, , }@cnit.it"

'''
    The RAS antenna is part of the extension Adant developed a complete custom reconfigurable antenna system (RAS) that can
be integrated with the WISHFUL testbeds. Specifically, the RAS developed as part of this extension	is a 2x2 MIMO antenna
system composed	of reconfigurable antennas working at 2.4GHz or at 5GHz, controllers with USB and serial connections for
interfacing the antennas with the selected testbeds and new local UPIs compatible with the WISHFUL framework that allow
to change the configuration of the smart antenna system remotely. The RAS has been successfully installed on w-iLab2.
    The protocol-specific definition of the WiSHFUL radio control interface, UPI_R, for configuration/monitoring of the
    RAS antenna.

'''

'''
    PHY layer
'''
def set_sas_conf(band, conf_ant1, conf_ant2, conf_ant3, conf_ant4):
    '''Set RAS antenna configuration
    '''
    pass


def reset_controller():
    '''Restart RAS antenna module
    '''
    pass

