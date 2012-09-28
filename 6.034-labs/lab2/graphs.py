# Fall 2012 6.034 Lab 2: Search

from search import *

## The graphs you will use for the problem set.

## The heuristic values
## are lower bounds on the distance to the node with the id of
## "Common Area"

GRAPH1 = Graph(edgesdict = \
               [{NAME:'e1',  VAL: 5, NODE1:'Common Area', NODE2:'Stairs'},
                {NAME:'e2',  VAL:15, NODE1:'Entrance Hall', NODE2:'Hospital'},
                {NAME:'e3',  VAL: 7, NODE1:'Classroom 11', NODE2:'Hospital'},
                {NAME:'e4',  VAL:25, NODE1:'Haunted Bathroom', NODE2:'The Chamber'},
                {NAME:'e5',  VAL: 5, NODE1:'Forbidden Area', NODE2:'Trophy Room'},
                {NAME:'e6',  VAL: 3, NODE1:'Mirrored Room', NODE2:'Statues'},
                {NAME:'e7',  VAL: 1, NODE1:'Grand Hall', NODE2:'Entrance Hall'},
                {NAME:'e8',  VAL: 4, NODE1:'Dungeon 5', NODE2:'Haunted Bathroom'},
                {NAME:'e9',  VAL: 2, NODE1:'Stairs', NODE2:'Grand Hall' },
                {NAME:'e10', VAL: 9, NODE1:'Statues', NODE2:'Stairs' },
                {NAME:'e11', VAL: 6, NODE1:'Entrance Hall', NODE2:'Haunted Bathroom' },
                {NAME:'e12', VAL: 4, NODE1:'Forbidden Area', NODE2:'Stairs' },
                {NAME:'e13', VAL:10, NODE1:'Classroom 11', NODE2:'Entrance Hall' },
                {NAME:'e14', VAL: 5, NODE1:'Trophy Room', NODE2:'Stairs' },
                {NAME:'e15', VAL: 8, NODE1:'Stairs', NODE2:'Mirrored Room' },
                {NAME:'e16', VAL: 3, NODE1:'Entrance Hall', NODE2:'Stairs' },
                {NAME:'e17', VAL: 8, NODE1:'Necessary Room', NODE2:'Common Area'}
                ],
               heuristic = \
               {'Common Area':
                    {'Hospital':17,
                     'Classroom 11':10,
                     'Entrance Hall':7,
                     'Haunted Bathroom':13,
                     'Dungeon 5':15,
                     'The Chamber':14,
                     'Forbidden Area':8,
                     'Trophy Room':6,
                     'Stairs':4,
                     'Grand Hall':6,
                     'Common Area':0,
                     'Statues':12,
                     'Mirrored Room':10,
                     'Necessary Room':6 }})

GRAPH2 = Graph(edgesdict=[ 
        {NAME: 'e1',  VAL:10, NODE1:'S', NODE2:'A' },
        {NAME: 'e2',  VAL: 4, NODE1:'S', NODE2:'B' },
        {NAME: 'e3',  VAL: 9, NODE1:'A', NODE2:'C' },
        {NAME: 'e4',  VAL: 8, NODE1:'B', NODE2:'C' },
        {NAME: 'e5',  VAL: 7, NODE1:'C', NODE2:'D' },
        {NAME: 'e6',  VAL: 9, NODE1:'C', NODE2:'E' },
        {NAME: 'e7',  VAL: 7, NODE1:'D', NODE2:'E' },
        {NAME: 'e8',  VAL:13, NODE1:'D', NODE2:'F' },
        {NAME: 'e9',  VAL: 8, NODE1:'E', NODE2:'F' },
        {NAME: 'e10', VAL: 5, NODE1:'E', NODE2:'G' },
        {NAME: 'e11', VAL:10, NODE1:'F', NODE2:'G' } ],
               heuristic={'G':{'S':25, 'A':20, 'B':22, 'C':15, 'D':8, 'E':3, 'F':9}})
                   
GRAPH3 = Graph(edgesdict=[ 
        {NAME: 'e1', VAL: 6, NODE1:'S', NODE2:'B' },
        {NAME: 'e2', VAL:10, NODE1:'S', NODE2:'A' },
        {NAME: 'e3', VAL:10, NODE1:'A', NODE2:'B' },
        {NAME: 'e4', VAL: 7, NODE1:'B', NODE2:'C' },
        {NAME: 'e5', VAL: 4, NODE1:'A', NODE2:'D' },
        {NAME: 'e6', VAL: 2, NODE1:'C', NODE2:'D' },
        {NAME: 'e7', VAL: 6, NODE1:'C', NODE2:'G' },
        {NAME: 'e8', VAL: 8, NODE1:'G', NODE2:'D' } ],
               heuristic={'G':{"S":0,"A":2,"B":5,"C":6,"D":5}})

GRAPH4 = Graph(edgesdict=[
        {NAME: 'e1',  VAL:1, NODE1:'S', NODE2:'A' },
        {NAME: 'e2',  VAL:1, NODE1:'S', NODE2:'B' },
        {NAME: 'e3',  VAL:1, NODE1:'A', NODE2:'B' },
        {NAME: 'e4',  VAL:1, NODE1:'C', NODE2:'A' },
        {NAME: 'e5',  VAL:1, NODE1:'C', NODE2:'B' },
        {NAME: 'e6',  VAL:1, NODE1:'D', NODE2:'C' },
        {NAME: 'e7',  VAL:1, NODE1:'D', NODE2:'B' },
        {NAME: 'e8',  VAL:1, NODE1:'E', NODE2:'C' },
        {NAME: 'e9',  VAL:1, NODE1:'E', NODE2:'D' },
        {NAME: 'e10', VAL:1, NODE1:'F', NODE2:'D' },
        {NAME: 'e11', VAL:1, NODE1:'F', NODE2:'E' },
        {NAME: 'e12', VAL:1, NODE1:'G', NODE2:'E' },
        {NAME: 'e13', VAL:1, NODE1:'G', NODE2:'F' } ],
               heuristic={"G":{"S":1,"A":3,"B":3,"C":2,"D":2,"E":1,"F":1}})

GRAPH5 = Graph(edgesdict=[
        {NAME: 'e1', VAL:  1, NODE1:'S', NODE2:'A' },
        {NAME: 'e2', VAL:  1, NODE1:'G', NODE2:'C' },
        {NAME: 'e3', VAL:100, NODE1:'B', NODE2:'C' },
        {NAME: 'e4', VAL: 10, NODE1:'S', NODE2:'B' },
        {NAME: 'e5', VAL: 10, NODE1:'C', NODE2:'A' } ],
               heuristic={"G":{"S":10,"A":1000,"B":5,"C":5}})

SAQG = Graph(edgesdict=[
    {'NAME': 'SA', 'LENGTH': 1, 'NODE1': 'S', 'NODE2': 'A'},
    {'NAME': 'SQ', 'LENGTH': 1, 'NODE1': 'S', 'NODE2': 'Q'},
    {'NAME': 'AG', 'LENGTH': 1, 'NODE1': 'A', 'NODE2': 'G'},
    {'NAME': 'QG', 'LENGTH': 1, 'NODE1': 'Q', 'NODE2': 'G'},
    {'NAME': 'SG', 'LENGTH': 1, 'NODE1': 'S', 'NODE2': 'G'}])

NEWGRAPH1 = Graph(edgesdict=[ 
        { 'NAME': 'e1',  'LENGTH':  6, 'NODE1': 'S', 'NODE2': 'A' },
        { 'NAME': 'e2',  'LENGTH':  4, 'NODE1': 'A', 'NODE2': 'B' },
        { 'NAME': 'e3',  'LENGTH':  7, 'NODE1': 'B', 'NODE2': 'F' },
        { 'NAME': 'e4',  'LENGTH':  6, 'NODE1': 'C', 'NODE2': 'D' },
        { 'NAME': 'e5',  'LENGTH':  3, 'NODE1': 'C', 'NODE2': 'A' },
        { 'NAME': 'e6',  'LENGTH':  7, 'NODE1': 'E', 'NODE2': 'D' },
        { 'NAME': 'e7',  'LENGTH':  6, 'NODE1': 'D', 'NODE2': 'H' },
        { 'NAME': 'e8',  'LENGTH':  2, 'NODE1': 'S', 'NODE2': 'C' },
        { 'NAME': 'e9',  'LENGTH':  2, 'NODE1': 'B', 'NODE2': 'D' },
        { 'NAME': 'e10', 'LENGTH': 25, 'NODE1': 'E', 'NODE2': 'G' },
        { 'NAME': 'e11', 'LENGTH':  5, 'NODE1': 'E', 'NODE2': 'C' } ],
                  heuristic={"G":{'S': 11,
                                  'A': 9,
                                  'B': 6,
                                  'C': 12,
                                  'D': 8,
                                  'E': 15,
                                  'F': 1,
                                  'H': 2},
                             "H":{'S': 11,
                                  'A': 9,
                                  'B': 6,
                                  'D': 12,
                                  'E': 8,
                                  'F': 15,
                                  'G': 14},
                             'A':{'S':5, # admissible
                                  "B":1, # h(d) > h(b)+c(d->b) ...  6 > 1 + 2
                                  "C":3,
                                  "D":6,
                                  "E":8,
                                  "F":11,
                                  "G":33,
                                  "H":12},
                             'C':{"S":2, # consistent
                                  "A":3,
                                  "B":7,
                                  "D":6,
                                  "E":5,
                                  "F":14,
                                  "G":30,
                                  "H":12},
                             "D":{"D":3}, # dumb
                             "E":{} # empty
                             })

NEWGRAPH2 = Graph(edgesdict=
                  [ { 'NAME': 'e1', 'LENGTH': 2, 'NODE1': 'D', 'NODE2': 'F' },
                    { 'NAME': 'e2', 'LENGTH': 4, 'NODE1': 'C', 'NODE2': 'E' },
                    { 'NAME': 'e3', 'LENGTH': 2, 'NODE1': 'S', 'NODE2': 'B' },
                    { 'NAME': 'e4', 'LENGTH': 5, 'NODE1': 'S', 'NODE2': 'C' },
                    { 'NAME': 'e5', 'LENGTH': 4, 'NODE1': 'S', 'NODE2': 'A' },
                    { 'NAME': 'e6', 'LENGTH': 8, 'NODE1': 'F', 'NODE2': 'G' },
                    { 'NAME': 'e7', 'LENGTH': 5, 'NODE1': 'D', 'NODE2': 'C' },
                    { 'NAME': 'e8', 'LENGTH': 6, 'NODE1': 'D', 'NODE2': 'H' } ],
                  heuristic={"G":{'S': 9,
                                  'A': 1,
                                  'B': 2,
                                  'C': 3,
                                  'D': 6,
                                  'E': 5,
                                  'F': 15,
                                  'H': 10}})


NEWGRAPH3 = Graph(nodes=["S"])


NEWGRAPH4 = Graph(nodes=["S","A", "B", "C", "D", "E", "F", "H", "J", "K",
            "L", "T" ],
                 edgesdict = [{ 'NAME': 'eSA', 'LENGTH': 2, 'NODE1': 'S', 'NODE2': 'A' },
              { 'NAME': 'eSB', 'LENGTH': 10, 'NODE1': 'S', 'NODE2':'B' },
              { 'NAME': 'eBC', 'LENGTH': 5, 'NODE1': 'B', 'NODE2':'C' },
              { 'NAME': 'eBF', 'LENGTH': 2, 'NODE1': 'B', 'NODE2':'F' },
              { 'NAME': 'eCE', 'LENGTH': 5, 'NODE1': 'C', 'NODE2':'E' },
              { 'NAME': 'eCJ', 'LENGTH': 12, 'NODE1': 'C', 'NODE2':'J' },
              { 'NAME': 'eFH', 'LENGTH': 8, 'NODE1': 'F', 'NODE2':'H' },
              { 'NAME': 'eHD', 'LENGTH': 3, 'NODE1': 'H', 'NODE2':'D' },
              { 'NAME': 'eHK', 'LENGTH': 5, 'NODE1': 'H', 'NODE2':'K' },
              { 'NAME': 'eKJ', 'LENGTH': 1, 'NODE1': 'K', 'NODE2':'J' },
              { 'NAME': 'eJL', 'LENGTH': 4, 'NODE1': 'J', 'NODE2':'L' },
              { 'NAME': 'eKT', 'LENGTH': 7, 'NODE1': 'K', 'NODE2':'T' },
              { 'NAME': 'eLT', 'LENGTH': 5, 'NODE1': 'L', 'NODE2':'T' },
              ],
                 heuristic={"T":{'S': 10,
                                 'A': 6,
                                 'B': 5,
                                 'C': 2,
                                 'D': 5,
                                 'E': 1,
                                 'F': 100,
                                 'H': 2,
                                 'J': 3,
                                 'K': 100,
                                 'L': 4,
                                 'T': 0,}})

# graph used in a_star test 7 (Test 31),
# to differentiate using an extended-list vs not.
# the heuristic is admissible but not consistent,
# so if you use an extended-list (as you're supposed to),
# it won't find an optimal path.
AGRAPH = Graph(nodes = ['S', 'A', 'B', 'C', 'G'],
               edgesdict = [{'NAME': 'eSA', 'LENGTH': 3, 'NODE1': 'S', 'NODE2': 'A'},
                            {'NAME': 'eSB', 'LENGTH': 1, 'NODE1': 'S', 'NODE2': 'B'},
                            {'NAME': 'eAB', 'LENGTH': 1, 'NODE1': 'A', 'NODE2': 'B'},
                            {'NAME': 'eAC', 'LENGTH': 1, 'NODE1': 'A', 'NODE2': 'C'},
                            {'NAME': 'eCG', 'LENGTH': 10, 'NODE1': 'C', 'NODE2': 'G'}],
               heuristic = {'G':{'S': 12,
                                 'A': 9,
                                 'B': 12,
                                 'C': 8,
                                 'G': 0}})
