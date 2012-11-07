# template for PSet #4
import sys
import math
import random
import numpy
import matplotlib
import os
if os.uname()[0] == 'Darwin':
    matplotlib.use('macosx')
import matplotlib.pyplot as p
import matplotlib.mlab as mlab
import StringIO
import scipy.signal
import scipy.stats
import operator
from optparse import OptionParser

# import the channel class that utilizes the pyaudio infrastructure to send samples over the speaker/microphone audio link
import audio_channel as ach
import bypass_channel as bch
#import bypass_channel_audiocom as bch #uncomment to use our version of the bypass channel
from link_defs import *
from transmitter import *
from srcsink import *
from preamble import *
#from preamble_audiocom import * #uncomment to use our version of the preamble detector
from graphs import *

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
    for i in xrange(1,min(len(s), 100)):
        h[i] = s[i]-s[i-1]
    truncate(h, 1.0e-4)
    return h

# Main program for the audio communication system
if __name__ == '__main__':

    # debugging helper
    #numpy.seterr(all='raise')
    
    if len(sys.argv) == 1:
        import config
        opt = config.Options()
    else:
        parser = OptionParser()
        # Source and Sink options
        parser.add_option("-S", "--src", type="string", dest="srctype", 
                          default='random', help="payload (0s, 1s, random)")
        parser.add_option("-n", "--nbits", type="int", dest="numbits", 
                          default=200, help="number of data bits")
        parser.add_option("-f", "--file", type="string", dest="fname",
                          action="append", help="filename(s)")
        parser.add_option("-H", "--header", action="store_true", dest="header",
                          default=False, help="use header")
        
        # Phy-layer Transmitter and Receiver options
        parser.add_option("-r", "--samplerate", type="int", dest="samplerate", 
                          default=48000, help="sample rate (Hz)")
        parser.add_option("-i", "--chunksize", type="int", dest="chunksize", 
                          default=256, help="samples per chunk (transmitter)")
        parser.add_option("-p", "--prefill", type="int", dest="prefill", 
                          default=60, help="write buffer prefill (transmitter)")
        parser.add_option("-s", "--spb", type="int", dest="spb", 
                          default=256, help="samples per bit")
        parser.add_option("-c", "--channel", type="int", dest="channel", 
                          action="append", help="lowest carrier frequency (Hz)")
        parser.add_option("-G", "--gap", type="int", dest="changap", 
                          default=500, help="lowest carrier frequency (Hz)")
        parser.add_option("-q", "--silence", type="int", dest="silence",
                          default=80, help="#samples of silence at start of preamble")
        parser.add_option("-C", "--carrier-preamble", action="store_true", dest="carrier_preamble",
                          default=False, help="detect preamble over carrier, not baseband")

        # Modulation (signaling) and Demodulation options
        parser.add_option("-k", "--keytype", type="string", dest="ktype",
                          default="on_off", help="keying (signaling) scheme")
        parser.add_option("-d", "--demod", type="string", dest="demod",
                          default="envelope", help="demodulation scheme")
        parser.add_option("-t", "--filter", type="string", dest="filter",
                          default="avg", help="filter type ('avg' or 'lopass')")
        parser.add_option("-o", "--one", type="float", dest="one",
                          default="1.0", help="voltage level for bit 1")

        # BypassChannel options
        parser.add_option("-b", "--bypass", action="store_true", dest="bypass",
                          default=False, help="use bypass channel instead of audio")
        parser.add_option("-z", "--noise", type="float", dest="noise", 
                          default=0.25, help="noise variance (for bypass channel)")
        parser.add_option("-l", "--lag", type="int", dest="lag", 
                          default='0', help="lag (for bypass channel)")
        parser.add_option("-u", "--usr", type="string", dest="h", 
                          default='1', help="unit step & sample response (h)")

        # Got graphs?
        parser.add_option("-g", "--graph", action="store_true", dest="graph",
                          default=False, help="show graphs")

        (opt,args) = parser.parse_args()

    # Choose receiver class based on carrier_preamble paramater
    if opt.carrier_preamble:
        from receiver_carrier_preamble import ReceiverCarrierPreamble
        ReceiverClass = ReceiverCarrierPreamble
    else:
        from receiver import Receiver
        ReceiverClass = Receiver
        
    # Get a good list of carrier frequencies into the channels variable
    if opt.channel is None:
        opt.channel = [1000]
    channels = opt.channel
    if opt.fname is not None:
        # make sure there are as many channels as there are files
        if len(opt.fname) != len(channels):
            if len(channels) != 1:
                raise RuntimeError, ("Number of given channel frequencies must either contain " +
                                     "one frequency (and then a series of frequencies are used, based " +
                                     "on the given frequency), or as many frequencies as there are file inputs")
            else:
                channels = [channels[0] + int(opt.changap)*i for i in xrange(len(opt.fname))]

    # Print option summary:
    print 'Parameters in experiment:'
    print '\tSamples per bit:', opt.spb
    print '\tKeying scheme:', opt.ktype
    print '\tDemodulation scheme:', opt.demod
    print '\tChannel type:', ('Audio' if not opt.bypass else 'Bypass')
    if opt.bypass:
        print '\t  Noise:', opt.noise, ' lag:', opt.lag, 'h: [', opt.h, ']'
    print '\tFrequency list:', channels, 'Hz'
    
    # create Preamble instance
    preamble = Preamble(opt.silence)

    # Produce the samples to be transmitted
    mod_samples = numpy.empty([0], dtype=numpy.float32) # samples to be trasmitted
    src = {} # dictionary from carrier frequency to Source instance
    i = 0
    for fc in channels:
        if opt.fname is not None:
            src[fc] = Source(opt.srctype, opt.header, opt.numbits, opt.fname[i])
        else:
            src[fc] = Source(opt.srctype, opt.header, opt.numbits, None)

        i += 1
        print 'Channel', fc, 'Hz'
        print '\tData type:', src[fc].srctype
        print '\tData size (bits):', len(src[fc].payload)
        if opt.header:
            print '\tHeader len: %d bits' % len(src[fc].frame.header)
        else:
            print '\tNo header used'

        xmitter = Transmitter(opt.ktype, fc, opt.samplerate, opt.one, opt.spb, preamble)
        new_samples = xmitter.xmit(src[fc].frame.bits)

        # enlarge mod_samples and new_samples to the same length (larger of the two)
        L = max(len(new_samples), len(mod_samples))
        new_samples = numpy.append(new_samples, [0]*(L-len(new_samples)))
        mod_samples = numpy.append(mod_samples, [0]*(L-len(mod_samples)))
        
        # add new_samples to mod_samples
        mod_samples = mod_samples + new_samples
    
#    plot_sig_spectrum(numpy.real(mod_samples), 'Spectrum of modulated samples')
    # create channel instance
    if opt.bypass:
        h = [float(x) for x in opt.h.replace(',', ' ').split(' ') if x != '']
        channel = bch.BypassChannel(opt.noise, opt.lag, h)
    else:
        channel = ach.AudioChannel(opt.samplerate, opt.chunksize, opt.prefill)
        
    # transmit the samples, and retrieve samples back from the channel
    try:
        samples_rx = channel.xmit_and_recv(mod_samples)
    except ZeroDivisionError:
        # should only happen for audio channel
        print "I didn't get any samples; is your microphone or speaker OFF?"
        print "Please turn them on!"
        sys.exit(1)

    # process the received samples
    for fc in channels:
        # make receiver
        #r = ReceiverClass(opt.ktype, fc, opt.changap, opt.samplerate, opt.spb, opt.demod, preamble)
        r = ReceiverClass(opt, fc, preamble)
        rcdbits, softinfo, snr, demod_samples, hist_samples, offset = r.recv(samples_rx)
        # push into sink
        sink = Sink(r, opt.header, src[fc].srctype)
        if opt.fname is not None:
            rcd_payload = sink.process(rcdbits, softinfo, src[fc].fname)
        else:
            rcd_payload = sink.process(rcdbits, softinfo)
    
        if len(rcd_payload) > 0:
            hd, err = hamming(rcd_payload, src[fc].payload)
            print 'Hamming distance for payload at frequency', fc,'Hz:', hd, 'BER:', err
        else:
            print 'Could not recover transmission.'

        if opt.srctype == "01":
            stepoffset = preamble.barkerlen()*opt.spb + opt.spb*opt.numbits/2 
            ds = demod_samples[stepoffset:stepoffset+80]
            usr = step2sample(ds)
            if opt.bypass:
                usrfile = open('usr.'+opt.h, 'w')
            else:
                usrfile = open('usr.audio.'+ str(int(time.time())), 'w')
            pickle.dump(usr, usrfile)
            if opt.graph:
                p.figure(1)
                p.stem(range(len(usr)), usr)
                p.figure(2)
#                plot_samples(demod_samples[stepoffset:stepoffset+400], 'unit-step response')
                p.stem(range(len(ds)), ds)
                p.show()
        else:
            if opt.graph:
                len_demod = len(rcd_payload) + preamble.barkerlen()
                if opt.header:
                    len_demod += len(src[fc].frame.header) 
                len_demod = opt.spb*len_demod
                plot_graphs(mod_samples, samples_rx[offset:], demod_samples[:len_demod], hist_samples[:len_demod], opt.spb, src[fc].srctype, preamble, opt.header)

