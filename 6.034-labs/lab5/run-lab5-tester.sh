#!/bin/bash
# Shell script for running lab5.py with the proper environment settings.
#
export LD_LIBRARY_PATH=/afs/athena.mit.edu/course/6/6.034/lib/python2.5/dist-packages/orange
python tester.py lab5.py
