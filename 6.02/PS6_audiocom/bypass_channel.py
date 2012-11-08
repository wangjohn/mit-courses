import math
import numpy
import matplotlib.pyplot as p
import graphs

class BypassChannel:
    def __init__(self, noise, lag, h):
        self.noise = noise
        self.lag = lag
        self.h = h
        numpy.random.seed()

    def xmit_and_recv(self, tx_samples):
        # convolve samples with h
        conv_samples = numpy.convolve(self.h, tx_samples)
        # add lag
        lag_samples = numpy.append([0]*self.lag, conv_samples)  
        # add Gaussian noise
        return lag_samples + numpy.random.normal(0.0, math.sqrt(self.noise), len(lag_samples))
