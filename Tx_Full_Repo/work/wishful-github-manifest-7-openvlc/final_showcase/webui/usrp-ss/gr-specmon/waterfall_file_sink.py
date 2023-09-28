"""
Plotting Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import pmt
from multiprocessing import Process
# from threading import Thread
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime
# import zmq

cmap = plt.get_cmap("viridis")


def gen_spectrogram(data, rx_freq=None, rx_rate=None):
    ax = plt.gca()
    time_size, freq_size = data.shape
    ax.imshow(
        data.T,
        cmap=cmap,
        aspect='auto',
        interpolation='nearest',
        # extent=(
        #     data.index[0],
        #     data.index[-1],
        #     data.columns[0],
        #     data.columns[-1]
        # ),
        origin='lower',
    )

    def y_freq(y, pos):
        result = (y + 1) * rx_rate/ freq_size - rx_rate / 2 + rx_freq
        result = result / 1e6
        return '{:,.0f}'.format(result)

    if rx_rate and rx_freq:
        ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(y_freq))
        ax.yaxis.set_minor_formatter(mpl.ticker.FuncFormatter(y_freq))
        ax.set_ylabel('Frequency (MHz)')
    fig = plt.gcf()
    fname = 'data/usrp_' + str(datetime.now())
    fig.savefig('test.png')
    fig.savefig(fname + '.png')
    np.savetxt(fname + '.csv', data, delimiter=',')

class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Waterfall Plot to File Sink

    It will plot Waterfall plot of `freq_size` and `num_Samples`.
    """

    def __init__(self, freq_Size=256, num_Samples=1000):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        self.freq_size = freq_Size
        gr.sync_block.__init__(
            self,
            name='Waterfall Plot to File Sink',   # will show up in GRC
            in_sig=[(np.float32, 256)],
            out_sig=None,
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.nsamples = num_Samples
        self.worker = Process()
        self.message_port_register_out(pmt.intern('drop'))
        self.drop = False
        self.rx_freq = None
        self.rx_rate = None

    def work(self, input_items, output_items):
        """example: multiply with constant"""
        if self.worker.is_alive():
            return len(input_items[0])

        if self.drop:
            self.drop = False
            self.message_port_pub(
                pmt.intern('drop'),
                pmt.from_bool(False),
            )


        if input_items[0].shape[0] == self.nsamples:
            print(datetime.now())

            tags = self.get_tags_in_window(0,0, self.nsamples)
            for tag in tags:
                tag = gr.tag_to_python(tag)
                if tag.key == 'rx_freq':
                    self.rx_freq = tag.value
                if tag.key == 'rx_rate':
                    self.rx_rate = tag.value

            self.worker = Process(
                target=gen_spectrogram,
                args=(
                    input_items[0].copy(),
                    self.rx_freq,
                    self.rx_rate,
                ))
            # self.worker.setDaemon(True)
            self.worker.start()

            self.message_port_pub(
                pmt.intern('drop'),
                pmt.from_bool(True))

            self.drop = True
            return self.nsamples

        return 0

