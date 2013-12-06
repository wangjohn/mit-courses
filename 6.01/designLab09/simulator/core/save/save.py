"""
Methods to save and open boards.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import DEBUG
from constants import OPEN_FILE_TITLE
from constants import REQUEST_SAVE_MESSAGE
from constants import REQUEST_SAVE_TITLE
from constants import SAVE_AS_TITLE
from core.gui.board import Board
from core.gui.components import Wire
from os.path import isfile
from tkFileDialog import askopenfilename
from tkMessageBox import askquestion
from tkMessageBox import CANCEL
from tkMessageBox import YESNOCANCEL
from tkFileDialog import asksaveasfilename
from util import strip_dir
from util import strip_file_name

def get_board_rep(board):
  """
  Returns a string representing the content of the given |board|.
  Note that the order (i.e. Drawables then Wires) is important to how the rest
      of the methods here behave.
  """
  assert isinstance(board, Board), 'board must be a Board'
  rep = []
  # record all drawables on the board
  for drawable in board.get_drawables():
    rep.append(drawable.serialize(board.get_drawable_offset(drawable)))
  # record all wires on the board
  rep.extend(map(Wire.serialize, reduce(set.union, (drawable.wires() for
      drawable in board.get_drawables()), set())))
  # delimit with line breaks
  return '\n'.join(rep)

def save_board(board, file_name, file_type, file_extension):
  """
  Saves the given |board|. If the given |file_name| is not valid, asks the user
      for a new file name of with given |file_extension|. |file_type| is a
      description of the intended type of file to help the user.
  Returns the file name that was used to save the board.
  """
  assert isinstance(board, Board), 'board must be a Board'
  if not file_name or not file_name.endswith(file_extension):
    # if valid file name is not provided, ask for one
    file_name = asksaveasfilename(title=SAVE_AS_TITLE,
        filetypes=[('%s files' % file_type, file_extension)])
    board.reset_cursor_state()
    # ensure extension is tagged
    if file_name and not file_name.endswith(file_extension):
      file_name += file_extension
  if file_name:
    # write serialized board into file
    save_file = open(file_name, 'w')
    save_file.write(get_board_rep(board))
    save_file.close()
  return file_name

def request_save_board():
  """
  Presents a pop-up window asking the user whether to save the file. Returns
      True if the user responds yes, False otherwise.
  """
  return askquestion(title=REQUEST_SAVE_TITLE, message=REQUEST_SAVE_MESSAGE,
      type=YESNOCANCEL, default=CANCEL)

def open_board_from_file(board, file_name, deserializers, file_extension):
  """
  Reads the given file and puts the content on |board| after clearing it. The
      content of the file is determined using the given |deserializers|. The
      requirements on the |file_name| are that it be an existing file and it
      have the given |file_extension|. Returns True on success, and False on
      failure.
  """
  if not isfile(file_name) or not file_name.endswith(file_extension):
    return False
  # reset board cursor state
  board.reset_cursor_state()
  # clear board
  board.clear()
  # populate board with file content
  board_file = open(file_name, 'r')
  for line in board_file:
    for deserializer in deserializers:
      if deserializer.deserialize(line, board):
        break
    else:
      if DEBUG:
        print 'Could not deserialize:', line
  board_file.close()
  board.reset()
  return True

def get_board_file_name(current_file_name, file_type, file_extension):
  """
  Pops up a window to request a file name. |current_file_name| is the path for
      the board currently open, it is used to suggest what new file to open.
      |file_type| and |file_extension| are used to filter the types of files.
      Returns the name of the file that was openned, or '' on cancel.
  """
  return askopenfilename(title=OPEN_FILE_TITLE,
      filetypes=[('%s files' % file_type, file_extension)],
      initialfile=strip_file_name(current_file_name),
      initialdir=strip_dir(current_file_name))
