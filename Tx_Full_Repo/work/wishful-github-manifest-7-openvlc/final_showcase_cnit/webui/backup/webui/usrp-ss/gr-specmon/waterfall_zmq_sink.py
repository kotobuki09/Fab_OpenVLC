"""
Plotting Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import datetime
import zmq
import json


class blk(gr.sync_block):
    """Waterfall ZMQ Sink

    It will send Waterfall plot data over ZMQ PUB socket.
    """

    def __init__(self,
            freq_Size=128,
            num_Samples=1000,
            msg_interval=1000,
            addr='tcp://localhost:5507'):
        """arguments to this function show up as parameters in GRC"""
        self.freq_size = freq_Size
        gr.sync_block.__init__(
            self,
            name='Waterfall ZMQ Sink',   # will show up in GRC
            in_sig=[(np.float32, freq_Size)],
            out_sig=None,
        )
        self.nsamples = num_Samples
        self.msg_interval = datetime.timedelta(milliseconds=msg_interval)
        self.rx_freq = None
        self.rx_rate = None
        self.done = False

        context = zmq.Context()
        self.sock = context.socket(zmq.PUB)
        self.sock_addr = addr
        self.sock_connected = False
        self.last_msg_time = datetime.datetime.now()

    def work(self, input_items, output_items):
        if not self.sock_connected:
            print('Connecting to {}'.format(self.sock_addr))
            self.sock.connect(self.sock_addr)
            self.sock_connected = True
        current_time = datetime.datetime.now()

        if ((current_time - self.last_msg_time)
                > datetime.timedelta(seconds=10)):
            return -1

        tags = self.get_tags_in_window(0, 0, self.nsamples)
        for tag in tags:
            tag = gr.tag_to_python(tag)
            if tag.key == 'rx_freq':
                self.rx_freq = tag.value
            if tag.key == 'rx_rate':
                self.rx_rate = tag.value
        # if (self.last_msg_time + self.msg_interval) > current_time:
        if self.done:
            self.done = False
            return len(input_items[0])
        if input_items[0].shape[0] == self.nsamples:
            self.send_message(input_items[0])
            self.last_msg_time = datetime.datetime.now()
            self.done = True
            return self.nsamples
        return 0

    def send_message(self, data):
        now = datetime.datetime.now()
        data = data.T
        l, w = data.shape
        info = {'l': l, 'w': w, 'fc': self.rx_freq, 'bw': self.rx_rate}
        full_msg = [
            b'gnuradio.spectrogram',
            json.dumps(info).encode('utf-8'),
            data.ravel().tobytes(),
        ]
        self.sock.send_multipart(full_msg)
        print('i: %s, p: %s %s' % (
            str(now - self.last_msg_time),
            str(datetime.datetime.now() - now),
            str(self.sock_connected),
        ))
