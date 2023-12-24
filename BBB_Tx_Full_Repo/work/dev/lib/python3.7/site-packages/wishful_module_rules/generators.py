import logging
import threading
import time
import queue
from wishful_framework import CmdDesc


__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz}@tkn.tu-berlin.de"


class UpiEventGenerator(object):
    def __init__(self, agent, eventDesc):
        self.log = logging.getLogger('UpiEventGenerator')
        self._stop = False
        self.agent = agent
        self.eventDesc = eventDesc

    def stop(self):
        self._stop = True

    def __call__(self):
        cmdDesc = CmdDesc()
        cmdDesc.type = self.eventDesc.upi_type
        cmdDesc.func_name = self.eventDesc.upi_func
        cmdDesc.call_id = str(0)
        cmdDesc.interface = self.eventDesc.iface
        kwargs = self.eventDesc.kwargs
        msgContainer = ["agent", cmdDesc, kwargs]

        #check if UPI is implemented as generator
        myModule = self.agent.moduleManager.get_module(msgContainer)
        myGenerator = self.agent.moduleManager.get_generator(msgContainer)
        if myModule and myGenerator:
            #if there is function that has to be called before generator function, call it
            self.log.info("Prepare UPI generator".format())
            myModule.before_call(msgContainer)

            gen = myGenerator()
            while not self._stop:
                next_sample = next(gen)
                self.log.debug("Next sample{}".format(next_sample))
                yield next_sample
                if self._stop:
                    self.log.info("UPI Generator break".format())
                    break

            #if there is function that has to be called after generator function, call it
            self.log.info("Kill UPI generator".format())
            myModule.after_call(msgContainer)

        else:
            while not self._stop:
              # perform UPI call
              response = self.agent.moduleManager.send_cmd_to_module_blocking(msgContainer)
              next_sample = response[2]
              self.log.debug("Next sample{}".format(next_sample))
              yield next_sample
              if self._stop:
                self.log.info("UPI Generator break".format())
                break
              time.sleep(self.eventDesc.interval)


class PacketGenerator(object):
    def __init__(self, iface, pfilter=None, field_selector=None):
        self.log = logging.getLogger('PacketGenerator')
        self.log.info("start packet generator on iface: {}, packet filter: {}, field selector: {}".format(iface,pfilter,field_selector))
        self._stop = False
        self.queue = queue.Queue()

        self.iface = iface
        self.pfilter = pfilter
        self.field_selector = field_selector
        self.selector_func = None
        
        if field_selector:
            self.selector_func = self.create_selector_func(field_selector)

    def create_selector_func(self, field_selector):
        header = field_selector.split(".")
        selector_str = "{}:%{}%".format(header[0],field_selector)
        selector_str = "{" +selector_str+"}"
        selector_func = lambda x:x.sprintf(selector_str)
        return selector_func

    def stop(self):
        self._stop = True

    def pkt_recv_callback(self, pkt):
        if not self._stop:
            self.queue.put(pkt)

    def __call__( self):
        while not self._stop:
            try:
                pkt = self.queue.get(block=True, timeout=0.5)
                if self.selector_func:
                    value = self.selector_func(pkt)
                    self.log.debug("Next sample for selector: {} - {}".format(self.field_selector, value))
                    yield value
                else:
                    self.log.debug("Next pkt".format())
                    yield pkt

                if self._stop:
                    self.log.info("PKT Generator break".format())
                    break
            except queue.Empty: 
              pass