#!/usr/bin/env python

import unittest
import sys
import glob
import re
from circuit import *

class CircuitTest(unittest.TestCase):
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
        print 'Testing correctness:'
        for in_filename in self._in_files:
            print 'Testing {0} ......'.format(os.path.basename(in_filename)),
            sys.stdout.flush()
            with open(in_filename) as in_file:
                sim = Simulation.from_file(in_file)
                sim.run()
                out_lines = sim.outputs_to_line_list()
               
                gold_filename = re.sub('\.in$', '.gold', in_filename)
                with open(gold_filename) as gold_file:
                    same = self._cmp_files(gold_file, out_lines)
                    if same:
                        print 'OK'
                    else: 
                        print 'Failed'
                    self.assertTrue(same)
    
if __name__ == '__main__':
    unittest.main()

