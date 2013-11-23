"""
Tools to figure out a good placement of circuit pieces on the proto board given
    the pieces.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_pieces import Circuit_Piece
from circuit_pieces import N_Pin_Connector_Piece
from circuit_pieces import Op_Amp_Piece
from circuit_pieces import Place_Holder_Piece
from circuit_pieces import Pot_Piece
from circuit_pieces import Resistor_Piece
from circuit_simulator.main.constants import GROUND
from circuit_simulator.main.constants import POWER
from collections import defaultdict
from constants import BODY_BOTTOM_ROWS
from constants import BODY_TOP_ROWS
from constants import COST_TYPE_BLOCKING
from constants import COST_TYPE_DISTANCE
from constants import GROUND_RAIL
from constants import POWER_RAIL
from constants import PROTO_BOARD_WIDTH
from constants import PROTO_BOARD_HEIGHT
from constants import RAIL_LEGAL_COLUMNS
from constants import RAIL_ROWS
from copy import deepcopy
from core.data_structures.disjoint_set_forest import Disjoint_Set_Forest
from core.data_structures.queue import Queue
from itertools import permutations
from itertools import product
from util import body_section_rows
from util import dist

def closest_rail_loc(loc, rail_r):
  """
  Returns the closest rail location in row |rail_r| to the location |loc|.
  """
  assert rail_r in RAIL_ROWS, 'rail_r must be a rail row'
  r, c = loc
  return (rail_r, min(RAIL_LEGAL_COLUMNS, key=lambda col: abs(c - col)))

def loc_pairs_for_node(node_locs, node):
  """
  Returns a list of tuples of the form  (loc_1, loc_2, node) such that the set
      of locations in |nodes_locs| is fully connected if all the output pairs of
      locations are connected. This is essentially an MST problem where the
      locations are the nodes and the weight of an edge between two locations
      is the distance (manhattan) between the two locations. We use Kruskal's
      greedy algorithm. |node| is the corresponding node in for the locations
      in the circuit.
  """
  if node == GROUND or node == POWER:
    return [(loc, closest_rail_loc(loc, GROUND_RAIL if node == GROUND else
        POWER_RAIL), node) for loc in node_locs]
  # find all possible pairs of locations
  all_loc_pairs = [(loc_1, loc_2) for i, loc_1 in enumerate(node_locs) for
      loc_2 in node_locs[i + 1:]]
  # sort in increasing order of loc pair distance
  all_loc_pairs.sort(key=lambda loc_pair: dist(*loc_pair))
  disjoint_loc_pair_sets = Disjoint_Set_Forest()
  # initialize the graph as fully disconnected
  for loc in node_locs:
    disjoint_loc_pair_sets.make_set(loc)
  mst_loc_pairs = []
  # add edges to the graph until fully connected, but use the least expensive
  # edges to do so in the process
  for (loc_1, loc_2) in all_loc_pairs:
    if (disjoint_loc_pair_sets.find_set(loc_1) !=
        disjoint_loc_pair_sets.find_set(loc_2)):
      disjoint_loc_pair_sets.union(loc_1, loc_2)
      mst_loc_pairs.append((loc_1, loc_2, node))
  return mst_loc_pairs

def locs_for_node(pieces, node):
  """
  Returns a list of all the locations associated with the given |node| among
      all of the pieces in |pieces|.
  """
  return reduce(list.__add__, (piece.locs_for(node) for piece in pieces), [])

def all_nodes(pieces):
  """
  Returns a list of all of the nodes present in the given collection of
      |pieces|.
  """
  return reduce(set.union, (piece.nodes for piece in pieces), set())

def loc_pairs_to_connect(pieces, resistors):
  """
  Returns a tuple of the locations pairs to connect so that the |pieces| and
      |resistors| are appropriately connected. Each location pairs
      comes with a flag indicating whether or not to include a resistor. Each
      location pair also comes with the node for the pair. If there is to be a
      resistor between the locations, the node of the first location is given (
      both nodes can be obtained from the flag, the first is given for the sake
      of consistency).
  """
  # find loc pairs to connect not taking resistors into account
  loc_pairs = reduce(list.__add__, (loc_pairs_for_node(locs_for_node(pieces,
      node), node) for node in all_nodes(pieces) if node), [])
  # find loc pairs to connect for resistors
  occurences = defaultdict(int)
  flagged_loc_pairs = []
  for loc_1, loc_2, node in loc_pairs:
    occurences[loc_1] += 1
    occurences[loc_2] += 1
    flagged_loc_pairs.append((loc_1, loc_2, None, node))
  # where resistors are treated as wires, what we have here is very ad hoc!
  for resistor in resistors:
    loc_1, loc_2 = min(product(locs_for_node(pieces, resistor.n1),
        locs_for_node(pieces, resistor.n2)), key=lambda (loc_1, loc_2): 5 * (
        occurences[loc_1] + occurences[loc_2]) + dist(loc_1, loc_2))
    occurences[loc_1] += 1
    occurences[loc_2] += 1
    flagged_loc_pairs.append((loc_1, loc_2, resistor, resistor.n1))
  return flagged_loc_pairs

def set_locations(pieces, resistors_as_components):
  """
  Given a (ordered) list of |pieces|, assigns them locations on the proto
      board. Tries to center the pieces in the middle of the proto board. Leaves
      a separation of 2 (or 3 if |resistors_as_components|) columns between each
      consecuitive pair of pieces, unless the pieces are both resistors, in
      which case only 1 column is left. Returns True if the pieces are
      successfully assigned top_left_locs (i.e. if they fit on the board), False
      otherwise.
  """
  pair_separation = 2 if resistors_as_components else 3
  # find spaces (in number of columns) between each consecutive pair of pieces
  separations = []
  for i in xrange(len(pieces) - 1):
    separations.append(1 if isinstance(pieces[i], Resistor_Piece) and
        isinstance(pieces[i + 1], Resistor_Piece) else pair_separation)
  # set piece locations, trying to center the group
  separations.append(0)
  col = (PROTO_BOARD_WIDTH - sum(piece.width for piece in pieces) - sum(
      separations)) / 2
  if col < 0:
    return False
  for i, piece in enumerate(pieces):
    piece.top_left_loc = (piece.top_left_row, col)
    col += piece.width + separations[i]
  return True

def _distance_cost(placement):
  """
  Placement cost based on total distance to connect.
  """
  return sum(dist(loc_1, loc_2) for loc_1, loc_2, resistor_flag, node in
      loc_pairs_to_connect(placement, []))

def _blocking_cost(placement):
  """
  Placement cost based on how many rows are blocked.
  """
  def row_rep(r):
    if r in BODY_TOP_ROWS:
      return 2
    elif r in BODY_BOTTOM_ROWS:
      return PROTO_BOARD_HEIGHT - 3
    else:
      return r
  counter = defaultdict(int)
  for piece in placement:
    r, c = piece.top_left_loc
    if isinstance(piece, N_Pin_Connector_Piece):
      _r = min((2, PROTO_BOARD_HEIGHT - 3), key=lambda _r: abs(r - _r))
      for _c in xrange(c, c + piece.width):
        counter[(_r, _c)] += 1
    else:
      for _r in xrange(r, r + piece.height):
        for _c in xrange(c, c + piece.width):
          counter[(row_rep(_r), _c)] += 1
  for loc_1, loc_2, resistor_flag, node in loc_pairs_to_connect(placement, []):
    r1, c1 = loc_1
    r2, c2 = loc_2
    for _r in set([row_rep(r1), row_rep(r2)]):
      for _c in xrange(min(c1, c2), max(c1, c2) + 1):
        counter[(_r, _c)] += 1
  return sum(v ** 2 for v in counter.values())

def cost(placement, resistors_as_components, cost_type):
  """
  Returns a heuristic cost of the given |placement|. Returns float('inf') if the
      |placement| does not fit on a board.
  """
  if set_locations(placement, resistors_as_components):
    if cost_type == COST_TYPE_BLOCKING:
      return _blocking_cost(placement)
    elif cost_type == COST_TYPE_DISTANCE:
      return _distance_cost(placement)
    else:
      raise Exception('Unexpected cost type: %s' % cost_type)
  else:
    return float('inf')

def find_placement(pieces, resistors_as_components, cost_type):
  """
  Given a list of |pieces|, returns a placement of the pieces that requires
      comparatively small wiring. Finding the absolute best placement is too
      expensive. If the |pieces| cannot be placed so as to fit on a protoboard,
      returns None with a cost of float('inf').
  """
  assert isinstance(pieces, list), 'pieces must be a list'
  assert all(isinstance(piece, Circuit_Piece) for piece in pieces), ('all '
      'items in pieces must be Circuit_Pieces')
  pieces = deepcopy(pieces)
  if len(pieces) == 0:
    return [], 0
  # order pieces in decreasing number of nodes
  pieces.sort(key=lambda piece: -len(piece.nodes))
  queue = Queue()
  def add_to_queue(piece):
    if piece in pieces:
      queue.push(piece)
      pieces.remove(piece)
  placement = []
  placement_cost = float('inf')
  while pieces:
    add_to_queue(pieces[0])
    while queue:
      current_piece = queue.pop()
      # try inserting the current piece at all possible indicies in the current
      #     placement, consider both regular and inverted piece
      best_placement = None
      best_placement_cost = float('inf')
      # all indicies in which the piece can be inserted
      for i in xrange(len(placement) + 1):
        # both regular and inverted piece
        for piece in set([current_piece, current_piece.inverted()]):
          for top_left_row in piece.possible_top_left_rows:
            piece.top_left_row = top_left_row
            new_placement = deepcopy(placement)
            new_placement.insert(i, piece)
            new_placement_cost = cost(new_placement, resistors_as_components,
                cost_type)
            if new_placement_cost < best_placement_cost:
              best_placement = deepcopy(new_placement)
              best_placement_cost = new_placement_cost
      if best_placement is None:
        return None, float('inf')
      placement = best_placement
      placement_cost = best_placement_cost
      # add pieces connected to this piece to the queue
      for piece in reduce(list.__add__, [[piece for piece in pieces if node
          in piece.nodes] for node in current_piece.nodes], []):
        add_to_queue(piece)
  return placement, placement_cost

def _find_placement(pieces, resistors_as_components, cost_type):
  """
  find_placement that looks at every possibility. Takes too long!
  """
  piece_options = []
  for piece in pieces:
    options = []
    for p in set([piece, piece.inverted()]):
      for top_left_row in piece.possible_top_left_rows:
        option = deepcopy(p)
        option.top_left_row = top_left_row
        options.append(option)
    piece_options.append(options)
  best_placement = None
  best_cost = float('inf')
  for perm in permutations(piece_options):
    perm_best = min(product(*perm), key=cost)
    perm_best_cost = cost(perm_best, resistors_as_components, cost_type)
    if perm_best_cost < best_cost:
      best_placement = perm_best
      best_cost = perm_best_cost
  return best_placement, best_cost
