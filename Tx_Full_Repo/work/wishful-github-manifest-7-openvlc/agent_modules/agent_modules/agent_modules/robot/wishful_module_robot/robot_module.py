import logging
import random
import wishful_upis as upis
import wishful_framework as wishful_module

__author__ = "Johannes Kunkel"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "johannes.kunkel@campus.tu-berlin.de"


@wishful_module.build_module
class RobotModule(wishful_module.AgentModule):
    def __init__(self):
        super(RobotModule, self).__init__()
        self.log = logging.getLogger('RobotModule')
        self.position = [12,323]


    @wishful_module.bind_function(upis.context.get_node_position)
    def get_position(self):
        self.log.debug("Get Node Position".format())
        return self.position