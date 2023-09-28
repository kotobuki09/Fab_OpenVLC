__author__ = "Adant Technologies Inc."
__copyright__ = "Copyright (c) 2016, Adant Technologies Inc."
__version__ = "1.0.0"
__email__ = ""
__status__ = "Final"

'''SmartAntenna driver family
'''
import serial
import logging
import time

EXIT_SUCCESS = 0
EXIT_FAILURE = -1
ERROR_UNSYNC = -2

WISHFUL_MODE = "w"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smartantenna")

HW_ID = "0403:6010"  # vendor and product id
DEV_PRODUCT = "AD-WSFL-U"
DEV_MANUFACTURER = "Adant"
DEV_WELCOME = b'-- WiSHFUL UART RECEIVER --'
DEV_SERIAL = 'ADK1EVUB'
BAUDRATE = 115200

class Controller():
    def __init__(self):
        import serial.tools.list_ports
        devices = []
        for dev in serial.tools.list_ports.grep(HW_ID):
            requirements = ((dev.manufacturer == DEV_MANUFACTURER
                             and dev.product == DEV_PRODUCT)
                            or dev.serial_number == DEV_SERIAL)
            if not requirements:
                logging.debug("Ignoring serial device with same Hardware ID but missing requirements:\n"
                              "\tManufacturer:%s\n"
                              "\tProduct:%s", dev.manufacturer, dev.product)
                continue
            else:
                # Test the device connection
                with serial.Serial(dev.device, BAUDRATE,
                                   write_timeout=1,
                                   timeout=1) as ser:
                    ser.write(b'x')
                    response = ser.readline()
                    if DEV_WELCOME in response:
                        # Correct device
                        devices.append(dev)
                    else:
                        logger.debug("Unexpecetd device response: %s",
                                     str(response))
        if not devices:
            self.dev = None
            logger.error("SmartAntenna controller %s not found!", DEV_PRODUCT)
            for dev in serial.tools.list_ports.comports():
                logger.error("%s", dev.description)
            raise Exception("SmartAntenna controller %s not found!", DEV_PRODUCT)
        for dev in devices:
            logger.info(DEV_PRODUCT + " found on " + dev.device)
        if len(devices) > 1:
            logger.error("MULTIPLE " + DEV_PRODUCT + " found!")
            raise Exception("Multiple " + DEV_PRODUCT + " found!")
        self.dev = devices[0]
        self.ser = serial.Serial()
        self.ser.port = dev.device
        self.ser.baudrate = BAUDRATE
        self.ser.timeout = 1
        self.ser.write_timeout = 2
        self.ser.xonxoff = True
        self.ser.open()
        logger.info("Connected to: " + self.ser.port)
        self.set_mode(WISHFUL_MODE)

    def set_mode(self, mode=WISHFUL_MODE):
        if mode == WISHFUL_MODE:
            self.ser.write(b'w')
            response = self.ser.readlines()
            status = any([b'WiSHFUL mode activated' in x for x in response])
            if status:
                logger.debug("Controller set in WISHFUL_MODE: %s", status)
            else:
                logger.warning("Unable to set controller in WISHFUL_MODE:\n"
                               "Response: %s:", response)
            return status

    def __del__(self):
        try:
            logger.info("Closing connection to: " + self.ser.port)
            self.ser.close()
        except AttributeError:
            pass


    def write_sequence(self, seq):
        if self.ser.is_open:
            self.ser.write(bytes(seq, 'utf8'))
            time.sleep(0.5)
            response = self.ser.read_all()
            logger.debug(str(response))
            if not ("successful command received" in str(response)):
                logger.warning(str(response))

    def test_leds(self):
        """ Test proper LED functionality

        :return: None
        """
        logger.info("Starting test led mode...")
        sequence = [[1, 0, 0, 0], [0, 1, 0, 0],
                    [0, 0, 1, 0], [0, 0, 0, 1],
                    [0, 0, 0, 0]]
        delay = 0.25
        for band in [2, 5]:
            for a1, a2, a3, a4 in sequence:
                self.set_sas_conf(band, a1, a2, a3, a4)
                time.sleep(delay)
        #reverse
        for band in [5, 2]:
            for a4, a3, a2, a1 in sequence:
                self.set_sas_conf(band, a1, a2, a3, a4)
                time.sleep(delay)


    def set_sas_conf(self, band, conf_ant1, conf_ant2, conf_ant3, conf_ant4):
        """ Set the configuration for each smart-antenna

        :param band: (int) WiFi band, 2 or 5
        :param conf_ant1: (int) direction for antenna 1
        :param conf_ant2: (int) direction for antenna 2
        :param conf_ant3: (int) direction for antenna 3
        :param conf_ant4: (int) direction for antenna 4
        :return:
        """
        antennas = [conf_ant1, conf_ant2, conf_ant3, conf_ant4]
        # Validate
        if not self.ser.is_open:
            logger.error("Impossible to set_sas_conf")
            logger.error("Connection not available")
            return -1
        if not band in [2, 5]:
            logger.error("Impossible to set_sas_conf")
            logger.error("Unexpceted band value: %s", str(band))
            return -2
        try:
            if not all([a >= 0 and a <= 8 for a in antennas]):
                logger.error("Impossible to set_sas_conf")
                logger.error("Unexpceted antennas value: %s", str(antennas))
                return -3
        except TypeError:
            logger.error("Impossible to set_sas_conf")
            logger.error("Unexpceted antenna type (must be int): %s", str(antennas))
            return -4
        else:
            logger.debug("Input command: %s, %s", str(band), str(antennas))

        command = "W" + str(band) + "".join([str(x) for x in antennas]) + "t"
        return self.write_sequence(command)

    def reset_controller(self):
        """ Reset the controller serial interface.
        This function is sometimes blocking.

        :return: (bool) the serial interface status
        """
        logger.debug("Resetting the controller...")
        self.ser.close()
        logger.debug("Wait one sec...")
        time.sleep(1)
        logger.debug("Open again")
        self.ser.open()
        return self.ser.is_open

