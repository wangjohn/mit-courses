This directory contains the public and private test cases for the circuit
simulation problem. Cases 1-5 are public, and cases 6-10 are private. 

If you are reading this document, you probably want to write a new test. Tests
1-5 should supply good models. This file documents the file format and the steps
for making a test work with the visualizer.

Each line in a test case starts with a command. 

0) Comments
Input lines that start with the # character are ignored by the simulator.

GATE FUNCTIONS
The first lines of a test case describe the functions implemented by the gates,
e.g. nand2 (2-input negated logical and). The functions are described using the
sequence of values in a function's truth table. The command for describing a new
function (table) is:
table <truth table name> <2^n 0/1 values>

GATE TYPES
The next lines in a test case describe the types available in the gate library.
A gate type corresponds to a physical gate's specification, and covers the
gate's functionality and timing. The command for a new gate type is:
type <type name> <truth table name> <gate delay>

GATES
The circuit to be simulated is described using a netlist format. Each gate is
listed, together with the gates that its inputs are connected to. The following
command instantiates a gate:
gate <gate name> <type name> <names of gates supplying inputs>

PROBES
Any gate may be probed, and the output of the simulation is the list of all
transitions of the gates which are probed. A gate may not be probed twice,
because that would be pointless. The command is:
probe <gate name>

EXTERNAL INPUT
The external input to the circuit is modeled as transitions in some gates'
output values. To make circuits easy to understand, gates that receive outside
input are conventially 0-delay buffers whose type is named "eq". Input gates are
not connected to any other gates' output. The command for setting a gate's
output is:
flip <gate name> <0/1 gate output> <time of output change>

CIRCUIT COMPLETE
The simulator stops reading the input file after receiving the following
command:
done

VISUALIZATION SUPPORT
Laying out circuits for visualization requires complex algorithms which are 
outside the scope of our JavaScript software. The layout information is embedded
in the simulation input file, using the "layout" command. If present, "layout"
is the last command in an input file, and all the following lines are the
contents of a SVG file with the circuit layout.

Keep in mind that is the layout information is optional. Don't bother generating
it if you don't plan to use TRACE=jsonp to generate a visualization.

To add layout information to your own test case, follow these steps:
0) Install graphviz.
    sudo apt-get install graphviz
1) Get an automatically generated layout
    ruby layout.rb < tests/1gate.in > tests/1gate.svg
2) Tweak the layout in a SVG editor (e.g., Inkscape).
3) Inject the layout in the test case
    ruby layout.rb tests/1gate.in < tests/1gate.svg
