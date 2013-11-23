"""
Proto board visualization constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.proto_board.constants import (
    NUM_ROWS_PER_VERTICAL_SEPARATION)
from circuit_simulator.proto_board.constants import PROTO_BOARD_HEIGHT
from circuit_simulator.proto_board.constants import PROTO_BOARD_WIDTH

# color
BACKGROUND_COLOR = 'white'
BROWN = '#AB6533'
CONNECTOR_COLOR = 'grey'
VIOLET = '#FF00FF'
WIRE_COLORS = ['black', BROWN, 'red', 'orange', 'yellow', 'green', 'blue',
    VIOLET, 'grey', 'white']
WIRE_OUTLINE = 'black'

# size
CONNECTOR_SIZE = 4
CONNECTOR_SPACING = 8
VERTICAL_SEPARATION = NUM_ROWS_PER_VERTICAL_SEPARATION * CONNECTOR_SIZE + (
    (NUM_ROWS_PER_VERTICAL_SEPARATION + 1) * CONNECTOR_SPACING)
PADDING = 30
HEIGHT = (PROTO_BOARD_HEIGHT * CONNECTOR_SIZE + (PROTO_BOARD_HEIGHT - 4) *
    CONNECTOR_SPACING + 3 * VERTICAL_SEPARATION + 2 * PADDING)
WIDTH = (PROTO_BOARD_WIDTH * CONNECTOR_SIZE + (PROTO_BOARD_WIDTH - 1) *
    CONNECTOR_SPACING + 2 * PADDING)

# text
CMAX_FILE_EXTENSION = '.cmax'
WINDOW_TITLE = 'Proto board'
