#!/usr/bin/env ruby

require 'pp'  # Used for printing stats.
require 'rubygems'  # Used to load json when TRACE=jsonp
require 'json'      # Used when TRACE=jsonp

# Truth table representation of the logic inside a gate.
class TruthTable
  attr_reader :input_count, :name
  
  # Creates a truth table.
  #
  # Args:
  #   name:: user-friendly name for the truth table
  #   output_list:: the entries in the truth table, in the standard order
  #                 (the inputs should look like an incrementing counter)
  #
  # Raises an exception if the list's length is not a power of two.
  def initialize(name, output_list)
    @name = name
    @table = TruthTable.build_table output_list
    @input_count = TruthTable.table_depth @table
  end
  
  # Computes this truth table's output for a list of inputs.
  #
  # Args:
  #   inputs
  def output(inputs)
    raise "Input list is incorrectly sized" unless inputs.length == @input_count
    inputs.inject(@table) { |table, input| table[input] }
  end
  
  # :nodoc: class methods
  class <<self
    # Builds an evaluation table out of a list of truth table values.
    #
    # Raises an exception if the list's length is not a power of two.
    def build_table(output_list)
      if output_list.length == 2
        unless output_list.all? { |output| output == 0 || output == 1 }
          raise "Invalid value in truth table output list"
        end
        return output_list
      end
      
      length = output_list.length
      raise "Output list length is not a power of two" unless length % 2 == 0
      half = length / 2
      [build_table(output_list[0, half]), build_table(output_list[half, half])]
    end
    
    # The depth (number of inputs) of a truth table.
    def table_depth(table)
      depth = 0
      while table.respond_to? :each
        depth += 1
        table = table[0]
      end
      depth
    end
  end
end  # class TruthTable

# A type of gate, such as a 2-input NAND with 60ps delay.
class GateType
  attr_reader :input_count, :truth_table, :name
  
  # Creates a gate type with a truth table and output delay.
  #
  # Args:
  #   name:: user-friendly name for the gate type
  #   truth_table:: TruthTable instance containing the gate's logic
  #   delay:: the time it takes an input transtion to cause an output transition
  #
  # Raises an exception if the delay is negative.
  def initialize(name, truth_table, delay)
    raise "Invalid delay" unless delay >= 0
    @name = name
    @truth_table = truth_table
    @input_count = truth_table.input_count
    @delay = delay
  end
  
  # The gate's output value, given a list of inputs.
  def output(inputs)
    @truth_table.output inputs
  end
  
  # The time of the gate's output transition, given a transition in the inputs.
  def output_time(input_time)
    @delay + input_time
  end
end  # class GateType

# A gate in a circuit.
class Gate
  attr_reader :name, :in_gates, :out_gates, :probed, :type
  
  # The gate's output at the current simulation time.
  attr_accessor :output
  
  # Creates an unconnected gate whose initial output is false.
  #
  # Args:
  #   name:: user-friendly name for the gate
  #   gate_type:: GateType instance specifying the gate's behavior
  def initialize(name, gate_type)
    @name = name
    @type = gate_type
    @in_gates = Array.new gate_type.input_count
    @out_gates = []
    
    @probed = false
    @output = 0
  end
  
  # Connects one of this gate's input terminals to another gate's output.
  #
  # Args:
  #   gate:: the gate whose output terminal will be connected
  #   terminal:: the number of this gate's input terminal that will be connected
  #              (using 0-based indexing)
  def connect_input(gate, terminal)
    unless terminal >= 0 && terminal < @in_gates.length
      raise "Invalid terminal number #{terminal}"
    end
    if @in_gates[terminal]
      raise "Input terminal #{terminal} of gate #{gate.name} already connected"
    end
    @in_gates[terminal] = gate
    gate.out_gates << self
  end
  
  # Marks this gate as probed, so the simulator will record its transitions.
  #
  # Raises an exception if the gate is already probed.
  def probe!
    raise "Gate already probed" if @probed
    @probed = true
  end
  
 # True if the gate was marked as probed by a call to probe!
  def probed?
    @probed
  end
  
  # True if all the gate's input terminals are connected to other gates.  
  def inputs_connected?
    @in_gates.all? { |input| input }
  end
  
  # True if the gate's output terminal is connected.
  def output_connected?
    !@out_gates.empty?
  end
  
  # True if all the gate's terminals are connected.
  def connected?
    inputs_connected? && output_connected? 
  end
  
  # The value that the gate's output will have when reflecting current inputs.
  #
  # The gate's output will not reflect this value right away. Each gate has a
  # delay from its inputs' transitions to the output's transition. The circuit
  # simulator is responsible for setting the appropriate time. 
  def transition_output
    @type.output @in_gates.map(&:output)
  end
  
  # The time that the gate's output will reflect a change in its inputs.
  #
  # Args:
  #   input_time:: the last time when the gate's inputs changed
  def transition_time(input_time)
    @type.output_time input_time
  end
  
  # A hash that obeys the JSON format restrictions, representing the gate.
  def as_json
    { :id => @name, :table => @type.truth_table.name,
      :type => @type.name, :probed => @probed,
      :inputs => @in_gates.map { |g| g && g.name },
      :outputs => @out_gates.map { |g| g && g.name },
    }
  end
end  # class Gate

# The topology of a combinational circuit, and a snapshot of its state.
#
# This class contains topological information about a circuit (how the gates are
# connected to each other) as well as information about the gates' states
# (values at their output terminals) at an instance of time.
class Circuit
  # Maps gate names to gates in the circuit.
  attr_reader :gates
  
  # Creates an empty circuit.
  def initialize
    @truth_tables = {}
    @gate_types = {}
    @gates = {}
  end
  
  # Adds a truth table that can be later attached to gate types.
  #
  # Args:
  #   name:: a unique string used to identify the truth table
  #   output_list:: list of outputs for the truth table
  #
  # Returns the newly created TruthTable instance.
  def add_truth_table(name, output_list)
    raise "Truth table name #{name} already used" if @truth_tables[name]
    @truth_tables[name] = TruthTable.new name, output_list
  end
  
  # Adds a gate type that can be later attached to gates.
  #
  # Args:
  #   name:: a unique string used to identify the gate type
  #   truth_table_name:: the name of the gate's truth table
  #   delay:: the gate's delay from an input transition to an output transition
  #
  # Returns the newly created GateType instance.
  def add_gate_type(name, truth_table_name, delay)
    raise "Gate type name #{name} already used" if @gate_types[name]
    unless truth_table = @truth_tables[truth_table_name]
      raise "Invalid truth table name #{truth_table_name}" 
    end
    raise "Invalid delay" if delay < 0
    @gate_types[name] = GateType.new name, truth_table, delay
  end
  
  # Adds a gate and connects it to other gates.
  #
  # Args:
  #   name:: a unique string used to identify the gate
  #   type_name:: the name of the gate's type
  #   input_names:: list of the names of gates whose outputs are connected to
  #                 this gate's inputs
  #
  # Returns the newly created Gate instance.
  def add_gate(name, type_name, input_names)
    raise "Gate name #{name} already used" if @gates[name]
    unless gate_type = @gate_types[type_name]
      raise "Invalid gate type name #{type_name}"
    end
    @gates[name] = new_gate = Gate.new(name, gate_type)
    input_names.each_with_index do |gate_name, index|
      unless gate = @gates[gate_name]
        raise "Invalid input gate name #{gate_name}"
      end
      new_gate.connect_input gate, index
    end
    new_gate
  end
  
  # Adds a gate to the list of outputs.
  def add_probe(gate_name)
    raise "Invalid gate name #{gate_name}" unless gate = @gates[gate_name]
    gate.probe!
  end
  
  # A hash that obeys the JSON format restrictions, representing the circuit.
  def as_json
    json = {}
    json[:gates] = @gates.map { |name, gate| gate.as_json }
    json
  end
end  # class Circuit

# A transition in a gate's output.
class Transition
  include Comparable
  
  attr_reader :gate, :new_output, :time
  
  # Creates a potential transition of a gate's output to a new value.
  #
  # Args:
  #   gate:: the Gate whose output might transition
  #   new_output:: the new output value that the gate will take
  #   time:: the time at which the Gate's output will match the new value
  def initialize(gate, new_output, time)
    raise "Invalid output value" unless (new_output == 0 || new_output == 1)
    @gate = gate
    @new_output = new_output
    @time = time
  end
  
  # :nodoc: override <=> so that we can compare in a priority queue
  def <=>(other)
    ((time_result = time <=> other.time) != 0) ?
        time_result : object_id <=> other.object_id
  end
  
  # True if the transition would cause an actual change in the gate's output.
  def valid?
    gate.output != @new_output
  end
  
  # Makes this transition effective by changing the gate's output.
  #
  # Raises an exception if applying the transition wouldn't cause an actual
  # change in the gate's output. 
  def apply!
    if gate.output == @new_output
      raise "Gate output should not transition to the same value"
    end
    
    gate.output = @new_output
    true
  end
  
  # :nodoc: debug output
  def inspect
    "#<Transition at t=#{@time}, gate #{@gate.name} -> #{@new_output}>"
  end
end  # class Transition

# Array-based priority queue implementation.
class PriorityQueue
  # Initially empty priority queue.
  def initialize
    @queue = []
    @min_index = nil
  end
  
  # Number of elements in the queue.
  def length
    @queue.length
  end
  
  # True if there are no elements in the queue.
  def empty?
    @queue.empty?
  end

  # Inserts an element in the priority queue.
  def <<(key)
    raise ArgumentError, "Cannot insert nil in the queue" if key.nil?
    
    @queue << key
    @min_index = nil
    self
  end
  alias :push :<<
  
  # The smallest element in the queue.
  def first
    @min_index ||= min_index!
    @queue[@min_index]
  end
  alias :min :first
  
  # Removes the minimum element in the queue.
  #
  # Returns the value of the first element, or nil if the queue was empty.
  def shift
    min_index ||= min_index!
    popped_key = @queue.delete_at min_index
    @min_index = nil
    popped_key
  end
  alias :pop :shift
  
  # Computes the index of the smallest element in the queue.
  def min_index!
    min = @queue[0]
    min_index = 0
    1.upto(@queue.length - 1) do |i|
      if (key = @queue[i]) < min
        min = key
        min_index = i
      end
    end
    min_index
  end
  private :min_index!
end  # class PriorityQueue

# Included in priority queue implementations to add workload instrumentation.
module PriorityQueueStats
  # :nodoc: constructor instrumentation for workload stats
  def initialize_stats
    @max_length = 0
    @insert_work = 0
    @insert_count = 0
    @extract_work = 0
    @extract_count = 0
  end
  
  # :nodoc: insertion instrumentation for workload stats
  def <<(key)
    @insert_work += length
    @insert_count += 1
    return_value = super
    @max_length = length if length > @max_length
    return_value
  end
  
  # :nodoc: extraction instrumentation for workload stats
  def shift
    @extract_work += length
    @extract_count += 1
    super
  end
  
  # Returns the instrumentation statistics.
  def stats
    (respond_to?(:extra_stats) ? extra_stats : {}).merge({
      :max_length => @max_length,
      :insert_count => @insert_count,
      :insert_avg => @insert_work / @insert_count.to_f,
      :extract_count => @extract_count,
      :extract_avg => @extract_work / @extract_count.to_f
    })
  end
end  # module PriorityQueueStats

# Included in priority queue implementation to show each operation.
module PriorityQueueDebug
  # :nodoc: log insertions
  def <<(key)
    puts "+ #{key.inspect}"
    super
  end
  
  # :nodoc: log extractions
  def shift
    return_value = super
    puts "- #{return_value.inspect}"
    return_value
  end
end  # module PriorityQueueDebug

# State needed to compute a circuit's state as it evolves over time.
class Simulation
  # Creates a simulation that will run on a pre-built circuit.
  #
  # The Circuit instance does not need to be completely built before it is given
  # to the class constructor. However, it does need to be complete before the
  # run method is called.
  #
  # Args:
  #   circuit:: the circuit whose state transitions will be simulated
  def initialize(circuit)
    @circuit = circuit
    @in_transitions = []
    
    @queue = nil
    @probes = []
    @probe_all_undo_log = []
  end
  
  # Configures the simulation's priority queue.
  #
  # The options hash accepts the following keys:
  #   :stats:: if true, the priority queue will be instrumented to provide
  #            workload statistics
  #   :debug:: if true, the priority queue will log each operation to stdout
  def queue(options)
    @queue = PriorityQueue.new

    if options[:stats]
      class <<@queue
        include PriorityQueueStats
      end
      @queue.initialize_stats
    end
    if options[:debug]
      class <<@queue
        include PriorityQueueDebug
      end
    end
    self
  end
  
  # Adds a transition to the simulation's initial conditions.
  #
  # The transition should involve one of the circuit's input gates.
  def add_transition(gate_name, output_value, output_time)
    raise "Invalid gate name" unless gate = @circuit.gates[gate_name]
    @in_transitions << [output_time, gate_name, output_value, gate]
  end
  
  # Runs the simulation for one time slice.
  #
  # A step does not equal one unit of time. The simulation logic ignores time
  # units where nothing happens, and bundles all the transitions that happen at
  # the same time in a single step.
  #
  # Returns the simulation time after the step occured.
  def step
    step_time = @queue.first.time
    
    # Need to apply all the transitions at the same time before propagating.
    transitions = []
    while @queue.first && @queue.first.time == step_time
      transition = @queue.shift
      next unless transition.valid?
      transition.apply!
      if transition.gate.probed?
        @probes << [transition.time, transition.gate.name,
                    transition.new_output]
      end
      transitions << transition
    end
    
    # Propagate the transition effects.
    transitions.each do |transition|
      transition.gate.out_gates.each do |gate|
        output = gate.transition_output
        time = gate.transition_time step_time
        @queue << Transition.new(gate, output, time)
      end
    end
    
    step_time
  end
  
  # Runs the simulation to completion.
  def run
    @queue ||= PriorityQueue.new
    @in_transitions.sort.each do |time, _, value, gate|
      @queue << Transition.new(gate, value, time)
    end
    
    step until @queue.empty?
    self
  end
  
  # Turns on probing for all gates in the simulation.
  def probe_all_gates!
    @circuit.gates.each do |_, gate|
      next if gate.probed?
      @probe_all_undo_log << gate
      gate.probe!
    end
  end

  # Reverts the effects of calling probe_all_gates!  
  def undo_probe_all_gates!
    @probe_all_undo_log.each do |gate|
      gate.instance_variable_set :@probed, false
    end
    @probe_all_undo_log = []
  end
  
  # Builds a simulation by reading a textual description from a file.
  #
  # Args:
  #   io:: a File-like object supplying the input
  #
  # Returns a new Simulation instance.
  def self.from_file(io)
    circuit = Circuit.new
    simulation = Simulation.new circuit
    
    loop do
      command = io.gets.split.map(&:strip)
      case command[0]
      when 'table'
        outputs = command[2..-1].map { |token| token.to_i }
        circuit.add_truth_table command[1], outputs
      when 'type'
        unless command.length == 4
          raise "Invalid number of arguments for gate type command"
        end
        circuit.add_gate_type command[1], command[2], command[3].to_i
      when 'gate'
        circuit.add_gate command[1], command[2], command[3..-1]
      when 'probe'
        unless command.length == 2
          raise "Invalid number of arguments for gate probe command"
        end
        circuit.add_probe command[1]
      when 'flip'
        unless command.length == 4
          raise "Invalid number of arguments for flip output command"
        end
        simulation.add_transition command[1], command[2].to_i, command[3].to_i
      when 'done'
        break
      end
    end
    simulation
  end
  
  # Reads the simulation's visual layout from a file.
  #
  # Args:
  #   io:: a File-like object supplying the input
  #
  # Returns self.
  def layout_from_file(io)
    loop do
      raise "Input lacks circuit layout information" if io.eof?
      if io.gets.strip == 'layout'
        @layout_svg = io.read
        # Get rid of the XML marker and doctype.
        @layout_svg.sub! /\<\?xml.*\?\>/, ''
        @layout_svg.sub! /\<\!DOCTYPE[^>]*\>/, ''
        @layout_svg.strip!
        break
      end
    end
    self
  end
  
  # Writes a textual description of the simulation's probe results to a file.
  #
  # Args:
  #   io:: a File-like object that receives the probe results
  def outputs_to_file(io)
    @probes.sort.each do |time, gate_name, output_value|
      io << "#{time} #{gate_name} #{output_value}\n"
    end
    self
  end
  
  # True if the simulation supports workload statistics.
  def has_stats?
    @queue.respond_to? :stats
  end
  
  # Pretty-prints the simulation stats to the standard output.
  def print_stats
    pp @queue.stats
    self
  end
  
  # A hash that obeys the JSON format restrictions, containing simulation data.
  def trace_as_json
    {
      :circuit => @circuit.as_json,
      :trace => @probes.sort,
      :layout => @layout_svg 
    }
  end
end  # class Simulation

# Command-line controller.
class Cli
  def run(args)
    sim = Simulation.from_file STDIN
    if ENV['TRACE'] == 'jsonp'
      sim.layout_from_file STDIN
      sim.probe_all_gates!
    end
    sim.queue(:stats => (ENV['TRACE'] == 'stats'),
              :debug => (ENV['DEBUG'] == 'true'))
    sim.run
    if sim.has_stats?
      sim.print_stats
    elsif ENV['TRACE'] == 'jsonp'
      sim.undo_probe_all_gates!
      print "onJsonp("
      print sim.trace_as_json.to_json
      print ");\n"
    else
      sim.outputs_to_file STDOUT
    end
  end
end  # class Cli

Cli.new.run(ARGV) if __FILE__ == $0
