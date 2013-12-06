"""
Runs circuit simulator.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from analyze_board import run_analysis
from circuit_drawables import Ground_Drawable
from circuit_drawables import Head_Connector_Drawable
from circuit_drawables import Motor_Drawable
from circuit_drawables import Motor_Pot_Drawable
from circuit_drawables import Op_Amp_Drawable
from circuit_drawables import Photosensors_Drawable
from circuit_drawables import Pot_Drawable
from circuit_drawables import Power_Drawable
from circuit_drawables import Probe_Minus_Drawable
from circuit_drawables import Probe_Plus_Drawable
from circuit_drawables import Proto_Board_Run_Drawable
from circuit_drawables import Resistor_Drawable
from circuit_drawables import Robot_Connector_Drawable
from circuit_drawables import Robot_IO_Drawable
from circuit_drawables import Robot_Power_Drawable
from circuit_drawables import Simulate_Run_Drawable
from circuit_simulator.proto_board.solve import combined_solve_layout
from circuit_simulator.proto_board.visualization.visualization import (
    visualize_proto_board)
from circuit_simulator.simulation.circuit import Robot_Connector
from circuit_simulator.simulation.simulate import close_all_windows
from constants import APP_NAME
from constants import BOARD_HEIGHT
from constants import BOARD_WIDTH
from constants import DEV_STAGE
from constants import FILE_EXTENSION
from constants import OP_AMP_NP
from constants import OP_AMP_PN
from constants import PALETTE_HEIGHT
from constants import PROBE_INIT_PADDING
from constants import PROBE_SIZE
from core.gui.app_runner import App_Runner
from core.gui.board import Board
from core.gui.components import Wire
from core.gui.components import Wire_Connector_Drawable
from core.gui.constants import CTRL_DOWN
from core.gui.constants import LEFT
from core.gui.constants import RIGHT
from core.gui.constants import ERROR
from sys import argv
from Tkinter import Toplevel

def on_init(board):
  """
  Method called when a new circuit simulator |board| is created.
  """
  assert isinstance(board, Board), 'board must be a Board'
  # create probe drawables and connect minus probe to ground
  minus_probe = Probe_Minus_Drawable()
  board.add_drawable(minus_probe, (PROBE_INIT_PADDING, PROBE_INIT_PADDING))
  if False:
    ground = Ground_Drawable().rotated().rotated()
    board.add_drawable(ground, (PROBE_SIZE + 2 * PROBE_INIT_PADDING,
        PROBE_INIT_PADDING))
    x1, y1 = iter(minus_probe.connectors).next().center
    x2, y2 = iter(ground.connectors).next().center
    board.add_wire(x1, y1, x2, y2)
  board.add_drawable(Probe_Plus_Drawable(), (
      PROBE_INIT_PADDING, PROBE_SIZE + 2 * PROBE_INIT_PADDING))

if __name__ == '__main__':
  app_runner = App_Runner(on_init, APP_NAME, DEV_STAGE, FILE_EXTENSION, (
      Power_Drawable, Ground_Drawable, Probe_Plus_Drawable,
      Probe_Minus_Drawable, Resistor_Drawable, Op_Amp_Drawable, Pot_Drawable,
      Motor_Drawable, Motor_Pot_Drawable, Photosensors_Drawable,
      Robot_Power_Drawable, Robot_IO_Drawable, Wire_Connector_Drawable, Wire),
      BOARD_WIDTH, BOARD_HEIGHT, PALETTE_HEIGHT, False, True, True, argv[1] if
      len(argv) > 1 else None)
  # track all proto board visualizations
  app_runner.visuals = []
  def simulate(circuit, plotters):
    """
    Displays the plot that are drawn by the |plotters|.
    """
    # show label tooltips on board
    app_runner.board.show_label_tooltips()
  def proto_board_layout(circuit, plotters):
    """
    Finds a way to layout the given |circuit| on a proto board and displays the
        discovered proto board.
    """
    app_runner.board.set_busy_cursor()
    proto_board = combined_solve_layout(circuit)
    if proto_board:
      # show labels on board for easy schematic-layout matching
      app_runner.board.show_label_tooltips()
      # visualize proto board
      show_pwr_gnd_pins = not any([isinstance(component, Robot_Connector) for
          component in circuit.components])
      visual = visualize_proto_board(proto_board, Toplevel(), show_pwr_gnd_pins)
      app_runner.board.set_drawable_highlight(visual.outline_piece_from_label)
      app_runner.board.set_wire_highlight(visual.outline_wires_from_label)
      visual.set_piece_highlight(app_runner.board.outline_drawables_from_labels)
      visual.set_wire_highlight(app_runner.board.outline_wires_from_label)
      for v in app_runner.visuals:
        # disable previous proto board visuals from affecting the board
        v.set_piece_highlight(lambda labels: None)
        v.set_wire_highlight(lambda label: None)
      app_runner.visuals.append(visual)
    else:
      app_runner.board.display_message('Could not find proto board wiring',
          ERROR, False)
    app_runner.board.set_regular_cursor()
  # add circuit components to palette
  app_runner.palette.add_drawable_type(Power_Drawable, LEFT, None)
  app_runner.palette.add_drawable_type(Ground_Drawable, LEFT, None)
  app_runner.palette.add_drawable_type(Resistor_Drawable, LEFT, None,
      board=app_runner.board)
  app_runner.palette.add_drawable_type(Pot_Drawable, LEFT, None,
      on_signal_file_changed=lambda: app_runner.board.set_changed(True))
  app_runner.palette.add_drawable_type(Op_Amp_Drawable, LEFT, None,
      board=app_runner.board, signs=OP_AMP_PN, jfet=False)
  app_runner.palette.add_drawable_type(Op_Amp_Drawable, LEFT, None,
      board=app_runner.board, signs=OP_AMP_NP, jfet=False)
  app_runner.palette.add_drawable_type(Robot_Connector_Drawable, LEFT, None,
      types_to_add=[(Robot_Power_Drawable, {})] + [(Robot_IO_Drawable,
      {'name': 'Ai%d' % i}) for i in (1, 2, 3, 4)] + [(Robot_IO_Drawable,
      {'name': 'Ao'})])
  app_runner.palette.add_drawable_type(Head_Connector_Drawable, LEFT, None,
      types_to_add=[(Motor_Drawable, {}), (Motor_Pot_Drawable, {}), (
      Photosensors_Drawable, {'on_signal_file_changed':
      lambda: app_runner.board.set_changed(True)})])
  app_runner.palette.add_drawable_type(Motor_Drawable, LEFT, None)
  # add buttons to analyze circuit
  app_runner.palette.add_drawable_type(Proto_Board_Run_Drawable, RIGHT,
      lambda event: run_analysis(app_runner.board, proto_board_layout,
      no_shorts=True))
  #app_runner.palette.add_drawable_type(Simulate_Run_Drawable, RIGHT,
  #    lambda event: run_analysis(app_runner.board, simulate,
  #    solve_circuit=True, no_shorts=True))
  # shortcuts
  app_runner.board.add_key_binding('s', lambda: run_analysis(app_runner.board,
      simulate, solve_circuit=True, no_shorts=True))
  app_runner.board.add_key_binding('g', lambda: run_analysis(app_runner.board,
      proto_board_layout, no_shorts=True))
  app_runner.board.add_key_binding('w', close_all_windows, CTRL_DOWN)
  # run
  app_runner.run()
