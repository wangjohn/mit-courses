# 6.02 PSet: Time Division Multiple Access (TDMA)

import random, sys, wx, math, time
from optparse import OptionParser
from PS7_wsim import *
import matplotlib.pyplot as p

###############################################################

class TDMANode(WirelessNode):
    def __init__(self,location,network,retry):
        WirelessNode.__init__(self,location,network,retry)
        # any additional state or variables may be set here

    def channel_access(self,time,ptime,numnodes):
        return time % (numnodes*ptime) == self.get_id()*ptime

    def on_collision(self,packet):
        pass

    def on_xmit_success(self,packet):
        pass

################################################################

class TDMAWirelessNetwork(WirelessNetwork):
    def __init__(self,n,chantype,ptime,dist,load,retry,backoff,
		 skew=SOURCE_NOSKEW,qmax=0,simtime=10000):
        WirelessNetwork.__init__(self,n,chantype,ptime,dist,load,retry,backoff,
                                 skew,qmax,simtime)
    def make_node(self,loc,retry):
        return TDMANode(loc,self,retry)

################################################################

if __name__ == '__main__':
#    random.seed(6172538) # uncomment this line for repeatability
    parser = OptionParser()
    parser.add_option("-g", "--gui", action="store_true", dest="gui", 
                      default=False, help="show GUI")
    parser.add_option("-n", "--numnodes", type="int", dest="numnodes", 
                      default=16, help="number of nodes")
    parser.add_option("-t", "--simtime", type="int", dest="simtime", 
                      default=10000, help="simulation time")
    parser.add_option("-s", "--size", type="int", dest="ptime", 
                      default=1, help="packet size (in time units)")
    parser.add_option("-l", "--load", type="int", dest="load", 
                      default=100, help="total load % (in pkts/timeslot)")
    parser.add_option("-r", "--retry", action="store_true", dest="retry", 
                      default=False, help="show GUI")
    parser.add_option("-k", "--skew", action="store_true", dest="skew", 
                      default=False, help="skew source loads")

    (opt, args) = parser.parse_args()
    print 'Protocol: TDMA'
    wnet = TDMAWirelessNetwork(opt.numnodes,'TDMA',opt.ptime,
                               'exponential',opt.load,opt.retry,'None',
                               opt.skew,0,opt.simtime)
    
    if opt.gui == True:
        sim = NetSim()
        sim.SetNetwork(wnet)
        sim.MainLoop()
    else:
        wnet.step(opt.simtime)
        succ = []
        for node in wnet.nlist: succ.append(node.stats.success)
        for node in wnet.nlist:
            if node.stats.collisions > 0: 
                print "ERROR! TDMA should not have collisions"
        ind = numpy.arange(len(wnet.nlist))
        width = 0.35
        p.bar(ind, succ, width, color = 'r')
        p.ylabel('Throughput')
        p.xlabel('Node #')
        p.show()
