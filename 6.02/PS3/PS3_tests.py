import numpy,operator

# compute hamming distance of two bit sequences
def hamming(s1,s2):
    return sum(map(operator.xor,s1,s2))

# xor together all the bits in an integer
def xorbits(n):
    result = 0
    while n > 0:
        result ^= (n & 1)
        n >>= 1
    return result

def expected_parity(from_state,to_state,k,glist):
    # x[n] comes from to_state
    # x[n-1] ... x[n-k-1] comes from from_state
    x = ((to_state >> (k-2)) << (k-1)) + from_state
    return [xorbits(g & x) for g in glist]

def convolutional_encoder(bits, K, glist):
    result = [0] * (len(bits)*len(glist))
    state = 0
    index = 0
    for b in bits:
        state = (b << (K-1)) + (state >> 1)
        for g in glist:
            result[index] = xorbits(state & g)
            index += 1
    return numpy.array(result, dtype=numpy.float)

def ber(xmit,received):
    return numpy.sum((xmit != received) * 1)/float(len(xmit))

def test_hard_metrics(decoder,debug=False):
    k = 3
    glist = (7,6)
    d = decoder(k,glist)

    # message with no errors
    message = numpy.random.random_integers(0,1,10)
    sent = convolutional_encoder(message,k,glist)
    received_message = d.decode(sent,debug=debug)
    if numpy.any(message != received_message):
        print "Decoder testing failed (no transmission errors)..."
        print "Received parity bits:",sent
        print "Decoded message returned by your decoder: ",received_message
        print "Expected:",message
        return

    # message with two transmission errors
    sent[3] = 1 - sent[3]
    sent[12] = 1 - sent[12]
    received_message = d.decode(sent,debug=debug)
    if numpy.any(message != received_message):
        print "Decoder testing failed (2 transmission errors)..."
        print "Received parity bits:",sent
        print "Decoded message returned by your decoder: ",received_message
        print "Expected:",message
        return

    print "Hard-metric Viterbi decoder tests complete!"

def test_soft_metrics(decoder):
    k = 3
    glist = (7,6)
    d = decoder(k,glist)
    for i in xrange(10):
        expected = numpy.random.random_integers(0,1,len(glist))
        received = numpy.random.rand(len(glist))
        dist = d.branch_metric(expected,received)
        expected_dist = sum([(expected[j] - received[j])**2 for j in xrange(len(glist))])
        if numpy.any((dist - expected_dist) > 1e-5):
            print "soft branch_metric failed..."
            print "expected voltages:",expected
            print "received voltages:",received
            print "value returned by branch_metric:",dist
            print "expected return value:",expected_dist
            return
    print "Soft-metric Viterbi decoder tests complete!"

# compute even parity for a binary sequence (a list of 0's and 1's).
# returns 0 if the number of 1's in data is even, else 1
def even_parity(data):
    return sum(data) % 2

# construct a codeword with row and column parity
def codeword(data,nrows,ncols):
    ndata = len(data)
    assert ndata == nrows*ncols,"codeword: data must have nrows*ncols bits"
    result = numpy.zeros(ndata + nrows + ncols,dtype=int)
    result[:ndata] = data
    # compute row parity bits
    for r in xrange(nrows):
        result[ndata + r] = even_parity(data[r*ncols:(r+1)*ncols])
    # compute column parity bits
    for c in xrange(ncols):
        result[ndata + nrows + c] = even_parity(data[c:len(data):ncols])
    return result

# decode stream of blocks using rectangular code decoder.
# each block has nrows*ncols + nrows + ncols bits
def decode_blocks(decoder,stream,nrows,ncols):
    result = []
    index = 0
    while index < len(stream):
        end = index + nrows*ncols + nrows + ncols
        result.extend(decoder(stream[index:end],nrows,ncols))
        index = end
    return result

# convert nbits of int into bit sequences, lsb first
def int_to_bits(n,nbits):
    return [(n >> i) & 1 for i in xrange(nbits)]

# convert bit sequence (lsb first) to an int
def bits_to_int(bits):
    result = 0
    for i in xrange(len(bits)):
        result += bits[i] * (1 << i)
    return int(result)
