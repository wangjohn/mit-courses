"""
Script to find a good path of wires from one point on a board to another,
    attempting not to cross drawables and other wires already on the board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import BEND_COST
from constants import BOARD_GRID_SEPARATION
from constants import CROSS_COST
from core.search.search import a_star
from core.search.search import Search_Node
from core.util.util import sign
from util import snap
from util import path_coverage
from util import wire_coverage

def _manhattan_dist(start, end):
  """
  Returns the Manhattan distance on the board from point |start| to point |end|.
  """
  x1, y1 = start
  x2, y2 = end
  return (abs(x1 - x2) + abs(y1 - y2)) / BOARD_GRID_SEPARATION

class Wire_Path_Search_Node(Search_Node):
  """
  Search_Node for wire path search.
  """
  def __init__(self, board_coverage, current_point, num_bends=0, direction=None,
      steps=0, parent=None, cost=0):
    Search_Node.__init__(self, (board_coverage, current_point, num_bends,
        direction, steps), parent, cost)
  def get_children(self):
    board_coverage, current_point, num_bends, direction, steps = self.state
    x, y = current_point
    children = []
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
      new_x = x + dx * BOARD_GRID_SEPARATION
      new_y = y + dy * BOARD_GRID_SEPARATION
      new_wire_coverage = wire_coverage((new_x, new_y), current_point)
      bend = direction is not None and direction != (dx, dy)
      cost = self.cost + 1 + CROSS_COST * len(board_coverage &
          new_wire_coverage) + BEND_COST * bend + abs(dy) * 0.001 * steps
      children.append(Wire_Path_Search_Node(board_coverage, (new_x, new_y),
          num_bends + bend, (dx, dy), steps + 1, self, cost))
    return children

def goal_test_for_end_point(end_point):
  def goal_test(state):
    board_coverage, current_point, num_bends, direction, steps = state
    return current_point == end_point
  return goal_test

def heuristic_for_end_point(end_point):
  def heuristic(state):
    board_coverage, current_point, num_bends, direction, steps = state
    x1, y1 = current_point
    x2, y2 = end_point
    return _manhattan_dist(current_point, end_point) + BEND_COST * (
        (x1 != x2) and (y1 != y2))
  return heuristic

def condensed_points(points):
  """
  Returns a collapsed version of |points| so that there are no three consecutive
      collinear points.
  """
  assert len(points) >= 1
  condensed = points[:1]
  for i in xrange(1, len(points) - 1):
    _x, _y = condensed[-1]
    x, y = points[i]
    x_, y_ = points[i + 1]
    if sign(x - _x) != sign(x_ - x) or sign(y - _y) != sign(y_ - y):
      condensed.append(points[i])
  condensed.append(points[-1])
  return condensed

def find_wire_path_simple(board_coverage, start_point, end_point):
  """
  Returns a list of tuples indicating a path from |start_point| to |end_point|
      on a board, doing an exhaustive search for paths including up to 2
      bends. Tries to avoid points in |board_coverage|.
  """
  x1, y1 = start_point
  x2, y2 = end_point
  if x1 == x2 or y1 == y2:
    return [start_point, end_point]
  else:
    paths = [[(x1, y1), (x1, y2), (x2, y2)], [(x1, y1), (x2, y1), (x2, y2)]]
    x_sign = 1 if x1 <= x2 else -1
    for x in xrange(x1 + x_sign * BOARD_GRID_SEPARATION, x2, x_sign *
        BOARD_GRID_SEPARATION):
      paths.append([(x1, y1), (x, y1), (x, y2), (x2, y2)])
    y_sign = 1 if y1 <= y2 else -1
    for y in xrange(y1 + y_sign * BOARD_GRID_SEPARATION, y2, y_sign *
        BOARD_GRID_SEPARATION):
      paths.append([(x1, y1), (x1, y), (x2, y), (x2, y2)])
    return min(paths, key=lambda path: len(board_coverage & path_coverage(
        path)))

def find_wire_path(board_coverage, start_point, end_point):
  """
  Returns a list of tuples indicating a path from |start_point| to |end_point|
      on a board, doing an overall search. If the overall search takes too
      long, uses find_wire_path_simple. Tries to avoid points in
      |board_coverage|.
  """
  board_coverage = frozenset(board_coverage)
  search_result, num_expanded = a_star(Wire_Path_Search_Node(board_coverage,
      start_point), goal_test_for_end_point(end_point),
      heuristic_for_end_point(end_point), max_states_to_expand=1000,
      verbose=False)
  if search_result:
    return condensed_points([state[1] for state in search_result.get_path()])
  else:
    return find_wire_path_simple(board_coverage, start_point, end_point)
