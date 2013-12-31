class BSTnode(object):
    """
Representation of a node in a binary search tree.
Has a left child, right child, and key value, and stores its subtree size.
"""
    def __init__(self, parent, t):
        """Create a new leaf with key t."""
        self.key = t
        self.parent = parent
        self.left = None
        self.right = None
        self.size = 1
        self.height = 0
        
    def update_stats(self):
        """Updates this node's size based on its children's sizes."""
        self.size = (0 if self.left is None else self.left.size) + (0 if self.right is None else self.right.size) 

    def insert(self, t, NodeType):
        """Insert key t into the subtree rooted at this node (updating subtree size)."""
        self.size += 1
        if t < self.key:
            if self.left is None:
                self.left = NodeType(self, t)                
                return self.left
            else:
                return self.left.insert(t, NodeType)
        else:
            if self.right is None:
                self.right = NodeType(self, t)   
                return self.right
            else:
                return self.right.insert(t, NodeType)

    def find(self, t):
        """Return the node for key t if it is in this tree, or None otherwise."""
        if t == self.key:
            return self
        elif t < self.key:
            if self.left is None:
                return None
            else:
                return self.left.find(t)
        else:
            if self.right is None:
                return None
            else:
                return self.right.find(t)

    def rank(self, t):
        """Return the number of keys <= t in the subtree rooted at this node."""
        left_size = 0 if self.left is None else self.left.size 
        if t == self.key:
            return left_size + 1
        elif t < self.key:
            if self.left is None:
                return 0
            else:
                return self.left.rank(t)
        else:
            if self.right is None:
                return left_size + 1
            else:
                return self.right.rank(t) + left_size + 1 
            
    def minimum(self):
        """Returns the node with the smallest key in the subtree rooted by this node."""
        current = self
        while current.left is not None:
            current = current.left
        return current
        

    def successor(self):
        """Returns the node with the smallest key larger than this node's key, or None if this has the largest key in the tree."""
        if self.right is not None:
            return self.right.minimum()
        current = self
        while current.parent is not None and current.parent.right is current:
            current = current.parent
        return current.parent

    def delete(self):
        """"Delete this node from the tree."""
        if self.left is None or self.right is None:
            if self is self.parent.left:
                self.parent.left = self.left or self.right
                if self.parent.left is not None:
                    self.parent.left.parent = self.parent
            else:
                self.parent.right = self.left or self.right
                if self.parent.right is not None:
                    self.parent.right.parent = self.parent 
            current = self.parent
            while current.key is not None:
                current.update_stats()
                current = current.parent
            return self
        else:
            s = self.successor()
            self.key, s.key = s.key, self.key
            return s.delete()        
        
    def check(self, lokey, hikey):
        """Checks that the subtree rooted at t is a valid BST and all keys are between (lokey, hikey)."""
        if lokey is not None and self.key <= lokey:
            raise "BST RI violation"
        if hikey is not None and self.key >= hikey:
            raise "BST RI violation"
        if self.left is not None:
            if self.left.parent is not self:
                raise "BST RI violation"
            self.left.check(lokey, self.key)
        if self.right is not None:
            if self.right.parent is not self:
                raise "BST RI violation"
            self.right.check(self.key, hikey)
        if self.size != 1 + (0 if self.left is None else self.left.size) + (0 if self.right is None else self.right.size):
            raise "BST RI violation"
            
    def __repr__(self):
        return "<BST Node, key:" + str(self.key) + ">"

class BST(object):
    """
Simple binary search tree implementation, augmented with subtree sizes.
This BST supports insert, find, and delete-min operations.
Each tree contains some (possibly 0) BSTnode objects, representing nodes,
and a pointer to the root.
"""

    def __init__(self, NodeType=BSTnode):
        self.root = None
        self.NodeType = NodeType
        self.psroot = self.NodeType(None, None)
    
    def reroot(self):
        self.root = self.psroot.left

    def insert(self, t):
        """Insert key t into this BST, modifying it in-place."""
        if self.root is None:
            self.psroot.left = self.NodeType(self.psroot, t)
            self.reroot()
            return self.root
        else:
            return self.root.insert(t, self.NodeType)
        
    def find(self, t):
        """Return the node for key t if is in the tree, or None otherwise."""
        if self.root is None:
            return None
        else:
            return self.root.find(t)
        
    def rank(self, t):
        """The number of keys <= t in the tree."""
        if self.root is None:
            return 0
        else:
            return self.root.rank(t)        
        
    def delete(self, t):
        """Delete the node for key t if it is in the tree."""
        node = self.find(t)
        deleted = self.root.delete()
        self.reroot()
        return deleted

    def check(self):
        if self.root is not None:
            self.root.check(None, None)
            
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

def height(node):
    if node is None:
        return -1
    else:
        return node.height

def update_height(node):
    node.height = max(height(node.left), height(node.right)) + 1

class AVL(BST):

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
        update_height(x)
        update_height(y)

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
        update_height(x)
        update_height(y)

    def insert(self, t):
        """Insert key t into this tree, modifying it in-place."""
        node = BST.insert(self, t)
        self.rebalance(node)

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
        self.rebalance(node.parent)

    def rebalance(self, node):
        while node is not None:
            update_height(node)
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

    def delete_min(self):
        node, parent = bst.BST.delete_min(self)
        self.rebalance(parent)
        #raise NotImplemented('AVL.delete_min')

import random
import time

def test(datasize, datatype = 'AVL'):
    length = 0
    if datatype == 'AVL':
        a = AVL()
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
