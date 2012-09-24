# Test file for 6.02 linear block codes lab
import operator
import math,numpy,random
from numpy import *

# return True if the binary sequence contains an even number of 1's
def even_parity(seq):
    return reduce(operator.xor,seq,0) == 0

def hamming(s1,s2):
    return sum(map(operator.xor,s1,s2))

def ber(xmit,received):
    return numpy.sum((xmit != received) * 1)/float(len(xmit))

# construct a (nrows*ncols+nrows+ncols,nrows*ncols,3) codeword
def codeword(data,nrows,ncols):
    result = data[:]
    # compute row parity bits
    for r in xrange(nrows):
        result.append(int(not even_parity(data[r*ncols:(r+1)*ncols])))
    # compute column parity bits
    for c in xrange(ncols):
        result.append(int(not even_parity(data[c:len(data):ncols])))
    return result

# convert integer to binary list of specified size (lsb first)
def int2bin(c,size=8):
    return [(c >> i) % 2 for i in xrange(size)]

def test_correct_errors(correct_errors):
    # test the decoder on a particular value, returns True if failed
    def run_test(test,nrows,ncols,expected,msg):
        result = correct_errors(test[:],nrows,ncols)
        if result != expected:
            print "Error detected while testing",msg
            print "Test code word:",test
            print "Expected:",expected
            print "Received:",result
            return True
        return False

    # test all 256 data values for 8 data bits
    print 'Testing all 2**n = 256 valid codewords'
    for i in xrange(256):
        data = int2bin(i)
        if run_test(codeword(data,2,4),2,4,data,"valid codewords"): return
    print '...passed'

    # test all single-bit errors (should be corrected)
    print 'Testing all possible single-bit errors'
    for count in range(10):
        good = codeword(int2bin((count*37 + 15) % 256),4,2)
        for i in xrange(14):
            bad = good[:]
            bad[i] ^= 1
            if run_test(bad,4,2,good[0:8],"correctable single-bit errors (bit %d)" % i): return
    print '...passed'
    print 'Testing all possible two-bit errors'
    for i in range(256):                    # all possible 8-bit messages
        good = codeword(int2bin(i),2,4)     # form a valid codeword, mimic TX
        for j in range(14):                 # 14 bits in total
            bad = good[:]
            bad[j] ^= 1                     # flip one of them
            for k in range(j,14) :          # pick another one to flip
               bad2=bad[:]
               bad2[k] ^= 1                 # flip that 
               if((j==8)or(j==9)) :         # check if j is a row parity bit
                 if ((k==10)or(k==11)or(k==12)or(k==13)) : # check if k is a col parity bit 
                      decResult=bad2[:]
                      decResult[(j-8)*4 + (k-10)] ^=1     # "simulate" the decoding. Luckily you are able to still triangulate though it's not ML
                      if run_test(bad2,2,4,decResult[0:8],"Two bit errors @(" +str(j)+ "," + str(k)+")" ): return
               else :
                 if run_test(bad2,2,4,bad2[0:8],"Two bit errors @(" +str(j)+ "," + str(k)+")" ): return
                                            # best effort here. Just return bits as is. 
    print '...passed'
    print '(8,4) rectangular parity code successfully passed all 0,1 and 2 bit error tests'

# construct a codeword with row and column parity
def codeword2(data,nrows,ncols):
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

def test_stream_decode(decoder,verbose=True):
    nrows = 2
    ncols = 2
    nbits = 59*nrows*ncols      # kind of a random choice (59)
    message = numpy.random.random_integers(0,1,nbits)
    cw = []
    for i in range(0,nbits,nrows*ncols):
        cw.extend(codeword2(message[i:i+nrows*ncols], nrows, ncols))
    result = decoder(numpy.array(cw), nrows, ncols)
    if numpy.any(result != message):
        print "Error detected while testing", message
        print "Decoded wrongly as", result
        print "The correct codeword is", cw
        return False

    nrows = 4
    ncols = 3
    nbits = 39*nrows*ncols      # kind of a random choice (39)
    message = numpy.random.random_integers(0,1,nbits)
    cw = []
    for i in range(0,nbits,nrows*ncols):
        cw.extend(codeword2(message[i:i+nrows*ncols], nrows, ncols))
    result = decoder(cw, nrows, ncols)
    if numpy.any(result != message):
        print "Error detected while testing", message
        print "Decoded wrongly as", result
        print "The correct codeword is", cw
        return False

    if verbose: print "***Stream decoding succeeded***"
    return True

# For testing: generate all codewords of n bits in a list of lists, where each
# list has length n.  There are 2**n lists in the list of lists being returned.
def all_codewords(n):
    words = []
    c = [0]*n
    for i in range(2**n):
        for j in range(n):
            c[j] = 1 if (i & (2**j)) else 0
        words.append(list(c))
    return words

# def eqlist(a, b):
#     for i in range(len(a)):
#         if a[i] != b[i]:
#             return False
#     return True

def eqlist(a, b):
    if (a==b).all():
        return True
    return False
    
# Traverse an integer matrix A and replace each entry with its modulo 2 value.
# All your base belong to 2. :-)
def mod2(A):
    for i in range(2):
        A[A%2==i] = i
    return A

def all_valid_codewords(n, k, G):
    C = numpy.mat([0]*(n))
    for i in range(1, 2**k):
        data = int2bin(i,k)
        cw = numpy.matrix(data) * G
        C = numpy.vstack([C, cw])
    return mod2(C)

def test_linear_sec(decoder, n, k, G):
    print 'Testing all 2**k =', 2**k, 'valid codewords'
    C = all_valid_codewords(n, k, G)
    for i in range(2**k):
        cw = numpy.array(C[i:i+1].flatten()[0].tolist()[0])
        d = decoder(cw, n, k, G)
        if not eqlist(d, cw[:k]):
            print 'In code with generator matrix', G
            print 'Error decoding', cw, 'Expected', cw, 'got', d
            return
#        print cw, '... passed'
    print '...passed'
    print 'Testing all n*2**k =', n*2**k, 'single-bit error codewords'
    for i in range(2**k):
        cw = numpy.array(C[i:i+1].flatten()[0].tolist()[0])
        for j in range(n):
            test = 1*cw         # copy of cw
            test[j] ^= 1
            storetest = 1*test
            d = decoder(test, n, k, G)
            if not eqlist(d, cw[:k]):
                print 'In code with generator matrix'
                print G
                print 'OOPS: Error decoding', storetest, '...expected', cw[:k], 'got', d
                return
#            print test, '... passed'
            
    print '...passed'
    print "All 0 and 1 error tests passed for (%d,%d,3) code with generator matrix G =" % (n, k)
    print G
