#!/usr/bin/env python3

__author__ = 'domenico'
import time
import sys
import datetime
import logging
import gevent
import yaml


#import wishful_upis as upis
import wishful_controller

#help('modules')
#time.sleep(5)

print("import0")


controller = wishful_controller.Controller()
#
# controller.add_module(moduleName="wireless_topology", pyModuleName="wishful_module_wireless_topology ",
#                           className="WirelessTopologyModule", importAs="wireless_topology")

print("import1")

pyModule = __import__('wishful_module_wireless_topology')

print("import2")

pyModule_2 = __import__('luca')


#globals()[module_name] = pyModule


