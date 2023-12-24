import logging
import random
import sys
import time
from .wishful_module import *

__author__ = "Piotr Gawlowicz, Mikolaj Chwalisz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, chwalisz}@tkn.tu-berlin.de"


class ControllerModule(WishfulModule):
    def __init__(self, controller):
        super(ControllerModule, self).__init__()
        self.controller = controller

    def set_controller(self, controller):
        self.controller = controller

    def send_to_module(self, msgContainer):
        self.log.debug("Module {} received cmd".format(self.__class__.__name__))
        pass