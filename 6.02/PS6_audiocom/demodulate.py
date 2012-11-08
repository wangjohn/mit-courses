#demodulate solutions
import numpy
import sendrecv
import math

def avgfilter(samples_in, carrier_freq, config):
    window = config.spb / 2 
    y = [0]*len(samples_in)
    for i in range(len(y)):
        y[i] = numpy.mean(samples_in[i:i+window])
    return numpy.array(y)

def lpfilter(samples_in, carrier_freq, config):
    cutoff_freq = (config.changap*config.spb/(2*config.samplerate))
    h = [math.sin(2*math.pi*cutoff_freq*i)/(i*math.pi) for i in xrange(-50, 51, 1)]
    h = numpy.array(h)
    return numpy.convolve(samples_in, h)

def envelope(samples, carrier_freq, config):
    sample_rate = config.samplerate
    return avgfilter(numpy.abs(samples), (sample_rate/carrier_freq)/2)

def heterodyne(samples, carrier_freq, config):
    sample_rate = config.samplerate
    local_carrier = sendrecv.local_carrier(carrier_freq, len(samples), sample_rate)
    return numpy.multiply(samples, local_carrier)

def quadrature(samples, carrier_freq, config):
    quadcarrier = sendrecv.local_carrier(carrier_freq, len(samples), config.samplerate, "demodquad")
    return numpy.multiply(samples, quadcarrier)
