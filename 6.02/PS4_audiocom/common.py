import numpy
import math
import operator


# Methods common to both the transmitter and receiver.
def local_carrier(fc, n, samplerate, name=None):
    '''
    Generate a cosine waveform at fc/samplerate for n samples.
    '''
    if name is None:
        args = numpy.arange(0, n) * fc * 2 * math.pi / samplerate
        return numpy.cos(args)
    elif name == "demodquad":        # used in quadrature DEMODULATION
        args = numpy.arange(0, n) * fc * 2 * math.pi / samplerate
        return numpy.exp(1j*args)

def hamming(s1,s2):
    l = min(len(s1), len(s2))
    hd = sum(map(operator.xor,s1[:l],s2[:l]))
    err = 1.0*hd/float(l)
    return hd, err    

def truncate(h, thresh):
    for i in xrange(len(h)-1, 0, -1):
        if abs(h[i]) > thresh:
            break
    return h[:i]

def step2sample(s):
    h = numpy.append(s[0], [0]*(len(s)-1))
    for i in xrange(1,max(len(s), 100)):
        h[i] = s[i]-s[i-1]
    truncate(h, 1.0e-4)
    return h
