#!/usr/bin/env python3

import os
import time
import xmlrpc.client
import subprocess

'''
    Run-time control of meta radio program which allows very fast switching from
    one protocol to another:
    - context switching
'''

__author__ = "A. Zubow"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{zubow}@tkn.tu-berlin.de"

START_GNURADIO = False

if __name__ == '__main__':

    if START_GNURADIO:
        gr_process_io = {'stdout': open('/tmp/gnuradio.log', 'w+'), 'stderr': open('/tmp/gnuradio-err.log', 'w+')}
        gr_process = subprocess.Popen(["env", "python2", '../testdata/top_block.py'],
                                           stdout=gr_process_io['stdout'], stderr=gr_process_io['stderr'])
        time.sleep(1)

    # open proxy
    proxy = xmlrpc.client.ServerProxy("http://localhost:8080/")

    # load metadata
    proto_usrp_src_dicts = eval(open('../testdata/proto_usrp_src_dicts.txt', 'r').read())
    usrp_source_fields = eval(open('../testdata/usrp_source_fields.txt', 'r').read())

    # main control loop
    while True:
        res = getattr(proxy, "get_session_var")()

        print('Current proto: %s' % str(res))

        last_proto = res[0]
        last_proto = (last_proto + 1) % 2

        # read variables of new protocol
        init_session_value = []
        init_session_value.append(last_proto)
        for field in usrp_source_fields:
            res = getattr(proxy, "get_%s" % proto_usrp_src_dicts[last_proto][field])()
            init_session_value.append(float(res))

        print('Switch to protocol %d with cfg %s' % (last_proto, str(init_session_value)))
        getattr(proxy, "set_session_var")(init_session_value)

    if START_GNURADIO:
        gr_process.kill()