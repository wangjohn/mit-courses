"""
All the Drawables for the circuit simulator.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import BOLD_FONT
from constants import DIRECTION_DOWN
from constants import DIRECTION_LEFT
from constants import DIRECTION_RIGHT
from constants import DIRECTION_UP
from constants import FONT
from constants import GROUND
from constants import HEAD_COLOR
from constants import HEAD_SIZE
from constants import LABEL_PADDING
from constants import LAMP_BOX_COLOR
from constants import LAMP_BOX_PADDING
from constants import LAMP_BOX_SIZE
from constants import LAMP_COLOR
from constants import LAMP_EMPTY_COLOR
from constants import LAMP_RADIUS
from constants import LAMP_SIGNAL_FILE_EXTENSION
from constants import LAMP_SIGNAL_FILE_TYPE
from constants import MOTOR_FILL
from constants import MOTOR_POT_SIZE
from constants import MOTOR_SIZE
from constants import NEGATIVE_COLOR
from constants import OP_AMP_CONNECTOR_PADDING
from constants import OP_AMP_DOWN_VERTICES
from constants import OP_AMP_FILL
from constants import OP_AMP_LEFT_VERTICES
from constants import OP_AMP_NP
from constants import OP_AMP_OUTLINE
from constants import OP_AMP_PN
from constants import OP_AMP_PWR_GND_FILL
from constants import OP_AMP_RIGHT_VERTICES
from constants import OP_AMP_UP_VERTICES
from constants import OPEN_LAMP_SIGNAL_FILE_TITLE
from constants import OPEN_POT_SIGNAL_FILE_TITLE
from constants import PHOTOSENSORS_SIZE
from constants import PIN_HORIZONTAL_HEIGHT
from constants import PIN_HORIZONTAL_WIDTH
from constants import PIN_OUTLINE
from constants import PIN_TEXT_COLOR
from constants import POSITIVE_COLOR
from constants import POT_ALPHA_EMPTY_FILL
from constants import POT_ALPHA_FILL
from constants import POT_ALPHA_HEIGHT
from constants import POT_ALPHA_OUTLINE
from constants import POT_ALPHA_TEXT
from constants import POT_ALPHA_WIDTH
from constants import POT_SIGNAL_FILE_EXTENSION
from constants import POT_SIGNAL_FILE_TYPE
from constants import POWER_VOLTS
from constants import PROBE_MINUS
from constants import PROBE_PLUS
from constants import PROBE_SIZE
from constants import PROTO_BOARD
from constants import RE_OP_AMP_VERTICES
from constants import RESISTOR_HORIZONTAL_HEIGHT
from constants import RESISTOR_HORIZONTAL_WIDTH
from constants import RESISTOR_TEXT_PADDING
from constants import ROBOT_COLOR
from constants import ROBOT_IO_DRAWABLE_SIZE
from constants import ROBOT_POWER_DRAWABLE_SIZE
from constants import ROBOT_SIZE
from constants import SMALL_FONT
from constants import SIMULATE
from core.gui.components import Drawable
from core.gui.components import Run_Drawable
from core.gui.constants import CONNECTOR_BLRT
from core.gui.constants import CONNECTOR_LEFT
from core.gui.constants import CONNECTOR_RIGHT
from core.gui.constants import ERROR
from core.gui.util import create_circle
from core.gui.util import create_editable_text
from core.gui.util import rotate_connector_flags
from core.save.constants import RE_INT
from core.save.constants import RE_INT_PAIR
from core.undo.undo import Action
from core.util.util import is_callable
from core.util.util import sign
from os.path import isfile
from os.path import relpath
from re import match
from tkFileDialog import askopenfilename
from tkSimpleDialog import askstring
from Tkinter import CENTER
from Tkinter import Menu
from util import draw_resistor_zig_zags
from util import resistance_from_string
from util import resistance_to_string

class Pin_Drawable(Drawable):
  """
  Abstract Drawable to represent basic pins. Draws a box with a label.
  """
  def __init__(self, text, fill, width, height, connectors=0):
    """
    |text|: label for this pin.
    |fill|: color for this pin.
    """
    Drawable.__init__(self, width, height, connectors)
    self.text = text
    self.fill = fill
  def draw_on(self, canvas, offset=(0, 0)):
    ox, oy = offset
    self._rect_id = canvas.create_rectangle((ox, oy, ox + self.width,
        oy + self.height), fill=self.fill, outline=PIN_OUTLINE)
    self.parts.add(self._rect_id)
    self.parts.add(canvas.create_text(ox + self.width / 2,
        oy + self.height / 2, text=self.text, fill=PIN_TEXT_COLOR,
        width=.9 * self.width, justify=CENTER, font=FONT))

class Power_Drawable(Pin_Drawable):
  """
  Power pin.
  """
  def __init__(self, connectors=CONNECTOR_BLRT):
    Pin_Drawable.__init__(self, '+%d' % POWER_VOLTS, POSITIVE_COLOR,
        PIN_HORIZONTAL_WIDTH, PIN_HORIZONTAL_HEIGHT, connectors)
  def rotated(self):
    if self.connector_flags == CONNECTOR_BLRT:
      return self
    return Power_Drawable(rotate_connector_flags(self.connector_flags))
  def serialize(self, offset):
    return 'Power %s' % str(offset)
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Power %s' % RE_INT_PAIR, item_str)
    if m:
      ox, oy = map(int, m.groups())
      board.add_drawable(Power_Drawable(), (ox, oy))
    else:
      # old style Power_Drawable
      m = match(r'Power %s %s' % (RE_INT, RE_INT_PAIR), item_str)
      if m:
        connectors, ox, oy = map(int, m.groups())
        board.add_drawable(Power_Drawable(connectors), (ox, oy))
        return True
      return False

class Ground_Drawable(Pin_Drawable):
  """
  Ground pin.
  """
  def __init__(self, connectors=CONNECTOR_BLRT):
    Pin_Drawable.__init__(self, GROUND, NEGATIVE_COLOR, PIN_HORIZONTAL_WIDTH,
        PIN_HORIZONTAL_HEIGHT, connectors)
  def rotated(self):
    if self.connector_flags == CONNECTOR_BLRT:
      return self
    return Ground_Drawable(rotate_connector_flags(self.connector_flags))
  def serialize(self, offset):
    return 'Ground %s' % str(offset)
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Ground %s' % RE_INT_PAIR, item_str)
    if m:
      ox, oy = map(int, m.groups())
      board.add_drawable(Ground_Drawable(), (ox, oy))
    else:
      # old style Ground_Drawable
      m = match(r'Ground %s %s' % (RE_INT, RE_INT_PAIR), item_str)
      if m:
        connectors, ox, oy = map(int, m.groups())
        board.add_drawable(Ground_Drawable(connectors), (ox, oy))
        return True
      return False

class Probe_Plus_Drawable(Pin_Drawable):
  """
  +probe pin.
  """
  def __init__(self, connectors=CONNECTOR_RIGHT):
    Pin_Drawable.__init__(self, PROBE_PLUS, POSITIVE_COLOR, PROBE_SIZE,
        PROBE_SIZE, connectors)
  def rotated(self):
    return Probe_Plus_Drawable(rotate_connector_flags(self.connector_flags))
  def deletable(self):
    return False
  def serialize(self, offset):
    return 'Probe_Plus %d %s' % (self.connector_flags, str(offset))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Probe_Plus %s %s' % (RE_INT, RE_INT_PAIR), item_str)
    if m:
      connectors, ox, oy = map(int, m.groups())
      board.add_drawable(Probe_Plus_Drawable(connectors), (ox, oy))
      return True
    return False

class Probe_Minus_Drawable(Pin_Drawable):
  """
  -probe pin.
  """
  def __init__(self, connectors=CONNECTOR_RIGHT):
    Pin_Drawable.__init__(self, PROBE_MINUS, NEGATIVE_COLOR, PROBE_SIZE,
        PROBE_SIZE, connectors)
  def rotated(self):
    return Probe_Minus_Drawable(rotate_connector_flags(self.connector_flags))
  def deletable(self):
    return False
  def serialize(self, offset):
    return 'Probe_Minus %d %s' % (self.connector_flags, str(offset))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Probe_Minus %s %s' % (RE_INT, RE_INT_PAIR), item_str)
    if m:
      connectors, ox, oy = map(int, m.groups())
      board.add_drawable(Probe_Minus_Drawable(connectors), (ox, oy))
      return True
    return False

class Resistor_Drawable(Drawable):
  """
  Drawable for Resistors.
  """
  def __init__(self, board, width=RESISTOR_HORIZONTAL_WIDTH,
      height=RESISTOR_HORIZONTAL_HEIGHT,
      connectors=CONNECTOR_LEFT | CONNECTOR_RIGHT, init_resistance='1.0K'):
    """
    |board|: the board on which this Resistor_Drawable is placed.
    |init_resistance|: the initial resistance for this resistor.
    """
    Drawable.__init__(self, width, height, connectors)
    self.board = board
    self.init_resistance = init_resistance
    # for automated tests
    self.get_resistance = lambda: init_resistance
  def draw_on(self, canvas, offset=(0, 0)):
    ox, oy = offset
    w, h = self.width, self.height
    self._resistor_zig_zags = draw_resistor_zig_zags(canvas, ox, oy, w, h)
    self.parts |= self._resistor_zig_zags
    text = resistance_to_string(resistance_from_string(self.init_resistance))
    if w > h: # horizontal
      self.resistor_text = canvas.create_text(ox + w / 2,
          oy - RESISTOR_TEXT_PADDING, text=text, font=FONT)
    else: # vertical
      self.resistor_text = canvas.create_text(ox + w + RESISTOR_TEXT_PADDING +
          8, oy + h / 2, text=text, font=FONT)
    self.parts.add(self.resistor_text)
    def get_resistance():
      """
      Returns the string representing this resistor's resistance.
      """
      return canvas.itemcget(self.resistor_text, 'text')
    self.get_resistance = get_resistance
    def _set_resistance(r):
      canvas.itemconfig(self.resistor_text, text=r)
      self.init_resistance = r
    def set_resistance(r):
      """
      Sets the resistance of this resistor to be the string |r|, after
          appropriately modifying it.
      """
      if not r:
        self.board.display_message('No resistance entered', ERROR)
        return
      try:
        old_r = self.get_resistance()
        new_r = resistance_to_string(resistance_from_string(r))
        do = lambda: _set_resistance(new_r)
        undo = lambda: _set_resistance(old_r)
        do()
        self.board.set_changed(True, Action(do, undo, 'set_resistance'))
      except Exception as e:
        self.board.display_message(e.message, ERROR)
    self.set_resistance = set_resistance
  def rotated(self):
    return Resistor_Drawable(self.board, self.height, self.width,
        rotate_connector_flags(self.connector_flags), self.get_resistance())
  def _setup_menu(self, parent):
    menu = Menu(parent, tearoff=0)
    menu.add_command(label='Set Resistance', command=lambda:
        self.set_resistance(askstring('Resistor', 'Enter Resistance Value:')))
    return menu
  def on_right_click(self, event):
    self._setup_menu(event.widget).tk_popup(event.x_root, event.y_root)
  def add_to_menu(self, menu):
    menu.add_cascade(label='Resistor', menu=self._setup_menu(menu))
    return menu.index('Resistor')
  def serialize(self, offset):
    # remove ohm sign
    resistance = self.get_resistance().replace(u'\u03a9', '')
    return 'Resistor %s %d %d %d %s' % (resistance, self.width, self.height,
        self.connector_flags, str(offset))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Resistor (.+) %s %s %s %s' % (RE_INT, RE_INT, RE_INT,
        RE_INT_PAIR), item_str)
    if m:
      r = m.group(1)
      width, height, connectors, ox, oy = map(int, m.groups()[1:])
      board.add_drawable(Resistor_Drawable(board, width, height, connectors,
          r), (ox, oy))
      return True
    return False

class Op_Amp_Drawable(Drawable):
  """
  Drawable for op amps.
  """
  def __init__(self, board, vertices=OP_AMP_RIGHT_VERTICES, signs=OP_AMP_PN,
      jfet=False):
    """
    |board|: the board on which this Op_Amp_Drawable lives.
    |vertices|: the vertices of the triangle for this op amp.
    |signs|: order of signs for this op amp, to allow two configurations.
    |jfet|: True if this is a JFET Op Amp, False otherwise (Power).
    """
    assert vertices in (OP_AMP_RIGHT_VERTICES, OP_AMP_DOWN_VERTICES,
        OP_AMP_LEFT_VERTICES, OP_AMP_UP_VERTICES), 'invalid op amp vertices'
    assert signs in (OP_AMP_PN, OP_AMP_NP), 'invalid op amp signs'
    self.board = board
    self.signs = signs
    self.vertices = vertices
    self.jfet = jfet
    x1, y1, x2, y2, x3, y3 = vertices
    min_x, max_x = [f(x1, x2, x3) for f in min, max]
    min_y, max_y = [f(y1, y2, y3) for f in min, max]
    Drawable.__init__(self, max_x - min_x, max_y - min_y)
  def draw_on(self, canvas, offset=(0, 0)):
    x1, y1, x2, y2, x3, y3 = self.vertices
    ox, oy = offset
    x1, x2, x3 = x1 + ox, x2 + ox, x3 + ox
    y1, y2, y3 = y1 + oy, y2 + oy, y3 + oy
    # pwr, gnd line
    _x, x_ = min(x1, x2, x3), max(x1, x2, x3)
    _x_ = (_x + x_) / 2
    _y, y_ = min(y1, y2, y3), max(y1, y2, y3)
    _y_ = (_y + y_) / 2
    top = '+10'
    bottom = 'gnd'
    if self.signs != OP_AMP_PN:
      top, bottom = bottom, top
    if x1 == x2 or x2 == x3:
      self.parts.add(canvas.create_line(_x_, _y + 10, _x_, y_ - 10,
          fill=OP_AMP_PWR_GND_FILL))
    else:
      self.parts.add(canvas.create_line(_x + 10, _y_, x_ - 10, _y_,
          fill=OP_AMP_PWR_GND_FILL))
    # triangle
    self._triangle_id = canvas.create_polygon(x1, y1, x2, y2, x3, y3,
        fill=OP_AMP_FILL, outline=OP_AMP_OUTLINE)
    self.parts.add(self._triangle_id)
    # labels
    text_1 = '+' if self.signs == OP_AMP_PN else '-'
    text_2 = '-' if self.signs == OP_AMP_PN else '+'
    if self.vertices == OP_AMP_RIGHT_VERTICES:
      self.parts.add(canvas.create_text(x1 + LABEL_PADDING,
          y1 + OP_AMP_CONNECTOR_PADDING, text=text_1, font=FONT))
      self.parts.add(canvas.create_text(x2 + LABEL_PADDING,
          y2 - OP_AMP_CONNECTOR_PADDING, text=text_2, font=FONT))
      self.parts.add(canvas.create_text(_x_, _y + 4, text=top,
          font=SMALL_FONT, fill=OP_AMP_PWR_GND_FILL))
      self.parts.add(canvas.create_text(_x_, y_ - 4, text=bottom,
          font=SMALL_FONT, fill=OP_AMP_PWR_GND_FILL))
    elif self.vertices == OP_AMP_DOWN_VERTICES:
      self.parts.add(canvas.create_text(x3 - OP_AMP_CONNECTOR_PADDING,
          y3 + LABEL_PADDING, text=text_1, font=FONT))
      self.parts.add(canvas.create_text(x1 + OP_AMP_CONNECTOR_PADDING,
          y1 + LABEL_PADDING, text=text_2, font=FONT))
      self.parts.add(canvas.create_text(_x, _y_, text=bottom,
          font=SMALL_FONT, fill=OP_AMP_PWR_GND_FILL))
      self.parts.add(canvas.create_text(x_, _y_, text=top,
          font=SMALL_FONT, fill=OP_AMP_PWR_GND_FILL))
    elif self.vertices == OP_AMP_LEFT_VERTICES:
      self.parts.add(canvas.create_text(x2 - LABEL_PADDING,
          y2 - OP_AMP_CONNECTOR_PADDING, text=text_1, font=FONT))
      self.parts.add(canvas.create_text(x3 - LABEL_PADDING,
          y3 + OP_AMP_CONNECTOR_PADDING, text=text_2, font=FONT))
      self.parts.add(canvas.create_text(_x_, _y + 4, text=bottom,
          font=SMALL_FONT, fill=OP_AMP_PWR_GND_FILL))
      self.parts.add(canvas.create_text(_x_, y_ - 4, text=top,
          font=SMALL_FONT, fill=OP_AMP_PWR_GND_FILL))
    else: # OP_AMP_UP_VERTICES
      self.parts.add(canvas.create_text(x2 + OP_AMP_CONNECTOR_PADDING,
          y2 - LABEL_PADDING, text=text_1, font=FONT))
      self.parts.add(canvas.create_text(x3 - OP_AMP_CONNECTOR_PADDING,
          y3 - LABEL_PADDING, text=text_2, font=FONT))
      self.parts.add(canvas.create_text(_x, _y_, text=top,
          font=SMALL_FONT, fill=OP_AMP_PWR_GND_FILL))
      self.parts.add(canvas.create_text(x_, _y_, text=bottom,
          font=SMALL_FONT, fill=OP_AMP_PWR_GND_FILL))
    if self.jfet:
      self._jfet_id = canvas.create_text((x1 + x2 + x3) / 3.,
          (y1 + y2 + y3) / 3., text='J', fill='red', font=BOLD_FONT)
      self.parts.add(self._jfet_id)
    def toggle_jfet():
      if self.jfet:
        assert self._jfet_id in self.parts
        self.parts.remove(self._jfet_id)
        canvas.delete(self._jfet_id)
        self.jfet = False
      else:
        x1, y1, x2, y2, x3, y3 = self.vertices
        ox, oy = self.offset
        self._jfet_id = canvas.create_text(ox + (x1 + x2 + x3) / 3., oy + (y1 +
            y2 + y3) / 3., text='J', fill='red', font=BOLD_FONT)
        self.parts.add(self._jfet_id)
        self.jfet = True
    self.toggle_jfet = toggle_jfet
  def _setup_menu(self, parent):
    def command():
      self.toggle_jfet()
      self.board.set_changed(True, Action(self.toggle_jfet, self.toggle_jfet,
          'toggle_jfet'))
    menu = Menu(parent, tearoff=0)
    menu.add_command(label='Toggle JFET', command=command)
    return menu
  def on_right_click(self, event):
    self._setup_menu(event.widget).tk_popup(event.x_root, event.y_root)
  def add_to_menu(self, menu):
    menu.add_cascade(label='Op Amp', menu=self._setup_menu(menu))
    return menu.index('Op Amp')
  def draw_connectors(self, canvas, offset=(0, 0)):
    x1, y1, x2, y2, x3, y3 = self.vertices
    ox, oy = offset
    x1, x2, x3 = x1 + ox, x2 + ox, x3 + ox
    y1, y2, y3 = y1 + oy, y2 + oy, y3 + oy
    if self.vertices == OP_AMP_RIGHT_VERTICES:
      self.plus_port = self._draw_connector(canvas, (x1,
          y1 + OP_AMP_CONNECTOR_PADDING))
      self.minus_port = self._draw_connector(canvas, (x2,
          y2 - OP_AMP_CONNECTOR_PADDING))
      self.out_port = self._draw_connector(canvas, (x3, y3))
    elif self.vertices == OP_AMP_DOWN_VERTICES:
      self.plus_port = self._draw_connector(canvas,
          (x3 - OP_AMP_CONNECTOR_PADDING, y3))
      self.minus_port = self._draw_connector(canvas,
          (x1 + OP_AMP_CONNECTOR_PADDING, y1))
      self.out_port = self._draw_connector(canvas, (x2, y2))
    elif self.vertices == OP_AMP_LEFT_VERTICES:
      self.plus_port = self._draw_connector(canvas, (x2,
          y2 - OP_AMP_CONNECTOR_PADDING))
      self.minus_port = self._draw_connector(canvas, (x3,
          y3 + OP_AMP_CONNECTOR_PADDING))
      self.out_port = self._draw_connector(canvas, (x1, y1))
    else: # OP_AMP_UP_VERTICES
      self.plus_port = self._draw_connector(canvas,
          (x2 + OP_AMP_CONNECTOR_PADDING, y2))
      self.minus_port = self._draw_connector(canvas,
          (x3 - OP_AMP_CONNECTOR_PADDING, y3))
      self.out_port = self._draw_connector(canvas, (x1, y1))
    if self.signs == OP_AMP_NP:
      self.plus_port, self.minus_port = self.minus_port, self.plus_port
  def rotated(self):
    if self.vertices == OP_AMP_RIGHT_VERTICES:
      return Op_Amp_Drawable(self.board, OP_AMP_DOWN_VERTICES, self.signs,
          self.jfet)
    elif self.vertices == OP_AMP_DOWN_VERTICES:
      return Op_Amp_Drawable(self.board, OP_AMP_LEFT_VERTICES, self.signs,
          self.jfet)
    elif self.vertices == OP_AMP_LEFT_VERTICES:
      return Op_Amp_Drawable(self.board, OP_AMP_UP_VERTICES, self.signs,
          self.jfet)
    else: # OP_AMP_UP_VERTICES
      return Op_Amp_Drawable(self.board, OP_AMP_RIGHT_VERTICES, self.signs,
          self.jfet)
  def serialize(self, offset):
    return 'Op_Amp %s %s %d %d' % (str(self.vertices), str(offset), self.signs,
        int(self.jfet))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Op_Amp %s %s %s %s' % (RE_OP_AMP_VERTICES, RE_INT_PAIR, RE_INT,
        RE_INT), item_str)
    if m:
      x1, y1, x2, y2, x3, y3, ox, oy, signs, jfet = map(int, m.groups())
      board.add_drawable(Op_Amp_Drawable(board, (x1, y1, x2, y2, x3, y3), signs,
          jfet), (ox, oy))
      return True
    else:
      m = match(r'Op_Amp %s %s' % (RE_OP_AMP_VERTICES, RE_INT_PAIR), item_str)
      if m:
        x1, y1, x2, y2, x3, y3, ox, oy = map(int, m.groups())
        board.add_drawable(Op_Amp_Drawable(board, (x1, y1, x2, y2, x3, y3)),
            (ox, oy))
        return True
    return False

class Pot_Drawable(Drawable):
  """
  Drawable for pots.
  """
  def __init__(self, on_signal_file_changed, width=RESISTOR_HORIZONTAL_WIDTH,
      height=RESISTOR_HORIZONTAL_HEIGHT, direction=DIRECTION_UP,
      signal_file=None):
    """
    |on_signal_file_changed|: function to be called when pot signal file is
        changed.
    |direction|: the direction of this pot, one of DIRECTION_DOWN,
        DIRECTION_LEFT, DIRECTION_RIGHT, or DIRECTION_UP.
    |signal_file|: the signal file (containing alpha) associated with this pot.
    """
    assert is_callable(on_signal_file_changed), ('on_signal_file_changed must '
        'be callable')
    Drawable.__init__(self, width, height)
    self.on_signal_file_changed = on_signal_file_changed
    self.direction = direction
    self.signal_file = signal_file
  def draw_on(self, canvas, offset=(0, 0)):
    ox, oy = offset
    w, h = self.width, self.height
    self._resistor_zig_zags = draw_resistor_zig_zags(canvas, ox, oy, w, h)
    self.parts |= self._resistor_zig_zags
    # create button that lets user select a signal file for this pot when
    #     right-clicked
    pot_alpha_window = canvas.create_rectangle(ox + (w - POT_ALPHA_WIDTH) / 2,
        oy + (h - POT_ALPHA_HEIGHT) / 2, ox + (w + POT_ALPHA_WIDTH) / 2,
        oy + (h + POT_ALPHA_HEIGHT) / 2, fill=POT_ALPHA_FILL if
        self.signal_file else POT_ALPHA_EMPTY_FILL, outline=POT_ALPHA_OUTLINE)
    pot_alpha_text = canvas.create_text(ox + w / 2, oy + h / 2 - 1,
        text=POT_ALPHA_TEXT, justify=CENTER, fill='white' if self.signal_file
        else 'black', font=FONT)
    def set_signal_file():
      """
      Opens a window to let the user choose a signal file.
      """
      new_signal_file = askopenfilename(title=OPEN_POT_SIGNAL_FILE_TITLE,
          filetypes=[('%s files' % POT_SIGNAL_FILE_TYPE,
          POT_SIGNAL_FILE_EXTENSION)], initialfile=self.signal_file)
      if new_signal_file and new_signal_file != self.signal_file:
        self.signal_file = relpath(new_signal_file)
        canvas.itemconfig(pot_alpha_window, fill=POT_ALPHA_FILL)
        canvas.itemconfig(pot_alpha_text, fill='white')
        self.on_signal_file_changed()
    self.set_signal_file = set_signal_file
    self.parts.add(pot_alpha_window)
    self.parts.add(pot_alpha_text)
  def draw_connectors(self, canvas, offset=(0, 0)):
    ox, oy = offset
    w, h = self.width, self.height
    if self.direction == DIRECTION_UP:
      self.top_connector = self._draw_connector(canvas, (ox, oy + h / 2))
      self.middle_connector = self._draw_connector(canvas, (ox + w / 2, oy))
      self.bottom_connector = self._draw_connector(canvas, (ox + w,
          oy + h / 2))
    elif self.direction == DIRECTION_RIGHT:
      self.top_connector = self._draw_connector(canvas, (ox + w / 2, oy))
      self.middle_connector = self._draw_connector(canvas, (ox + w,
          oy + h / 2))
      self.bottom_connector = self._draw_connector(canvas, (ox + w / 2,
          oy + h))
    elif self.direction == DIRECTION_DOWN:
      self.top_connector = self._draw_connector(canvas, (ox + w,
          oy + h / 2))
      self.middle_connector = self._draw_connector(canvas, (ox + w / 2,
          oy + h))
      self.bottom_connector = self._draw_connector(canvas, (ox, oy + h / 2))
    elif self.direction == DIRECTION_LEFT:
      self.top_connector = self._draw_connector(canvas, (ox + w / 2, oy + h))
      self.middle_connector = self._draw_connector(canvas, (ox, oy + h / 2))
      self.bottom_connector = self._draw_connector(canvas, (ox + w / 2, oy))
    else:
      # should never get here
      raise Exception('Invalid direction %s' % self.direction)
  def rotated(self):
    return Pot_Drawable(self.on_signal_file_changed, self.height, self.width,
        (self.direction + 1) % 4, self.signal_file)
  def _setup_menu(self, parent):
    menu = Menu(parent, tearoff=0)
    menu.add_command(label='Set Signal File', command=self.set_signal_file)
    return menu
  def on_right_click(self, event):
    self._setup_menu(event.widget).tk_popup(event.x_root, event.y_root)
  def add_to_menu(self, menu):
    menu.add_cascade(label='Pot', menu=self._setup_menu(menu))
    return menu.index('Pot')
  def serialize(self, offset):
    return 'Pot %s %d %d %d %s' % (self.signal_file, self.width, self.height,
        self.direction, str(offset))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Pot (.+) %s %s %s %s' % (RE_INT, RE_INT, RE_INT, RE_INT_PAIR),
        item_str)
    if m:
      signal_file = m.group(1).replace('\\', '//')
      if not isfile(signal_file):
        signal_file = None
      width, height, direction, ox, oy = map(int, m.groups()[1:])
      board.add_drawable(Pot_Drawable(lambda: board.set_changed(True), width,
          height, direction, signal_file), (ox, oy))
      return True
    return False

class Motor_Drawable(Pin_Drawable):
  """
  Drawable for motor (can be independent or can be part of head).
  """
  def __init__(self, color=MOTOR_FILL, group_id=0, direction=DIRECTION_UP):
    """
    |group_id|: indicator for the head this Motor_Drawable is a part of, if this
        is not an independent motor.
    """
    Pin_Drawable.__init__(self, 'Head\nMotor' if group_id else 'Motor', color,
        MOTOR_SIZE, MOTOR_SIZE)
    self.color = color
    self.group_id = group_id
    self.direction = direction
  def _plus_minus_positions(self, offset):
    ox, oy = offset
    w, h = self.width, self.height
    cx, cy = ox + w / 2, oy + h / 2
    if self.direction == DIRECTION_UP:
      return cx, oy, cx, oy + h
    elif self.direction == DIRECTION_RIGHT:
      return ox + w, cy, ox, cy
    elif self.direction == DIRECTION_DOWN:
      return cx, oy + h, cx, oy
    elif self.direction == DIRECTION_LEFT:
      return ox, cy, ox + w, cy
    else:
      # should never get here
      raise Exception('Invalid direction %s' % self.direction)
  def draw_on(self, canvas, offset=(0, 0)):
    Pin_Drawable.draw_on(self, canvas, offset)
    ox, oy = offset
    w, h = self.width, self.height
    cx, cy = ox + w / 2, oy + h / 2
    plus_x, plus_y, minus_x, minus_y = self._plus_minus_positions(offset)
    self.parts.add(canvas.create_text(plus_x + LABEL_PADDING * sign(cx -
        plus_x), plus_y + LABEL_PADDING * sign(cy - plus_y), text='+',
        fill='white', justify=CENTER, font=FONT))
    self.parts.add(canvas.create_text(minus_x + LABEL_PADDING * sign(cx -
        minus_x), minus_y + LABEL_PADDING * sign(cy - minus_y), text='-',
        fill='white', justify=CENTER, font=FONT))
  def draw_connectors(self, canvas, offset=(0, 0)):
    plus_x, plus_y, minus_x, minus_y = self._plus_minus_positions(offset)
    self.plus = self._draw_connector(canvas, (plus_x, plus_y))
    self.minus = self._draw_connector(canvas, (minus_x, minus_y))
  def rotated(self):
    return Motor_Drawable(self.color, self.group_id, (self.direction + 1) % 4)
  def _setup_menu(self, parent):
    if not self.group_id:
      # this is a stand alone motor, not part of a head
      return None
    motor_pot_needed = True
    photosensors_needed = True
    for drawable in self.board.get_drawables():
      if isinstance(drawable, Motor_Pot_Drawable) and (drawable.group_id ==
          self.group_id):
        motor_pot_needed = False
      elif isinstance(drawable, Photosensors_Drawable) and (drawable.group_id ==
          self.group_id):
        photosensors_needed = False
    if motor_pot_needed or photosensors_needed:
      menu = Menu(parent, tearoff=0)
      def readd():
        if motor_pot_needed:
          self.board.add_drawable(Motor_Pot_Drawable(self.color, self.group_id),
              self.offset)
        if photosensors_needed:
          self.board.add_drawable(Photosensors_Drawable(self.color,
            self.group_id, lambda: self.board.set_changed(True)), self.offset)
        if motor_pot_needed and photosensors_needed:
          self.board._action_history.combine_last_n(2)
      menu.add_command(label='Re-add Missing Parts', command=readd)
      return menu
  def on_right_click(self, event):
    m = self._setup_menu(event.widget)
    if m is not None:
      m.tk_popup(event.x_root, event.y_root)
  def add_to_menu(self, menu):
    m = self._setup_menu(menu)
    if m is not None:
      menu.add_cascade(label='Motor', menu=m)
      return menu.index('Motor')
  def serialize(self, offset):
    return 'Motor %s %d %d %s' % (self.color, self.direction, self.group_id,
        str(offset))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Motor (.+) %s %s %s' % (RE_INT, RE_INT, RE_INT_PAIR), item_str)
    if m:
      color = m.group(1)
      direction, group_id, ox, oy = map(int, m.groups()[1:])
      board.add_drawable(Motor_Drawable(color, group_id, direction), (ox, oy))
      return True
    return False

class Motor_Pot_Drawable(Pin_Drawable):
  """
  Drawable for motor pot on head.
  """
  def __init__(self, color, group_id, direction=DIRECTION_RIGHT):
    """
    |group_id|: indicator for the head this Motor_Pot_Drawable is a part of.
    """
    Pin_Drawable.__init__(self, 'Head\nPot', color, MOTOR_POT_SIZE,
        MOTOR_POT_SIZE)
    self.color = color
    self.group_id = group_id
    self.direction = direction
  def _pin_positions(self, offset):
    ox, oy = offset
    w, h = self.width, self.height
    cx, cy = ox + w / 2, oy + h / 2
    if self.direction == DIRECTION_UP:
      return ox, cy, cx, oy, ox + w, cy
    elif self.direction == DIRECTION_RIGHT:
      return cx, oy, ox + w, cy, cx, oy + h
    elif self.direction == DIRECTION_DOWN:
      return ox + w, cy, cx, oy + h, ox, cy
    elif self.direction == DIRECTION_LEFT:
      return cx, oy + h, ox, cy, cx, oy
    else:
      # should never get here
      raise Exception('Invalid direction %s' % self.direction)
  def draw_on(self, canvas, offset=(0, 0)):
    Pin_Drawable.draw_on(self, canvas, offset)
    ox, oy = offset
    w, h = self.width, self.height
    cx, cy = ox + w / 2, oy + h / 2
    top_x, top_y, middle_x, middle_y, bottom_x, bottom_y = self._pin_positions(
        offset)
    self.parts.add(canvas.create_text(top_x + LABEL_PADDING * sign(cx - top_x),
        top_y + LABEL_PADDING * sign(cy - top_y), text='+', fill='white',
        justify=CENTER, font=FONT))
    self.parts.add(canvas.create_text(middle_x + LABEL_PADDING * sign(cx -
        middle_x), middle_y + LABEL_PADDING * sign(cy - middle_y), text='m',
        fill='white', justify=CENTER, font=FONT))
    self.parts.add(canvas.create_text(bottom_x + LABEL_PADDING * sign(cx -
        bottom_x), bottom_y + LABEL_PADDING * sign(cy - bottom_y), text='-',
        fill='white', justify=CENTER, font=FONT))
  def draw_connectors(self, canvas, offset=(0, 0)):
    top_x, top_y, middle_x, middle_y, bottom_x, bottom_y = self._pin_positions(
        offset)
    self.top = self._draw_connector(canvas, (top_x, top_y))
    self.middle = self._draw_connector(canvas, (middle_x, middle_y))
    self.bottom = self._draw_connector(canvas, (bottom_x, bottom_y))
  def rotated(self):
    return Motor_Pot_Drawable(self.color, self.group_id,
        (self.direction + 1) % 4)
  def _setup_menu(self, parent):
    motor_needed = True
    photosensors_needed = True
    for drawable in self.board.get_drawables():
      if isinstance(drawable, Motor_Drawable) and (drawable.group_id ==
          self.group_id):
        motor_needed = False
      elif isinstance(drawable, Photosensors_Drawable) and (drawable.group_id ==
          self.group_id):
        photosensors_needed = False
    if motor_needed or photosensors_needed:
      menu = Menu(parent, tearoff=0)
      def readd():
        if motor_needed:
          self.board.add_drawable(Motor_Drawable(self.color, self.group_id),
              self.offset)
        if photosensors_needed:
          self.board.add_drawable(Photosensors_Drawable(self.color,
            self.group_id, lambda: self.board.set_changed(True)), self.offset)
        if motor_needed and photosensors_needed:
          self.board._action_history.combine_last_n(2)
      menu.add_command(label='Re-add Missing Parts', command=readd)
      return menu
  def on_right_click(self, event):
    m = self._setup_menu(event.widget)
    if m is not None:
      m.tk_popup(event.x_root, event.y_root)
  def add_to_menu(self, menu):
    m = self._setup_menu(menu)
    if m is not None:
      menu.add_cascade(label='Motor Pot', menu=m)
      return menu.index('Motor Pot')
  def serialize(self, offset):
    return 'Motor_Pot %s %d %d %s' % (self.color, self.direction,
        self.group_id, str(offset))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Motor_Pot (.+) %s %s %s' % (RE_INT, RE_INT, RE_INT_PAIR),
        item_str)
    if m:
      color = m.group(1)
      direction, group_id, ox, oy = map(int, m.groups()[1:])
      board.add_drawable(Motor_Pot_Drawable(color, group_id, direction), (ox,
          oy))
      return True
    return False

class Photosensors_Drawable(Pin_Drawable):
  """
  Drawable for photodetectors on head.
  """
  def __init__(self, color, group_id, on_signal_file_changed,
      direction=DIRECTION_RIGHT, signal_file=None):
    """
    |group_id|: indicator for the head this Photosensors_Drawable is a part of.
    |on_signal_file_changed|: function to be called when photosensor signal
        file is changed.
    |signal_file|: the signal file containing lamp angle and distance.
    """
    assert is_callable(on_signal_file_changed), ('on_signal_file_changed must '
        'be callable')
    Pin_Drawable.__init__(self, 'Head\nEyes', color, PHOTOSENSORS_SIZE,
        PHOTOSENSORS_SIZE)
    self.color = color
    self.group_id = group_id
    self.on_signal_file_changed = on_signal_file_changed
    self.direction = direction
    self.signal_file = signal_file
  def _pin_positions(self, offset):
    ox, oy = offset
    w, h = self.width, self.height
    cx, cy = ox + w / 2, oy + h / 2
    if self.direction == DIRECTION_UP:
      return ox, cy, cx, oy, ox + w, cy
    elif self.direction == DIRECTION_RIGHT:
      return cx, oy, ox + w, cy, cx, oy + h
    elif self.direction == DIRECTION_DOWN:
      return ox + w, cy, cx, oy + h, ox, cy
    elif self.direction == DIRECTION_LEFT:
      return cx, oy + h, ox, cy, cx, oy
    else:
      # should never get here
      raise Exception('Invalid direction %s' % self.direction)
  def draw_on(self, canvas, offset=(0, 0)):
    Pin_Drawable.draw_on(self, canvas, offset)
    ox, oy = offset
    w, h = self.width, self.height
    cx, cy = ox + w / 2, oy + h / 2
    left_x, left_y, common_x, common_y, right_x, right_y = self._pin_positions(
        offset)
    self.parts.add(canvas.create_text(left_x + LABEL_PADDING * sign(cx -
        left_x), left_y + LABEL_PADDING * sign(cy - left_y), text='l',
        fill='white', justify=CENTER, font=FONT))
    self.parts.add(canvas.create_text(common_x + LABEL_PADDING * sign(cx -
        common_x), common_y + LABEL_PADDING * sign(cy - common_y), text='c',
        fill='white', justify=CENTER, font=FONT))
    self.parts.add(canvas.create_text(right_x + LABEL_PADDING * sign(cx -
        right_x), right_y + LABEL_PADDING * sign(cy - right_y), text='r',
        fill='white', justify=CENTER, font=FONT))
    # draw the button that shows whether a signal file has been selected
    lamp_cx = ox + LAMP_BOX_PADDING + LAMP_BOX_SIZE / 2
    lamp_cy = oy + LAMP_BOX_PADDING + LAMP_BOX_SIZE / 2
    lamp_box = canvas.create_rectangle(lamp_cx - LAMP_BOX_SIZE / 2, lamp_cy -
        LAMP_BOX_SIZE / 2, lamp_cx + LAMP_BOX_SIZE / 2, lamp_cy +
        LAMP_BOX_SIZE / 2, fill=LAMP_BOX_COLOR)
    lamp = create_circle(canvas, lamp_cx, lamp_cy, LAMP_RADIUS, fill=LAMP_COLOR
        if self.signal_file else LAMP_EMPTY_COLOR)
    def set_signal_file():
      """
      Opens a window to let the user choose a lamp signal file.
      """
      new_signal_file = askopenfilename(title=OPEN_LAMP_SIGNAL_FILE_TITLE,
          filetypes=[('%s files' % LAMP_SIGNAL_FILE_TYPE,
          LAMP_SIGNAL_FILE_EXTENSION)], initialfile=self.signal_file)
      if new_signal_file and new_signal_file != self.signal_file:
        self.signal_file = relpath(new_signal_file)
        canvas.itemconfig(lamp, fill=LAMP_COLOR)
        self.on_signal_file_changed()
    self.set_signal_file = set_signal_file
    self.parts.add(lamp_box)
    self.parts.add(lamp)
  def draw_connectors(self, canvas, offset=(0, 0)):
    left_x, left_y, common_x, common_y, right_x, right_y = self._pin_positions(
        offset)
    self.left = self._draw_connector(canvas, (left_x, left_y))
    self.common = self._draw_connector(canvas, (common_x, common_y))
    self.right = self._draw_connector(canvas, (right_x, right_y))
  def rotated(self):
    return Photosensors_Drawable(self.color, self.group_id,
        self.on_signal_file_changed, (self.direction + 1) % 4, self.signal_file)
  def _setup_menu(self, parent):
    menu = Menu(parent, tearoff=0)
    menu.add_command(label='Set Signal File', command=self.set_signal_file)
    motor_needed = True
    motor_pot_needed = True
    for drawable in self.board.get_drawables():
      if isinstance(drawable, Motor_Drawable) and (drawable.group_id ==
          self.group_id):
        motor_needed = False
      elif isinstance(drawable, Motor_Pot_Drawable) and (drawable.group_id ==
          self.group_id):
        motor_pot_needed = False
    if motor_needed or motor_pot_needed:
      def readd():
        if motor_needed:
          self.board.add_drawable(Motor_Drawable(self.color, self.group_id),
              self.offset)
        if motor_pot_needed:
          self.board.add_drawable(Motor_Pot_Drawable(self.color, self.group_id),
              self.offset)
        if motor_needed and motor_pot_needed:
          self.board._action_history.combine_last_n(2)
      menu.add_command(label='Re-add Missing Parts', command=readd)
    return menu
  def on_right_click(self, event):
    self._setup_menu(event.widget).tk_popup(event.x_root, event.y_root)
  def add_to_menu(self, menu):
    menu.add_cascade(label='Photosensors', menu=self._setup_menu(menu))
    return menu.index('Photosensors')
  def serialize(self, offset):
    return 'Photosensors %s %s %d %d %s' % (self.signal_file, self.color,
        self.direction, self.group_id, str(offset))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Photosensors (\S+) (\S+) %s %s %s' % (RE_INT, RE_INT,
        RE_INT_PAIR), item_str)
    if m:
      signal_file = m.group(1).replace('\\', '//')
      if not isfile(signal_file):
        signal_file = None
      color = m.group(2)
      direction, group_id, ox, oy = map(int, m.groups()[2:])
      board.add_drawable(Photosensors_Drawable(color, group_id,
          lambda: board.set_changed(True), direction, signal_file), (ox, oy))
      return True
    return False

class Head_Connector_Drawable(Pin_Drawable):
  """
  Drawable that, when clicked, spawns the drawables for items on the head (i.e.
      Motor_Drawable, Motor_Pot_Drawable, Photosensors_Drawable).
  """
  def __init__(self):
    Pin_Drawable.__init__(self, 'Head', HEAD_COLOR, HEAD_SIZE, HEAD_SIZE)

class Robot_Power_Drawable(Pin_Drawable):
  """
  Drawable for robot power.
  """
  def __init__(self, color, group_id, direction=DIRECTION_UP):
    """
    |group_id|: indicator for the robot this Robot_Power_Drawable is a part of.
    """
    Pin_Drawable.__init__(self, 'Robot Power', color,
        ROBOT_POWER_DRAWABLE_SIZE, ROBOT_POWER_DRAWABLE_SIZE)
    self.color = color
    self.group_id = group_id
    self.direction = direction
  def _pwr_gnd_positions(self, offset):
    ox, oy = offset
    w, h = self.width, self.height
    cx, cy = ox + w / 2, oy + h / 2
    if self.direction == DIRECTION_UP:
      return cx, oy, cx, oy + h
    elif self.direction == DIRECTION_RIGHT:
      return ox + w, cy, ox, cy
    elif self.direction == DIRECTION_DOWN:
      return cx, oy + h, cx, oy
    elif self.direction == DIRECTION_LEFT:
      return ox, cy, ox + w, cy
    else:
      # should never get here
      raise Exception('Invalid direction %s' % self.direction)
  def draw_on(self, canvas, offset=(0, 0)):
    Pin_Drawable.draw_on(self, canvas, offset)
    ox, oy = offset
    w, h = self.width, self.height
    cx, cy = ox + w / 2, oy + h / 2
    pwr_x, pwr_y, gnd_x, gnd_y = self._pwr_gnd_positions(offset)
    self.parts.add(canvas.create_text(pwr_x + LABEL_PADDING * sign(cx - pwr_x),
        pwr_y + LABEL_PADDING * sign(cy - pwr_y), text='+', fill='white',
        justify=CENTER, font=FONT))
    self.parts.add(canvas.create_text(gnd_x + LABEL_PADDING * sign(cx - gnd_x),
        gnd_y + LABEL_PADDING * sign(cy - gnd_y), text='-', fill='white',
        justify=CENTER, font=FONT))
  def draw_connectors(self, canvas, offset=(0, 0)):
    pwr_x, pwr_y, gnd_x, gnd_y = self._pwr_gnd_positions(offset)
    self.pwr = self._draw_connector(canvas, (pwr_x, pwr_y))
    self.gnd = self._draw_connector(canvas, (gnd_x, gnd_y))
  def rotated(self):
    return Robot_Power_Drawable(self.color, self.group_id,
        (self.direction + 1) % 4)
  def _setup_menu(self, parent):
    present = set()
    for drawable in self.board.get_drawables():
      if isinstance(drawable, Robot_IO_Drawable) and (drawable.group_id ==
          self.group_id):
        present.add(drawable.name)
    if len(present) < 5:
      menu = Menu(parent, tearoff=0)
      def readd():
        n = 0
        for name in ['Ai1', 'Ai2', 'Ai3', 'Ai4', 'Ao']:
          if name not in present:
            self.board.add_drawable(Robot_IO_Drawable(name, self.color,
                self.group_id), self.offset)
            n += 1
        if n > 1:
          self.board._action_history.combine_last_n(n)
      menu.add_command(label='Re-add Missing Parts', command=readd)
      return menu
  def on_right_click(self, event):
    m = self._setup_menu(event.widget)
    if m is not None:
      m.tk_popup(event.x_root, event.y_root)
  def add_to_menu(self, menu):
    m = self._setup_menu(menu)
    if m is not None:
      menu.add_cascade(label='Robot Power', menu=m)
      return menu.index('Robot Power')
  def serialize(self, offset):
    return 'Robot_Power %s %s %d %s' % (self.color, self.group_id,
        self.direction, str(offset))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Robot_Power (.+) %s %s %s' % (RE_INT, RE_INT, RE_INT_PAIR),
        item_str)
    if m:
      color = m.group(1)
      group_id, direction, ox, oy = map(int, m.groups()[1:])
      board.add_drawable(Robot_Power_Drawable(color, group_id, direction), (ox,
          oy))
      return True
    return False

class Robot_IO_Drawable(Pin_Drawable):
  """
  Drawable for robot analog inputs and output.
  """
  def __init__(self, name, color, group_id, connectors=CONNECTOR_RIGHT):
    """
    name: name of this IO drawable (e.g. Ai1, Ao)
    |group_id|: indicator for the robot this Robot_IO_Drawable is a part of.
    """
    Pin_Drawable.__init__(self, name, color, ROBOT_IO_DRAWABLE_SIZE,
        ROBOT_IO_DRAWABLE_SIZE, connectors)
    self.name = name
    self.color = color
    self.group_id = group_id
  def rotated(self):
    return Robot_IO_Drawable(self.name, self.color, self.group_id,
        rotate_connector_flags(self.connector_flags))
  def _setup_menu(self, parent):
    present = set()
    robot_power_needed = True
    for drawable in self.board.get_drawables():
      if isinstance(drawable, Robot_IO_Drawable) and (drawable.group_id ==
          self.group_id):
        present.add(drawable.name)
      elif isinstance(drawable, Robot_Power_Drawable) and (drawable.group_id ==
          self.group_id):
        robot_power_needed = False
    if robot_power_needed or len(present) < 5:
      menu = Menu(parent, tearoff=0)
      def readd():
        n = 0
        if robot_power_needed:
          self.board.add_drawable(Robot_Power_Drawable(self.color,
              self.group_id), self.offset)
          n += 1
        for name in ['Ai1', 'Ai2', 'Ai3', 'Ai4', 'Vo']:
          if name not in present:
            self.board.add_drawable(Robot_IO_Drawable(name, self.color,
                self.group_id), self.offset)
            n += 1
        if n > 1:
          self.board._action_history.combine_last_n(n)
      menu.add_command(label='Re-add Missing Parts', command=readd)
      return menu
  def on_right_click(self, event):
    m = self._setup_menu(event.widget)
    if m is not None:
      m.tk_popup(event.x_root, event.y_root)
  def add_to_menu(self, menu):
    m = self._setup_menu(menu)
    if m is not None:
      menu.add_cascade(label='Robot I/O', menu=m)
      return menu.index('Robot I/O')
  def serialize(self, offset):
    return 'Robot_IO %s %s %s %d %s' % (self.name, self.color, self.group_id,
        self.connector_flags, str(offset))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Robot_IO (.+) (.+) %s %s %s' % (RE_INT, RE_INT, RE_INT_PAIR),
        item_str)
    if m:
      name, color = m.groups()[:2]
      group_id, connectors, ox, oy = map(int, m.groups()[2:])
      board.add_drawable(Robot_IO_Drawable(name, color, group_id, connectors),
          (ox, oy))
      return True
    return False

class Robot_Connector_Drawable(Pin_Drawable):
  """
  Drawable that, when clicked, spawns the drawables for items on the robot
      connector (i.e. Robot_Power_Drawable and 5 Robot_IO_Drawables, 4 input and
      1 output).
  """
  def __init__(self):
    Pin_Drawable.__init__(self, 'Robot', ROBOT_COLOR, ROBOT_SIZE, ROBOT_SIZE)

class Simulate_Run_Drawable(Run_Drawable):
  """
  Drawable to surve as a button to simulate circuit.
  """
  def __init__(self):
    Run_Drawable.__init__(self, SIMULATE, 80)

class Proto_Board_Run_Drawable(Run_Drawable):
  """
  Drawable to surve as button to display proto board layout.
  """
  def __init__(self):
    Run_Drawable.__init__(self, PROTO_BOARD, 80)
