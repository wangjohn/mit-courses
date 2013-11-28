from soar.io import io
import graph
import lib601.idealReadings as idealReadings
import lib601.markov as markov
import lib601.dist as dist
import lib601.sonarDist as sonarDist
import os,os.path

####################################################################
###
### Preliminaries -- do not change the following code
###
####################################################################

labPath = os.getcwd()
WORLD_FILE = os.path.join(labPath,'oneDWorld.py')
FORWARD_VELOCITY = 0.5

# Robot's Ideal Readings
ideal = None

# Where the robot will be in the world
(xMin, xMax) = (0.5, 7.5)
robotY = y = 1.0

# Distance and Gain for Wall Following
desiredRight = 0.5
(Kp,Ka) = (30,3.646)

# Maximum "good" sonar reading
sonarMax = 1.5

#method to discretize values into boxes of size gridSize
def discretize(value, gridSize, maxBin=float('inf')):
    return min(int(value/gridSize), maxBin)

#method to clip x to be within lo and hi limits, inclusive
def clip(x, lo, hi):
    return max(lo, min(x, hi))

####################################################################
###
###          Probabilistic Models -- you may change this code
###
####################################################################

import lib601.dist as dist
# lib601.dist provides methods for manipulating discrete probability distributions
# see the documentation for details

# Number of discrete locations and discrete observations
numStates = 75 
numObservations = 3

#observation model
def obsModel(s):
    if numObservations < 10:
        return dist.mixture(dist.deltaDist(ideal[s]), dist.uniformDist(range(numObservations)), float(numObservations) / 15.)
    return dist.mixture(dist.triangleDist(ideal[s], int(numObservations / 6.0) + 2), dist.uniformDist(range(numObservations)), 0.8)

#transition model
def transModel(s):
    distance = FORWARD_VELOCITY * 0.1
    result1 = (float(s) / numStates) * (xMax - xMin) + distance
    result2 = (float(s+1) / numStates) * (xMax - xMin) + distance
    
    state1 = clip(int(float(result1) * numStates / (xMax - xMin)), 0, numStates-1)
    state2 = clip(int(float(result2) * numStates / (xMax - xMin)), 0, numStates-1)

    prob = float(distance) / (xMax - xMin) * numStates
    return dist.mixture(dist.deltaDist(state1), dist.deltaDist(state2), 1.0 - (prob % 1.0))


######################################################################
###
###          Brain Methods -- do not change the following code
###
######################################################################

def setup():
    global ideal
    ideal = idealReadings.computeIdealReadings(WORLD_FILE, xMin, xMax, robotY, numStates, numObservations)
    if not (hasattr(robot,'g') and robot.g.winfo_exists()):
        robot.g = graph.Grapher(ideal)
        robot.nS = numStates
    if robot.nS != numStates:
        robot.g.destroy()
        robot.g = graph.Grapher(ideal)
        robot.nS = numStates
    robot.estimator = markov.StateEstimator(dist.uniformDist(range(numStates)), transModel, obsModel)
    robot.g.updateObsGraph([0 for s in xrange(numStates)])
    robot.g.updateBeliefGraph([robot.estimator.belief.prob(s) for s in xrange(numStates)])

def brainStart():
    pass

def step():
    sonars = io.getSonars()

    # current discretized sonar reading
    left = discretize(sonars[0], sonarMax/numObservations, numObservations-1)
    
    # GRAPHICS
    if robot.g is not None:
        # update observation model graph
        robot.g.updateObsLabel(left)
        robot.g.updateObsGraph([obsModel(s).prob(left) for s in xrange(numStates)])

    # update belief state
    robot.estimator.update(left)

    # GRAPHICS
    if robot.g is not None:
        # update belief graph
        robot.g.updateBeliefGraph([robot.estimator.belief.prob(s) for s in xrange(numStates)])
    
    # DL6 Angle Controller

    (distanceRight, theta) = sonarDist.getDistanceRightAndAngle(sonars)
    if not theta:
       theta = 0
       print 'Angle too large!'
    e = desiredRight-distanceRight
    ROTATIONAL_VELOCITY = Kp*e - Ka*theta

    io.setForward(FORWARD_VELOCITY)
    io.setRotational(ROTATIONAL_VELOCITY)

def brainStop():
    pass

def shutdown():
    pass
