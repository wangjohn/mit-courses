from le import solveEquations

class OnePort:
    def __init__(self, e1, e2, i):
        self.e1 = e1
        self.e2 = e2
        self.i = i

class VSrc(OnePort):
    def __init__(self, v0, e1, e2, i):
        OnePort.__init__(self,e1,e2,i)
        self.equation = [(1, e1), (-1, e2), (-v0, None)]

class ISrc(OnePort):
    def __init__(self, i0, e1, e2, i):
        OnePort.__init__(self,e1,e2,i)
        self.equation = [(1, i), (-i0, None)]

class Resistor(OnePort):
    def __init__(self, r, e1, e2, i):
        OnePort.__init__(self,e1,e2,i)
        self.equation = [(1, e1), (-1, e2), (-r, i)]

#OP-AMPS

class VoltageSensor(OnePort):
    def __init__(self, e1, e2, i):
        OnePort.__init__(self,e1,e2,i)
        self.equation = [(1, i)]

class VCVS(OnePort):
    def __init__(self, sensor, e1, e2, i, K=1000000):
        OnePort.__init__(self,e1,e2,i)
        self.equation = [(1, e1), (-1, e2), (-K, sensor.e1), (K, sensor.e2)]

def OpAmp(ea1, ea2, Ia, eb1, eb2, Ib, K=1000000):
    sensor = VoltageSensor(ea1, ea2, Ia)
    return [sensor, VCVS(sensor, eb1, eb2, Ib, K)]


#THEVENINS

class Thevenin(OnePort):
    def __init__(self, v, r, e1, e2, i):
        OnePort.__init__(self,e1,e2,i)
        self.equation = [(1, e1), (-1, e2), (-r, i), (-v, None)]

def theveninEquivalent(components, nPlus, nMinus, current):
    result = solveCircuit(components, nMinus)
    vth = result[nPlus]

    new_components = list(components)
    new_components.append(VSrc(0, nPlus, nMinus, current))

    short_circuited_result = solveCircuit(new_components, nMinus)
    ith = short_circuited_result[current]
    rth = float(vth) / ith
    return Thevenin(vth, rth, nPlus, nMinus, current)

#SOLVING CIRCUITS

def flatten_list(l):
    out = []
    for i in l:
        if type(i) == list:
            out.extend(flatten_list(i))
        else:
            out.append(i)
    return out

def solveCircuit(componentList, GND):
    # flatten_list is necessary for lists that contain two-ports.
    # It has no effect on lists that contain just one-ports.
    # Do not remove the following line.
    componentList = flatten_list(componentList)
    componentList = [comp for comp in componentList if comp != None]
    equations = []

    # one equation for each component
    for component in componentList:
            equations.append(component.equation)

    # one KCL equation for each node except ground
    equations.extend(create_kcls(componentList, GND))

    # one equation for ground
    equations.append([(1, GND)])

    return solveEquations(equations)

def create_kcls(componentList, GND):
    nodes = find_nodes(componentList)
    kcl_equations = []
    for node in nodes:
        if node is not GND:
            equation = []
            for comp in connected_components(componentList, node):
                if node == comp.e1:
                    equation.append((1, comp.i))
                else:
                    equation.append((-1, comp.i))
            kcl_equations.append(equation)

    return kcl_equations

def connected_components(componentList, node):
    connected = []
    for component in componentList:
        if component.e1 == node or component.e2 == node:
            connected.append(component)

    return connected

def find_nodes(componentList):
    nodes = set()
    for component in componentList:
        nodes.add(component.e1)
        nodes.add(component.e2)

    return nodes

def old_circuit():
    circuitComponents = []
    circuitComponents.append(ISrc(920.0 * 10**(-12), 'e1', 'gnd', 'i0'))
    circuitComponents.append(Resistor(52.0 * 10**(6), 'e1', 'transamp_out', 'i1'))
    circuitComponents.append(OpAmp('gnd', 'e1', 'i4', 'transamp_out', 'gnd', 'i5'))
    circuitComponents.append(Resistor(3.0 * 10**(3), 'transamp_out', 'e3', 'i2'))
    circuitComponents.append(Resistor(300.0 * 10**(3), 'e3', 'v_out', 'i3'))
    circuitComponents.append(OpAmp('gnd', 'e3', 'i6', 'v_out', 'gnd', 'i7'))
    
    res = solveCircuit(circuitComponents,'gnd')
    print (res['transamp_out'], res['v_out'])
    print res['i3']
    print res['e3']
    print res['i5']

if __name__ == '__main__':
    Vi = 8
    Vs = 19
    r1 = 3
    r2 = 3
    r3 = 5
    r4 = 9
    r5 = 10
    circuitComponents = []
    circuitComponents.append(Resistor(4, 'vplus', 'e1', 'i0'))
    circuitComponents.append(Resistor(5, 'e1', 'vminus', 'i1'))
    circuitComponents.append(VSrc(50, 'e1', 'e2', 'i2'))
    circuitComponents.append(Resistor(20, 'e2', 'vminus', 'i3'))
    #circuitComponents.append(Resistor(400, 'vminus', 'vplus', 'i0'))
    #circuitComponents.append(ISrc(0.1, 'vminus', 'vplus', 'i1'))
    #circuitComponents.append(Resistor(100, 'vminus', 'vplus', 'i2'))
    print theveninEquivalent(circuitComponents, 'vplus', 'vminus', 'isc').equation
