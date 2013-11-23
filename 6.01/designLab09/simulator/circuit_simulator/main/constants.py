"""
Main constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.simulation.constants import NUM_SAMPLES
from circuit_simulator.simulation.constants import T
from platform import system

# colors
HEAD_COLOR = '#666'
LAMP_BOX_COLOR = 'white'
LAMP_COLOR = 'yellow'
LAMP_EMPTY_COLOR = '#DDD'
MOTOR_FILL = '#666'
NEGATIVE_COLOR = '#1531AE'
OP_AMP_FILL = '#EEE'
OP_AMP_OUTLINE = 'black'
OP_AMP_PWR_GND_FILL = '#444'
PIN_OUTLINE = 'black'
PIN_TEXT_COLOR = 'white'
POSITIVE_COLOR = '#EF002A'
POT_ALPHA_EMPTY_FILL = '#EEE'
POT_ALPHA_FILL = '#3AAACF'
POT_ALPHA_OUTLINE = '#888'
RESISTOR_FILL = ''
RESISTOR_OUTLINE = ''
ROBOT_COLOR = '#666'

# circuit drawable component constants
DIRECTION_UP    = 0
DIRECTION_RIGHT = 1
DIRECTION_DOWN  = 2
DIRECTION_LEFT  = 3
HEAD_SIZE = 40
LABEL_PADDING = 8
LAMP_BOX_PADDING = 3
LAMP_BOX_SIZE = 12
LAMP_RADIUS = 4
MOTOR_SIZE = 60
MOTOR_POT_SIZE = 60
OP_AMP_BASE = 60
OP_AMP_HEIGHT = 60
OP_AMP_DOWN_VERTICES = (0, 0, OP_AMP_BASE / 2, OP_AMP_HEIGHT, OP_AMP_BASE, 0)
OP_AMP_LEFT_VERTICES = (0, OP_AMP_BASE / 2, OP_AMP_HEIGHT, OP_AMP_BASE,
    OP_AMP_HEIGHT, 0)
OP_AMP_RIGHT_VERTICES = (0, 0, 0, OP_AMP_BASE, OP_AMP_HEIGHT, OP_AMP_BASE / 2)
OP_AMP_UP_VERTICES = (OP_AMP_BASE / 2, 0, 0, OP_AMP_HEIGHT, OP_AMP_BASE,
    OP_AMP_HEIGHT)
OP_AMP_CONNECTOR_PADDING = 20
OP_AMP_NP = 0
OP_AMP_PN = 1
PHOTOSENSORS_SIZE = 60
PIN_HORIZONTAL_HEIGHT = 20
PIN_HORIZONTAL_WIDTH = 40
POT_ALPHA_WIDTH = 12
POT_ALPHA_HEIGHT = 12
POWER_VOLTS = 10
PROBE_SIZE = 20
PROBE_INIT_PADDING = 10
RESISTOR_HORIZONTAL_HEIGHT = 20
RESISTOR_HORIZONTAL_WIDTH = 40
RESISTOR_NUM_ZIG_ZAGS = 5
RESISTOR_TEXT_PADDING = 10
ROBOT_IO_DRAWABLE_SIZE = 40
ROBOT_POWER_DRAWABLE_SIZE = 60
ROBOT_SIZE = 40

# text
APP_NAME = '6.01 Circuit Simulator'
DEV_STAGE = 'alpha'
FILE_EXTENSION = '.circsim'
GROUND = 'gnd'
LAMP_SIGNAL_FILE_EXTENSION = '.lampsig'
LAMP_SIGNAL_FILE_TYPE = 'Lamp Signal File'
OPEN_LAMP_SIGNAL_FILE_TITLE = 'Open lamp signal file ...'
OPEN_POT_SIGNAL_FILE_TITLE = 'Open pot signal file ...'
POT_ALPHA_TEXT = u'\u03B1'
POT_SIGNAL_FILE_EXTENSION = '.potsig'
POT_SIGNAL_FILE_TYPE = 'Pot Signal File'
POWER = 'pwr'
PROBE_MINUS = '-p'
PROBE_PLUS = '+p'
PROTO_BOARD = 'Generate\nLayout'
SIMULATE = 'Run\nSimulation'

# fonts, use different font on Mac OS
BOLD_FONT = ('Helvetica', 12 if system() == 'Darwin' else 10, 'bold')
FONT = ('Helvetica', 12 if system() == 'Darwin' else 10)
SMALL_FONT = ('Helvetica', 10 if system() == 'Darwin' else 8)

# window constants
BOARD_WIDTH = 1000
BOARD_HEIGHT = 600
PALETTE_HEIGHT = 100

# plotter constants
T_SAMPLES = [(n * T) for n in xrange(NUM_SAMPLES)]

# resistance to string conversion, see util.resistance_to_string
RESISTANCE_SUFFIX = [u'\u03a9', u'0\u03a9', u'K\u03a9', u'K\u03a9', u'0K\u03a9',
    u'M\u03a9', u'M\u03a9', u'0M\u03a9', u'G\u03a9', u'G\u03a9']

# regular expressions
RE_OP_AMP_VERTICES = r'\((\d+), (\d+), (\d+), (\d+), (\d+), (\d+)\)'
