#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from module_gnuradio import GnuRadioModule
import os
import time

if __name__ == '__main__':

    grm = GnuRadioModule()

    rps = ['t1', 't2']

    if True:
        print('load radio programs')
        for rp in rps:
            fid = open(os.path.join(os.path.expanduser("."), "testdata", rp + ".grc"))
            grc_xml = fid.read()
            #print(grc_xml)

            inval = {}
            inval['grc_radio_program_name'] = rp
            inval['grc_radio_program_code'] = grc_xml

            grm.add_program(**inval)

    meta_rp_fname = None
    if True:
        print('Merge the radio programs into one meta program')

        inval = {}
        inval['grc_radio_program_names'] = rps
        meta_rp_fname = grm.merge_programs(**inval)
        meta_rp_fname = meta_rp_fname.replace('.grc', '')

    if True:
        print('Activate meta radio program')

        inval = {}
        inval['grc_radio_program_name'] = meta_rp_fname
        inval['grc_radio_program_code'] = None

        grm.set_active(**inval)

    if True:
        time.sleep(5)
        print('Switch to radio program %s' % rps[1])
        grm.switch_program(rps[1])

        time.sleep(10)
        print('Switch to radio program %s' % rps[0])
        grm.switch_program(rps[0])

    if False:
        print('remove radio programs')
        for rp in rps:
            inval = {}
            inval['grc_radio_program_name'] = rp
            grm.remove_program(**inval)


    #grm.set_active(**inval)
    #grm.set_inactive(**tvals)