#!/usr/bin/env python2.6

__author__ = 'zubow'

import time
import operator
from stream import ThreadedFeeder, repeatcall, seq, takewhile, dropwhile, maximum, take, filter, map
from random import randint
from collections import deque
import itertools
from itertools import islice



"""
http://www.trinhhaianh.com/stream.py/
"""

def get_RSSI():
  next_rssi = randint(0, 100)
  #print next_rssi
  return next_rssi

def get_streaming_RSSI(sample_interval=0.05, num_samples=100):
   for ii in range(num_samples):
      time.sleep(sample_interval)
      # perform UPI call
      next_rssi = get_RSSI()
      yield next_rssi

def bigVals(x, threshold=16):
    if x >= threshold:
        return False
    else:
        return True

def moving_average(iterator, length):
    d = deque(islice(iterator, 0, length))
    s = sum(d)
    yield s / length
    for i in iterator:
        s -= d.popleft()
        s += i
        d.append(i)
        yield s / length

if __name__ == '__main__':
  f = lambda x: x*x
  #print ThreadedFeeder(get_streaming_RSSI) >> map(f) >> sum
  #bigVals = lambda x: x < 16
  validRssi = lambda x: x<=63 and x>=0

  #print ThreadedFeeder(get_streaming_RSSI) >> dropwhile(bigVals) >> list
  print ThreadedFeeder(get_streaming_RSSI) >> filter(validRssi) >> maximum(lambda x: x)
  #print ThreadedFeeder(get_streaming_RSSI) >> filter(validRssi) >> sum


  #for i in itertools.count():
  #   print i
  #   time.sleep(0.01)

  #for i in iter(int, 1):
  #  print i
  #  time.sleep(0.1)