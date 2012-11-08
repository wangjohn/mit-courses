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
	# start looking at dsamples[offset] for the preamble sequence
        sample_seq = receiver.mapper.bits2samples(self.barker())
        local_carrier_result = sendrecv.local_carrier(receiver.fc, len(sample_seq), receiver.samplerate)
        waveform = numpy.multiply(sample_seq, local_carrier_result)
        demodulated_waveform = receiver.demodulate(waveform)
        
        search_length = self.barkerlen()*3*receiver.mapper.spb
        index = self.correlate(dsamples, demodulated_waveform[offset:(offset+search_length)])
        return offset + index

    def correlate(self, x, y):
        if len(x) > len(y) or len(x) == 0:
            return 0
        best_normed_dp = None 
        best_index = 0
        for i in xrange(len(y)-len(x)):
            ysubsequence = y[i:(i+len(x))]
            normalized_dot_product = sum(numpy.multiply(x, ysubsequence)) / (LA.norm(x)*LA.norm(ysubsequence))
            if best_normed_dp == None or normalized_dot_product > best_normed_dp:
                best_normed_dp = normalized_dot_product
                best_index = i
        return best_index

    def check(self, bits):
        for i in xrange(len(bits)-self.barkerlen()):
            if (self.barker() == bits[i:i+self.barkerlen()]).all():
                return i
        # else, couldn't find preamble :(
        return -1
