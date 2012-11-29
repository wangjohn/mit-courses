# 6.02 routing protocol tests
import os,sys,time,random
from PS8_netsim import *

def verify_routing_table(net,source,entries,verbose=True):
    src = net.addresses[source]
    for dest,expected_route in entries.items():
        route = src.routes.get(dest,None)
        if isinstance(route,Link):
            n = route.end2 if src==route.end1 else route.end1
            route = n.address
        elif route is not None:
            print route, 'isn\'t a Link; each route should be a Link.'
            sys.exit(1)
        if route in expected_route:
            continue
        if (verbose):
            print 'error in routing table: node %s, dest %s, expected %s, got %s' % \
                (source,dest,' or '.join(expected_route) if expected_route[0] is not None else None,route)
        return False
    return True

def verify_routes(network):
    # build the deterministic test network
    #   A---B   C---D
    #   |   | / | / |
    #   E   F---G---H
    # format: (name of node, x coord, y coord)
    random.seed(617617761)
    NODES =(('A',0,0), ('B',1,0), ('C',2,0), ('D',3,0),
            ('E',0,1), ('F',1,1), ('G',2,1), ('H',3,1))
    # format: (link start, link end)
    LINKS = (('A','B'),('A','E'),('B','F'),
             ('C','D'),('C','F'),('C','G'),
             ('D','G'),('D','H'),('F','G'),('G','H'))

    # make a network
    net_euclidean = network(4000, NODES, LINKS, 0.0)

    ######################################################################
    # test w/ no broken links
    print 'Testing Euclidean',network,'with no broken links...'
    net_euclidean.reset()
    net_euclidean.step(count=1000)
    # specify dest:first-hop to be checked

    print '\tA---B   C---D'
    print '\t|   | / | / |'
    print '\tE   F---G---H'
    print '\tlink costs = 1 on straight links, sqrt(2) on diagonal links'

    result = verify_routing_table(net_euclidean,'A',{'B': ('B',),
                                           'C': ('B',),
                                           'D': ('B',),
                                           'E': ('E',),
                                           'F': ('B',),
                                           'G': ('B',),
                                           'H': ('B',),
                                           })
    result &= verify_routing_table(net_euclidean,'B',{'A': ('A',),
                                            'C': ('F',),
                                            'D': ('F',),
                                            'E': ('A',),
                                            'F': ('F',),
                                            'G': ('F',),
                                            'H': ('F',),
                                            })
    result &= verify_routing_table(net_euclidean,'C',{'A': ('F',),
                                            'B': ('F',),
                                            'D': ('D',),
                                            'E': ('F',),
                                            'F': ('F',),
                                            'G': ('G',),
                                            'H': ('D','G'),
                                            })
    result &= verify_routing_table(net_euclidean,'D',{'A': ('C','G'),
                                            'B': ('C','G'),
                                            'C': ('C',),
                                            'E': ('C','G'),
                                            'F': ('C','G'),
                                            'G': ('G',),
                                            'H': ('H',),
                                            })
    result &= verify_routing_table(net_euclidean,'E',{'A': ('A',),
                                            'B': ('A',),
                                            'C': ('A',),
                                            'D': ('A',),
                                            'F': ('A',),
                                            'G': ('A',),
                                            'H': ('A',),
                                            })
    result &= verify_routing_table(net_euclidean,'F',{'A': ('B',),
                                            'B': ('B',),
                                            'C': ('C',),
                                            'D': ('C','G'),
                                            'E': ('B',),
                                            'G': ('G',),
                                            'H': ('G',),
                                            })
    result &= verify_routing_table(net_euclidean,'G',{'A': ('F',),
                                            'B': ('F',),
                                            'C': ('C',),
                                            'D': ('D',),
                                            'E': ('F',),
                                            'F': ('F',),
                                            'H': ('H',),
                                            })
    result &= verify_routing_table(net_euclidean,'H',{'A': ('G',),
                                            'B': ('G',),
                                            'C': ('D','G'),
                                            'D': ('D',),
                                            'E': ('G',),
                                            'F': ('G',),
                                            'G': ('G',),
                                            })
    if result:
        print '...PASSED'
        print

    ####################################################
    # Begin Katrina's test case: Non-Euclidean topology
    # format: (name of node, x coord, y coord)
    NODES =(('A',0,0), ('B',1,0), ('E',2,0),
            ('C',0,1), ('D',1,1), ('F',2,1))
    # format: (link start, link end)
    LINKS = (('A','B'),('A','C'),('B','C'),
             ('B','D'),('B','E'),('C','D'),
             ('D','F'))

    # make a network
    net = network(4000, NODES, LINKS,0)

    for l in net.links:
        if (l.end1.address == 'A' and l.end2.address == 'B'):
            l.set_cost(7)
        elif (l.end1.address == 'A' and l.end2.address == 'C'):
            l.set_cost(1)
        elif (l.end1.address == 'B' and l.end2.address == 'C'):
            l.set_cost(2)
        elif (l.end1.address == 'B' and l.end2.address == 'D'):
            l.set_cost(9)
        elif (l.end1.address == 'B' and l.end2.address == 'E'):
            l.set_cost(1)
        elif (l.end1.address == 'C' and l.end2.address == 'D'):
            l.set_cost(4)
        elif (l.end1.address == 'D' and l.end2.address == 'F'):
            l.set_cost(1)

    # test non-euclidean topology
    print 'Testing non-Euclidean',network,'with no broken links'
    print '\t A-7-B-1-E'
    print '\t |     / |'
    print '\t 1  2/   9'
    print '\t | /     |'
    print '\t C-4-D-1-F'

    net.reset()
    net.step(count=1000)
    # specify dest:first-hop to be checked
    result = verify_routing_table(net,'A',{'B': ('C',),
                                           'C': ('C',),
                                           'D': ('C',),
                                           'E': ('C',),
                                           'F': ('C',),})

    result &= verify_routing_table(net,'B',{'A': ('C'),
                                            'C': ('C'),
                                            'D': ('C'),
                                            'E': ('E'),
                                            'F': ('C'),})

    result &= verify_routing_table(net,'C',{'A': ('A'),
                                            'B': ('B'),
                                            'D': ('D'),
                                            'E': ('B'),
                                            'F': ('D'),})

    result &= verify_routing_table(net,'D',{'A': ('C'),
                                            'B': ('C'),
                                            'C': ('C'),
                                            'E': ('C'),
                                            'F': ('F'),})

    result &= verify_routing_table(net,'E',{'A': ('B'),
                                            'B': ('B'),
                                            'C': ('B'),
                                            'D': ('B'),
                                            'F': ('B'),})

    result &= verify_routing_table(net,'F',{'A': ('D'),
                                            'B': ('D'),
                                            'C': ('D'),
                                            'D': ('D'),
                                            'E': ('D'),})

    if result:
        print '...PASSED'
        print

    ######################################################################
    # test w/ one broken links
    print 'Testing', network, 'with one broken link'
    # break F<-->G link
    for link in net_euclidean.links:
        if link.end1.address=='F' and link.end2.address=='G':
            link.broken = True
    print 'Breaking F-G link in topology (\'X\' marks the spot!)'
    print '\tA---B   C---D'
    print '\t|   | / | / |'
    print '\tE   F-X-G---H'
    print '\tlink costs = 1 on straight links, sqrt(2) on diagonal links'
    net_euclidean.step(count=1000)
    # specify dest:first-hop to be checked
    result = verify_routing_table(net_euclidean,'A',{'B': ('B',),
                                           'C': ('B',),
                                           'D': ('B',),
                                           'E': ('E',),
                                           'F': ('B',),
                                           'G': ('B',),
                                           'H': ('B',),
                                           })
    result &= verify_routing_table(net_euclidean,'B',{'A': ('A',),
                                            'C': ('F',),
                                            'D': ('F',),
                                            'E': ('A',),
                                            'F': ('F',),
                                            'G': ('F',),
                                            'H': ('F',),
                                            })
    result &= verify_routing_table(net_euclidean,'C',{'A': ('F',),
                                            'B': ('F',),
                                            'D': ('D',),
                                            'E': ('F',),
                                            'F': ('F',),
                                            'G': ('G',),
                                            'H': ('D','G'),
                                            })
    result &= verify_routing_table(net_euclidean,'D',{'A': ('C',),
                                            'B': ('C',),
                                            'C': ('C',),
                                            'E': ('C',),
                                            'F': ('C',),
                                            'G': ('G',),
                                            'H': ('H',),
                                            })
    result &= verify_routing_table(net_euclidean,'E',{'A': ('A',),
                                            'B': ('A',),
                                            'C': ('A',),
                                            'D': ('A',),
                                            'F': ('A',),
                                            'G': ('A',),
                                            'H': ('A',),
                                            })
    result &= verify_routing_table(net_euclidean,'F',{'A': ('B',),
                                            'B': ('B',),
                                            'C': ('C',),
                                            'D': ('C',),
                                            'E': ('B',),
                                            'G': ('C',),
                                            'H': ('C',),
                                            })
    result &= verify_routing_table(net_euclidean,'G',{'A': ('C',),
                                            'B': ('C',),
                                            'C': ('C',),
                                            'D': ('D',),
                                            'E': ('C',),
                                            'F': ('C',),
                                            'H': ('H',),
                                            })
    result &= verify_routing_table(net_euclidean,'H',{'A': ('D','G',),
                                            'B': ('D','G'),
                                            'C': ('D','G'),
                                            'D': ('D',),
                                            'E': ('D','G',),
                                            'F': ('D','G',),
                                            'G': ('G',),
                                            })
    if result:
        print '...PASSED'
        print
    else:
        print 'failed'
        sys.exit(1)


    ######################################################################
    # Katrina's test: Non-Euclidean topology with failures and cost changes
    # format: (name of node, x coord, y coord)
    NODES =(('A',0,0), ('B',1,0), ('C',2,0), ('D',3,0),
            ('E',0,1), ('F',1,1), ('G',2,1), ('H',3,1))
    # format: (link start, link end)
    LINKS = (('A','B'),('A','E'),('B','F'),
             ('B','C'),('C','F'),('C','D'),
             ('D','G'),('D','H'),('E','F'),
             ('F','G'),('G','H'),('C','G')) # this last link is going to start out broken

    # make a network
    net = network(4000, NODES, LINKS,0)

    print 'Testing',network,'prior to changing costs and more failures'
    print '\tA---B-4-C---D'
    print '\t|   | /2X /2|'
    print '\tE---F---G---H'
    print '\tCosts: BC=4 DG=2 CF=2 CG broken; all other costs are 1'

    # every other link has cost 1
    for l in net.links:
        if (l.end1.address == 'B' and l.end2.address == 'C'):
            l.cost = 4
        elif (l.end1.address == 'D' and l.end2.address == 'G'):
            l.cost = 2
        elif (l.end1.address == 'C' and l.end2.address == 'F'):
            l.cost = 2
        elif (l.end1.address == 'C' and l.end2.address == 'G'):
            l.broken = True

    # test non-euclidean topology with changing costs and failures
    net.reset()
    net.step(count=1000)
    # specify dest:first-hop to be checked

    result = verify_routing_table(net,'A',{'B': ('B',),
                                           'C': ('B','E'),
                                           'D': ('B','E'),
                                           'E': ('B','E',),
                                           'F': ('B','E'),
                                           'G': ('B','E'),
                                           'H': ('B','E')})

    result &= verify_routing_table(net,'B',{'A': ('A',),
                                            'C': ('F',),
                                            'D': ('F',),
                                            'E': ('A','F',),
                                            'F': ('F',),
                                            'G': ('F',),
                                            'H': ('F',)})

    result &= verify_routing_table(net,'C',{'A': ('F',),
                                            'B': ('F',),
                                            'D': ('D',),
                                            'E': ('F',),
                                            'F': ('F',),
                                            'G': ('D','F'),
                                            'H': ('D',)})

    result &= verify_routing_table(net,'D',{'A': ('C','G','H'),
                                            'B': ('C','G','H'),
                                            'C': ('C',),
                                            'E': ('C','G','H'),
                                            'F': ('C','G','H'),
                                            'G': ('G','H'),
                                            'H': ('H',)})

    result &= verify_routing_table(net,'E',{'A': ('A',),
                                            'B': ('A','F'),
                                            'C': ('F',),
                                            'D': ('F',),
                                            'F': ('F',),
                                            'G': ('F',),
                                            'H': ('F',)})

    result &= verify_routing_table(net,'F',{'A': ('B','E'),
                                            'B': ('B',),
                                            'C': ('C',),
                                            'D': ('C','G','H'),
                                            'E': ('E',),
                                            'G': ('G',),
                                            'H': ('G',)})

    result &= verify_routing_table(net,'G',{'A': ('F',),
                                            'B': ('F',),
                                            'C': ('D','F','H'),
                                            'D': ('D','H'),
                                            'E': ('F',),
                                            'F': ('F',),
                                            'H': ('H',)})

    result &= verify_routing_table(net,'H',{'A': ('G',),
                                            'B': ('G',),
                                            'C': ('D',),
                                            'D': ('D',),
                                            'E': ('G',),
                                            'F': ('G',),
                                            'G': ('G',)})

    if result:
        print '...PASSED'
        print

    print 'Testing',network,'with changing costs and more failures'
    print '\tNow breaking CF, CG, DG; changing BF<--15, CD <--13'
    for l in net.links:
        if (l.end1.address == 'C' and l.end2.address == 'F'):
            l.broken = True
        elif (l.end1.address == 'B' and l.end2.address == 'F'):
            l.cost = 15
        elif (l.end1.address == 'C' and l.end2.address == 'G'):
            l.broken = False # cost is 1, so this is fine
        elif (l.end1.address == 'C' and l.end2.address == 'D'):
            l.cost = 13
        elif (l.end1.address == 'D' and l.end2.address == 'G'):
            l.broken = True
    
    net.step(count=1000)

    result &= verify_routing_table(net,'A',{'B': ('B',),
                                            'C': ('E',),
                                            'D': ('E',),
                                            'E': ('E',),
                                            'F': ('E',),
                                            'G': ('E',),
                                            'H': ('E',)})

    result &= verify_routing_table(net,'B',{'A': ('A',),
                                            'C': ('C',),
                                            'D': ('A',),
                                            'E': ('A',),
                                            'F': ('A',),
                                            'G': ('A',),
                                            'H': ('A',)})

    result &= verify_routing_table(net,'C',{'A': ('G',),
                                            'B': ('B',),
                                            'D': ('G',),
                                            'E': ('G',),
                                            'F': ('G',),
                                            'G': ('G',),
                                            'H': ('G',)})

    result &= verify_routing_table(net,'D',{'A': ('H',),
                                            'B': ('H',),
                                            'C': ('H',),
                                            'E': ('H',),
                                            'F': ('H',),
                                            'G': ('H',),
                                            'H': ('H',)})

    result &= verify_routing_table(net,'E',{'A': ('A',),
                                            'B': ('A',),
                                            'C': ('F',),
                                            'D': ('F',),
                                            'F': ('F',),
                                            'G': ('F',),
                                            'H': ('F',)})

    result &= verify_routing_table(net,'F',{'A': ('E',),
                                            'B': ('E',),
                                            'C': ('G',),
                                            'D': ('G',),
                                            'E': ('E',),
                                            'G': ('G',),
                                            'H': ('G',)})

    result &= verify_routing_table(net,'G',{'A': ('F',),
                                            'B': ('F',),
                                            'C': ('C',),
                                            'D': ('H',),
                                            'E': ('F',),
                                            'F': ('F',),
                                            'H': ('H',)})

    result &= verify_routing_table(net,'H',{'A': ('G',),
                                            'B': ('G',),
                                            'C': ('G',),
                                            'D': ('D',),
                                            'E': ('G',),
                                            'F': ('G',),
                                            'G': ('G',)})


    if result:
        print '...PASSED'

    ######################################################################
    # Test convergence time for link cost increases and decreases

    # format: (name of node, x coord, y coord)
    NODES =(('X',0,1), ('Y',1,0), ('Z',2,1))
    # format: (link start, link end)
    LINKS = (('X','Y'),('Y','Z'),('X','Z'))

    # make a network
    net = network(4000, NODES, LINKS,0)

    for l in net.links:
        if (l.end1.address == 'X' and l.end2.address == 'Y'):
            l.cost = 4
        elif (l.end1.address == 'Y' and l.end2.address == 'Z'):
            l.cost = 1
        elif (l.end1.address == 'X' and l.end2.address == 'Z'):
            l.cost = 12

    print "Testing convergence time on a simple network:"
    print '\t  Y'
    print '\t / \\'
    print '\tX---Z'
    print '\tCosts: XY=4 YZ=1 ZX=12'
    test_convergence_time(net)

    ######################################################################
    # test w/ two broken links => disconnected network
    print 'Testing',network,'with two broken links (disconnected network)'

    NODES =(('A',0,0), ('B',1,0), ('C',2,0), ('D',3,0),
            ('E',0,1), ('F',1,1), ('G',2,1), ('H',3,1))
    # format: (link start, link end)
    LINKS = (('A','B'),('A','E'),('B','F'),
             ('C','D'),('C','F'),('C','G'),
             ('D','G'),('D','H'),('F','G'),('G','H'))

    # make a network
    net = network(4000, NODES, LINKS, 0.0)

    for link in net.links:
        # break F<-->C link
        if link.end1.address=='C' and link.end2.address=='F':
            link.broken = True
        # break F<-->G link
        if link.end1.address=='F' and link.end2.address=='G':
            link.broken = True

    print 'Breaking links F-C and F-G (\'X\' marks the spot!)'
    print '\tA---B   C---D'
    print '\t|   | X | / |'
    print '\tE   F-X-G---H'
    print '\tlink costs = distance (1 or sqrt(2))'

    net.reset()
    net.step(count=10000)

    # specify dest:first-hop to be checked
    result = verify_routing_table(net,'A',{'B': ('B',),
                                           'C': (None,),
                                           'D': (None,),
                                           'E': ('E',),
                                           'F': ('B',),
                                           'G': (None,),
                                           'H': (None,),
                                           })
    result &= verify_routing_table(net,'B',{'A': ('A',),
                                            'C': (None,),
                                            'D': (None,),
                                            'E': ('A',),
                                            'F': ('F',),
                                            'G': (None,),
                                            'H': (None,),
                                            })
    result &= verify_routing_table(net,'C',{'A': (None,),
                                            'B': (None,),
                                            'D': ('D',),
                                            'E': (None,),
                                            'F': (None,),
                                            'G': ('G',),
                                            'H': ('D','G'),
                                            })
    result &= verify_routing_table(net,'D',{'A': (None,),
                                            'B': (None,),
                                            'C': ('C',),
                                            'E': (None,),
                                            'F': (None,),
                                            'G': ('G',),
                                            'H': ('H',),
                                            })
    result &= verify_routing_table(net,'E',{'A': ('A',),
                                            'B': ('A',),
                                            'C': (None,),
                                            'D': (None,),
                                            'F': ('A',),
                                            'G': (None,),
                                            'H': (None,),
                                            })
    result &= verify_routing_table(net,'F',{'A': ('B',),
                                            'B': ('B',),
                                            'C': (None,),
                                            'D': (None,),
                                            'E': ('B',),
                                            'G': (None,),
                                            'H': (None,),
                                            })
    result &= verify_routing_table(net,'G',{'A': (None,),
                                            'B': (None,),
                                            'C': ('C',),
                                            'D': ('D',),
                                            'E': (None,),
                                            'F': (None,),
                                            'H': ('H',),
                                            })
    result &= verify_routing_table(net,'H',{'A': (None,),
                                            'B': (None,),
                                            'C': ('D','G'),
                                            'D': ('D',),
                                            'E': (None,),
                                            'F': (None,),
                                            'G': ('G',),
                                            })
    if result:
        print '...PASSED'
        print

    print '**************************************************'
    print 'Tests complete for %s Task' % (net.__class__.__name__,)
    print '**************************************************'

    ######################################################################
    # Test network with cost that is too high.  THIS SHOULD BREAK.
    ######################################################################
    if (net.__class__.__name__ == "DVRouterNetwork"):
        print '\nOne more thing...'
        test_high_cost_network(network)

def test_high_cost_network(network):

    NODES = (('A',0,0), ('B',1,0), ('C',2,0), ('D',3,0))
    LINKS = (('A','B'), ('B','C'), ('C','D'))

    net = network(4000, NODES, LINKS, 0.0)

    infinity = None
    # just in case they define infinity differently per node
    for src in net.addresses.keys():
        if infinity == None:
            infinity = net.addresses[src].INFINITY
        else:
            infinity = max(infinity, net.addresses[src].INFINITY)

    # add one really high cost link
    for l in net.links:
        if (l.end1.address == 'B' and l.end2.address == 'C'):
            l.cost = infinity - 2

    print 'Testing a network path with very high cost'
    print 'A-----B--------------------------C-----D'
    print '   1      self.INFINITY-2           1   '

    net.reset()
    net.step(count=1000)

    result = verify_routing_table(net,'A',{'B': ('B',),
                                           'C': ('B',),
                                           'D': (None,)})

    result &= verify_routing_table(net,'B',{'A': ('A',),
                                            'C': ('C',),
                                            'D': ('C',)})

    result &= verify_routing_table(net,'C',{'A': ('B',),
                                            'B': ('B',),
                                            'D': ('D',)})

    result &= verify_routing_table(net,'D',{'A': (None,),
                                            'B': ('C',),
                                            'C': ('C',)})

    if (result):
        print "Routing Tables: (format: src, (dst1, link1), (dst2, link2), ...)"
        print "\tA, (B,B), (C,B), (D,None)"
        print "\tB, (A,A), (C,C), (D,C)"
        print "\tC, (A,B), (B,B), (D,D)"
        print "\tD, (A,None), (B,C), (C,C)"
        print 'Route from A<-->D exists in topology but your protocol says it doesn\'t!'
        print 'Why did this happen?  Give your answer in the pset.'

def test_convergence_time(net):

    # this is the correct routing table for the original network
    original_routing_table = dict()
    original_routing_table['X'] = {'Y': ('Y',), 'Z': ('Y',)}
    original_routing_table['Y'] = {'X': ('X',), 'Z': ('Z',)}
    original_routing_table['Z'] = {'X': ('Y',), 'Y': ('Y',)}

    # this is the correct table for *both* of the augmented networks
    augmented_routing_table = dict()
    augmented_routing_table['X'] = {'Y': ('Z',), 'Z': ('Z',)}
    augmented_routing_table['Y'] = {'X': ('Z',), 'Z': ('Z',)}
    augmented_routing_table['Z'] = {'X': ('X',), 'Y': ('Y',)}

    net.reset()
    net.step(count = 1000)

    # make sure they get the original routing table correct.  we don't care about convergence time yet
    result = 1
    for src in original_routing_table.keys():
        result &= verify_routing_table(net, src, original_routing_table[src])

    if (not result):
        print "error on original network"
        return

    # now change the cost from X -> Z to 2.  routing table should change
    for l in net.links:
        if (l.end1.address == 'X' and l.end2.address == 'Z'):
            l.cost = 2

    c_time, result = convergence_time(net, augmented_routing_table)

    if (not result):
        print "error in new network"
        return

    # first convergence time.  should be ~90
    print "Convergence time after changing Cost(Z->X) to 2: %d" % c_time

    if (c_time > 100):
        print "...Well, passed but took too long to converge"
    else:
        print "...PASSED"

    for l in net.links:
        if (l.end1.address == 'X' and l.end2.address == 'Z'):
            l.cost = 12

    print "Reset to original network"

    # reset the network back to the original; again, don't care about this convergence time
    net.step(1000)
    result = 1
    for src in original_routing_table.keys():
        result &= verify_routing_table(net, src, original_routing_table[src])
    
    if not result:
        print "error resetting network"
        return

    # change cost of X -> Y to 14.  routing table should change
    for l in net.links:
        if (l.end1.address == 'X' and l.end2.address == 'Y'):
            l.cost = 14

    # second convergence time.  should be ~390
    c_time, result = convergence_time(net, augmented_routing_table)
    if (result):
        print "Convergence time after changing Cost(X->Y) to 14: %d" % c_time
        if (c_time > 500):
            print "...Well, passed but took too long to converge"
        else:
            print "...PASSED"
    else:
        print "error in new network"

    print

def convergence_time(net, correct_routing_table):

    correct_count = 0

    for i in range(100000):
        net.step(count=1)
        result = 1
        for src in correct_routing_table.keys():
            result &= verify_routing_table(net, src, correct_routing_table[src], verbose=False)
        if (result):
            correct_count += 1
        else:
            correct_count = 0

        if (correct_count == 10):
            break

    return i-9, result
