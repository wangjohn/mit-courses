import numpy
import sendrecv
from numpy import linalg as LA

class Preamble:
    def __init__(self, silence):
        self.silence = silence

    def set_preamble(self):
        '''
        Our preamble is "silence" 0's followed by a 11-bit Barker sequence, 
        known to have low auto-correlation.
        '''
        barker =  [1,0,1,1,0,1,1,1,0,0,0,1,1,1,1,1,0,0,1,1,0,1,0,1]
        return numpy.append([0]*self.silence, barker)

    def barker(self):
        return self.set_preamble()[self.silence:]

    def barkerlen(self):
        return len(self.barker())

    def __len__(self):
        return len(self.set_preamble())

    def detect(self, dsamples, receiver, offset):
        raise NotImplementedError, 'Preamble.detect'

    def correlate(self, x, y):
        raise NotImplementedError, 'Preamble.correlate'

    def check(self, bits):
        for i in xrange(len(bits)-self.barkerlen()):
            if (self.barker() == bits[i:i+self.barkerlen()]).all():
                return i
        # else, couldn't find preamble :(
        return -1
