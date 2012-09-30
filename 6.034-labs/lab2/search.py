# Fall 2012 6.034 Lab 2: Search

try:
    set()
except NameError:
    from sets import Set as set, ImmutableSet as frozenset

NAME="NAME"
NODE1="NODE1"
NODE2="NODE2"
VAL="LENGTH"

class Edge:
    def __init__(self, name, node1, node2, length):
        self.name = name
        self.node1 = node1
        self.node2 = node2
        self.length = length

class Graph:
    def __init__(self, nodes=None, edgesdict=None, heuristic=None,
                 edges=None):
        '''specify EITHER edgesdict OR edges'''
        if edges:
            self.edges = edges
        elif edgesdict:
            try:
                self.edges = [Edge(e['NAME'], e['NODE1'], e['NODE2'], e['LENGTH'])\
                              for e in edgesdict]
            except KeyError:
                self.edges = [Edge(e['name'], e['node1'], e['node2'], e['length'])\
                              for e in edgesdict]
        else:
            self.edges = []
        self.nodes = nodes
        if not nodes:
            self.nodes = list(set([edge.node1 for edge in self.edges] + 
                                  [edge.node2 for edge in self.edges]))
        # heuristic is a dictionary where heuristic[G][S] is the
        #  heuristic distance from S to G
        self.heuristic = heuristic
        if not heuristic:
            self.heuristic = {}
        self.validate()
    
    def validate(self):
        for name in self.nodes:
            assert isinstance(name,basestring), str(type(name))+": "+str(name)
        assert len(self.nodes) == len(set(self.nodes)), "no duplicate nodes"
        edgenames = [edge.name for edge in self.edges]
        assert len(edgenames) == len(set(edgenames)), "no duplicate edges"
        for edge in self.edges:
            assert isinstance(edge.name, basestring), type(edge.name)
            assert edge.node1 in self.nodes
            assert edge.node2 in self.nodes
            assert edge.length > 0, "positive edges only today"
        for start in self.nodes:
            for end in self.nodes:
                assert self.get_heuristic(start,end) >= 0

    def get_connected_nodes(self, node):
        """
        gets a list of all node id values connected to a given node.
        'node' should be a node name, not a dictionary.
        The return value is a list of node names.
        """
        assert node in self.nodes, "No node "+str(node)+" in graph "+str(self)
        result = [x.node2 for x in self.edges if x.node1 == node]
        result += [x.node1 for x in self.edges if x.node2 == node]
        return sorted(result)

    def get_edge(self, node1, node2):
        """
        checks the list of edges and returns an edge if
        both connected nodes are part of the edge, or 'None' otherwise.
        'node1' and 'node2' are names of nodes, not 'NODE' dictionaries.
        """
        assert node1 in self.nodes, "No node "+str(node1)+" in graph "+str(self)
        assert node2 in self.nodes, "No node "+str(node2)+" in graph "+str(self)
        node_names = ( node1, node2 )
        for edge in self.edges:
            if ((edge.node1, edge.node2) == node_names or 
                (edge.node2, edge.node1) == node_names):
                return edge
        return None

    def are_connected(self, node1, node2):
        """
        checks if two edges are connected.
        'node1' and 'node2' are names of nodes, not 'NODE' dictionaries.
        """
        return bool( self.get_edge(node1, node2) )

    def get_heuristic(self, start, goal):
        """ Return the value of the heuristic from the start to the goal"""
        assert start in self.nodes, "No node "+str(start)+" in graph "+str(self)
        assert goal in self.nodes, "No node "+str(goal)+" in graph "+str(self)
        if goal in self.heuristic:
            if start in self.heuristic[goal]:
                return self.heuristic[goal][start]
            else:
                return 0 # we have checked that everything is positive
        else: 
            return 0 # we have checked that everything is positive
    
    def is_valid_path(self, path):
        def is_valid_path_reducer(elt_a, elt_b):
            if elt_a == False or not self.are_connected(elt_a, elt_b):
                return False
            else:
                return elt_b
        return (reduce(is_valid_path_reducer, path) != False)

    def add_edge(self, node1, node2, length, name=None):
        if node1 not in self.nodes:
            self.nodes.append(node1)
        if node2 not in self.nodes:
            self.nodes.append(node2)
        if name == None:
            name = ("%s %s" % (node1, node2))
        self.edges.append(Edge(name, node1, node2, length))

    def set_heuristic(self, start, goal, value):
        if goal not in self.heuristic:
            self.heuristic[goal] = {}
        self.heuristic[goal][start] = value

    def __str__(self):
        return "Graph: \n  edges="+str(self.edges)+"\n  heuristic="+str(self.heuristic)

