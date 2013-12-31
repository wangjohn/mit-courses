#!/usr/bin/env python

import unittest
import sys
import glob
import re
from circuit2 import *

class Circuit2Test(unittest.TestCase):
  def setUp(self):
    dir = os.path.dirname(__file__)
    # Obtains a list of cross-platform test file paths.
    self._in_files = glob.glob(os.path.join(dir, 'tests', '*.in'))
    self._in_files.sort()
  
  def _cmp_lists(self, file, result_set):
    crossings = {}
    for crossing in result_set.crossings:
      key = tuple(crossing)
      if key in crossings:
        # Same crossing reported twice.
        return False
      crossings[key] = True
    
    crossing_count = len(crossings)
    while True:
      line = file.readline()
      if len(line) == 0:
        return crossing_count == 0
      key = tuple(line.split())
      if key in crossings:
        crossing_count -= 1
      else:
        return False

  def _cmp_counts(self, file, result):
    return int(file.readline()) == result

  def testCorrectness(self):
    print 'Testing correctness:'
    for in_filename in self._in_files:
      list_test = in_filename.find("list_") >= 0
      print 'Testing {0} ......'.format(os.path.basename(in_filename)),
      sys.stdout.flush()
      with open(in_filename) as in_file:
        layer = WireLayer.from_file(in_file)
        verifier = CrossVerifier(layer)
        if list_test:
          result = verifier.wire_crossings()
        else:
          result = verifier.count_crossings()
       
        gold_filename = re.sub('\.in$', '.gold', in_filename)
        with open(gold_filename) as gold_file:
          if list_test:
            same = self._cmp_lists(gold_file, result)
          else:
            same = self._cmp_counts(gold_file, result)
            
          if same:
            print 'OK'
          else: 
            print 'Failed'
          self.assertTrue(same)
    
if __name__ == '__main__':
  unittest.main()

