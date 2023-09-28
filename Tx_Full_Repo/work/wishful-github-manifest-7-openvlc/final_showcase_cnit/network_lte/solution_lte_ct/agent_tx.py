#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GNURadio Agent: Example tutorial of WiSHFUL (agent side)

Usage:
   wishful_simple_agent [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --config configFile Config file path

Example:
   ./wishful_example_tutorial_agent -v --config ./tx.yaml
   ./wishful_example_tutorial_agent -v --config ./rx.yaml

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""

import logging
import signal
import sys, os
import yaml

sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')
sys.path.append("../../../agent_modules/wifi_ath")
sys.path.append("../../../agent_modules/wifi_wmp")
sys.path.append("../../../agent_modules/wifi")
sys.path.append("../../../agent_modules/iperf")
sys.path.append("../../../agent_modules/net_linux")
sys.path.append('../../../upis')
sys.path.append('../../../framework')
sys.path.append('../../../agent')
sys.path.append("../../../agent_modules/module_srslte/")


import wishful_upis as upis
import wishful_agent

__author__ = "Maicon Kist"
__copyright__ = "Copyright (c) 2017 Connect Centre - Trinity College Dublin" 
__version__ = "0.1.0"
__email__ = "kistm@tcd.ie"

"""
Setting of agent node
"""
agent_PC_interface = "eth0"
"""
END setting of agent node
"""


""" START WiSHFUL agent setting """
"""
The WiSHFUL controller module is the core module of the WiSHFUL framework and allow all the basics functions
such as the node discovery, the UPI functions execution on local and remote node, perform the messages exchange between
global control program and local control program, and all the other management functions of the framework. The different
works of the controller are  performed by different module can be added on demand in the controller
"""
#Create agent
agent = wishful_agent.Agent()

#Configure agent, we specify in the parameters the controller name and a string information related to the
#controller
agent.set_agent_info(name="ENB", info="Example tutorial Agent", iface=agent_PC_interface)


#the following rows add all the needed modules to the controller

#add the discovery module, responsable for the nodes discovery procedure
#we specify interface and the name of the nodes group

agent.add_module(moduleName="discovery", pyModule="wishful_module_discovery_pyre",
                 className="PyreDiscoveryAgentModule", kwargs={"iface":agent_PC_interface, "groupName":"network_lte_cnit"})

#add the srs_lte module,
agent.add_module(moduleName="srslte", pyModule="wishful_module_srslte", className="SrslteModule")

#add the net_linux module,
agent.add_module(moduleName="network", pyModule="wishful_module_net_linux", className="NetworkModule")

#add the iperf module,
#agent.add_module(moduleName="iperf", pyModule="wishful_module_iperf", className="IperfModule")

""" END WiSHFUL agent setting """


""" START Define logging controller """
""" we use the python logging system module (https://docs.python.org/2/library/logging.html) """

#set the logging name
log = logging.getLogger('wishful_agent')

""" END Define logging controller """


if __name__ == "__main__":
    try:
        from docopt import docopt
    except:
        print("""
        Please install docopt using:
            pip install docopt==0.6.1
        For more refer to:
        https://github.com/docopt/docopt
        """)
        raise

    #get program arguments
    args = docopt(__doc__, version=__version__)

    #set the logging level by argument parameters
    log_level = logging.INFO  # default
    if args['--verbose']:
        log_level = logging.DEBUG
    elif args['--quiet']:
        log_level = logging.ERROR

    #set the logging format
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

    try:
        #Start agent
        agent.run()
    except KeyboardInterrupt:
        log.debug("Agent exits")
    finally:
        log.debug("Exit")
        agent.stop()
