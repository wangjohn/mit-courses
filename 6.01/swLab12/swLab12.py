import lib601.dist as dist
from lib601.markov import HMM, StateEstimator
from simulator import Simulator

#ideal = [1,8,8,1,1,8,1,8,8]
ideal = [1,8,8,1,1]
numStates = len(ideal)

## OBSERVATION MODELS

def perfectObsModel(state):
    return dist.deltaDist(ideal[state])

def obsModelA(state):
    zero_dist = dist.uniformDist([0])
    return dist.mixture(dist.deltaDist(ideal[state]), zero_dist, 0.7)

def obsModelB(state):
    random_dist = dist.squareDist(0, 10)
    return dist.mixture(dist.deltaDist(ideal[state]), random_dist, 0.7)

def obsModelC(state):
    return dist.deltaDist(9 - ideal[state])

def obsModelD(state):
    ideal_d = dist.deltaDist(ideal[state])
    other_d = dist.deltaDist(9 - ideal[state])
    return dist.mixture(ideal_d, other_d, 0.5)

## TRANSITION MODELS

def moveRightModel(state):
    return dist.deltaDist(min(state+1, numStates-1))

def teleportModel(state):
    right_d = dist.deltaDist(min(state+1, numStates-1))
    random_d = dist.uniformDist(range(numStates))
    return dist.mixture(right_d, random_d, 0.7)

def resetModel(state):
    right_d = dist.deltaDist(min(state+1, numStates-1))
    zero_d = dist.deltaDist(0)
    return dist.mixture(right_d, zero_d, 0.7)

def teleportModel2(state):
    current_d = dist.deltaDist(state)
    random_d = dist.uniformDist(range(numStates))
    return dist.mixture(current_d, random_d, 0.7)

def resetModel2(state):
    current_d = dist.deltaDist(state)
    zero_d = dist.deltaDist(0)
    return dist.mixture(current_d, zero_d, 0.7)

## STARTING DISTRIBUTIONS

uniformPrior = dist.uniformDist(range(len(ideal)))
alwaysLeftPrior = dist.DDist({0:1.0})

## SIMULATION CODE

def simulate(transDist, obsDist):
    testSE = StateEstimator(uniformPrior, transDist, obsDist)
    testHMM = HMM(alwaysLeftPrior, transDist, obsDist)
    Simulator(testHMM, testSE, ideal).simulate()

simulate(moveRightModel, obsModelB)
