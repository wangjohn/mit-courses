import lib601.sm as sm
from soar.io import io
import lib601.sonarDist as sonarDist
import lib601.plotWindow as plotWindow
from angleModel import bestKa

desiredRight = 0.4
desiredAngle = 0.0
forwardVelocity = 0.1
Kp = 8.75
Ka = bestKa(Kp, -100.0, 100.0)[0]

def setup():
    robot.distances = []
    robot.rvels = []

def brainStart():
    io.setForward(forwardVelocity)

def step():
    sonars = io.getSonars()
    (distanceRight, theta) = sonarDist.getDistanceRightAndAngle(sonars)
    print 'd_o =',distanceRight,' theta =',theta
    if theta == None:
        theta = robot.rvels[-1]
    if distanceRight == None:
        distanceRight = robot.distances[-1]
    robot.distances.append(distanceRight)

    rotationalVelocity = Kp * (desiredRight - distanceRight) + Ka * (desiredAngle - theta)

    robot.rvels.append(rotationalVelocity)
    io.setRotational(rotationalVelocity)

def brainStop():
    withClips = [(x,max(-0.5,min(0.5,x))) for x in robot.rvels]
    plotWindow.PlotWindow(title="distanceRight vs time").plot(robot.distances)
    plotWindow.PlotWindow(title="rotationalVelocity vs time").plot(withClips)

def shutdown():
    pass
