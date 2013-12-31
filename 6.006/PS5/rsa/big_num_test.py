#!/usr/bin/env python

import unittest
import os

if os.environ.get('SOLUTION'):
  from big_num_full import *
else:
  from big_num import *

class BigNumTest(unittest.TestCase):
  def test_equality(self):
    self.assertEqual(BigNum.zero(1), BigNum.zero(1))
    self.assertEqual(BigNum.zero(1), BigNum.zero(2))
    self.assertEqual(BigNum.one(1), BigNum.one(1))
    self.assertEqual(BigNum.one(1), BigNum.one(2))
    self.assertNotEqual(BigNum.zero(1), BigNum.one(1))
    self.assertNotEqual(BigNum.zero(1), BigNum.one(2))
    self.assertNotEqual(BigNum.zero(2), BigNum.one(1))
    self.assertNotEqual(BigNum.zero(2), BigNum.one(2))
    
  def test_strings(self):
    self.assertEqual(BigNum.zero(1).hex(), '00')
    self.assertEqual(BigNum.zero(3).hex(), '00')
    self.assertEqual(BigNum.one(1).hex(), '01')
    self.assertEqual(BigNum.one(3).hex(), '01')
    self.assertEqual(str(BigNum.one(3)), '0x01')
    self.assertEqual(repr(BigNum.one(1)), 'BigNum.h("01", 1)')
    self.assertEqual(repr(BigNum.one(3)), 'BigNum.h("01", 3)')
    self.assertEqual(BigNum.from_hex('01'), BigNum.one())
    self.assertEqual(BigNum.h('00'), BigNum.zero())
    self.assertEqual(BigNum.from_hex('00F1E2D3C4B5').hex(), 'F1E2D3C4B5')
    
  def test_is_normalized(self):
    self.assertTrue(BigNum.zero(1).is_normalized())
    self.assertFalse(BigNum.zero(2).is_normalized())
    self.assertTrue(BigNum.one(1).is_normalized())
    self.assertFalse(BigNum.one(2).is_normalized())
    self.assertTrue(BigNum.h('100').is_normalized())
    self.assertTrue(BigNum.h('0100').is_normalized())
    self.assertFalse(BigNum.h('00101').is_normalized())

  def test_normalize(self):
    self.assertEqual(repr(BigNum.one(1).normalize()), 'BigNum.h("01", 1)')
    self.assertEqual(repr(BigNum.one(3).normalize()), 'BigNum.h("01", 1)')
    self.assertEqual(repr(BigNum.zero(1).normalize()), 'BigNum.h("00", 1)')
    self.assertEqual(repr(BigNum.zero(3).normalize()), 'BigNum.h("00", 1)')

  def test_comparisons(self):
    self.assertLess(BigNum.zero(), BigNum.one())
    self.assertLessEqual(BigNum.zero(), BigNum.one())
    self.assertLessEqual(BigNum.zero(), BigNum.zero())
    self.assertLessEqual(BigNum.one(), BigNum.one())
    self.assertGreater(BigNum.one(), BigNum.zero())
    self.assertGreaterEqual(BigNum.one(), BigNum.zero())
    self.assertGreaterEqual(BigNum.zero(), BigNum.zero())
    self.assertGreaterEqual(BigNum.one(), BigNum.one())
    
    self.assertLess(BigNum.h('11FF'), BigNum.h('1200'))
    self.assertLess(BigNum.h('11FE'), BigNum.h('11FF'))
    self.assertLess(BigNum.h('10FE'), BigNum.h('1100'))
    self.assertLess(BigNum.h('FF11'), BigNum.h('10000'))
    self.assertFalse(BigNum.h('1200') < BigNum.h('001200'))
    self.assertLessEqual(BigNum.h('11FF'), BigNum.h('1200'))
    self.assertLessEqual(BigNum.h('11FE'), BigNum.h('11FF'))
    self.assertLessEqual(BigNum.h('10FE'), BigNum.h('1100'))
    self.assertLessEqual(BigNum.h('FF11'), BigNum.h('10000'))
    self.assertLessEqual(BigNum.h('1200'), BigNum.h('001200'))

  def test_shifting(self):
    self.assertEqual(BigNum.h('1234567') >> 2, BigNum.h('123'))
    self.assertEqual(BigNum.h('1234567') >> 0, BigNum.h('1234567'))
    self.assertEqual(BigNum.h('1234567') >> 4, BigNum.zero())
    self.assertEqual(BigNum.h('1234567') >> 5, BigNum.zero())
    self.assertEqual(BigNum.h('12345') << 1, BigNum.h('1234500'))
    self.assertEqual(BigNum.h('12345') << 2, BigNum.h('123450000'))
    self.assertEqual(BigNum.h('12345') << 0, BigNum.h('12345'))
    self.assertEqual(BigNum.one() << 6, BigNum.h('1000000000000'))
  
  def test_addition(self):
    self.assertEqual(BigNum.zero() + BigNum.zero(), BigNum.zero())
    self.assertEqual(BigNum.one() + BigNum.zero(), BigNum.one())
    self.assertEqual(BigNum.zero() + BigNum.one(), BigNum.one())
    self.assertEqual(BigNum.h('1234') + BigNum.h('5678'), BigNum.h('68AC'))
    self.assertEqual(BigNum.h('1234') + BigNum.h('56789A'), BigNum.h('568ACE'))
    self.assertEqual(BigNum.one() + BigNum.h('FFFFFF'), BigNum.h('1000000'))
    self.assertEqual(BigNum.h('FEFDFC') + BigNum.h('FBFAF9F8'),
                     BigNum.h('FCF9F7F4'))

  def test_subtraction(self):
    self.assertEqual(BigNum.zero() - BigNum.zero(), BigNum.zero())
    self.assertEqual(BigNum.one() - BigNum.zero(), BigNum.one())
    self.assertEqual(BigNum.one() - BigNum.one(), BigNum.zero())
    self.assertEqual(BigNum.zero() - BigNum.one(), BigNum.h('FF'))
    self.assertEqual(BigNum.h('5678') - BigNum.h('4321'), BigNum.h('1357'))
    self.assertEqual(BigNum.h('4321') - BigNum.h('5678'), BigNum.h('ECA9'))
    self.assertEqual(BigNum.h('56789A') - BigNum.h('4321'), BigNum.h('563579'))
    self.assertEqual(BigNum.h('4321') - BigNum.h('56789A'), BigNum.h('A9CA87'))
    self.assertEqual(BigNum.h('4321') - BigNum.h('056789A'),
                     BigNum.h('FFA9CA87'))
    self.assertEqual(BigNum.one() - BigNum.h('FFFFFF'), BigNum.h('2'))
    self.assertEqual(BigNum.zero() - BigNum.h('FFFFFF'), BigNum.one())
    self.assertEqual(BigNum.one() - BigNum.h('1000000'), BigNum.h('FF000001'))
    self.assertEqual(BigNum.zero() - BigNum.one(4), BigNum.h('FFFFFFFF'))

  def test_multiplication(self):
    self.assertEqual(BigNum.zero() * BigNum.zero(), BigNum.zero())
    self.assertEqual(BigNum.one() * BigNum.zero(), BigNum.zero())
    self.assertEqual(BigNum.one() * BigNum.one(), BigNum.one())
    self.assertEqual(BigNum.h('1234') * BigNum.h('5678'), BigNum.h('06260060'))
    self.assertEqual(BigNum.h('1234') * BigNum.h('56789A'),
                     BigNum.h('06260B5348'))
    self.assertEqual(BigNum.h('FFFFFF') * BigNum.h('FFFFFF'),
                     BigNum.h('FFFFFE000001'))
    self.assertEqual(BigNum.h('FEFDFC') * BigNum.h('FBFAF9F8'),
                     BigNum.h('FAFD0318282820'))
    
  def test_slow_multiplication(self):
    old_mul = BigNum.__mul__
    try:
      BigNum.__mul__ = BigNum.slow_mul
      self.test_multiplication()
    finally:
      BigNum.__mul__ = old_mul

  def test_fast_multiplication(self):
    old_mul = BigNum.__mul__
    try:
      BigNum.__mul__ = BigNum.fast_mul
      self.test_multiplication()
    finally:
      BigNum.__mul__ = old_mul

  def test_division(self):
    self.assertEqual(BigNum.one() // BigNum.one(), BigNum.one(), '1 // 1 == 1')
    self.assertEqual(BigNum.zero() // BigNum.one(), BigNum.zero(),
                     '0 // 1 == 0')
    self.assertEqual(BigNum.h('42') // BigNum.h('03'), BigNum.h('16'))
    self.assertEqual(BigNum.h('43') // BigNum.h('03'), BigNum.h('16'))    
    
    self.assertEqual(BigNum.h('06260060') // BigNum.h('1234'), BigNum.h('5678'))
    self.assertEqual(BigNum.h('06263F29') // BigNum.h('5678'), BigNum.h('1234'))
    self.assertEqual(BigNum.h('06260FE3C9') // BigNum.h('56789A'),
                     BigNum.h('1234'))
    self.assertEqual(BigNum.h('FFFFFE000001') // BigNum.h('FFFFFF'),
                     BigNum.h('FFFFFF'))
    self.assertEqual(BigNum.h('FFFFFE0CFEDC') // BigNum.h('FFFFFF'),
                     BigNum.h('FFFFFF'))
    self.assertEqual(BigNum.h('FAFD0318282820') // BigNum.h('FEFDFC'),
                     BigNum.h('FBFAF9F8'))
    self.assertEqual(BigNum.h('FAFD0318C3D9EF') // BigNum.h('FEFDFC'),
                     BigNum.h('FBFAF9F8'))

    self.assertEqual(BigNum.h('100000000') // BigNum.h('20000'),
                     BigNum.h('8000'))

  def test_slow_division(self):
    old_divmod = BigNum.__divmod__
    try:
      BigNum.__divmod__ = BigNum.slow_divmod
      self.test_division()
    finally:
      BigNum.__divmod__ = old_divmod

  def test_fast_division(self):
    old_divmod = BigNum.__divmod__
    try:
      BigNum.__divmod__ = BigNum.fast_divmod
      self.test_division()
    finally:
      BigNum.__divmod__ = old_divmod

  def test_modulo(self):
    self.assertEqual(BigNum.one() % BigNum.one(), BigNum.zero(), '1 % 1 == 0')
    self.assertEqual(BigNum.zero() % BigNum.one(), BigNum.zero(), '0 % 1 == 0')
    self.assertEqual(BigNum.h('42') % BigNum.h('03'), BigNum.zero())
    self.assertEqual(BigNum.h('43') % BigNum.h('03'), BigNum.one())    
    self.assertEqual(BigNum.h('44') % BigNum.h('03'), BigNum.h('02'))

    self.assertEqual(BigNum.h('06260060') % BigNum.h('1234'), BigNum.zero())
    self.assertEqual(BigNum.h('06263F29') % BigNum.h('5678'), BigNum.h('3EC9'))
    self.assertEqual(BigNum.h('06260FE3C9') % BigNum.h('56789A'),
                     BigNum.h('49081'))
    self.assertEqual(BigNum.h('FFFFFE000001') % BigNum.h('FFFFFF'),
                     BigNum.zero())
    self.assertEqual(BigNum.h('FFFFFE0CFEDC') % BigNum.h('FFFFFF'),
                     BigNum.h('CFEDB'))
    self.assertEqual(BigNum.h('FAFD0318282820') % BigNum.h('FEFDFC'),
                     BigNum.zero())
    self.assertEqual(BigNum.h('FAFD0318C3D9EF') % BigNum.h('FEFDFC'),
                     BigNum.h('9BB1CF'))

  def test_powmod(self):
    modulo = BigNum.h('100000000')
    self.assertEqual(BigNum.h('42').powmod(BigNum.zero(), modulo), BigNum.one())
    self.assertEqual(BigNum.h('42').powmod(BigNum.one(), modulo),
                     BigNum.h('42'))
    self.assertEqual(BigNum.h('42').powmod(BigNum.h('2'), modulo),
                     BigNum.h('1104'))
    self.assertEqual(BigNum.h('42').powmod(BigNum.h('5'), modulo),
                     BigNum.h('4AA51420'))
    self.assertEqual(BigNum.h('41').powmod(BigNum.h('BECF'), modulo),
                     BigNum.h('C73043C1'))

if __name__ == '__main__':
  unittest.main()
