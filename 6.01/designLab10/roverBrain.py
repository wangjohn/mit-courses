from soar.io import io
import lib601.sonarDist as sonarDist
from angleModel import bestKa
######################################################################
###
###          Brain methods
###
######################################################################

desiredRight = 0.4
desiredAngle = 0.0
forwardVelocity = 0.1
Kp = 3.
Ka = bestKa(Kp, -100.0, 100.0)[0]

desiredDistance = 8.5

def setup():
    robot.distances = []
    robot.rvels = [0]

def brainStart():
    io.setForward(0.1)

def lightExists(in1, in2):
    return max(in1, in2) > 6.0

def step():
    vNeck,vLeft,vRight,vCommon = io.getAnalogInputs()

    if lightExists(vLeft, vRight):
        forward = 0.1 * (desiredDistance - max(vLeft, vRight))
        rotational = vLeft - vRight
        io.setForward(forward)
        io.setRotational(rotational)
    else:
        wall_follower_step()

def wall_follower_step():
    sonars = io.getSonars()
    (distanceRight, theta) = sonarDist.getDistanceRightAndAngle(sonars)
    if theta == None:
        theta = robot.rvels[-1]
    if distanceRight == None:
        distanceRight = robot.distances[-1]
    print 'd_o =',distanceRight,' theta =',theta
    robot.distances.append(distanceRight)

    rotationalVelocity = Kp * (desiredRight - distanceRight) + Ka * (desiredAngle - theta)

    robot.rvels.append(rotationalVelocity)
    io.setRotational(rotationalVelocity)
    io.setForward(0.1)

def brainStop():
    pass

def shutdown():
    pass
