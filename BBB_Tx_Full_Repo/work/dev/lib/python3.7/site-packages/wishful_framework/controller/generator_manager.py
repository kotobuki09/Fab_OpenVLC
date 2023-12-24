import logging
import queue
import gevent.queue
from wishful_framework import TimeEvent, PktEvent, MovAvgFilter, PeakDetector, Match, Action, Permanance

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


class GeneratorDescriptor(object):
    def __init__(self, genManager, agentUuid, genId, event, filters=[], match=None,):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))
        self.agentUuid = agentUuid
        self.id = genId
        self.genManager = genManager
        self.event = event
        self.filters = filters
        self.match = match

        self._stop = False
        self.sampleQueue = gevent.queue.Queue()

    def __iter__(self):
        return self

    def __next__(self):
        if not self._stop:
            try:
                return self.sampleQueue.get()
            except Exception as e:
                raise e
        else:
            raise StopIteration()

    def receive_sample(self, sample):
        self.sampleQueue.put(sample)

    def stop(self):
        self._stop = True
        return self.genManager.stop(self.id, self.agentUuid)


class GeneratorManager(object):
    def __init__(self, controller):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))

        self.controller = controller
        self.generatorIdGen = 0
        self.generators_by_node = {}


    def generate_new_generator_id(self):
        self.generatorIdGen = self.generatorIdGen + 1
        return self.generatorIdGen


    def _receive(self, group, node, msg):
        node_uuid = msg["node_uuid"]
        generator_id = msg["rule_id"]
        sample = msg["msg"]

        node_generators = []
        if node_uuid in self.generators_by_node:
            node_generators = self.generators_by_node[node_uuid]

        myGenerator = None
        for generator in node_generators:
            if generator_id == generator.id:
                myGenerator = generator
                break

        if myGenerator:
            myGenerator.receive_sample(sample)


    def start(self, event, pktMatch=None, selector=None, filters=[], match=None):
        self.log.debug("Adding new generator to node".format())

        destNode = self.controller._scope
        destNode = self.controller.nodeManager.get_node_by_str(destNode)
        destNodeUuid = destNode.id

        #TODO: improve serialization
        generator = {"event":event, "pktMatch":pktMatch, "selector":selector, "filters":filters, 
                     "match":match, "action":None, "permanence":Permanance.PERSISTENT, "notify_ctrl":True, "generator":True}

        generator_id = self.controller.blocking(True).mgmt.add_rule(generator)
        descriptor = GeneratorDescriptor(self, destNodeUuid, generator_id, event, filters, match)

        if destNodeUuid in self.generators_by_node:
            self.generators_by_node[destNodeUuid].append(descriptor)
        else:
            self.generators_by_node[destNodeUuid] = [descriptor]

        return descriptor


    def stop(self, generator_id, agentUuid=None):
        self.log.debug("Remove generator with id: {}".format(generator_id))

        if agentUuid in self.generators_by_node:
            myGenerator = None
            for generator in self.generators_by_node[agentUuid]:
                if generator_id == generator.id:
                    myGenerator = generator
                    break

            if myGenerator:
                self.generators_by_node[agentUuid].remove(myGenerator)
                del myGenerator

        if agentUuid:
            retVal = self.controller.blocking(True).node(agentUuid).mgmt.delete_rule(generator_id)
        else:
            retVal = self.controller.blocking(True).mgmt.delete_rule(generator_id)
        return retVal


class LocalGeneratorDescriptor(object):
    def __init__(self, genManager, genId, event, filters=[], match=None):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))
        self.id = genId
        self.genManager = genManager
        self.event = event
        self.filters = filters
        self.match = match

        self._stop = False
        self.sampleQueue = queue.Queue()

    def __iter__(self):
        return self

    def __next__(self):
        if not self._stop:
            try:
                return self.sampleQueue.get()
            except Exception as e:
                raise e
        else:
            raise StopIteration()

    def receive_sample(self, sample):
        self.sampleQueue.put(sample)

    def stop(self):
        self._stop = True
        return self.genManager.stop(self.id)


class LocalGeneratorManager(object):
    def __init__(self, controller):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))

        self.controller = controller
        self.generatorIdGen = 0
        self.generators = []

    def generate_new_generator_id(self):
        self.generatorIdGen = self.generatorIdGen + 1
        return self.generatorIdGen

    def _receive(self, msg):
        node_uuid = msg["node_uuid"]
        generator_id = msg["rule_id"]
        sample = msg["msg"]

        myGenerator = None
        for generator in self.generators:
            if generator_id == generator.id:
                myGenerator = generator
                break

        if myGenerator:
            myGenerator.receive_sample(sample)


    def start(self, event, pktMatch=None, selector=None, filters=[], match=None):
        self.log.debug("Adding new generator to node".format())

        generator = {"event":event, "pktMatch":pktMatch, "selector":selector, "filters":filters, 
                "match":match, "action":None, "permanence":Permanance.PERSISTENT, "notify_ctrl":True, "generator":True,
                "LocalControllerId":self.controller.id}

        generator_id = self.controller.blocking(True).mgmt.add_rule(generator)
        descriptor = LocalGeneratorDescriptor(self, generator_id, event, filters, match)
        self.generators.append(descriptor)

        return descriptor


    def stop(self, generatorId):
        self.log.debug("Stop generator with id: {}".format(generatorId))

        myGenerator = None
        for generator in self.generators:
            if generatorId == generator.id:
                myGenerator = generator
                break

        if myGenerator:
            self.generators.remove(myGenerator)
            del myGenerator

        retVal = self.controller.blocking(True).mgmt.delete_rule(generatorId)
        return retVal