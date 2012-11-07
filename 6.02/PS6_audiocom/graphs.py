# audiocom library: plotting functions
# MIT 6.02. 
# For more information: hari@mit.edu

import math
import numpy
import matplotlib.mlab as mlab
import matplotlib.pyplot as p

def plot_samples(samples,name):
    # TODO: write the code to plot the samples and label the figure with 'name' string
    p.title(name)
    p.xlabel('Sample number')
    p.ylabel('Voltage')
#    p.stem(range(len(samples)), samples)
    p.plot(range(len(samples)), samples)

def plot_hist(data, name):
    # the histogram of the data
#    for d in data:
#        if d < 1.0e-6:
#            data = numpy.delete(data, d)
    n, bins, patches = p.hist(data, math.sqrt(len(data)), normed=1,
                              facecolor='g', alpha=0.75)
    mean = numpy.mean(data)
    std = numpy.std(data)
    #y = mlab.normpdf(bins, mean, std)
    #p.plot(bins, y, 'r--', linewidth=2)
    print 'Sample mean %.2g, sample stddev %.2g, max %.2g, min %.2g' % (mean, std, numpy.max(data), numpy.min(data))
    p.xlabel('Voltage')
    p.ylabel('Prob. density')
    p.title('Histogram of the %s' % name)
    p.grid(True)

def plot_eye(samples, spb, name):
    '''
    Plot the eye diagram of the sample sequence, wrapping around every 
    3*SAMPLES_PER_BIT
    '''
    eyel=3*spb
    for i in range((len(samples)-1)/(eyel)):
        p.plot(range(eyel),samples[i*eyel:(i+1)*eyel])
    p.title('%s' % name)
    p.xlabel('Sample number')
    p.ylabel('Voltage')
    
def plot_graphs(mod_samples, rx_samples, demod_samples, hist_samples, spb, 
                srctype, preamble, header):

    scale = spb/4 - 1
   
    #fix hist_samples to only consider the 1/2 of the samples per bit closest to the center
    header_len = 16 if header else 0
    plotrange = (preamble.barkerlen()+header_len)*spb, len(hist_samples)-spb
    hist = hist_samples[plotrange[0]:plotrange[1]]
    hist_samples = []
    for i in xrange(len(hist)/spb):
        hist_samples.extend(hist[int((i+0.25)*spb):int((i+0.75)*spb)])

    p.figure(1)
    # plot the transmitted samples
    p.subplot(311)
    sent = mod_samples[preamble.silence*spb::scale]
    recd = rx_samples[::scale]
    sent = numpy.append(sent,numpy.zeros((1,max(0,len(recd)-len(sent)))))
    recd = numpy.append(recd,numpy.zeros((1,max(0,len(sent)-len(recd)))))
    plot_samples(sent, 'transmitted samples')
    p.hold(True)
    plot_samples(recd, 'blue: transmitted, green: received')

    # plot the received samples
    p.subplot(312)
    plot_samples(demod_samples[plotrange[0]:plotrange[1]], 'demod samples') 
    
    # plot the histogram of demodulated samples in ONE dimension 
    # (for quad, it's the REAL part alone)
    p.subplot(313)
    plot_hist(hist_samples, 'demod samples (1-D) histogram')

    p.figure(2)
    plot_eye(demod_samples[plotrange[0]:plotrange[1]], spb, 'eye diagram')

    p.show()

def plot_sig_spectrum(samples, name):
    P = len(samples)
    omega1 = 2*math.pi/P
    # omegaks = numpy.arange(0,P) * omega1 - math.pi
    omegak = omega1*P*numpy.fft.fftfreq(P)
    omegaks = numpy.fft.fftshift(omegak)
    X = numpy.fft.fft(samples)
    Xs = numpy.fft.fftshift(X)
    # plot pretty pics
    p.figure()
    p.plot(omegaks,abs(Xs))
    p.title('Spectrum abs(Xk) of signal %s' % name)
    p.xlabel('Omega')
