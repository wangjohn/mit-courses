#demodulate solutions
import numpy
import sendrecv
import math

def avgfilter(samples_in, carrier_freq, config):
    y = [0]*len(samples_in)
    for i in range(len(y)):
        y[i] = numpy.mean(samples_in[i:i+window])
    return numpy.array(y)

def lpfilter(samples_in, carrier_freq, config):
    raise NotImplementedError, 'lpfilter'

def envelope(samples, carrier_freq, config):
    return avgfilter(numpy.abs(samples), (sample_rate/carrier_freq)/2)

def heterodyne(samples, carrier_freq, config):
    raise NotImplementedError, 'heterodyne'

def quadrature(samples, carrier_freq, config):
    raise NotImplementedError, 'quadrature'
