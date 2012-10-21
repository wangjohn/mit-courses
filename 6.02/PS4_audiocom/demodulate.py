#demodulate workfile: 6.02 PS 4,5,6
import numpy
import sendrecv
import math

def avgfilter(samples_in, window):
    x = []
    for i in xrange(len(samples_in)):
        current_slice = samples_in[i:(i+window)]
        x.append(sum(current_slice) / float(len(current_slice)))
    return numpy.array(x)

def lpfilter(samples_in, omega_cut):
    raise NotImplementedError, "lpfilter"

def envelope_demodulator(samples, sample_rate, carrier_freq, spb):
    raise NotImplementedError, "envelope_demodulator"

def avg_demodulator(samples, sample_rate, carrier_freq, spb):
    window_size = (0.5*sample_rate*spb/carrier_freq)
    abs_samples = [abs(sample) for sample in samples]
    return avgfilter(abs_samples, window_size)

def quad_demodulator(samples, sample_rate, carrier_freq, spb, channel_gap = 500):
    raise NotImplementedError, "avg_demodulator"
