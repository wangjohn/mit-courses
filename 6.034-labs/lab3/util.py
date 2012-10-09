from threading import Thread
from time import time
from connectfour import ConnectFourBoard
import tree_searcher

## Define 'INFINITY' and 'NEG_INFINITY'
try:
    INFINITY = float("infinity")
    NEG_INFINITY = float("-infinity")
except ValueError:                 # Windows doesn't support 'float("infinity")'.
    INFINITY = float(1e3000)       # However, '1e3000' will overflow and return
    NEG_INFINITY = float(-1e3000)  # the magic float Infinity value anyway.

class ContinuousThread(Thread):
    """
    A thread that runs a function continuously,
    with an incrementing 'depth' kwarg, until
    a specified timeout has been exceeded
    """

    def __init__(self, timeout=5, target=None, group=None, name=None, args=(), kwargs={}):
        """
        Store the various values that we use from the constructor args,
        then let the superclass's constructor do its thing
        """
        self._timeout = timeout
        self._target = target
        self._args = args
        self._kwargs = kwargs
        Thread.__init__(self, args=args, kwargs=kwargs, group=group, target=target, name=name)

    def run(self):
        """ Run until the specified time limit has been exceeded """
        depth = 1

        timeout = self._timeout**(1/2.0)  # Times grow exponentially, and we don't want to
                                          # start a new depth search when we won't have
                                          # enough time to finish it

        end_time = time() + timeout
        
        while time() < end_time:
            self._kwargs['depth'] = depth
            self._most_recent_val = self._target(*self._args, **self._kwargs)
            depth += 1

    def get_most_recent_val(self):
        """ Return the most-recent return value of the thread function """
        try:
            return self._most_recent_val
        except AttributeError:
            print "Error: You ran the search function for so short a time that it couldn't even come up with any answer at all!  Returning a random column choice..."
            import random
            return random.randint(0, 6)
    
def run_search_function(board, search_fn, eval_fn, timeout = 5):
    """
    Run the specified search function "search_fn" to increasing depths
    until "time" has expired; then return the most recent available return value

    "search_fn" must take the following arguments:
    board -- the ConnectFourBoard to search
    depth -- the depth to estimate to
    eval_fn -- the evaluation function to use to rank nodes

    "eval_fn" must take the following arguments:
    board -- the ConnectFourBoard to rank
    """

    eval_t = ContinuousThread(timeout=timeout, target=search_fn, kwargs={ 'board': board,
                                                                          'eval_fn': eval_fn })

    eval_t.setDaemon(True)
    eval_t.start()
    
    eval_t.join(timeout)

    # Note that the thread may not actually be done eating CPU cycles yet;
    # Python doesn't allow threads to be killed meaningfully...
    return int(eval_t.get_most_recent_val())


class memoize(object):
    """
    'Memoize' decorator.

    Caches a function's return values,
    so that it needn't compute output for the same input twice.

    Use as follows:
    @memoize
    def my_fn(stuff):
        # Do stuff
    """
    def __init__(self, fn):
        self.fn = fn
        self.memocache = {}

    def __call__(self, *args, **kwargs):
        memokey = ( args, tuple( sorted(kwargs.items()) ) )
        if memokey in self.memocache:
            return self.memocache[memokey]
        else:
            val = self.fn(*args, **kwargs)
            self.memocache[memokey] = val
            return val


class count_runs(object):
    """
    'Count Runs' decorator

    Counts how many times the decorated function has been invoked.

    Use as follows:
    @count_runs
    def my_fn(stuff):
        # Do stuff


    my_fn()
    my_fn()
    print my_fn.get_count()  # Prints '2'
    """

    def __init__(self, fn):
        self.fn = fn
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        self.fn(*args, **kwargs)

    def get_count(self):
        return self.count


    
# Some sample boards, useful for testing:
# Obvious win
WINNING_BOARD = ConnectFourBoard(board_array =
                                 ( ( 0,0,0,0,0,0,0 ),
                                   ( 0,0,0,0,0,0,0 ),
                                   ( 0,0,0,0,0,0,0 ),
                                   ( 0,1,0,0,0,0,0 ),
                                   ( 0,1,0,0,0,2,0 ),
                                   ( 0,1,0,0,2,2,0 ),
                                   ),
                                 current_player = 1)

# 2 can win, but 1 can win a lot more easily
BARELY_WINNING_BOARD = ConnectFourBoard(board_array =
                                        ( ( 0,0,0,0,0,0,0 ),
                                          ( 0,0,0,0,0,0,0 ),
                                          ( 0,0,0,0,0,0,0 ),
                                          ( 0,2,2,1,1,2,0 ),
                                          ( 0,2,1,2,1,2,0 ),
                                          ( 2,1,2,1,1,1,0 ),
                                          ),
                                        current_player = 2)

BASIC_STARTING_BOARD_1 = ConnectFourBoard(board_array =
                                          ( ( 0,0,0,0,0,0,0 ),
                                            ( 0,0,0,0,0,0,0 ),
                                            ( 0,0,0,0,0,0,0 ),
                                            ( 0,0,0,0,0,0,0 ),
                                            ( 0,0,0,0,0,0,0 ),
                                            ( 0,0,1,0,2,0,0 ),
                                            ),
                                          current_player = 1)

BASIC_STARTING_BOARD_2 = ConnectFourBoard(board_array =
                                          ( ( 0,0,0,0,0,0,0 ),
                                            ( 0,0,0,0,0,0,0 ),
                                            ( 0,0,0,0,0,0,0 ),
                                            ( 0,0,0,0,0,0,0 ),
                                            ( 0,0,2,0,0,0,0 ),
                                            ( 0,0,1,0,0,0,0 ),
                                            ),
                                          current_player = 1)

# Generic board
BASIC_BOARD = ConnectFourBoard()

TEST_TREE_1 = tree_searcher.make_tree(("A", None,
                                       ("B", None,
                                        ("C", None,
                                         ("D", 2),
                                         ("E", 2)),
                                        ("F", None,
                                         ("G", 0),
                                         ("H", 4))
                                        ),
                                       ("I", None,
                                        ("J", None,
                                         ("K", 6),
                                         ("L", 8)),
                                        ("M", None,
                                         ("N", 4),
                                         ("O", 6))
                                        )
                                       ))

TEST_TREE_2 = tree_searcher.make_tree(("A", None,
                                       ("B", None,
                                        ("C", None,
                                         ("D", 6),
                                         ("E", 4)),
                                        ("F", None,
                                         ("G", 8),
                                         ("H", 6))
                                        ),
                                       ("I", None,
                                        ("J", None,
                                         ("K", 4),
                                         ("L", 0)),
                                        ("M", None,
                                         ("N", 2),
                                         ("O", 2))
                                        )
                                       ))

TEST_TREE_3 = tree_searcher.make_tree(("A", None,
                                       ("B", None,
                                        ("E", None,
                                         ("K", 8),
                                         ("L", 2)),
                                        ("F", 6)
                                        ),
                                       ("C", None,
                                        ("G", None,
                                         ("M", None,
                                          ("S", 4),
                                          ("T", 5)),
                                         ("N", 3)),
                                        ("H", None,
                                         ("O", 9),
                                         ("P", None,
                                          ("U", 10),
                                          ("V", 8))
                                         ),
                                        ),
                                       ("D", None,
                                        ("I", 1),
                                        ("J", None,
                                         ("Q", None,
                                          ("W", 7),
                                          ("X", 12)),
                                         ("K", None,
                                          ("Y", 11),
                                          ("Z", 15)
                                          ),
                                         )
                                        )
                                       ))



