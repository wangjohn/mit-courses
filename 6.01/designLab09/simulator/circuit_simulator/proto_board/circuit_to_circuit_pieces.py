"""
Tools to produce a list of circuit pieces to put on the proto board given a
    circuit (an instance of circuit_simulator.simulation.circuit.Circuit).
Terms used in this file:
  Let I be the list of items [i_0, i_1, i_2, i_3].
  A *partition* of I is a list of positive integers adding to 4, the size of I.
    Example: [2, 1, 1]
  A *grouping* is a list of subcollections of I respecting some partition.
    Example: for the partition above, one possible grouping is
        [(i_0, i_1), (i_2), (i_3)] (canonical grouping). Another possible
        grouping is [(i_0, i_2), (i_1), (i_3)]. Yet another different grouping
        is [(i_1, i_0), (i_2), (i_3)], i.e. subcollection order matters.
    In the representation used below, the subcollections are python tuples.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_piece_placement import find_placement
from circuit_pieces import Head_Connector_Piece
from circuit_pieces import Motor_Connector_Piece
from circuit_pieces import Op_Amp_Piece
from circuit_pieces import Place_Holder_Piece
from circuit_pieces import Pot_Piece
from circuit_pieces import Resistor_Piece
from circuit_pieces import Robot_Connector_Piece
from circuit_simulator.main.constants import GROUND
from circuit_simulator.main.constants import POWER
from circuit_simulator.simulation.circuit import Circuit
from circuit_simulator.simulation.circuit import Head_Connector
from circuit_simulator.simulation.circuit import Motor
from circuit_simulator.simulation.circuit import Op_Amp
from circuit_simulator.simulation.circuit import Resistor
from circuit_simulator.simulation.circuit import Signalled_Pot
from circuit_simulator.simulation.circuit import Robot_Connector
from itertools import permutations

def all_1_2_partitions(n):
  """
  Returns a list of all the sorted lists of 1s and 2s whose members add to |n|.
  For instance all_1_2_partitions(4) -> [[1, 1, 1, 1], [1, 1, 2], [2, 2]].
  """
  # base case
  if n <= 1:
    return [[1] * n]
  return [[1] * n] + [rest + [2] for rest in all_1_2_partitions(n - 2)]

def grouping(permuted_items, partition):
  """
  Returns the canonical grouping of the given |permuted_items| respecting
      the given |partition|.
  For instance, grouping([1, 2, 3, 4], [2, 2]) -> set([(1, 2), (3, 4)]).
  """
  assert len(permuted_items) == sum(partition), ('partition elements must sum '
      ' number of permuted_items')
  return set(tuple(permuted_items[sum(partition[:i]):sum(partition[:i + 1])])
      for i in range(len(partition)))

def all_groupings(items, partition):
  """
  Returns a list of all possible groupings of the given |items| respecting the
      given |partition|.
  """
  assert len(items) == sum(partition), ('partition elements must sum to number'
      ' of items')
  groupings = []
  for permuted_items in permutations(items):
    new_grouping = grouping(permuted_items, partition)
    if new_grouping not in groupings:
      groupings.append(new_grouping)
  return groupings

def resistor_piece_from_resistor(resistor):
  """
  Returns a Resistor_Piece constructed using |resistor|, an instance of
      Resistor.
  """
  assert isinstance(resistor, Resistor), 'resistor must be a Resistor'
  return Resistor_Piece(resistor.n1, resistor.n2, resistor.r, True,
      resistor.label)

def pot_piece_from_pot(pot):
  """
  Returns a Pot_Piece constructed using |pot|, an instance of Signalled_Pot.
  """
  assert isinstance(pot, Signalled_Pot), 'pot must be a Signalled_Pot'
  return Pot_Piece(pot.n_top, pot.n_middle, pot.n_bottom, pot.label)

def motor_connector_piece_from_motor(motor):
  """
  Returns a Motor_Connector_Piece constructed using |motor|, an instance of
      Motor.
  """
  assert isinstance(motor, Motor), ('motor must be a Motor')
  return Motor_Connector_Piece(motor.motor_plus, motor.motor_minus, motor.label)

def robot_connector_piece_from_robot_connector(robot_connector):
  """
  Returns a Robot_Connector_Piece constructed using |robot_connector|, an
      instance of Robot_Connector.
  """
  assert isinstance(robot_connector, Robot_Connector), ('robot_connector must '
      'be a Robot_Connector')
  return Robot_Connector_Piece([robot_connector.Vi1, robot_connector.pwr,
      robot_connector.Vi2, robot_connector.gnd, robot_connector.Vi3,
      robot_connector.Vo, robot_connector.Vi4], robot_connector.label)

def head_connector_piece_from_head_connector(head_connector):
  """
  Returns a Head_Connector_Piece constructed using |head_connector|, an
      instance of Head_Connector.
  """
  assert isinstance(head_connector, Head_Connector), ('head_connector must be '
      'a Head_Connector')
  return Head_Connector_Piece(head_connector.pin_nodes, ','.join(filter(bool, [
      head_connector.motor_label, head_connector.motor_pot_label,
      head_connector.photo_label])))

def op_amp_piece_from_op_amp(op_amp_tup):
  """
  Returns an Op_Amp_Piece constructed using |op_amp_tup|, a tuple of 1 or 2
      instances of Op_Amp. The first op_amp in op_amp_tup takes the first
      position in the Op_Amp_Piece (i.e. pins 1, 7, and 8).
  """
  assert 1 <= len(op_amp_tup) <= 2, 'op_amp_tup should have 1 or 2 items'
  assert all(isinstance(obj, Op_Amp) for obj in op_amp_tup), ('all items in '
      'op_amp_tup must be Op_Amps')
  # if only one of the two op amps is used, tie unused op amp negative input
  #     to output (pins 3 and 5), and tie positive input to ground (pin 6)
  unused_op_amp_node = str(id(op_amp_tup))
  op_amp_1 = op_amp_tup[0]
  op_amp_2 = op_amp_tup[1] if len(op_amp_tup) == 2 else None
  if op_amp_2:
    assert op_amp_1.jfet == op_amp_2.jfet
  if op_amp_1.jfet:
    n_1 = op_amp_1.nb1
    n_2 = op_amp_1.na2
    n_3 = op_amp_1.na1
    n_4 = GROUND
    n_5 = op_amp_2.na1 if op_amp_2 else GROUND
    n_6 = op_amp_2.na2 if op_amp_2 else unused_op_amp_node
    n_7 = op_amp_2.nb1 if op_amp_2 else unused_op_amp_node
    n_8 = POWER
  else:
    n_1 = op_amp_1.nb1
    n_2 = POWER
    n_3 = op_amp_2.nb1 if op_amp_2 else unused_op_amp_node
    n_4 = GROUND
    n_5 = op_amp_2.na2 if op_amp_2 else unused_op_amp_node
    n_6 = op_amp_2.na1 if op_amp_2 else GROUND
    n_7 = op_amp_1.na1
    n_8 = op_amp_1.na2
  return Op_Amp_Piece(n_1, n_2, n_3, n_4, n_5, n_6, n_7, n_8, ','.join(
      op_amp.label for op_amp in op_amp_tup), jfet=op_amp_1.jfet)

def get_piece_placement(circuit, resistors_as_components, cost_type,
    verbose=True):
  """
  Returns a *good* ordering of Circuit_Pieces for the given |circuit|. Finding
      the best one (i.e. the one the requires minimal wiring) is too expensive.
      Also returns a list of the resistors the |circuit|.
  """
  assert isinstance(circuit, Circuit), 'circuit must be a Circuit'
  if verbose:
    print 'finding piece placement ...'
  resistors = filter(lambda obj: obj.__class__ == Resistor, circuit.components)
  if resistors_as_components:
    resistor_pieces = map(resistor_piece_from_resistor, resistors)
  else:
    resistor_nodes = reduce(set.union, [set([resistor.n1, resistor.n2]) for
        resistor in resistors], set())
  pots = filter(lambda obj: obj.__class__ == Signalled_Pot, circuit.components)
  pot_pieces = map(pot_piece_from_pot, pots)
  motors = filter(lambda obj: obj.__class__ == Motor, circuit.components)
  motor_connector_pieces = map(motor_connector_piece_from_motor, motors)
  robot_connectors = filter(lambda obj: obj.__class__ == Robot_Connector,
      circuit.components)
  robot_connector_pieces = map(robot_connector_piece_from_robot_connector,
      robot_connectors)
  head_connectors = filter(lambda obj: obj.__class__ == Head_Connector,
      circuit.components)
  head_connector_pieces = map(head_connector_piece_from_head_connector,
      head_connectors)
  jfet_op_amps = filter(lambda obj: obj.__class__ == Op_Amp and obj.jfet,
      circuit.components)
  power_op_amps = filter(lambda obj: obj.__class__ == Op_Amp and not obj.jfet,
      circuit.components)
  best_placement = None
  best_placement_cost = float('inf')
  # search through all the ways of packaging up the op amps
  for jfet_partition in all_1_2_partitions(len(jfet_op_amps)):
    for jfet_grouping in all_groupings(jfet_op_amps, jfet_partition):
      for power_partition in all_1_2_partitions(len(power_op_amps)):
        for power_grouping in all_groupings(power_op_amps, power_partition):
          op_amp_pieces = map(op_amp_piece_from_op_amp, jfet_grouping |
              power_grouping)
          non_resistor_pieces = (pot_pieces + motor_connector_pieces +
              robot_connector_pieces + head_connector_pieces + op_amp_pieces)
          if resistors_as_components:
            pieces = non_resistor_pieces + resistor_pieces
          else:
            non_resistor_nodes = reduce(set.union, (piece.nodes for piece in
                non_resistor_pieces), set())
            # create place holders for nodes needed for resistors
            place_holder_pieces = [Place_Holder_Piece(node) for node in
                (resistor_nodes - non_resistor_nodes)]
            pieces = non_resistor_pieces + place_holder_pieces
          placement, cost = find_placement(pieces, resistors_as_components,
              cost_type)
          if cost < best_placement_cost:
            best_placement = placement
            best_placement_cost = cost
  if verbose:
    print '\tdone.'
  return best_placement, ([] if resistors_as_components else
      resistors)
