#!/usr/bin/env python

import json   # Used when TRACE=jsonp
import os     # Used to get the TRACE environment variable
import re     # Used when TRACE=jsonp
import sys    # Used to smooth over the range / xrange issue.

# Python 3 doesn't have xrange, and range behaves like xrange.
if sys.version_info >= (3,):
    xrange = range


# Circuit simulation library.

class TruthTable:
    """Truth table representation of the logic inside a gate."""
    
    def __init__(self, name, output_list):
        """Creates a truth table from a list representation.
        
        Args:
            name: User-friendly name for the truth table.
            output_list: The entries in the truth table, in the standard order
                (the inputs should look like an incrementing counter).
        
        Raises:
            TypeError: An exception if the list's length is not a power of two.
        """
        self.name = name
        self.table = self._build_table(output_list)
        self.input_count = self._table_depth(self.table)

    def output(self, inputs):
        """Computes the output for this truth table, given a list of inputs."""
        if len(inputs) != self.input_count:
            raise ValueError('Inputs list is incorrectly sized')
        value = self.table
        for i in inputs:
            value = value[i]
        return value

    def _build_table(self, output_list):
        # Builds an evaluation table out of a list of truth table values.
        #
        # Raises:
        #    TypeError: An exception if the list's length is not a power of two.
        if len(output_list) == 2:
            for value in output_list:
                if value != 0 and value != 1:
                    raise TypeError('Invalid value in truth output list')
            return output_list
        else:
            length = len(output_list)
            if length % 2 != 0:
                raise ValueError('Invalid truth output list length')
            half = length // 2
            return [self._build_table(output_list[0:half]),
                    self._build_table(output_list[half:])]

    def _table_depth(self, table):
        # The depth (number of inputs) of a truth table.
        depth = 0
        while table != 0 and table != 1:
            depth += 1
            table = table[0]
        return depth
    
class GateType:
    """A type of gate, e.g. 2-input NAND with 60ps delay."""
    
    def __init__(self, name, truth_table, delay):
        """Creates a gate type with a truth table and output delay.
        
        Args:
            name: User-friendly name for the gate type.
            truth_table: TruthTable instance containing the gate's logic.
            delay: The time it takes an input transition to cause an output 
                transition.
        
        Raises:
            ValueError: An exception if the delay is negative.
        """
        self.name = name
        if delay < 0:
            raise ValueError('Invalid delay')
        self.truth_table = truth_table
        self.input_count = truth_table.input_count
        self.delay = delay

    def output(self, inputs):
        """The gate's output value, given a list of inputs."""
        return self.truth_table.output(inputs)
    
    def output_time(self, input_time):
        """The time of the gate's output transition.
        
        Computes the time of the output transition given an input transition 
        time.
        
        Args:
            input_time: Time of the input transition.
        """
        return self.delay + input_time

class Gate:
    """A gate in a circuit."""

    def __init__(self, name, gate_type):
        """ Creates an unconnected gate whose initial output is false.
        
        Args:
            name: User-friendly name for the gate.
            gate_type: GateType instance specifying the gate's behavior.
        """
        self.name = name
        self.gate_type = gate_type
        self.in_gates = [None for i in xrange(gate_type.input_count)]
        self.out_gates = []
        self.probed = False
        self.output = 0
  
    def connect_input(self, gate, terminal):
        """Connects one of this gate's input terminals to another gate's output.
        
        Args:
            gate: The gate whose output terminal will be connected.
            terminal: The number of this gate's input terminal that will be 
                connected (using 0-based indexing)
        """
        if self.in_gates[terminal] is not None:
            raise RuntimeError('Input terminal already connected')
        self.in_gates[terminal] = gate
        gate.out_gates.append(self)
      
    def probe(self):
        """Marks this gate as probed.
        
        So the simulator will record its transitions.
        
        Raises:
            RuntimeError: An exception if the gate is already probed.
        """
        if self.probed:
            raise RuntimeError('Gate already probed')
        self.probed = True

    def has_inputs_connected(self):
        """True if all the gate's input terminals are connected to other gates.
        """
        for input in self.in_gates:
            if input == None:
                return False
        return True
  
    def has_output_connected(self):
        """True if the gate's output terminal is connected to another gate."""
        return self.out_gates.length > 0
  
    def is_connected(self):
        """True if all the gate's inputs and outputs are connected."""
        return self.has_inputs_connected and self.has_output_connected

    def transition_output(self):
        """The value that the gate's output will have after transition.
        
        The gate's output will not reflect this value right away. Each gate has 
        a delay from its inputs' transitions to the output's transition. The 
        circuit simulator is responsible for setting the appropriate time. 
        """
        return self.gate_type.output([gate.output for gate in self.in_gates])
  
    def transition_time(self, input_time):
        """The time that the gate's output will reflect a change in its inputs.
        
        Args:
            input_time: The last time when the gate's inputs changed.
        """
        return self.gate_type.output_time(input_time)
    
    def as_json(self):
        """"A hash that obeys the JSON format, representing the gate."""
        return {'id': self.name, 'table': self.gate_type.truth_table.name,
                'type': self.gate_type.name, 'probed': self.probed,
                'inputs': [g and g.name for g in self.in_gates],
        'outputs': [g and g.name for g in self.out_gates]}

class Circuit:
    """The topology of a combinational circuit, and a snapshot of its state.
    
    This class contains topological information about a circuit (how the gates 
    are connected to each other) as well as information about the gates' states
    (values at their output terminals) at an instance of time.
    """
    def __init__(self):
        """Creates an empty circuit."""
        self.truth_tables = {}
        self.gate_types = {}
        self.gates = {}

    def add_truth_table(self, name, output_list):
        """Adds a truth table that can be later attached to gate types.
        
        Args:
            name: A unique string used to identify the truth table.
            output_list: A list of outputs for the truth table.
        
        Returns:
            A newly created TruthTable instance.
        """
        if name in self.truth_tables:
            raise ValueError('Truth table name already used')
        self.truth_tables[name] = TruthTable(name, output_list)
    
    def add_gate_type(self, name, truth_table_name, delay):
        """Adds a gate type that can be later attached to gates.
        
        Args:
            name: A unique string used to identify the gate type.
            truth_table_name: The name of the gate's truth table.
            delay: The gate's delay from an input transition to an output 
                transition.
        
        Returns:
            The newly created GateType instance.
        """
        if name in self.gate_types:
            raise ValueError('Gate type name already used')
        truth_table = self.truth_tables[truth_table_name]
        if delay < 0:
            raise ValueError('Invalid delay')
        self.gate_types[name] = GateType(name, truth_table, delay)
    
    def add_gate(self, name, type_name, input_names):
        """Adds a gate and connects it to other gates.
        
        Args:
            name: A unique string used to identify the gate.
            type_name: The name of the gate's type.
            input_names: List of the names of gates whose outputs are connected 
                to this gate's inputs.
        
        Returns:
            The newly created Gate instance.
        """
        if name in self.gates:
            raise ValueError('Gate name already used')
        gate_type = self.gate_types[type_name]
        self.gates[name] = new_gate = Gate(name, gate_type)
        for i in xrange(len(input_names)):
            gate = self.gates[input_names[i]]
            new_gate.connect_input(gate, i)
        return new_gate
    
    def add_probe(self, gate_name):
        """Adds a gate to the list of outputs."""
        gate = self.gates[gate_name]
        gate.probe()
      
    def as_json(self):
        """A hash that obeys the JSON format, representing the circuit."""
        json = {}
        json['gates'] = [gate.as_json() for gate in self.gates.itervalues()]
        return json

class Transition:
    """A transition in a gate's output."""
  
    def __init__(self, gate, new_output, time):
        """Creates a potential transition of a gate's output to a new value.
        
        Args:
            gate: The Gate whose output might transition.
            new_output: The new output value that the gate will take.
            time: The time at which the Gate's output will match the new value.
        
        Raises:
            ValueError: An exception if the output is not 0 or 1. 
        """
        if new_output != 0 and new_output != 1:
            raise ValueError('Invalid output value')
        self.gate = gate
        self.new_output = new_output
        self.time = time
        self.object_id = Transition.next_object_id()
    
    def __lt__(self, other):
        # :nodoc: Transitions should be comparable.
        return (self.time < other.time or
                (self.time == other.time and self.object_id < other.object_id))
    
    def __le__(self, other):
        # :nodoc: Transitions should be comparable.
        return (self.time < other.time or
                (self.time == other.time and self.object_id <= other.object_id))
    
    def __gt__(self, other):
        # :nodoc: Transitions should be comparable.
        return (self.time > other.time or
                (self.time == other.time and self.object_id > other.object_id))
    
    def __ge__(self, other):
        # :nodoc: Transitions should be comparable.
        return (self.time > other.time or
                (self.time == other.time and self.object_id >= other.object_id))
    
    # NOTE: Due to the comparisons' use of object_id, no two Transitions will be
    #       equal. So we don't need to override __eq__, __ne__, or __hash__.
      
    def is_valid(self):
        """True if the transition would cause an actual change in the gate's 
        output.
        """
        return self.gate.output != self.new_output
    
    def apply(self):
        """Makes this transition effective by changing the gate's output.
        
        Raises:
            ValueError: An exception if applying the transition wouldn't cause 
                an actual change in the gate's output.
        """
        if self.gate.output == self.new_output:
            raise ValueError('Gate output should not transition to the same '
                             'value')
        self.gate.output = self.new_output
    
    def __repr__(self):
        # :nodoc: debug output
        return ('<Transition at t=' + str(self.time) + ', gate ' + 
                self.gate.name + ' -> ' + str(self.new_output) + '>')
    
    # Next number handed out by Transition.next_object_id()
    _next_id = 0
    
    @staticmethod
    def next_object_id():
        """Returns a unique numerical ID to be used as a Transition's object_id.  
        """
        id = Transition._next_id
        Transition._next_id += 1
        return id

class PriorityQueue:
    """Array-based priority queue implementation."""
    def __init__(self):
        """Initially empty priority queue."""
        self.queue = []
        self.min_index = None
    
    def __len__(self):
        # Number of elements in the queue.
        return len(self.queue)
    
    def append(self, key):
        """Inserts an element in the priority queue."""
        if key is None:
            raise ValueError('Cannot insert None in the queue')
        self.queue.append(key)
        length = len(self.queue)
        self.siftup(length - 1)
        self.min_index = None

    def siftup(self, count):
        parent = count // 2
        if count == 0:
            pass
        elif self.queue[parent] >= self.queue[count]:
            self.queue[parent], self.queue[count] = self.queue[count], self.queue[parent]
            self.siftup(parent)
            
    def min(self):
        """The smallest element in the queue."""
        if len(self.queue) == 0:
            return None
        self._find_min()
        # The array is sorted in reverse order.
        return self.queue[self.min_index]
    
    def pop(self):
        """Removes the minimum element in the queue.
    
        Returns:
            The value of the removed element.
        """
        length = len(self.queue)
        heapsize = length - 1
        if length == 0:
            return None
        self.queue[heapsize], self.queue[0] = self.queue[0], self.queue[heapsize]
        popped_key = self.queue.pop()
        self.min_index = None
        # Min heapify the rest of the array
        self.minheapify(0, heapsize - 1)
        return popped_key
    
    def _find_min(self):
        # Computes the index of the minimum element in the queue.
        #
        # This method may crash if called when the queue is empty.
      if self.min_index is not None:
        return
      self.min_index = 0

    def minheapify(self, count, heapsize):
        if count > 0:
            l = count * 2
            r = count * 2 + 1
        else:
            l = 1
            r = 2
        if l <= heapsize and self.queue[l] < self.queue[count]:
            smallest = l
        else:
            smallest = count
        if r <= heapsize and self.queue[r] < self.queue[smallest]:
            smallest = r
        if smallest != count:
            self.queue[smallest], self.queue[count] = \
                                  self.queue[count], self.queue[smallest]
            self.minheapify(smallest, heapsize)
        
    def buildheap(self):
        heapsize = len(self.queue) - 1
        for x in range(heapsize/2,-1,-1):
            self.minheapify(x, heapsize)
    
class Simulation:
    """State needed to compute a circuit's state as it evolves over time."""
    
    def __init__(self, circuit):
        """Creates a simulation that will run on a pre-built circuit.
        
        The Circuit instance does not need to be completely built before it is 
        given to the class constructor. However, it does need to be complete 
        before the run method is called.
        
        Args:
            circuit: The circuit whose state transitions will be simulated.
        """
        self.circuit = circuit
        self.in_transitions = []
        
        self.queue = PriorityQueue()
        self.probes = []
        self.probe_all_undo_log = []

    def add_transition(self, gate_name, output_value, output_time):
        """Adds a transition to the simulation's initial conditions.
        
        The transition should involve one of the circuit's input gates.
        """
        gate = self.circuit.gates[gate_name]
        self.in_transitions.append([output_time, gate_name, output_value, gate])
    
    def step(self):
        """Runs the simulation for one time slice.
        
        A step does not equal one unit of time. The simulation logic ignores 
        time units where nothing happens, and bundles all the transitions that 
        happen at the same time in a single step.
        
        Returns:
            The simulation time after the step occurred.
        """ 
        step_time = self.queue.min().time
        
        # Need to apply all the transitions at the same time before propagating.
        transitions = []
        while len(self.queue) > 0 and self.queue.min().time == step_time:
          transition = self.queue.pop()
          if not transition.is_valid():
            continue
          transition.apply()
          if transition.gate.probed:
            self.probes.append([transition.time, transition.gate.name,
                                transition.new_output])
          transitions.append(transition)
        
        # Propagate the transition effects.
        for transition in transitions:
          for gate in transition.gate.out_gates:
            output = gate.transition_output()
            time = gate.transition_time(step_time)
            self.queue.append(Transition(gate, output, time))
        
        return step_time
    
    def run(self):
        """Runs the simulation to completion."""
        for in_transition in sorted(self.in_transitions):
            self.queue.append(Transition(in_transition[3], in_transition[2],
                                         in_transition[0]))
        while len(self.queue) > 0:
            self.step()
        self.probes.sort()
            
    def probe_all_gates(self):
        """Turns on probing for all gates in the simulation."""
        for gate in self.circuit.gates.itervalues():
            if not gate.probed:
                self.probe_all_undo_log.append(gate)
                gate.probe()

    def undo_probe_all_gates(self):
        """Reverts the effects of calling probe_all_gates!"""  
        for gate in self.probe_all_undo_log:
            gate.probed = False
        self.probe_all_undo_log = []
    
    @staticmethod
    def from_file(file):
        """Builds a simulation by reading a textual description from a file.
        
        Args:
            file: A File object supplying the input.
        
        Returns: A new Simulation instance.
        """
        circuit = Circuit()
        simulation = Simulation(circuit)
        
        while True:
            command = file.readline().split()
            if len(command) < 1:
                continue
            if command[0] == 'table':
                outputs = [int(token) for token in command[2:]]
                circuit.add_truth_table(command[1], outputs)
            elif command[0] == 'type':
                if len(command) != 4:
                    raise ValueError('Invalid number of arguments for gate type'
                                     ' command')
                circuit.add_gate_type(command[1], command[2], int(command[3]))
            elif command[0] == 'gate':
                circuit.add_gate(command[1], command[2], command[3:])
            elif command[0] == 'probe':
                if len(command) != 2:
                    raise ValueError('Invalid number of arguments for gate '
                                      'probe command')
                circuit.add_probe(command[1])
            elif command[0] == 'flip':
                if len(command) != 4:
                    raise ValueError('Invalid number of arguments for flip '
                                     'command')
                simulation.add_transition(command[1], int(command[2]), 
                                          int(command[3]))
            elif command[0] == 'done':
                break
        return simulation
    
    def layout_from_file(self, file):
        """Reads the simulation's visual layout from a file.
        
        Args:
            file: A File-like object supplying the input.
        
        Returns:
             self.
        """
        while True:
          line = file.readline()
          if len(line) == 0:
              raise ValueError('Input lacks circuit layout information')
          if line.strip() == 'layout':
              svg = file.read()
              # Get rid of the XML doctype.
              svg = re.sub('\\<\\?xml.*\\?\\>', '', svg)
              svg = re.sub('\\<\\!DOCTYPE[^>]*\\>', '', svg)
              self.layout_svg = svg.strip()
              break
        self
    
    def trace_as_json(self):
        """A hash that obeys the JSON format, containing simulation data."""
        return {'circuit': self.circuit.as_json(), 'trace': self.probes,
                'layout': self.layout_svg}
    
    def outputs_to_line_list(self):
        return [' '.join([str(probe[0]), probe[1], str(probe[2])]) for probe in self.probes]
    
    def outputs_to_file(self, file):
        """Writes a textual description of the simulation's probe results to a 
        file.
        
        Args:
            file: A File object that receives the probe results.
        """
        for line in self.outputs_to_line_list():
            file.write(line)
            file.write("\n")
            
    def jsonp_to_file(self, file):
        """Writes a JSONP description of the simulation's probe results to a 
        file.
        
        Args:
            file: A File object that receives the probe results.
        """
        file.write('onJsonp(')
        json.dump(self.trace_as_json(), file)
        file.write(');\n')

# Command-line controller.
if __name__ == '__main__':
    import sys
    sim = Simulation.from_file(sys.stdin)
    if os.environ.get('TRACE') == 'jsonp':
        sim.layout_from_file(sys.stdin)
        sim.probe_all_gates()
    sim.run()
    if os.environ.get('TRACE') == 'jsonp':
        sim.undo_probe_all_gates()
        sim.jsonp_to_file(sys.stdout)
    else:
        sim.outputs_to_file(sys.stdout)

