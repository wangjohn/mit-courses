#demodulate workfile: 6.02 PS 4,5,6
import numpy
import sendrecv
import math

def avgfilter(samples_in, window):
    raise NotImplementedError, "avgfilter"

def lpfilter(samples_in, omega_cut):
    raise NotImplementedError, "lpfilter"

def envelope_demodulator(samples, sample_rate, carrier_freq, spb):
    raise NotImplementedError, "envelope_demodulator"

def avg_demodulator(samples, sample_rate, carrier_freq, spb):
    raise NotImplementedError, "avg_demodulator"

def quad_demodulator(samples, sample_rate, carrier_freq, spb, channel_gap = 500):
    raise NotImplementedError, "avg_demodulator"
