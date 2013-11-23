"""
Utility methods for file saving.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from os.path import isdir
from os.path import isfile
from os.path import split

def strip_file_name(path):
  """
  Returns the file name of the given |path|, or '' on failure.
  """
  return split(path)[-1] if path and isfile(path) else ''

def strip_dir(path):
  """
  Returns the directory for the given |path|, or '' on failure.
  """
  if path:
    if isdir(path):
      return path
    elif isfile(path):
      return split(path)[0]
  return ''
