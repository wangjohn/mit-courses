"""
Circuit simulator constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.math.CT_signal import Constant_CT_Signal

# op amp constants
OP_AMP_K = 1000000000

# head constants
HEAD_POT_INIT_ALPHA = 0.5
HEAD_POT_RESISTANCE = 10

# motor constants
MOTOR_B_LOADED = 0.0045
MOTOR_B_UNLOADED = 0.0006
MOTOR_INIT_ANGLE = 0
MOTOR_INIT_SPEED = 0
MOTOR_J = 0.00132
MOTOR_KB = 0.495
MOTOR_KT = 0.323
MOTOR_RESISTANCE = 5.26

# photodetector constants
PHOTODETECTOR_K = 5e-7

# sampling constants
NUM_SAMPLES = 100
T = 0.01 # sampling periond

# default simulation signals
DEFAULT_LAMP_ANGLE_SIGNAL = Constant_CT_Signal(0)
DEFAULT_LAMP_DISTANCE_SIGNAL = Constant_CT_Signal(0.5)
DEFAULT_POT_SIGNAL = Constant_CT_Signal(0.5)

# debugging
DEBUG = True
