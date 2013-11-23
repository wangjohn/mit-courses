"""
Disjoint set forest data structure.
Credit to Introduction to Algorithms (CLRS) Chapter 21.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from collections import defaultdict

class Disjoint_Set_Forest:
  """
  Disjoint set forest data structure.
  """
  def __init__(self, parent=None, rank=None):
    """
    |parent|: stores parent pointers.
    |rank|: stores node ranks.
    """
    self._parent = parent if parent is not None else {}
    self._rank = rank if rank is not None else {}
  def make_set(self, x):
    """
    Makes a new set containing just |x|, if a set containing |x| does not
        already exist.
    """
    if x not in self._parent:
      self._parent[x] = x
      self._rank[x] = 0
  def _link(self, x, y):
    """
    Unites the sets represented by |x| and |y|.
    Assumes that |x| and |y| are set representatives.
    """
    assert x in self._parent
    assert y in self._parent
    if self._rank[x] > self._rank[y]:
      self._parent[y] = x
    else:
      self._parent[x] = y
      if self._rank[x] == self._rank[y]:
        self._rank[y] += 1
  def union(self, x, y):
    """
    Unites the sets containing |x| and |y|.
    Assuemes that |x| and |y| are in this forest.
    """
    self._link(self.find_set(x), self.find_set(y))
  def find_set(self, x):
    """
    If there is a set containing |x|, returns that set's representative.
        Returns None otherwise.
    """
    if x not in self._parent:
      return None
    elif self._parent[x] != x:
      self._parent[x] = self.find_set(self._parent[x])
    return self._parent[x]
  def copy(self):
    """
    Returns a copy of this forest.
    """
    return Disjoint_Set_Forest(self._parent.copy(), self._rank.copy())
  def __str__(self):
    disjoint_sets = defaultdict(list)
    for x in self._parent:
      disjoint_sets[self.find_set(x)].append(x)
    return '\n'.join(map(str, disjoint_sets.values()))
  def __eq__(self, other):
    return (isinstance(other, Disjoint_Set_Forest) and frozenset(
        self._parent.items()) == frozenset(other._parent.items()) and frozenset(
        self._rank.items()) == frozenset(other._rank.items()))
  def __hash__(self):
    return hash((frozenset(self._parent.items()), frozenset(
        self._rank.items())))
