#!/usr/bin/env ruby

require File.join File.dirname(__FILE__), 'circuit.rb'
require 'nokogiri'
require 'set'

# :nodoc: SVG generation methods
class TruthTable
  # Path to the SVG shape for the gates using this truth table.
  def shape_svg_file
    File.expand_path "visualizer/shapes/#{@name.gsub(/\d/, '')}.svg",
                     File.dirname(__FILE__)
  end
  
  # ID for the SVG <symbol> with the shape of the gate using this truth table.
  def svg_symbol_id
    @svg_symbol_id ||= "svgsym-gate-type-#{@name.gsub(/\d/, '')}"
  end

  # Shape of the gate using this truth table, in SVG.
  #
  # This result is suitable for embedding in SVG circuit diagrams.
  def svg_shape
    @svg_shape ||= svg_shape!
  end
  
  # svg_shape without caching. This should not be called directly.
  def svg_shape!
    svg = File.read shape_svg_file
    # Get rid of the XML doctype.
    svg.sub! /\<\?xml.*\?\>/, ''
    svg.strip!

    # Get rid of namespaces, version, and scaling.
    tag = /\<svg[^\>]*\>/.match(svg)[0]
    tag.gsub! /xmlns\:?\w*\="[^"]*"/, ''
    tag.gsub! /version="[^"]*"/, ''
    svg.sub! /\<svg[^\>]*\>/, tag
    
    svg
  end
  
  # SVG <symbol> directive.  
  def svg_symbol
    @svg_symbol ||= svg_symbol!
  end
  
  # svg_symbol without caching. This should not be called directly.
  def svg_symbol!
    svg = svg_shape

    # Replace <svg> with <symbol id=...>.
    svg.sub! '<svg ', %Q|<symbol preserveAspectRatio="none" id="#{svg_symbol_id}" |
    svg.sub! '</svg>', '</symbol>'
    
    svg
  end
  
  # Hash containing the :width and :height of the image.
  def shape_size
    @shape_size ||= shape_size!
  end
  
  # shape_size without caching. This should not be called directly.
  def shape_size!
    bounds = /viewBox=\"([^"]*)"/.match(svg_shape)[1].split.map(&:to_f)
    { :width => bounds[2] - bounds[0], :height => bounds[3] - bounds[1] }
  end 
end  # class TruthTable

# :nodoc: SVG generation methods.
class Gate
  # ID of the gate shape in the SVG output.
  def svg_id
    "gate__#{@name}"
  end
  
  # Description of the gate's node in Graphviz's DOT language.
  def to_graphviz
    truth_table = type.truth_table
    shape_svg = truth_table.shape_svg_file
    shape_size = truth_table.shape_size
    shape_ratio = shape_size[:width] / shape_size[:height]
    %Q|#{svg_id} [id="#{svg_id}",shape=box,style=solid,label="#{@name}",ratio=#{shape_ratio}];|
  end
end  # class Gate

# :nodoc: SVG generation methods.
class Circuit
  # A string containing the circuit's representation in Graphviz's DOT language.
  def to_graphviz
    dot = ["digraph G {", "rankdir=LR;"]
    gates.each { |name, gate| dot << gate.to_graphviz }
    gates.each do |name, gate|
      gate.in_gates.each do |in_gate|
        next unless in_gate
        dot << %Q|#{in_gate.svg_id} -> #{gate.svg_id} [arrowhead=none,headclip=false,tailclip=false,id="wire__#{in_gate.name}__#{gate.name}"];|
      end
    end
    dot << "};"
    dot.join
  end
  
  # A string containing a circuit diagram using automated layout, in SVG.
  def to_svg
    svg_fragments = []
    IO.popen 'dot -Tsvg', 'r+' do |graphviz|
      graphviz.write to_graphviz
      graphviz.close_write
      svg_fragments << graphviz.read until graphviz.eof?
    end
    svg = svg_fragments.join
    
    # Inject the gate symbols in the SVG.
    svg.sub! /(\<svg[^>]*\>)/, "\\1#{svg_symbol_defs}"
    svg = svg_gates_to_symbols svg
    
    # Remove crud from SVG.
    svg.gsub! /\<\!\-\-.*?\-\-\>/m, ''  # Comments
    svg.gsub! /\n\s*\n/m, "\n"  # Repeated newlines
    
    svg    
  end

  # SVG code that defines all the symbols used by the gates in this circuit.
  def svg_symbol_defs
    gates.map { |_, g| g.type.truth_table }.uniq!.map(&:svg_symbol).join
  end
  
  # Replaces the SVG code for gates with references to the gates' symbols.
  #
  # Assumes the gates' symbols are polygons. 
  def svg_gates_to_symbols(svg_bits)
    svg_doc = Nokogiri::XML svg_bits
    gates.each do |name, gate|
      # The graphviz-generated SVG looks like this:
      # <g id="gate__name">
      #   <polygon ....>  -- contains a box representing the gate
      #   <text ...->  -- the gate label, plus more markup 
      gate_group = svg_doc.root.css("\##{gate.svg_id}")[0]  # The <g> element.
      gate_box = gate_group.css('polygon')[0]  # The <polygon> inside the g.
      
      # Compute the bounding box around the polygon representing the gate. We
      # tell graphviz to generate a box, but this code will handle any polygon.
      bounding_box = gate_box.attr('points').split.map { |token|
        token.split(',').map(&:to_f)
      }
      x_bounds = bounding_box.map(&:first)
      x0 = x_bounds.min
      xl = x_bounds.max - x0
      y_bounds = bounding_box.map(&:last)
      y0 = y_bounds.min
      yl = y_bounds.max - y0
      
      # Replace the <polygon> shape with a <use> pointing to the gate symbol. 
      symbol_id = gate.type.truth_table.svg_symbol_id
      symbol_ref_xml =
          %Q|<use xlink:href="\##{symbol_id}" x="#{x0}" width="#{xl}" y="#{y0}" height="#{yl}"/>|
      gate_box.after(symbol_ref_xml).remove
      
      # Move the gate at the end of the SVG, so gates are painted after wires.
      parent = gate_group.parent
      gate_group.remove
      parent.add_child gate_group
    end
    svg_doc.to_xml
  end
end  # class Circuit

# :nodoc: SVG generation code.
class Simulation
  attr_reader :circuit
end  # class Simulation

# Command-line controller for the layout tool.
class LayoutCli
  def run(args)
    if args.length == 0
      # Compute layout.
      sim = Simulation.from_file STDIN
      STDOUT.write sim.circuit.to_svg
    else
      # Package SVG in input.
      svg_bits = STDIN.read
      input = File.read args.first
      svg_offset = input.index(/^layout$/m) || input.length
      input[svg_offset..-1] = "layout\n" + svg_bits
      File.open(args.first, 'wb') { |f| f.write input }
    end
  end
end  # class LayoutCli 

LayoutCli.new.run(ARGV) if __FILE__ == $0
