import sys
import math
import numpy
import matplotlib.pyplot as p
import scipy.cluster.vq
import mapper
import sendrecv
from link_defs import *
from preamble import *
from graphs import *

#change the following to "import demodulate" to use your own demodulator(s)
import demodulate_audiocom as demodulate

class Receiver:
    def __init__(self, ktype, carrier_freq, changap, samplerate, spb, demodtype, preamble):
        self.ktype = ktype
        self.fc = carrier_freq
        self.changap = changap
        self.samplerate = samplerate
        self.mapper = mapper.Mapper(ktype, 1.0, spb, preamble) # 1.0 is arbitrary
        self.demodtype = demodtype
        self.preamble = preamble

    def recv(self, samples):
        '''
        The physical-layer receive function, which processes the
        received samples by detecting the preamble and then
        demodulating the samples from the start of the preamble's
        Barker sequence. Returns the sequence of received bits (after
        demapping), soft information (the squared Euclidean distance
        between the symbol corresponding to each bit and the nominal
        (mean) received value for that bit, and the signal-to-noise
        ratio estimated from the preamble's Barker sequence.
        '''
        print 'Received', len(samples), 'samples'
        demod_samples = self.demodulate(samples)
        if self.demodtype == 'quad':
            hist_samples = numpy.real(demod_samples)
            demod_samples = numpy.abs(demod_samples)
        else:
            hist_samples = demod_samples

        spb = self.mapper.spb
        preamble = self.preamble
        # Now, we have a bunch of values that, for on-off keying, are
        # either near amplitude 0 or near a positive amplitude
        # (corresp. to bit "1").  Because we don't know the balance of
        # zeroes and ones in the input, we use 2-means clustering to
        # determine the "1" and "0" clusters.  In practice, some
        # systems use a random scrambler to XOR the input to balance
        # the zeroes and ones. We have decided to avoid that degree of
        # complexity in audiocom (for the time being, anyway).
        one = max(scipy.cluster.vq.kmeans(demod_samples, 2)[0])
        zero = min(scipy.cluster.vq.kmeans(demod_samples, 2)[0])
        thresh = (one + zero)/2.0
        print 'One:', one, "Zero:", zero, '2-means thresh:', thresh
        # Find the sample corresp. to the first reliable bit "1"; this step 
        # is crucial to a proper and correct synchronization w/ the xmitter.
        offset = self.detect_one(demod_samples, thresh, one)
        if offset < 0:
            print '*** ERROR: Could not detect any ones (so no preamble). ***'
            print '\tIncrease volume / turn on mic?'
            print '\tOr is there some other synchronization bug? ***'
            sys.exit(1)

        barker_start = preamble.detect(demod_samples, self, offset)
        subsamples = self.subsample(demod_samples[barker_start:], int(spb/4), int(3*spb/4))

        (bits,si,snr) = self.mapper.demap(subsamples)
        start = preamble.check(bits)

        if start >= 0:
            print 'I think the Barker sequence starts at bit', start + barker_start/spb, \
                '(sample', start*spb+barker_start,')'
            recd_bits = numpy.array(bits[start:], dtype=int)
            if snr > 0.0:
                print 'SNR from preamble: %.1f dB' % (10.0*math.log(snr, 10))
            else:
                print 'WARNING: Couldn\'t estimate SNR...'
            return recd_bits, si[start:], snr, demod_samples[barker_start:], hist_samples[barker_start:], offset
        else:
            print '*** ERROR: Could not detect preamble. ***'
            print '\tIncrease volume / turn on mic / reduce noise?'
            print '\tOr is there some other synchronization bug? ***'
            print bits
            plot_hist(subsamples, 'samples: no separation between levels?')
            p.show()
            sys.exit(1)

    def subsample(self, dsamples, start, end):
        subsamp = numpy.array([])
        for i in range(0, len(dsamples), self.mapper.spb):
            if i+start < len(dsamples):
                subsamp = numpy.append(subsamp, numpy.mean(dsamples[i+start:i+end]))
        return subsamp

    def detect_one(self, demod_samples, thresh, one):
        spb = self.mapper.spb
        for offset in xrange(len(demod_samples)):
            if numpy.mean(demod_samples[offset+spb/4:offset+3*spb/4]) > thresh + (one-thresh) / 2:
                return offset
        return -1

    def demodulate(self, samples):
        if self.demodtype == "envelope":
            return demodulate.envelope_demodulator(samples, self.samplerate, self.fc, self.mapper.spb)
        elif self.demodtype == "avg":
            return demodulate.avg_demodulator(samples, self.samplerate, self.fc, self.mapper.spb)
        elif self.demodtype == "quad":
            return demodulate.quad_demodulator(samples, self.samplerate, self.fc, self.mapper.spb)
        else:
            print 'Unsupported demodulation scheme'
            sys.exit(1)

    def plot_freq_resp(self, hf, num_samples, name):
        omegax = numpy.arange(0,num_samples) * 2*math.pi/num_samples - math.pi
        n = 0
        H = numpy.array([0]*num_samples)
        for hn in hf:
            H = H + hn*numpy.exp(-1j*omegax*n)
            n += 1
        p.figure()
        p.plot(omegax,abs(H))
        p.title('Frequency response abs(H) of %s' % name)
        p.xlabel('Omega')

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
