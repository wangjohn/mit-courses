import re
import math
import lib601.sig as sig
#import sig
reload(sig)
from lib601.plotWindow import PlotWindow


import Tkinter
tcl =Tkinter.Tcl()
def reafter():
        tcl.after(500,reafter)
tcl.after(500,reafter)

sim_output = ''
sim_windows = set()

def add_window(w):
    global sim_windows
    sim_windows.add(w)

def close_all_windows():
    global sim_windows
    for win in sim_windows:
        try:
            win.destroy()
        except:
            pass
    sim_windows = set()

def add_to_output(s):
    global sim_output
    sim_output += "%s\n" % s

def set_output(s=''):
    global sim_output
    sim_output = s

def warn(message):
    add_to_output(message)

class SingularMatrix(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class MultipleSources(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Resistor:
    def __init__(self,resistance,n1,n2):
        self.resistance = resistance
        self.n1 = n1
        self.n2 = n2
    def __str__(self):
        return 'Resistor ('+str(self.resistance)+' ohms): ' + chr(97 +self.n1)+'--'+chr(97 + self.n2)
    def addConductance(self,gMatrix):
        gMatrix[self.n1][self.n1] += 1./self.resistance
        gMatrix[self.n1][self.n2] -= 1./self.resistance
        gMatrix[self.n2][self.n1] -= 1./self.resistance
        gMatrix[self.n2][self.n2] += 1./self.resistance
    def connected(self):
        return self.n1 != None and self.n2 != None

class Pot:
    def __init__(self,resistance,n1,n2,n3):
        self.resistance = resistance
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        self.alpha = 0.5
        self.alphaSample = sig.ConstantSignal(0.5).sample
    def __str__(self):
        return 'Pot ('+str(self.resistance)+' ohms): '+chr(97+self.n1)+'--'+chr(97+self.n2)+'--'+chr(97+self.n3)
    def addConductance(self,gMatrix):
        a = min(max(self.alpha,0.001),0.999)
        gMatrix[self.n1][self.n1] += 1./((1.0-a)*self.resistance)
        gMatrix[self.n1][self.n2] -= 1./((1.0-a)*self.resistance)
        gMatrix[self.n2][self.n1] -= 1./((1.0-a)*self.resistance)
        gMatrix[self.n2][self.n2] += 1./((1.0-a)*self.resistance)
        gMatrix[self.n2][self.n2] += 1./(a*self.resistance)
        gMatrix[self.n2][self.n3] -= 1./(a*self.resistance)
        gMatrix[self.n3][self.n2] -= 1./(a*self.resistance)
        gMatrix[self.n3][self.n3] += 1./(a*self.resistance)
    def connected(self):
        return sum([1 for n in [self.n1, self.n2, self.n3] if n!=None])>1

class PhotoResistor:
    def __init__(self,resistance,n1,n2):
        self.n1 = n1
        self.n2 = n2
        self.resistance = resistance
    def __str__(self):
        return 'PhotoResistor: '+chr(97+self.n1)+'--'+chr(97+self.n2)
    def addConductance(self,gMatrix):
        gMatrix[self.n1][self.n1] += 1./self.resistance
        gMatrix[self.n1][self.n2] -= 1./self.resistance
        gMatrix[self.n2][self.n1] -= 1./self.resistance
        gMatrix[self.n2][self.n2] += 1./self.resistance
    def connected(self):
        return self.n1 != None and self.n2 != None

class PhotoDiode:
    def __init__(self,n1,n2):
        self.n1 = n1
        self.n2 = n2
        self.resistance = 1e10
        self.current = 1e-7
    def __str__(self):
        return 'PhotoDiode: '+chr(97+self.n1)+'--'+chr(97+self.n2)
    def addConductance(self,gMatrix):
        gMatrix[self.n1][self.n1] += 1./self.resistance
        gMatrix[self.n1][self.n2] -= 1./self.resistance
        gMatrix[self.n2][self.n1] -= 1./self.resistance
        gMatrix[self.n2][self.n2] += 1./self.resistance
    def setCurrent(self,currents):
        currents[self.n1] = self.current
        currents[self.n2] = -self.current
    def connected(self):
        return self.n1 != None and self.n2 != None

class Head:
    def __init__(self,n1,n2,pot,left,right):
        self.n1 = n1
        self.n2 = n2
        self.omega = 0
        self.theta = 0.0
        self.Rm = 5.26
        self.Kt = 0.323
        self.Kb = 0.495
        self.J  = 0.00132
        self.B  = 0.0006
        self.B  = 0.0045 # to fit with measurements on 2012_07_02
        self.pot = pot
        self.left = left
        self.right = right
        self.phi = 0.0
        self.distance = 1
        self.lampAngleSample = sig.ConstantSignal(0.).sample
        self.lampDistanceSample = sig.ConstantSignal(1.).sample
    def __str__(self):
        return 'Motor: '+chr(97+self.n1)+'--'+chr(97+self.n2)
    def addConductance(self,gMatrix):
#        gMatrix[self.n1][self.n1] += 0.000001
#        gMatrix[self.n1][self.n2] -= 0.000001
#        gMatrix[self.n2][self.n1] -= 0.000001
#        gMatrix[self.n2][self.n2] += 0.000001
        gMatrix[self.n1][self.n1] += .2
        gMatrix[self.n1][self.n2] -= .2
        gMatrix[self.n2][self.n1] -= .2
        gMatrix[self.n2][self.n2] += .2
    def connected(self):
        return self.n1 != None and self.n2 != None
    def updatePhotoResistors(self):
        if self.left:
            tt = self.phi-self.theta-math.pi/4.
            tt = max(min(tt,3),-3)
            r2 = 14000
            xx = 3.*self.distance
            r1 = min(-200+1400*xx-50*math.exp(2),r2)
            ww = 0.22*math.pi
            r3 = r1+50*(math.exp((tt/ww)*(tt/ww)+2))
            self.left.resistance = min(r2,r3)
        if self.right:
            tt = self.phi-self.theta+math.pi/4.
            tt = max(min(tt,3),-3)
            r2 = 14000
            xx = 3.*self.distance
            r1 = min(-200+1400*xx-50*math.exp(2),r2)
            ww = 0.22*math.pi
            r3 = r1+50*(math.exp((tt/ww)*(tt/ww)+2))
            self.right.resistance = min(r2,r3)
    def updatePhotoDiodes(self):
        if self.left:
            tt = self.phi-self.theta-math.pi/4.
            tt = max(min(tt,3),-3)
            xx = 3.*self.distance
            self.left.current = max(0.,0.5e-7*math.cos(tt)/xx/xx)
        if self.right:
            tt = self.phi-self.theta+math.pi/4.
            tt = max(min(tt,3),-3)
            xx = 3.*self.distance
            self.right.current = max(0.,0.5e-7*math.cos(tt)/xx/xx)
    def updatePot(self):
        if self.pot:
            self.pot.alpha = (self.theta/2./math.pi+0.5)%1.0
    def update(self,voltages,T):
        tau = (voltages[self.n1]-voltages[self.n2]-self.Kb*self.omega)*self.Kt/self.Rm
        omegaDot = (tau-self.B*self.omega)/self.J
        omega = self.omega+T*omegaDot
        theta = self.theta+T*omega
        self.omega = omega
        self.theta = theta

class VoltageSource:
    def __init__(self,voltage,n1):
        self.voltage = voltage
        self.n1 = n1
    def __str__(self):
        return 'Source ('+str(self.voltage)+' volts): '+chr(97+self.n1)
    def setVoltage(self,voltages,knowns):
        if knowns[self.n1]:
            warn('Voltage on node {0:d} set by multiple sources.'.format(self.n1))
            raise MultipleSources('Voltage on node {0:d} set by multiple sources.'.format(self.n1))
        voltages[self.n1] = self.voltage
        knowns[self.n1] = True
    def addConductance(self,gMatrix):
        gMatrix[self.n1][self.n1] += 1./0.000001
    def connected(self):
        return self.n1 != None

class OpAmp:
    def __init__(self,vO,vP,vM,pP,pM):
        self.vO = vO
        self.vP = vP
        self.vM = vM
        self.pP = pP
        self.pM = pM
        self.K = 10000
        self.alpha = 0.0001
    def __str__(self):
        return 'OpAmp: '+chr(97 + self.vO)+'--'+chr(97 + self.vP)+'--'+chr(97 + self.vM)+'--'+chr(97 + self.pP)+'--'+chr(97 + self.pM)
    def initial(self,voltages,knowns):
        if knowns[self.vO]:
            warn('Voltage on node {0:d} set by multiple sources.'.format(self.vO))
            raise MultipleSources('Voltage on node {0:d} set by multiple sources.'.format(self.vO))
        voltages[self.vO] = 0
        knowns[self.vO] = True
    def update(self,voltages,knowns):
        v = self.K*(voltages[self.vP]-voltages[self.vM])
        v = self.alpha*v+(1.-self.alpha)*voltages[self.vO]
        if v>voltages[self.pP]:
            v = voltages[self.pP]
        if v<voltages[self.pM]:
            v = voltages[self.pM]
        voltages[self.vO] = v
        knowns[self.vO] = True
    def addConductance(self,gMatrix):
        gMatrix[self.vO][self.vO] += 1./0.0001
        gMatrix[self.pP][self.pP] += 1./0.000001
        gMatrix[self.pM][self.pM] += 1./0.000001
    def connected(self):
        return self.vP != None and self.vM != None

class Probe:
    def __init__(self,n1,sign):
        self.n1 = n1
        self.sign = sign
    def __str__(self):
        return 'Probe ('+self.sign+'): '+chr(97 + self.n1)
    def addConductance(self,gMatrix):
        gMatrix[self.n1][self.n1] += 0.000001
    def connected(self):
        return self.n1 != None

def pin(x,y):
    # (mikemeko) hack to make CMax simulator to work with circuit simulator
    # For all (x,y) pairs, x may be any non-negative integer, but y will be
    #     either 0 or 1. No two different (x,y) pairs are considered connected.
    return  2 * x + y
    if x < 1 or x > 63:
        warn('Illegal pin %s,%s'%(x,y))
        return False
    if y == 1 and 2<x<62 and (x%6 != 2): return 201
    if y == 2 and 2<x<62 and (x%6 != 2): return 202
    if y == 19 and 2<x<62 and (x%6 != 2): return 203
    if y == 20 and 2<x<62 and (x%6 != 2): return 204
    if 4 < y < 10: return 300+x
    if 11 < y < 17: return 400+x
    warn('Illegal pin %s,%s'%(x,y))
    return False

def makeNodes(lines):
    global nodes
    nodes = 500*[None]
    N = 0
    connected = []
    counts = []
    def addNode(x0,y0):
        a = pin(x0,y0)
        if nodes[a]==None:
            nodes[a] = len(connected)
            connected.append([a])
            counts.append(1)
        else:
            counts[nodes[a]] += 1
    for line in lines:
        match = re.match(r'opamp: \((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (x0,y0,x1,y1) = [int(x) for x in match.groups()]
            if y0<y1:
                for i in range(4):
                    addNode(x0-i,y0)
                    addNode(x0-i,y1)
            else:
                for i in range(4):
                    addNode(x0+i,y0)
                    addNode(x0+i,y1)
        match = re.match(r'resistor\((\d),(\d),(\d)\): \((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (c1,c2,c3,x0,y0,x1,y1) = [int(x) for x in match.groups()]
            addNode(x0,y0)
            addNode(x1,y1)
        match = re.match(r'pot: \((\d+),(\d+)\)--\((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (x0,y0,x1,y1,x2,y2) = [int(x) for x in match.groups()]
            addNode(x0,y0)
            addNode(x1,y1)
            addNode(x2,y2)
        match = re.match(r'robot: \((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (x0,y0,x1,y1) = [int(x) for x in match.groups()]
            if x0 < x1:
                addNode(x0+1,y0)
                addNode(x0+3,y0)
            else:
                addNode(x0-1,y0)
                addNode(x0-3,y0)
        match = re.match(r'motor: \((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (x0,y0,x1,y1) = [int(x) for x in match.groups()]
            if x0 < x1:
                addNode(x0+4,y0)
                addNode(x0+5,y0)
            else:
                addNode(x0-4,y0)
                addNode(x0-5,y0)
        match = re.match(r'head: \((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (x0,y0,x1,y1) = [int(x) for x in match.groups()]
            if x0 < x1:
                for i in range(8):
                    addNode(x0+i,y0)
            else:
                for i in range(8):
                    addNode(x0-i,y0)
        match = re.match(r'\+probe: \((\d+),(\d+)\)',line)
        if match:
            (x0,y0) = [int(x) for x in match.groups()]
            addNode(x0,y0)
        match = re.match(r'\-probe: \((\d+),(\d+)\)',line)
        if match:
            (x0,y0) = [int(x) for x in match.groups()]
            addNode(x0,y0)
        match = re.match(r'\+10: \((\d+),(\d+)\)',line)
        if match:
            (x0,y0) = [int(x) for x in match.groups()]
            addNode(x0,y0)
        match = re.match(r'gnd: \((\d+),(\d+)\)',line)
        if match:
            (x0,y0) = [int(x) for x in match.groups()]
            addNode(x0,y0)
    for line in lines:
        match = re.match(r'wire: \((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (x0,y0,x1,y1) = [int(x) for x in match.groups()]
            a = pin(x0,y0)
            b = pin(x1,y1)
            if nodes[a]==None:
                if nodes[b]==None:
                    nodes[a] = len(connected)
                    nodes[b] = len(connected)
                    connected.append([a,b])
                    counts.append(0)
                else:
                    connected[nodes[b]] += [a]
                    nodes[a] = nodes[b]
            else:
                if nodes[b]==None:
                    connected[nodes[a]] += [b]
                    nodes[b] = nodes[a]
                else:
                    if nodes[a]!=nodes[b]:
                        t = nodes[b]
                        connected[nodes[a]] += connected[nodes[b]]
                        counts[nodes[a]] += counts[nodes[b]]
                        for c in connected[t]:
                            nodes[c] = nodes[a]
                        connected[t] = []
                        counts[t] = 0
    renum = {}
    i = 0
    for n in range(len(connected)):
        if counts[n]<1:
            renum[n] = None
        else:
            renum[n] = i
            i += 1
    renum[None] = None
    return ([renum[n] for n in nodes],i)

def node(x,y):
    global nodes
    return nodes[pin(x,y)]

def parseComponents(lines):
    resistors = []
    pots = []
    motorPots = []
    heads = []
    motors = []
    vsources = []
    isources = []
    opAmps = []
    probes = []
    for line in lines:
        match = re.match(r'resistor\((\d),(\d),(\d)\): \((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (c1,c2,c3,x0,y0,x1,y1) = [int(x) for x in match.groups()]
            resistors.append(Resistor((c1*10+c2)*(10**c3),node(x0,y0),node(x1,y1)))
        match = re.match(r'pot: \((\d+),(\d+)\)--\((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (x0,y0,x1,y1,x2,y2) = [int(x) for x in match.groups()]
            pots.append(Pot(5000.,node(x0,y0),node(x1,y1),node(x2,y2)))
        match = re.match(r'head: \((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (x0,y0,x1,y1) = [int(x) for x in match.groups()]
            if x0 < x1:
                pot = Pot(10000.,node(x0,y0),node(x0+1,y0),node(x0+2,y0))
#                left = PhotoResistor(10000.,node(x0+3,y0),node(x0+4,y0))
#                right = PhotoResistor(10000.,node(x0+4,y0),node(x0+5,y0))
                left = PhotoDiode(node(x0+3,y0),node(x0+4,y0))
                right = PhotoDiode(node(x0+5,y0),node(x0+4,y0))
                head = Head(node(x0+6,y0),node(x0+7,y0),pot,left,right)
                motorPots.append(pot)
#                resistors.append(left)
#                resistors.append(right)
                isources.append(left)
                isources.append(right)
                heads.append(head)
                def fromHead(n):
                    pot.alpha = (head.theta/2./math.pi+0.5)%1.0
                pot.AlphaSample = fromHead
            else:
                pot = Pot(10000.,node(x0,y0),node(x0-1,y0),node(x0-2,y0))
#                left = PhotoResistor(10000.,node(x0-3,y0),node(x0-4,y0))
#                right = PhotoResistor(10000.,node(x0-4,y0),node(x0-5,y0))
                left = PhotoDiode(node(x0-3,y0),node(x0-4,y0))
                right = PhotoDiode(node(x0-5,y0),node(x0-4,y0))
                head = Head(node(x0-6,y0),node(x0-7,y0),pot,left,right)
                motorPots.append(pot)
#                resistors.append(left)
#                resistors.append(right)
                isources.append(left)
                isources.append(right)
                heads.append(head)
                def fromHead(n):
                    pot.alpha = (head.theta/2./math.pi+0.5)%1.0
                pot.AlphaSample = fromHead
        match = re.match(r'motor: \((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (x0,y0,x1,y1) = [int(x) for x in match.groups()]
            if x0 < x1:
                motors.append(Head(node(x0+4,y0),node(x0+5,y0),None,None,None))
            else:
                motors.append(Head(node(x0-4,y0),node(x0-5,y0),None,None,None))
        match = re.match(r'robot: \((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (x0,y0,x1,y1) = [int(x) for x in match.groups()]
            if x0 < x1:
                vsources.append(VoltageSource(10,node(x0+1,y0)))
                vsources.append(VoltageSource(0,node(x0+3,y0)))
            else:
                vsources.append(VoltageSource(10,node(x0-1,y0)))
                vsources.append(VoltageSource(0,node(x0-3,y0)))
        match = re.match(r'\+10: \((\d+),(\d+)\)',line)
        if match:
            (x0,y0) = [int(x) for x in match.groups()]
            vsources.append(VoltageSource(10,node(x0,y0)))
        match = re.match(r'gnd: \((\d+),(\d+)\)',line)
        if match:
            (x0,y0) = [int(x) for x in match.groups()]
            vsources.append(VoltageSource(0,node(x0,y0)))
        match = re.match(r'opamp: \((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (x0,y0,x1,y1) = [int(x) for x in match.groups()]
            if y0<y1:
                opAmps.append(OpAmp(node(x0,y0),node(x0-1,y1),node(x0,y1),node(x0-1,y0),node(x0-3,y0)))
                opAmps.append(OpAmp(node(x0-2,y0),node(x0-2,y1),node(x0-3,y1),node(x0-1,y0),node(x0-3,y0)))
            else:
                opAmps.append(OpAmp(node(x0,y0),node(x0+1,y1),node(x0,y1),node(x0+1,y0),node(x0+3,y0)))
                opAmps.append(OpAmp(node(x0+2,y0),node(x0+2,y1),node(x0+3,y1),node(x0+1,y0),node(x0+3,y0)))
        match = re.match(r'\+probe: \((\d+),(\d+)\)',line)
        if match:
            (x0,y0) = [int(x) for x in match.groups()]
            probes.append(Probe(node(x0,y0),'+'))
        match = re.match(r'\-probe: \((\d+),(\d+)\)',line)
        if match:
            (x0,y0) = [int(x) for x in match.groups()]
            probes.append(Probe(node(x0,y0),'-'))
    return (resistors,pots,motorPots,heads,motors,vsources,isources,opAmps,probes)

def printComponents(lines):
    for line in lines:
        match = re.match(r'wire: \((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (x0,y0,x1,y1) = [int(x) for x in match.groups()]
            print 'Wire:',chr(97+node(x0,y0)),chr(97+node(x1,y1))
        match = re.match(r'opamp: \((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (x0,y0,x1,y1) = [int(x) for x in match.groups()]
            if y0<y1:
                print 'OpAmp:',chr(97+node(x0,y0)),chr(97+node(x0-1,y1)),chr(97+node(x0,y1)),chr(97+node(x0-1,y0)),chr(97+node(x0-3,y0))
                print 'OpAmp:',chr(97+node(x0-2,y0)),chr(97+node(x0-2,y1)),chr(97+node(x0-3,y1)),chr(97+node(x0-1,y0)),chr(97+node(x0-3,y0))
            else:
                print 'OpAmp:',chr(97+node(x0,y0)),chr(97+node(x0+1,y1)),chr(97+node(x0,y1)),chr(97+node(x0+1,y0)),chr(97+node(x0+3,y0))
                print 'OpAmp:',chr(97+node(x0+2,y0)),chr(97+node(x0+2,y1)),chr(97+node(x0+3,y1)),chr(97+node(x0+1,y0)),chr(97+node(x0+3,y0))
        match = re.match(r'resistor\((\d),(\d),(\d)\): \((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (c1,c2,c3,x0,y0,x1,y1) = [int(x) for x in match.groups()]
            print 'Resistor ({0:d}):'.format((c1*10+c2)*(10**c3)),chr(97+node(x0,y0)),chr(97+node(x1,y1))
        match = re.match(r'pot: \((\d+),(\d+)\)--\((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (x0,y0,x1,y1,x2,y2) = [int(x) for x in match.groups()]
            print 'Pot:',chr(97+node(x0,y0)),chr(97+node(x1,y1)),chr(97+node(x2,y2))
        match = re.match(r'robot: \((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (x0,y0,x1,y1) = [int(x) for x in match.groups()]
            if x0 < x1:
                print 'Robot:',[chr(97+node(x0+i,y0)) for i in range(8)]
                print 'Power:',chr(97+node(x0+1,y0))
                print 'Ground:',chr(97+node(x0+3,y0))
            else:
                print 'Robot:',[chr(97+node(x0-i,y0)) for i in range(8)]
                print 'Power:',chr(97+node(x0-1,y0))
                print 'Ground:',chr(97+node(x0-3,y0))
        match = re.match(r'motor: \((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (x0,y0,x1,y1) = [int(x) for x in match.groups()]
            if x0 < x1:
                print 'Motor:',[chr(97+node(x0+i,y0)) for i in range(6)]
            else:
                print 'Motor:',[chr(97+node(x0-i,y0)) for i in range(6)]
        match = re.match(r'head: \((\d+),(\d+)\)--\((\d+),(\d+)\)',line)
        if match:
            (x0,y0,x1,y1) = [int(x) for x in match.groups()]
            if x0 < x1:
                print 'Head:',[chr(97+node(x0+i,y0)) for i in range(8)]
            else:
                print 'Head:',[chr(97+node(x0-i,y0)) for i in range(8)]
        match = re.match(r'\+probe: \((\d+),(\d+)\)',line)
        if match:
            (x0,y0) = [int(x) for x in match.groups()]
            print '+Probe:',chr(97+node(x0,y0))
        match = re.match(r'\-probe: \((\d+),(\d+)\)',line)
        if match:
            (x0,y0) = [int(x) for x in match.groups()]
            print '-Probe:',chr(97+node(x0,y0))
        match = re.match(r'\+10: \((\d+),(\d+)\)',line)
        if match:
            (x0,y0) = [int(x) for x in match.groups()]
            print 'Power:',chr(97+node(x0,y0))
        match = re.match(r'gnd: \((\d+),(\d+)\)',line)
        if match:
            (x0,y0) = [int(x) for x in match.groups()]
            print 'Ground:',chr(97+node(x0,y0))

class NonexistentPart(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def solve(lines,potAlphaSignals,lampAngleSignals,lampDistanceSignals,potLabels,lampLabels,headMotorLabels,motorLabels,nSamples=100,deltaT=0.02):
    global nodes,N
    def makeGMatrix():
        gMatrix = [[0.0 for x in range(N)] for y in range(N)]
        for c in resistors+pots+motorPots+heads+motors+probes+opAmps+vsources+isources:
                if c.connected():
                    c.addConductance(gMatrix)
        return gMatrix
    def makeVoltages():
        vArray = [0.0 for i in range(N)]
        vKnown = [False for i in range(N)]
        iArray = [0.0 for i in range(N)]
        for c in vsources:
            c.setVoltage(vArray,vKnown)
        for c in isources:
            c.setCurrent(iArray)
        for c in opAmps:
            c.initial(vArray,vKnown)
        return (vArray,vKnown,iArray)

    (nodes,N) = makeNodes(lines)
    (resistors,pots,motorPots,heads,motors,vsources,isources,opAmps,probes) = parseComponents(lines)

    assert len(pots) == len(potAlphaSignals) == len(potLabels)
    assert len(heads) == len(lampAngleSignals) == len(
        lampDistanceSignals) == len(lampLabels) == len(headMotorLabels)
    assert len(motors) == len(motorLabels)

    nodePins = []
    for i in range(N):
        msg = ''
        if nodes[201]==i: msg += ' top-'
        if nodes[202]==i: msg += ' top+'
        if nodes[203]==i: msg += ' bottom-'
        if nodes[204]==i: msg += ' bottom+'
        for c in range(1,64):
            if nodes[300+c]==i: msg += ' '+str(c)+'J'
            if nodes[400+c]==i: msg += ' '+str(c)+'A'
        nodePins.append(msg)

    for i in range(N):
        warn('node '+chr(97+i)+':'+nodePins[i])
    for c in resistors: warn(str(c))
    for c in pots: warn(str(c))
    for c in motorPots: warn(str(c))
    for c in heads: warn(str(c))
    for c in motors: warn(str(c))
    for c in vsources: warn(str(c))
    for c in isources: warn(str(c))
    for c in opAmps: warn(str(c))
    for c in probes: warn(str(c))

    for h in heads:
        h.phi = h.lampAngleSample(0)*2.*math.pi
        h.distance = h.lampDistanceSample(0)
#        h.updatePhotoResistors()
        h.updatePhotoDiodes()
        h.updatePot()
    for p in pots:
        p.alpha = p.alphaSample(0)
    gMatrix = makeGMatrix()
    (vArray,vKnown,iArray) = makeVoltages()

    j = 0
    for i in range(N):
        if gMatrix[i][i]==0.0:
            warn('Floating node at{0:s} must be connected - it is possible you have not connected the inputs of an opamp.'.format(nodePins[i]))
            j += 1
    if j>0:
        raise SingularMatrix('Floating nodes must be connected')

    for i, pot in enumerate(pots):
      pot.alphaSample = potAlphaSignals[i].sample

    #if potAlphaSignal:
    #    if len(pots)<1:
    #        warn('Simulation file specifies input signal for nonexistent pot')
    #        raise NonexistentPart('No pot in this circuit!')
    #    else:
    #        pots[0].alphaSample = potAlphaSignal.sample
    #        warning = 'potAlphaSignal:'
    #        for n in range(nSamples):
    #            warning +='{0:5.2f}'.format(potAlphaSignal.sample(n))
    #        warn(warning)

    for i, head in enumerate(heads):
      head.lampAngleSample = lampAngleSignals[i].sample
      head.lampDistanceSample = lampDistanceSignals[i].sample

    #if lampAngleSignal:
    #    if len(heads)<1:
    #        warn('Simulation file specifies lamp angle input signal for nonexistent head')
    #        raise NonexistentPart('No head in this circuit!')
    #    else:
    #        heads[0].lampAngleSample = lampAngleSignal.sample
    #        warning = 'lampAngleSignal:'
    #        for n in range(nSamples):
    #            warning += '{0:5.2f}'.format(lampAngleSignal.sample(n))
    #        warn(warning)
    #if lampDistanceSignal:
    #    if len(heads)<1:
    #        warn('Simulation file specifies lamp angle input signal for nonexistent head')
    #        raise NonexistentPart('No head in this circuit!')
    #    else:
    #        heads[0].lampDistanceSample = lampDistanceSignal.sample
    #        warning = 'lampDistanceSignal:'
    #        for n in range(nSamples):
    #            warning += '{0:5.2f}'.format(lampDistanceSignal.sample(n))
    #        warn(warning)

    for h in heads+motors:
        h.thetaOutput = []
        h.omegaOutput = []
    for p in probes:
        p.outputs = []
    for n in range(nSamples):
        for h in heads:
            h.phi = h.lampAngleSample(n)*2.*math.pi
            h.distance = h.lampDistanceSample(n)
#            h.updatePhotoResistors()
            h.updatePhotoDiodes()
            h.updatePot()
        for p in pots:
            p.alpha = p.alphaSample(n)
        gMatrix = makeGMatrix()
        (vArray,vKnown,iArray) = makeVoltages()

#        print '---'
#        for i in range(N):
#            print i,vArray[i],vKnown[i]
#        print '---'
#        for i in range(N):
#            for j in range(N):
#                if gMatrix[i][j]!=0:
#                    print 'gMatrix[{0:d}][{1:d}]={2:f}'.format(i,j,gMatrix[i][j])
#        exit()

        for o in opAmps:
            gain = 0
            if not vKnown[o.vP]:
                gain += gMatrix[o.vP][o.vO]/gMatrix[o.vP][o.vP]
            if not vKnown[o.vM]:
                gain -= gMatrix[o.vM][o.vO]/gMatrix[o.vM][o.vM]
            if gain!=0:
                o.alpha = 1./gain/o.K
            else:
                o.alpha = 1./o.K
        vArray0 = vArray[:]
        for j in range(1000):
            for nn in range(N):
                if not vKnown[nn]:
                    vArray[nn] = 0
                    vArray[nn] = (-iArray[nn]-sum([gMatrix[nn][k]*vArray[k] for k in range(N)]))/gMatrix[nn][nn]
            for c in opAmps:
                c.update(vArray,vKnown)
            if j%10==0:
                error = math.sqrt(sum([(vArray[i]-vArray0[i])**2 for i in range(len(vArray))])/len(vArray))
                if error<max([abs(v) for v in vArray])/1000.:
                    break
                vArray0 = vArray[:]
#        print j,error
        for h in heads+motors:
            h.update(vArray,deltaT)
            h.thetaOutput.append(h.theta)
            h.omegaOutput.append(h.omega)
        for p in probes:
            p.outputs.append(vArray[p.n1])
    pos = []
    neg = []
    for p in probes:
        if p.sign=='+':
            pos.append(p)
        else:
            neg.append(p)

    def myPlot(s,title,y0,y1):
        if nSamples>1:
            samps = [s.sample(x) for x in xrange(nSamples)]
            yy0 = min(samps)
            yy1 = max(samps)
            if float(yy1-y0)/float(y1-y0+.001)>0.9:
                y1 = yy1
            if float(y1-yy0)/float(y1-y0+.001)>0.9:
                y0 = yy0
            p = PlotWindow(title)
            p.stem(range(nSamples),samps)
            p.axis([0,nSamples,y0,y1])
            add_window(p)
        warning = str(title)+':'
        for nn in range(nSamples):
            warning += '{0:6.2f}'.format(s.sample(nn))
        warn(warning)

    w = 0
    for i in range(min(len(pos),len(neg))):
        myPlot(sig.ListSignal([a-b for (a,b) in zip(pos[i].outputs,neg[i].outputs)]),'probe',0,.01)
        w += 1
    for i, label in enumerate(headMotorLabels):
      myPlot(sig.ListSignal(heads[i].thetaOutput),'Motor %s Angle' % label,0,0)
      myPlot(sig.ListSignal(heads[i].omegaOutput),'Motor %s Velocity' % label,0,0)
      w += 1
    for i, label in enumerate(motorLabels):
      myPlot(sig.ListSignal(motors[i].thetaOutput),'Motor %s Angle' % label,0,0)
      myPlot(sig.ListSignal(motors[i].omegaOutput),'Motor %s Velocity' % label,0,0)
      w += 1
    #for h in heads+motors:
    #    myPlot(sig.ListSignal(h.thetaOutput),'Motor Angle',0,0)
    #    myPlot(sig.ListSignal(h.omegaOutput),'Motor Velocity',0,0)
    #    w += 1
    for i, label in enumerate(lampLabels):
      if label:
        myPlot(lampDistanceSignals[i], 'Lamp %s Distance Signal' % label, 0, 1)
        myPlot(lampAngleSignals[i], 'Lamp %s Angle Signal' % label, -1./8, 1./8)
        w += 2
    #if lampDistanceSignal:
    #    myPlot(lampDistanceSignal,'Lamp Distance Signal',0,1)
    #    w += 1
    #if lampAngleSignal:
    #    myPlot(lampAngleSignal,'Lamp Angle Signal',-1./8.,1./8.)
    #    w += 1
    for i, label in enumerate(potLabels):
      myPlot(potAlphaSignals[i], 'Pot %s Alpha Signal' % label, 0, 1)
      w += 1
    #if potAlphaSignal:
    #    myPlot(potAlphaSignal,'Pot Alpha Signal',0,1)
    #    w += 1
    #elif len(pots)>0:
    #    myPlot(sig.ListSignal([pots[0].alphaSample(n) for n in range(nSamples)]),'Pot Alpha Signal',0,1)
    #    w += 1
    if w==0:
        warn('No output signals are specified. Do you want to add a Probe?')
