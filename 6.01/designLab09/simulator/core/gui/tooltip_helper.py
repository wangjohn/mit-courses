"""
Utility to show tooltips on Tkinter Canvases.
Credit to http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import TOOLTIP_BACKGROUND
from constants import DEFAULT_FONT
from Tkinter import Label
from Tkinter import LEFT
from Tkinter import SOLID
from Tkinter import TclError
from Tkinter import Toplevel

class Tooltip_Helper:
  """
  Class to help show tooltips on Tkinter Canvases.
  """
  def __init__(self, canvas):
    """
    |canvas|: the canvas on which tooltips will be shown.
    """
    self._canvas = canvas
    self._tip = None
  def show_tooltip(self, x, y, text, background=TOOLTIP_BACKGROUND):
    """
    Shows a tooltip containing the given |text| close to the point (|x|, |y|) on
        the canvas.
    """
    x += self._canvas.winfo_rootx() + 10
    y += self._canvas.winfo_rooty() + 10
    geometry = '+%d+%d' % (x, y)
    if not self._tip:
      self._tip = Toplevel(self._canvas)
      self._tip.wm_overrideredirect(1)
      self._tip.wm_geometry(geometry)
      try:
        # for Mac OS
        self._tip.tk.call('::tk::unsupported::MacWindowStyle', 'style',
            self._tip._w, 'help', 'noActivates')
      except TclError:
        pass
      self.label = Label(self._tip, text=text, justify=LEFT,
          background=background, relief=SOLID, borderwidth=1, font=DEFAULT_FONT)
      self.label.pack()
    else:
      self._tip.geometry(geometry)
      self.label.config(text=text, background=background)
  def hide_tooltip(self):
    """
    Hides the previously added tooltip, if any.
    """
    if self._tip:
      self._tip.destroy()
      self._tip = None
