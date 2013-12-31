'''Interface to low-level arithmetic functionality in KS cores.

WARNING: the mock implementation below is intended to allow running KS code on
non-KS hardware. Do NOT rely on any private members in the code below. The KS
Python VM compiles these objects into hardware primitives. For example,
accessing the _byte property of a Byte will raise an exception in the KS Python
VM.
'''

from __future__ import division  # Use // for integer division.

class Byte(object):
  '''An 8-bit digit. (base 256)'''
  
  @staticmethod
  def zero():
    '''A byte initialized to 0.'''
    return Byte._bytes[0]
  
  @staticmethod
  def one():
    '''A byte initialized to 1.'''
    return Byte._bytes[1]

  @staticmethod
  def from_hex(hex_string):
    '''A byte initialized to the value in the given hexadecimal number.
    
    Args:
      string: a 2-character string containing the hexadecimal digits 0-9, a-f,
              and/or A-F
    '''
    if len(hex_string) != 2:
      raise ValueError('Invalid hexadecimal string')
    d1 = hex_string[0]
    d2 = hex_string[1]
    if d1 not in Byte._nibbles or d2 not in Byte._nibbles:
      raise ValueError('Invalid hexadecimal string')
    return Byte._bytes[(Byte._nibbles[d1] << 4) | Byte._nibbles[d2]]
    
  @staticmethod
  def h(hex_string):
    '''Shorthand for from_hex(hex_string).'''
    return Byte.from_hex(hex_string)

  def hex(self):
    '''A 2-character string containing the hexadecimal value of this byte.'''
    return self._hex
  
  def word(self):
    '''A Word with the same value as this Byte.'''
    return self._word
    
  def __lt__(self, other):
    '''< for Bytes.'''
    return self._byte < other._byte

  def __le__(self, other):
    '''<= for Bytes.'''
    return self._byte <= other._byte

  def __gt__(self, other):
    '''> for Bytes.'''
    return self._byte > other._byte

  def __ge__(self, other):
    '''>= for Bytes.'''
    return self._byte >= other._byte
  
  # NOTE: Bytes are singletons and  don't need __eq__, __ne__, or __hash__.

  def __add__(self, other):
    '''Returns a Word with the result of adding 2 Bytes.'''
    return Word._words[(self._byte + other._byte) & 0xFFFF]

  def __sub__(self, other):
    '''Returns a Word with the result of subtracting 2 Bytes.'''
    return Word._words[(0x10000 + self._byte - other._byte) & 0xFFFF]

  def __mul__(self, other):
    '''Returns a Word with the result of multiplying 2 Bytes.'''
    return Word._words[self._byte * other._byte]
    
  def __floordiv__(self, other):
    '''Returns a Byte with the division quotient of 2 Bytes.'''
    return self.word() // other

  def __mod__(self, other):
    '''Returns a Byte with the division remainder of 2 Bytes.'''
    return self.word() % other
  
  def __and__(self, other):
    '''Returns the logical AND of two Bytes.'''
    return Byte._bytes[self._byte & other._byte]
    
  def __or__(self, other):
    '''Returns the logical AND of two Bytes.'''
    return Byte._bytes[self._byte | other._byte]
    
  def __xor__(self, other):
    '''Returns the logical AND of two Bytes.'''
    return Byte._bytes[self._byte ^ other._byte]
    
  def __str__(self):
    '''Debugging help: returns the Byte formatted as "0x??".'''
    return '0x' + self.hex()
  
  def __repr__(self):
    '''Debugging help: returns a Python expression that can create this Byte.'''
    return 'Byte.h("' + self.hex() + '")'

  def __init__(self, value):
    '''Do not call the Byte constructor directly.
    
    Use Byte.zero(), Byte.one(), or Byte.from_hex() instead.
    '''
    if len(Byte._bytes) == 0x100:  # True after all Byte singletons are created.
      raise ValueError('Do not call the Byte constructor directly!')
    self._byte = value
    self._hex = Byte._hex_digits[value >> 4] + Byte._hex_digits[value & 0xF]
    self._word = None  # Will be set during initialization.

  # Private: maps nibbles to hexadecimal digit strings.
  _hex_digits = '0123456789ABCDEF'

  # Private: maps hexadecimal digit strings to nibbles.
  _nibbles = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
              '8': 8, '9': 9,
              'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15,
              'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15}
  
  # Private: array of singleton Byte instances.
  _bytes = []
  
class Word(object):
  '''A 16-bit digit. (base 65536)'''

  @staticmethod
  def zero():
    '''A word initialized to 0.'''
    return Word._words[0]
  
  @staticmethod
  def one():
    '''A word initialized to 1.'''
    return Word._words[1]

  @staticmethod
  def from_byte(byte):
    '''A word initialized to the value of a Byte.'''
    return Word._words[byte._byte]
  
  @staticmethod
  def from_bytes(msb, lsb):
    '''A word initialized from two Bytes. (msb:lsb)'''
    return Word._words[(msb._byte << 8) | lsb._byte]

  @staticmethod
  def from_hex(hex_string):
    '''A word initialized to the value in the given hexadecimal number.
    
    Args:
      string: a 2-character string containing the hexadecimal digits 0-9, a-f,
              and/or A-F
    '''
    if len(hex_string) != 4:
      raise ValueError('Invalid hexadecimal string')
    return Word.from_bytes(Byte.from_hex(hex_string[0:2]),
                           Byte.from_hex(hex_string[2:4]))
    
  @staticmethod
  def h(hex_string):
    '''Shorthand for from_hex(hex_string).'''
    return Word.from_hex(hex_string)

  def hex(self):
    '''A 4-character string containing the hexadecimal value of this word.'''
    return self._hex
  
  def lsb(self):
    '''The word's least significant Byte.'''
    return self._lsb
    
  def msb(self):
    '''The word's most significant Byte.'''
    return self._msb

  def __lt__(self, other):
    '''< for Words.'''
    return self._word < other._word

  def __le__(self, other):
    '''<= for Words.'''
    return self._word <= other._word

  def __gt__(self, other):
    '''> for Words.'''
    return self._word > other._word

  def __ge__(self, other):
    '''>= for Words.'''
    return self._word >= other._word
  
  # NOTE: Words are singletons and  don't need __eq__, __ne__, or __hash__.
  
  def __add__(self, other):
    '''Returns a Word with the result of adding 2 Words modulo 65,536.'''
    return Word._words[(self._word + other._word) & 0xFFFF]

  def __sub__(self, other):
    '''Returns a Word with the result of subtracting 2 Words modulo 65,536.'''
    return Word._words[(0x10000 + self._word - other._word) & 0xFFFF]

  def __mul__(self, other):
    '''Do not call. Multiply two Bytes to obtain a Word.'''
    return NotImplemented  # Multiply two Bytes to obtain a Word.
    
  def __floordiv__(self, other):
    '''Returns a Byte with the division quotient between this Word and a Byte.
    '''
    return Byte._bytes[(self._word // other._byte) & 0xFF]

  def __mod__(self, other):
    '''Returns a Byte with the division remainder between this Word and a Byte.
    '''
    return Byte._bytes[self._word % other._byte]

  def __and__(self, other):
    '''Returns the logical AND of two Words.'''
    return Word._words[self._word & other._word]
    
  def __or__(self, other):
    '''Returns the logical AND of two Words.'''
    return Word._words[self._word | other._word]
    
  def __xor__(self, other):
    '''Returns the logical AND of two Words.'''
    return Word._words[self._word ^ other._word]

  def __str__(self):
    '''Debugging help: returns the Byte formatted as "0x????".'''
    return '0x' + self.hex()
  
  def __repr__(self):
    '''Debugging help: returns a Python expression that can create this Word.'''
    return 'Word.h("' + self.hex() + '")'

  def __init__(self, value):
    '''Do not call the Word constructor directly.
    
    Use Word.zero(), Byte.one(), or Byte.from_hex() instead.
    '''
    if len(Word._words) == 0x10000:  # True after Word singletons are created.
      raise ValueError('Do not call the Word constructor directly!')
    self._word = value
    self._lsb = Byte._bytes[self._word & 0xFF]
    self._msb = Byte._bytes[self._word >> 8]
    self._hex = Byte.hex(self.msb()) + Byte.hex(self.lsb())
  
  # Private: array of singleton Word instances.
  _words = []

  
# Private: initialize singleton Byte instances.
for i in range(0, 0x100):
  Byte._bytes.append(Byte(i))

# Private: initialize singleton Word instances.
for i in range(0, 0x10000):
  Word._words.append(Word(i))

# Private: link Byte instances to their corresponding Words.
for i in range(0, 0x100):
  Byte._bytes[i]._word = Word._words[i]
