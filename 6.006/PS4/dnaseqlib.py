import sys
import math
import kfasta
from array import array
try:
    from PIL import Image
except ImportError:
    print "You don't have PIL (the Python Imaging Library) installed."
    print "Please check README.txt for instructions on how to install PIL."
    sys.exit(-1)

# Produces hash values for a rolling sequence.
class RollingHash:
    def __init__(self, s):
        self.HASH_BASE = 7
        self.seqlen = len(s)
        n = self.seqlen - 1
        h = 0
        for c in s:
            h += ord(c) * (self.HASH_BASE ** n)
            n -= 1
        self.curhash = h

    # Returns the current hash value.
    def current_hash(self):
        return self.curhash

    # Updates the hash by removing previtm and adding nextitm.  Returns the updated
    # hash value.
    def slide(self, previtm, nextitm):
        self.curhash = (self.curhash * self.HASH_BASE) + ord(nextitm)
        self.curhash -= ord(previtm) * (self.HASH_BASE ** self.seqlen)
        return self.curhash

# A simple 2D integer array implementation on top of Python's built-in 1D array.
class Array2D:
    def __init__(self, typecode, w, h, defaultval):
        self.arr = array(typecode, [defaultval]*(w*h))
        self.w = w
        self.h = h
    def put(self, x, y, v):
        assert x >= 0 and x < self.w
        assert y >= 0 and y < self.h
        self.arr[(y*self.w)+x] = v
    def incr(self, x, y):
        assert x >= 0 and x < self.w
        assert y >= 0 and y < self.h
        self.arr[(y*self.w)+x] += 1
    def get(self, x, y):
        assert x >= 0 and x < self.w
        assert y >= 0 and y < self.h
        return self.arr[(y*self.w)+x]
    def max(self):
        return max(self.arr)

### High-level driver code.  You shouldn't have to tweak this. ###

# Given a sequence of matches, produces a w-by-h image and saves it to filename.
# The remapping function takes values in (0,1) and returns values in (0,1); the default
# value (fourth-root) makes lightly-populated bins considerably darker.
def buildComparisonImage(filename, w, h, alen, blen, matches, remapfn=lambda x:math.sqrt(math.sqrt(x))):
    arr = Array2D('L', w, h, 0L)
    print "Sequence A length: " + str(alen)
    print "Sequence B length: " + str(blen)
    abinsize = int(math.ceil(alen / float(w)))
    bbinsize = int(math.ceil(blen / float(h)))
    assert abinsize > 0 and bbinsize > 0
    print "Binning matches..."
    for m in matches:
        #print m, (abinsize, bbinsize), (m[0]//abinsize, m[1]//bbinsize), (w, h)
        arr.incr(m[0] // abinsize, m[1] // bbinsize)
    print "...done binning matches."
    print "Normalizing and plotting results..."
    maxval = float(arr.max())
    img = Image.new('RGB', (w,h))
    for y in range(0, h):
        for x in range(0, w):
            val = 255 - int(math.ceil(remapfn((arr.get(x,y) / maxval)) * 255.0))
            img.putpixel((x,y), (val,val,val))
    print "...done normalizing and plotting."
    img.save(filename)

def compareSequences(getExactSubmatches, imgfile, imgsize, afile, bfile, k, m):
    a = kfasta.FastaSequence(afile)
    b = kfasta.FastaSequence(bfile)
    matches = getExactSubmatches(a, b, k, m)
    buildComparisonImage(imgfile, imgsize[0], imgsize[1],
                         kfasta.getSequenceLength(afile),
                         kfasta.getSequenceLength(bfile), matches)
