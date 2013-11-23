"""
Utility methods.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import RESISTOR_FILL
from constants import RESISTOR_NUM_ZIG_ZAGS
from constants import RESISTOR_OUTLINE
from constants import RESISTANCE_SUFFIX

def draw_resistor_zig_zags(canvas, ox, oy, w, h):
  """
  Draws resistor zig zags on the given |canvas| at the given offset (|ox|,
      |oy|). The width |w| and height |h| are used to determine orientation.
  Returns a set containing the canvas ids of the lines used to draw the zig
      zag.
  """
  parts = set()
  parts.add(canvas.create_rectangle(ox, oy, ox + w, oy + h, fill=RESISTOR_FILL,
      outline=RESISTOR_OUTLINE))
  if w > h: # horizontal
    s = w / (2 * RESISTOR_NUM_ZIG_ZAGS)
    parts.add(canvas.create_line(ox, oy + h / 2, ox + s, oy))
    for i in xrange(1, RESISTOR_NUM_ZIG_ZAGS):
      parts.add(canvas.create_line(ox + (2 * i - 1) * s, oy, ox + 2 * i * s,
          oy + h))
      parts.add(canvas.create_line(ox + (2 * i + 1) * s, oy, ox + 2 * i * s,
          oy + h))
    parts.add(canvas.create_line(ox + w, oy  + h / 2, ox + w - s, oy))
  else: # vertical
    s = h / (2 * RESISTOR_NUM_ZIG_ZAGS)
    parts.add(canvas.create_line(ox + w / 2, oy, ox + w, oy + s))
    for i in xrange(1, RESISTOR_NUM_ZIG_ZAGS):
      parts.add(canvas.create_line(ox, oy + 2 * i * s, ox + w,
          oy + (2 * i - 1) * s))
      parts.add(canvas.create_line(ox, oy + 2 * i * s, ox + w,
          oy + (2 * i + 1) * s))
    parts.add(canvas.create_line(ox + w / 2, oy + h, ox + w,
        oy + h - s))
  return parts

def resistance_from_string(s):
  """
  Returns a 3-tuple corresponding to the resistance encoded by |s|. Raises an
      exception with the appropriate message on failure.
  Credit to CMax.
  """
  orig = s
  s = s.replace(u'\u03a9', '')
  s = s.lower().replace(' ', '').replace('s', '').replace(',', '')
  kilo, mega, giga = s.find('kilo'), s.find('mega'), s.find('giga')
  s = s.replace('ohm', '').replace('kilo', '').replace('mega', '').replace(
      'giga', '')
  k, m, g = s.find('k'), s.find('m'), s.find('g')
  s = s.replace('o', '').replace('k', '').replace('m', '').replace(
      'g', '')
  try:
    n = float(s)
  except:
    raise Exception('Invalid resistance: %s' % orig)
  mul = max(1, 1e3 * (kilo > -1 or k > -1)) * max(1, 1e6 * (mega > -1 or
      m > -1)) * max(1, 1e9 * (giga > -1 or g > -1))
  n = n * mul
  if n >= 1e11:
    raise Exception('Resistance too large: %s' % orig)
  elif n < 1:
    raise Exception('Resistance too small: %s' % orig)
  e = 0
  while 10 ** (e + 1) <= n:
    e += 1
  coeff = n / (10 ** e)
  coeff = int(coeff * 10)
  if e == 0:
    return (0, coeff / 10, 0)
  else:
    return (coeff / 10, coeff % 10, e - 1)

def resistance_to_string(r):
  """
  Returns a string concisely representing the resistance 3-tuple |r|.
  Credit to CMax.
  """
  if r[0] == 0:
    # deal with small resistance
    value = str(r[1])
    if r[2] % 3 == 2:
      # indent
      value = '0.' + value[0]
  else:
    value = str(r[0]) + str(r[1])
    if r[2] % 3 == 2:
      # indent
      value = value[0] + '.' + value[1]
  value += RESISTANCE_SUFFIX[r[2]]
  return value
