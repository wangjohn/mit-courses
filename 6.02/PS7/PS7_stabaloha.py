# 6.02 PSet: Stabilizing the Aloha protocol using random backoffs

import random, sys, wx, math, time
from optparse import OptionParser
from PS7_wsim import *
import matplotlib.pyplot as p

###############################################################

class AlohaNode(WirelessNode):
    def __init__(self,location,network,retry):
        WirelessNode.__init__(self,location,network,retry)
        ## Your code to initialize any additional state or variables goes here
        ## You can use self.network.pmin, self.network.pmax, etc.

        # for plots of collisions/success
        self.sent = []
        self.coll = []

        # initialize local probability of transmission
        self.p = self.network.pmax

    def channel_access(self,time,ptime,numnodes):
        if time % ptime == 0 and random.random() < self.p:
            return True
        return False

    def on_collision(self,packet):
        # for plots of collisions
        self.coll.append(self.network.time)
        self.p = max(self.p/2, self.network.pmin)

    def on_xmit_success(self,packet):
        # for plots of successful transmissions
        self.sent.append(self.network.time)
        self.p = min(self.p*2, self.network.pmax)

################################################################

class AlohaWirelessNetwork(WirelessNetwork):
    def __init__(self,n,chantype,ptime,dist,load,retry,backoff,
		 skew,qmax,pmax,pmin,simtime):
        self.pmax = pmax
        self.pmin = pmin
        WirelessNetwork.__init__(self,n,chantype,ptime,dist,load,retry,backoff,
                                 skew,qmax,simtime)

    def make_node(self,loc,retry):
        return AlohaNode(loc,self,retry)

################################################################

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-g", "--gui", action="store_true", dest="gui", 
                      default=False, help="show GUI")
    parser.add_option("-n", "--numnodes", type="int", dest="numnodes", 
                      default=16, help="number of nodes")
    parser.add_option("-t", "--simtime", type="int", dest="simtime", 
                      default=10000, help="simulation time")
    parser.add_option("-b", "--backoff", dest="backoff", 
                      default='Mine', help="backoff scheme (Mine, None)")
    parser.add_option("-s", "--size", type="int", dest="ptime", 
                      default=1, help="packet size (in time units)")
    parser.add_option("-p", "--pmax", type="float", dest="pmax", 
                      default=1.0, help="max probability of xmission")    
    parser.add_option("-q", "--pmin", type="float", dest="pmin", 
                      default=0.0, help="min probability of xmission")    
    parser.add_option("-l", "--load", type="int", dest="load", 
                      default=100, help="total load % (in pkts/timeslot)")
    parser.add_option("-r", "--retry", action="store_true", dest="retry", 
                      default=False, help="show GUI")
    parser.add_option("-k", "--skew", action="store_true", dest="skew", 
                      default=False, help="skew source loads")

    (opt, args) = parser.parse_args()
    print 'Protocol: Aloha with stabilization'
    wnet = AlohaWirelessNetwork(opt.numnodes,'Aloha',opt.ptime,
                                'exponential',opt.load,opt.retry,opt.backoff,
                                opt.skew,0,opt.pmax,opt.pmin,opt.simtime)
    
    if opt.gui == True:
        sim = NetSim()
        sim.SetNetwork(wnet)
        sim.MainLoop()
    else:
        wnet.step(opt.simtime)
        plot_data(wnet)         # in PS8_wsim
