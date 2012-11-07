import sys
import numpy
import scipy.stats
from sendrecv import *

class Mapper:
    '''
    Mapper: Maps bits to samples, and demap samples to bits, soft info, and SNR.
    '''
    def __init__(self, ktype, samples_per_bit, preamble):
        self.spb = samples_per_bit
        self.ktype = ktype
        self.preamble = preamble

    def bits2samples(self, bits):
        '''
        Expand bits to samples by replacing each bit with self.spb samples.
        Each bit is mapped to corresponding sample using onebit2onesample.
        '''
        xsamples = [0]*len(bits)*self.spb
        for i in range(len(xsamples)):
            xsamples[i] = self.onebit2onesample(bits[int(i/self.spb)])
        return xsamples

    def onebit2onesample(self, bit):
        '''
        Takes a bit and returns the sample according to self.ktype (modulation)
        '''
        if bit == 's':
            return 0
        if self.ktype == "bipolar":
            return 2*bit - 1
        return bit

    def demap(self, samples, demodtype=None):
        '''
        Takes a sequence of samples and returns:
        1) a sequence of bits using a hard-decision threshold
        2) a "soft-decision" value for each demapped bit (symbol). 
        3) The signal-to-noise ratio.
        The threshold is calculated dynamically for on_off keying;
        it is 0 for bipolar keying.
        '''
        snr, thresh = self.snr(samples)
        print '0/1 threshold: %.3f' % thresh

        '''
        if demodtype == 'quad':
            samples = self.decimate(samples, self.spb)
            return numpy.array((samples>thresh), dtype=int), None, snr
            
        if self.ktype == "bipolar":
            thresh = 0
        else: 
            upper = scipy.stats.scoreatpercentile(samples, 95)
            lower = scipy.stats.scoreatpercentile(samples, 5)
            thresh = (upper + lower)/2.0
            print 'Receiver thresh: %.3f' % thresh
       '''

        bits = numpy.array([])
        softinfo = []
        for i in range(0, len(samples), self.spb):
            if i+self.spb/4 >= len(samples): break
            m = numpy.mean(samples[i+self.spb/4:i+3*self.spb/4])
            softinfo.append((m-thresh)**2)
            if m > thresh:
                bits = numpy.append(bits, 1)
            else:
                bits = numpy.append(bits, 0)
        return bits, softinfo, snr

    def snr(self, samples):
        barker = self.preamble.barker()
        presamples = samples[:self.preamble.barkerlen()*self.spb]
        samp = [ numpy.array([]), numpy.array([]) ]
        for i in xrange(self.preamble.barkerlen()):
            samp[barker[i]] = numpy.append(samp[barker[i]], samples[i*self.spb+self.spb/4:i*self.spb+3*self.spb/4])
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
