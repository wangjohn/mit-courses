from soar.io import io
import graph
import lib601.idealReadings as idealReadings
import lib601.markov as markov
import lib601.dist as dist
import lib601.sonarDist as sonarDist
import lib601.util as util
import os,os.path
import math

####################################################################
###
### Preliminaries -- do not change the following code
###
####################################################################

labPath = os.getcwd()
WORLD_FILE = os.path.join(labPath,'oneDWorld.py')
FORWARD_VELOCITY = 0.2

# Robot's Ideal Readings
ideal = None

# Where the robot will be in the world
(xMin, xMax) = (0.5, 7.5)
robotY = y = 1.0

# Number of discrete locations 
numStates = 200 

# Number of discrete observations
sonarMax = 1.5 #maximum 'good' sonar reading
numObservations = 70

#method to discretize values into boxes of size gridSize
def discretize(value, gridSize, maxBin=float('inf')):
    return min(int(value/gridSize), maxBin)

#method to clip x to be within lo and hi limits, inclusive
def clip(x, lo, hi):
    return max(lo, min(x, hi))

#desired distance from right wall
desiredRight = 0.5
Kp,Ka = (10.0,2.0)

####################################################################
###
###          Probabilistic Models -- you may change this code
###
####################################################################

import lib601.dist as dist
# lib601.dist provides methods for manipulating discrete probability distributions
# see the documentation for details

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

def confidentLocation(belief):
    max_location = None
    max_prob = 0
    for location in belief.support():
        prob = belief.prob(location)
        if max_location == None or prob > max_prob:
            max_location = location
            max_prob = prob

    num_states = convert_into_states(0.075)
    max_location_range = range(max_location - num_states, max_location + num_states + 1)

    second_max_location = None
    second_max_prob = 0
    for location in belief.support():
        prob = belief.prob(location)
        if (second_max_location == None or prob > second_max_prob) and location not in max_location_range:
            second_max_location = location
            second_max_prob = prob

    total_prob = 0
    for i in max_location_range:
        total_prob += belief.prob(i)
    total_second_prob = 0
    for i in xrange(second_max_location - num_states, second_max_location + num_states + 1):
        total_second_prob += belief.prob(i)

    print max_location, total_prob, total_second_prob
    if total_prob > 0.60 and (total_prob - total_second_prob) > 0.1:
        return (max_location, True)
    else:
        return (max_location, False)

def convert_into_states(num_meters):
    return int(clip(float(num_meters) / (xMax - xMin) * numStates, 0, numStates - 1))

# flag for whether to update the belief based on observations
# turn off to take measurements
DO_ESTIMATION = True

######################################################################
###
###          Brain Methods -- do not change the following code
###
######################################################################

def getParkingSpot(ideal):
    avg = sum(ideal)/float(len(ideal))
    i = len(ideal)-1
    while i>0 and ideal[i]>avg:
        i -= 1
    j = i
    while j>0 and ideal[j]<avg:
        j -= 1
    i = j
    while i>0 and ideal[i]>avg:
        i -= 1
    return (i+1+j)/2

def setup():
    global ideal,confident,parkingSpot,targetTheta,targetX
    ideal = idealReadings.computeIdealReadings(WORLD_FILE, xMin, xMax, robotY, numStates, numObservations)
    parkingSpot = getParkingSpot(ideal)
    targetX = None
    targetTheta = math.pi/2
    confident = False
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
    global confident, targetX, targetTheta
    inp = io.SensorInput()
    sonars = inp.sonars

    # current discretized sonar reading
    left = discretize(sonars[0], sonarMax/numObservations, numObservations-1)
   
    if not confident:
        # GRAPHICS
        if robot.g is not None:
            # update observation model graph
            robot.g.updateObsLabel(left)
            robot.g.updateObsGraph([obsModel(s).prob(left) for s in xrange(numStates)])

        if DO_ESTIMATION:
            # update belief state
            robot.estimator.update(left)

        (location, confident) = confidentLocation(robot.estimator.belief)

        # GRAPHICS
        if robot.g is not None:
            # update belief graph
            robot.g.updateBeliefGraph([robot.estimator.belief.prob(s) for s in xrange(numStates)])
        if confident:
            targetX = (parkingSpot-location)*(xMax-xMin)/float(numStates)+inp.odometry.x
            print 'I am at x =',location,': proceeding to parking space'
        
        # DL6 Angle Controller
        (distanceRight, theta) = sonarDist.getDistanceRightAndAngle(sonars)
        if not theta:
           theta = 0
           print 'Angle too large!'
        e = desiredRight-distanceRight
        ROTATIONAL_VELOCITY = Kp*e - Ka*theta

        io.setForward(FORWARD_VELOCITY)
        io.setRotational(ROTATIONAL_VELOCITY)
    else:
        inp.odometry.theta = util.fixAnglePlusMinusPi(inp.odometry.theta)
        if inp.odometry.x>targetX+.05 and abs(inp.odometry.theta)<math.pi/4:
            io.Action(fvel=-0.2,rvel=0).execute() #drive backwards if necessary
        elif inp.odometry.x<targetX and abs(inp.odometry.theta)<math.pi/4:
            io.Action(fvel=0.2,rvel=0).execute()  #drive to desired x location
        elif inp.odometry.theta<targetTheta-.05:
            io.Action(fvel=0,rvel=0.2).execute()  #rotate
        elif inp.sonars[3]>.3:
            io.Action(fvel=0.2,rvel=0).execute()  #drive into spot
        else:
            io.Action(fvel=0,rvel=0).execute()  #congratulate yourself (or call insurance company)

def brainStop():
    pass

def shutdown():
    pass

if __name__ == '__main__':
    prior = dist.uniformDist(range(200))
    se = StateEstimator(prior,transModel,obsModel)
    se.reset()
    for i in xrange(len(C)):
        ix,s,obs = C[i] #timestep, state, observation
        se.update(obs)
        loc,done = confidentLocation(se.belief)
        if done:
            break
    estimatedState = loc
    realState = s
