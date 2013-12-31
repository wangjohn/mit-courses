class BST(object):
    """
    Simple binary search tree implementation.
    This BST supports insert, find, and delete-min operations.
    Each tree contains some (possibly 0) BSTnode objects, representing nodes,
    and a pointer to the root.
    """

    def __init__(self):
        self.root = None

    def insert(self, t):
        """Insert key t into this BST, modifying it in-place."""
        new = BSTnode(t)
        if self.root is None:
            self.root = new
        else:
            node = self.root
            while True:
                if t < node.key:
                    # Go left
                    if node.left is None:
                        node.left = new
                        new.parent = node
                        break
                    node = node.left
                else:
                    # Go right
                    if node.right is None:
                        node.right = new
                        new.parent = node
                        break
                    node = node.right
        return new

    def find(self, t):
        """Return the node for key t if is in the tree, or None otherwise."""
        node = self.root
        while node is not None:
            if t == node.key:
                return node
            elif t < node.key:
                node = node.left
            else:
                node = node.right
        return None

    def delete_min(self):
        """Delete the minimum key (and return the old node containing it)."""
        if self.root is None:
            return None, None
        else:
            # Walk to leftmost node.
            node = self.root
            while node.left is not None:
                node = node.left
            # Remove that node and promote its right subtree.
            if node.parent is not None:
                node.parent.left = node.right
            else: # The root was smallest.
                self.root = node.right
            if node.right is not None:
                node.right.parent = node.parent
            parent = node.parent
            node.disconnect()
            return node, parent

    def minimum(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current

    def successor(self, node):
        """ Returns the node with the smallest key larger than this node's
        key. """
        if node.right is not None:
            return self.minimum(node.right)
        current = node
        while current.parent is not None and current.parent.right is current:
            current = current.parent
        return current.parent

    def __str__(self):
        if self.root is None: return '<empty tree>'
        def recurse(node):
            if node is None: return [], 0, 0
            label = str(node.key)
            left_lines, left_pos, left_width = recurse(node.left)
            right_lines, right_pos, right_width = recurse(node.right)
            middle = max(right_pos + left_width - left_pos + 1, len(label), 2)
            pos = left_pos + middle // 2
            width = left_pos + middle + right_width - right_pos
            while len(left_lines) < len(right_lines):
                left_lines.append(' ' * left_width)
            while len(right_lines) < len(left_lines):
                right_lines.append(' ' * right_width)
            if (middle - len(label)) % 2 == 1 and node.parent is not None and \
               node is node.parent.left and len(label) < middle:
                label += '.'
            label = label.center(middle, '.')
            if label[0] == '.': label = ' ' + label[1:]
            if label[-1] == '.': label = label[:-1] + ' '
            lines = [' ' * left_pos + label + ' ' * (right_width - right_pos),
                     ' ' * left_pos + '/' + ' ' * (middle-2) +
                     '\\' + ' ' * (right_width - right_pos)] + \
              [left_line + ' ' * (width - left_width - right_width) +
               right_line
               for left_line, right_line in zip(left_lines, right_lines)]
            return lines, pos, width
        return '\n'.join(recurse(self.root) [0])

class BSTSize(BST):
    """ BST implementation with augmentation for the size of the subtrees """
    def __init__(self):
        self.root = None

    def insert(self, t):
        node = BST.insert(self, t)
        while node is not None:
            update_size(node)
            node = node.parent

    def delete_min(self):
        deleted, parent = bst.BST.delete_min(self)
        node = parent
        while node is not None:
            update_size(node)
            node = node.parent
        return deleted, parent

class BSTnode(object):
    """
    Representation of a node in a binary search tree.
    Has a left child, right child, and key value.
    """
    def __init__(self, t):
        """Create a new leaf with key t."""
        self.key = t
        self.disconnect()
    def disconnect(self):
        self.left = None
        self.right = None
        self.parent = None
        self.height = 0

def update_size(node):
    if node is None:
        return 0
    node.size = update_size(node.left) + update_size(node.right) + 1
    return node.size

def update_height(node):
    if node is None:
        return -1
    node.height = max(update_height(node.left), update_height(node.right)) + 1
    return node.height

def height(node):
    if node is None:
        return -1
    else:
        return node.height

class AVLTree(BSTSize):
    """ AVL implementation of BST """
    def left_rotate(self, x):
        y = x.right
        y.parent = x.parent
        if y.parent is None:
            self.root = y
        else:
            if y.parent.left is x:
                y.parent.left = y
            elif y.parent.right is x:
                y.parent.right = y
        x.right = y.left
        if x.right is not None:
            x.right.parent = x
        y.left = x
        x.parent = y
        update_size(self.root)
        update_height(self.root)
        
    def right_rotate(self, x):
        y = x.left
        y.parent = x.parent
        if y.parent is None:
            self.root = y
        else:
            if y.parent.left is x:
                y.parent.left = y
            elif y.parent.right is x:
                y.parent.right = y
        x.left = y.right
        if x.left is not None:
            x.left.parent = x
        y.right = x
        x.parent = y
        update_size(self.root)
        update_height(self.root)

    def rebalance(self, node):
        while node is not None:
            update_height(self.root)
            if height(node.left) >= 2 + height(node.right):
                if height(node.left.left) >= height(node.left.right):
                    self.right_rotate(node)
                else:
                    self.left_rotate(node.left)
                    self.right_rotate(node)
            elif height(node.right) >= 2 + height(node.left):
                if height(node.right.right) >= height(node.right.left):
                    self.left_rotate(node)
                else:
                    self.right_rotate(node.right)
                    self.left_rotate(node)
            node = node.parent
        update_size(self.root)
        
    def insert(self, key):
        node = BSTSize.insert(self, key)
        self.rebalance(node)
        self.rebalance(self.find(key))
        
    def delete_min(self):
        node, parent = BSTSize.delete_min(self)
        self.rebalance(parent)

    def delete(self, x):
        if x.right is not None:
            if x.left is not None:
                y = self.successor(x)
                y.key, x.key = y.key, x.key
                self.delete(y)
            else:
                if x.parent is None:
                    x.disconnect()
                    x.right.parent = None
                    self.root = x.right
                elif x.parent.left is x:
                    x.parent.left = x.right
                    x.right.parent = x.parent
                else:
                    x.parent.right = x.right
                    x.right.parent = x.parent
        else:
            if x.left is not None:
                if x.parent is None:
                    x.disconnect()
                    x.left.parent = None
                    self.root = x.left
                elif x.parent.left is x:
                    x.parent.left = x.left
                    x.left.parent = x.parent
                else:
                    x.parent.right = x.left
                    x.left.parent = x.parent
            else:
                if x.parent is None:
                    self.root = None
                elif x.parent.right is x:
                    x.parent.right = None
                else:
                    x.parent.left = None
                x.disconnect()
        if x.parent is not None:
            node = x.parent
            update_height(self.root)
            update_size(self.root)
            
    def rank(self, t):
        """ The number of keys <= t in the tree. """
        if self.root is None:
            return 0
        else:
            node = self.root
            rank = 0
            while True:
                left_size = 0 if node.left is None else node.left.size
                if t == node.key:
                    return rank + left_size + 1
                if t < node.key:
                    if self.find_max(node).key < t:
                        return rank +  node.size
                    if node.left is None:
                        return rank
                    else:
                        node = node.left
                else:
                    if self.find_max(node).key < t:
                        return rank + node.size
                    if node.right is None:
                        return left_size + 1
                    else:
                        rank += left_size + 1
                        node = node.right

    def find_max(self, node):
        """ Start from this node and find the maximum value in the tree. """
        current = node
        while current.right is not None:
            current = current.right
        return current

    def count(self, l, h):
        # if neither l nor h exist:
        l_exist = self.find(l)
        if l_exist == None:
            return self.rank(h) - self.rank(l)
        else:
            return self.rank(h) - self.rank(l) + 1

    def list_all_keys(self, l, h):
        """ This is just LIST(tree, l, h) from the problem set. """
        lca = self.lca(l, h)
        result = []
        self.node_list(lca, l, h, result)
        return result

    def lca(self, l, h):
        node = self.root
        while True:
            if node == None or (l <= node.key and h >= node.key):
                break
            if l < node.key:
                node = node.left
            else:
                node = node.right
        return node

    def node_list(self, node, l, h, result):
        if node == None:
            return
        if l <= node.key and node.key <= h:
            result.append(node.key)
        if node.key >= l:
            self.node_list(node.left, l, h, result)
        if node.key <= h:
            self.node_list(node.right, l, h, result)

import random
import time

def test(datasize, datatype = 'AVL'):
    length = 0
    if datatype == 'AVL':
        a = AVLTree()
    else:
        a = []
    for i in range(datasize):
        rand = random.randrange(1,datasize)
        if rand < datasize / 2:
            length += 1
            if datatype == 'AVL':
                a.insert(rand)
            else:
                a.append(rand)
        else:
            if length > 0:
                index = int(length * random.random())
                if datatype == 'AVL':
                    #try:
                        a.delete(index)
                    #except:
                    #    print(a)
                    #    break
                else:
                    a.pop(index)
                length -= 1

datasize = 10000

t0 = time.time()
test(datasize, 'AVL')
print 'AVL: ', time.time() - t0

t0 = time.time()
test(datasize, 'List')
print 'List: ', time.time() - t0
