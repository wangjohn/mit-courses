Shortest path using Dijkstra's algorithm code for MIT 6.006 Fall 2011 PS6

The code distribution contains the following files:
  * dijkstra.py - pset (stripped) version with unimplemented Dijkstra's algorithm
  * dijkstra_test.py - tester used for grading
  * nhpn.py - loader for parsing data from NHPN files
  * priority_queue.py - heap-based priority queue
  * data/nhpn.lnk - link data from NHPN database
  * data/nhpn.nod - node data from NHPN database
  * data/{datadict, format}.txt - data format description  
  * tests/*.in - bi-directional dijkstra test inputs
  * tests/*.gold - outputs that we believe to be correct for the dijkstra test 
      inputs

USAGE

dijkstra.py's behavior can be tweaked using the TRACE environment variable. If 
TRACE=kml, two kml files path_flat.kml and path_curved.kml will be created 
representing the shortest path from the source to the destination. The files can
be viewed on Google Map. If not, a text description of the path is output to the
stdout. 

Command-line example:
    TRACE=kml python dijkstra.py < tests/0boston_berkeley.in


DEPENDENCIES

{dijkstra, priority_queue, nhpn}.py have been tested on Python 2.7 and PyPy 1.6.