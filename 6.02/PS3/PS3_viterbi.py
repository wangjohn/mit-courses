# This is the template file for 6.02 Viterbi decoding
import numpy,sys
import PS3_tests

class ViterbiDecoder:
    # Given the constraint length and a list of parity generator
    # functions, do the initial set up for the decoder.  The
    # following useful instance variables are created:
    #   self.K
    #   self.nstates
    #   self.r
    #   self.predecessor_states
    #   self.expected_parity
    def __init__(self, K, glist):
        self.K = K             # constraint length
        self.nstates = 2**(K-1) # number of states in state machine

        # number of parity bits transmitted for each message bit
        print glist
        self.r = len(glist)     

        # States are named using (K-1)-bit integers in the range 0 to
        # nstates-1. The bit representation of the integer corresponds
        # to state label in the transition diagram.  So state 10 is
        # named with the integer 2, state 00 is named with the
        # integer 0.

        # for each state s, figure out the two states in the diagram
        # that have transitions ending at state s.  Record these two
        # states as a two-element tuple.
        self.predecessor_states = \
          [((2*s+0) % self.nstates,(2*s+1) % self.nstates)
           for s in xrange(self.nstates)]

        # this is a 2D table implemented as a list of lists.
        # self.expected_parity[s1][s2] returns the r-bit sequence
        # of parity bits the encoder transmitted when make the
        # state transition from s1 to s2.
        self.expected_parity = \
          [[PS3_tests.expected_parity(s1, s2, K, glist) \
            if s1 in self.predecessor_states[s2] else None
            for s2 in xrange(self.nstates)]
           for s1 in xrange(self.nstates)]

    # expected is an r-element list of the expected parity bits.
    # received is an r-element list of actual sampled voltages for the
    # incoming parity bits.  This is a hard-decision branch metric,
    # so, as described in lab write up, digitize the received voltages
    # to get bits and then compute the Hamming distance between the
    # expected sequence and the received sequence, return that as the
    # branch metric.  Consider using PS3_tests.hamming(seq1,seq2) which
    # computes the Hamming distance between two binary sequences.
    def branch_metric(self,expected,received):
        hard_coded = []
        for bit in received:
            if bit >= 0.5:
                new_bit = 1
            else:
                new_bit = 0
            hard_coded.append(new_bit)
        return PS3_tests.hamming(expected, hard_coded)

    # Compute self.PM[...,n] from the batch of r parity bits and the
    # path metrics for self.PM[...,n-1] computed on the previous
    # iteration.  Consult the method described in the lab write up.
    # In addition to making an entry for self.PM[s,n] for each state
    # s, keep track of the most-likely predecessor for each state in
    # the self.Predecessor array (a two-dimensional array indexed by s
    # and n).  You'll probably find the following instance variables
    # and methods useful: self.predecessor_states, self.expected_parity,
    # and self.branch_metric().  To see what these mean, scan through the
    # code above.
    def viterbi_step(self,n,received_voltages):
        #for states_tuple in self.predecessor_states:
        print received_voltages

        for j in xrange(self.nstates):
            branch_metrics = []
            for i in xrange(self.nstates):
                expected = self.expected_parity[i][j]
                if expected:
                    branch_metrics.append((self.PM[i,n-1] + self.branch_metric(expected, received_voltages), i))
            lowest = None
            for bm in branch_metrics:
                if bm[0] < lowest or lowest == None:
                    lowest = bm[0]
                    lowest_i = bm[1]
            self.PM[j,n] = lowest
            self.Predecessor[j,n] = lowest_i

    # Identify the most-likely ending state of the encoder by
    # finding the state s that has the minimum value of PM[s,n]
    # where n points to the last column of the trellis.  If there
    # are several states with the same minimum value, choose one
    # arbitrarily.  Return the state s.
    def most_likely_state(self,n):
        lowest = None
        state = None
        for i in xrange(self.nstates):
            if self.PM[i,n] < lowest or lowest == None:
                lowest = self.PM[i,n]
                state = i
        return state

    # Starting at state s at time n, use the Predecessor
    # array to find all the states on the most-likely
    # path (in reverse order since we're tracing back through
    # the trellis).  Each state contributes a message bit.
    # Return the decoded message as a sequence of 0's and 1's.
    def traceback(self,s,n):
        current_state = s
        path = [current_state]
        for i in xrange(n):
            current_state = self.Predecessor[current_state, n-i]
            path.append(current_state)
        path.reverse()
        
        message = []
        for state in path:
            message.append(state >> (self.K-2))
        return message[1:]

    # Figure out what the transmitter sent from info in the
    # received voltages.
    def decode(self,received_voltages,debug=False):
        # figure out how many columns are in the trellis
        nreceived = len(received_voltages)
        max_n = (nreceived/self.r) + 1

        # this is the path metric trellis itself, organized as a
        # 2D array: rows are the states, columns are the time points.
        # PM[s,n] is the metric for the most-likely path through the
        # trellis arriving at state s at time n.
        self.PM = numpy.zeros((self.nstates,max_n),dtype=numpy.float)

        # at time 0, the starting state is the most likely, the other
        # states are "infinitely" worse.
        self.PM[1:self.nstates,0] = 1000000

        # a 2D array: rows are the states, columns are the time
        # points, contents indicate the predecessor state for each
        # current state.
        self.Predecessor = numpy.zeros((self.nstates,max_n),
                                       dtype=numpy.int)

        # use the Viterbi algorithm to compute PM
        # incrementally from the received parity bits.
        n = 0
        for i in xrange(0,nreceived,self.r):
            n += 1

            # Fill in the next columns of PM, Predecessor based
            # on info in the next r incoming parity bits
            self.viterbi_step(n,received_voltages[i:i+self.r])

            # print out what was just added to the trellis state

        if debug:
             print "Final PM table \n"
             for curState in xrange(0,self.nstates) :
                for time in range(len(self.PM[curState,:])) :
                    if((self.PM[curState,time])>=1000000) :
                        print 'inf ',
                    else :
                        print '%3d ' % (self.PM[curState,time]) ,              # print all times for a given state as one row 
                print '\n'
             print "\n Final Predecessor table \n"
             for curState in xrange(0,self.nstates) :
                for time in range(len(self.Predecessor[curState,:])) :
                    print '%3d ' % (self.Predecessor[curState,time]) ,              # print all times for a given state as one row 
                print '\n'
             print "\n"

        # find the most-likely ending state from the last row
        # of the trellis
        s = self.most_likely_state(n)

        # reconstruct message by tracing the most likely path
        # back through the matrix using self.Predecessor.
        return self.traceback(s,n)

    # print out final path metrics
    def dump_state(self):
        print self.PM[:,-1]

if __name__=='__main__':
    constraint_len = 3; glist = (7,5,3)
    d = ViterbiDecoder(constraint_len, glist)

    # first test case: example from lecture
    message = [1,0,1,0,1,1,0,0]
    received = PS3_tests.convolutional_encoder(message, constraint_len, glist)
    i = 0
    print 'TEST', i
    decoded = numpy.array(d.decode(received, debug=True))
    print 'Testing without adding noise...'
    if (message == decoded).all() == True: 
        print 'Successfully decoded no-noise Test 0: congratulations!'
        print
    else:
        print 'Oops... error in decoding no-noise Test', i
        print 'Decoded as ', decoded
        print 'Correct is', message
        sys.exit(1)

    # second batch of test cases: different constraint lengths, generators
    nbits = 29
    message = numpy.random.random_integers(0,1,nbits)
    for (constraint_len, glist) in ((3, (7,5)), (4, (0xD,0xE))):
        i = i + 1
        print 'TEST', i
        d = ViterbiDecoder(constraint_len, glist)
        received = PS3_tests.convolutional_encoder(message, constraint_len, glist)
        decoded = numpy.array(d.decode(received, debug=True))
        if (message == decoded).all() == True: 
            print 'Successfully decoded no-noise Test', i, ': congratulations!'
            print
        else:
            print 'Oops... error in decoding no-noise Test', i
            print 'Decoded as', decoded
            print 'Correct is', message
            sys.exit(1)

    # now try some tests with noise
    PS3_tests.test_hard_metrics(ViterbiDecoder)
