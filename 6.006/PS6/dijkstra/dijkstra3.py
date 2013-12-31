#!usr/bin/env python

import sys
import os
import time
from math import *
from nhpn import *
from priority_queue import *

def distance(node1, node2):
    """Returns the distance between node1 and node2, ignoring the Earth's 
    curvature.
    """
    latitude_diff = node1.latitude - node2.latitude
    longitude_diff = node1.longitude - node2.longitude
    return (latitude_diff**2 + longitude_diff**2)**.5

def distance_curved(node1, node2):
    """Returns the distance between node1 and node2, including the Earth's 
    curvature.
    """
    A = node1.latitude * pi / 10**6 / 180
    B = node1.longitude * pi / 10**6 / 180
    C = node2.latitude * pi / 10**6 / 180
    D = node2.longitude * pi / 10**6 / 180
    return acos(sin(A) * sin(C) + cos(A) * cos(C) * cos(B - D))

class NodeDistancePair(object):
    """Wraps a node and its distance representing it in the priority queue."""
    
    def __init__(self, node, distance):
        """Creates a NodeDistancePair to be used as a key in the priority queue.
        """
        self.node = node
        self.distance = distance
        
    def __lt__(self, other):
        # :nodoc: Delegate comparison to distance.
        return (self.distance < other.distance or 
                (self.distance == other.distance and 
                 id(self.node) < id(other.node)))
    
    def __le__(self, other):
        # :nodoc: Delegate comparison to distance.
        return (self.distance < other.distance or
                (self.distance == other.distance and 
                 id(self.node) <= id(other.node)))
                
    def __gt__(self, other):
        # :nodoc: Delegate comparison to distance.
        return (self.distance > other.distance or
                (self.distance == other.distance and 
                 id(self.node) > id(other.node)))
    
    def __ge__(self, other):
        # :nodoc: Delegate comparison to distance.
        return (self.distance > other.distance or
                (self.distance == other.distance and 
                 id(self.node) >= id(other.node)))
    
class Network(object):
    """The National Highway Planning network."""
    def __init__(self):
        """Creates a network with nodes, links and an edge set."""
        self.nodes, self.links = self._load_data()
        self._create_adjacency_lists()
        self.edge_set = self._create_edge_set()
    
    def __str__(self):
        """String representation of the network size."""
        num_nodes = len(self.nodes)
        num_edges = 0
        for node in self.nodes:
            num_edges += len(node.adj)
        return "Graph size: %d nodes, %d edges" % (num_nodes, num_edges)
        
    def verify_path(self, path, source, destination):
        """Verifies that path is a valid path from source to destination.
        
        Returns:
            True if the path is valid such that it uses only edges in the edge
            set.
            
        Raises:
            ValueError: if the first node and the last node do not match source
                and destination respectively or if the edge in not the the edge
                set.
        """
        if source != path[0]:
            raise ValueError('First node on a path is different form the \
                              source.')
        if destination != path[-1]:
            raise ValueError('Last node on a path is different form the \
                              destination.')
        for i in range(len(path) - 1):
            if (path[i], path[i+1]) not in self.edge_set and \
                (path[i+1], path[i]) not in self.edge_set:
                raise ValueError('Adjacent nodes in path have no edge between \
                                  them')
        return True

    def node_by_name(self, city, state):
        """Returns the first node that matches specified location.
        
        Args:
            city: the description of the node should include city.
            state: the state of the node should match state.
        
        Returns:
            The node if it exists, or None otherwise.
        """
    
        for node in self.nodes:
            if node.state == state:
                if city in node.description:
                    return node
        return None
    
    def _load_data(self):
        loader = Loader()
        lnodes = loader.nodes()
        llinks = loader.links()
        return lnodes, llinks
    
    def _create_adjacency_lists(self):
        # Use an adjacency list representation, by putting all vertices
        # adjacent to node in node.adj.
        for node in self.nodes:
            node.adj = []
        for link in self.links:
            link.begin.adj.append(link.end)
            link.end.adj.append(link.begin)
            
    def _create_edge_set(self):
        # Puts edges in a set for faster lookup.
        edge_set = set()
        for link in self.links:
            edge_set.add((link.begin, link.end))
        return edge_set
            
class NodePriorityQueue(object):
    """Min-heap-based priority queue, using 1-based indexing. Adapted from CLRS.
    
    Augmented to include a map of keys to their indices in the heap so that
    key lookup is constant time and decrease_key(key) is O(log n) time.
    """
    
    def __init__(self):
        """Initializes the priority queue."""
        self.heap = [None] # To make the index 1-based.
        self.key_index = {} # key to index mapping.
        self.nodes = {}
    
    def __len__(self):
        return len(self.heap) - 1
       
    def getitem(self, i):
        return self.heap[i]

    def setitem(self, i, node):
        self.heap[i] = node

    def decrease_node(self, node):
        """Decreases the value of the key if it is in the priority queue and 
        maintains the heap property."""
        
        index = self.key_index[node]
        last_dist = self.heap[index]
        self.heap[index] = node.distance
        self.nodes.pop(last_dist)
        self.nodes[node.distance] = node
        
        if index:
            self._decrease_key(index, node.distance)
    
    def insert(self, node):
        """Inserts a key into the priority queue."""
        self.heap.append(node.distance)
        self.nodes[node.distance] = node
        self.key_index[node] = len(self)
        self._decrease_key(len(self), node)

    def _extract_min(self):
        """Removes and returns the minimum key."""
        if len(self) < 1:
            return None
        self._swap(1, len(self))
        min = self.heap.pop()
        del self.key_index[min]
        self._min_heapify(1)
        return min

    def extract_min(self):
        min_distance = self._extract_min()
        min_node = self.nodes[min_distance]
        return min_node
    
    def _decrease_key(self, i, key):
        """Decreases key at a give index.
        
        Args:
            i: index of the key.
            key: key with decreased value.
        """
        while i > 1:
            parent = i // 2
            if self[parent] > key:
                self._swap(i, parent)
                i = parent
            else:
                break
            
    def _min_heapify(self, i):
        """Restores the heap property from index i downwards."""
        l = 2 * i
        r = 2 * i + 1
        smallest = i
        if l <= len(self) and self[l] < self[i]:
            smallest = l
        if r <= len(self) and self[r] < self[smallest]:
            smallest = r
        if smallest != i:
            self._swap(i, smallest)
            self._min_heapify(smallest)

    def _swap(self, i, j):
        # Swaps the key at indices i and j and updates the key to index map.
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.key_index[self.heap[i]], self.key_index[self.heap[j]] = i, j

    def check_ri(self):
        heap = self.heap
        i = 1
        while i <= (len(heap) - 1) // 2:
            l = i * 2
            if heap[i] > heap[l]:
                raise ValueError('Left child is smaller than parent.')
            r = i * 2 + 1
            if r < len(heap) and heap[i] > heap[r]:
                raise ValueError('Right child is smaller than parent.')
            i += 1
            
        for key, index in self.key_index.items():
            if self.heap[index] is not key:
                raise ValueError('Key index mapping is wrong.')    


class PathFinder(object):
    """Finds a shortest path from the source to the destination in the network.
    """
    def __init__(self, network, source, destination):
        """Creates a PathFinder for the network with source and destination.
        
        Args:
            network: the network on which paths should be found.
            source: source of the path.
            destination: destination of the path.
        """    
        self.network = network
        self.source = source
        self.destination = destination
        
    def shortest_path(self, weight):
        """Returns a PathResult for the shortest path from source to destination. 
        
        Args: 
            weight: weight function to compute edge weights.
            
        Returns:
            PathResult for the shortest path or None if path is empty.
        """
        start_time = time.clock()
        
        path, num_visited = self.dijkstra(weight, self.network.nodes, 
                                          self.source, self.destination)
            
        time_used = round(time.clock() - start_time, 3)
        if path:
            if self.network.verify_path(path, self.source, self.destination):
                return PathResult(path, num_visited, weight, self.network, 
                                  time_used)
        else:
            return None

    def dijkstra(self, weight, nodes, source, destination):
        """Performs Dijkstra's algorithm until it finds the shortest
        path from source to destination in the graph with nodes and edges.
        Assumes that all weights are non-negative.
    
        At the end of the algorithm:
        - node.visited is True if the node is visited, False otherwise.
        (Note: node is visited if the shortest path to it is computed.)
    
        Args:
            weight: function for calculating the weight of edge (u, v). 
            nodes: list of all nodes in the network.
            source: the source node in the network.
            destination: the destination node in the network.
         
        Returns:
            A tuple: (the path as a list of nodes from source to destination, 
                      the number of visited nodes)
        """
        
        heap = PriorityQueue()
        for node in nodes:
            node.distance = sys.maxint
            node.visited = False
            node.seen = False
        source.distance = 0
        source.visited = True
        source.parent = None
        source.seen = True
        
        heap.insert(source)
        num_visited = 0
        while len(heap) > 0:
            num_visited += 1
            current = heap.extract_min()
            current.visited = True
            if current == destination:
                path_list = self.get_path(source, destination)
                return (path_list, num_visited)
            for node in current.adj:
                if not node.visited:
                    new_distance = weight(current, node) + current.distance
                    if node.seen:
                        if new_distance < node.distance:
                            node.distance = new_distance
                            heap.decrease_key(node)
                            node.parent = current
                    else:
                        node.distance = new_distance
                        heap.insert(node)
                        node.parent = current
                        node.seen = True
        return (None, num_visited)
        

    def get_path(self, source, destination):
        nodes = []
        current = destination
        while current.parent != None:
            nodes.append(current)
            current = current.parent
        nodes.append(source)
        nodes.reverse()
        return(nodes)
    
    @staticmethod
    def from_file(file, network):
        """Creates a PathFinder object with source and destination read from 
        file.
        
        Args:
            file: file containing source and destination.
            network: network in which a shortest path needs to be found.
        
        Returns:
            A PathFinder object.
            
        Raises:
            ValueError: when source or destination is not valid.
        """
        source = destination = None
        for i in range(2):
            command = file.readline().split()
            city = ' '.join(command[1].split('_')).upper()
            node = network.node_by_name(city, command[2].upper())
            if command[0] == 'source':
                source = node
            elif command[0] == 'destination':
                destination = node
                
        if source and destination:
            return PathFinder(network, source, destination)
        else:
            if source is None:
                raise ValueError('Invalid source.')
            if destination is None:
                raise ValueError('Invalid destination.')  
    
class PathResult(object):
    """An object containing the results of a path found by PathFinder."""
    
    def __init__(self, path, num_visited, weight, network, time):
        """Creates a PathResult.
        
        Args:
            path: a list of nodes in the path.
            num_visited: number of nodes visited during path finding.
            weight: function to compute the weight of an edge (u, v).
            network: the network on which the path is found.
            time: time used to find the path.
        """
        self.network = network
        self.path = path
        self.num_visited = num_visited
        self.total_weight = self._total_weight(weight)
        self.time = time
        
    def to_kml(self):
        """Returns the path in kml format."""
        
        kml = ["""<?xml version="1.0" encoding="utf-8"?>
<kml xmlns="http://earth.google.com/kml/2.1">
  <Document>
    <Placemark>
      <LineString>
        <extrude>1</extrude>
        <tessellate>1</tessellate>
        <coordinates>
"""]
        kml.append(''.join("%f,%f\n" % (node.longitude/1000000., 
                                        node.latitude/1000000.) 
                           for node in self.path))
        kml.append("""</coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>
""")
        return ''.join(kml)
    
    def to_lines(self):
        """Returns a list of lines representing the results."""
        source = self.path[0]
        dest = self.path[-1]
        list = ["Path: %s, %s -> %s, %s" %  (source.description, \
                    source.state, dest.description, dest.state)]
        list.append(str(self.network))
        list.append("Nodes visited: %d" % self.num_visited)
        list.append("Path length: %.4f" % self.total_weight)
        list.append("Number of roads: %d" % (len(self.path) - 1))
        list.append("Time used in seconds: %.3f" % self.time)
        return list
    
    def sol_to_lines(self):
        return ["Path length: %.4f" % self.total_weight]
    
    def to_file(self, file):
        """Outputs to an output stream."""
        for line in self.to_lines():
            file.write(line)
            file.write("\n")
    
    def sol_to_file(self, file):
        """Outputs solution to output stream."""
        for line in self.sol_to_lines():
            file.write(line)
            file.write("\n")
                    
    def _total_weight(self, weight):
        """Computes the sum of weights along a path.
        
        Args:
            weight: function to compute the weight of an edge (u, v).
        """
        sum = 0
        for i in range(len(self.path) - 1):
            sum += weight(self.path[i], self.path[i + 1])
        return sum

# Command-line controller.
if __name__ == '__main__':
    network = Network()
    if os.environ.get('TRACE') == 'kml':
        pf = PathFinder.from_file(sys.stdin, network)
        with open('path_flat.kml', 'w') as file:
            r = pf.shortest_path(distance)
            r and file.write(r.to_kml())
        with open('path_curved.kml', 'w') as file:
            r = pf.shortest_path(distance_curved)
            r and file.write(r.to_kml())
    else:
        pf = PathFinder.from_file(sys.stdin, network)
        r = pf.shortest_path(distance)
        if r:
            if os.environ.get('TRACE') == 'sol':
                r.sol_to_file(sys.stdout)
            else:
                r.to_file(sys.stdout)
        else:
            print 'No path is found.'
    
