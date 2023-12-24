#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from module_rs_signal_gen import RsSignalGen
import os
import time

if __name__ == '__main__':

    rs = RsSignalGen()

    iface = '192.168.200.35'
    freq = '5200'
    power_lvl = 0
    rs.play_waveform(iface, freq, power_lvl)

    time.sleep(5)

    rs.stop_waveform(iface)