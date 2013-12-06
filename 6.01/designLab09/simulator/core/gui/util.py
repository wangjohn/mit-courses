"""
Utility methods.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import BOARD_GRID_SEPARATION
from constants import CONNECTOR_BOTTOM
from constants import CONNECTOR_CENTER
from constants import CONNECTOR_LEFT
from constants import CONNECTOR_RADIUS
from constants import CONNECTOR_RIGHT
from constants import CONNECTOR_TOP
from constants import CONNECTOR_WIDTH
from constants import DEFAULT_FONT
from constants import EDIT_TAG
from constants import WIRE_ARROW_LENGTH
from constants import WIRE_COLOR
from constants import WIRE_INTERSECT_MARKER_SIZE
from constants import WIRE_WIDTH
from core.math.line_segment_intersect import intersect
from math import atan2
from math import cos
from math import pi
from math import sin
from math import sqrt
from Tkinter import Canvas
from Tkinter import CURRENT
from Tkinter import END
from Tkinter import INSERT
from Tkinter import SEL_FIRST
from Tkinter import SEL_LAST

def create_editable_text(canvas, x, y, text='?', on_text_changed=lambda:None,
    font=DEFAULT_FONT):
  """
  Creates an edittable text box on the |canvas| centered at the given position
      (|x|, |y|) and containing the given |text| with the given |font|.
      |on_text_changed| is called whenever the text is changed, with two
      arguments: the old text, and the new text.
  Returns the canvas id of the text box.
  Credit to http://effbot.org/zone/editing-canvas-text-items.htm
  """
  assert isinstance(canvas, Canvas), 'canvas must be a Canvas'
  # create the text box
  text_box = canvas.create_text(x, y, text=text, font=font, tags=(EDIT_TAG,))
  def set_focus(event):
    """
    Focus text box. Selects all the text inside the text box.
    """
    canvas.focus_set()
    canvas.focus(text_box)
    canvas.select_from(CURRENT, 0)
    canvas.select_to(CURRENT, END)
  canvas.tag_bind(text_box, '<Double-Button-1>', set_focus)
  def handle_key(event):
    """
    Handle a key press when the text box is in focus.
    """
    text_before_key = canvas.itemcget(text_box, 'text')
    insert = canvas.index(text_box, INSERT)
    if event.keysym == 'BackSpace':
      if canvas.select_item():
        canvas.dchars(text_box, SEL_FIRST, SEL_LAST)
        canvas.select_clear()
      else:
        if insert > 0:
          canvas.dchars(text_box, insert - 1, insert - 1)
    elif event.keysym == 'Right':
      canvas.icursor(text_box, insert + 1)
      canvas.select_clear()
    elif event.keysym == 'Left':
      canvas.icursor(text_box, insert - 1)
      canvas.select_clear()
    elif event.keysym in ('Escape', 'Return'):
      canvas.select_clear()
      canvas.focus('')
    elif event.char >= ' ':
      # printable character
      if canvas.select_item():
        canvas.dchars(text_box, SEL_FIRST, SEL_LAST)
        canvas.select_clear()
      canvas.insert(text_box, 'insert', event.char)
    text_after_key = canvas.itemcget(text_box, 'text')
    # callback if text is changed
    if text_before_key != text_after_key:
      on_text_changed(text_before_key, text_after_key)
  canvas.tag_bind(text_box, '<Key>', handle_key)
  return text_box

def create_circle(canvas, x, y, r, *args, **kwargs):
  """
  Draws a circle of radius |r| centered at (|x|, |y|) on the |canvas|.
  Returns the canvas id of the circle.
  """
  return canvas.create_oval(x - r, y - r, x + r, y + r, *args, **kwargs)

def create_connector(canvas, x, y, fill, outline, active_width):
  """
  Draws a connector centered at (|x|, |y|) on the |canvas| and with the given
      |fill| and |outline| colors. |active_width| is the width of the outline
      when the cursor is over the connector.
  Returns the canvas id of the created object.
  """
  return create_circle(canvas, x, y, CONNECTOR_RADIUS, fill=fill,
      outline=outline, width=CONNECTOR_WIDTH, activewidth=active_width)

def create_wire(canvas, x1, y1, x2, y2, other_wires, directed=True,
    color=WIRE_COLOR):
  """
  Draws a piece of a wire on the |canvas| pointing from (|x1|, |y1|) to
      (|x2|, |y2|). The two end points must define a horizontal or vertical
      line. If the piece intersects any of the |other_wires|, marks the
      intersections. If |directed| is True, the drawn piece will have an arrow.
  Returns a list of the canvas ids of the lines the wire is composed of.
  """
  assert isinstance(canvas, Canvas), 'canvas must be a Canvas'
  assert x1 == x2 or y1 == y2, 'wire piece must be horizontal or vertical'
  parts = []
  if x1 == x2 and y1 == y2:
    return parts
  intersection_points = []
  for wire in other_wires:
    for i in xrange(len(wire.path) - 1):
      intersection = intersect(((x1, y1), (x2, y2)), (wire.path[i],
          wire.path[i + 1]))
      if intersection not in (False, 'collinear', (x1, y1), (x2, y2)):
        intersection_points.append(intersection)
  intersection_points.sort(key=lambda (x, y): (x - x1) / (x2 - x1) if x1 != x2
      else (y - y1) / (y2 - y1))
  last_point = (x1, y1)
  if intersection_points:
    h = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    dx = WIRE_INTERSECT_MARKER_SIZE * (x2 - x1) / h
    dy = WIRE_INTERSECT_MARKER_SIZE * (y2 - y1) / h
    for (x, y) in intersection_points:
      _x, _y = x - dx, y - dy
      x_, y_ = x + dx, y + dy
      xm, ym = _x + dx - sqrt(3) * dy, _y + sqrt(3) * dx + dy
      parts.append(canvas.create_line(last_point, (_x, _y), fill=color,
          width=WIRE_WIDTH))
      parts.append(canvas.create_line(_x, _y, xm, ym, x_, y_, fill=color,
          width=WIRE_WIDTH, smooth=True))
      last_point = (x_, y_)
  parts.append(canvas.create_line(last_point, (x2, y2), fill=color,
      width=WIRE_WIDTH))
  if directed:
    wire_angle = atan2(y2 - y1, x2 - x1)
    arrow_angle_1 = wire_angle + 3 * pi / 4
    parts.append(canvas.create_line(x2, y2, x2 + WIRE_ARROW_LENGTH *
        cos(arrow_angle_1), y2 + WIRE_ARROW_LENGTH * sin(arrow_angle_1),
        fill=color, width=WIRE_WIDTH))
    arrow_angle_2 = wire_angle + 5 * pi / 4
    parts.append(canvas.create_line(x2, y2, x2 + WIRE_ARROW_LENGTH *
        cos(arrow_angle_2), y2 + WIRE_ARROW_LENGTH * sin(arrow_angle_2),
        fill=color, width=WIRE_WIDTH))
  return parts

def point_inside_bbox(point, bbox):
  """
  |point|: a tuple of the form (x, y) indicating a point.
  |bbox|: a tuple of the form (x1, y1, x2, y2) indicating a bounding box.
  Returns True if |point| is inside the |bbox|, False otherwise.
  """
  x, y = point
  x1, y1, x2, y2 = bbox
  return x1 <= x <= x2 and y1 <= y <= y2

def dist(point1, point2):
  """
  |point1|, |point2|: tuples of the form (x, y) indicating points.
  Returns the distance between the two points.
  """
  x1, y1 = point1
  x2, y2 = point2
  return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def point_inside_circle(point, circle):
  """
  |point|: a tuple of the form (x, y) indicating a point.
  |circle|: a tuple of the form (x, y, r) where (x, y) is the center of the
      circle, and r is its radius.
  Returns True if the point is inside the circle, False otherwise.
  """
  cx, cy, r = circle
  return dist(point, (cx, cy)) <= r

def snap(coord):
  """
  Returns |coord| snapped to the closest board marker location.
  """
  return (((coord + BOARD_GRID_SEPARATION / 2) // BOARD_GRID_SEPARATION) *
      BOARD_GRID_SEPARATION)

def rotate_connector_flags(connector_flags):
  """
  Returns the flags that would result from rotationg the given
      |connector_flags| by 90 degrees clockwise.
  """
  new_flags = 0
  if connector_flags & CONNECTOR_CENTER:
    new_flags |= CONNECTOR_CENTER
  if connector_flags & CONNECTOR_TOP:
    new_flags |= CONNECTOR_RIGHT
  if connector_flags & CONNECTOR_RIGHT:
    new_flags |= CONNECTOR_BOTTOM
  if connector_flags & CONNECTOR_BOTTOM:
    new_flags |= CONNECTOR_LEFT
  if connector_flags & CONNECTOR_LEFT:
    new_flags |= CONNECTOR_TOP
  return new_flags

def wire_coverage(start, end):
  """
  Returns the set of the points on the board that would be covered by a wire
      going from point |start| to point |end|. |start| and |end| must define a
      horizontal or vertical line segment.
  """
  x1, y1 = start
  x2, y2 = end
  assert x1 == x2 or y1 == y2, 'segment must be horizontal or vertical'
  return set([(x, y) for x in xrange(min(x1, x2), max(x1, x2) + 1,
      BOARD_GRID_SEPARATION) for y in xrange(min(y1, y2), max(y1, y2) + 1,
      BOARD_GRID_SEPARATION)])

def path_coverage(path):
  """
  Returns the set of the points on the board covered by the given |path| of
      points. Each consecuitive pair of points in |path| must define a
      horizontal or vertical line segment.
  """
  coverage = set()
  for i in xrange(len(path) - 1):
    coverage |= wire_coverage(path[i], path[i + 1])
  return coverage

def split_path(path, point):
  """
  Splits the given |path| at the given |point| and returns the two resulting
      paths, the first of which ends at |point| and the second of which starts
      at |point|. Returns None if |point| is not on the given |path|.
  """
  for i in xrange(len(path) - 1):
    if point in wire_coverage(path[i], path[i + 1]):
      return path[:i + 1] + [point], [point] + path[i + 1:]

def wire_parts_from_path(canvas, path, other_wires, directed=False,
    color=WIRE_COLOR):
  """
  Returns the parts that result from drawing the given wire |path|.
  """
  parts = []
  for i in xrange(len(path) - 1):
    x1, y1 = path[i]
    x2, y2 = path[i + 1]
    parts.extend(create_wire(canvas, x1, y1, x2, y2, other_wires, directed,
        color))
  return parts
