"""
GUI constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from platform import system

# colors
BOARD_BACKGROUND_COLOR = 'white'
BOARD_MARKER_LINE_COLOR = '#DDD'
CONNECTOR_DISABLED_COLOR = '#AAA'
CONNECTOR_DISABLED_OUTLINE = '#777'
CONNECTOR_EMPTY_COLOR = 'white'
CONNECTOR_EMPTY_OUTLINE = 'black'
CONNECTOR_FULL_COLOR = '#111'
CONNECTOR_FULL_OUTLINE = '#BBB'
DRAG_SAFE_COLOR = '#00AB6F'
DRAG_UNSAFE_COLOR = 'red'
MESSAGE_ERROR_COLOR = '#FD7279'
MESSAGE_INFO_COLOR = '#95EE6B'
MESSAGE_WARNING_COLOR = '#FFD640'
PALETTE_BACKGROUND_COLOR = '#BBB'
PALETTE_SEPARATION_LINE_COLOR = '#777'
RUN_RECT_FILL = 'white'
RUN_RECT_OUTLINE = 'black'
RUN_TEXT_ACTIVE_FILL = '#000'
RUN_TEXT_FILL = '#333'
SELECTION_OUTLINE_COLOR = '#00AB6F'
TOOLTIP_BACKGROUND = '#FFFFE0'
TOOLTIP_DRAWABLE_LABEL_BACKGROUND = '#73FFFF'
WIRE_COLOR = '#777'
WIRE_CONNECTOR_FILL = 'grey'
WIRE_CONNECTOR_OUTLINE = 'black'

# connector flags
CONNECTOR_BOTTOM = 2 ** 0
CONNECTOR_CENTER = 2 ** 1
CONNECTOR_LEFT =   2 ** 2
CONNECTOR_RIGHT =  2 ** 3
CONNECTOR_TOP =    2 ** 4
CONNECTOR_BLRT = (CONNECTOR_BOTTOM | CONNECTOR_LEFT | CONNECTOR_RIGHT |
    CONNECTOR_TOP)

# message types
ERROR = 0
INFO = 1
WARNING = 2

# sides of the palette on which items are added
LEFT = 0
RIGHT = 1

# size constants
BOARD_WIDTH = 600
BOARD_HEIGHT = 400
BOARD_GRID_SEPARATION = 10
CONNECTOR_RADIUS = 2
CONNECTOR_WIDTH = 1
MESSAGE_WIDTH = 300
MESSAGE_HEIGHT = 40
MESSAGE_PADDING = 10
MESSAGE_TEXT_WIDTH = 260
PALETTE_WIDTH = 600
PALETTE_HEIGHT = 60
PALETTE_PADDING = 10
RUN_RECT_SIZE = 40
WIRE_ARROW_LENGTH = 10
WIRE_INTERSECT_MARKER_SIZE = 4
WIRE_WIDTH = 2

# duration constants
MESSAGE_ERROR_DURATION = 5 # seconds
MESSAGE_INFO_DURATION = 3 # seconds
MESSAGE_WARNING_DURATION = 4 # seconds

# key-press flags
CTRL_DOWN =  2 ** 0
SHIFT_DOWN = 2 ** 1

# cursors
CTRL_CURSOR = 'pirate'
SHIFT_CURSOR = 'exchange'

# tags
EDIT_TAG = 'edit_tag'
ROTATE_TAG = 'rotate_tag'

# fonts
DEFAULT_FONT = ('Helvetica', 12 if system() == 'Darwin' else 10)

# keycodes for badly mapped keys on apple keyboards
# see https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/backends/backend_tkagg.py
KEYCODE_LOOKUP = {262145: 'Control_L', 524320: 'Alt_L', 524352: 'Alt_R',
    1048584: 'Super_L', 1048592: 'Super_R', 131074: 'Shift_L',
    131076: 'Shift_R'}

# wire path search costs
CROSS_COST = 100
BEND_COST = 2

# images
HAND_IMAGE = 'core/gui/images/hand.gif'
PENCIL_IMAGE = 'core/gui/images/pencil.gif'

# debug options
DEBUG_DISPLAY_WIRE_LABELS = False
DEBUG_CONNECTOR_CENTER_TOOLTIP = False
