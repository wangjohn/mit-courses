import unicodedata
import sys

# Python 2.3 compatibiliy with sets
if not 'set' in globals():
    from sets import Set as set

def reverse(lst):
    """
    Reverses the order of a list.
    Very similar in functionality to the 'reversed()' builtin
    in newer versions of Python.  However, this function works
    with Python 2.3, and it returns a list rather than a generator.
    """
    retVal = list(lst)
    retVal.reverse()
    return retVal
    
def transpose(matrix):
    """ Transpose a matrix (defined as a list of lists, where each sub-list is a row in the matrix) """
    # This feels dirty somewhow; but it does do exactly what I want
    return zip(*matrix)

class InvalidMoveException(Exception):
    """ Exception raised if someone tries to make an invalid move """
    def __init__(self, column, board):
        """
        'board' is the board on which the movement took place;
        'column' is the column to which an addition was attempted
        """
        self._column = column
        self._board = board

    def __str__(self):
        return "InvalidMoveException: Can't add to column %s on board\n%s" % (str(self._column), str(self._board))

    def __unicode__(self):
        return "InvalidMoveException: Can't add to column %s on board\n%s" % (unicode(self._column), unicode(self._board))

    def __repr__(self):
        return self.__str__()


class NonexistentMoveException(Exception):
    """ Raised if you try to request information on a move that does not exist """
    pass

    
class ConnectFourBoard(object):
    """ Store a Connect-Four Board

    Connect-Four boards are intended to be immutable; please don't use
    Python wizardry to hack/mutate them.  (It won't give you an advantage;
    it'll just make the tester crash.)

    A Connect-Four board is a matrix, laid out as follows:

         0 1 2 3 4 5 6 7
       0 * * * * * * * *
       1 * * * * * * * *
       2 * * * * * * * *
       3 * * * * * * * *
       4 * * * * * * * *
       5 * * * * * * * *
       6 * * * * * * * *

    Board columns fill from the bottom (ie., row 6).
    """

    # The horizontal width of the board
    board_width = 7
    # The vertical height of the board
    board_height = 6

    # Map of board ID numbers to display characters used to print the board
    board_symbol_mapping = { 0: u' ',
                             1: unicodedata.lookup("WHITE SMILING FACE"),
                             2: unicodedata.lookup("BLACK SMILING FACE") }

    board_symbol_mapping_ascii = { 0: ' ',
                                   1: 'X',
                                   2: 'O' }
    
    def __init__(self, board_array = None, board_already_won = None, modified_column = None, current_player = 1, previous_move = -1):
        """ Create a new ConnectFourBoard

        If board_array is specified, it should be an MxN matrix of iterables
        (ideally tuples or lists), that will be used to describe the initial
        board state.  Each cell should be either '0', meaning unoccupied, or
        N for some integer N corresponding to a player number.

        board_already_won can optionally be set to either None, or to the id#
        of the player who has already won the board.
        If modified_column is specified, it should be the index of the last column
        that had a token dropped into it.
        Both board_already_won and modified_column are used as hints to the
        'is_win_for_player()' function.  It is fine to not specify them, but if they
        are specified, they must be correct.
        """
        if sys.stdout.encoding and 'UTF' not in sys.stdout.encoding: # If we don't support Unicode
            self.board_symbol_mapping = self.board_symbol_mapping_ascii
        
        if board_array == None:
            self._board_array = ( ( 0, ) * self.board_width , ) * self.board_height
        else:
            # Make sure we're storing tuples, so that they're immutable
            self._board_array = tuple( map(tuple, board_array) )

        #if board_already_won:
        #    self._is_win = board_already_won
        #elif modified_column:
        #    self._is_win = self._is_win_from_cell(self.get_height_of_column(modified_column), modified_column)
        #else:
        self._is_win = self.is_win()
            
        self.current_player = current_player

    def get_current_player_id(self):
        """ Return the id of the player who should be moving now """
        return self.current_player

    def get_other_player_id(self):
        """ Return the id of the opponent of the player who should be moving now """
        if self.get_current_player_id() == 1:
            return 2
        else:
            return 1
        
    def get_board_array(self):
        """ Return the board array representing this board (as a tuple of tuples) """
        return self._board_array

    def get_top_elt_in_column(self, column):
        """
        Get the id# of the player who put the topmost token in the specified column.
        Return 0 if the column is empty.
        """
        for row in self._board_array:
            if row[column] != 0:
                return row[column]

        return 0

    def get_height_of_column(self, column):
        """
        Return the index of the first cell in the specified column that is filled.
        Return ConnectFourBoard.board_height if the column is empty.
        """
        for i in xrange(self.board_height):
            if self._board_array[i][column] != 0:
                return i-1

        return self.board_height

    def get_cell(self, row, col):
        """
        Get the id# of the player owning the token in the specified cell.
        Return 0 if it is unclaimed.
        """
        return self._board_array[row][col]
    
    def do_move(self, column):
        """
        Execute the specified move as the specified player.
        Return a new board with the result.
        Raise 'InvalidMoveException' if the specified move is invalid.
        """
        player_id = self.get_current_player_id()

        if self.get_height_of_column(column) < 0:
            raise InvalidMoveException(column, self)

        new_board = list( transpose( self.get_board_array() ) )
        target_col = [ x for x in new_board[column] if x != 0 ]
        target_col = [0 for x in xrange(self.board_height - len(target_col) - 1) ] + [ player_id ] + target_col

        new_board[column] = target_col
        new_board = transpose(new_board)

        # Re-immutablize the board
        new_board = tuple( map(tuple, new_board) )

        return ConnectFourBoard(new_board, board_already_won=self.is_win(), modified_column=column, current_player = self.get_other_player_id())

    def _is_win_from_cell(self, row, col):
        """ Determines if there is a winning set of four connected nodes containing the specified cell """
        return ( self._max_length_from_cell(row, col) >= 4 )
        
    def _max_length_from_cell(self, row, col):
        """ Return the max-length chain containing this cell """
        return max( self._contig_vector_length(row, col, (1,1)) + self._contig_vector_length(row, col, (-1,-1)) + 1,
                    self._contig_vector_length(row, col, (1,0)) + self._contig_vector_length(row, col, (-1,0)) + 1,
                    self._contig_vector_length(row, col, (0,1)) + self._contig_vector_length(row, col, (0,-1)) + 1,
                    self._contig_vector_length(row, col, (-1,1)) + self._contig_vector_length(row, col, (1,-1)) + 1 )

    def _contig_vector_length(self, row, col, direction):
        """
        Starting in the specified cell and going a step of direction = (row_step, col_step),
        count how many consecutive cells are owned by the same player as the starting cell.
        """
        count = 0
        playerid = self.get_cell(row, col)

        while 0 <= row < self.board_height and 0 <= col < self.board_width and playerid == self.get_cell(row, col):
            row += direction[0]
            col += direction[1]
            count += 1

        return count - 1

    def longest_chain(self, playerid):
        """
        Returns the length of the longest chain of tokens controlled by this player,
        0 if the player has no tokens on the board
        """
        longest = 0
        for i in xrange(self.board_height):
            for j in xrange(self.board_width):
                if self.get_cell(i,j) == playerid:
                    longest = max( longest, self._max_length_from_cell(i,j) )

        return longest

    def _contig_vector_cells(self, row, col, direction):
        """
        Starting in the specified cell and going a step of direction = (row_step, col_step),
        count how many consecutive cells are owned by the same player as the starting cell.
        """
        retVal = []
        playerid = self.get_cell(row, col)

        while 0 <= row < self.board_height and 0 <= col < self.board_width and playerid == self.get_cell(row, col):
            retVal.append((row, col))
            row += direction[0]
            col += direction[1]

        return retVal[1:]

    def _chain_sets_from_cell(self, row, col):
        """ Return the max-length chain containing this cell """
        return [ tuple(x) for x in [
                reverse(self._contig_vector_cells(row, col, (1,1))) + [(row, col)] + self._contig_vector_cells(row, col, (-1,-1)),
                 reverse(self._contig_vector_cells(row, col, (1,0))) + [(row, col)] + self._contig_vector_cells(row, col, (-1,0)),
                reverse(self._contig_vector_cells(row, col, (0,1))) + [(row, col)] + self._contig_vector_cells(row, col, (0,-1)),
                reverse(self._contig_vector_cells(row, col, (-1,1))) + [(row, col)] + self._contig_vector_cells(row, col, (1,-1)) 
                 ] ]

    def chain_cells(self, playerid):
        """
        Returns a set of all cells on the board that are part of a chain controlled
        by the specified player.

        The return value will be a Python set containing tuples of coordinates.
        For example, a return value might look like:

        set([ ( (0,1),(0,2),(0,3) ), ( (0,1),(1,1) ) ])

        This would indicate a contiguous string of tokens from (0,1)-(0,3) and (0,1)-(1,1).

        The coordinates within a tuple are weakly ordered: any coordinates that are 
        adjacent in a tuple are also adjacent on the board.

        Note that single lone tokens are regarded as chains of length 1.  This is
        sometimes useful, but sometimes not; however, it's relatively easy to remove
        such elements via list comprehension or via the built-in Python 'filter' function
        as follows (for example):

        >>> my_big_chains = filter(lambda x: len(x) > 1, myBoard.chain_cells(playernum))

        Also recall that you can convert this set to a list as follows:

        >>> my_list = list( myBoard.chain_cells(playernum) )

        The return value is provided as a set because sets are unique and unordered,
        as is this collection of chains.
        """
        retVal = set()
        for i in xrange(self.board_height):
            for j in xrange(self.board_width):
                if self.get_cell(i,j) == playerid:
                    retVal.update( self._chain_sets_from_cell(i,j) )
                    
        return retVal
                    
        
    def is_win(self):
        """
        Return the id# of the player who has won this game.
        Return 0 if it has not yet been won.
        """
        #if hasattr(self, "_is_win"):
        #    return self._is_win
        #else:
        for i in xrange(self.board_height):
            for j in xrange(self.board_width):
                cell_player = self.get_cell(i,j)
                if cell_player != 0:
                    win = self._is_win_from_cell(i,j)
                    if win:
                        self._is_win = win
                        return cell_player

        return 0

    def is_game_over(self):
        """ Return True if the game has been won, False otherwise """
        return ( self.is_win() != 0 or self.is_tie() )

    def is_tie(self):
        """ Return true iff the game has reached a stalemate """
        return not 0 in self._board_array[0]

    def clone(self):
        """ Return a duplicate of this board object """
        return ConnectFourBoard(self._board_array, board_already_won=self._is_win, current_player = self.get_current_player_id())

    def num_tokens_on_board(self):
        """
        Returns the total number of tokens (for either player)
        currently on the board
        """
        tokens = 0

        for row in self._board_array:
            for col in row:
                if col != 0:
                    tokens += 1

        return tokens

    def __unicode__(self):
        """ Return a string representation of this board """
        retVal = [ u"  " + u' '.join([str(x) for x in range(self.board_width)]) ]
        retVal += [ unicode(i) + ' ' + u' '.join([self.board_symbol_mapping[x] for x in row]) for i, row in enumerate(self._board_array) ]
        return u'\n' + u'\n'.join(retVal) + u'\n'

    def __str__(self):
        """ Return a string representation of this board """
        retVal = [ "  " + ' '.join([str(x) for x in range(self.board_width)]) ]
        retVal += [ str(i) + ' ' + ' '.join([self.board_symbol_mapping_ascii[x] for x in row]) for i, row in enumerate(self._board_array) ]
        return '\n' + '\n'.join(retVal) + '\n'
        
    def __repr__(self):
        """ The string representation of a board in the Python shell """
        return self.__str__()

    def __hash__(self):
        """ Determine the hash key of a board.  The hash key must be the same on any two identical boards. """
        return self._board_array.__hash__()

    def __eq__(self, other):
        """ Determine whether two boards are equal. """
        return ( self.get_board_array() == other.get_board_array() )

    
class ConnectFourRunner(object):
    """ Runs a game of Connect Four.

    The rules of this Connect Four game are the same as those for the real Connect Four game:

    * The game is a two-player game.  Players take turns adding tokens to the board.
    * When a token is added to the board, it is added to a particular column.
      It "falls" to the unoccupied cell in the column with the largest index.
    * The game ends when one of the two players has four consecutive tokens in a row
      (either horizontally, vertically, or on 45-degree diagonals), or when the board
      is completely filled.  If the game ends with a player having four consecutive
      diagonal tokens, that player is the winner.

    The game runner is implemented via callbacks:  The two players specify callbacks to be 
    called when it's their turn.  The callback is passed two arguments, self and self.get_board().
    The function must return a value within the time specified (in seconds) by self.get_time_limit();
    otherwise the corresponding player will lose!

    The callback functions must return integers corresponding to the columns they want
    to drop a token into.
    """

    def __init__(self, player1_callback, player2_callback, board = ConnectFourBoard(), time_limit = 10):
        """ Create a new ConnectFourRunner.

        player1_callback and player2_callback are the callback functions for the two players.
        board is the initial board to start with, a generic ConnectFourBoard() by default.
        time_limit is the time (in seconds) allocated per player, 10 seconds by default.
        """
        self._board = board
        self._time_limit = time_limit     # timeout in seconds
        self.player1_callback = player1_callback
        self.player2_callback = player2_callback

    def get_board(self):
        """ Return the current game board """
        return self._board

    def get_time_limit(self):
        """ Return the time limit (in seconds) for callback functions for this runner """
        return self._time_limit

    def run_game(self, verbose=True):
        """ Run the test defined by this test runner.  Print and return the id of the winning player. """
        player1 = (self.player1_callback, 1, self._board.board_symbol_mapping[1])
        player2 = (self.player2_callback, 2, self._board.board_symbol_mapping[2])
        
        win_for_player = []

        while not win_for_player and not self._board.is_tie():            
            for callback, id, symbol in ( player1, player2 ):
                if verbose:
                    if sys.stdout.encoding and 'UTF' in sys.stdout.encoding:
                        print unicode(self._board)
                    else:
                        print str(self._board)

                has_moved = False

                while not has_moved:
                    try:
                        new_column = callback(self._board.clone())
                        print "Player %s (%s) puts a token in column %s" % (id, symbol, new_column)
                        self._board = self._board.do_move(new_column)
                        has_moved = True
                    except InvalidMoveException, e:
                        if sys.stdout.encoding and 'UTF' in sys.stdout.encoding:
                            print unicode(e)
                        else:
                            print str(e)
                            print "Illegal move attempted.  Please try again."
                            continue

                if self._board.is_game_over():
                    win_for_player = self._board.is_win()
                    break


        win_for_player = self._board.is_win()
                
        if win_for_player != 0 and self._board.is_tie():
            print "It's a tie!  No winner is declared."
            return 0
        else:
            self._do_gameend(win_for_player)
            return win_for_player

    def _do_gameend(self, winner):
        """ Someone won!  Handle this eventuality. """
        print "Win for %s!" % self._board.board_symbol_mapping[winner]
        if sys.stdout.encoding and 'UTF' in sys.stdout.encoding:
            print unicode(self._board)
        else:
            print str(self._board)


def human_player(board):
    """
    A callback that asks the user what to do
    """
    target = None

    while type(target) != int:
        target = raw_input("Pick a column #: --> ")
        try:
            target = int(target)
        except ValueError:
            print "Please specify an integer column number"

    return target

        
def run_game(player1, player2, board = ConnectFourBoard()):
    """ Run a game of Connect Four, with the two specified players """
    game = ConnectFourRunner(player1, player2, board=board)
    return game.run_game()
    
