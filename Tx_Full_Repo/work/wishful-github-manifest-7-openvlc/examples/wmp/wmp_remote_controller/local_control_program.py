"""
Local control program to be executed on remote nodes.
"""

__author__ = "Domenico Garlisi"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"


# Definition of Local Control Program
def my_local_control_program(controller):
    # do all needed imports here!!!
    import time
    import datetime
    import sys
    sys.path.append('../../../')
    sys.path.append("../../../agent_modules/wifi_ath")
    sys.path.append("../../../agent_modules/wifi_wmp")
    sys.path.append("../../../agent_modules/wifi")
    sys.path.append('../../../upis')
    sys.path.append('../../../framework')
    sys.path.append('../../../agent')
    from agent_modules.wifi_wmp.wmp_structure import UPI_R


    @controller.set_default_callback()
    def default_callback(cmd, data):
        print(("DEFAULT CALLBACK : Cmd: {}, Returns: {}".format(cmd, data)))

    # control loop
    print("Local ctrl program started: {}".format(controller.name))
    while not controller.is_stopped():
        msg = controller.recv(timeout=1)
        if msg:
            ch = msg["new_channel"]
            print("Schedule get monitor to {} in 5s:".format(ch))
            UPI_myargs = {'interface' : 'wlan0', 'measurements' : [UPI_R.REGISTER_1, UPI_R.REGISTER_2, UPI_R.NUM_TX_DATA_FRAME, UPI_R.NUM_RX_ACK, UPI_R.NUM_RX_ACK_RAMATCH, UPI_R.BUSY_TYME , UPI_R.TSF, UPI_R.NUM_RX_MATCH] }
            result = controller.delay(5).radio.get_monitor(UPI_myargs)
            controller.send_upstream({"myResult": result})

    print("Local ctrl program stopped: {}".format(controller.name))