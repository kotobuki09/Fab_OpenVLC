#!/usr/bin/env python2.6

__author__ = 'Gawlowicz,Zubow'

import time
import operator
from stream import ThreadedFeeder, repeatcall, seq, takewhile, dropwhile, maximum, take, filter, map, item
from random import randint
from collections import deque
import itertools
from itertools import islice

import threading
from Queue import Queue

from scapy.all import *
"""
http://www.trinhhaianh.com/stream.py/
"""

def myPrint1(x):
    #print("Before:", x)
    return x

def myPrint2(x):
    #print("After",x)
    return x

def myPrint3(x):
    #print("MOV",x)
    return x




def get_packet():
  packet = 1
  return packet

def get_RSSI():
  next_rssi = randint(0, 100)
  #print next_rssi
  return next_rssi


def one_out_of_n(x, threshold=16):
    if x >= threshold:
        return True
    else:
        return False

def bigVals(x, threshold=16):
    if x >= threshold:
        return True
    else:
        return False


class PacketGenerator(object):
    def __init__(self, iface="eth0", pfilter="icmp", field_selector=None):
        self._stop = False
        self.queue = Queue.Queue()


        header = field_selector.split(".")
        selector_str = "{}:%{}%".format(header[0],field_selector)
        selector_str = "{" +selector_str+"}"

        self.selector_func = lambda x:x.sprintf(selector_str)
        #self.worker = threading.Thread(target=sniff, args=(iface, self.ip_monitor_callback, pfilter))
        self.worker = threading.Thread(target=sniff, kwargs={"iface":iface, "prn":self.ip_monitor_callback, "filter":pfilter})
        
        self.worker.setDaemon(True)
        self.worker.start()
        
    def ip_monitor_callback(self, pkt):
        self.queue.put(pkt)

    def stop(self):
        self._stop = True

    def __call__( self):
        while not self._stop:
          try:
            pkt = self.queue.get(block=True, timeout=0.5)
            #field selector
            #TODO: check if field exist
            value = self.selector_func(pkt)
            yield value
          except Queue.Empty:
            pass
          except KeyboardInterrupt as e:
            sys.exit()

        
class Generator(object):
    def __init__(self, sample_interval=1):
        self._stop = False
        self.sample_interval = sample_interval

    def stop(self):
        self._stop = True

    def __call__( self):
        while not self._stop:
          # perform UPI call
          next_rssi = get_RSSI()
          yield next_rssi
          time.sleep(self.sample_interval)


class DataFilter(object):
    def __init__(self, length=5):
        self.length = length
        self.samples = deque()

    def add_filter(self, dfilter):
      pass

    def __call__(self, sample):
      sample = int(sample)
      self.samples.append(sample)
      #print self.samples
            
      if len(self.samples) == self.length:
          s = sum(self.samples)
          self.samples.popleft()
          return s / self.length

class MovAvg(object):
    def __init__(self, length=5):
        self.length = length
        self.samples = deque()

    def __call__(self, sample):
      sample = int(sample) 
      self.samples.append(sample)
      #print self.samples
            
      if len(self.samples) == self.length:
          s = sum(self.samples)
          self.samples.popleft()
          return s / self.length


def notify_ctrl(x):
  print "notify_ctrl",x
  pass


class MyRule(threading.Thread):
    def __init__(self, rtype):
        super(MyRule, self).__init__()
        self.myGen = Generator(0.1)
        self.type = rtype

    def stop(self):
        self.myGen.stop()

    def run( self ):
      if self.type == "TRANSIENT":
        sink = item[:1]
      else:
        sink = min

      dataFilter = MovAvg(10)
      nop = map(myPrint1)
      elements = [nop, nop, nop, nop, nop]

      elements[0] = map(myPrint1)
      elements[1] = map(lambda x: dataFilter(x)) 
      elements[2] = filter(lambda x: bigVals(x, 40))
      elements[3] = map(notify_ctrl)
    
      self.myGen() >> elements[0] >> elements[1] >> elements[2] >> elements[3] >> elements[4] >> sink 


class MyPktRule(threading.Thread):
    def __init__(self, rtype, iface="wlan0", pfilter="icmp", field_selector="IP.ttl"):
        super(MyPktRule, self).__init__()
        self.myGen = PacketGenerator(iface, pfilter, field_selector)
        self.type = rtype

    def stop(self):
        self.myGen.stop()

    def run( self ):
      if self.type == "TRANSIENT":
        sink = item[:1]
      else:
        sink = min

      dataFilter = MovAvg(10)
      nop = map(myPrint1)
      elements = [nop, nop, nop, nop, nop]

      elements[0] = map(myPrint1)
      elements[1] = map(lambda x: dataFilter(x)) 
      elements[2] = filter(lambda x: bigVals(x, 40))
      elements[3] = map(notify_ctrl)
    
      try:
        self.myGen() >> elements[0] >> elements[1] >> elements[2] >> elements[3] >> elements[4] >> sink 
      except Exception as e:
        pass




if __name__ == '__main__':
  f = lambda x: x*x
  #bigVals = lambda x: x < 16
  validRssi = lambda x: x<=63 and x>=0

  print "START"
  if 1:
    thread = None
    try:
      thread = MyPktRule("P", iface="eth0", pfilter="icmp", field_selector="IP.ttl")
      thread.deamon = True
      thread.start()

      while 1:
        time.sleep(1)

    except KeyboardInterrupt as e:
      print e

    except Exception as e:
      print e

    finally:
      thread.stop()
      thread.join()
      print "DONE"

  if 0:
    pktGen = PacketGenerator(iface="wlan0", pfilter="icmp", field_selector="IP.ttl")

    try:
      for value in pktGen():
        print "Field value: ", value

    except Exception as e:
        pass
    finally:
      pktGen.stop()
