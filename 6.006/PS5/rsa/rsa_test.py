#!/usr/bin/env python

import unittest
import sys
import glob
import re

from rsa import *

class RsaTest(unittest.TestCase):
  def setUp(self):
    dir = os.path.dirname(__file__)
    # Obtains a list of cross-platform test file paths.
    self._in_files = glob.glob(os.path.join(dir, 'tests', '*.in'))
    self._in_files.sort()
  
  def _cmp_files(self, file, lines):
    for line in lines:
      if line != file.readline().strip():
        return False
    return file.readline() == ''

  def testCorrectness(self):
    print('Testing correctness:')
    for in_filename in self._in_files:
      test_name = os.path.basename(in_filename)
      sys.stdout.write('Testing {0} ...... '.format(test_name))
      sys.stdout.flush()
      with open(in_filename) as in_file:
        image = EncryptedImage.from_file(in_file)
        out_lines = image.to_line_list()
       
        gold_filename = re.sub('\.in$', '.gold', in_filename)
        with open(gold_filename) as gold_file:
          same = self._cmp_files(gold_file, out_lines)
          if same:
            sys.stdout.write('OK\n')
          else: 
            sys.stdout.write('Failed\n')
          self.assertTrue(same)
  
if __name__ == '__main__':
    unittest.main()
