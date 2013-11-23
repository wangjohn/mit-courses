"""
Contains the method to analyze the circuit drawn on a board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_drawables import Ground_Drawable
from circuit_drawables import Motor_Drawable
from circuit_drawables import Motor_Pot_Drawable
from circuit_drawables import Op_Amp_Drawable
from circuit_drawables import Photosensors_Drawable
from circuit_drawables import Pot_Drawable
from circuit_drawables import Power_Drawable
from circuit_drawables import Probe_Minus_Drawable
from circuit_drawables import Probe_Plus_Drawable
from circuit_drawables import Resistor_Drawable
from circuit_drawables import Robot_IO_Drawable
from circuit_drawables import Robot_Power_Drawable
from circuit_simulator.simulation.circuit import Circuit
from circuit_simulator.simulation.circuit import Head_Connector
from circuit_simulator.simulation.circuit import Motor
from circuit_simulator.simulation.circuit import Op_Amp
from circuit_simulator.simulation.circuit import Probe
from circuit_simulator.simulation.circuit import Resistor
from circuit_simulator.simulation.circuit import Signalled_Pot
from circuit_simulator.simulation.circuit import Robot_Connector
from circuit_simulator.simulation.circuit import Voltage_Source
from collections import defaultdict
from constants import GROUND
from constants import POWER
from constants import POWER_VOLTS
from core.gui.constants import ERROR
from plotters import Head_Plotter
from plotters import Motor_Plotter
from plotters import Probe_Plotter
from plotters import Signalled_Pot_Plotter
from util import resistance_from_string

def current_name(item, n1, n2):
  """
  Returns a unique name for the current "through" the given unique |item| going
      from node |n1| to node |n2|.
  """
  return '%d %s->%s' % (id(item), n1, n2)

def run_analysis(board, analyze, solve_circuit=False,
    ensure_pwr_gnd_nodes=False, no_shorts=False, ensure_signal_files=False):
  """
  Extracts a Circuit object from what is drawn on the given |board| and calls
      the given function |analyze| on it. The funtion |analyze| should take as
      arguments the circuit, as well as the plotters that are collected.
  """
  # remove current message on board, if any
  board.remove_message()
  # components in the circuit
  circuit_components = []
  # analysis plotters
  plotters = []
  # probe labels
  probe_plus, probe_minus = None, None
  # constants for motors, motor_pots, and photosensors
  # we use this state to be able to identify robot head groups
  head_connector_group_ids = set()
  n_motor_plus = defaultdict(str)
  n_motor_minus = defaultdict(str)
  i_motor = defaultdict(str)
  motor_label = defaultdict(str)
  n_motor_pot_top = defaultdict(str)
  n_motor_pot_middle = defaultdict(str)
  n_motor_pot_bottom = defaultdict(str)
  i_motor_pot_top_middle = defaultdict(str)
  i_motor_pot_middle_bottom = defaultdict(str)
  motor_pot_label = defaultdict(str)
  n_photo_left = defaultdict(str)
  n_photo_common = defaultdict(str)
  n_photo_right = defaultdict(str)
  i_photo_left_common = defaultdict(str)
  i_photo_common_right = defaultdict(str)
  photo_lamp_angle_signal = defaultdict(str)
  photo_lamp_distance_signal = defaultdict(str)
  photo_label = defaultdict(str)
  # constants for robot power and robot analog inputs and outputs
  robot_connector_group_ids = set()
  robot_pwr = defaultdict(str)
  robot_gnd = defaultdict(str)
  robot_power_label = defaultdict(str)
  robot_ai1 = defaultdict(lambda: (None, None))
  robot_ai2 = defaultdict(lambda: (None, None))
  robot_ai3 = defaultdict(lambda: (None, None))
  robot_ai4 = defaultdict(lambda: (None, None))
  robot_ao = defaultdict(lambda: (None, None))
  # first identify all power and ground nodes and use the same name for all
  #     power nodes, as well as the same name for all ground nodes
  power_nodes, ground_nodes = set(), set()
  for drawable in board.get_drawables():
    # wires attached to this component
    nodes = [wire.label for wire in drawable.wires()]
    # power component
    if isinstance(drawable, Power_Drawable):
      for node in nodes:
        power_nodes.add(node)
    # ground component
    elif isinstance(drawable, Ground_Drawable):
      for node in nodes:
        ground_nodes.add(node)
    # robot connector component
    elif isinstance(drawable, Robot_Power_Drawable):
      for node in [wire.label for wire in drawable.pwr.wires()]:
        power_nodes.add(node)
      for node in [wire.label for wire in drawable.gnd.wires()]:
        ground_nodes.add(node)
      robot_connector_group_ids.add(drawable.group_id)
      robot_pwr[drawable.group_id] = POWER
      robot_gnd[drawable.group_id] = GROUND
      robot_power_label[drawable.group_id] = drawable.label
  # ensure that there is at least one power component
  if ensure_pwr_gnd_nodes and not power_nodes:
    board.display_message('No power nodes', ERROR)
    return
  # ensure that there is at least one ground component
  if ensure_pwr_gnd_nodes and not ground_nodes:
    board.display_message('No ground nodes', ERROR)
    return
  # ensure that power nodes and ground nodes are disjoint (no short circuit)
  if no_shorts and power_nodes.intersection(ground_nodes):
    board.display_message('Short circuit', ERROR)
    return
  # add voltage source to circuit
  circuit_components.append(Voltage_Source(POWER, GROUND, current_name(
      board, POWER, GROUND), POWER_VOLTS))
  def maybe_rename_node(node):
    """
    If this |node| is a power node or a ground node, this method returns the
        appropriate unique name, otherwise the original name is returned.
    """
    if node in power_nodes:
      return POWER
    elif node in ground_nodes:
      return GROUND
    return node
  for drawable in board.get_drawables():
    # wires attached to this component
    nodes = [wire.label for wire in drawable.wires()]
    # probe plus component
    if isinstance(drawable, Probe_Plus_Drawable):
      if nodes:
        probe_plus = maybe_rename_node(nodes[0])
        circuit_components.append(Probe('+', probe_plus))
    # probe minus component
    elif isinstance(drawable, Probe_Minus_Drawable):
      if nodes:
        probe_minus = maybe_rename_node(nodes[0])
        circuit_components.append(Probe('-', probe_minus))
    # resistor component
    elif isinstance(drawable, Resistor_Drawable):
      connector_it = iter(drawable.connectors)
      pin_1_nodes = [wire.label for wire in connector_it.next().wires()]
      pin_2_nodes = [wire.label for wire in connector_it.next().wires()]
      # get its resistance
      try:
        c1, c2, e = resistance_from_string(drawable.get_resistance())
        r = (c1 * 10 + c2) * 10 ** e
      except:
        board.display_message('Could not obtain resistance constant', ERROR)
        return
      n1 = maybe_rename_node(pin_1_nodes[0]) if pin_1_nodes else None
      n2 = maybe_rename_node(pin_2_nodes[0]) if pin_2_nodes else None
      resistor = Resistor(n1, n2, current_name(drawable, n1, n2), r)
      resistor.label = drawable.label
      circuit_components.append(resistor)
    # op amp component
    elif isinstance(drawable, Op_Amp_Drawable):
      plus_nodes = [wire.label for wire in drawable.plus_port.wires()]
      minus_nodes = [wire.label for wire in drawable.minus_port.wires()]
      out_nodes = [wire.label for wire in drawable.out_port.wires()]
      na1 = maybe_rename_node(plus_nodes[0]) if plus_nodes else None
      na2 = maybe_rename_node(minus_nodes[0]) if minus_nodes else None
      nb1 = maybe_rename_node(out_nodes[0]) if out_nodes else None
      nb2 = GROUND
      op_amp = Op_Amp(na1, na2, current_name(drawable, na1, na2), nb1, nb2,
          current_name(drawable, nb1, nb2), jfet=drawable.jfet)
      op_amp.label = drawable.label
      circuit_components.append(op_amp)
    # pot component
    elif isinstance(drawable, Pot_Drawable):
      if ensure_signal_files and not drawable.signal_file:
        board.display_message('No signal file loaded for Pot', ERROR)
        return
      pot_variables = {'pot_r': None, 'pot_signal': None}
      if drawable.signal_file:
        execfile(drawable.signal_file, pot_variables)
        if ensure_signal_files and not (pot_variables['pot_r'] and
            pot_variables['pot_signal']):
          board.display_message('Invalid Pot signal file', ERROR)
          return
      top_nodes = [wire.label for wire in drawable.top_connector.wires()]
      middle_nodes = [wire.label for wire in drawable.middle_connector.wires()]
      bottom_nodes = [wire.label for wire in drawable.bottom_connector.wires()]
      n_top = maybe_rename_node(top_nodes[0]) if top_nodes else None
      n_middle = maybe_rename_node(middle_nodes[0]) if middle_nodes else None
      n_bottom = maybe_rename_node(bottom_nodes[0]) if bottom_nodes else None
      pot = Signalled_Pot(n_top, n_middle, n_bottom, current_name(drawable,
          n_top, n_middle), current_name(drawable, n_middle, n_bottom),
          pot_variables['pot_r'], pot_variables['pot_signal'])
      pot.label = drawable.label
      circuit_components.append(pot)
      plotters.append(Signalled_Pot_Plotter(pot))
    # motor component
    elif isinstance(drawable, Motor_Drawable):
      plus_nodes = [wire.label for wire in drawable.plus.wires()]
      minus_nodes = [wire.label for wire in drawable.minus.wires()]
      plus_node = maybe_rename_node(plus_nodes[0]) if plus_nodes else None
      minus_node = maybe_rename_node(minus_nodes[0]) if minus_nodes else None
      i = current_name(drawable, n_motor_plus, n_motor_minus)
      if not drawable.group_id:
        motor = Motor(plus_node, minus_node, i)
        motor.label = drawable.label
        circuit_components.append(motor)
        plotters.append(Motor_Plotter(motor))
      else:
        head_connector_group_ids.add(drawable.group_id)
        n_motor_plus[drawable.group_id] = plus_node
        n_motor_minus[drawable.group_id] = minus_node
        i_motor[drawable.group_id] = i
        motor_label[drawable.group_id] = drawable.label
    # motor pot component
    elif isinstance(drawable, Motor_Pot_Drawable):
      pot_top_nodes = [wire.label for wire in drawable.top.wires()]
      pot_middle_nodes = [wire.label for wire in drawable.middle.wires()]
      pot_bottom_nodes = [wire.label for wire in drawable.bottom.wires()]
      head_connector_group_ids.add(drawable.group_id)
      n_motor_pot_top[drawable.group_id] = (maybe_rename_node(pot_top_nodes[0])
          if pot_top_nodes else None)
      n_motor_pot_middle[drawable.group_id] = maybe_rename_node(
          pot_middle_nodes[0]) if pot_middle_nodes else None
      n_motor_pot_bottom[drawable.group_id] = maybe_rename_node(
          pot_bottom_nodes[0]) if pot_bottom_nodes else None
      i_motor_pot_top_middle[drawable.group_id] = current_name(drawable,
          n_motor_pot_top, n_motor_pot_middle)
      i_motor_pot_middle_bottom[drawable.group_id] = current_name(drawable,
          n_motor_pot_middle, n_motor_pot_bottom)
      motor_pot_label[drawable.group_id] = drawable.label
    # photosensor component
    elif isinstance(drawable, Photosensors_Drawable):
      if ensure_signal_files and not drawable.signal_file:
        board.display_message('No signal file loaded for Photosensors', ERROR)
        return
      lamp_signals = {'lamp_angle_signal': None, 'lamp_distance_signal': None}
      if drawable.signal_file:
        execfile(drawable.signal_file, lamp_signals)
      photo_lamp_angle_signal[drawable.group_id] = lamp_signals[
          'lamp_angle_signal']
      photo_lamp_distance_signal[drawable.group_id] = lamp_signals[
          'lamp_distance_signal']
      photo_left_nodes = [wire.label for wire in drawable.left.wires()]
      photo_common_nodes = [wire.label for wire in drawable.common.wires()]
      photo_right_nodes = [wire.label for wire in drawable.right.wires()]
      head_connector_group_ids.add(drawable.group_id)
      n_photo_left[drawable.group_id] = (maybe_rename_node(photo_left_nodes[0])
          if photo_left_nodes else None)
      n_photo_common[drawable.group_id] = maybe_rename_node(
          photo_common_nodes[0]) if photo_common_nodes else None
      n_photo_right[drawable.group_id] = maybe_rename_node(
          photo_right_nodes[0]) if photo_right_nodes else None
      i_photo_left_common[drawable.group_id] = current_name(drawable,
          n_photo_left, n_photo_common)
      i_photo_common_right[drawable.group_id] = current_name(drawable,
          n_photo_common, n_photo_right)
      photo_label[drawable.group_id] = drawable.label
    # motor analog i/o component
    elif isinstance(drawable, Robot_IO_Drawable):
      node = maybe_rename_node(nodes[0]) if nodes else None
      robot_connector_group_ids.add(drawable.group_id)
      if drawable.name == 'Ai1':
        robot_ai1[drawable.group_id] = (node, drawable.label)
      elif drawable.name == 'Ai2':
        robot_ai2[drawable.group_id] = (node, drawable.label)
      elif drawable.name == 'Ai3':
        robot_ai3[drawable.group_id] = (node, drawable.label)
      elif drawable.name == 'Ai4':
        robot_ai4[drawable.group_id] = (node, drawable.label)
      elif drawable.name == 'Ao':
        robot_ao[drawable.group_id] = (node, drawable.label)
  # collect robot head pieces together
  for group_id in head_connector_group_ids:
    head_connector = Head_Connector(n_motor_pot_top[group_id],
        n_motor_pot_middle[group_id], n_motor_pot_bottom[group_id],
        i_motor_pot_top_middle[group_id], i_motor_pot_middle_bottom[group_id],
        n_photo_left[group_id], n_photo_common[group_id], n_photo_right[
        group_id], i_photo_left_common[group_id], i_photo_common_right[
        group_id], n_motor_plus[group_id], n_motor_minus[group_id], i_motor[
        group_id], photo_lamp_angle_signal[group_id],
        photo_lamp_distance_signal[group_id])
    head_connector.motor_label = motor_label[group_id]
    head_connector.motor_pot_label = motor_pot_label[group_id]
    head_connector.photo_label = photo_label[group_id]
    circuit_components.append(head_connector)
    plotters.append(Head_Plotter(head_connector))
  # collect robot connector pieces together
  for group_id in robot_connector_group_ids:
    ai1_node, ai1_label = robot_ai1[group_id]
    ai2_node, ai2_label = robot_ai2[group_id]
    ai3_node, ai3_label = robot_ai3[group_id]
    ai4_node, ai4_label = robot_ai4[group_id]
    ao_node, ao_label = robot_ao[group_id]
    robot_connector = Robot_Connector(robot_pwr[group_id], robot_gnd[group_id],
        ai1_node, ai2_node, ai3_node, ai4_node, ao_node)
    robot_connector.label = ','.join(filter(bool, [robot_power_label[group_id],
        ai1_label, ai2_label, ai3_label, ai4_label, ao_label]))
    circuit_components.append(robot_connector)
  # if both probes are given, display probe voltage difference graph
  if probe_plus and probe_minus:
    plotters.append(Probe_Plotter(probe_plus, probe_minus))
  # create and analyze circuit
  circuit = Circuit(circuit_components, GROUND, solve_circuit)
  board.relabel_wires(maybe_rename_node)
  return analyze(circuit, plotters)
