"""
Representation for a wire on a proto board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import NUM_ROWS_PER_VERTICAL_SEPARATION
from core.math.line_segment_intersect import intersect
from core.util.util import sign
from math import sqrt
from util import num_vertical_separators

class Wire:
  """
  Wire representation.
  """
  def __init__(self, loc_1, loc_2, node):
    """
    |loc_1|, |loc_2|: start end end locations of this wire.
    |node|: the circuit node this wire is a part of.
    """
    self.loc_1 = loc_1
    self.loc_2 = loc_2
    r_1, c_1 = loc_1
    r_2, c_2 = loc_2
    self.r_1 = r_1
    self.c_1 = c_1
    self.r_2 = r_2
    self.c_2 = c_2
    self.node = node
  def crosses(self, other):
    """
    Returns True if this wire and the |other| wire intersect, False otherwise.
    """
    assert isinstance(other, Wire), 'other must be a Wire'
    return  intersect((self.loc_1, self.loc_2), (other.loc_1,
        other.loc_2)) != False
  def length(self):
    """
    Returns the length of this wire.
    """
    vertical_separators = num_vertical_separators(max(self.r_1, self.r_2)) - (
        num_vertical_separators(min(self.r_1, self.r_2)))
    return sqrt((abs(self.r_1 - self.r_2) + vertical_separators *
        NUM_ROWS_PER_VERTICAL_SEPARATION) ** 2 + (self.c_1 - self.c_2) ** 2)
  def horizontal(self):
    """
    Returns True if this wire is horizontal, False otherwise.
    """
    return self.r_1 == self.r_2
  def vertical(self):
    """
    Returns True if this wire is vertical, False otherwise.
    """
    return self.c_1 == self.c_2
  def locs(self):
    """
    Returns an (approximate) list of the locations on the proto board covered by
        this wire.
    """
    dr = self.r_1 - self.r_2
    _dr = sign(dr)
    dc = self.c_1 - self.c_2
    _dc = sign(dc)
    if dr == 0:
      return [(self.r_1, c) for c in xrange(self.c_1, self.c_2 - _dc, -_dc)]
    elif dc == 0:
      return [(r, self.c_1) for r in xrange(self.r_1, self.r_2 - _dr, -_dr)]
    elif abs(dc) > abs(dr):
      return [(self.r_1 + (c - self.c_1) * dr / dc , c) for c in xrange(
          self.c_1, self.c_2 - _dc, -_dc)]
    else: # abs(dr) >= abs(dc)
      return [(r, self.c_1 + (r - self.r_1) * dc / dr) for r in xrange(
          self.r_1, self.r_2 - _dr, -_dr)]
  def __str__(self):
    return 'Wire %s-%s %s' % (self.loc_1, self.loc_2, self.node)
  def __eq__(self, other):
    return (isinstance(other, Wire) and ((self.loc_1 == other.loc_1 and
        self.loc_2 == other.loc_2) or (self.loc_1 == other.loc_2 and
        self.loc_2 == other.loc_1)) and self.node == other.node)
  def __hash__(self):
    return hash((frozenset([self.loc_1, self.loc_2]), self.node))
