#!/usr/bin/python

__author__ = 'P.Gawlowicz'

from pytc.TrafficControl import TrafficControl
from pytc.Profile import Profile
import logging
import time, sys

if __name__ == '__main__':

    operation = "del"
    if len(sys.argv) > 1:
        operation = str(sys.argv[1])

    tcMgr = TrafficControl()
    wlan0 = tcMgr.getInterface('wlan0')

    if operation == "add":
        profile2G = Profile("profile2G")
        profile2G.setPacketLimit(1000)
        band_1Mbps = 1000 * 1024
        profile2G.setRate(band_1Mbps)
        profile2G.setDelay(delay=100, jitter=1)
        wlan0.setProfile(profile2G) 
    else:
        wlan0.clean()