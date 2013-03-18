from collections import defaultdict
import aes

def input_to_triples(inputs):
  triples = inputs.split("; ")

  cipher_text_triples = []
  for triple in triples:
    if triple.strip():
      split_result = triple.split(", ")
      ctt = CipherTextTriple(split_result[0], split_result[1], split_result[2])
      cipher_text_triples.append(ctt)

  return cipher_text_triples

# Class for wrapping cipher text triple into. Contains attributes for
# the plaintext, ciphertext, and ones_count result held in each triple.
class CipherTextTriple:
  def __init__(self, plaintext, ciphertext, ones_count):
    self.plaintext = self._parse_text(plaintext)
    self.ciphertext = self._parse_text(ciphertext)
    self.ones_count = int(ones_count)

  # Parses the input line and turns it into integers.
  def _parse_text(self, text):
    if not isinstance(text, list):
      split_result = text.split(" ")
      text = [int(num) for num in split_result]
    return text

# The class used to crack AES using the side-channel information.
class AESCracker:
  def __init__(self, inputs=None):
    self.counter_cache = defaultdict(list)
    self.triples_processed = 0

    if inputs is not None:
      self.process_inputs(inputs)

  # This method takes a set of inputs from the file (not processed yet at all)
  # and increments the counter on each of them.
  def process_inputs(self, inputs):
    cipher_text_triples = input_to_triples(inputs.replace("\n", ""))
    self.process_triples(cipher_text_triples)

  def process_triples(self, cipher_text_triples):
    for triple in cipher_text_triples:
      self._read_plaintext_to_counter(triple.plaintext, triple.ones_count, self.counter_cache)
      self.triples_processed += 1

  # Outputs the results of the counting of the triples. For each position, we
  # use a threshold to determine whether or not the average is above or below
  # the expected result.
  def get_result(self, expected_result=704, t=1048):
    result = {}
    for position, count_list in self.counter_cache.iteritems():
      average_count = float(sum(count_list))/len(count_list)
      diff = (average_count - expected_result)
      value = 1 if diff < 0 else 0
      result[position] = value

    # Compute the confidence that we have
    confidence = float(expected_result*2) / self.triples_processed
    print "Triples Processed: ", self.triples_processed
    print "Confidence: ", confidence

    return [result[sorted_key] for sorted_key in sorted(result.iterkeys())]

  ######################
  ### HELPER METHODS ###
  ######################

  def _read_plaintext_to_counter(self, plaintext, ones_count, counter_cache):
    position = 0
    for number in plaintext:
      binary_representation = self._convert_num_to_binary(number, 8)

      for bit in binary_representation:
        if bit == "1":
          counter_cache[position].append(ones_count)
        position += 1

    return counter_cache

  def _convert_num_to_binary(self, number, total_length):
    binary = bin(number)[2:]
    padding_size = total_length - len(binary)
    return "".join(['0' for i in xrange(padding_size)]) + binary


def get_full_key(filename, secret_key=None):
  with open(filename, 'r') as f:
    input_data = f.read()
    triples = input_to_triples(input_data)

    if secret_key == None:
      cracker = AESCracker()
      cracker.process_triples(triples)
      secret_key = cracker.get_result()

      print "Secret Key Bits: "
      print secret_key

      secret_key = convert_key_to_byte_array(secret_key)
      print "Secret Key Byte Array: "
      print secret_key

    check_secret_key(secret_key, triples)
  return secret_key

def convert_key_to_byte_array(round_key):
  byte_array = []
  for i in xrange(16):
    byte_bits = round_key[i*8:(i+1)*8]

    byte_in_decimal = 0
    for i in xrange(8):
      byte_in_decimal += byte_bits[i]*(2**(8-i-1))

    byte_array.append(byte_in_decimal)
  return byte_array

def check_secret_key(secret_key, triples):
  num_wrong = 0
  num_processed = 0
  aes_algo = aes.AES()
  for triple in triples:
    encrypted_form = aes_algo.encrypt(triple.plaintext, secret_key, 16)
    if encrypted_form != triple.ciphertext:
      num_wrong += 1
    num_processed += 1

    if num_processed % 10000 == 0:
      print "Processed: ", num_processed
      print "Percentage Incorrect: ", float(num_wrong)/num_processed

  print "Final Result: "
  print "Percentage Incorrect: ", float(num_wrong)/len(triples)

if __name__ == '__main__':
  filename = 'triples_data'
  get_full_key(filename)
