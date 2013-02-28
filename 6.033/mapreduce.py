# Single-machine but multi-process mapreduce library using python multiprocessing Pool.
# http://docs.python.org/2/library/multiprocessing.html#module-multiprocessing.pool
#
# Inspired by http://mikecvet.wordpress.com/2010/07/02/parallel-mapreduce-in-python, but
# this design follows the MapReduce paper more closely.
#
# The master (run()) creates a pool of processes and invokes maptask Map tasks.
# Each Map task applies Map() to 1/maptask-th of the input file, and partitions its
# output in reducetask regions, for a total of maptask x reducetask Reduce
# regions (each stored in a separate file). The master then creates reducetask
# Reduce tasks. Each Reduce task reads maptask regions, sorts the keys, and
# applies Reduce to each key, producing one output file. The reducetask output
# files can be merged by invoking Merge().

import sys
import os
import pickle
import string
import timeit
from multiprocessing import Pool

# A class for the MapReduce framwork
class MapReduce(object):

    def __init__(self, m, r, path):
        self.maptask = m
        self.reducetask = r
        self.path = path
        self.domap_counter = 0
        self.doreduce_counter = 0
        self.Split(path)

    # Splits input in mapworker temporary files, each with a keyvalue, respecting word boundaries
    # The keyvalue is the byte offset in the input file. User of class can overwrite the default.
    def Split(self, path):
        size = os.stat(self.path).st_size;
        chunk = size / self.maptask
        chunk += 1
        f = open(self.path, "r")
        buffer = f.read()
        f.close()
        f = open("#split-%s-%s" % (self.path, 0), "w+")
        f.write(str(0) + "\n")
        i = 0
        m = 1
        for c in buffer:
            f.write(c)
            i += 1
            if (c in string.whitespace) and (i > chunk * m):
                f.close()
                m += 1
                f = open("#split-%s-%s" % (self.path, m-1), "w+")
                f.write(str(i) + "\n")
        f.close()
            

    # Maps value into into a list of (key, value) pairs
    # To be defined by user of class
    def Map(self, keyvalue, value):
        pass

    # Determines the default reduce task that will receive (key, value)
    # User of class can overwrite the default.
    def Partition(self, item):
        return hash(item[0]) % self.reducetask

    # Reduces all pairs for one key [(key, value), ...])
    # To be defined by user of class
    def Reduce(self, key, keyvalues):
        pass

    # Optionally merge all reduce partitions into a single output file
    # A better implementation would do a merge sort of the reduce partitions,
    # since each partition has been sorted by key.
    def Merge(self):
        out = []
        for r in xrange(0, self.reducetask):
            f = open("#reduce-%s-%d" % (self.path, r), "r")
            out = out + pickle.load(f)
            f.close()
            os.unlink("#reduce-%s-%d" % (self.path, r))
        out = sorted(out, key=lambda pair: pair[0])
        return out

    # Load a mapper's split and apply Map to it
    def doMap(self, i):
        self.domap_counter += 1
        f = open("#split-%s-%s" % (self.path, i), "r")
        keyvalue = f.readline()
        value = f.read()
        f.close()
        os.unlink("#split-%s-%s" % (self.path, i))
        keyvaluelist = self.Map(keyvalue, value)
        for r in range(0, self.reducetask):
            # print "map", i, "#map-%s-%s-%d" % (self.path, i, r)
            f = open("#map-%s-%s-%d" % (self.path, i, r), "w+")
            itemlist = [item for item in keyvaluelist if self.Partition(item) == r]
            pickle.dump(itemlist, f)
            f.close()
        return [(i, r) for r in range(0, self.reducetask)]

    # Get reduce regions from maptasks, sort by key, and apply Reduce for each key
    def doReduce(self, i):
        self.doreduce_counter += 1
        keys = {}
        out = []
        for m in range(0, self.maptask):
            # print "reduce", i, "#map-%s-%s-%d" % (self.path, m, i)
            f = open("#map-%s-%s-%d" % (self.path, m, i), "r")
            itemlist = pickle.load(f)
            for item in itemlist:
                if keys.has_key(item[0]):
                    keys[item[0]].append(item)
                else:
                    keys[item[0]] = [item]
            os.unlink("#map-%s-%s-%d" % (self.path, m, i))
        for k in sorted(keys.keys()):
            out.append(self.Reduce(k, keys[k]))
        f = open("#reduce-%s-%d" % (self.path, i), "w+")
        pickle.dump(out, f)
        f.close()
        return i

    # The master.
    def run(self):
        pool = Pool(processes=max(self.maptask, self.reducetask),)
        regions = pool.map(self.doMap, range(0, self.maptask))
        partitions = pool.map(self.doReduce, range(0, self.reducetask))

# An instance of the MapReduce framework. It performs word count on title-cased words.
class WordCount(MapReduce):

    def __init__(self, maptask, reducetask, path):
        MapReduce.__init__(self,  maptask, reducetask, path)

    # Produce a (key, value) pair for each title word in value
    def Map(self, keyvalue, value):
        results = []
        i = 0
        n = len(value)
        while i < n:
            # skip non-ascii letters in C/C++ style a la MapReduce paper:
            while i < n and value[i] not in string.ascii_letters:
                i += 1
            start = i
            while i < n and value[i] in string.ascii_letters:
                i += 1
            w = value[start:i]
            if start < i and w.istitle():
                results.append ((w.lower(), 1))
        return results

    # Reduce [(key,value), ...]) 
    def Reduce(self, key, keyvalues):
        return (key, sum(pair[1] for pair in keyvalues))

# Python doesn't pickle method instance by default, so here you go:
def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)
import copy_reg
import types
copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)

def run_everything(m, r):
  # Create a WordCount MapReduce program
  wc = WordCount(4, 2, sys.argv[1])
  # Run it
  wc.run()
  # Merge out of Reduce tasks:
  out = wc.Merge()
  # Sort by word count:
  out = sorted(out, key=lambda pair: pair[1], reverse=True)

# Run WordCount instance
if __name__ == '__main__':
  if (len(sys.argv) != 2):
    print "Program requires path to file for reading!"
    sys.exit(1)

  for m in xrange(1,16,4):
    for r in xrange(1,16,4):
      print m, r
      print timeit.timeit("run_everything(%s, %s)" % (m, r), setup='from __main__ import run_everything', number=5)

