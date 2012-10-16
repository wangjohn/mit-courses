import math
import numpy
from numpy import linalg as LA
import matplotlib.pyplot as p
from mapper_carrier_preamble import *
import common #for local_carrier
from link_defs import *

class ReceiverCarrierPreamble:
    def __init__(self, ktype, carrier_freq, changap, samplerate, spb, demodtype, preamble):
        self.ktype = ktype
        self.fc = carrier_freq
        self.changap = changap
        self.samplerate = samplerate
        self.mapper = Mapper(ktype, spb, preamble)
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
        start = self.detect_preamble(samples)
        print 'I think the signal (Barker sequence) starts at', start
        demod_samples = self.demodulate(samples[start:])
        recd_bits,si,snr = self.mapper.demap(demod_samples, self.demodtype)
        if snr > 0.0:
            print 'Measured SNR: %.1f dB' % (10.0*math.log(snr, 10))
        else:
            print 'Couldn\'t estimate SNR; negative signal???!'
        recd_bits = numpy.array(recd_bits, dtype=int)        
        if not (recd_bits[:self.preamble.barkerlen()] == self.preamble.barker()).all():
            print '*** WARNING: Could not detect preamble reliably. ***'
        return recd_bits, si, snr, demod_samples, []
        
    def detect_preamble(self, samples):
        '''
        Preamble detection modulating over carrier (ie, not in baseband).
        '''
        offset = max(0, self.detect_energy(samples))
        print 'Some sort of energy detected around sample', offset
        barker = self.preamble.barker()
        presamples = self.mapper.bits2samples(barker)
        mod_presamples = presamples * common.local_carrier(self.fc, len(presamples), self.samplerate)
        x = 2*self.preamble.barkerlen()*self.mapper.spb
        return max(0, self.correlate(mod_presamples, 
                                     samples[max(0,offset-x):offset+x]))

    def detect_energy(self, samples):
        zerolen = self.preamble.silence * self.mapper.spb
        isamp = samples[:zerolen]
        mod_isamp = isamp * common.local_carrier(self.fc, len(isamp), self.samplerate)
        noise_mean = numpy.mean(mod_isamp)
        noise_std = numpy.std(mod_isamp)
        for offset in xrange(len(samples)):
            if abs(samples[offset] > noise_mean + 5.0*noise_std):
                break
        return offset
        
    def correlate(self, x, y):
        '''
        Find the starting point in y of the best occurrence of x.
        Assume len(x) <= len(y). Returns -1 if len(x) > len(y).
        We assume that x shows up in y from the xmitter only once in the 
        stream, but if it happens to repeat, we'll return the "best" match.
        The match is done by correlating y with x, i.e., taking the dot product
        of the corresponding samples.
        '''
        # actually an error, but we'll let the caller deal w/ it
        if len(x) > len(y) or len(x) == 0:
            return 0 
        correl = []
        for i in range(len(y)-len(x)+1):
            correl.append(numpy.sum(y[i:i+len(x)]*x)/LA.norm(y[i:i+len(x)]))
#        print correl, numpy.argmax(correl)

        '''
        p.figure(1)
        # plot the transmitted samples
        p.subplot(211)
        plot_samples(x, 'presamples')
        p.subplot(212)
        plot_samples(y, 'rcdsamples')
        # plot the received samples
        p.show()
        '''
        return numpy.argmax(correl)

    def demodulate(self, samples):
        if self.demodtype == "envelop":
            return self.avgfilter(numpy.abs(samples), (self.samplerate/self.fc)/2)
        elif self.demodtype == "avg":
            het_samples = samples * common.local_carrier(self.fc, len(samples), self.samplerate)
        #        return self.avgfilter(het_samples, SAMPLES_PER_CARRIER/2)
            return self.avgfilter(het_samples, (self.samplerate/self.fc)/2)
        elif self.demodtype == "quad":
            '''
            A quadrature demodulator.
            '''
            het_samples = samples * common.local_carrier(self.fc, len(samples), self.samplerate, "demodquad")
#        self.plot_sig_spectrum(numpy.real(het_samples),"demodulated samples before LPF - I-branch")

            # set the LPF cut-off frequency
            omega_lo = 1.5 * math.pi / self.mapper.spb
            omega_hi = self.fc * 2 * math.pi / self.samplerate
            omega_cut = (self.changap*2*math.pi/self.samplerate)/2.0
            print "Rx LPF Cutoff frequency :", omega_cut
    
            demod_filt_out = self.lpfilter(het_samples, omega_cut, 'receive LPF')
            samples_rx_out = numpy.abs(demod_filt_out)
#        self.plot_sig_spectrum(numpy.real(demod_filt_out),
#                               "demodulated samples after LPF - I-branch")

        #        p.show()
            return samples_rx_out
        else:
            print 'Unsupported demod type'
            sys.exit(1)

    def avgfilter(self, samples_in, window):
        '''
        A simple averaging filter whose every output is the
        mean of the last "window" samples.
        y[n] = (x[n] + x[n+1] + ... + x[n+window-1])/window, 
        where x is the input sequence of samples and y is the output
        '''
        y = [0]*len(samples_in)
        for i in range(len(y)):
            y[i] = numpy.sum(samples_in[i:i+window])/window
        return y        


    def lpfilter(self, samples_in, omega_cut, name):
        '''
        A low-pass filter of frequency omega_cut.
        '''
        # set the filter unit sample response
        L = 100
        hf = numpy.sin(omega_cut*numpy.arange(-L,L+1))/(math.pi*numpy.arange(-L,L+1))
        hf[L] = omega_cut/math.pi
#        self.plot_freq_resp(hf, len(samples_in), name)

        # convolve unit sample response with input samples
        samples_out=[0]*len(samples_in)
        for i in range(len(samples_out)-len(hf)):
            samples_out[i] = numpy.sum(samples_in[i:i+len(hf)]*hf[::-1])
        return numpy.array(samples_out)

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
