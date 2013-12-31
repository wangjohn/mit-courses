'''Large number arithmetic optimized for KS cores.'''

from __future__ import division  # Use // for integer division.
import os     # Used for os.environ.
import sys    # Used to smooth over the range / xrange issue.
# Python 3 doesn't have xrange, and range behaves like xrange.
if sys.version_info >= (3,):
    xrange = range

if os.environ.get('KS_DEBUG') and os.environ.get('KS_DEBUG') != 'false':
  from ks_primitives import *
else:
  from ks_primitives_unchecked import *


class BigNum(object):
  '''Large number implemented as a little-endian array of Bytes.'''
  
  def __init__(self, digits, size = None, no_copy = False):
    '''Creates a BigNum from a sequence of digits.
    
    Args:
      digits: the Bytes used to populate the BigNum
      size: if set, the BigNum will only use the first "size" elements of digits
      no_copy: uses the "digits" argument as the backing store for BigNum, if
               appropriate (meant for internal use inside BigNum)
    '''
    if size is None:
      size = len(digits)
    elif size < 0:
      raise ValueError('BigNums cannot hold a negative amount of digits')
    if size == 0:
      size = 1
    if no_copy and len(digits) == size:
      self.d = digits
    else:
      self.d = digits[0:size]
    while len(self.d) < size:
      self.d.append(Byte.zero())
      
    # Used by the Newton-Raphson division code.
    self.__inverse = None
    self.__inverse_precision = None
    
  @staticmethod
  def zero(size = 1):
    '''BigNum representing the number 0 (zero).'''
    return BigNum([Byte.zero()] * size, size, True)
  
  @staticmethod
  def one(size = 1):
    '''BigNum representing the number 1 (one).'''
    digits = [Byte.zero()] * size
    digits[0] = Byte.one()
    return BigNum(digits, size, True)
  
  @staticmethod
  def from_hex(hex_string):
    '''BigNum representing the given hexadecimal number.
    
    Args:
      hex_string: string containing the desired number in hexadecimal; the
                  allowed digits are 0-9, A-F, a-f
    '''
    digits = []
    for i in xrange(len(hex_string), 0, -2):
      if i == 1:
        byte_string = '0' + hex_string[0]
      else:
        byte_string = hex_string[(i - 2):i]
      digits.append(Byte.from_hex(byte_string))
    return BigNum(digits)
  
  @staticmethod
  def h(hex_string):
    '''Shorthand for from_hex(hex_string).'''
    return BigNum.from_hex(hex_string)
  
  def hex(self):
    '''Hexadecimal string representing this BigNum.
    
    This method does not normalize the BigNum, because it is used during
    debugging.
    '''
    start = len(self.d) - 1
    while start > 0 and self.d[start] == Byte.zero():
      start -= 1
    return ''.join([self.d[i].hex() for i in xrange(start, -1, -1)])
  
  def __eq__(self, other):
    '''== for BigNums.
    
    Comparing BigNums normalizes them.'''
    if not isinstance(other, BigNum):
      return False
    
    self.normalize()
    other.normalize()
    return self.d == other.d
    
  def __ne__(self, other):
    '''!= for BigNums.
    
    Comparing BigNums normalizes them.'''
    if not isinstance(other, BigNum):
      return True
    
    self.normalize()
    other.normalize()
    return self.d != other.d

  def __lt__(self, other):
    '''< for BigNums.
    
    Comparing BigNums normalizes them.'''
    if not isinstance(other, BigNum):
      return NotImplemented  # BigNums can only be compared to other BigNums.

    self.normalize()
    other.normalize()
    if len(self.d) != len(other.d):
      return len(self.d) < len(other.d)
    
    for i in xrange(len(self.d) - 1, -1, -1):
      if self.d[i] != other.d[i]:
        return self.d[i] < other.d[i]
    return False

  def __le__(self, other):
    '''<= for BigNums.
    
    Comparing BigNums normalizes them.
    '''
    if not isinstance(other, BigNum):
      return NotImplemented  # BigNums can only be compared to other BigNums.
     
    self.normalize()
    other.normalize()
    if len(self.d) != len(other.d):
      return len(self.d) < len(other.d)
    
    for i in xrange(len(self.d) - 1, -1, -1):
      if self.d[i] != other.d[i]:
        return self.d[i] < other.d[i]
    return True

  def __gt__(self, other):
    '''> for BigNums.
    
    Comparing BigNums normalizes them.
    '''
    if not isinstance(other, BigNum):
      return NotImplemented  # BigNums can only be compared to other BigNums.
    return not self.__le__(other)

  def __ge__(self, other):
    '''>= for BigNums.
    
    Comparing BigNums normalizes them.
    '''    
    if not isinstance(other, BigNum):
      return NotImplemented  # BigNums can only be compared to other BigNums.
    return not self.__lt__(other)

  def __lshift__(self, digits):
    '''This BigNum, with "digits" 0 digits appended at the end.
    
    Shifting to the left multiplies the BigNum by 256^digits.
    '''
    new_digits = [Byte.zero()] * digits
    new_digits.extend(self.d)
    return BigNum(new_digits, None, True)

  def __rshift__(self, digits):
    '''This BigNum, without the last "digits" digits.
    
    Shifting to the left multiplies the BigNum by 256^digits.
    '''
    if digits >= len(self.d):
      return BigNum.zero()
    return BigNum(self.d[digits:], None, True)
  
  def __add__(self, other):
    '''+ for BigNums.
    
    Shifting to the left has the effect of multiplying the BigNum by 256^digits.
    '''
    if not isinstance(other, BigNum):
      return NotImplemented  # BigNums can only be added to BigNums.
    
    # One would think that it'd be faster to have a for loop for the digits
    # between 0 and min(len(self.d), len(other.d)), and another loop between
    # min(...) and max(...), so the ifs would be eliminated.
    # Turns out pypy's JITter can eliminate the range checks on list accesses
    # for the code below, so this method ends up being significantly faster than
    # the one mentioned above, which intuitively seems better.
        
    result = BigNum.zero(1 + max(len(self.d), len(other.d)))
    carry = Byte.zero()
    for i in xrange(0, len(result.d)):
      if i < len(self.d):
        a = self.d[i] + carry
      else:
        a = carry.word()
      if i < len(other.d):
        b = other.d[i].word()
      else:
        b = Word.zero()
      word = a + b
      result.d[i] = word.lsb()
      carry = word.msb()
    return result.normalize()

  def __sub__(self, other):
    '''- for BigNums.
    
    Subtraction is done using 2s complement.
    
    Subtracting numbers does not normalize them. However, the result is
    normalized.
    '''
    if not isinstance(other, BigNum):
      return NotImplemented  # BigNums can only be subtracted from BigNums.    
    result = BigNum.zero(max(len(self.d), len(other.d)))
    carry = Byte.zero()
    for i in xrange(0, len(result.d)):
      if i < len(self.d):
        a = self.d[i].word()
      else:
        a = Word.zero()
      if i < len(other.d):
        b = other.d[i] + carry
      else:
        b = carry.word()
      word = a - b
      result.d[i] = word.lsb()
      if a < b:
        carry = Byte.one()
      else:
        carry = Byte.zero()
    return result.normalize()
  
  def __mul__(self, other):
    '''* for BigNums.
    
    Multiplying numbers does not normalize them. However, the result is
    normalized.
    '''
    if not isinstance(other, BigNum):
      return NotImplemented  # BigNums can only be multiplied by BigNums.    
    if len(self.d) <= 64 or len(other.d) <= 64:
      return self.slow_mul(other)
    return self.fast_mul(other)

  def slow_mul(self, other):
    '''
    Slow method for multiplying two numbers w/ good constant factors.
    '''
    self_len = len(self.d)
    other_len = len(other.d)
    N = max(self_len, other_len)
    C = Byte.zero(N)
    for i in range(N):
        carry = 0
        for j in range(N):
            digit = self.word(self.d[i])
            

    
    for i in range(self_len):
        for j in range(other_len):
            newDigit = self.d[self_len - 1 - i] * other.d[other_len - 1 - j]
            result[123 - j - i] += newDigit % 10
            if newDigit > 9 and newDigit <= 99:
                result[122 - j - i] += newDigit // 10
            
    for k in range(124):
        i = 123 - k
        remain = result[i]
        base = 0
        while remain > 9:
            result[i - base] = remain % 10
            remain = remain // 10
            if remain > 0:
                result[i - base - 1] += remain  
            base += 1

    resultBigNum = BigNum(result)    
    return resultBigNum.normalize()

  def fast_mul(self, other):
    '''
    Asymptotically fast method for multiplying two numbers.
    '''
    in_digits = max(len(self.d), len(other.d))
    if in_digits == 1:
      product = self.d[0] * other.d[0]
      return BigNum([product.lsb(), product.msb()], 2, True)
    split = in_digits // 2
    self_low = BigNum(self.d[:split], None, True)
    self_high = BigNum(self.d[split:], None, True)
    other_low = BigNum(other.d[:split], None, True)
    other_high = BigNum(other.d[split:], None, True)
    
    result_high_high = self_high * other_high
    result_low = self_low * other_low
    result_high = (self_low + self_high) * (other_low + other_high) - \
                  (result_high_high + result_low)
    return ((result_high_high << (2 * split)) + (result_high << split) +
            result_low).normalize()
  
  def __floordiv__(self, other):
    '''/ for BigNums.

    Dividing numbers normalizes them. The result is also normalized.
    '''
    if not isinstance(other, BigNum):
      return NotImplemented  # BigNums can only be divided by other BigNums.
    return self.__divmod__(other)[0]
  
  def __mod__(self, other):
    '''% for BigNums.
    
    Multiplying numbers does not normalize them. However, the result is
    normalized.
    '''    
    if not isinstance(other, BigNum):
      return NotImplemented  # BigNums can only be divided by other BigNums.
    return self.__divmod__(other)[1]
  
  def __divmod__(self, other):
    '''divmod() for BigNums.

    Dividing numbers normalizes them. The result is also normalized.
    '''
    if not isinstance(other, BigNum):
      return NotImplemented  # BigNums can only be divided by other BigNums.  
    self.normalize()
    other.normalize()
    if len(self.d) <= 256 or len(other.d) <= 256:
      return self.slow_divmod(other)
    return self.fast_divmod(other)
  
  def slow_divmod(self, other):
    '''
    Slow method for dividing two numbers w/ good constant factors.
    '''
    self_len = len(self.d)
    other_len = len(other.d)
    result = []

    # Dividend should always be length other_len
    dividend = PushQueue()
    for i in range(other_len):
        dividend.add(self_len(i))

    
    
    return self.fast_divmod(other)

  def fast_divmod(self, other):
    '''
    Asymptotically fast method for dividing two numbers.
    '''
    # Special-case 1 so we don't have to deal with its inverse.
    if len(other.d) == 1 and other.d[0] == Byte.one():
      return (self, BigNum.zero())
      
    if other.__inverse is None:
      # First approximation: the inverse of the first digit in the divisor + 1,
      # because 1 / 2xx is <= 1/200 and > 1/300.
      base = Word.from_bytes(Byte.one(), Byte.zero())
      msb_plus = (other.d[-1] + Byte.one()).lsb()
      if msb_plus == Byte.zero():
        msb_inverse = (base - Word.one()).lsb()
        other.__inverse_precision = len(other.d) + 1
      else:
        msb_inverse = base // msb_plus
        other.__inverse_precision = len(other.d)
      other.__inverse = BigNum([msb_inverse], 1, True)

    bn_one = BigNum.one()

    while True:
      # Division using other's multiplicative inverse.
      quotient = (self * other.__inverse) >> other.__inverse_precision
      product = other * quotient
      if product > self:
        product -= other
        quotient -= bn_one
      if product <= self:
        remainder = self - product
        if remainder >= other:
          remainder -= other
          quotient += bn_one
        if remainder < other:
          return (quotient, remainder)
      
      # other needs a better multiplicative inverse approximation.
      old_inverse = other.__inverse
      old_precision = other.__inverse_precision
      other.__inverse = ((old_inverse + old_inverse) << old_precision) - \
          (other * old_inverse * old_inverse)
      other.__inverse.normalize()
      other.__inverse_precision *= 2
      # Trim zero digits at the end, they don't help.
      zero_digits = 0
      while other.__inverse.d[zero_digits] == Byte.zero():
        zero_digits += 1
      if zero_digits > 0:
        other.__inverse = other.__inverse >> zero_digits
        other.__inverse_precision -= zero_digits
    
  def powmod(self, exponent, modulus):
    '''Modular ^.
    
    Args:
      exponent: the exponent that this number will be raised to
      modulus: the modulus
      
    Returns (self ^ exponent) mod modulus.
    '''
    multiplier = BigNum(self.d)
    result = BigNum.one()
    exp = BigNum(exponent.d)
    exp.normalize()
    two = (Byte.one() + Byte.one()).lsb()
    for i in xrange(len(exp.d)):
      mask = Byte.one()
      for j in xrange(0, 8):
        if (exp.d[i] & mask) != Byte.zero():
          result = (result * multiplier) % modulus
        mask = (mask * two).lsb()
        multiplier = (multiplier * multiplier) % modulus
    return result
  
  def __str__(self):
    '''Debugging help: returns the BigNum formatted as "0x????...".'''
    return '0x' + self.hex()
  
  def __repr__(self):
    '''Debugging help: returns an expression that can create this BigNum.'''
    return 'BigNum.h("' + self.hex() + '", ' + str(len(self.d)) + ')'

  def normalize(self):
    '''Removes all the trailing 0 (zero) digits in this number.
    
    Returns self, for easy call chaining.
    '''
    while len(self.d) > 1 and self.d[-1] == Byte.zero():
      self.d.pop()
    return self

  def is_normalized(self):
    '''False if the number has at least one trailing 0 (zero) digit.'''
    return len(self.d) == 1 or self.d[-1] != Byte.zero()

class QueueObject(object):
    """ Object for creating a Queue. """
    def __init__(self, value, left = None, right = None):
        self.right = right
        self.left = left
        self.value = value
        
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
