"""
Search infrastructure.
Credit to Chapter 7 of MIT 6.01 notes
    (http://mit.edu/6.01/www/handouts/readings.pdf).
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import PRINT_FAIL_REASON
from core.data_structures.priority_queue import Priority_Queue

class Search_Node:
  """
  Representation for a node in the search graph. Clients of the search
      infrastructure should use subclasses of Search_Node implementing the
      get_children method.
  """
  def __init__(self, state, parent=None, cost=0):
    """
    |state|: state of the search node, dependent on the application.
    |parent|: parent node to this node, None if this node is the root.
    |cost|: cost to reach from the root node to this node.
    """
    self.state = state
    self.parent = parent
    self.cost = cost
  def get_children(self):
    """
    Should return a list of the Search_Nodes that are reachable from this node.
    """
    raise NotImplementedError('subclasses should implement this')
  def get_path(self):
    """
    Returns a list of the states of the nodes from the root to this node.
    """
    path = []
    current = self
    while current is not None:
      path = [current.state] + path
      current = current.parent
    return path

def a_star(start_node, goal_test, heuristic=lambda state: 0, best_first=False,
    progress=lambda state, cost: None, max_states_to_expand=None, verbose=True):
  """
  Runs an A* search starting at |start_node| until a node that satisfies the
      |goal_test| is found. |goal_test| should be a function that takes in a
      state of a node and returns True if the desired goal has been satisfied.
      |heuristic| is a map from node states to estimates of distance to the
      goal, should be admissible to produce optimal value, and can result in
      considerable speed-up! (See Chapter 7 of MIT 6.01 course notes for more.)
  Returns the node whose state satisfies teh |goal_test|, or None if no such
      node is found. Also returns the total number of nodes expanded.
  For progress checks, everytime a node is popped out of the priority queue,
      this methods calls |progress| with the state and cost of the node that
      was just popped.
  So that a search problem does not take too long without success, may give a
      |max_states_to_expand| after which the search stops and returns None.
  """
  if goal_test(start_node.state):
    return start_node, 0
  agenda = Priority_Queue()
  agenda.push(start_node, (not best_first) * start_node.cost +
      heuristic(start_node.state))
  expanded = set()
  while agenda:
    parent, cost = agenda.pop()
    progress(parent.state, cost)
    if parent.state not in expanded:
      if goal_test(parent.state):
        return parent, len(expanded)
      expanded.add(parent.state)
      for child in parent.get_children():
        if child.state not in expanded:
          agenda.push(child, (not best_first) * child.cost +
              heuristic(child.state))
    if max_states_to_expand and len(expanded) > max_states_to_expand:
      if PRINT_FAIL_REASON:
        if verbose:
          print 'exceeded number of states to expand'
      return None, len(expanded)
  if PRINT_FAIL_REASON:
    if verbose:
      print 'exhausted search space'
  return None, len(expanded)
