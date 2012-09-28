# Fall 2012 6.034 Lab 2: Search

from search import *
from graphs import *
from tester import make_test, get_tests
from lab2 import bfs, dfs
import random
import time


### TEST 1 ###

ANSWER1_getargs = "ANSWER1"

def ANSWER1_testanswer(val, original_val = None):
    return ( val == False )

# If the search space is finite, and your heuristic estimates the distance
# to the goal, and you allow backtracking, then hill climbing will
# succeed.  Let us explore relaxing each criterion in turn.

# One way for hill climbing to fail is to run into local maxima.  In any
# search space, it is possible to be at a collection of nodes separated
# from the goal by a boundary region, where the scores of all the nodes in
# the boundary are lower than the scores of all the nodes within the
# collection, and the scores of all the nodes within the collection are
# lower than the score of the goal node.  This collection is called a
# local maximum.  If a hill climbing algorithm is exploring a local
# maximum, then it will keep choosing to explore that, rather than any
# node in the boundary region, because it does not want to go "downhill".
# If the local maximum is finite, it will eventually run out of nodes to
# explore.  If it is infinite, hill climbing will of course explore it
# indefinitely.

# Another common use of hill climbing techniques is where the score of the
# goal node is unknown.  In this case, even a finite local maximum will
# lead to a wrong answer: hill climbing will pick one of the nodes with
# the best score within the local maximum, which is still (by definition)
# not as high as the score of the actual goal node, the global maximum.

# Finally, without backtracking, hill climbing will take just one path,
# guaranteeing that it always goes uphill, but not necessarily up the right
# hill.  When it reaches a node from which it can only go downhill, then its
# answer depends on the second criterion: if the score of the goal node is
# known, then it can report failure explicitly; otherwise it may return a
# local maximum as its answer.


make_test(type = 'VALUE',
          getargs = ANSWER1_getargs,
          testanswer = ANSWER1_testanswer,
          expected_val = "False",
          name = ANSWER1_getargs
          )


### TEST 2 ###

ANSWER2_getargs = "ANSWER2"

def ANSWER2_testanswer(val, original_val = None):
    return ( val == False )

# Best first search will give an optimal path iff it has an admissible heuristic.

make_test(type = 'VALUE',
          getargs = ANSWER2_getargs,
          testanswer = ANSWER2_testanswer,
          expected_val = "False",
          name = ANSWER2_getargs
          )


### TEST 3 ###

ANSWER3_getargs = "ANSWER3"

# Hill climbing uses a heuristic to choose among nodes adjacent to the current
# node being explored.
# Best first search estimates "best" using the sum of the distance already
# travelled and the heuristic estimate of the distance remaining from the
# last node in any path.

def ANSWER3_testanswer(val, original_val = None):
    return ( val == True )

make_test(type = 'VALUE',
          getargs = ANSWER3_getargs,
          testanswer = ANSWER3_testanswer,
          expected_val = "True",
          name = ANSWER3_getargs
          )


### TEST 4 ###

ANSWER4_getargs = "ANSWER4"

# It goes by many names: extended list, extended set, visited set, etc. but
# by any name, keeping track of nodes which have already been extended is
# standard in A* search.

def ANSWER4_testanswer(val, original_val = None):
    return ( val == True )

make_test(type = 'VALUE',
          getargs = ANSWER4_getargs,
          testanswer = ANSWER4_testanswer,
          expected_val = "True",
          name = ANSWER4_getargs
          )


### TEST 5 ###

ANSWER5_getargs = "ANSWER5"

# Breadth first search explores all paths of length n before exploring any path
# of length n+1, and it will return as soon as a goal is found at the end of a
# path, so it cannot return a path with more nodes than another path to the goal.
# Note that this is guaranteed to be the cheapest path only if all of the edge
# costs are the same.

def ANSWER5_testanswer(val, original_val = None):
    return ( val == True )

make_test(type = 'VALUE',
          getargs = ANSWER5_getargs,
          testanswer = ANSWER5_testanswer,
          expected_val = "True",
          name = ANSWER5_getargs
          )


### TEST 6 ###

ANSWER6_getargs = "ANSWER6"

# Unlike best-first search, branch-and-bound uses only the cost travelled so far,
# not the estimated cost to the goal.

def ANSWER6_testanswer(val, original_val = None):
    return ( val == False )

make_test(type = 'VALUE',
          getargs = ANSWER6_getargs,
          testanswer = ANSWER6_testanswer,
          expected_val = "False",
          name = ANSWER6_getargs
          )

############ OPTIONAL WARM-UP: BFS and DFS ############

do_bfs = True
try:
    bfs(NEWGRAPH1, 'S', 'H')
except NotImplementedError:
    do_bfs = False

do_dfs = True
try:
    dfs(NEWGRAPH1, 'S', 'H')
except NotImplementedError:
    do_dfs = False

if do_bfs:

    ### TEST 7-optional ###

    def bfs_1_getargs():
        # (graph, start, goal, extended=None, queue=None)
        return [ NEWGRAPH1, 'S', 'H' ]

    def bfs_1_testanswer(val, original_val = None):
        if val and len(val) > 0 and isinstance(val[0], dict):
            raise Exception, "Error: Graph functions are supposed to return a list of node *names*, not node dictionaries!"

        return ( val and list(val) == list('SCDH') )

    make_test(type = 'FUNCTION',
              getargs = bfs_1_getargs,
              testanswer = bfs_1_testanswer,
              expected_val = list('SCDH'),
              name = 'bfs'
              )


    ### TEST 8-optional ###

    def bfs_2_getargs():
        return [ NEWGRAPH2, 'A', 'G' ]

    def bfs_2_testanswer(val, original_val = None):
        return ( val and list(val) == list('ASCDFG') )

    make_test(type = 'FUNCTION',
              getargs = bfs_2_getargs,
              testanswer = bfs_2_testanswer,
              expected_val = list('ASCDFG'),
              name = 'bfs'
              )


    ### TEST 9-optional ###

    def bfs_3_getargs():
        return [ NEWGRAPH3, 'S', 'S' ]

    def bfs_3_testanswer(val, original_val = None):
        return ( val and list(val) == list('S') )

    make_test(type = 'FUNCTION',
              getargs = bfs_3_getargs,
              testanswer = bfs_3_testanswer,
              expected_val = list('S'),
              name = 'bfs'
              )


    ### TEST 10-optional ###

    def bfs_4_getargs():
        return [ SAQG, 'S', 'G']

    def bfs_4_testanswer(val, original_val = None):
        return (val and list(val) == list("SG"))

    make_test(type = 'FUNCTION',
              getargs = bfs_4_getargs,
              testanswer = bfs_4_testanswer,
              expected_val = list("SG"),
              name = 'bfs')

if do_dfs:

    ### TEST 11-optional ###

    def dfs_1_getargs():
        return [ NEWGRAPH1, 'S', 'H' ]

    def dfs_1_testanswer(val, original_val = None):
        return ( NEWGRAPH1.is_valid_path(val) and 
                 len( NEWGRAPH1.get_connected_nodes(val[-1]) ) <= 1 )

    make_test(type = 'FUNCTION',
              getargs = dfs_1_getargs,
              testanswer = dfs_1_testanswer,
              expected_val = "A valid path along NEWGRAPH1",
              name = 'dfs'
              )


    ### TEST 12-optional ###

    def dfs_2_getargs():
        return [ NEWGRAPH2, 'A', 'G' ]

    def dfs_2_testanswer(val, original_val = None):
        return ( NEWGRAPH2.is_valid_path(val) and 
                 len( NEWGRAPH2.get_connected_nodes(val[-1]) ) <= 1 )

    make_test(type = 'FUNCTION',
              getargs = dfs_2_getargs,
              testanswer = dfs_2_testanswer,
              expected_val = "A valid path along NEWGRAPH1",
              name = 'dfs'
              )


    ### TEST 13-optional ###

    def dfs_3_getargs():
        return [ NEWGRAPH3, 'S', 'S' ]

    def dfs_3_testanswer(val, original_val = None):
        return ( NEWGRAPH3.is_valid_path(val) and 
                 len( NEWGRAPH3.get_connected_nodes(val[-1]) ) <= 1 )

    make_test(type = 'FUNCTION',
              getargs = dfs_3_getargs,
              testanswer = dfs_3_testanswer,
              expected_val = "A valid path along NEWGRAPH1",
              name = 'dfs'
              )


    ### TEST 14-optional ###

    def dfs_4_getargs():
        return [ SAQG, 'S', 'G']

    def dfs_4_testanswer(val, original_val = None):
        return (val and (list(val) == list("SQG") or 
                         list(val) == list("SAG") or 
                         list(val) == list("SG")))

    make_test(type = 'FUNCTION',
              getargs = dfs_4_getargs,
              testanswer = dfs_4_testanswer,
              expected_val = str(list("SQG"))+" or "+str(list("SAG")),
              name = 'dfs')


### TEST 7 ###

def path_length_1_getargs():
    return [ NEWGRAPH2, list('S') ]

def path_length_1_testanswer(val, original_val = None):
    return ( val == 0 )

make_test(type = 'FUNCTION',
          getargs = path_length_1_getargs,
          testanswer = path_length_1_testanswer,
          expected_val = 0,
          name = 'path_length'
          )


### TEST 8 ###

def path_length_2_getargs():
    return [ NEWGRAPH1, list('SASAS') ]

def path_length_2_testanswer(val, original_val = None):
    return ( val == 24 )

make_test(type = 'FUNCTION',
          getargs = path_length_2_getargs,
          testanswer = path_length_2_testanswer,
          expected_val = 24,
          name = 'path_length'
          )


### TEST 9 ###

def path_length_3_getargs():
    return [ NEWGRAPH2, list('HDCECSBSA') ]

def path_length_3_testanswer(val, original_val = None):
    return ( val == 32 )

make_test(type = 'FUNCTION',
          getargs = path_length_3_getargs,
          testanswer = path_length_3_testanswer,
          expected_val = 32,
          name = 'path_length'
          )


### TEST 10 ###

def hill_climbing_1_getargs():
    return [ NEWGRAPH1, 'S', 'G' ]

def hill_climbing_1_testanswer(val, original_val = None):
    return ( val == list('SABDCEG') )

make_test(type = 'FUNCTION',
          getargs = hill_climbing_1_getargs,
          testanswer = hill_climbing_1_testanswer,
          expected_val = list('SABDCEG'),
          name = 'hill_climbing'
          )


### TEST 11 ###

def hill_climbing_2_getargs():
    return [ NEWGRAPH1, 'F', 'G' ]

def hill_climbing_2_testanswer(val, original_val = None):
    return ( val == list('FBDCEG') )

make_test(type = 'FUNCTION',
          getargs = hill_climbing_2_getargs,
          testanswer = hill_climbing_2_testanswer,
          expected_val = list('FBDCEG'),
          name = 'hill_climbing'
          )


### TEST 12 ###

def hill_climbing_3_getargs():
    return [ NEWGRAPH1, 'H', 'G' ]

def hill_climbing_3_testanswer(val, original_val = None):
    return ( val == list('HDBASCEG') )

make_test(type = 'FUNCTION',
          getargs = hill_climbing_3_getargs,
          testanswer = hill_climbing_3_testanswer,
          expected_val = list('HDBASCEG'),
          name = 'hill_climbing'
          )


### TEST 13 ###

def hill_climbing_4_getargs():
    return [ NEWGRAPH2, 'G', 'H' ]

def hill_climbing_4_testanswer(val, original_val = None):
    return ( val == list('GFDH') )

make_test(type = 'FUNCTION',
          getargs = hill_climbing_4_getargs,
          testanswer = hill_climbing_4_testanswer,
          expected_val = list('GFDH'),
          name = 'hill_climbing'
          )


### TEST 14 ###

def hill_climbing_5_getargs():
    return [ NEWGRAPH2, 'E', 'A' ]

def hill_climbing_5_testanswer(val, original_val = None):
    return ( val == list('ECSA') )

make_test(type = 'FUNCTION',
          getargs = hill_climbing_5_getargs,
          testanswer = hill_climbing_5_testanswer,
          expected_val = list('ECSA'),
          name = 'hill_climbing'
          )


### TEST 15 ###

def exp_graph(depth):
    g = Graph(["1"])
    goal = 1
    for d in range(depth):
        nodeids = range(2**(d+1), 2**(d+2))
        goal = random.choice(nodeids)
        for nodeid in nodeids:
            parent = nodeid/2 # intentional integer division
            g.add_edge(str(parent), str(nodeid), 1)
    best_path = [goal]
    while goal > 0:
        goal = goal/2 # intentional integer division
        best_path.append(goal)
    goal = best_path[0]

    for nodeid in range(1,2**(depth+1)):
        distance = 0
        shared_parent = nodeid
        while shared_parent not in best_path:
            distance += 1
            shared_parent = shared_parent / 2 # intentional integer division
        g.set_heuristic(str(nodeid), str(goal), distance+best_path.index(shared_parent))
    return g

hill_climbing_test_6_graph = exp_graph(10)
hill_climbing_test_6_goal = hill_climbing_test_6_graph.heuristic.keys()[0]
hill_climbing_timing = {'START': 0}

def hill_climbing_6_getargs():
    hill_climbing_timing["START"] = time.time()
    return [hill_climbing_test_6_graph, "1", hill_climbing_test_6_goal]

def hill_climbing_6_testanswer(val, original_val = None):
    elapsed = time.time() - hill_climbing_timing["START"]
    return ( elapsed < 5 and val[-1] == hill_climbing_test_6_goal)

make_test(type = 'FUNCTION',
          getargs = hill_climbing_6_getargs,
          testanswer = hill_climbing_6_testanswer,
          expected_val = ("hill climbing to take less than one second and get to %s"
                          % hill_climbing_test_6_goal),
          name = 'hill_climbing'
          )


### TEST 16 ###

def beam_search_1_getargs():
    return [ NEWGRAPH1, 'S', 'G', 2 ]

beam_search_1_answer = list('')

def beam_search_1_testanswer(val, original_val = None):
    return ( val == beam_search_1_answer )

make_test(type = 'FUNCTION',
          getargs = beam_search_1_getargs,
          testanswer = beam_search_1_testanswer,
          expected_val = beam_search_1_answer,
          name = 'beam_search',
          )


### TEST 17 ###

def beam_search_1_beam_10_getargs():
    return [ NEWGRAPH1, 'S', 'G', 10 ]

beam_search_1_beam_10_answer = list('SCEG')

def beam_search_1_beam_10_testanswer(val, original_val = None):
    return ( val == beam_search_1_beam_10_answer )

make_test(type = 'FUNCTION',
          getargs = beam_search_1_beam_10_getargs,
          testanswer = beam_search_1_beam_10_testanswer,
          expected_val = beam_search_1_beam_10_answer,
          name = 'beam_search',
          )


### TEST 18 ###

def beam_search_2_getargs():
    return [ NEWGRAPH1, 'F', 'G', 2 ]

beam_search_2_answer = list('FBASCEG')
def beam_search_2_testanswer(val, original_val = None):
    return ( val == beam_search_2_answer )

make_test(type = 'FUNCTION',
          getargs = beam_search_2_getargs,
          testanswer = beam_search_2_testanswer,
          expected_val = beam_search_2_answer,
          name = 'beam_search',
          )


### TEST 19 ###

def beam_search_2_beam_10_getargs():
    return [ NEWGRAPH1, 'F', 'G', 10 ]
beam_search_2_beam_10_answer = list('FBDEG')
def beam_search_2_beam_10_testanswer(val, original_val = None):
    return ( val == beam_search_2_beam_10_answer )

make_test(type = 'FUNCTION',
          getargs = beam_search_2_beam_10_getargs,
          testanswer = beam_search_2_beam_10_testanswer,
          expected_val = beam_search_2_beam_10_answer,
          name = 'beam_search',
          )


### TEST 20 ###

def beam_search_3_beam_2_getargs():
    return [ NEWGRAPH2, 'S', 'G', 2 ]

beam_search_3_beam_2_answer = list('')

def beam_search_3_beam_2_testanswer(val, original_val = None):
    return ( val == beam_search_3_beam_2_answer )

make_test(type = 'FUNCTION',
          getargs = beam_search_3_beam_2_getargs,
          testanswer = beam_search_3_beam_2_testanswer,
          expected_val = beam_search_3_beam_2_answer,
          name = 'beam_search',
          )


### TEST 21 ###

def beam_search_3_beam_5_getargs():
    return [ NEWGRAPH2, 'S', 'G', 5 ]

beam_search_3_beam_5_answer = list('SCDFG')

def beam_search_3_beam_5_testanswer(val, original_val = None):
    return ( val == beam_search_3_beam_5_answer )

make_test(type = 'FUNCTION',
          getargs = beam_search_3_beam_5_getargs,
          testanswer = beam_search_3_beam_5_testanswer,
          expected_val = beam_search_3_beam_5_answer,
          name = 'beam_search',
          )


### TEST 22 ###

def branch_and_bound_1_getargs():
    return [ NEWGRAPH1, 'S', 'G' ]

def branch_and_bound_1_testanswer(val, original_val = None):
    return ( val == list('SCEG') )

make_test(type = 'FUNCTION',
          getargs = branch_and_bound_1_getargs,
          testanswer = branch_and_bound_1_testanswer,
          expected_val = list('SCEG'),
          name = 'branch_and_bound'
          )


### TEST 23 ###

def branch_and_bound_2_getargs():
    return [ NEWGRAPH1, 'S', 'D' ]

def branch_and_bound_2_testanswer(val, original_val = None):
    return ( val == list('SCD') )

make_test(type = 'FUNCTION',
          getargs = branch_and_bound_2_getargs,
          testanswer = branch_and_bound_2_testanswer,
          expected_val = list('SCD'),
          name = 'branch_and_bound'
          )


### TEST 24 ###

def branch_and_bound_6_getargs():
    return [NEWGRAPH4, "S", "T"]

def branch_and_bound_6_testanswer(val, original_val=None):
    return (val and list(val) == list("SBFHKT"))
            
make_test(type = 'FUNCTION_ENCODED_ARGS',
          getargs = branch_and_bound_6_getargs,
          testanswer = branch_and_bound_6_testanswer,
          expected_val = "correct path for the quiz search problem",
          name = 'branch_and_bound'
          )


### TEST 25 ###

def a_star_1_getargs():
    return [ NEWGRAPH3, 'S', 'S' ]

def a_star_1_testanswer(val, original_val = None):
    return ( list(val) == list('S') )

make_test(type = 'FUNCTION',
          getargs = a_star_1_getargs,
          testanswer = a_star_1_testanswer,
          expected_val = list('S'),
          name = 'a_star'
          )


### TEST 26 ###

def a_star_2_getargs():
    return [ NEWGRAPH1, 'S', 'G' ]

def a_star_2_testanswer(val, original_val = None):
    return ( list(val) == list('SCEG') )

make_test(type = 'FUNCTION',
          getargs = a_star_2_getargs,
          testanswer = a_star_2_testanswer,
          expected_val = list('SCEG'),
          name = 'a_star'
          )


### TEST 27 ###

def a_star_3_getargs():
    return [ NEWGRAPH2, 'S', 'G' ]

def a_star_3_testanswer(val, original_val = None):
    return ( list(val) == list('SCDFG') )

make_test(type = 'FUNCTION',
          getargs = a_star_3_getargs,
          testanswer = a_star_3_testanswer,
          expected_val = list('SCDFG'),
          name = 'a_star'
          )


### TEST 28 ###

def a_star_4_getargs():
    return [ NEWGRAPH2, 'E', 'G' ]

def a_star_4_testanswer(val, original_val = None):
    return ( list(val) == list('ECDFG') )

make_test(type = 'FUNCTION',
          getargs = a_star_4_getargs,
          testanswer = a_star_4_testanswer,
          expected_val = list('ECDFG'),
          name = 'a_star'
          )


### TEST 29 ###

a_star_test_5_graph = exp_graph(11)
a_star_test_5_goal = a_star_test_5_graph.heuristic.keys()[0]
a_star_timing = {'START': 0}

def a_star_5_getargs():
    a_star_timing["START"] = time.time()
    return [a_star_test_5_graph, "1", a_star_test_5_goal]

def a_star_5_testanswer(val, original_val = None):
    elapsed = time.time() - a_star_timing["START"]
    return ( elapsed < 1 and val[-1] == a_star_test_5_goal)

make_test(type = 'FUNCTION',
          getargs = a_star_5_getargs,
          testanswer = a_star_5_testanswer,
          expected_val = ("a_star to take less than one second and get to %s"
                          % a_star_test_5_goal),
          name = 'a_star'
          )


### TEST 30 ###

def a_star_test_6_getargs():
    return [NEWGRAPH4, "S", "T"]

def a_star_test_6_testanswer(val, original_val=None):
    return (list(val) == list("SBCJLT"))
            
make_test(type = 'FUNCTION_ENCODED_ARGS',
          getargs = a_star_test_6_getargs,
          testanswer = a_star_test_6_testanswer,
          expected_val = "correct path for the quiz search problem",
          name = 'a_star'
          )


### TEST 31 ###

def a_star_7_getargs():
    return [AGRAPH, "S", "G"]

def a_star_7_testanswer(val, original_val=None):
    return (val and list(val) == list('SACG'))
            
make_test(type = 'FUNCTION',
          getargs = a_star_7_getargs,
          testanswer = a_star_7_testanswer,
          expected_val = list('SACG'),
          name = 'a_star'
          )
  

### TEST 32 ###

def is_admissible_1_getargs():
    return [ NEWGRAPH1, "H" ]

def is_admissible_1_testanswer(val, original_val = None):
    return False == bool(val)

make_test(type='FUNCTION',
          getargs = is_admissible_1_getargs,
          testanswer = is_admissible_1_testanswer,
          expected_val = 'False for NEWGRAPH1/H',
          name = 'is_admissible')


### TEST 33 ###

def is_admissible_2_getargs():
    return [ NEWGRAPH1, "A" ]

def is_admissible_2_testanswer(val, original_val = None):
    return True == bool(val)

make_test(type='FUNCTION',
          getargs = is_admissible_2_getargs,
          testanswer = is_admissible_2_testanswer,
          expected_val = 'True for NEWGRAPH1/A',
          name = 'is_admissible')


### TEST 34 ###

def is_admissible_3_getargs():
    return [ NEWGRAPH1, "C" ]

def is_admissible_3_testanswer(val, original_val = None):
    return True == bool(val)

make_test(type='FUNCTION',
          getargs = is_admissible_3_getargs,
          testanswer = is_admissible_3_testanswer,
          expected_val = 'True for NEWGRAPH1/C',
          name = 'is_admissible')


### TEST 35 ###

def is_admissible_4_getargs():
    return [ NEWGRAPH1, "D" ]

def is_admissible_4_testanswer(val, original_val = None):
    return False == bool(val)

make_test(type='FUNCTION',
          getargs = is_admissible_4_getargs,
          testanswer = is_admissible_4_testanswer,
          expected_val = 'False for NEWGRAPH1/D',
          name = 'is_admissible')


### TEST 36 ###

def is_admissible_5_getargs():
    return [ NEWGRAPH1, "E" ]

def is_admissible_5_testanswer(val, original_val = None):
    return True == bool(val)

make_test(type='FUNCTION',
          getargs = is_admissible_5_getargs,
          testanswer = is_admissible_5_testanswer,
          expected_val = 'True for NEWGRAPH1/E',
          name = 'is_admissible')


### TEST 37 ###

def is_consistent_1_getargs():
    return [ NEWGRAPH1, "H" ]

def is_consistent_1_testanswer(val, original_val = None):
    return False == bool(val)

make_test(type='FUNCTION',
          getargs = is_consistent_1_getargs,
          testanswer = is_consistent_1_testanswer,
          expected_val = 'False for NEWGRAPH1/H',
          name = 'is_consistent')


### TEST 38 ###

def is_consistent_2_getargs():
    return [ NEWGRAPH1, "A" ]

def is_consistent_2_testanswer(val, original_val = None):
    return False == bool(val)

make_test(type='FUNCTION',
          getargs = is_consistent_2_getargs,
          testanswer = is_consistent_2_testanswer,
          expected_val = 'False for NEWGRAPH1/A',
          name = 'is_consistent')


### TEST 39 ###

def is_consistent_3_getargs():
    return [ NEWGRAPH1, "C" ]

def is_consistent_3_testanswer(val, original_val = None):
    return True == bool(val)

make_test(type='FUNCTION',
          getargs = is_consistent_3_getargs,
          testanswer = is_consistent_3_testanswer,
          expected_val = 'True for NEWGRAPH1/C',
          name = 'is_consistent')


### TEST 40 ###

def is_consistent_4_getargs():
    return [ NEWGRAPH1, "D" ]

def is_consistent_4_testanswer(val, original_val = None):
    return False == bool(val)

make_test(type='FUNCTION',
          getargs = is_consistent_4_getargs,
          testanswer = is_consistent_4_testanswer,
          expected_val = 'False for NEWGRAPH1/D',
          name = 'is_consistent')


### TEST 41 ###

def is_consistent_5_getargs():
    return [ NEWGRAPH1, "E" ]

def is_consistent_5_testanswer(val, original_val = None):
    return True == bool(val)

make_test(type='FUNCTION',
          getargs = is_consistent_5_getargs,
          testanswer = is_consistent_5_testanswer,
          expected_val = 'True for NEWGRAPH1/E',
          name = 'is_consistent')


### TEST 42 ###

HOW_MANY_HOURS_THIS_PSET_TOOK_getargs = "HOW_MANY_HOURS_THIS_PSET_TOOK"

def HOW_MANY_HOURS_THIS_PSET_TOOK_testanswer(val, original_val = None):
    return ( val != '' and val != None )

make_test(type = 'VALUE',
          getargs = HOW_MANY_HOURS_THIS_PSET_TOOK_getargs,
          testanswer = HOW_MANY_HOURS_THIS_PSET_TOOK_testanswer,
          expected_val = "[a number of hours]",
          name = HOW_MANY_HOURS_THIS_PSET_TOOK_getargs
          )


### TEST 43 ###

WHAT_I_FOUND_INTERESTING_getargs = "WHAT_I_FOUND_INTERESTING"

def WHAT_I_FOUND_INTERESTING_testanswer(val, original_val = None):
    return ( val != '' and val != None )

make_test(type = 'VALUE',
          getargs = WHAT_I_FOUND_INTERESTING_getargs,
          testanswer = WHAT_I_FOUND_INTERESTING_testanswer,
          expected_val = "[an interesting thing]",
          name = WHAT_I_FOUND_INTERESTING_getargs
          )


### TEST 44 ###

WHAT_I_FOUND_BORING_getargs = "WHAT_I_FOUND_BORING"

def WHAT_I_FOUND_BORING_testanswer(val, original_val = None):
    return ( val != '' and val != None )

make_test(type = 'VALUE',
          getargs = WHAT_I_FOUND_BORING_getargs,
          testanswer = WHAT_I_FOUND_BORING_testanswer,
          expected_val = "[a number of hours]",
          name = WHAT_I_FOUND_BORING_getargs
          )

