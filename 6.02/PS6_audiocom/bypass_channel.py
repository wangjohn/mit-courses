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
        raise NotImplementedError, 'BypassChannel.xmit_and_recv'
