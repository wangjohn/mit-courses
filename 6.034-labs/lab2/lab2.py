# Fall 2012 6.034 Lab 2: Search
#
# Your answers for the true and false questions will be in the following form.  
# Your answers will look like one of the two below:
#ANSWER1 = True
#ANSWER1 = False

# 1: True or false - Hill Climbing search is guaranteed to find a solution
#    if there is a solution
ANSWER1 = False 

# 2: True or false - Best-first search will give an optimal search result
#    (shortest path length).
#    (If you don't know what we mean by best-first search, refer to
#     http://courses.csail.mit.edu/6.034f/ai3/ch4.pdf (page 13 of the pdf).)
ANSWER2 = False

# 3: True or false - Best-first search and hill climbing make use of
#    heuristic values of nodes.
ANSWER3 = True

# 4: True or false - A* uses an extended-nodes set.
ANSWER4 = True

# 5: True or false - Breadth first search is guaranteed to return a path
#    with the shortest number of nodes.
ANSWER5 = True 

# 6: True or false - The regular branch and bound uses heuristic values
#    to speed up the search for an optimal path.
ANSWER6 = False

# Import the Graph data structure from 'search.py'
# Refer to search.py for documentation
from search import Graph

## Optional Warm-up: BFS and DFS
# If you implement these, the offline tester will test them.
# If you don't, it won't.
# The online tester will not test them.

def bfs(graph, start, goal):
    raise NotImplementedError

## Once you have completed the breadth-first search,
## this part should be very simple to complete.
def dfs(graph, start, goal):
    raise NotImplementedError


## Now we're going to add some heuristics into the search.  
## Remember that hill-climbing is a modified version of depth-first search.
## Search direction should be towards lower heuristic values to the goal.
def hill_climbing(graph, start, goal):
    queue = [[start]]
    while len(queue) > 0 and queue[0][-1] != goal:
        current_path = queue.pop(0)
        current_node = current_path[-1]
        connected = graph.get_connected_nodes(current_node)
        new_paths = {}
        for connected_node in connected:
            distance_to_goal = graph.get_heuristic(connected_node, goal)
            if connected_node not in current_path:
                add_to_dictlist(new_paths, distance_to_goal, current_path + [connected_node])
        paths_for_front = []
        for path_distance in sorted(new_paths):
            paths_for_front.extend(new_paths[path_distance])
        queue = paths_for_front + queue
    if len(queue) > 0:
        return queue[0]
    else:
        return [] 

def add_to_dictlist(dictionary, key, value):
    if key in dictionary:
        dictionary[key].append(value)
    else:
        dictionary[key] = [value]

## Now we're going to implement beam search, a variation on BFS
## that caps the amount of memory used to store paths.  Remember,
## we maintain only k candidate paths of length n in our agenda at any time.
## The k top candidates are to be determined using the 
## graph get_heuristic function, with lower values being better values.
def beam_search(graph, start, goal, beam_width):
    queue = { graph.get_heuristic(start, goal): [[start]]}
    made_progress = True
    while len(queue) > 0 and made_progress:
        top_k_distances = sorted(queue)[:beam_width]
        k = 0
        current_paths = []
        for distance in top_k_distances:
            for path in queue[distance]:
                if k < beam_width:
                    current_paths.append(path)
                    k += 1
                else:
                    break
                    break
        made_progress = False
        queue = {}
        for path in current_paths:
            current_node = path[-1]
            for node in graph.get_connected_nodes(current_node):
                if node == goal:
                    return path + [node]
                if node not in path:
                    made_progress = True
                    add_to_dictlist(queue, graph.get_heuristic(node, goal), path + [node])
    return []
     
## Now we're going to try optimal search.  The previous searches haven't
## used edge distances in the calculation.

## This function takes in a graph and a list of node names, and returns
## the sum of edge lengths along the path -- the total distance in the path.
def path_length(graph, node_names):
    length = 0
    for i in xrange(len(node_names)-1):
        node1 = node_names[i]
        node2 = node_names[i+1]
        length += graph.get_edge(node1, node2).length
    return length 

def branch_and_bound(graph, start, goal):
    raise NotImplementedError

def a_star(graph, start, goal):
    raise NotImplementedError


## It's useful to determine if a graph has a consistent and admissible
## heuristic.  You've seen graphs with heuristics that are
## admissible, but not consistent.  Have you seen any graphs that are
## consistent, but not admissible?

def is_admissible(graph, goal):
    raise NotImplementedError

def is_consistent(graph, goal):
    raise NotImplementedError

HOW_MANY_HOURS_THIS_PSET_TOOK = ''
WHAT_I_FOUND_INTERESTING = ''
WHAT_I_FOUND_BORING = ''
