#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
global_controller.py: Global WiSHFUL controller illustrating
the use of generators.

Usage:
   global_controller.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --config configFile Config file path

Example:
   ./global_controller -v --config ./config.yaml

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""

import sys
import datetime
import logging
import wishful_controller
import gevent
import yaml
import random
import time
from scapy.all import *
import wishful_upis as upis
from wishful_framework import TimeEvent, PktEvent, MovAvgFilter, PeakDetector, Match, Action, Permanance, PktMatch, FieldSelector


__author__ = "Piotr Gawlowicz, Anatolij Zubow"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"


log = logging.getLogger('wishful_controller.main')
controller = wishful_controller.Controller()
nodes = []


@controller.new_node_callback()
def new_node(node):
    nodes.append(node)
    print("New node appeared:")
    print(node)


@controller.node_exit_callback()
def node_exit(node, reason):
    if node in nodes:
        nodes.remove(node);
    print("NodeExit : NodeName : {} Reason : {}".format(node.name, reason))


@controller.set_default_callback()
def default_callback(group, node, cmd, data):
    print("DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(group, node.name, cmd, data))


def main(args):
    log.debug(args)

    config_file_path = args['--config']
    config = None
    with open(config_file_path, 'r') as f:
        config = yaml.load(f)

    controller.load_config(config)
    controller.start()

    # wait for at least one node
    while len(nodes) < 1:
        gevent.sleep(1)

    # control loop
    loop_cnt = 0
    update_ival = 1

    while True:
        print("Connected nodes", [str(node.name) for node in nodes])
        loop_cnt += 1

        if nodes:

            print("Controller loop: %d." % loop_cnt)

            csi = controller.node(nodes[0]).radio.iface("wlan0").receive_csi()
            print("Received CSI:")
            print(csi)

            gevent.sleep(update_ival)


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

    args = docopt(__doc__, version=__version__)

    log_level = logging.INFO  # default
    if args['--verbose']:
        log_level = logging.DEBUG
    elif args['--quiet']:
        log_level = logging.ERROR

    logfile = None
    if args['--logfile']:
        logfile = args['--logfile']

    logging.basicConfig(filename=logfile, level=log_level,
        format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

    try:
        main(args)
    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        controller.stop()