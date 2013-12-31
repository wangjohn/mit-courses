#!/usr/bin/env ruby

require 'rubygems'  # Used to load gems when QUEUE=lib or TRACE=jsonp
require 'json'      # Used when TRACE=jsonp
require 'rbtree'    # Used when QUEUE=lib

# A wire in an on-chip circuit.
#
# Wires are immutable, and are either horizontal or vertical.
class Wire
  # The wire's user-visible name.
  attr_accessor :name
  # The X coordinate for the wire's lowest / leftmost endpoint. 
  attr_reader :x1
  # The Y coordinate for the wire's lowest / leftmost endpoint. 
  attr_reader :y1
  # The X coordinate for the wire's highest / rightmost endpoint. 
  attr_reader :x2
  # The X coordinate for the wire's highest / rightmost endpoint. 
  attr_reader :y2
  # Unique numeric id for the wire.
  attr_reader :id
  
  # Creates a wire.
  #
  # Raises an ArgumentError if the coordinates don't make up a horizontal wire
  # or a vertical wire.
  #
  # Args:
  #   name:: the wire's user-visible name
  #   x1:: the X coordinate of the wire's first endpoint
  #   y1:: the Y coordinate of the wire's first endpoint
  #   x2:: the X coordinate of the wire's last endpoint
  #   y2:: the Y coordinate of the wire's last endpoint
  def initialize(name, x1, y1, x2, y2)
    # Normalize the coordinates.
    x1, x2 = x2, x1 if x1 > x2
    y1, y2 = y2, y1 if y1 > y2
    
    @name = name
    @x1, @y1 = x1, y1
    @x2, @y2 = x2, y2
    @id = self.class.next_object_id
    
    unless horizontal? or vertical?
      raise ArgumentError, "#{inspect} is neither horizontal nor vertical"
    end
  end
  
  # True if the wire's endpoints have the same Y coordinates.
  def horizontal?
    @y1 == @y2
  end
  
  # True if the wire's endpoints have the same X coordinates.
  def vertical?
    @x1 == @x2
  end
  
  # True if this wire intersects another wire.
  def intersects?(other_wire)
    # NOTE: we assume that wires can only cross, but not overlap.
    return false if horizontal? == other_wire.horizontal?
    
    if horizontal?
      h = self
      v = other_wire
    else
      h = other_wire
      v = self
    end
    v.y1 <= h.y1 && h.y1 <= v.y2 && h.x1 <= v.x1 && v.x1 <= h.x2
  end
  
  # :nodoc: nicer formatting to help with debugging
  def inspect
    "Wire #{@name}: (#{x1}, #{y1}) - (#{x2}, #{y2})"
  end
  
  # A hash that obeys the JSON format restrictions, representing the wire.
  def as_json
    {:id => @name, :x => [@x1, @x2], :y => [@y1, @y2]}
  end
  
  # Next number handed out by Wire.next_object_id()
  @next_id = 0
  
  # Returns a unique numerical ID to be used as a Wire's id.
  def self.next_object_id
    id = @next_id
    @next_id += 1
    id
  end
end  # class Wire

# The layout of one layer of wires in a chip.
class WireLayer
  # Creates a layer layout with no wires. 
  def initialize
    @wires = {}
  end
  
  # The wires in the layout.
  def wires
    @wires.values
  end
  
  # Adds a wire to a layer layout.
  #
  # Args:
  #   name:: the wire's unique name
  #   x1:: the X coordinate of the wire's first endpoint
  #   y1:: the Y coordinate of the wire's first endpoint
  #   x2:: the X coordinate of the wire's last endpoint
  #   y2:: the Y coordinate of the wire's last endpoint
  #
  # Raises an exception if the wire isn't perfectly horizontal (y1 = y2) or
  # perfectly vertical (x1 = x2).
  def add_wire(name, x1, y1, x2, y2)
    raise "Wire name #{name} not unique" if @wires.has_key?(name)
    @wires[name] = Wire.new(name, x1, y1, x2, y2)
  end
  
  # A hash that obeys the JSON format restrictions, representing the layout.
  def as_json
    { :wires => @wires.map { |name, wire| wire.as_json } }
  end
  
  # Builds a wire layer layout by reading a textual description from a file.
  #
  # Args:
  #   io:: a File-like object supplying the input
  #
  # Returns a new Simulation instance.
  def self.from_file(io)
    layer = WireLayer.new
    
    loop do
      command = io.gets.split.map(&:strip)
      case command[0]
      when 'wire'
        coordinates = command[2, 4].map(&:to_i)
        layer.add_wire command[1], *coordinates
      when 'done'
        break
      end
    end
    layer
  end
end  # class WireLayer

# Array-based range index implementation.
class RangeIndex
  # Initially empty range index.
  def initialize
    @data = []
  end
  
  # Inserts a key in the range index.
  def add(key)
    raise ArgumentError, "Cannot insert nil in the index" if key.nil?
    @data << key
    self
  end
  
  # Removes a key from the range index.
  def delete(key)
    @data.delete key
  end
  
  # Array of [key, value] pairs whose keys fall within the given range.
  def [](range)
    @data.select { |key| range.include? key }
  end
  
  # Counts the number of keys that fall within the given range.
  def count(range)
    @data.inject(0) { |sum, key| sum + (range.include?(key) ? 1 : 0) }
  end
end  # class RangeIndex

# Mixed into RangeIndex instances to build a trace for the visualizer. 
module RangeIndexTracing
  # Sets the object receiving tracing info.
  def initialize_tracing(trace)
    @trace = trace
  end
  
  # see: RangeIndex#add 
  def add(key)
    @trace.push :type => 'add', :id => key.wire.name
    super
  end
  
  # see: RangeIndex#delete 
  def delete(key)
    @trace.push :type => 'delete', :id => key.wire.name
    super
  end
  
  # see: RangeIndex#[]
  def [](range)
    result = super
    @trace.push :type => 'list', :from => range.first.key,
        :to => range.last.key, :ids => result.map { |key| key.wire.name }
    result
  end
  
  # see: RangeIndex#count
  def count(range)
    result = super
    @trace.push :type => 'count', :from => range.first.key,
                :to => range.last.key, :count => result
  end
end  # class RangeIndexTracing

# Records the result of the circuit verifier (pairs of crossing wires).
class ResultSet
  def initialize
    @crossings = []
  end
  
  # Records the fact that two wires are crossing.
  def add_crossing(wire1, wire2)
    @crossings << [wire1.name, wire2.name].sort
  end
  
  # Write the result to a file.
  def to_io(io)
    @crossings.each { |crossing| io.puts crossing.join(' ') }
  end
end

# Mixed into ResultSet instances to build a trace for the visualizer. 
module ResultSetTracing
  # Sets the object receiving tracing info.
  def initialize_tracing(trace)
    @trace = trace
  end
  
  # see: ResultSet#add_crossing 
  def add_crossing(wire1, wire2)
    @trace.push :type => 'crossing', :id1 => wire1.name, :id2 => wire2.name
    super
  end
end  # class ResultSet

# Wraps a wire and the key representing it in the range index.
#
# Once created, a key-wire pair is immutable.
class KeyWirePair
  attr_reader :key
  attr_reader :wire_id
  
  # The wire associated with the key.
  #
  # If the wire 
  attr_reader :wire
  
  # Creates a new key for insertion in the range index.
  def initialize(key, wire)
    @key = key
    if self.class == KeyWirePair
      raise "Use KeyWirePairL or KeyWirePairH for queries" unless wire
      @wire_id = wire.id
    end
    @wire = wire
  end

  # :nodoc: delegate comparison to keys   
  def <=>(other)
    result = @key <=> other.key 
    (result == 0) ? @wire_id <=> other.wire_id : result
  end
  
  # :nodoc: delegate equality to keys
  def ==(other)
    @key == other.key && @wire_id == other.wire_id
  end
  
  # :nodoc: delegate hashing to keys
  def hash
    [@key, @wire_id].hash
  end
end  # class KeyWirePair

# A KeyWirePair that is used as the low end of a range query.
#
# This KeyWirePair is smaller than all other KeyWirePairs with the same key.
class KeyWirePairL < KeyWirePair
  def initialize(key)
    super(key, nil)
    @wire_id = -1_000_000_000
  end
end  # class KeyWirePairL

# A KeyWirePair that is used as the high end of a range query.
#
# This KeyWirePair is larger than all other KeyWirePairs with the same key.
class KeyWirePairH < KeyWirePair
  def initialize(key)
    super(key, nil)
    @wire_id = 1_000_000_000
  end
end  # class KeyWirePairH

# Checks whether a wire network has any crossing wires.
class CrossVerifier
  # Verifier for a layer of wires.
  #
  # Once created, the verifier can list the crossings between wires (the 
  # wire_crossings method) or count the crossings (count_crossings).
  def initialize(layer)
    @events = []
    events_from_layer layer
    @events.sort!
    
    @index = RangeIndex.new
    @result_set = ResultSet.new
    @performed = false
  end
  
  # Returns the number of pairs of wires that cross each other.
  def count_crossings
    raise "Already performed a computation" if @performed
    @performed = true
    compute_crossings! true
  end

  # An array of pairs of wires that cross each other.
  def wire_crossings
    raise "Already performed a computation" if @performed
    @performed = true
    compute_crossings! false
  end
  
  # Populates the sweep line events from the wire layer.
  def events_from_layer(layer)
    left_edge = layer.wires.map(&:x1).min - 1
    layer.wires.each do |wire|
      if wire.horizontal?
        @events << [left_edge, 0, wire.id, :add, wire]
      else
        @events << [wire.x1, 1, wire.id, :query, wire]
      end
    end    
  end

  # Implements count_crossings and wire_crossings.
  def compute_crossings!(count_only = true)
    if count_only
      result = 0
    else
      result = @result_set
    end
    @events.each do |event_x, _, _, event_type, wire|
      case event_type
      when :add
        @index.add KeyWirePair.new(wire.y1, wire)
      when :query
        trace_sweep_line event_x

        range = KeyWirePairL.new(wire.y1)..KeyWirePairH.new(wire.y2)
        cross_wires = @index[range].map(&:wire).
            select { |cross_wire| wire.intersects?(cross_wire) }
        if count_only
          result += cross_wires.length
        else
          cross_wires.each do |cross_wire|
            result.add_crossing wire, cross_wire
          end
        end
      end
    end
    result
  end
  private :compute_crossings!
  
  # Enables tracing of range index operations. 
  def trace!
    @trace = []
    class <<@index
      include RangeIndexTracing
    end
    @index.initialize_tracing @trace
    class <<@result_set
      include ResultSetTracing
    end
    @result_set.initialize_tracing @trace
    class <<self
      include CrossVerifierTracing
    end
    self.initialize_tracing @trace
  end
  
  # When tracing is enabled, adds info about where the sweep line is.
  #
  # Args:
  #   x:: the coordinate of the vertical sweep line
  def trace_sweep_line(x)
    # NOTE: this no-op method is replaced when trace! is called.
  end
  
  # An array that obeys the JSON format restrictions with the index operations.
  def trace_as_json
    @trace
  end
end  # class CrossVerifier

# Mixed into CrossingVerifier instances to build a trace for the visualizer. 
module CrossVerifierTracing
  # Sets the object receiving tracing info.
  def initialize_tracing(trace)
    @trace = trace
  end
  
  # see: CrossVerifier#trace_sweep_line
  def trace_sweep_line(x)
    @trace.push :type => 'sweep', :x => x
  end
end  # module CrossVerifierTracing

# Command-line controller.
class Cli
  def run(args)
    layer = WireLayer.from_file STDIN
    verifier = CrossVerifier.new layer
    
    if ENV['TRACE'] == 'jsonp'
      verifier.trace!
      result = verifier.wire_crossings
      json = {
        :layer => layer.as_json,
        :trace => verifier.trace_as_json
      }
      print "onJsonp("
      print json.to_json
      print ");\n"
    elsif ENV['TRACE'] == 'list'
      verifier.wire_crossings.to_io STDOUT
    else
      puts verifier.count_crossings
    end
  end
end  # class Cli

Cli.new.run(ARGV) if __FILE__ == $0
