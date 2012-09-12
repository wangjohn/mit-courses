# template file for 6.02 PS1, Python Task 1
import PS1_tests

class Node:
    def __init__(self, prob, name):
        self.prob = prob
        self.name = name
        self.left = None
        self.right = None
        self.path = []
    def insert_into_path(self, integer):
        self.path.insert(0, integer)
        if self.left is not None:
            self.left.insert_into_path(integer)
        if self.right is not None:
            self.right.insert_into_path(integer)

# arguments:
#   plist -- sequence of (probability,object) tuples
# return:
#   a dictionary mapping object -> binary encoding
def huffman(pList):
    """
    Example:
    plist: ((0.50,'A'),(0.25,'B'),(0.125,'C'),(0.125,'D'))
    returns: {'A': [0], 'B': [1, 0], 'C': [1, 1, 0], 'D': [1, 1, 1]} 
    """
    output = {} 
    # sort the list in descending order
    pList = list(pList)
    pList.sort()
    pList.reverse()
    node_list = []
    original_nodes = []
    # create a list of nodes
    for tup in pList:
        new_node = Node(tup[0], tup[1])
        node_list.append(new_node)
        original_nodes.append(new_node)
    # continue until the list is a single node
    while len(node_list) > 1:
        last_node = node_list.pop()
        second_last_node = node_list.pop()
        parent = Node(last_node.prob + second_last_node.prob, last_node.name + second_last_node.name)
        parent.left = last_node
        # insert 1's and 0's into the path of the right and left child
        last_node.insert_into_path(0)
        parent.right = second_last_node
        second_last_node.insert_into_path(1)
        # put the parent node back into the node list
        inserted = False
        for i in xrange(len(node_list)):
            if parent.prob > node_list[i].prob:
                node_list.insert(i, parent)
                inserted = True
                break
        if not inserted:
            node_list.append(parent)
    for node in original_nodes:
        output[node.name] = node.path
    return output

if __name__ == '__main__':
    # test case 1: four symbols with equal probability
    PS1_tests.test_huffman(huffman,
                           # symbol probabilities
                           ((0.25,'A'),(0.25,'B'),(0.25,'C'),
                            (0.25,'D')),
                           # expected encoding lengths
                           ((2,'A'),(2,'B'),(2,'C'),(2,'D')))

    # test case 2: example from section 22.3 in notes
    PS1_tests.test_huffman(huffman,
                           # symbol probabilities
                           ((0.34,'A'),(0.5,'B'),(0.08,'C'),
                            (0.08,'D')),
                           # expected encoding lengths
                           ((2,'A'),(1,'B'),(3,'C'),(3,'D')))

    # test case 3: example from Exercise 5 in notes
    PS1_tests.test_huffman(huffman,
                           # symbol probabilities
                           ((0.07,'I'),(0.23,'II'),(0.07,'III'),
                            (0.38,'VI'),(0.13,'X'),(0.12,'XVI')),
                           # expected encoding lengths
                           ((4,'I'),(3,'II'),(4,'III'),
                            (1,'VI'),(3,'X'),(3,'XVI')))

    # test case 4: 3 flips of unfair coin
    phead = 0.9
    plist = []
    for flip1 in ('H','T'):
        p1 = phead if flip1 == 'H' else 1-phead
        for flip2 in ('H','T'):
            p2 = phead if flip2 == 'H' else 1-phead
            for flip3 in ('H','T'):
                p3 = phead if flip3 == 'H' else 1-phead
                plist.append((p1*p2*p3,flip1+flip2+flip3))
    expected_sizes = ((1,'HHH'),(3,'HTH'),(5,'TTT'))
    PS1_tests.test_huffman(huffman,plist,expected_sizes)
