import math
import numpy
import matplotlib.pyplot as p
import graphs
import random

class BypassChannel:
    def __init__(self, noise, lag, h):
        self.noise = noise
        self.lag = lag
        self.h = h
        #DO NOT modify the following lines.
        numpy.random.seed()
        random.seed()

    def xmit_and_recv(self, tx_samples):
	    output = [numpy.random.normal(0, self.noise) for x in xrange(self.lag)]
        convolved = numpy.convolve(self.h, tx_samples)
        for result in convolved:
		    output.append(result + numpy.random.normal(0, self.noise))
	    return numpy.array(output)


