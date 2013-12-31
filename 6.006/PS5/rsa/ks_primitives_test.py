#!/usr/bin/env python

import os
import unittest

if os.environ.get('KS_DEBUG') and os.environ.get('KS_DEBUG') != 'false':
  from ks_primitives import *
else:
  from ks_primitives_unchecked import *

class ByteTest(unittest.TestCase):
  def test_equality(self):
    self.assertEqual(Byte.zero(), Byte.zero(), '0 == 0')
    self.assertEqual(Byte.one(), Byte.one(), '0 == 0')
    self.assertNotEqual(Byte.zero(), Byte.one(), '0 != 1')
    self.assertNotEqual(Byte.one(), Byte.zero(), '1 != 0')

  def test_comparisons(self):
    self.assertGreater(Byte.one(), Byte.zero(), '1 > 0')
    self.assertFalse(Byte.zero() > Byte.one(), 'not (0 > 1)')
    self.assertGreaterEqual(Byte.one(), Byte.zero(), '1 >= 0')
    self.assertGreaterEqual(Byte.one(), Byte.one(), '1 >= 1')
    self.assertLess(Byte.zero(), Byte.one(), '0 < 1')
    self.assertFalse(Byte.one() < Byte.zero(), 'not (0 < 1)')
    self.assertLessEqual(Byte.zero(), Byte.one(), '0 <= 1')
    self.assertLessEqual(Byte.one(), Byte.one(), '1 <= 1')
    
  def test_strings(self):
    self.assertEqual(Byte.one().hex(), '01')
    self.assertEqual(str(Byte.one()), '0x01')
    self.assertEqual(repr(Byte.one()), 'Byte.h("01")',)
    self.assertEqual(Byte.from_hex('01'), Byte.one())
    self.assertEqual(Byte.h('00'), Byte.zero())
    self.assertEqual(Byte.h('F1').hex(), 'F1')
    
  def test_addition(self):
    self.assertEqual(Byte.zero() + Byte.zero(), Word.zero(), '0 + 0 == 0')
    self.assertEqual(Byte.one() + Byte.zero(), Word.one(), '1 + 0 == 1')
    self.assertEqual(Byte.zero() + Byte.one(), Word.one(), '0 + 1 == 1')
    self.assertEqual(Byte.h('5A') + Byte.h('A5'), Word.h('00FF'))
    self.assertEqual(Byte.h('FF') + Byte.h('FF'), Word.h('01FE'))

  def test_subtraction(self):
    self.assertEqual(Byte.zero() - Byte.zero(), Word.zero(), '0 - 0 == 0')
    self.assertEqual(Byte.one() - Byte.zero(), Word.one(), '1 - 0 == 1')
    self.assertEqual(Byte.one() - Byte.one(), Word.zero(), '1 - 1 == 0')
    self.assertEqual(Byte.h('A5') - Byte.h('5A'), Word.h('004B'))
    self.assertEqual(Byte.h('5A') - Byte.h('A5'), Word.h('FFB5'))
    self.assertEqual(Byte.h('FF') - Byte.h('FF'), Word.h('0000'))

  def test_multiplication(self):
    self.assertEqual(Byte.zero() * Byte.zero(), Word.zero(), '0 * 0 == 0')
    self.assertEqual(Byte.zero() * Byte.one(), Word.zero(), '0 * 1 == 0')
    self.assertEqual(Byte.one() * Byte.one(), Word.one(), '1 * 1 == 0')
    self.assertEqual(Byte.h('A5') * Byte.h('5A'), Word.h('3A02'))
    self.assertEqual(Byte.h('FF') * Byte.h('FF'), Word.h('FE01'))
    
  def test_division(self):
    self.assertEqual(Byte.one() // Byte.one(), Byte.one(), '1 // 1 == 1')
    self.assertEqual(Byte.zero() // Byte.one(), Byte.zero(), '0 // 1 == 0')
    self.assertEqual(Byte.h('42') // Byte.h('03'), Byte.h('16'))
    self.assertEqual(Byte.h('43') // Byte.h('03'), Byte.h('16'))    

  def test_modulo(self):
    self.assertEqual(Byte.one() % Byte.one(), Byte.zero(), '1 % 1 == 0')
    self.assertEqual(Byte.zero() % Byte.one(), Byte.zero(), '0 % 1 == 0')
    self.assertEqual(Byte.h('42') % Byte.h('03'), Byte.zero())
    self.assertEqual(Byte.h('43') % Byte.h('03'), Byte.one())    
    self.assertEqual(Byte.h('44') % Byte.h('03'), Byte.h('02'))    

  def test_and(self):
    self.assertEqual(Byte.one() & Byte.one(), Byte.one(), '1 & 1 == 1')
    self.assertEqual(Byte.one() & Byte.zero(), Byte.zero(), '1 & 0 == 0')
    self.assertEqual(Byte.zero() & Byte.zero(), Byte.zero(), '0 & 0 == 0')
    self.assertEqual(Byte.h('5F') & Byte.h('6A'), Byte.h('4A'))

  def test_or(self):
    self.assertEqual(Byte.one() | Byte.one(), Byte.one(), '1 | 1 == 1')
    self.assertEqual(Byte.one() | Byte.zero(), Byte.one(), '1 | 0 == 1')
    self.assertEqual(Byte.zero() | Byte.zero(), Byte.zero(), '0 | 0 == 0')
    self.assertEqual(Byte.h('5F') | Byte.h('6A'), Byte.h('7F'))

  def test_xor(self):
    self.assertEqual(Byte.one() ^ Byte.one(), Byte.zero(), '1 ^ 1 == 0')
    self.assertEqual(Byte.one() ^ Byte.zero(), Byte.one(), '1 ^ 0 == 1')
    self.assertEqual(Byte.zero() ^ Byte.zero(), Byte.zero(), '0 ^ 0 == 0')
    self.assertEqual(Byte.h('5F') ^ Byte.h('6A'), Byte.h('35'))

class WordTest(unittest.TestCase):
  def test_equality(self):
    self.assertEqual(Word.zero(), Word.zero(), '0 == 0')
    self.assertEqual(Word.one(), Word.one(), '0 == 0')
    self.assertNotEqual(Word.zero(), Word.one(), '0 != 1')
    self.assertNotEqual(Word.one(), Word.zero(), '1 != 0')
    
  def test_equality_vs_byte(self):
    self.assertNotEqual(Word.zero(), Byte.zero(), '(Word)0 != (Byte)0')
    self.assertNotEqual(Word.one(), Byte.one(), '(Word)1 != (Byte)1')

  def test_comparisons(self):
    self.assertGreater(Word.one(), Word.zero(), '1 > 0')
    self.assertFalse(Word.zero() > Word.one(), 'not (0 > 1)')
    self.assertGreaterEqual(Word.one(), Word.zero(), '1 >= 0')
    self.assertGreaterEqual(Word.one(), Word.one(), '1 >= 1')
    self.assertLess(Word.zero(), Word.one(), '0 < 1')
    self.assertFalse(Word.one() < Word.zero(), 'not (0 < 1)')
    self.assertLessEqual(Word.zero(), Word.one(), '0 <= 1')
    self.assertLessEqual(Word.one(), Word.one(), '1 <= 1')
    
  def test_strings(self):
    self.assertEqual(Word.one().hex(), '0001')
    self.assertEqual(str(Word.one()), '0x0001')
    self.assertEqual(repr(Word.one()), 'Word.h("0001")',)
    self.assertEqual(Word.from_hex('0001'), Word.one())
    self.assertEqual(Word.h('0000'), Word.zero())
    self.assertEqual(Word.h('FE12').hex(), 'FE12')
    
  def test_addition(self):
    self.assertEqual(Word.zero() + Word.zero(), Word.zero(), '0 + 0 == 0')
    self.assertEqual(Word.one() + Word.zero(), Word.one(), '1 + 0 == 1')
    self.assertEqual(Word.zero() + Word.one(), Word.one(), '0 + 1 == 1')
    self.assertEqual(Word.h('1234') + Word.h('5678'), Word.h('68AC'))
    self.assertEqual(Word.h('FFFF') + Word.h('FFFF'), Word.h('FFFE'))

  def test_subtraction(self):
    self.assertEqual(Word.zero() - Word.zero(), Word.zero(), '0 - 0 == 0')
    self.assertEqual(Word.one() - Word.zero(), Word.one(), '1 - 0 == 1')
    self.assertEqual(Word.one() - Word.one(), Word.zero(), '1 - 1 == 0')
    self.assertEqual(Word.zero() - Word.one(), Word.h('FFFF'))
    self.assertEqual(Word.h('5678') - Word.h('4321'), Word.h('1357'))
    self.assertEqual(Word.h('4321') - Word.h('5678'), Word.h('ECA9'))

  def test_division(self):
    self.assertEqual(Word.one() // Byte.one(), Byte.one(), '1 // 1 == 1')
    self.assertEqual(Word.zero() // Byte.one(), Byte.zero(), '0 // 1 == 0')
    self.assertEqual(Word.h('4321') // Byte.h('56'), Byte.h('C7'))
    self.assertEqual(Word.h('3A02') // Byte.h('A5'), Byte.h('5A'))
    self.assertEqual(Word.h('FE01') // Byte.h('FF'), Byte.h('FF'))
    self.assertEqual(Word.h('4321') // Byte.one(), Byte.h('21'))

  def test_modulo(self):
    self.assertEqual(Word.one() % Byte.one(), Byte.zero(), '1 % 1 == 0')
    self.assertEqual(Word.zero() % Byte.one(), Byte.zero(), '0 % 1 == 0')
    self.assertEqual(Word.h('4321') % Byte.h('56'), Byte.h('47'))
    self.assertEqual(Word.h('3A02') % Byte.h('A5'), Byte.zero())    
    self.assertEqual(Word.h('4321') % Byte.one(), Byte.zero())    
    self.assertEqual(Word.h('FEFF') % Byte.h('FF'), Byte.h('FE'))

  def test_and(self):
    self.assertEqual(Word.one() & Word.one(), Word.one(), '1 & 1 == 1')
    self.assertEqual(Word.one() & Word.zero(), Word.zero(), '1 & 0 == 0')
    self.assertEqual(Word.zero() & Word.zero(), Word.zero(), '0 & 0 == 0')
    self.assertEqual(Word.h('125F') & Word.h('346A'), Word.h('104A'))

  def test_or(self):
    self.assertEqual(Word.one() | Word.one(), Word.one(), '1 | 1 == 1')
    self.assertEqual(Word.one() | Word.zero(), Word.one(), '1 | 0 == 1')
    self.assertEqual(Word.zero() | Word.zero(), Word.zero(), '0 | 0 == 0')
    self.assertEqual(Word.h('125F') | Word.h('346A'), Word.h('367F'))

  def test_xor(self):
    self.assertEqual(Word.one() ^ Word.one(), Word.zero(), '1 ^ 1 == 0')
    self.assertEqual(Word.one() ^ Word.zero(), Word.one(), '1 ^ 0 == 1')
    self.assertEqual(Word.zero() ^ Word.zero(), Word.zero(), '0 ^ 0 == 0')
    self.assertEqual(Word.h('125F') ^ Word.h('346A'), Word.h('2635'))


if __name__ == '__main__':
  unittest.main()
