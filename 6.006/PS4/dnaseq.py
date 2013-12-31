#!/usr/bin/env python2.7

import unittest
from dnaseqlib import *

### Utility classes ###

# Maps integer keys to a set of arbitrary values.
class Multidict:
    # Initializes a new multi-value dictionary, and adds any key-value
    # 2-tuples in the iterable sequence pairs to the data structure.
    def __init__(self, pairs=[]):
        # Initialize dictionary
        self.dict = {}
        length = len(pairs)
        if length != 0:
            for i in range(length):
                self.put(pairs[i][0], pairs[i][1])
        
    # Associates the value v with the key k.
    def put(self, k, v):
        try:
            self.dict[k].append(v)
        except KeyError:
            self.dict[k] = [v]
        
    # Gets any values that have been associated with the key k; or, if
    # none have been, returns an empty sequence.
    def get(self, k):
        try:
            return self.dict[k]
        except KeyError:
            return []

    # Gets all the key, value pairs in the dictionary
    def get_dict(self):
        output = []
        for key in self.dict:
            for j in self.dict[key]:
                output.append( (key, j) )
        return output

class DNADictionary(Multidict):

    def put(self, k, v, subdict):
        if subdict == 'a':
            try:
                self.dict[k][0].append(v)
            except KeyError:
                self.dict[k] = [[v], []]
        else:
            self.dict[k][1].append(v)

    def get_indices(self):
        for key in self.dict:
            if len(self.dict[key][1]) > 0: 
                for aval in self.dict[key][0]:
                    for bval in self.dict[key][1]:
                        yield (aval, bval)
                    

# Given a sequence of nucleotides, return all k-length subsequences
# and their hashes.  (What else do you need to know about each
# subsequence?)
def subsequenceHashes(seq, k):
    current = PushQueue()
    index = 0
    for i in seq:
        if index < k:
            current.add(i)
            if len(current) == k:
                h = RollingHash(current.get_all())
                yield h.current_hash(), current.get_all(), index - k + 1
        else:
            out = current.push(i)
            h.slide(out, i)
            yield h.current_hash(), current.get_all(), index - k + 1
        index += 1
    

# Similar to subsequenceHashes(), but returns one k-length subsequence
# every m nucleotides.  (This will be useful when you try to use two
# whole data files.)
def intervalSubsequenceHashes(seq, k, m):
    current = PushQueue()
    index = 0
    mod = 0
    out = ''
    for i in seq:
        index += 1
        if index <= k:
            current.add(i)
            if len(current) == k:
                h = RollingHash(current.get_all())
                yield h.current_hash(), current.get_all(), index - k 
        else:
            out += current.push(i)
            h.slide(out[-1], i)
            if (index  - k) % m  == 0:
                yield h.current_hash(), current.get_all(), index - k 
                out = ''  

# Searches for commonalities between sequences a and b by comparing
# subsequences of length k.  The sequences a and b should be iterators
# that return nucleotides.  The table is built by computing one hash
# every m nucleotides (for m >= k).
def getExactSubmatches(a, b, k, m):
    d = DNADictionary()
    for i in intervalSubsequenceHashes(a, k, m):
        d.put((i[0], i[1]), i[2], 'a')
    for j in subsequenceHashes(b, k):
        if d.get((j[0], j[1])) != []:
            d.put((j[0], j[1]), j[2], 'b')
    return d.get_indices()


# Create a Queue
class QueueObject(object):
    """ Object for creating a Queue. """
    def __init__(self, value, left = None, right = None):
        self.right = right
        self.left = left
        self.value = str(value)
        
    def disconnect(self):
        self.right = None
        self.left = None

class PushQueue(object):
    """ Queue for pushing and popping items. """
    def __init__(self, first_obj = 'None'):
        self.first = QueueObject(first_obj)
        self.last = self.first

    def __len__(self):
        index = 0
        obj = self.first
        while obj != self.last:
            index += 1
            obj = obj.right
        return index + 1

    def add(self, obj):
        if  self.first.value == 'None' and self.last == self.first:
            self.first.disconnect()
            self.first = QueueObject(value = obj, left = self.last)
            self.last = self.first
        else:
            self.last.right = QueueObject(value = obj, left = self.last)
            self.last = self.last.right

    def push(self, obj):
        self.add(obj)
        old_first = self.first
        new_first = self.first.right
        
        self.first = new_first
        new_first.left = None
        old_first.disconnect()

        return old_first.value

    def get_all(self):
        output = []
        obj = self.first
        while obj != self.last:
            output.append(obj.value)
            obj = obj.right
        output.append(self.last.value)
        return ''.join(output)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage: {0} [file_a.fa] [file_b.fa] [output.png]'.format(sys.argv[0])
        sys.exit(1)

    # The arguments are, in order: 1) Your getExactSubmatches
    # function, 2) the filename to which the image should be written,
    # 3) a tuple giving the width and height of the image, 4) the
    # filename of sequence A, 5) the filename of sequence B, 6) k, the
    # subsequence size, and 7) m, the sampling interval for sequence
    # A.
    compareSequences(getExactSubmatches, sys.argv[3], (500,500), sys.argv[1], sys.argv[2], 8, 100)
