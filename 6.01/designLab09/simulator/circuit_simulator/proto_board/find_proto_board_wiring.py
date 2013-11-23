"""
Search to find proto board wiring to connect a given list of pairs of locations
    on the proto board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_pieces import Resistor_Piece
from collections import defaultdict
from constants import ALLOW_PIECE_CROSSINGS
from constants import ALLOW_WIRE_CROSSINGS
from constants import MAX_STATES_TO_EXPAND
from constants import MODE_ALL_PAIRS
from constants import MODE_PER_NODE
from constants import MODE_PER_PAIR
from constants import ORDER_DECREASING
from constants import ORDER_INCREASING
from constants import PROTO_BOARD_HEIGHT
from constants import PROTO_BOARD_WIDTH
from constants import RAIL_ROWS
from constants import ROWS
from constants import VALID_WIRE_LENGTHS
from core.search.search import a_star
from core.search.search import Search_Node
from itertools import product
from util import body_opp_section_rows
from util import dist
from util import is_body_loc
from util import is_rail_loc
from util import valid_loc
from wire import Wire

class Proto_Board_Search_Node(Search_Node):
  """
  Search_Node for proto board wiring problem.
  """
  def __init__(self, proto_board, loc_pairs, parent=None, cost=0,
      filter_wire_lengths=False):
    """
    |proto_board|: current Proto_Board in the search.
    |loc_pairs|: a tuple of tuples of the form (loc_1, loc_2, resistor, label),
        where loc_1 and loc_2 are to be connected and resistor indicates
        whether there needs to be a resistor between them. label gives the label
        for the path of wires connected to loc_1.
    |parent|: this node's parent node, or None if this is the root node.
    |cost|: the cost of getting from the root node to this node.
    """
    Search_Node.__init__(self, (proto_board, loc_pairs), parent, cost)
    self.filter_wire_lengths = filter_wire_lengths
  def _valid_not_occupied_filter(self, proto_board):
    """
    Returns a filter for locations that are valid and not occupied on the
        given |proto_board|.
    """
    return lambda loc: valid_loc(loc) and not proto_board.occupied(loc)
  def _wire_ends_from_rail_loc(self, loc, proto_board):
    """
    Returns a list of the locations that can be connected by a wire with the
        given |loc| on the given |proto_board|, assuming that |loc| is a rail
        location.
    """
    assert is_rail_loc(loc)
    r, c = loc
    # can draw vertical wires to every other location in the same column
    wire_ends = [(new_r, c) for new_r in ROWS]
    return filter(self._valid_not_occupied_filter(proto_board), wire_ends)
  def _wire_ends_from_body_loc(self, loc, proto_board, span):
    """
    Returns a list of the locations that can be connected by a wire with the
        given |loc| on the given |proto_board|, assuming that |loc| is a body
        location. |span| is the length of the longest wire that may be used.
    """
    assert is_body_loc(loc)
    # make max possible horizontal wire length at least 5
    span = max(span, 5)
    r, c = loc
    wire_ends = []
    # can draw horizontal wires to locations to the left and right of |loc|
    # note that we limit the lengh of these horizontal wires (can technically
    #     be very big, but considering all gets us a huge branching factor)
    wire_lengths = range(1, span + 1)
    if self.filter_wire_lengths:
      wire_lengths = filter(VALID_WIRE_LENGTHS.__contains__, wire_lengths)
    for l in wire_lengths:
      wire_ends.append((r, c - l))
      wire_ends.append((r, c + l))
    # can draw vertical wires to the opposite half
    for new_r in body_opp_section_rows(r):
      wire_ends.append((new_r, c))
    # can draw vertical wires to the rails
    for rail_r in RAIL_ROWS:
      wire_ends.append((rail_r, c))
    return filter(self._valid_not_occupied_filter(proto_board), wire_ends)
  def get_children(self):
    children = []
    proto_board, loc_pairs = self.state
    for i, (loc_1, loc_2, resistor, node) in enumerate(loc_pairs):
      # can extend a wire from |loc_1| towards |loc_2| from any of the
      #     the locations |loc_1| is internally connected to
      for neighbor_loc in filter(proto_board.free,
          proto_board.locs_connected_to(loc_1)):
        # get candidate end locations for the new wire to draw
        wire_ends = (self._wire_ends_from_rail_loc(neighbor_loc,
            proto_board) if is_rail_loc(neighbor_loc) else
            self._wire_ends_from_body_loc(neighbor_loc, proto_board,
            span=dist(loc_1, loc_2)))
        for wire_end in wire_ends:
          # make sure that there is a wire to draw
          if wire_end == neighbor_loc:
            continue
          new_wire = Wire(neighbor_loc, wire_end, node)
          # track number of pieces this wire crosses
          num_piece_crossings = sum(piece.crossed_by(new_wire) for piece in
              proto_board.get_pieces())
          if not ALLOW_PIECE_CROSSINGS and num_piece_crossings:
            continue
          # track number of other wires this new wire crosses
          any_same_orientation_crossings = False
          num_wire_crossings = 0
          for wire in proto_board.get_wires():
            if wire.crosses(new_wire):
              if wire.vertical() == new_wire.vertical():
                any_same_orientation_crossings = True
                break
              else:
                num_wire_crossings += 1
          # don't allow any wire crossings where the two wires have the same
          #     orientation
          if any_same_orientation_crossings:
            continue
          # continue if we do not want to allow any crossing wires at all, even
          #     ones of different orientation
          if not ALLOW_WIRE_CROSSINGS and num_wire_crossings:
            continue
          # construct a proto board with this new wire
          wire_proto_board = proto_board.with_wire(new_wire)
          # check that adding the wire is reasonable
          wire_proto_board_valid = (wire_proto_board and wire_proto_board is
              not proto_board)
          # potentially create another proto board with a resistor in place of
          #     the new wire
          add_resistor = (resistor is not None and not num_piece_crossings and
              not num_wire_crossings and new_wire.length() == 3)
          if add_resistor:
            n1, n2, r, label = (resistor.n1, resistor.n2, resistor.r,
                resistor.label)
            # find representatives for the two nodes, they better be there
            n1_group = proto_board.rep_for(n1)
            assert n1_group
            n2_group = proto_board.rep_for(n2)
            assert n2_group
            # check that wire loc 1 is in the same group as node n1
            assert proto_board.rep_for(new_wire.loc_1) == n1_group
            # find representative for wire loc 2, might not be there
            wire_loc_2_group = proto_board.rep_for(new_wire.loc_2)
            # if it is there, it better be the same as n2_group, or we can't put
            #     a resistor here
            if (not wire_loc_2_group) or wire_loc_2_group == n2_group:
              # figure out correct orientation of Resistor_Piece n1 and n2
              vertical = new_wire.vertical()
              if new_wire.c_1 < new_wire.c_2 or new_wire.r_1 < new_wire.r_2:
                resistor_piece = Resistor_Piece(n1, n2, r, vertical, label)
                resistor_piece.top_left_loc = new_wire.loc_1
              else:
                resistor_piece = Resistor_Piece(n2, n1, r, vertical, label)
                resistor_piece.top_left_loc = new_wire.loc_2
              # create proto board with resistor
              new_proto_board = proto_board.with_piece(resistor_piece)
              if not wire_loc_2_group:
                # ensure to mark the oposite location with its apporpriate node
                new_proto_board = new_proto_board.with_loc_repped(n2_group,
                    new_wire.loc_2)
              # would no longer need a resistor for this pair of locations
              new_resistor = None
              # and the node for the rest of the wires will be the node for the
              #     other end of the resistor
              new_node = n2
            else:
              # placing the resistor would create a violating connection
              add_resistor = False
          if not add_resistor:
            if wire_proto_board_valid:
              # can still put a wire down if allowed
              new_proto_board = wire_proto_board
              new_resistor = resistor
              new_node = node
            else:
              continue
          # we have a candidate proto board, compute state and cost
          new_loc_pairs = list(loc_pairs)
          new_cost = self.cost + new_wire.length()
          if proto_board.connected(wire_end, loc_2):
            new_loc_pairs.pop(i)
            # favor connectedness a lot
            new_cost -= 100
          else:
            new_loc_pairs[i] = (wire_end, loc_2, new_resistor, new_node)
          # penalize long wires
          new_cost += new_wire.length()
          # penalize many wires
          new_cost += 10
          # penalize wires crossing pieces (if allowed at all)
          new_cost += 1000 * num_piece_crossings
          # penalize crossing wires of opposite orientation (if allowed at all)
          new_cost += 1000 * num_wire_crossings
          # favor wires that get us close to the goal, and penalize wires
          #     that get us farther away
          new_cost += dist(wire_end, loc_2) - dist(loc_1, loc_2)
          children.append(Proto_Board_Search_Node(new_proto_board,
              frozenset(new_loc_pairs), self, new_cost,
              self.filter_wire_lengths))
          # if added a resistor, also create a proto board where we use a wire
          #     instead of the resistor
          if add_resistor and wire_proto_board_valid:
            wire_loc_pairs = list(loc_pairs)
            wire_loc_pairs[i] = (wire_end, loc_2, resistor, node)
            children.append(Proto_Board_Search_Node(wire_proto_board,
                frozenset(wire_loc_pairs), self, new_cost,
                self.filter_wire_lengths))
    return children

def goal_test(state):
  """
  Returns True if the given Proto_Board_Search_Node |state| satisfies the
      condition that all location pairs to be connected have been connected,
      False otherwise.
  """
  proto_board, loc_pairs = state
  return all((resistor is None) and proto_board.connected(loc_1, loc_2) for
      (loc_1, loc_2, resistor, node) in loc_pairs)

def heuristic(state):
  """
  Returns an estimate of the distance between the given Proto_Board_Search_Node
      |state| and a goal state.
  """
  proto_board, loc_pairs = state
  return sum(min(dist(loc_1, loc) for loc in proto_board.locs_connected_to(
      loc_2)) for loc_1, loc_2, resistor, node in loc_pairs)

def find_wiring(loc_pairs, start_proto_board, mode, order, best_first,
    filter_wire_lengths, max_states_to_expand=MAX_STATES_TO_EXPAND,
    verbose=True):
  """
  Returns a Proto_Board in which all the pairs of locations in |loc_pairs| are
      properly connected, or None if no such Proto_Board can be found. Search
      starts from |start_proto_board|. Also returns the total number of nodes
      expanded in the search.
  |mode|: MODE_ALL_PAIRS | MODE_PER_NODE | MODE_PER_PAIR
      MODE_ALL_PAIRS: connect all pairs in one search.
      MODE_PER_NODE: connect the pairs for each node in a separate search.
      MODE_PER_PAIR: connect each pair in a separate search.
  |order|: ORDER_DECREASING | ORDER_INCREASING
      MODE_ALL_PAIRS: ignored.
      MODE_PER_NODE: order of number of pairs per node to consider.
      MODE_PER_PAIR: order of pairwise distance to consider.
  """
  assert mode in (MODE_ALL_PAIRS, MODE_PER_NODE, MODE_PER_PAIR)
  if mode is not MODE_ALL_PAIRS:
    assert order in (ORDER_DECREASING, ORDER_INCREASING)
  if mode is MODE_ALL_PAIRS:
    return _find_wiring_all(loc_pairs, start_proto_board, best_first,
        filter_wire_lengths, max_states_to_expand, verbose)
  elif mode is MODE_PER_NODE:
    return _find_wiring_per_node(loc_pairs, start_proto_board, order,
        best_first, filter_wire_lengths, max_states_to_expand, verbose)
  else: # mode is MODE_PER_PAIR
    return _find_wiring_per_pair(loc_pairs, start_proto_board, order,
        best_first, filter_wire_lengths, max_states_to_expand, verbose)

def _find_wiring_all(loc_pairs, start_proto_board, best_first,
    filter_wire_lengths, max_states_to_expand, verbose):
  """
  Wiring all pairs of locations in one search.
  """
  if verbose:
    print 'connecting %d pairs ...' % len(loc_pairs)
  search_result, num_expanded = a_star(Proto_Board_Search_Node(
      start_proto_board, frozenset(loc_pairs),
      filter_wire_lengths=filter_wire_lengths), goal_test, heuristic,
      best_first=best_first, max_states_to_expand=max_states_to_expand)
  if search_result is not None:
    if verbose:
      print '\tdone.'
    return search_result.state[0], [num_expanded]
  else:
    if verbose:
      print '\tCouldn\'t do it :('
    return None, [num_expanded]

def _find_wiring_per_node(loc_pairs, start_proto_board, order, best_first,
    filter_wire_lengths, max_states_to_expand, verbose):
  """
  Wiring the pairs of locations for each node separately.
  """
  loc_pairs_by_node = defaultdict(list)
  for loc_pair in loc_pairs:
    loc_pairs_by_node[loc_pair[3]].append(loc_pair)
  proto_board = start_proto_board
  if verbose:
    print 'interconnecting %d nodes ...' % len(loc_pairs_by_node)
  all_num_expanded = []
  f = len if order is ORDER_INCREASING else lambda l: -len(l)
  for node, loc_pair_collection in sorted(loc_pairs_by_node.items(),
      key=lambda (k, v): f(v)):
    if verbose:
      print '\tinterconnecting node \'%s\', %d pairs' % (node,
          len(loc_pair_collection))
    search_result, num_expanded = a_star(Proto_Board_Search_Node(proto_board,
        frozenset(loc_pair_collection),
        filter_wire_lengths=filter_wire_lengths), goal_test, heuristic,
        best_first=best_first, max_states_to_expand=max_states_to_expand)
    all_num_expanded.append(num_expanded)
    if search_result is not None:
      proto_board = search_result.state[0]
      if verbose:
        print proto_board
    else:
      if verbose:
        print '\tCouldn\'t do it :('
      return None, all_num_expanded
  if verbose:
    print '\tdone.'
  return proto_board, all_num_expanded

def _find_wiring_per_pair(loc_pairs, start_proto_board, order, best_first,
    filter_wire_lengths, max_states_to_expand, verbose):
  """
  Wiring each pair separately.
  """
  proto_board = start_proto_board
  if verbose:
    print 'connecting %d pairs ...' % len(loc_pairs)
  all_num_expanded = []
  sign = 1 if order is ORDER_INCREASING else -1
  for i, loc_pair in enumerate(sorted(loc_pairs,
      key=lambda (loc_1, loc_2, resistor, node): sign * dist(loc_1, loc_2))):
    loc_1, loc_2, resistor, node = loc_pair
    if verbose:
      print '\t%d/%d connecting: %s -- %s' % (i + 1, len(loc_pairs), loc_1,
          loc_2)
    search_result, num_expanded = a_star(Proto_Board_Search_Node(proto_board,
        frozenset([loc_pair]), filter_wire_lengths=filter_wire_lengths),
        goal_test, heuristic, best_first=best_first,
        max_states_to_expand=max_states_to_expand)
    all_num_expanded.append(num_expanded)
    if search_result is not None:
      proto_board = search_result.state[0]
      if verbose:
        print proto_board
    else:
      if verbose:
        print '\tCouldn\'t do it :('
      return None, all_num_expanded
  if verbose:
    print '\tdone.'
  return proto_board, all_num_expanded

def find_terrible_wiring(loc_pairs, start_proto_board):
  """
  Finds a terrible wiring without penalizing anything at all.
  To be used as a fall-back option.
  """
  proto_board = start_proto_board
  connect_loc_pairs = []
  resistor_r1 = PROTO_BOARD_HEIGHT / 2 - 1
  resistor_r2 = resistor_r1 + 1
  def find_free_c():
    c = PROTO_BOARD_WIDTH / 2
    for dc in xrange(PROTO_BOARD_WIDTH / 2):
      for sign in (-1, 1):
        _c = c + sign * dc
        locs = ((resistor_r1, _c), (resistor_r2, _c))
        if all(proto_board.rep_for(loc) is None and proto_board.free(loc) for
            loc in locs):
          return _c
    return None
  for loc_1, loc_2, resistor, node in loc_pairs:
    if resistor:
      c = find_free_c()
      if c is None:
        print 'Terrible wiring failed: no space for resistor'
        return None
      resistor_piece = Resistor_Piece(resistor.n1, resistor.n2, resistor.r,
          True, resistor.label)
      resistor_piece.top_left_loc = (resistor_r1, c)
      proto_board = proto_board.with_piece(resistor_piece)
      proto_board = proto_board.with_loc_repped(proto_board.rep_for(
          resistor.n1), (resistor_r1, c))
      proto_board = proto_board.with_loc_repped(proto_board.rep_for(
          resistor.n2), (resistor_r2, c))
      connect_loc_pairs.append((loc_1, (resistor_r1, c), resistor.n1))
      connect_loc_pairs.append((loc_2, (resistor_r2, c), resistor.n2))
    else:
      connect_loc_pairs.append((loc_1, loc_2, node))
  for loc_1, loc_2, node in connect_loc_pairs:
    candidates = list(product(filter(proto_board.free,
        proto_board.locs_connected_to(loc_1)), filter(proto_board.free,
        proto_board.locs_connected_to(loc_2))))
    if not candidates:
      print 'Terrible wiring failed: could not connect %s and %s' % (loc_1,
          loc_2)
      return None
    def cost((l1, l2)):
      wire = Wire(l1, l2, node)
      num_wires_crossed = sum(_wire.crosses(wire) for _wire in
          proto_board.get_wires())
      num_pieces_crossed = sum(piece.crossed_by(wire) for piece in
          proto_board.get_pieces())
      return 100 * (num_wires_crossed + num_pieces_crossed) + dist(l1, l2)
    l1, l2 = min(candidates, key=cost)
    proto_board = proto_board.with_wire(Wire(l1, l2, node))
  return proto_board
