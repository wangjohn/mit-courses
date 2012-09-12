# template file for 6.02 PS1, Python Task 2
import numpy,random
import PS1_tests
from PS1_1 import huffman

class Node:
    def __init__(self, bit, name):
        self.bit = bit
        self.name = name
        self.left = None
        self.right = None
    def create_next_node(self, next_bit):
        if next_bit == 0:
            if self.left is None:
                self.left = Node(next_bit, self.name + '0')
            return self.left
        else:
            if self.right is None:
                self.right = Node(next_bit, self.name + '1')
            return self.right
    def get_next_node(self, next_bit):
        if next_bit == 0:
            return self.left
        else:
            return self.right

def build_tree(encoding_dict):
    root = Node(None, '')
    for key,value in encoding_dict.items():
        node = root
        new_value = list(value)
        while len(new_value) > 0:
            next_bit = new_value.pop(0)
            node = node.create_next_node(next_bit)
        node.name = key
    return root

# arguments:
#   encoding_dict -- dictionary mapping characters to binary encodings,
#                    as provided by your huffman procedure from PS1_1
#   encoded_message -- a numpy array of 0's and 1's representing the encoded message
# return:
#   a list of decoded symbols
def decode(encoding_dict,encoded_message):
    """
    Example:
    encoding_dict: {'A': [1, 1], 'C': [1, 0, 0], 'B': [0], 'D': [1, 0, 1]}
    encoded_msg: [1, 1, 0, 1, 0, 0, 1, 0, 1]
    returns 'ABCD'
    """
    root = build_tree(encoding_dict) 
    node = root
    message = [] 
    for bit in encoded_message:
        next_node = node.get_next_node(bit)
        if next_node is None:
            message.append(node.name)
            node = root.get_next_node(bit)
        else:
            node = next_node
    message.append(node.name)
    return message


if __name__ == '__main__':
    # start by building Huffman tree from probabilities
    plist = ((0.34,'A'),(0.5,'B'),(0.08,'C'),(0.08,'D'))
    cdict = huffman(plist)

    # test case 1: decode a simple message
    message = ['A', 'B', 'C', 'D']
    encoded_message = PS1_tests.encode(cdict,message)
    decoded_message = decode(cdict,encoded_message)
    assert message == decoded_message, \
           "Decoding failed: expected %s, got %s" % \
           (message,decoded_message)

    # test case 2: construct a random message and encode it
    message = [random.choice('ABCD') for i in xrange(100)]
    encoded_message = PS1_tests.encode(cdict,message)
    decoded_message = decode(cdict,encoded_message)
    assert message == decoded_message, \
           "Decoding failed: expected %s, got %s" % \
           (message,decoded_message)

    print "Tests passed!"
