
#
# Simple FASTA-reading library
# Copyright 2010 Kevin Kelley <kelleyk@kelleyk.net>
#
# Provided under the MIT license: yours gratis,
# and if it breaks, you get to keep both pieces.
#

import unittest

# An iterator that returns the nucleotide sequence stored in the given FASTA file.
class FastaSequence:
    def __init__(self, filename):
        self.f = open(filename, 'r')
        self.buf = ''
        self.info = self.f.readline()
        self.pos = 0
    def __iter__(self):
        return self
    def next(self):
        while '' == self.buf:
            self.buf = self.f.readline()
            if '' == self.buf:
                self.f.close()
                raise StopIteration
            self.buf = self.buf.strip()
        nextchar = self.buf[0]
        self.buf = self.buf[1:]
        self.pos += 1
        return nextchar

def getSequenceLength(filename):
    seq = FastaSequence(filename)
    n = 0
    for x in seq:
        n += 1
    return n

# Returns all subsequences of length k in seq.
def subsequences(seq, k):
    try:
        subseq = ''
        while True:
            while len(subseq) < k:
                subseq += seq.next()
            yield subseq
            subseq = subseq[1:]
    except StopIteration:
        return

# Simple sanity checks
class TestKFASTA(unittest.TestCase):
    def test_readseq(self):
        seq = FastaSequence('trivial.fa')
        seqstr = ''
        for c in seq:
            seqstr += c
        self.assertTrue('ABCDEFGHIJKLMNOPQRSTUVWXYZ' == seqstr)
    def test_subseq(self):
        seq = FastaSequence('trivial.fa')
        i = 0
        for subseq in subsequences(seq, 3):
            print subseq
            i += 1
        self.assertTrue(24 == i)
#if __name__ == '__main__':
#    unittest.main()
