#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from module_gnuradio import GnuRadioModule
import os
import time

if __name__ == '__main__':

    grm = GnuRadioModule()

    fid = open(os.path.join(os.path.expanduser("."), "testdata", "testgrc.grc"))
    grc_xml = fid.read()

    #print(grc_xml)

    inval = {}
    inval['ID'] = 11
    inval['grc_radio_program_name'] = 'test'
    inval['grc_radio_program_code'] = grc_xml

    grm.set_active(**inval)

    time.sleep(2)
    if True:

        gvals = {}
        gvals['samp_rate'] = None
        gvals['freq'] = None

        for ii in range(5):
            res = grm.gnuradio_get_vars(**gvals)
            print(res)

    tvals = {}
    tvals['do_pause'] = str(True)
    grm.set_inactive(**tvals)