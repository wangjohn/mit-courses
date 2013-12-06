"""
Representation for a proto board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import BODY_BOTTOM_ROWS
from constants import BODY_TOP_ROWS
from constants import PROTO_BOARD_WIDTH
from constants import PROTO_BOARD_HEIGHT
from constants import RAIL_ILLEGAL_COLUMNS
from constants import RAIL_ROWS
from core.data_structures.disjoint_set_forest import Disjoint_Set_Forest
from string import ascii_lowercase
from string import ascii_uppercase
from string import digits
from util import body_section_rows
from util import section_locs
from wire import Wire

class Proto_Board:
  """
  Proto board representation.
  """
  def __init__(self, wire_mappings=None, wires=None, pieces=None,
      loc_disjoint_set_forest=None):
    """
    |wire_mappings|: a dictionary mapping locations to other locations to which
        they are connected by a wire.
    |wires|: a list of the Wires on this proto board.
    |pieces|: a set of the Circuit_Pieces on this proto board.
    |loc_disjoint_set_forest|: an instance of Disjoint_Set_Forest representing
        disjoint sets of locations on the proto board that should alwas remain
        disconnected. This is used to avoid shorts.
    """
    self._wire_mappings = wire_mappings if wire_mappings is not None else {}
    self._wires = wires if wires is not None else []
    self._pieces = pieces if pieces is not None else set()
    self._loc_disjoint_set_forest = (loc_disjoint_set_forest if
        loc_disjoint_set_forest is not None else Disjoint_Set_Forest())
  def get_wires(self):
    """
    Returns a generator for the Wires on this proto board.
    """
    for wire in self._wires:
      yield wire
  def num_wires(self):
    """
    Returns the number of wires on this proto board.
    """
    return len(self._wires)
  def num_wire_crosses(self):
    """
    Returns the number of wire crosses on this proto board.
    """
    return sum(reduce(list.__add__, [[wire.crosses(other_wire) for other_wire in
        self._wires[i + 1:]] for i, wire in enumerate(self._wires)], []))
  def get_pieces(self):
    """
    Returns a generator for the Circuit_Pieces on this proto board.
    """
    for piece in self._pieces:
      yield piece
  def _connected(self, loc_1, loc_2, visited):
    """
    Helper for self.connected, see below.
    """
    if loc_1 in visited:
      return False
    group = set(section_locs(loc_1))
    new_visited = visited | group
    return loc_2 in group or any(map(lambda new_loc_1: self._connected(
        new_loc_1, loc_2, new_visited), (self._wire_mappings[loc] for loc in
        group if loc in self._wire_mappings)))
  def connected(self, loc_1, loc_2):
    """
    Returns True if |loc_1| and |loc_2| are connected by wires, False
        otherwise.
    """
    return self._connected(loc_1, loc_2, set())
  def locs_connected_to(self, loc):
    """
    Returns a set of the locations on this proto board that are connected (
        internally or by wires) to |loc|.
    """
    connected_locs = set()
    queue = set(section_locs(loc))
    while queue:
      connected_loc = queue.pop()
      connected_locs.add(connected_loc)
      if connected_loc in self._wire_mappings:
        for wire_neighbor in section_locs(self._wire_mappings[connected_loc]):
          if wire_neighbor not in connected_locs:
            queue.add(wire_neighbor)
    return connected_locs
  def rep_for(self, item):
    """
    Returns the representative for the group to which |item|, a location or
        node name, belongs.
    """
    return self._loc_disjoint_set_forest.find_set(item)
  def node_for(self, loc):
    """
    Returns the node associated with the location |loc|, or None if the location
        is not linked to a node.
    """
    # check if the loc is on some path of wires
    connected_locs = self.locs_connected_to(loc)
    for wire in self._wires:
      if wire.loc_1 in connected_locs or wire.loc_2 in connected_locs:
        return wire.node
    # check if the loc is internally connected to one of the circuit pieces
    for piece in self._pieces:
      piece_loc_node = piece.node_for(loc)
      if piece_loc_node:
        return piece_loc_node
    return None
  def with_loc_disjoint_set_forest(self, loc_disjoint_set_forest):
    """
    Returns a copy of this board with a new forest of disjoint location sets to
        keep disconnected. If this board violates the given forest, this method
        raises and Exception.
    """
    board = Proto_Board(loc_disjoint_set_forest=loc_disjoint_set_forest)
    for piece in self._pieces:
      board = board.with_piece(piece)
    for wire in self._wires:
      board = board.with_wire(wire)
      if board is None:
        raise Exception('board violates given forest')
    return board
  def with_loc_repped(self, rep, loc):
    """
    Returns a new Proto_Board with the given |loc| and the locations internally
        connected to it being members of the group of locations represented by
        |rep|.
    """
    assert self.rep_for(rep)
    assert not self.rep_for(loc)
    new_loc_disjoint_set_forest = self._loc_disjoint_set_forest.copy()
    for section_loc in section_locs(loc):
      new_loc_disjoint_set_forest.make_set(section_loc)
      new_loc_disjoint_set_forest.union(rep, section_loc)
    return self.with_loc_disjoint_set_forest(new_loc_disjoint_set_forest)
  def with_wire(self, new_wire):
    """
    Returns a new Proto_Board containing the |new_wire|. If the wire connects
        nodes that are already connected, this method returns this proto board.
        If the wire connects nodes that are meant not to be connected, as per
        |self._loc_disjoint_set_forest|, this method returns None. If the wire's
        locations don't match the wire's node, this method returns None.
    """
    # if locations are already connected, no need for the wire
    if self.connected(new_wire.loc_1, new_wire.loc_2):
      return self
    # if the wire results in a short, no new proto board
    new_wire_node_rep = self.rep_for(new_wire.node)
    group_1 = self.rep_for(new_wire.loc_1)
    if group_1 and group_1 is not new_wire_node_rep:
      return None
    group_2 = self.rep_for(new_wire.loc_2)
    if group_2 and group_2 is not new_wire_node_rep:
      return None
    if group_1 and group_2 and group_1 != group_2:
      return None
    new_wire_mappings = self._wire_mappings.copy()
    new_wire_mappings[new_wire.loc_1] = new_wire.loc_2
    new_wire_mappings[new_wire.loc_2] = new_wire.loc_1
    new_loc_disjoint_set_forest = self._loc_disjoint_set_forest.copy()
    # update to avoid shorts that may result via the new wire
    if bool(group_1) != bool(group_2):
      present_loc = new_wire.loc_1 if group_1 else new_wire.loc_2
      absent_loc = new_wire.loc_1 if present_loc == new_wire.loc_2 else (
          new_wire.loc_2)
      for loc in section_locs(absent_loc):
        new_loc_disjoint_set_forest.make_set(loc)
        new_loc_disjoint_set_forest.union(present_loc, loc)
    return Proto_Board(new_wire_mappings, self._wires + [new_wire],
        self._pieces, new_loc_disjoint_set_forest)
  def with_piece(self, piece):
    """
    Returns a new Proto_Board containing the given |piece|. If the piece
        collides with another object on the board, this method raises an
        Exception.
    """
    # check for intersections with current objects on the board
    if any(piece.crossed_by(wire) for wire in self._wires) or any(
        piece.overlaps_with(other_piece) for other_piece in self._pieces):
      raise Exception('new piece overlaps with existing piece')
    # add new piece to pieces
    new_pieces = self._pieces.copy()
    new_pieces.add(piece)
    # account for piece sacred locations, i.e. make sure these locations never
    #     get connected to another node in the circuit
    new_loc_disjoint_set_forest = self._loc_disjoint_set_forest.copy()
    for loc in piece.get_sacred_locs():
      new_loc_disjoint_set_forest.make_set(loc)
      for section_loc in section_locs(loc):
        new_loc_disjoint_set_forest.make_set(section_loc)
        new_loc_disjoint_set_forest.union(loc, section_loc)
    return Proto_Board(self._wire_mappings, self._wires, new_pieces,
        new_loc_disjoint_set_forest)
  def occupied(self, loc):
    """
    Returns True if the given |loc| is occupied, False otherwise.
    """
    return loc in self._wire_mappings or any(loc in piece.all_locs() for piece
        in self._pieces)
  def free(self, loc):
    """
    Returns True if the given |loc| is not occupied, False otherwise.
    """
    return not self.occupied(loc)
  def to_ascii(self, distinguish_wires=False):
    """
    Quick, convenience str method, not at all comprehensive.
    """
    # represent proto board as a grid
    grid = [[' '] * (PROTO_BOARD_WIDTH + 1) for row in xrange(
        PROTO_BOARD_HEIGHT + 2)]
    # write out row and column numbers
    for r in xrange(PROTO_BOARD_HEIGHT):
      grid[r + 1][0] = str(r % 10)
    for c in xrange(PROTO_BOARD_WIDTH):
      if c not in RAIL_ILLEGAL_COLUMNS:
        grid[0][c + 1] = grid[PROTO_BOARD_HEIGHT + 1][c + 1] = str(c % 10)
    # write out a box of !s for each piece
    for piece in self._pieces:
      for (r, c) in piece.all_locs():
        grid[r + 1][c + 1] = '!'
    # write out a string of identical letters for each wire
    if distinguish_wires:
      chars = ascii_lowercase + ascii_uppercase + digits
    for i, wire in enumerate(sorted(self._wires,
        key=lambda wire: -wire.length())):
      for (r, c) in wire.locs():
        grid[r + 1][c + 1] = (chars[i % len(chars)] if distinguish_wires else
            '#')
    return '\n'.join([''.join(row) for row in grid])
  def __str__(self):
    return self.to_ascii(True)
  def __eq__(self, other):
    return (isinstance(other, Proto_Board) and frozenset(self._wires) ==
        frozenset(other._wires) and frozenset(self._pieces) == frozenset(
        other._pieces) and self._loc_disjoint_set_forest ==
        other._loc_disjoint_set_forest)
  def __hash__(self):
    return hash((frozenset(self._wires), frozenset(self._pieces),
        self._loc_disjoint_set_forest))
  def prettified(self):
    """
    Makes the protoboard slightly more appealing by collapsing long vertical
        wires (when possible) and shifting horizontal wires up or down to avoid
        corssing wires (when possible).
    I apologize for really ugly code :(
    This is targetted for the regular protoboard structure, and not any others.
        I.e. changing the constants will result in this code not being as
        useful.
    """
    new = Proto_Board().with_loc_disjoint_set_forest(
        self._loc_disjoint_set_forest)
    for piece in self._pieces:
      new = new.with_piece(piece)
    for i, wire in enumerate(self._wires):
      if wire.vertical():
        r1, c1 = wire.loc_1
        r2, c2 = wire.loc_2
        assert c1 == c2
        if r1 > r2:
          r1, r2 = r2, r1
          c1, c2 = c2, c1
        if r2 - r1 == 1:
          new = new.with_wire(wire)
          continue
        def safe(r):
          return r == r1 or r == r2 or (self.free((r, c1)) and self.rep_for(
              (r, c1)) is None)
        if r1 in RAIL_ROWS and r2 in BODY_BOTTOM_ROWS and all(safe(r) for r in
            [2, 6, 7]):
          pairs = ((r1, 2), (6, 7))
        elif r1 in RAIL_ROWS and r2 in RAIL_ROWS and all(safe(r) for r in
            [2, 6, 7, 11]):
          pairs = ((r1, 2), (6, 7), (11, r2))
        elif r1 in BODY_TOP_ROWS and r2 in RAIL_ROWS and all(safe(r) for r in
            [6, 7, 11]):
          pairs = ((6, 7), (11, r2))
        else:
          pairs = ((r1, r2),)
        for _r, r_ in pairs:
          w = Wire((_r, c1), (r_, c1), wire.node)
          new = new.with_wire(w)
      elif wire.horizontal():
        r1, c1 = wire.loc_1
        r2, c2 = wire.loc_2
        assert r1 == r2
        r = r1
        # try to get horizontal wires closer to the center
        rows = [2, 3, 4, 5, 6] if r1 <= 6 else [11, 10, 9, 8, 7]
        for _r in rows:
          test_wire = Wire((_r, c1), (_r, c2), wire.node)
          if (not any(test_wire.crosses(w) for w in self._wires[i + 1:]) and not
              any(test_wire.crosses(w) for w in new._wires) and not any(
              piece.crossed_by(test_wire) for piece in new._pieces)):
            r = _r
        new = new.with_wire(Wire((r, c1), (r, c2), wire.node))
      else:
        new = new.with_wire(wire)
    return new
