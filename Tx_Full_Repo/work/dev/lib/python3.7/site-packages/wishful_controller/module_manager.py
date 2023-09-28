import logging
import subprocess
import zmq.green as zmq
import random
import wishful_framework as msgs

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"

class ModuleManager(object):
    def __init__(self, controller):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))

        self.controller = controller
        self.moduleIdGen = 0
        self.ifaceIdGen = 0
        
        self.discoveryModule = None
        self.modules = {}
        self.interfaces = {}
        self.iface_to_module_mapping = {}
        self.modules_without_iface = []


    def my_import(self, module_name):
        pyModule = __import__(module_name)
        globals()[module_name] = pyModule
        return pyModule


    def generate_new_module_id(self):
        newId = self.moduleIdGen
        self.moduleIdGen = self.moduleIdGen + 1
        return newId


    def generate_new_iface_id(self):
        newId = self.ifaceIdGen
        self.ifaceIdGen = self.ifaceIdGen + 1
        return newId


    def start(self):
        self.log.debug("Notify START to modules".format())
        for module in list(self.modules.values()):
            module.start()


    def exit(self):
        self.log.debug("Notify EXIT to modules".format())
        for module in list(self.modules.values()):
            module.exit()


    def connected(self):
        self.log.debug("Notify CONNECTED to modules".format())
        for module in list(self.modules.values()):
            module.connected()

    def disconnected(self):
        self.log.debug("Notify DISCONNECTED to modules".format())
        for module in list(self.modules.values()):
            module.disconnected()


    def get_iface_id(self, name):
        for k,v in self.interfaces.items():
            if v == name:
                return k

        return None


    def add_module_obj(self, moduleName, wishfulModule):
        moduleId = self.generate_new_module_id()
        wishfulModule.id = moduleId

        self.modules[moduleId] = wishfulModule

        if moduleName == "discovery":
            self.discoveryModule = wishfulModule

        return wishfulModule


    def add_module(self, moduleName, pyModuleName, className, kwargs):
        self.log.debug("Add new module: {}:{}:{}".format(moduleName, pyModuleName, className))

        pyModule = self.my_import(pyModuleName)
        moduleContructor = getattr(pyModule, className)
        wishfulModule = moduleContructor(self.controller, **kwargs)
        return self.add_module_obj(moduleName, wishfulModule)
