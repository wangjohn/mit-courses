import lib601.gfx as gfx
from soar.io import io

# this function is called when the brain is (re)loaded
def setup():
    pass

# this function is called when the start button is pushed
def brainStart():
    pass

# this function is called 10 times per second
def step():
    #io.sonarMonitor(True)

    #read in the sonar readings from the robot.
    #s will be a list of 8 values, with the value at index
    #0 representing the left-most sonar
    s = io.getSonars()

    #print the reading from the central sonar
    print s[3]

    #set the robot's forward and rotational velocities to 0
    io.setForward(0)
    io.setRotational(0)

# called when the stop button is pushed
def brainStop():
    pass

# called when brain or world is reloaded (before setup)
def shutdown():
    pass
