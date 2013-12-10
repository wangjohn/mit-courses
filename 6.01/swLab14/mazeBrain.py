import maze
reload(maze)
import search
reload(search)
import lib601.util as util
import lib601.sonarDist as sonarDist
import time
import math
from soar.io import io
import soar.outputs.simulator as sim
import random
import checkoff
reload(checkoff)
import noiseModel
def e(x):
    if len(x) > 117:
        return checkoff.encode(x[:117]) + 'G' + e(x[117:])
    return checkoff.encode(x) 

###### SETUP

NOISE_ON = False

bigFrustrationWorld = [0.2, util.Point(7.0, 1.0), (-0.5, 8.5, -0.5, 8.5)]
frustrationWorld = [0.15, util.Point(3.5, 0.5), (-0.5, 5.5, -0.5, 5.5)]
raceWorld = [0.1, util.Point(2.0, 5.5), (-0.5, 5.5, -0.5, 8.5)]
bigPlanWorld = [0.25, util.Point(3.0, 1.0), (-0.5, 10.5, -0.5, 10.5)]
realRobotWorld = [0.1, util.Point(1.5,0.0), (-2.0, 6.0, -2.0, 6.0)]
robotRaceWorld = [0.1, util.Point(3.0,0.0), (-2.0, 6.0, -2.0, 6.0)]
                                                                 
THE_WORLD = bigFrustrationWorld
(gridSquareSize, goalPoint, (xMin, xMax, yMin, yMax)) = THE_WORLD

###### SOAR CONTROL

# this function is called when the brain is (re)loaded 
def setup():
    #initialize robot's internal map
    width = int((xMax-xMin)/gridSquareSize)
    height = int((yMax-yMin)/gridSquareSize)
    robot.map = maze.DynamicRobotMaze(height,width,xMin,yMin,xMax,yMax)
    robot.map.redrawWorld()
    robot.map.render()
    sim.SONAR_VARIANCE = (lambda mean: 0.001) if NOISE_ON else (lambda mean: 0) #sonars are accurate to about 1 mm
    robot.plan = None

# this function is called when the start button is pushed
def brainStart():
    robot.count = 0
    checkoff.check_start(globals())

minDistancePrimary = 0.6
minDistanceSecondary = 0.45
def tooCloseToWall(primary_readings, secondary_readings):
    for tup in primary_readings:
        if tup[0] < minDistancePrimary:
            return True

    for tup in secondary_readings:
        if tup[0] < minDistanceSecondary:
            return True

# this function is called 10 times per second
def step():
    global inp
    robot.count += 1
    inp = io.SensorInput(cheat=True)
    
    for c in ('orange','cyan','blue','red','gold'):
        robot.map.clearColor(c)

    if robot.map.doHeatMap:
        robot.map.heatMap()
        
    # discretize sonar readings
    # each element in discreteSonars is a tuple (d, cells)
    # d is the distance measured by the sonar
    # cells is a list of grid cells (r,c) between the sonar and the point d meters away
    discreteSonars = []
    for (sonarPose,d) in zip(sonarDist.sonarPoses,inp.sonars):
        if NOISE_ON:
            d = noiseModel.noisify(d,gridSquareSize)
        if d < 1.5:
            discreteSonars.append((d,util.lineIndices(robot.map.pointToIndices(inp.odometry.transformPose(sonarPose)), robot.map.pointToIndices(sonarDist.sonarHit(d, sonarPose, inp.odometry)))))


    # update map
    for (d,cells) in discreteSonars:
        robot.map.sonarHit(cells[-1])

    # if necessary, make new plan
    secondary_sonars = discreteSonars[:3] + discreteSonars[5:]
    if robot.plan is None or tooCloseToWall(discreteSonars[3:5], secondary_sonars):
        print 'REPLANNING'
        robot.plan = search.ucSearch(search.MazeSearchNode(robot.map,
                              robot.map.pointToIndices(inp.odometry.point()),None,0), 
                              lambda x: x == robot.map.pointToIndices(goalPoint), 
                              lambda x: 0)

    # graphics (draw robot's plan, robot's location, goalPoint)
    # do not change this block
    if robot.map.showPassable:
        robot.map.markNotPassable()
    if robot.plan is not None:
        robot.map.markCells(robot.plan,'blue')
    robot.map.markCell(robot.map.pointToIndices(inp.odometry.point()),'gold')
    robot.map.markCell(robot.map.pointToIndices(goalPoint),'green')

    # move to target point (similar to driving task in DL2)
    currentPoint = inp.odometry.point()
    currentAngle = inp.odometry.theta
    destinationPoint = robot.map.indicesToPoint(robot.plan[0])
    while currentPoint.isNear(destinationPoint,0.1) and len(robot.plan)>1:
        robot.plan.pop(0)
        destinationPoint = robot.map.indicesToPoint(robot.plan[0])

    if not currentPoint.isNear(destinationPoint,0.1):
        angle = util.fixAnglePlusMinusPi(currentPoint.angleTo(destinationPoint)-currentAngle)
        if abs(angle)<0.1:
            #if close enough to pointing, use proportional control on forward velocity
            fv = 2*currentPoint.distance(destinationPoint)
            rv = 0
        else:
            #otherwise, use proportional control on angular velocity
            fv = 0
            rv = 2*angle
    else:
        raise Exception,'Goal Reached!\n\n%s' % checkoff.generate_code(globals())
            
    robot.map.render()
    io.Action(fvel=fv,rvel=rv).execute()

# called when the stop button is pushed
def brainStop():
    stopTime = time.time()
    print 'Total steps:', robot.count
    print 'Elapsed time in seconds:', stopTime - robot.startTime
