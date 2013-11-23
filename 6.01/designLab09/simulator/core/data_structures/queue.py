"""
Queue.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

class Queue:
  """
  Queue data structure that supports push and pop.
  """
  def __init__(self):
    self._data = []
  def push(self, item):
    """
    Adds |item| to the queue.
    """
    self._data.append(item)
  def pop(self):
    """
    Returns the oldest item in the queue, or None if the queue is empty.
    """
    if self._data:
      return self._data.pop(0)
    return None
  def __bool__(self):
    return bool(self._data)
  def __iter__(self):
    return iter(self._data)
  def __len__(self):
    return len(self._data)
  def __str__(self):
    return str(self._data)
