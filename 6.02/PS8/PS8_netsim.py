# NetSim: network simulator for routing and transport protocols (6.02)
import random, sys, wx, math, time

################################################################################
#
# Node -- a network node
#
# Node.reset()        -- reset node's state at start of simulation
# Node.add_packet(p)  -- add packet to node's transmit queue
# Node.receive(p)     -- called to process packet sent to this node
# Node.transmit(time) -- allow node to send packets at current time
# Node.forward(p)     -- lookup route for pkt p and send it on appropriate link
# Node.arrived_on(p)  -- returns link that packet p just arrived on
#
################################################################################

class Node:
    def __init__(self,location,address=None):
        self.location = location
        if address is None: self.address = location
        else: self.address = address
        self.links = []  # links that connect to this node
        self.packets = []  # packets to be processed this timestep
        self.transmit_queue = []  # packets to be transmitted from this node
        self.receive_queue = []  # packets received by this node
        self.properties = {}
        self.network = None  # will be filled in later
        self.nsize = 0       # filled in by draw method

    def __repr__(self):
        return 'Node<%s>' % str(self.address)

    def address(self):
        return self.address

    # reset to initial state
    def reset(self):
        for l in self.links: l.reset()
        self.transmit_queue = []   # nothing to transmit
        self.receive_queue = []    # nothing received
        self.queue_length_sum = 0  # reset queue statistics
        self.queue_length_max = 0
	self.neighbors.clear()
#	self.LSA.clear()
        self.routes.clear()
        self.routes[self.address] = 'Self'
        self.properties.clear()

    # keep track of links that connect to this node
    def add_link(self,l):
        self.links.append(l)

    # add a packet to be transmitted from this node.  Transmit queue
    # is kept ordered by packet start time.
    def add_packet(self,p):
        index = 0
        for pp in self.transmit_queue:
            if p.start < pp.start:
                self.transmit_queue.insert(index,p)
                break
            else: index += 1
        else: self.transmit_queue.append(p)

    # first phase of simulation timestep: collect one packet from
    # each incoming link
    def phase1(self):
        self.packets = [link.receive(self) for link in self.links]

    # second phase of simulation timestep: process arriving packets    
    def phase2(self,time):
        # process each arriving packet
        for link_p in self.packets:
            if link_p is not None: self.process(link_p[1],link_p[0],time)
        self.packets = []

        # give this node a chance to transmit some packets
        self.transmit(time)

        # compute number of packets this node has queued up on its
        # outgoing links.  So we can compute queue length stats, keep
        # track of max and sum.
        pending = 0
        for link in self.links: pending += link.queue_length(self)
        self.queue_length_sum += pending
        self.queue_length_max = max(self.queue_length_max,pending)

        # report total number of packets that need processing
        return pending + len(self.transmit_queue)

    # default processing for packets addressed to this node -- just
    # keep a list of them
    def receive(self,p,link):
        self.receive_queue.append(p)

    # called each simulation cycle to give this node a chance to send
    # some packets.  Default behavior: source packets from a transmit
    # queue based on packets' specified start time.
    def transmit(self,time):
        # look for packets on this node's transmit queue whose time has come
        while len(self.transmit_queue) > 0:
            if self.transmit_queue[0].start <= time:
                self.process(self.transmit_queue.pop(0),None,time)
            else: break

    # OVERRIDE: forward packet onto proper outgoing link.  Default behavior
    # is to pick a link at random!
    def forward(self,p):
        link = random.choice(self.links)
        link.send(self,p)

    # deal with each packet arriving at or sent from this node
    def process(self,p,link,time):
        if p.destination == self.address:
            # it's for us!  Just note time of arrival and pass it receive
            p.finish = time
            self.receive(p,link)
        else:
            p.add_hop(self,time)
            self.forward(p)

    #########################################################
    # support for graphical simulation interface
    #########################################################

    # convert our location to screen coordinates
    def net2screen(self,transform):
        return net2screen(self.location,transform)

    # draw ourselves on the screen as a colored square with black border
    def draw(self,dc,transform):
        self.nsize = transform[0]/16
        loc = self.net2screen(transform)
        dc.SetPen(wx.Pen('black',1,wx.SOLID))
        dc.SetBrush(wx.Brush(self.properties.get('color','black')))
        dc.DrawRectangle(loc[0]-self.nsize,loc[1]-self.nsize,
                         2*self.nsize+1,2*self.nsize+1)
        label = str(self.address)
        dc.SetTextForeground('light grey')
        dc.SetFont(wx.Font(max(4,self.nsize*2),wx.SWISS,wx.NORMAL,wx.NORMAL))
        dc.DrawText(label,loc[0]+self.nsize+2,loc[1]+self.nsize+2)

        if len(self.transmit_queue) > 0:
            self.transmit_queue[0].draw(dc,transform,
                                        loc[0]-2*self.nsize,loc[1]-2*self.nsize)

    # if pos is near us, return status string
    def nearby(self,pos):
        dx = self.location[0] - pos[0]
        dy = self.location[1] - pos[1]
        if abs(dx) < .1 and abs(dy) < .1:
            return self.status()
        elif len(self.transmit_queue) > 0:
            if (dx > .1 and dx < .2) and (dy > .1 and dy < .2):
                return 'Unsent '+self.transmit_queue[0].status()
        else:
            return None

    def click(self,pos,which):
        dx = self.location[0] - pos[0]
        dy = self.location[1] - pos[1]
        if abs(dx) < .1 and abs(dy) < .1:
            self.OnClick(which)
            return True
        else:
            return False

    def OnClick(self,which):
        pass
        
    # status report to appear in status bar when pointer is nearby
    def status(self):
        return self.__repr__()

################################################################################
#
# Link -- a communication link between two network nodes
#
# Link.queue_length(n) -- count undelivered packets sent by specified node
# Link.other_end(n)    -- return node at other end of link
# Link.receive(n)      -- return one packet destined for specified node (or None)
# Link.send(n,p)       -- send packet to other end of link
#
################################################################################
class Link:
    def __init__(self,n1,n2):
        self.end1 = n1   # node at one end of the link
        self.end2 = n2   # node at the other end
        self.q12 = []    # queue of packets to be delivered to end2
        self.q21 = []    # queue of packets to be delivered to end1
        self.cost = 1    # by default, cost is 1
        self.costrepr = str(self.cost) # representing cost in GUI
        self.network = None  # will be filled in later
        n1.add_link(self)
        n2.add_link(self)
        self.broken = False

    def __repr__(self):
        return 'link(%s<-->%s) (%.1f)' % (self.end1,self.end2, self.cost)

    def reset(self):
        self.q12 = []    # reset packet queues
        self.q21 = []

    # return count of undelivered packets sent by specified node
    def queue_length(self,n):
        if n == self.end1: return len(self.q12)
        elif n == self.end2: return len(self.q21)
        else: raise Exception,'bad node in Link.queue_length'

    # return (link, packet) destined for specified node (or None)
    def receive(self,n):
        if n == self.end1:
            if len(self.q21) > 0: return (self, self.q21.pop(0))
            else: return None
        elif n == self.end2:
            if len(self.q12): return (self, self.q12.pop(0))
            else: return None
        else: raise Exception,'bad node in Link.receive'

    # send one packet from specified node
    def send(self,n,p):
        if self.broken: return
        if n == self.end1: self.q12.append(p)
        elif n == self.end2: self.q21.append(p)
        else: raise Exception,'bad node in Link.send'

    #########################################################
    # support for graphical simulation interface
    #########################################################

    def draw(self,dc,transform):
        self.nsize = transform[0]/16
        n1 = self.end1.net2screen(transform)
        n2 = self.end2.net2screen(transform)
        dc.SetPen(wx.Pen('black',1,wx.SOLID))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawLine(n1[0],n1[1],n2[0],n2[1])
        # show link's cost near it
        dc.SetTextForeground('light grey')
        dc.SetFont(wx.Font(max(4,self.nsize*2),wx.SWISS,wx.NORMAL,wx.NORMAL))
        dc.DrawText(self.costrepr,(n1[0]+n2[0])/2,(n1[1]+n2[1])/2)

        if self.broken:
            dc.SetPen(wx.Pen('red',3,wx.SOLID))
            midx = (n1[0]+n2[0])/2
            midy = (n1[1]+n2[1])/2
            offset = 0.1 * transform[0]
            dc.DrawLine(midx-offset,midy-offset,midx+offset,midy+offset)
            dc.DrawLine(midx+offset,midy-offset,midx-offset,midy+offset)

        # draw first packet in each queue
        if len(self.q21) > 0:
            self.q21[0].draw_on_link(dc,transform,n1,n2)
        if len(self.q12) > 0:
            self.q12[0].draw_on_link(dc,transform,n2,n1)

    def nearby(self,pos):
        # check for packet icons
        msg = None
        if len(self.q21) > 0:
            msg = self.q21[0].nearby(pos,self.end1.location,self.end2.location)
        if msg is None and len(self.q12) > 0:
            msg = self.q12[0].nearby(pos,self.end2.location,self.end1.location)
        return msg

    def click(self,pos,which):
        if nearby(pos,self.end1.location,self.end2.location,.1):
            self.broken = not self.broken
            if self.broken:
                self.reset()
            return True
        return False

######################################################################
"""A link with cost (higher cost means worse link)
"""
######################################################################
class CostLink(Link):
    def __init__(self,n1,n2):
        Link.__init__(self,n1,n2)
        self.nsize = 0                # filled in by draw method
        loc1 = n1.location
        loc2 = n2.location
        dx2 = (loc1[0] - loc2[0])*(loc1[0] - loc2[0])
        dy2 = (loc1[1] - loc2[1])*(loc1[1] - loc2[1])
        self.cost = math.sqrt(dx2 + dy2)
#        self.cost = random.randint(1,10)
        if (int(self.cost) == self.cost): 
            self.costrepr = str(self.cost)
        else:
            self.costrepr = "sqrt(" + str(dx2+dy2) + ")"

    # method to set the cost of a link
    def set_cost(self, cost):
        self.cost = cost

class LossyCostLink(CostLink):
    def __init__(self,n1,n2,lossprob):
        CostLink.__init__(self,n1,n2)
        self.lossprob = lossprob
        self.linkloss = 0       # number of pkts lost on link

    def send(self,n,p):
        # we lose packets with probability self.lossprob
        if random.random() > self.lossprob:
            CostLink.send(self,n,p)
        else:
            self.linkloss = self.linkloss + 1 # stats on number of losses

################################################################################
#
# Packet -- data to be sent from one network node to another
#
# Packet.arrived_from() -- return node this packet just arrived from
#
################################################################################
class Packet:
    def __init__(self,src,dest,type,start,**props):
        self.source = src     # address of node that originated packet
        self.destination = dest  # address of node that should receive packet
        self.type = type
        self.start = start # simulation time at which packet was transmitted
        self.finish = None # simulation time at which packet was received
        self.route = []    # list of nodes this packet has visited
        self.network = None     # will be filled in later
        self.properties = props.copy()

    def __repr__(self):
        return 'Packet<%s to %s> type %s' % (self.source,self.destination,self.type)

    # keep track of where we've been
    def add_hop(self,n,time):
        self.route.append((n,time))

    #########################################################
    # support for graphical simulation interface
    #########################################################

    def draw(self,dc,transform,px,py):
        c = self.properties.get('color','blue')
        dc.SetPen(wx.Pen(c,1,wx.SOLID))
        dc.SetBrush(wx.Brush(c))
        radius = transform[0]/16
        dc.DrawCircle(px,py,radius)

    def draw_on_link(self,dc,transform,n1,n2):
        px = n1[0] + int(0.2*(n2[0] - n1[0]))
        py = n1[1] + int(0.2*(n2[1] - n1[1]))
        self.draw(dc,transform,px,py)

    def nearby(self,pos,n1,n2):
        px = n1[0] + 0.2*(n2[0] - n1[0])
        py = n1[1] + 0.2*(n2[1] - n1[1])
        dx = px - pos[0]
        dy = py - pos[1]
        if abs(dx) < .1 and abs(dy) < .1:
            return self.status()
        else: return None

    def status(self):
        return self.__repr__()        

################################################################################
#
# Network -- a collection of network nodes, links and packets
#
# Network.make_node(loc,address=None)  -- make a new network node
# Network.add_node(x,y,address=None)   -- add a new node at specified location
# Network.find_node(x,y)               -- return node at given location
# Network.map_node(f,default=0)        -- see below
# Network.make_link(n1,n2)             -- make a new link between n1 and n2
# Network.add_link(x1,y2,x2,y2)        -- add link between specified nodes
#
# Network.make_packet(src,dst,type,start,**props)  -- make a new packet
# Network.duplicate_packet(p)          -- duplicate a packet
#
# Network.reset()                      -- initialize network state
# Network.step(count=1)                -- simulate count timesteps
#
################################################################################
class Network:
    def __init__(self,simtime):
        self.nodes = {}
        self.addresses = {}
        self.nlist = []
        self.links = []
        self.time = 0
        self.pending = 0
        self.packets = []
        self.npackets = 0
        self.max_x = 0
        self.max_y = 0
        self.simtime = simtime
        self.playstep = 1.0     # 1 second play step by default

        self.numnodes = 0       # TBD

    # override to make your own type of node
    def make_node(self,loc,address=None):
        return Node(loc,address=address)

    # add a node to the network
    def add_node(self,x,y,address=None):
        n = self.find_node(x,y)
        if n is None:
            n = self.make_node((x,y),address=address)
            n.network = self
            if address is not None:
                self.addresses[address] = n
            self.nlist.append(n)
            ynodes = self.nodes.get(x,{})
            ynodes[y] = n
            self.nodes[x] = ynodes
            self.max_x = max(self.max_x,x)
            self.max_y = max(self.max_y,y)
        return n

    def set_nodes(self,n):
        self.numnodes = n

    # locate a node given its location
    def find_node(self,x,y):
        ynodes = self.nodes.get(x,None)
        if ynodes is not None:
            return ynodes.get(y,None)
        return None

    # apply f to each network node in top-to-bottom, left-to-right
    # order.  Returns list of return values (default value is used
    # if a particular grid point doesn't contain a node).  Useful
    # for gathering statistical data that can be processed by Matlab.
    def map_node(self,f,default=0):
        result = []
        for row in xrange(self.max_y+1):
            for col in xrange(self.max_x+1):
                node = self.find_node(row,col)
                if node: result.append(f(node))
                else: result.append(default)
        return result

    # override to make your own type of link
    def make_link(self,n1,n2):
        return Link(n1,n2)

    # add a link between nodes at the specified locations
    def add_link(self,x1,y1,x2,y2):
        n1 = self.find_node(x1,y1)
        n2 = self.find_node(x2,y2)
        if n1 is not None and n2 is not None:
            link = self.make_link(n1,n2)
            link.network = self
            self.links.append(link)

    # override to make your own type of packet
    def make_packet(self,src,dest,type,start,**props):
        p = Packet(src,dest,type,start,**props)
        p.network = self
        self.packets.append(p)
        self.npackets += 1
        return p

    # duplicate existing packet
    def duplicate_packet(self,old):
        return self.make_packet(old.source,old.destination,old.type,self.time,
                                **old.properties)

    # compute manhattan distance between two nodes
    def manhattan_distance(self,n1,n2):
        dx = n1[0] - n2[0]
        dy = n1[1] - n2[1]
        return abs(dx) + abs(dy)

    # return network to initial state
    def reset(self):
        for n in self.nlist: n.reset()
        self.time = 0
        self.pending = 0
        self.packets = []
        self.npackets = 0
        self.pending = 1    # ensure at least simulation step

    # simulate network one timestep at a time.  At each timestep
    # each node processes one packet from each of its incoming links
    def step(self,count=1):
        stop_time = self.time + count
        while self.time < stop_time and self.pending > 0:
            # phase 1: nodes collect one packet from each link
            for n in self.nlist: n.phase1()

            # phase 2: nodes process collected packets, perhaps sending
            # some to outgoing links.  Also nodes can originate packets
            # of their own.
            self.pending = 0
            for n in self.nlist: self.pending += n.phase2(self.time)

            # increment time
            self.time += 1
        return self.pending

    #########################################################
    # support for graphical simulation interface
    #########################################################

    def draw(self,dc,transform):
        # draw links
        for link in self.links:
            link.draw(dc,transform)

        # draw nodes
        for node in self.nlist:
            node.draw(dc,transform)

    def click(self,pos,which):
        for node in self.nlist:
            if node.click(pos,which):
                return True
        else:
            for link in self.links:
                if link.click(pos,which):
                    return True
        return False

    def status(self,statusbar,pos):
        for node in self.nlist:
            msg = node.nearby(pos)
            if msg: break
        else:
            for link in self.links:
                msg = link.nearby(pos)
                if msg: break
            else:
                msg = ''
        statusbar.SetFieldsCount(4)
        statusbar.SetStatusWidths([80,80,80,-1])
        statusbar.SetStatusText('Time: %d' % self.time, 0)
        statusbar.SetStatusText('Pending: %s' % self.pending, 1)
        statusbar.SetStatusText('Total: %s' % self.npackets, 2)
        statusbar.SetStatusText('Status: %s' % msg, 3)

grid_node_names = ['alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot',
             'golf', 'hotel', 'india', 'juliet', 'kilo', 'lima', 'mike',
             'november', 'oscar', 'papa', 'quebec', 'romeo', 'sierra',
             'tango', 'uniform', 'victor', 'whiskey', 'xray', 'yankee',
             'zulu']

class GridNetwork(Network):
    # make a grid network of specified size
    def __init__(self,nrows,ncols):
        Network.__init__(self)

        # make a manhattan grid of nodes
        for r in xrange(nrows):
            for c in xrange(ncols):
                index = r*ncols + c
                addr = grid_node_names[index % len(grid_node_names)]
                if index >= len(grid_node_names):
                    addr += str(index / len(grid_node_names))
                self.add_node(r,c,address=addr)

        for r in xrange(nrows):
            # horizontal links first
            for c in xrange(ncols):
                if c > 0: self.add_link(r,c,r,c-1)
            # then vertical links
            for c in xrange(ncols):
                if r > 0: self.add_link(r,c,r-1,c)

################################################################################
#
# NetSim -- a graphical front end for network simulations
#
################################################################################

# convert from network to screen coords
# transform = (scale,(xoffset,yoffset))
def net2screen(loc,transform):
    return (transform[1][0]+loc[0]*transform[0],
            transform[1][1]+loc[1]*transform[0])

# convert from screen to network coords
# transform = (scale,(xoffset,yoffset))
def screen2net(loc,transform):
    return (float(loc[0]-transform[1][0])/transform[0],
            float(loc[1]-transform[1][1])/transform[0])

# is pt within distance of line between end1 and end2?
def nearby(pt,end1,end2,distance):
    if end1[0] == end2[0]:    # vertical wire
        if abs(pt[0] - end1[0]) > distance:
            return False
        y1 = min(end1[1],end2[1])
        y2 = max(end1[1],end2[1])
        return pt[1] >= y1 - distance and pt[1] <= y2 + distance
    elif end1[1] == end2[1]:  # horizontal wire
        if abs(pt[1] - end1[1]) > distance:
            return False
        x1 = min(end1[0],end2[0])
        x2 = max(end1[0],end2[0])
        return pt[0] >= x1 - distance and pt[0] <= x2 + distance
    else:  # non-manhattan wire
        # slope and intercept for line between end1 and end2
        slope1 = float(end1[1] - end2[1])/(end1[0] - end2[0])
        intercept1 = float(end1[1]) - slope1*end1[0]
        # slope and intercept for perpendicular line passing through pt
        slope2 = -1/slope1
        intercept2 = float(pt[1]) - slope2*pt[0]
        # x coordinate of intersection of those two lines
        xi = (intercept2 - intercept1)/(slope1 - slope2)
        if xi < min(end1[0],end2[0]) or xi > max(end1[0],end2[0]):
            return False
        dx = pt[0] - xi;
        dy = pt[1] - (slope2*xi + intercept2)
        return (dx*dx) + (dy*dy) <= distance*distance        

# A panel that displays a network
class NetPanel(wx.Panel):
    def __init__(self,parent,statusbar):
        wx.Panel.__init__(self,parent,-1,wx.DefaultPosition,(10,10))
        self.SetBackgroundColour('white')
        self.SetMinSize((100,100))
        self.statusbar = statusbar
        self.network = None
        self.setupBuffer = False
        self.redraw = False
        self.playmode = False
        self.lastplaytime = 0
        self.transform = (2,(0,0))
        self.SetupBuffer()
        self.Bind(wx.EVT_PAINT,self.OnPaint)
        self.Bind(wx.EVT_SIZE,self.OnSize)
        self.Bind(wx.EVT_IDLE,self.OnIdle)
        self.Bind(wx.EVT_MOTION,self.OnMotion)
        self.Bind(wx.EVT_LEFT_DOWN,self.OnLeftClick)

    def SetupBuffer(self):
        # use an off-screen drawing buffer to reduce flicker
        size = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(size.width,size.height)
        self.setupBuffer = False
        self.redraw = True  # fill up new buffer

    def OnSize(self,event):
        # wait until IDLE to actually do refresh just in case there
        # are multiple SIZE events in a row that we can roll into one
        self.setupBuffer = True

    def OnClick(self,event,which):
        pos = screen2net(event.GetPositionTuple(),self.transform)
        if self.network.click(pos,which):
            self.redraw = True

    def OnLeftClick(self,event):
        self.OnClick(event,'left')

    def OnMotion(self,event):
        pos = screen2net(event.GetPositionTuple(),self.transform)
        self.network.status(self.statusbar,pos)

    def OnIdle(self,event):
        if self.setupBuffer:
            # create a new drawing buffer
            self.SetupBuffer()
        if self.redraw:
            self.DrawNetwork()
            self.Refresh(False)
            self.redraw = False
            self.network.status(self.statusbar,(-10,-10))                
        if self.playmode == True:
            self.redraw = True
            curtime = time.clock()
            delta = curtime - self.lastplaytime
            if delta > self.network.playstep:
                if self.network.simtime > self.network.time:
                    self.network.step(1)
                    self.lastplaytime = curtime
                else:
                    self.playmode = False
            event.RequestMore()

    def OnPaint(self,event):
        # just refresh the screen from our buffer
        dc = wx.BufferedPaintDC(self,self.buffer)        

    def OnReset(self,event):
        self.network.reset()
        self.network.status(self.statusbar,(-10,-10))
        self.redraw = True

    def OnStep(self,event):
        button = event.GetEventObject().GetLabel()
        arg = button[button.find(' '):]
	if arg == ' all': count = self.network.simtime-self.network.time
	else: count = int(arg)
        self.network.step(count=count)
        self.network.status(self.statusbar,(-10,-10))
        self.redraw = True

    def OnPlay(self,event):
        self.playmode = True

    def OnPause(self,event):
        self.playmode = False

    def OnNNodes(self,event):
        nnodes = event.GetEventObject().GetValue()
        self.network.set_nodes(nnodes)
        self.redraw = True

    def OnExit(self,event):
        self.network.status(self.statusbar,(-10,-10))
        self.redraw = True
	sys.exit(1)

    def DrawNetwork(self):
        # erase buffer
        dc = wx.BufferedDC(None,self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()

        # compute grid size for network
        size = self.GetClientSize()
        netsize = (self.network.max_x+1,self.network.max_y+1)
        grid = min(size[0]/netsize[0],size[1]/netsize[1])
        xoffset = (size[0] - (netsize[0]-1)*grid)/2
        yoffset = (size[1] - (netsize[1]-1)*grid)/2
        self.transform = (grid, (xoffset,yoffset))

        self.network.draw(dc,self.transform)

    def SetNetwork(self,network):
        self.network = network
        self.network.reset()
        self.redraw = True

class NetFrame(wx.Frame):
    def __init__(self,parent=None,id=-1,size=(1000,500),
                 pos=wx.DefaultPosition,title='NetSim'):
        wx.Frame.__init__(self,parent,id,title,pos,size)
        self.SetBackgroundColour('white')
        statusbar = self.CreateStatusBar()
        self.network = None

        self.netpanel = NetPanel(self,statusbar)  # panel for displaying the network

        # sizer for parameters
#        parameters = wx.Panel(self,-1)  # simulation parameters
#        parameters.SetBackgroundColour('light gray')
#        psizer = wx.FlexGridSizer(cols=2,hgap=5,vgap=5)
#        parameters.SetSizer(psizer)

        # number of nodes
#        psizer.Add(wx.StaticText(parameters,-1,'Num nodes:'),
#                   0,wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
#        self.nNodes = wx.SpinCtrl(parameters,-1,min=1,max=800)
#        self.Bind(wx.EVT_SPINCTRL,self.netpanel.OnNNodes,self.nNodes)
#        psizer.Add(self.nNodes,0)


        # holds netpanel and simulation controls
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(self.netpanel,1,flag=wx.EXPAND)  # expand V and H

#       controls = wx.Panel(self,-1)  # control panel
#        controls.SetBackgroundColour('white')

        # sizer for controls
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
#        controls.SetSizer(hsizer)
        vsizer.Add(hsizer,0,flag=wx.EXPAND)

        # reset button -- calls netpanel's OnReset
        button = wx.Button(self,-1,'Reset')
        self.Bind(wx.EVT_BUTTON, self.netpanel.OnReset, button)
        hsizer.Add(button,1)

        # step buttons -- calls netpanel's OnStep
        button = wx.Button(self,-1,'Step 1')
        self.Bind(wx.EVT_BUTTON, self.netpanel.OnStep, button)
        hsizer.Add(button,1)
        button = wx.Button(self,-1,'Step 10')
        self.Bind(wx.EVT_BUTTON, self.netpanel.OnStep, button)
        hsizer.Add(button,1)
        button = wx.Button(self,-1,'Step 100')
        self.Bind(wx.EVT_BUTTON, self.netpanel.OnStep, button)
        hsizer.Add(button,1)
        button = wx.Button(self,-1,'Step all')
        self.Bind(wx.EVT_BUTTON, self.netpanel.OnStep, button)
        hsizer.Add(button,1)
        button = wx.Button(self,-1,'Play')
        self.Bind(wx.EVT_BUTTON, self.netpanel.OnPlay, button)
        hsizer.Add(button,1)
        button = wx.Button(self,-1,'Pause')
        self.Bind(wx.EVT_BUTTON, self.netpanel.OnPause, button)
        hsizer.Add(button,1)

        # exit button
        button = wx.Button(self,-1,'Exit')
        self.Bind(wx.EVT_BUTTON, self.netpanel.OnExit, button)
        hsizer.Add(button,1)

#        self.SetSizer(vsizer)   # layout window
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
#        mainSizer.Add(parameters,0,flag=wx.EXPAND)
        mainSizer.Add(vsizer,1,flag=wx.EXPAND)

        self.SetSizer(mainSizer) # layout window

    def SetNetwork(self,network):
        self.netpanel.SetNetwork(network)

class NetSim(wx.App):
    def OnInit(self):
        self.frame = NetFrame()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

    def SetNetwork(self,network):
        self.frame.SetNetwork(network)

################################################################################
#
# Router base class
#
################################################################################

# use our own node class derived from the node class of network10.py
# so we can override routing behavior
class Router(Node):
    HELLO_INTERVAL = 10   # time between HELLO packets
    ADVERT_INTERVAL = 50  # time between route advertisements
        
    def __init__(self,location,address=None):
        Node.__init__(self, location, address=address)
        # additional instance variables
        self.neighbors = {}     # Link -> (timestamp, address, linkcost)
        self.routes = {}        # address -> Link
        self.routes[self.address] = 'Self'
        self.spcost = {}        # address -> shortest path cost to node
        self.spcost[self.address] = 0
        self.hello_offset = random.randint(0, self.HELLO_INTERVAL-1)
        self.ad_offset = random.randint(0, self.ADVERT_INTERVAL-1)
        self.hello_offset = 0
        self.ad_offset = 0

    def reset(self):
        Node.reset(self)
        self.spcost[self.address] = 0

    # return the link corresponding to a given neighbor, nbhr
    def getlink(self, nbhr):
        if self.address == nbhr: return None
        for l in self.links: 
            if l.end2.address == nbhr or l.end1.address == nbhr:
                return l
	return None

    def peer(self, link):
        if link.end1.address == self.address: return link.end2.address
        if link.end2.address == self.address: return link.end1.address

    # use routing table to forward packet along appropriate outgoing link
    def forward(self,p):
        link = self.routes.get(p.destination, None)
        if link is None:
            print 'No route for ',p,' at node ',self
        else:
            print 'sending packet'
            link.send(self, p)   

    def process(self,p,link,time):
        if p.type == 'HELLO':
            # remember addresses of our neighbors and time of latest update
            self.neighbors[link] = (time, p.source, link.cost)
        elif p.type == 'ADVERT':
            self.process_advertisement(p,link,time)
        else:
            Node.process(self, p, link, time)

    def process_advertisement(self,p,link,time):
        # will be filled in by the specific routing protocol
        return

    def sendHello(self, time): 
        # STEP 1(a): send HELLO packets along all my links to neighbors
        # These periodic HELLOs tell our neighbors I'm still alive
        # The neighbors will get my address from the source address field
        for link in self.links:
            p = self.network.make_packet(self.address, self.peer(link), 
                                         'HELLO', time,color='green')
            link.send(self,p)
        return

    def clearStaleHello(self, time):
        # STEP 1(b) : Look through neighbors table and eliminate
        # out-of-date entries.
        old = time - 2*self.HELLO_INTERVAL
        for link in self.neighbors.keys():
            if self.neighbors[link][0] <= old:
                del self.neighbors[link]
                self.link_failed(link)
        return
    
    def link_failed(self,link):
        pass
    
    def clear_routes(self,link):
        clear_list = []
        for dest in self.routes:
            if self.routes[dest] == link:
                clear_list.append(dest)
        for dest in clear_list:
            print self.address, ' clearing route to ', dest
            del self.routes[dest]
            del self.spcost[dest]

    def transmit(self, time):
        if (time % self.HELLO_INTERVAL) == self.hello_offset:
            self.sendHello(time)
            self.clearStaleHello(time)
        if (time % self.ADVERT_INTERVAL) == self.ad_offset:
            self.send_advertisement(time)
        return

    def OnClick(self,which):
        if which == 'left':
            #print whatever debugging information you want to print
            print self
            print '  neighbors:',self.neighbors.values()
            print '  routes:'
            for (key,value) in self.routes.items():
                print '    ',key,': ',value, 'pathcost %.2f' % self.spcost[key]


# Network with link costs.  By default, the cost of a link is the 
# Euclidean distance between the nodes at the ends of the link
class RouterNetwork(Network):
    def __init__(self,SIMTIME,NODES,LINKS,LOSSPROB):
        Network.__init__(self,SIMTIME)

        self.lossprob = LOSSPROB
        for n,r,c in NODES:
            self.add_node(r,c,address=n)
        for a1,a2 in LINKS:
            n1 = self.addresses[a1]
            n2 = self.addresses[a2]
            self.add_link(n1.location[0],n1.location[1],
                          n2.location[0],n2.location[1])
    
    # nodes should be an instance of LSNode (defined above)
    def make_node(self,loc,address=None):
        return Router(loc,address=address)

    def make_link(self,n1,n2):
        return LossyCostLink(n1,n2,self.lossprob)

#    def add_cost_link(self,x1,y1,x2,y2):
#        n1 = self.find_node(x1,y1)
#        n2 = self.find_node(x2,y2)
#        if n1 is not None and n2 is not None:
#            link = self.make_cost_link(n1,n2)
#            link.network = self
#            self.links.append(link)

    # reset network to its initial state
    def reset(self):
        # parent class handles the details
        Network.reset(self)
        # insert a single packet into the network with randomly
        # chosen source and destination.  Since we don't have code
        # to deliver the packet this just keeps the simulation alive...
        src = random.choice(self.nlist)
        dest = random.choice(self.nlist)
        src.add_packet(self.make_packet(src.location,dest.location,'DATA',1))


################################################################################
#
# Random graph generator
#
################################################################################

class RandomGraph:
    def __init__(self,numnodes=8):
        self.numnodes = numnodes
        if self.numnodes > 26:
            print "Maximum number of nodes = 26"
            self.numnodes = 26
        elif self.numnodes < 5:
            print "Minimum number of nodes = 5"
            self.numnodes = 5
        
        self.names = ['A', 'B', 'C', 'D', 'E',
                      'F', 'G', 'H', 'I', 'J',
                      'K', 'L', 'M', 'N', 'O',
                      'P', 'Q', 'R', 'S', 'T',
                      'U', 'V', 'W', 'X', 'Y', 'Z']
        self.maxRows = math.ceil(math.sqrt(self.numnodes))
        self.maxCols = math.ceil(math.sqrt(self.numnodes))

    def getCoord(self, i):
        x= i % self.maxCols
        y = math.floor(i/self.maxCols)
        return (x,y)
    
    def getIndex(self, x, y):
        if x<0 or y < 0 or x>=self.maxCols or y>=self.maxRows:
            return -1
        ind = y*self.maxCols + x    
        if ind < self.numnodes:
            return ind
        else:
            return -1
        
    def getAllNgbrs(self, i):
        (x,y) = self.getCoord(i)
        ngbrs = []
        ngbrsX = [x-1, x, x+1]
        ngbrsY = [y-1, y, y+1]
        for nx in ngbrsX:
            for ny in ngbrsY:
                if not (nx==x and ny == y):
                    ind = self.getIndex(nx, ny)
                    if ind>=0:
                        ngbrs.append(ind)
        return ngbrs
    
    def checkLinkExists(self, links, a, b):
        for (c,d) in links:
            if a==c and b==d:
                return True
            if a==d and b==c:
                return True
        return False
    
    def genGraph(self):
        NODES = []
        LINKS = []
        
        for i in range(self.numnodes):
            (x,y) = self.getCoord(i)
            name = self.names[i]
            NODES.append((name,x,y))
        
        for i in range(self.numnodes):
            ngbrs = self.getAllNgbrs(i)
            outdeg = int(random.random()*len(ngbrs)) + 1
            sampleNgbrs = random.sample(ngbrs, outdeg)
            for n1 in sampleNgbrs:
                n = int(n1)
                if not self.checkLinkExists(LINKS, self.names[i], self.names[n]):
                    LINKS.append((self.names[i], self.names[n]))

        return (NODES, LINKS)
    
########################################################################
if __name__ == '__main__':
    numnodes = 8 #can get this from commandline option
    SIMTIME = 10000
    rg = RandomGraph(numnodes)
    (NODES, LINKS) = rg.genGraph()
    print 'NODES: ', NODES
    print 'LINKS:', LINKS
    
    # make a network
    net = LSRouterNetwork(SIMTIME, NODES, LINKS)

    # setup graphical simulation interface
    sim = NetSim()
    sim.SetNetwork(net)
    sim.MainLoop()
########################################################################
