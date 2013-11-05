from lib601.plotWindow import PlotWindow
from soar.io import io
import lib601.sonarDist as sonarDist

# called when the brain is loaded
def setup():
    robot.distance = []     # initialize list of distances to plot

# called when the start button is pushed
def brainStart():
    io.setForward(0.1) #start robot moving forward at 0.1 m/s

desiredDistance = 0.5
proportionalityConstant = 1.0

# called 10 times per second
def step():
    sonars = io.getSonars()
    distance = sonarDist.getDistanceRight(sonars) 
    print "Distance to wall: %.03f" % distance
    robot.distance.append(distance)   # append new distance to list

    # your code here (to calculate rotationalVelocity)
    rotationalVelocity = (desiredDistance - distance) * proportionalityConstant

    io.setForward(0.1)
    io.setRotational(rotationalVelocity)

# called when the stop button is pushed
def brainStop():
    p = PlotWindow()
    p.plot(robot.distance)    # plot the list of distances

# called when brain or world is reloaded (before setup)
def shutdown():
    pass
