#!/bin/bash
# Bash script for running the Orange GUI on linux.mit.edu
#
#    ssh -X <user>@linux.mit.edu
#    ./run-orange-gui.sh
#
export PYTHONPATH=/afs/athena.mit.edu/course/6/6.034/lib/python2.6/dist-packages/orange:$PYTHONPATH
export LD_LIBRARY_PATH=/afs/athena.mit.edu/course/6/6.034/lib/python2.6/dist-packages/orange:$LD_LIBRARY_PATH
python /mit/6.034/lib/python2.6/dist-packages/orange/OrangeCanvas/orngCanvas.pyw

