import zlib
from math import acos,cos,sin,pi,atan2
try:
    import cPickle as pickle
except:
    import pickle

class Location:
    def __init__(self, id_number, longitude, latitude, name):
        self.id_number = id_number
        self.longitude = longitude
        self.latitude = latitude
        self.name = name

class Link:
    def __init__(self, node_a, node_b, name):
        self.begin = node_a
        self.end = node_b
        self.name = name


locationFromName = pickle.loads(zlib.decompress(open('loc_from_name.pickle','rb').read()))
locationFromID = pickle.loads(zlib.decompress(open('loc_from_id.pickle','rb').read()))
neighbors = pickle.loads(zlib.decompress(open('neighbors.pickle','rb').read()))
links = pickle.loads(zlib.decompress(open('links.pickle','rb').read()))

from lib601.search import SearchNode,search


def pathCost(path):
    pass #your code here

class HighwaySearchNode(SearchNode):
    def __init__(self, state, parent, cost):
        SearchNode.__init__(self, state)
        self.parent = parent
        self.cost = cost

    def getChildren(self):
        if self.state.id_number in neighbors:
            ids = neighbors[self.state.id_number]
            return [HighwaySearchNode(locationFromID[i], self, self.cost + id_distance(i, self.state.id_number)) for i in ids]
        return []

def ucSearch(startNode, goalTest, heuristic=lambda s: 0):
    if goalTest(startNode.state):
        return startNode.getPath()
    agenda = [(startNode,startNode.cost+heuristic(startNode.state))]
    expanded = set()
    while len(agenda) > 0:
        agenda.sort(key=lambda n: n[1])
        node,priority = agenda.pop(0)
        if node.state not in expanded:
            expanded.add(node.state)
            if goalTest(node.state):
                return (node.getPath(), len(expanded))
            for child in node.getChildren():
                if child.state not in expanded:
                    agenda.append((child,child.cost+heuristic(child.state)))
    return (None, len(expanded))


def to_kml(path):
    kml = open('path.kml', mode='w')
    kml.write("""<?xml version="1.0" encoding="utf-8"?>
<kml xmlns="http://earth.google.com/kml/2.1">
  <Document>
    <Placemark>
      <LineString>
        <extrude>1</extrude>
        <tessellate>1</tessellate>
        <coordinates>
""")
    kml.writelines("%f,%f\n" % (loc.longitude,loc.latitude) 
                   for loc in [locationFromID[i] for i in path])
    kml.write("""</coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>
""")
    kml.close()

def locationsMatchingName(state, name):
    name = name or ''
    return [(i,locationFromName[i].id_number) for i in locationFromName if i[:2]==state and name in i[2:]]

def id_distance(id1, id2):
    return distance(locationFromID[id1], locationFromID[id2])

def distance(loc1, loc2):
    """Returns the approximate distance between loc1 and loc2 in miles, 
    taking into account the Earth's curvature."""
    phi1 = loc1.latitude*pi/180.
    theta1 = loc1.longitude*pi/180.
    phi2 = loc2.latitude*pi/180.
    theta2 = loc2.longitude*pi/180.
    # cos(psi) is dot-product of the two unit vectors (as above)
    cospsi = sin(phi1)*sin(phi2) + cos(phi1)*cos(phi2)*cos(theta2-theta1)
    # sin(psi) is magnitude of cross product of the two unit vectors
    sinpsi = ((sin(theta1)*cos(phi1)*sin(phi2) - sin(theta2)*cos(phi2)*sin(phi1))**2 +\
              (cos(theta2)*cos(phi2)*sin(phi1) - cos(theta1)*cos(phi1)*sin(phi2))**2 +\
              (cos(phi1)*cos(phi2)*sin(theta2-theta1))**2)**0.5
    return atan2(sinpsi,cospsi) * 3958 # miles

def distance_of_path(locs):
    total = 0
    for i in xrange(len(locs)-1):
        first_loc = locationFromID[locs[i]]
        second_loc = locationFromID[locs[i+1]]
        total += distance(first_loc, second_loc)
    return total

def goal(state, destination):
    return state.id_number == destination

def run_search(start_id, end_id):
    start_node = HighwaySearchNode(locationFromID[start_id], None, 0)
    g = lambda s: goal(s, end_id)
    noh_ans, noh_expanded = ucSearch(start_node, g)
    print "No Heuristic Distance: ", distance_of_path([x.id_number for x in noh_ans])
    print "No Heuristic Expanded: ", noh_expanded

    h_ans, h_expanded = ucSearch(start_node, g, lambda s: distance(s, locationFromID[end_id]))
    print "Heuristic Distance: ", distance_of_path([x.id_number for x in h_ans])
    print "Heuristic Expanded: ", h_expanded

if __name__ == '__main__':
    run_search(20000071, 25000502)
