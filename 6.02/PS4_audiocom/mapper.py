import sys
import numpy
import scipy.stats
from sendrecv import *

class Mapper:
    '''
    Mapper: Maps bits to samples, and demap samples to bits, soft info, and SNR.
    '''
    def __init__(self, ktype, one, samples_per_bit, preamble):
        self.spb = samples_per_bit
        self.ktype = ktype
        self.one = one
        self.preamble = preamble

    def bits2samples(self, bits):
        '''
        Expand bits to samples by replacing each bit with self.spb samples.
        Each bit is mapped to corresponding sample using onebit2onesample.
        '''
        xsamples = [0.0]*len(bits)*self.spb
        for i in range(len(xsamples)):
            xsamples[i] = self.onebit2onesample(bits[int(i/self.spb)])
        return xsamples

    def onebit2onesample(self, bit):
        '''
        Takes a bit and returns the sample according to self.ktype (modulation)
        '''
        if self.ktype == "bipolar":
            return 2*bit - 1
        if bit == 1:
            return self.one
        return bit

    def demap(self, samples):
        bits = numpy.array([])
        softinfo = []
        snr, thresh = self.snr_subsamp(samples)
        print '0/1 threshold: %.3f' % thresh
        for s in samples:
            softinfo.append((s-thresh)**2)
            if s > thresh:
                bits = numpy.append(bits, 1)
            else:
                bits = numpy.append(bits, 0)
        return bits, softinfo, snr

    def snr_subsamp(self, samples):
        barker = self.preamble.barker()
        samp = [ numpy.array([]), numpy.array([]) ]
        for i in xrange(len(barker)):
            samp[barker[i]] = numpy.append(samp[barker[i]], samples[i])
        noise = [0.0, 0.0]
        signal = [0.0, 0.0]
        for i in xrange(2):
            noise[i] = numpy.var(samp[i])
            signal[i] = numpy.mean(samp[i])
        print 'On 0:', signal[0], noise[0]
        print 'On 1:', signal[1], noise[1]
        noise = (len(samp[1])*noise[1] + len(samp[0])*noise[0]) / (len(samp[1]) + len(samp[0]))
        thresh = (signal[1] + signal[0])/2
        return (signal[1] - signal[0])**2 / noise, thresh        

    def decimate(self, samples, dec_factor):
        return samples[::dec_factor]
