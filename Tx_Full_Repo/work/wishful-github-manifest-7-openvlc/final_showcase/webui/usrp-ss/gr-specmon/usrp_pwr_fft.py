#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: USRP Spectrum Monitor
# Author: Mikołaj Chwalisz
# Generated: Mon May 28 15:38:20 2018
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.fft import logpwrfft
from gnuradio.filter import firdes
from optparse import OptionParser
import time
import waterfall_zmq_sink


class usrp_pwr_fft(gr.top_block):

    def __init__(self, bandwidth=22000000, center_frequency=2462000000, usrp_addr="type=b200", zmq_addr="tcp://localhost:5507"):
        gr.top_block.__init__(self, "USRP Spectrum Monitor")

        ##################################################
        # Parameters
        ##################################################
        self.bandwidth = bandwidth
        self.center_frequency = center_frequency
        self.usrp_addr = usrp_addr
        self.zmq_addr = zmq_addr

        ##################################################
        # Variables
        ##################################################
        self.frame_rate = frame_rate = 0.001
        self.fft_size = fft_size = 128

        ##################################################
        # Blocks
        ##################################################
        self.waterfall_zmq_sink = waterfall_zmq_sink.blk(freq_Size=fft_size, num_Samples=1000, msg_interval=1000, addr=zmq_addr)
        self.uhd_usrp_source_0_0 = uhd.usrp_source(
        	",".join((usrp_addr, '')),
        	uhd.stream_args(
        		cpu_format="fc32",
        		otw_format='sc16',
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0_0.set_samp_rate(bandwidth)
        self.uhd_usrp_source_0_0.set_center_freq(center_frequency, 0)
        self.uhd_usrp_source_0_0.set_gain(30, 0)
        self.uhd_usrp_source_0_0.set_bandwidth(bandwidth, 0)
        (self.uhd_usrp_source_0_0).set_min_output_buffer(2024)
        self.logpwrfft_x_0 = logpwrfft.logpwrfft_c(
        	sample_rate=bandwidth,
        	fft_size=fft_size,
        	ref_scale=2,
        	frame_rate=1000,
        	avg_alpha=1.0,
        	average=False,
        )
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_float*1, fft_size)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_float*1, fft_size)
        (self.blocks_stream_to_vector_0).set_min_output_buffer(2024)
        self.blocks_stream_mux_0 = blocks.stream_mux(gr.sizeof_float*1, (fft_size/2, fft_size/2))
        self.blocks_deinterleave_0 = blocks.deinterleave(gr.sizeof_float*1, fft_size/2)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_deinterleave_0, 0), (self.blocks_stream_mux_0, 1))
        self.connect((self.blocks_deinterleave_0, 1), (self.blocks_stream_mux_0, 0))
        self.connect((self.blocks_stream_mux_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.waterfall_zmq_sink, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_deinterleave_0, 0))
        self.connect((self.logpwrfft_x_0, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.uhd_usrp_source_0_0, 0), (self.logpwrfft_x_0, 0))

    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        self.uhd_usrp_source_0_0.set_samp_rate(self.bandwidth)
        self.uhd_usrp_source_0_0.set_bandwidth(self.bandwidth, 0)
        self.logpwrfft_x_0.set_sample_rate(self.bandwidth)

    def get_center_frequency(self):
        return self.center_frequency

    def set_center_frequency(self, center_frequency):
        self.center_frequency = center_frequency
        self.uhd_usrp_source_0_0.set_center_freq(self.center_frequency, 0)

    def get_usrp_addr(self):
        return self.usrp_addr

    def set_usrp_addr(self, usrp_addr):
        self.usrp_addr = usrp_addr

    def get_zmq_addr(self):
        return self.zmq_addr

    def set_zmq_addr(self, zmq_addr):
        self.zmq_addr = zmq_addr

    def get_frame_rate(self):
        return self.frame_rate

    def set_frame_rate(self, frame_rate):
        self.frame_rate = frame_rate

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size


def argument_parser():
    parser = OptionParser(usage="%prog: [options]", option_class=eng_option)
    parser.add_option(
        "-b", "--bandwidth", dest="bandwidth", type="eng_float", default=eng_notation.num_to_str(22000000),
        help="Set Collected bandwidth [default=%default]")
    parser.add_option(
        "-c", "--center-frequency", dest="center_frequency", type="eng_float", default=eng_notation.num_to_str(2462000000),
        help="Set Center frequency [default=%default]")
    parser.add_option(
        "-u", "--usrp-addr", dest="usrp_addr", type="string", default="type=b200",
        help="Set Select USRP [default=%default]")
    parser.add_option(
        "-a", "--zmq-addr", dest="zmq_addr", type="string", default="tcp://localhost:5507",
        help="Set zmq_addr [default=%default]")
    return parser


def main(top_block_cls=usrp_pwr_fft, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print "Error: failed to enable real-time scheduling."

    tb = top_block_cls(bandwidth=options.bandwidth, center_frequency=options.center_frequency, usrp_addr=options.usrp_addr, zmq_addr=options.zmq_addr)
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
