from __future__ import division  # Use // for integer division.
import json   # Used when TRACE=jsonp
import os     # Used to get the TRACE environment variable
import sys
# Python 3 doesn't have xrange, and range behaves like xrange.
if sys.version_info >= (3,):
    xrange = range

if os.environ.get('SOLUTION'):
  from big_num_full import *
else:
  from big_num import *


class RsaKey(object):
  '''Public or private RSA key.'''
  def __init__(self, exponent_hex_string, modulus_hex_string):
    '''Initializes a key from a public or private exponent and the modulus.'''
    self.e = BigNum.from_hex(exponent_hex_string)
    self.n = BigNum.from_hex(modulus_hex_string)
    self.size = (len(self.n.hex()) + 1) // 2
    self.chunk_cache = {}
    
  def raw_crypt(self, number):
    '''Performs ECB RSA encryption / decryption.'''
    return number.powmod(self.e, self.n)
    
  def decrypt(self, hex_string):
    '''Decrypts a bunch of data stored as a hexadecimal string.
    
    Returns a hexadecimal string with the decrypted data.
    '''
    out_chunks = []
    i = 0
    in_chunk_size = self.size * 2
    out_chunk_size = (self.size - 1) * 2
    while i < len(hex_string):
      in_chunk = hex_string[i:(i + in_chunk_size)]
      if in_chunk in self.chunk_cache:
        out_chunk = self.chunk_cache[in_chunk]
      else:
        out_chunk = self.raw_crypt(BigNum.from_hex(in_chunk)).hex()
        if len(out_chunk) > out_chunk_size:
          # This indicates a decryption error. However, we'll truncate the
          # result, so the visualization can work.
          out_chunk = out_chunk[0:out_chunk_size]
        self.chunk_cache[in_chunk] = out_chunk
      if len(out_chunk) < out_chunk_size:
        out_chunks.append('0' * (out_chunk_size - len(out_chunk)))
      out_chunks.append(out_chunk)
      i += in_chunk_size
    return ''.join(out_chunks)


class EncryptedImage(object):
  '''Processes an image encrypted with an RSA key.'''

  def __init__(self):
    self.key = None
    self.encrypted_rows = []
    self.rows = None
    self.columns = None
  
  def set_key(self, exponent_hex_string, modulus_hex_string):
    '''Sets the RSA key to be used for decrypting the image.'''
    self.key = RsaKey(exponent_hex_string, modulus_hex_string)
    
  def add_row(self, encrypted_row_data):
    '''Appends a row of encrypted pixel data to the image.'''
    self.encrypted_rows.append(encrypted_row_data)
    
  def decrypt_image(self):
    '''Decrypts the encrypted image.'''
    if self.rows is not None:
      return 
    self.rows = []
    for encrypted_row in self.encrypted_rows:
      row = self.key.decrypt(encrypted_row)
      row_size = self.columns and (self.columns * 6) 
      if row_size:
        row = row[0:row_size]
      self.rows.append(row)
  
  def to_line_list(self):
    '''Returns a list of strings representing the image data.'''
    self.decrypt_image()
    return self.rows
    
  def to_file(self, file):
    '''Writes a textual description of the image data to a file.
    
    Args:
        file: A File object that receives the image data
    '''
    for line in self.to_line_list():
      file.write(line)
      file.write("\n")
      
  def as_json(self):
    '''"A dict that obeys the JSON format, representing the image.'''
    self.decrypt_image()
    jso = {}
    jso['image'] = {'rows': len(self.rows), 'cols': len(self.rows[0]) // 6,
                    'data': self.rows}
    jso['encrypted'] = {'data': self.encrypted_rows, 'rows': len(self.rows),
                        'cols': len(self.encrypted_rows[0]) // 6}
    return jso

  @staticmethod
  def from_file(file):
    '''Reads an encrypted image description from a file.
    
    Args:
      file: a File object supplying the input
    
    Returns a new RsaImageDecrypter instance.'''

    image = EncryptedImage()
    while True:
      command = file.readline().split()
      if command[0] == 'key':
        image.set_key(command[1], command[2])
      elif command[0] == 'sx':
        image.columns = int(command[1])
      elif command[0] == 'row':
        image.add_row(command[1])
      elif command[0] == 'end':
        break
    return image


# Command-line controller.
if __name__ == '__main__':
  image = EncryptedImage.from_file(sys.stdin)
  
  if os.environ.get('TRACE') == 'jsonp':
    sys.stdout.write('onJsonp(')
    json.dump(image.as_json(), sys.stdout)
    sys.stdout.write(');\n')
  else:
    image.to_file(sys.stdout)
