#!/usr/bin/env python

import json   # Used when TRACE=jsonp
import os     # Used to get the TRACE environment variable
import re     # Used when TRACE=jsonp
import sys    # Used to smooth over the range / xrange issue.

# Python 3 doesn't have xrange, and range behaves like xrange.
if sys.version_info >= (3,):
    xrange = range

### BST Classes ###

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
                x.key = y.key
                self.delete(y)
            else:
                if x.parent.left is x:
                    x.parent.left = x.right
                else:
                    x.parent.right = x.right
                x.right.parent = x.parent
        else:
            if x.left is not None:
                if x.parent.left is x:
                    x.parent.left = x.left
                else:
                    x.parent.right = x.left
                x.left.parent = x.parent
            else:
                if x.parent.right is x:
                    x.parent.right = None
                else:
                    x.parent.left = None
                x.disconnect()
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
        

# Circuit verification library.

class Wire(object):
  """A wire in an on-chip circuit.
  
  Wires are immutable, and are either horizontal or vertical.
  """
  
  def __init__(self, name, x1, y1, x2, y2):
    """Creates a wire.
    
    Raises an ValueError if the coordinates don't make up a horizontal wire
    or a vertical wire.
    
    Args:
      name: the wire's user-visible name
      x1: the X coordinate of the wire's first endpoint
      y1: the Y coordinate of the wire's first endpoint
      x2: the X coordinate of the wire's last endpoint
      y2: the Y coordinate of the wire's last endpoint
    """
    # Normalize the coordinates.
    if x1 > x2:
      x1, x2 = x2, x1
    if y1 > y2:
      y1, y2 = y2, y1
    
    self.name = name
    self.x1, self.y1 = x1, y1
    self.x2, self.y2 = x2, y2
    self.object_id = Wire.next_object_id()
    
    if not (self.is_horizontal() or self.is_vertical()):
      raise ValueError(str(self) + ' is neither horizontal nor vertical')
  
  def is_horizontal(self):
    """True if the wire's endpoints have the same Y coordinates."""
    return self.y1 == self.y2
  
  def is_vertical(self):
    """True if the wire's endpoints have the same X coordinates."""
    return self.x1 == self.x2
  
  def intersects(self, other_wire):
    """True if this wire intersects another wire."""
    # NOTE: we assume that wires can only cross, but not overlap.
    if self.is_horizontal() == other_wire.is_horizontal():
      return False 
    
    if self.is_horizontal():
      h = self
      v = other_wire
    else:
      h = other_wire
      v = self
    return v.y1 <= h.y1 and h.y1 <= v.y2 and h.x1 <= v.x1 and v.x1 <= h.x2
  
  def __repr__(self):
    # :nodoc: nicer formatting to help with debugging
    return('<wire ' + self.name + ' (' + str(self.x1) + ',' + str(self.y1) + 
           ')-(' + str(self.x2) + ',' + str(self.y2) + ')>')
  
  def as_json(self):
    """Dict that obeys the JSON format restrictions, representing the wire."""
    return {'id': self.name, 'x': [self.x1, self.x2], 'y': [self.y1, self.y2]}

  # Next number handed out by Wire.next_object_id()
  _next_id = 0
  
  @staticmethod
  def next_object_id():
    """Returns a unique numerical ID to be used as a Wire's object_id."""
    id = Wire._next_id
    Wire._next_id += 1
    return id

class WireLayer(object):
  """The layout of one layer of wires in a chip."""
  
  def __init__(self):
    """Creates a layer layout with no wires."""
    self.wires = {}
  
  def wires(self):
    """The wires in the layout."""
    self.wires.values()
  
  def add_wire(self, name, x1, y1, x2, y2):
    """Adds a wire to a layer layout.
    
    Args:
      name: the wire's unique name
      x1: the X coordinate of the wire's first endpoint
      y1: the Y coordinate of the wire's first endpoint
      x2: the X coordinate of the wire's last endpoint
      y2: the Y coordinate of the wire's last endpoint
    
    Raises an exception if the wire isn't perfectly horizontal (y1 = y2) or
    perfectly vertical (x1 = x2)."""
    if name in self.wires:
        raise ValueError('Wire name ' + name + ' not unique')
    self.wires[name] = Wire(name, x1, y1, x2, y2)
  
  def as_json(self):
    """Dict that obeys the JSON format restrictions, representing the layout."""
    return { 'wires': [wire.as_json() for wire in self.wires.values()] }
  
  @staticmethod
  def from_file(file):
    """Builds a wire layer layout by reading a textual description from a file.
    
    Args:
      file: a File object supplying the input
    
    Returns a new Simulation instance."""

    layer = WireLayer()
    
    while True:
      command = file.readline().split()
      if command[0] == 'wire':
        coordinates = [float(token) for token in command[2:6]]
        layer.add_wire(command[1], *coordinates)
      elif command[0] == 'done':
        break
      
    return layer

class RangeIndex(object):
  """Array-based range index implementation."""
  
  def __init__(self):
    """Initially empty range index."""
    self.data = AVLTree()
  
  def add(self, key):
    """Inserts a key in the range index."""
    if key is None:
        raise ValueError('Cannot insert nil in the index')
    self.data.insert(key)
  
  def remove(self, key):
    """Removes a key from the range index."""
    node = self.data.find(key)
    if node == None:
        pass
    else:
        self.data.delete(node)
  
  def list(self, first_key, last_key):
    """List of values for the keys that fall within [first_key, last_key]."""
    return self.data.list_all_keys(first_key, last_key)
  
  def count(self, first_key, last_key):
    """Number of keys that fall within [first_key, last_key]."""
    return self.data.count(first_key, last_key)
  
class TracedRangeIndex(RangeIndex):
  """Augments RangeIndex to build a trace for the visualizer."""
  
  def __init__(self, trace):
    """Sets the object receiving tracing info."""
    RangeIndex.__init__(self)
    self.trace = trace
  
  def add(self, key):
    self.trace.append({'type': 'add', 'id': key.wire.name})
    RangeIndex.add(self, key)
  
  def remove(self, key):
    self.trace.append({'type': 'delete', 'id': key.wire.name})
    RangeIndex.remove(self, key)
  
  def list(self, first_key, last_key):
    result = RangeIndex.list(self, first_key, last_key)
    self.trace.append({'type': 'list', 'from': first_key.key,
                       'to': last_key.key,
                       'ids': [key.wire.name for key in result]}) 
    return result
  
  def count(self, first_key, last_key):
    result = RangeIndex.count(self, first_key, last_key)
    self.trace.append({'type': 'list', 'from': first_key.key,
                       'to': last_key.key, 'count': result})
    return result

class ResultSet(object):
  """Records the result of the circuit verifier (pairs of crossing wires)."""
  
  def __init__(self):
    """Creates an empty result set."""
    self.crossings = []
  
  def add_crossing(self, wire1, wire2):
    """Records the fact that two wires are crossing."""
    self.crossings.append(sorted([wire1.name, wire2.name]))
  
  def write_to_file(self, file):
    """Write the result to a file."""
    for crossing in self.crossings:
      file.write(' '.join(crossing))
      file.write('\n')

class TracedResultSet(ResultSet):
  """Augments ResultSet to build a trace for the visualizer."""
  
  def __init__(self, trace):
    """Sets the object receiving tracing info."""
    ResultSet.__init__(self)
    self.trace = trace
    
  def add_crossing(self, wire1, wire2):
    self.trace.append({'type': 'crossing', 'id1': wire1.name,
                       'id2': wire2.name})
    ResultSet.add_crossing(self, wire1, wire2)

class KeyWirePair(object):
  """Wraps a wire and the key representing it in the range index.
  
  Once created, a key-wire pair is immutable."""
  
  def __init__(self, key, wire):
    """Creates a new key for insertion in the range index."""
    self.key = key
    if wire is None:
      raise ValueError('Use KeyWirePairL or KeyWirePairH for queries')
    self.wire = wire
    self.wire_id = wire.object_id

  def __lt__(self, other):
    # :nodoc: Delegate comparison to keys.
    return (self.key < other.key or
            (self.key == other.key and self.wire_id < other.wire_id))
  
  def __le__(self, other):
    # :nodoc: Delegate comparison to keys.
    return (self.key < other.key or
            (self.key == other.key and self.wire_id <= other.wire_id))  

  def __gt__(self, other):
    # :nodoc: Delegate comparison to keys.
    return (self.key > other.key or
            (self.key == other.key and self.wire_id > other.wire_id))
  
  def __ge__(self, other):
    # :nodoc: Delegate comparison to keys.
    return (self.key > other.key or
            (self.key == other.key and self.wire_id >= other.wire_id))

  def __eq__(self, other):
    # :nodoc: Delegate comparison to keys.
    return self.key == other.key and self.wire_id == other.wire_id
  
  def __ne__(self, other):
    # :nodoc: Delegate comparison to keys.
    return self.key == other.key and self.wire_id == other.wire_id

  def __hash__(self):
    # :nodoc: Delegate comparison to keys.
    return hash([self.key, self.wire_id])

  def __repr__(self):
    # :nodoc: nicer formatting to help with debugging
    return '<key: ' + str(self.key) + ' wire: ' + str(self.wire) + '>'

class KeyWirePairL(KeyWirePair):
  """A KeyWirePair that is used as the low end of a range query.
  
  This KeyWirePair is smaller than all other KeyWirePairs with the same key."""
  def __init__(self, key):
    self.key = key
    self.wire = None
    self.wire_id = -1000000000

class KeyWirePairH(KeyWirePair):
  """A KeyWirePair that is used as the high end of a range query.
  
  This KeyWirePair is larger than all other KeyWirePairs with the same key."""
  def __init__(self, key):
    self.key = key
    self.wire = None
    # HACK(pwnall): assuming 1 billion objects won't fit into RAM.
    self.wire_id = 1000000000

class CrossVerifier(object):
  """Checks whether a wire network has any crossing wires."""
  
  def __init__(self, layer):
    """Verifier for a layer of wires.
    
    Once created, the verifier can list the crossings between wires (the 
    wire_crossings method) or count the crossings (count_crossings)."""

    self.events = []
    self._events_from_layer(layer)
    self.events.sort()
  
    self.index = RangeIndex()
    self.result_set = ResultSet()
    self.performed = False
  
  def count_crossings(self):
    """Returns the number of pairs of wires that cross each other."""
    if self.performed:
      raise 
    self.performed = True
    return self._compute_crossings(True)

  def wire_crossings(self):
    """An array of pairs of wires that cross each other."""
    if self.performed:
      raise 
    self.performed = True
    return self._compute_crossings(False)

  def _events_from_layer(self, layer):
    """Populates the sweep line events from the wire layer."""
    for wire in layer.wires.values():
      if wire.is_horizontal():
        self.events.append([wire.x1, 0, wire.object_id, 'add', wire])
        self.events.append([wire.x2, 2, wire.object_id, 'remove', wire])
      else:
        self.events.append([wire.x1, 1, wire.object_id, 'query', wire])

  def _compute_crossings(self, count_only):
    """Implements count_crossings and wire_crossings."""
    if count_only:
      result = 0
    else:
      result = self.result_set

    for event in self.events:
        event_x, event_type, wire = event[0], event[3], event[4]
        self.trace_sweep_line(event_x)
        if event_type == 'add':
            self.index.add(KeyWirePair(wire.y1, wire))
        elif event_type == 'remove':
            self.index.remove(KeyWirePair(wire.y1, wire))  
        elif event_type == 'query': 
            if count_only:
                result += self.index.count(KeyWirePairL(wire.y1), \
                                 KeyWirePairH(wire.y2)):
            else:
                cross_wires = []
                for kwp in self.index.list(KeyWirePairL(wire.y1), \
                                       KeyWirePairH(wire.y2)):
                cross_wires.append(kwp.wire)
                for cross_wire in cross_wires:
                    result.add_crossing(wire, cross_wire)

    return result
  
  def trace_sweep_line(self, x):
    """When tracing is enabled, adds info about where the sweep line is.
    
    Args:
      x: the coordinate of the vertical sweep line
    """
    # NOTE: this is overridden in TracedCrossVerifier
    pass

# Nothing outside the subtree is between l and h

class TracedCrossVerifier(CrossVerifier):
  """Augments CrossVerifier to build a trace for the visualizer."""
  
  def __init__(self, layer):
    CrossVerifier.__init__(self, layer)
    self.trace = []
    self.index = TracedRangeIndex(self.trace)
    self.result_set = TracedResultSet(self.trace)
    
  def trace_sweep_line(self, x):
    self.trace.append({'type': 'sweep', 'x': x})
    
  def trace_as_json(self):
    """List that obeys the JSON format restrictions with the verifier trace."""
    return self.trace

# Command-line controller.
if __name__ == '__main__':
    import sys
    layer = WireLayer.from_file(sys.stdin)
    verifier = CrossVerifier(layer)
    
    if os.environ.get('TRACE') == 'jsonp':
      verifier = TracedCrossVerifier(layer)
      result = verifier.wire_crossings()
      json_obj = {'layer': layer.as_json(), 'trace': verifier.trace_as_json()}
      sys.stdout.write('onJsonp(')
      json.dump(json_obj, sys.stdout)
      sys.stdout.write(');\n')
    elif os.environ.get('TRACE') == 'list':
      verifier.wire_crossings().write_to_file(sys.stdout)
    else:
      sys.stdout.write(str(verifier.count_crossings()) + "\n")
