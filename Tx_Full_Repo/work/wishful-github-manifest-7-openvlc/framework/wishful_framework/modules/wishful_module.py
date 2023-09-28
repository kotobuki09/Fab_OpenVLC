import logging
import random
import sys
import time
import threading
import wishful_framework as msgs
import collections

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


class discover_controller(object):
    def __init__(self, ):
        self.discover_controller = True

    def __call__(self, f):
        f._discover_controller = self.discover_controller
        return f


class run_in_thread(object):
    def __init__(self, ):
        self.create_new_thread = True

    def __call__(self, f):
        f._create_new_thread = self.create_new_thread
        return f


class generator(object):
    def __init__(self):
        self.generator = True

    def __call__(self, f):
        f._generator = self.generator
        return f


class on_start(object):
    def __init__(self, ):
        self.onStart = True

    def __call__(self, f):
        f._onStart = self.onStart
        return f


class on_exit(object):
    def __init__(self):
        self.onExit = True

    def __call__(self, f):
        f._onExit = self.onExit
        return f


class on_connected(object):
    def __init__(self):
        self.onConnected = True

    def __call__(self, f):
        f._onConnected = self.onConnected
        return f


class on_disconnected(object):
    def __init__(self):
        self.onDisconnected = True

    def __call__(self, f):
        f._onDisconnected = self.onDisconnected
        return f


class on_first_call_to_module(object):
    def __init__(self):
        self.onFirstCallToModule = True

    def __call__(self, f):
        f._onFirstCallToModule = self.onFirstCallToModule
        return f


class before_call(object):
    def __init__(self, function):
        self.beforeCall = function.__name__

    def __call__(self, f):
        f._beforeCall = self.beforeCall
        return f


class after_call(object):
    def __init__(self, function):
        self.afterCall = function.__name__

    def __call__(self, f):
        f._afterCall = self.afterCall
        return f


class bind_function(object):
    def __init__(self, upiFunc):
        fname = upiFunc.__name__
        self.upi_fname = set([fname])

    def __call__(self, f):
        f._upi_fname = self.upi_fname
        return f


def build_module(module_class):
    original_methods = module_class.__dict__.copy()
    for name, method in original_methods.items():
        if hasattr(method, '_upi_fname'):
            #add UPI alias for the function
            for falias in method._upi_fname - set(original_methods):
                setattr(module_class, falias, method)
    return module_class


class WishfulModule(object):
    def __init__(self):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))

        self.id = None
        self.name = self.__class__.__name__

        self.firstCallToModule = True

        #discover UPI function implementation and create capabilities list
        func_name = [method for method in dir(self) if isinstance(getattr(self, method), collections.Callable) and hasattr(getattr(self, method), '_upi_fname')]
        self.functions = {list(getattr(self, method)._upi_fname)[0] : method for method in func_name if not hasattr(getattr(self, method), '_generator')}
        self.functions = list(self.functions.keys())
        self.generators = {list(getattr(self, method)._upi_fname)[0] : method for method in func_name if hasattr(getattr(self, method), '_generator')}
        self.generators = list(self.generators.keys())
        self.capabilities = self.functions + self.generators

        #interface to be used in UPI functions, it is set before function call
        self.interface = None


    def set_agent(self, agent):
        pass


    def set_controller(self, controller):
        pass

    def get_functions(self):
        return self.functions

    def get_generators(self):
        return self.generators

    def get_capabilities(self):
        return self.capabilities


    def get_discovered_controller_address(self):
        #discover controller discovery function
        funcs = [method for method in dir(self) if isinstance(getattr(self, method), collections.Callable) and hasattr(getattr(self, method), '_discover_controller')]
        fname = funcs[0]
        func = getattr(self, fname)
        if func:
            return func()
        else:
            return


    def execute_function(self, func):
        create_new_thread = hasattr(func, '_create_new_thread')
        if create_new_thread:
            self.threads = threading.Thread(target=func, name="upi_func_execution_{}".format(func.__name__))
            self.threads.setDaemon(True)
            self.threads.start()
        else:
            func()


    def start(self):
        #discover all functions that have to be executed on start
        funcs = [method for method in dir(self) if isinstance(getattr(self, method), collections.Callable) and hasattr(getattr(self, method), '_onStart')]
        for fname in funcs:
            f = getattr(self, fname)
            self.execute_function(f)


    def exit(self):
        #discover all functions that have to be executed on exit
        funcs = [method for method in dir(self) if isinstance(getattr(self, method), collections.Callable) and hasattr(getattr(self, method), '_onExit')]
        for fname in funcs:
            f = getattr(self, fname)
            self.execute_function(f)


    def connected(self):
        #discover all functions that have to be executed on connected
        funcs = [method for method in dir(self) if isinstance(getattr(self, method), collections.Callable) and hasattr(getattr(self, method), '_onConnected')]
        for fname in funcs:
            f = getattr(self, fname)
            self.execute_function(f)


    def disconnected(self):
        #discover all functions that have to be executed on disconnected
        funcs = [method for method in dir(self) if isinstance(getattr(self, method), collections.Callable) and hasattr(getattr(self, method), '_onDisconnected')]
        for fname in funcs:
            f = getattr(self, fname)
            self.execute_function(f)


    def first_call_to_module(self):
        #discover all functions that have to be executed before first UPI function call to module
        funcs = [method for method in dir(self) if isinstance(getattr(self, method), collections.Callable) and hasattr(getattr(self, method), '_onFirstCallToModule')]
        for fname in funcs:
            f = getattr(self, fname)
            self.execute_function(f)