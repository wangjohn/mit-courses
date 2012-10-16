import math
from mapper import *
from common import local_carrier

class Transmitter:
    def __init__(self, ktype, carrier_freq, samplerate, one, spb, preamble):
        self.ktype = ktype
        self.fc = carrier_freq  # in cycles per sec, i.e., Hz
        self.samplerate = samplerate
        self.mapper = Mapper(ktype, one, spb, preamble)
        self.preamble = preamble

    def xmit(self, data):
        '''
        Return an array of modulated samples. Make sure to 
        prepend the preamble to the data bits before converting to samples.
        '''
        xmitsamples = []
        xmitsamples = self.mapper.bits2samples(self.preamble.set_preamble())
        xmitsamples = numpy.append(xmitsamples, self.mapper.bits2samples(data))
        mod = self.modulate(xmitsamples)
#        self.plot_sig_spectrum(numpy.real(mod),
#                               "modulated samples")
        return mod

    def modulate(self, samples):
        '''
        Multiply samples by a local sinusoid carrier of the same length.
        Return the multiplied result.
        '''
        print '\tNumber of samples being sent:', len(samples)
        return samples * local_carrier(self.fc, len(samples), self.samplerate)

    def plot_sig_spectrum(self, samples, name):
        P = len(samples)
        omega1 = 2*math.pi/P
        # omegaks = numpy.arange(0,P) * omega1 - math.pi
        omegak = omega1*P*numpy.fft.fftfreq(P)
        omegaks = numpy.fft.fftshift(omegak)
        X = numpy.fft.fft(samples)
        Xs = numpy.fft.fftshift(X)
        p.figure()
        p.plot(omegaks,abs(Xs))
        p.title('Spectrum abs(Xk) of signal %s' % name)
        p.xlabel('Omega')
