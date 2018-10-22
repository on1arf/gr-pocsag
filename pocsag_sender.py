#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: POCSAG Sender via HackRF
# Author: ON1ARF & Tauebenuss
# Description: Sending Pocsag Messages via HACKRF One
# Generated: Mon Oct 22 21:00:22 2018
##################################################


from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.filter import pfb
from optparse import OptionParser
import math
import osmosdr
import pocsag_generator
import time


class pocsag_sender(gr.top_block):

    def __init__(self, RIC=1122551, SubRIC=0, Text='Testmessage by HACRF One'):
        gr.top_block.__init__(self, "POCSAG Sender via HackRF")

        ##################################################
        # Parameters
        ##################################################
        self.RIC = RIC
        self.SubRIC = SubRIC
        self.Text = Text

        ##################################################
        # Variables
        ##################################################
        self.tx_gain = tx_gain = 3
        self.symrate = symrate = 38400
        self.samp_rate = samp_rate = 12000000
        self.pocsagbitrate = pocsagbitrate = 1200
        self.pagerfreq = pagerfreq = 100880000
        self.max_deviation = max_deviation = 4500.0
        self.af_gain = af_gain = 190

        ##################################################
        # Blocks
        ##################################################
        self.pocsag_generator = pocsag_generator.pocsagsender(number=RIC, source=SubRIC, sleeptime=5, text=Text)
        self.pfb_arb_resampler_xxx_0 = pfb.arb_resampler_ccf(
        	  float(samp_rate)/float(symrate),
                  taps=None,
        	  flt_size=16)
        self.pfb_arb_resampler_xxx_0.declare_sample_delay(0)

        self.osmosdr_sink_0 = osmosdr.sink( args="numchan=" + str(1) + " " + 'hackrf' )
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(pagerfreq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(0, 0)
        self.osmosdr_sink_0.set_if_gain(tx_gain, 0)
        self.osmosdr_sink_0.set_bb_gain(20, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)

        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_char*1, symrate/pocsagbitrate)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((af_gain/100, ))
        self.blocks_char_to_float_0 = blocks.char_to_float(1, af_gain*0.7/1000)
        self.analog_frequency_modulator_fc_0 = analog.frequency_modulator_fc(2.0 * math.pi * max_deviation / float(symrate))

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_frequency_modulator_fc_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_char_to_float_0, 0), (self.analog_frequency_modulator_fc_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.pfb_arb_resampler_xxx_0, 0))
        self.connect((self.blocks_repeat_0, 0), (self.blocks_char_to_float_0, 0))
        self.connect((self.pfb_arb_resampler_xxx_0, 0), (self.osmosdr_sink_0, 0))
        self.connect((self.pocsag_generator, 0), (self.blocks_repeat_0, 0))

    def get_RIC(self):
        return self.RIC

    def set_RIC(self, RIC):
        self.RIC = RIC
        self.pocsag_generator.number = self.RIC

    def get_SubRIC(self):
        return self.SubRIC

    def set_SubRIC(self, SubRIC):
        self.SubRIC = SubRIC
        self.pocsag_generator.source = self.SubRIC

    def get_Text(self):
        return self.Text

    def set_Text(self, Text):
        self.Text = Text

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.osmosdr_sink_0.set_if_gain(self.tx_gain, 0)

    def get_symrate(self):
        return self.symrate

    def set_symrate(self, symrate):
        self.symrate = symrate
        self.pfb_arb_resampler_xxx_0.set_rate(float(self.samp_rate)/float(self.symrate))
        self.blocks_repeat_0.set_interpolation(self.symrate/self.pocsagbitrate)
        self.analog_frequency_modulator_fc_0.set_sensitivity(2.0 * math.pi * self.max_deviation / float(self.symrate))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.pfb_arb_resampler_xxx_0.set_rate(float(self.samp_rate)/float(self.symrate))
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)

    def get_pocsagbitrate(self):
        return self.pocsagbitrate

    def set_pocsagbitrate(self, pocsagbitrate):
        self.pocsagbitrate = pocsagbitrate
        self.blocks_repeat_0.set_interpolation(self.symrate/self.pocsagbitrate)

    def get_pagerfreq(self):
        return self.pagerfreq

    def set_pagerfreq(self, pagerfreq):
        self.pagerfreq = pagerfreq
        self.osmosdr_sink_0.set_center_freq(self.pagerfreq, 0)

    def get_max_deviation(self):
        return self.max_deviation

    def set_max_deviation(self, max_deviation):
        self.max_deviation = max_deviation
        self.analog_frequency_modulator_fc_0.set_sensitivity(2.0 * math.pi * self.max_deviation / float(self.symrate))

    def get_af_gain(self):
        return self.af_gain

    def set_af_gain(self, af_gain):
        self.af_gain = af_gain
        self.blocks_multiply_const_vxx_0.set_k((self.af_gain/100, ))
        self.blocks_char_to_float_0.set_scale(self.af_gain*0.7/1000)


def argument_parser():
    description = 'Sending Pocsag Messages via HACKRF One'
    parser = OptionParser(usage="%prog: [options]", option_class=eng_option, description=description)
    parser.add_option(
        "", "--RIC", dest="RIC", type="intx", default=1122551,
        help="Set RIC [default=%default]")
    parser.add_option(
        "", "--SubRIC", dest="SubRIC", type="intx", default=0,
        help="Set SubRIC [default=%default]")
    parser.add_option(
        "", "--Text", dest="Text", type="string", default='Testmessage by HACRF One',
        help="Set Testmessage by HACRF One [default=%default]")
    return parser


def main(top_block_cls=pocsag_sender, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    tb = top_block_cls(RIC=options.RIC, SubRIC=options.SubRIC, Text=options.Text)
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
