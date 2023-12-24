__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


#simple classes that do not contain ctypes pointers and can be pickled
class SimpleMatch(object):
    def __init__(self, match):
        self.name = match.name

class SimpleTarget(object):
    def __init__(self, target):
        self.name = target.name

class SimplePolicy(object):
    def __init__(self, policy):
        self.name = policy.name

class SimpleRule(object):
    def __init__(self, rule):
        self.protocol = rule.protocol
        self.src = rule.src
        self.dst = rule.dst
        self.in_interface = rule.in_interface
        self.out_interface = rule.out_interface
        self.fragment = rule.fragment

        (packets, byte) = rule.get_counters()
        self.pktCounter = packets
        self.byteCounter = byte

        self.matches = []
        for match in rule.matches:
            self.matches.append(SimpleMatch(match))

        self.target = SimpleTarget(rule.target)

class SimpleChain(object):
    def __init__(self, chain):
        self.name = chain.name

        (packets, byte) = chain.get_counters()
        self.pktCounter = packets
        self.byteCounter = byte

        self.rules = []
        for rule in chain.rules:
            self.rules.append(SimpleRule(rule))

class SimpleTable(object):
    def __init__(self, table):
        self.name = table.name
        self.chains = []
        for chain in table.chains:
            self.chains.append(SimpleChain(chain))