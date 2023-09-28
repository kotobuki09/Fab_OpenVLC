#!/usr/bin/env python3

import os
import time
import xmlrpc.client
import subprocess


def sigint_ignore():
    os.setpgrp()

if __name__ == '__main__':

    gr_process_io = {'stdout': open('/tmp/gnuradio.log', 'w+'), 'stderr': open('/tmp/gnuradio-err.log', 'w+')}

    gr_process = subprocess.Popen(["env", "python2", '/home/wifi/.wishful/radio/test/top_block.py'],
                                       stdout=gr_process_io['stdout'], stderr=gr_process_io['stderr'])

    time.sleep(1)

    proxy = xmlrpc.client.ServerProxy("http://localhost:8080/")

    k = 'samp_rate'
    res = getattr(proxy, "get_%s" % k)()

    print(res)

    gr_process.kill()