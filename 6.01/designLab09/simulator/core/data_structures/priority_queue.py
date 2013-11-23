"""
Priority queue.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from heapq import heappop
from heapq import heappush

class Priority_Queue:
  """
  Priority queue data structure.
  """
  def __init__(self):
    self.data = []
  def push(self, item, cost):
    """
    Adds the given |item| having the given |cost|.
    """
    heappush(self.data, (cost, item))
  def pop(self):
    """
    Removes and returns the (item, cost) pair in this priority queue with the
        smallest cost, or None if the queue is empty.
    """
    if not self.data:
      return None
    cost, item = heappop(self.data)
    return item, cost
  def __bool__(self):
    return bool(self.data)
  def __len__(self):
    return len(self.data)
  def __str__(self):
    return str(self.data)
