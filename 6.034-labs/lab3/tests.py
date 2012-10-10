from connectfour import ConnectFourBoard
from tester import make_test, get_tests
from time import time
import tree_searcher

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

ANSWER1_getargs = "ANSWER1"

def ANSWER1_testanswer(val, original_val = None):
    return ( val == 3 )

make_test(type = 'VALUE',
          getargs = ANSWER1_getargs,
          testanswer = ANSWER1_testanswer,
          expected_val = "3",
          name = ANSWER1_getargs
          )

ANSWER2_getargs = "ANSWER2"

def ANSWER2_testanswer(val, original_val = None):
    return ( val == 2 )

make_test(type = 'VALUE',
          getargs = ANSWER2_getargs,
          testanswer = ANSWER2_testanswer,
          expected_val = "2",
          name = ANSWER2_getargs
          )

def run_test_search_1_getargs():
    return [ 'minimax', 'WINNING_BOARD', 2, 'focused_evaluate' ]

def run_test_search_1_testanswer(val, original_val = None):
    return ( val == 1 )

make_test(type = 'FUNCTION',
          getargs = run_test_search_1_getargs,
          testanswer = run_test_search_1_testanswer,
          expected_val = "1",
          name = 'run_test_search'
          )

def run_test_search_2_getargs():
    return [ 'minimax', 'BARELY_WINNING_BOARD', 2, 'focused_evaluate' ]

def run_test_search_2_testanswer(val, original_val = None):
    return ( val == 3 )

make_test(type = 'FUNCTION',
          getargs = run_test_search_1_getargs,
          testanswer = run_test_search_1_testanswer,
          expected_val = "3",
          name = 'run_test_search'
          )
    
def run_test_search_3_getargs():
    return [ 'alpha_beta_search', 'WINNING_BOARD', 2, 'focused_evaluate' ]

def run_test_search_3_testanswer(val, original_val = None):
    return ( val == 1 )

make_test(type = 'FUNCTION',
          getargs = run_test_search_3_getargs,
          testanswer = run_test_search_3_testanswer,
          expected_val = "1",
          name = 'run_test_search'
          )


#
# Test alpha beta search using the tree_search framework,
# see tree_search.py
#
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

TREE_1_EXPECTED_BEST_MOVE = "I"

def run_test_tree_search_1_getargs():
    return [ 'alpha_beta_search', 'TEST_TREE_1', 10 ]

def run_test_tree_search_1_testanswer(val, original_val = None):
    return ( val == TREE_1_EXPECTED_BEST_MOVE )

make_test(type = 'FUNCTION',
          getargs = run_test_tree_search_1_getargs,
          testanswer = run_test_tree_search_1_testanswer,
          expected_val = TREE_1_EXPECTED_BEST_MOVE,
          name = 'run_test_tree_search'
          )

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

TREE_2_EXPECTED_BEST_MOVE = "B"

def run_test_tree_search_2_getargs():
    return [ 'alpha_beta_search', 'TEST_TREE_2', 10 ]

def run_test_tree_search_2_testanswer(val, original_val = None):
    return ( val == TREE_2_EXPECTED_BEST_MOVE )

make_test(type = 'FUNCTION',
          getargs = run_test_tree_search_2_getargs,
          testanswer = run_test_tree_search_2_testanswer,
          expected_val = TREE_2_EXPECTED_BEST_MOVE,
          name = 'run_test_tree_search'
          )

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

TREE_3_EXPECTED_BEST_MOVE = "B"

def run_test_tree_search_3_getargs():
    return [ 'alpha_beta_search', 'TEST_TREE_3', 10 ]

def run_test_tree_search_3_testanswer(val, original_val = None):
    return ( val == TREE_3_EXPECTED_BEST_MOVE )

make_test(type = 'FUNCTION',
          getargs = run_test_tree_search_3_getargs,
          testanswer = run_test_tree_search_3_testanswer,
          expected_val = TREE_3_EXPECTED_BEST_MOVE,
          name = 'run_test_tree_search'
          )


def run_test_search_4_getargs():
    return [ 'alpha_beta_search', 'BARELY_WINNING_BOARD', 2, 'focused_evaluate' ]

def run_test_search_4_testanswer(val, original_val = None):
    return ( val == 3 )

make_test(type = 'FUNCTION',
          getargs = run_test_search_4_getargs,
          testanswer = run_test_search_4_testanswer,
          expected_val = "3",
          name = 'run_test_search'
          )

def run_test_search_5_getargs():
    return [ 'alpha_beta_search', 'WINNING_BOARD', 2, 'better_evaluate' ]

def run_test_search_5_testanswer(val, original_val = None):
    return ( val == 1 )

make_test(type = 'FUNCTION',
          getargs = run_test_search_5_getargs,
          testanswer = run_test_search_5_testanswer,
          expected_val = "1",
          name = 'run_test_search'
          )

def run_test_search_6_getargs():
    return [ 'alpha_beta_search', 'BARELY_WINNING_BOARD', 2, 'better_evaluate' ]

def run_test_search_6_testanswer(val, original_val = None):
    return ( val == 3 )

make_test(type = 'FUNCTION',
          getargs = run_test_search_6_getargs,
          testanswer = run_test_search_6_testanswer,
          expected_val = "3",
          name = 'run_test_search'
          )

TIME_DICT = { 'time': -1 }

def run_test_search_7_getargs():
    TIME_DICT['time'] = time()
    return [ 'alpha_beta_search', 'BASIC_BOARD', 6, 'basic_evaluate' ]

def run_test_search_7_testanswer(val, original_val = None):
    try:
        from tester.test import LabTestFunctionInstance
        from datetime import timedelta
        test = LabTestFunctionInstance.objects.filter(test_function__args_generator='run_test_search_7', test_function__lab__name='lab3').order_by('-id')[0]
        return ( test.starttime >  datetime.now() - timedelta(seconds=25) ) # Be slightly generous; there's added latency from HTTP
    except ImportError:
        return ( time() - TIME_DICT['time'] < 20.0 )

make_test(type = 'FUNCTION',
          getargs = run_test_search_7_getargs,
          testanswer = run_test_search_7_testanswer,
          expected_val = "Any legitimate column is ok; the purpose of this test is to confirm that the test ends in a reasonable amount of time",
          name = 'run_test_search'
          )

def run_test_game_1_getargs():
    return [ [ 'your_player', 'basic_player', 'BASIC_STARTING_BOARD_1' ],
             [ 'basic_player', 'your_player', 'BASIC_STARTING_BOARD_1' ],
             [ 'your_player', 'basic_player', 'BASIC_STARTING_BOARD_2' ],
             [ 'basic_player', 'your_player', 'BASIC_STARTING_BOARD_2' ] ]

def run_test_game_1_testanswer(val, original_val = None):
    wins = 0
    losses = 0
    
    if val[0] == 1:
        wins += 1
    elif val[0] == 2:
        losses += 1

    if val[1] == 2:
        wins += 1
    elif val[1] == 1:
        losses += 1

    if val[2] == 1:
        wins += 1
    elif val[2] == 2:
        losses += 1

    if val[3] == 2:
        wins += 1
    elif val[3] == 1:
        losses += 1
        
    return ( wins - losses >= 2 )

# Set this if-guard to False to temporarily disable this test.
if True:
    make_test(type = 'MULTIFUNCTION',
              getargs = run_test_game_1_getargs,
              testanswer = run_test_game_1_testanswer,
              expected_val = "You must win at least 2 more games than you lose to pass this test",
              name = 'run_test_game'
              )

COMPETE_getargs = "COMPETE"

def COMPETE_testanswer(val, original_val = None):
    return ( val in (True, False) )

make_test(type = 'VALUE',
          getargs = COMPETE_getargs,
          testanswer = COMPETE_testanswer,
          expected_val = "Either True or False is ok, but you have to specify one or the other",
          name = COMPETE_getargs
          )

HOW_MANY_HOURS_THIS_PSET_TOOK_getargs = "HOW_MANY_HOURS_THIS_PSET_TOOK"

def HOW_MANY_HOURS_THIS_PSET_TOOK_testanswer(val, original_val = None):
    return ( val != '' )

make_test(type = 'VALUE',
          getargs = HOW_MANY_HOURS_THIS_PSET_TOOK_getargs,
          testanswer = HOW_MANY_HOURS_THIS_PSET_TOOK_testanswer,
          expected_val = "[a number of hours]",
          name = HOW_MANY_HOURS_THIS_PSET_TOOK_getargs
          )

WHAT_I_FOUND_INTERESTING_getargs = "WHAT_I_FOUND_INTERESTING"

def WHAT_I_FOUND_INTERESTING_testanswer(val, original_val = None):
    return ( val != '' )

make_test(type = 'VALUE',
          getargs = WHAT_I_FOUND_INTERESTING_getargs,
          testanswer = WHAT_I_FOUND_INTERESTING_testanswer,
          expected_val = "[an interesting thing]",
          name = WHAT_I_FOUND_INTERESTING_getargs
          )

WHAT_I_FOUND_BORING_getargs = "WHAT_I_FOUND_BORING"

def WHAT_I_FOUND_BORING_testanswer(val, original_val = None):
    return ( val != '' )

make_test(type = 'VALUE',
          getargs = WHAT_I_FOUND_BORING_getargs,
          testanswer = WHAT_I_FOUND_BORING_testanswer,
          expected_val = "[a number of hours]",
          name = WHAT_I_FOUND_BORING_getargs
          )

