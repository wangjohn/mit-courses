"""
Utility methods.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import BODY_BOTTOM_ROWS
from constants import BODY_LEGAL_COLUMNS
from constants import BODY_ROWS
from constants import BODY_TOP_ROWS
from constants import NUM_ROWS_PER_VERTICAL_SEPARATION
from constants import PROTO_BOARD_HEIGHT
from constants import RAIL_LEGAL_COLUMNS
from constants import RAIL_ROWS
from core.data_structures.disjoint_set_forest import Disjoint_Set_Forest

def valid_loc(loc):
  """
  Returns True if |loc| is a valid location for a connector on the proto board,
      False otherwise.
  """
  r, c = loc
  if r in RAIL_ROWS:
    return c in RAIL_LEGAL_COLUMNS
  elif r in BODY_ROWS:
    return c in BODY_LEGAL_COLUMNS
  return False

def is_body_loc(loc):
  """
  Returns True if |loc| resides in the body (middle) section of the proto
      board.
  """
  r, c = loc
  return valid_loc(loc) and r in BODY_ROWS

def is_rail_loc(loc):
  """
  Returns True if |loc| resides in the rail (bus) section of the proto board.
  """
  r, c = loc
  return valid_loc(loc) and r in RAIL_ROWS

def body_section_rows(r):
  """
  Returns the set of rows physically connected to the given row |r|.
  """
  assert r in BODY_ROWS, 'r must be a body row %s' % r
  return BODY_BOTTOM_ROWS if r in BODY_BOTTOM_ROWS else BODY_TOP_ROWS

def body_opp_section_rows(r):
  """
  Returns the set of rows on the opposite body side of the given row |r|.
  """
  assert r in BODY_ROWS, 'r must be a body row %s' % r
  return BODY_BOTTOM_ROWS if r in BODY_TOP_ROWS else BODY_TOP_ROWS

def section_locs(loc):
  """
  Returns the locations physically connected to the given |loc|.
  """
  r, c = loc
  return (((r, new_c) for new_c in RAIL_LEGAL_COLUMNS) if is_rail_loc(loc)
      else ((new_r, c) for new_r in body_section_rows(r)))

def num_vertical_separators(r):
  """
  Returns the number of vertical separators that stand between the top of the
      proto board and the given row |r|.
  """
  return sum(r >= barrier for barrier in (2, PROTO_BOARD_HEIGHT / 2,
      PROTO_BOARD_HEIGHT - 2))

def dist(loc_1, loc_2):
  """
  Returns the Manhattan distance between |loc_1| and |loc_2|.
  """
  r_1, c_1 = loc_1
  r_2, c_2 = loc_2
  vertical_separators = num_vertical_separators(max(r_1, r_2)) - (
      num_vertical_separators(min(r_1, r_2)))
  return abs(r_1 - r_2) + abs(c_1 - c_2) + (
      vertical_separators * NUM_ROWS_PER_VERTICAL_SEPARATION)

def node_disjoint_set_forest(node_locs_mapping):
  """
  Returns a Disjoint_Set_Forest representation of |node_locs_mapping|, a
      dictionary mapping node names to lists of locations on the proto board to
      be connected to the corresponding node.
  """
  forest = Disjoint_Set_Forest()
  for node, locs in node_locs_mapping.items():
    forest.make_set(node)
    for loc in locs:
      for section_loc in section_locs(loc):
        forest.make_set(section_loc)
        forest.union(section_loc, node)
  return forest

def loc_to_cmax_rep(loc):
  """
  Returns a tuple for the CMax representation of the given |loc|.
  """
  r, c = loc
  return c + 1, r + 2 * num_vertical_separators(r) + 1
