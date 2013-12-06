"""
Miscellaneous utility methods.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

def clip(val, m, M):
  """
  Clips |val| between minimum |m| and maximum |M|.
  """
  return min(max(val, m), M)

def empty(items):
  """
  Returns True if |items| is empty, False otherwise.
  """
  return len(items) == 0

def in_bounds(val, min_val, max_val):
  """
  Returns True if min_val <= val <= max_val, False otherwise.
  """
  return min_val <= val <= max_val

def is_callable(obj):
  """
  Returns True if |obj| is callable, False otherwise.
  """
  return hasattr(obj, '__call__')

def is_number(val):
  """
  Returns True if |val| is a number, False otherwise.
  """
  return isinstance(val, (complex, float, int, long))

def overlap(interval_1, interval_2):
  """
  Returns True if the given intervals overlap, False otherwise. Note that we
      consider, for example, (1, 2) and (2, 3) to overlap.
  """
  min_1, max_1 = interval_1
  min_2, max_2 = interval_2
  return min(max_1, max_2) >= max(min_1, min_2)

def rects_overlap(rect_1, rect_2):
  """
  Returns True if the given rectangles (represented as a tuple (r_min, c_min,
      r_max, c_max)) overlap, False otherwise.
  """
  r_min_1, c_min_1, r_max_1, c_max_1 = rect_1
  r_min_2, c_min_2, r_max_2, c_max_2 = rect_2
  return (overlap((r_min_1, r_max_1), (r_min_2, r_max_2)) and overlap((c_min_1,
      c_max_1), (c_min_2, c_max_2)))

def sign(x):
  """
  Returns -1 if |x| is negative, 1 if |x| is positive, or 0 if |x| is 0.
  """
  if x < 0:
    return -1
  elif x > 0:
    return 1
  return 0
