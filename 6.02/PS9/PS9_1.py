# 6.02 PSet: Reliable Transport Protocols.
# This file is for a stop-and-wait protocol that achieves reliable, in-order,
# exactly-once data delivery.
import random,sys
from optparse import OptionParser
from PS9_netsim import *

# ReliableSenderNode extends Router to implement a reliable sender
class ReliableSenderNode(Router):
    def __init__(self,location,qsize,address=None):
        Router.__init__(self,location,qsize,address=address)
        self.stream_destination = None  # where to send reliable packet stream
        self.reset()

    def reset(self):
        Router.reset(self)
        self.srtt = 0
        self.rttdev = -1
        self.timeout = 20    # arbitrary initial value
        ## Your initialization code here.  We've already initialized
        ## self.srtt, self.rttdev, self.timeout above.  Initialize anything
        ## else you need here.
        self.alpha = 0.5
        self.beta = 0.25

        self.saved_package = None
        self.seq_num = 1

    def __repr__(self):
        return 'ReliableSenderNode<%s>' % str(self.address)

    def OnClick(self,which):
        if which == 'left':
            if self.network.time > 1:
                print Node.__repr__(self) + \
                    " srtt %.1f rttdev %.1f timeout %.1f" \
                    % (self.srtt, self.rttdev, self.timeout)
            else:
                print self.__repr__()

    # Send a packet at the current time, with specified seqnum,
    # timestamp, and color ('black', 'gray', 'yellow', etc.).  You may
    # want to pick different colors for retransmissions.
    def send_pkt(self, time, seqnum, pkt_timestamp, color):
        xmit_packet = self.network.make_packet(
            self.address, self.stream_destination, 'DATA', time, 
            seqnum=seqnum, timestamp=pkt_timestamp, color=color)
        self.forward(xmit_packet)
        return xmit_packet

    def transmit(self, time):
        Router.transmit(self,time)
        if self.stream_destination is not None and time >= 1:
            self.reliable_send(time)

    # Implement the stop-and-wait protocol.  This function is called once each
    # time-slot.  Decide if you should send a packet or not, and if you decide
    # to send a packet, decide if it should be a retransmission.
    #
    # Please note the following useful hints:
    # 1. You may use p.start to get (and set) the time at which packet p was 
    # sent, which is useful to determine if the sender should retransmit p.
    # 2. Call self.send_pkt() to send a packet specifying the arguments as 
    # in the send_pkt() template shown above.  This method returns the packet.
    def reliable_send(self, time):
        if self.saved_package:
            if time - self.saved_package.start > self.timeout:
                self.saved_package.start = time
                self.send_pkt(time, self.saved_package.properties.get('seqnum'), time, "red")
        else:
            self.saved_package = self.send_pkt(time, self.seq_num, time, "black")
            self.saved_package.start = time
            self.seq_num += 1

    # An ACK just arrived; process it.  Remember to call calc_timeout with the
    # appropriate information.
    def process_ack(self, time, acknum, timestamp):
        if acknum == self.saved_package.properties.get('seqnum'):
            self.calc_timeout(time, timestamp)
            self.saved_package = None

    # Update RTT statistics and compute the sender's timeout value.  The 
    # current time and the timestamp echoed in the ACK from the receiver 
    # are arguments to this function.
    def calc_timeout(self, time, pkt_timestamp):
        diff = time - pkt_timestamp
        self.srtt = self.alpha*diff + (1-self.alpha)*self.srtt
        dev = abs(diff - self.srtt)
        self.rttdev = self.beta*dev + (1-self.beta)*self.rttdev
        self.timeout = self.srtt + 3.5*self.rttdev

    # Process an ACK (and ignore any other packet type)
    def receive(self,p,link,time):
        if p.type != 'ACK': return
        acknum = p.properties.get('seqnum', None)
        pkt_timestamp = int(p.properties.get('timestamp', None))
        if self.network.verbose == True:
            print "t=%d %s received ACK %d" % (time, self.address, acknum)
        self.process_ack(time, acknum, pkt_timestamp)


# ReliableReceiverNode extends Router to implement reliable
# receiver functionality with path vector routing.
class ReliableReceiverNode(Router):
    def __init__(self,location,qsize,address=None):
        Router.__init__(self,location,qsize,address=address)
        self.reset()

    def reset(self):
        Router.reset(self)
        self.app_seqnum = 0
        self.lastprinttime = 0
        ## Your code for initializing the receiver should go here.
        self.queue = {}

    def __repr__(self):
        return 'ReliableReceiverNode<%s>' % str(self.address)

    def OnClick(self,which):
        if which == 'left':
            if self.network.time > 1:
                print Node.__repr__(self) + \
                      " received %d (%.2f packets/timestep)" % (self.app_seqnum,
                      float(self.app_seqnum)/(self.network.time - 1))
            else:
                print self.__repr__()

    def send_ack(self, sender, time, seqnum, pkt_timestamp):
        ack = self.network.make_packet(self.address, sender, 'ACK', time,
                                       seqnum=seqnum, timestamp=pkt_timestamp,
                                       color='blue')
        self.forward(ack);

    def receive(self, p, link, time):
        seqnum = p.properties.get('seqnum', None)
        pkt_timestamp = p.properties.get('timestamp', None)
        if p.type == 'DATA':
            self.reliable_recv(p.source, time, seqnum, pkt_timestamp)

    # Process a DATA packet from "sender" with "seqnum" and 
    # specified sender timestamp.  The current time is "time".  
    # Call send_ack with the relevant arguments.  Then call
    # self.app_receive() IF AND ONLY IF the seqnum is one larger than
    # the last one (when you last called app_receive()).  The idea is
    # to deliver the DATA packets to the application in exact incrementing
    # sequence order without any duplicates or gaps.
    def reliable_recv(self, sender, time, seqnum, pkt_timestamp):
        self.send_ack(sender, time, seqnum, pkt_timestamp)
        self.queue[seqnum] = time

        if self.app_seqnum + 1 in self.queue:
            self.app_receive(self.app_seqnum+1, self.queue[self.app_seqnum+1])
            del self.queue[self.app_seqnum]

    # app_receive() should be called by receive() for each data packet that 
    # arrives in order of incrementing sequence number (i.e., without gaps)
    def app_receive(self, seqnum, time):
        try:
            assert seqnum == self.app_seqnum + 1, \
                "ERROR: Expected DATA packet #%d, got #%d" \
                % (self.app_seqnum+1,seqnum)
            if self.network.verbose == True:
                print "t=%d %s app_receive pkt %d" % (time,self.address,seqnum)
                if time - self.lastprinttime >= 100:
                    print "t=%d rcvr %s app_receive %d throughput: %.2f pkts/timestep" % (time, self.address, self.app_seqnum, float(self.app_seqnum)/(self.network.time - 1))
                    self.lastprinttime = time
        except AssertionError, a:
            print "*BUG* in protocol: %s" % a
        self.app_seqnum = seqnum

class MyNetwork(RouterNetwork):
    def __init__(self,SIMTIME,NODES,LINKS,QSIZE,LOSSPROB,XRATE,VERBOSE):
        self.qsize = QSIZE
        self.lossprob = LOSSPROB
        self.xrate = XRATE
        self.verbose = VERBOSE
        RouterNetwork.__init__(self,SIMTIME,NODES,LINKS)

    def make_node(self,loc,address=None):
        if address == 'S':
            return ReliableSenderNode(loc,self.qsize,address)
        elif address == 'R':
            return ReliableReceiverNode(loc,self.qsize,address)
        else:
            if self.xrate == 0.0 or len(NODES) == 2:
                return Router(loc,self.qsize,address=address)            
            if self.xrate > 0.0:
                numhops = len(NODES) - 1
                if address == str(numhops - 1):
                    print 'xtraffic node', address
                    return CrossTrafficNode(loc,self.qsize,address,
                                            self.xrate,'R')
                else:
                    return Router(loc,self.qsize,address=address)

    def make_link(self,n1,n2):
        return LossyLink(n1,n2,self.lossprob)

    # reset network to its initial state
    def reset(self):
        # parent class handles the details
        Network.reset(self)
        # insert a single packet into the network. Since we don't have code
        # to deliver the packet this just keeps the simulation alive...
        src = self.addresses['S']
        src.stream_destination = 'R'
        src.add_packet(self.make_packet('S','R','DATA',1))

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-t", "--simtime", type="int", dest="simtime", 
                      default=10000, help="simulation time (default: 10000)")
    parser.add_option("-q", "--qsize", type="int", dest="qsize",
                      default=10, help="queue size at each link (default: 10)")
    parser.add_option("-l", "--loss", type="float", dest="lossprob", 
                      default=0.01, help="per-link loss prob for DATA and ACK packets (default: 0.01)")
    parser.add_option("-n", "--numhops", type="int", dest="numhops", 
                      default=6, help="number of hops between sender S and receiver R (default: 6)")
    parser.add_option("-b", "--bottleneck", type="float", dest="bneck_rate", 
                      default=1, help="bottleneck link rate (link to R)")
    parser.add_option("-x", "--cross", type="float", dest="xrate",
                      default=0.0, help="set cross traffic (pkts/slot) (default: 0)")
    parser.add_option("-g", "--gui", action="store_true", dest="gui", 
                      default=False, help="show GUI")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      default=False, help="print each DATA/ACK/loss/drop event")
    
    (opt, args) = parser.parse_args()
    # Build the deterministic test network.
    # We're making a chain of length opt.numhops here, between S and R.
    # Format: (name of node, x coord, y coord).
    NODES = [('S', 0, 0)]
    LINKS = []
    prevnode = 'S'
    for i in xrange(1, opt.numhops):
        NODES.append((str(i), i, 0))
        LINKS.append((prevnode, str(i)))
        prevnode = str(i)
    NODES.append(('R', opt.numhops, 0))
    LINKS.append((prevnode, 'R'))

    # make a network
    net = MyNetwork(opt.simtime, NODES, LINKS, opt.qsize, \
                    opt.lossprob, opt.xrate, opt.verbose)

    bneck_node = net.find_node(opt.numhops-1, 0)
    bneck_link = bneck_node.getlink('R')
    bneck_link.set_rate(opt.bneck_rate)

    for node in net.nlist:
        if node.address == 'S':
            if opt.numhops > 1:
                node.routes['R'] = node.getlink('1')
            else:
                node.routes['R'] = node.getlink('R')
            for i in xrange(1, opt.numhops):
                node.routes[str(i)] = node.getlink('1')
        elif node.address == 'R':
            if opt.numhops > 1:
                node.routes['S'] = node.getlink(str(opt.numhops - 1))
            else:
                node.routes['S'] = node.getlink('S')

            for i in xrange(1, opt.numhops):
                node.routes[str(i)] = node.getlink(str(opt.numhops - 1))
        else:
            if node.address == '1':
                node.routes['S'] = node.getlink('S')
            else:
                node.routes['S'] = node.getlink(str(int(node.address) - 1))
            if int(node.address) == opt.numhops - 1:
                node.routes['R'] = node.getlink('R')
            else:
                node.routes['R'] = node.getlink(str(int(node.address) + 1))
                
            for i in xrange(1, opt.numhops):
                if int(node.address) < i:
                    node.routes[str(i)] = node.getlink(str(int(node.address)+1))
                elif int(node.address) > i:
                    node.routes[str(i)] = node.getlink(str(int(node.address)-1))

    if opt.gui == True:
        # setup graphical simulation interface
        sim = NetSim()
        sim.SetNetwork(net)
        sim.MainLoop()
    else:
        net.reset()
        net.step(opt.simtime)
        source = net.find_node(0,0)
        print "Sender S: srtt %.1f rttdev %.1f timeout %.1f" % (source.srtt, source.rttdev, source.timeout)
        sink = net.find_node(opt.numhops,0)
        print "Receiver R: throughput %.2f pkts/timeslot recd %d in time %d" % (float(sink.app_seqnum)/(net.time - 1), sink.app_seqnum, net.time-1)
        totaldrop = 0
        for node in net.nlist: totaldrop = totaldrop + node.qdrop 
        totalloss = 0
        for link in net.links: totalloss = totalloss + link.linkloss 
        print "\tqueue drops: %d pkts link losses %d pkts" % (totaldrop, totalloss)
