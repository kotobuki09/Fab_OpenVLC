import time
from scapy.all import Sink, SniffSource, PipeEngine

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz}@tkn.tu-berlin.de"


class MyPktSink(object):
    def __init__(self, name=None, field_selector=None, callback=None):
        self.name = name
        self.field_selector = field_selector
        self.callback = callback
        self.selector_func = None
        
        if field_selector:
            self.selector_func = self.create_selector_func(field_selector)

    def create_selector_func(self, field_selector):
        header = field_selector.split(".")
        selector_str = "{}:%{}%".format(header[0],field_selector)
        selector_str = "{" +selector_str+"}"
        selector_func = lambda x:x.sprintf(selector_str)
        return selector_func

    def recv(self, msg):
        if self.selector_func:
            msg = self.selector_func(msg)

        if self.callback:
            self.callback(msg)


class PacketSinkAggregator(Sink):
    def __init__(self, source, name="PacketSinkAggregator"):
        Sink.__init__(self, name=name)
        self.source = source
        self._mySinks = []

    def push(self, msg):
        for sink in self._mySinks:
            sink.recv(msg)

    def high_push(self, msg):
        for sink in self._mySinks:
            sink.recv(msg)

    def get_active_sink_number(self):
        return len(self._mySinks)

    def add_sink(self, sink, field_selector=None):
        self._mySinks.append(sink)

    def remove_sink(self, sink):
        if sink in self._mySinks:
            self._mySinks.remove(sink)


class PacketSniffer():
    def __init__(self, iface=None, pfilter=None, name="MyPacketSource"):
        self.iface = iface
        self.filter = pfilter
        self.name = name
        self._running = False

        self.source = SniffSource(iface=iface, filter=pfilter, name=name)
        self.sink = PacketSinkAggregator(source=self, name="PacketSinkAggregator")

        self.source > self.sink

        self.engine = PipeEngine(self.source)

    def _start(self):
        self._running = True
        self.engine.start()

    def _stop(self):
        self._running = False
        self.engine.stop()

    def isrunning(self):
        return self._running

    def add_sink(self, sink):
        self.sink.add_sink(sink)
        if self.sink.get_active_sink_number() and not self.isrunning():
            self._start()

    def remove_sink(self, sink):
        self.sink.remove_sink(sink)
        if self.sink.get_active_sink_number() == 0 and self.isrunning():
            self._stop()



if __name__ == "__main__":
    source = PacketSniffer(iface='wlan0', pfilter="icmp")
    ttlCb = lambda x: print("TTL:",x)
    dstCb = lambda x: print("DST:",x)
    pktCb = lambda x: x.show()

    myTtlSink = MyPktSink(name="ttlSink", field_selector="IP.ttl", callback=ttlCb)
    myDstSink = MyPktSink(name="dstSink", field_selector="IP.dst", callback=dstCb)
    myPktSink = MyPktSink(name="PktSink", callback=pktCb)

    print("SILENCE")
    time.sleep(5)

    print("Start TTL ")
    source.add_sink(myTtlSink)
    time.sleep(10)
    source.remove_sink(myTtlSink)

    print("SILENCE")
    time.sleep(5)

    print("Start PKT")
    source.add_sink(myPktSink)
    time.sleep(10)
    source.remove_sink(myPktSink)

    print("SILENCE")
    time.sleep(5)

    print("Start TTL and DST")
    source.add_sink(myTtlSink)
    source.add_sink(myDstSink)
    time.sleep(10)

    print("Remove DST")
    source.remove_sink(myDstSink)
    time.sleep(10)

    print("Remove DST")
    source.remove_sink(myTtlSink)

    print("SILENCE")
    time.sleep(10)

    print("DONE")
