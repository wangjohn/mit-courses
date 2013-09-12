import math
import lib601.util as util
import lib601.soarWorld as soarWorld
import lib601.search as search
from soar.io import io
from mazeAnswers import *

import tk
import soarWorld
tk.setInited()

worldname = 'dl2World'
#worldname = 'bigEmptyWorld'

PATH_TO_WORLD = '%s.py' % worldname
world = [i.strip() for i in open('%s.txt' % worldname).readlines()]

bounds = {'dl2World': (0.0,0.0,10.8,10.8),
          'bigEmptyWorld': (0.0,0.0,4.05,4.05)}

def getPath(worldname, world):
    if worldname == 'dl2World':
        return search.search(MazeSearchNode(world, world.start, None), lambda state: state==world.goal)
    else:
        return [(15,4), (17,8), (13,12), (11,8), (9,4), (5,8), (7,12)]
        

class RobotMaze(Maze):
    def __init__(self, mapText, x0, y0, x1, y1):
        Maze.__init__(self, mapText)
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

    def pointToIndices(self, point):
        ix = int(math.floor((point.x-self.x0)*self.width/(self.x1-self.x0)))
        iix = min(max(0,ix),self.width-1)
        iy = int(math.floor((point.y-self.y0)*self.height/(self.y1-self.y0)))
        iiy = min(max(0,iy),self.height-1)
        return ((self.height-1-iiy,iix))

    def indicesToPoint(self, (r,c)):
        x_index = (float(c)/(self.width)) * (self.x1 - self.x0) + self.x0
        y_index = (float(self.height - r - 1)/(self.height)) * (self.y1 - self.y0) + self.y0
        x = x_index + self.cellWidth() / 2.0
        y = y_index + self.cellHeight() / 2.0
        return util.Point(x, y)

    def cellWidth(self):
        return (self.x1 - self.x0) / (self.width)

    def cellHeight(self):
        return (self.y1 - self.y0) / (self.height)

    def isPassable(self, (r,c)):
        if not Maze.isPassable(self, (r,c)):
            return False

# this function is called when the brain is loaded
def setup():
    robot.maze = RobotMaze(world, *(bounds[worldname]))
    robot.path = getPath(worldname, robot.maze)
    (robot.window, robot.initialLocation) = \
                   soarWorld.plotSoarWorldDW(PATH_TO_WORLD)
    if robot.path:
        robot.window.drawPath([robot.maze.indicesToPoint(i).x - \
                               robot.initialLocation.x \
                               for i in robot.path],
                              [robot.maze.indicesToPoint(i).y - \
                               robot.initialLocation.y \
                               for i in robot.path], color = 'purple')
    else:
        print 'no plan from', robot.maze.start, 'to', robot.maze.goal
    robot.slimeX = []
    robot.slimeY = []

# this function is called when the start button is pushed
def brainStart():
    pass

def closeToPoint(current, destination, eps):
    return util.within(current.x, destination.x, eps) and util.within(current.y, destination.y, eps)

# this function is called 10 times per second
def step():
    if len(robot.path) == 0:
        io.setForward(0)
        io.setRotational(0)
        return

    x, y, theta = io.getPosition()
    robot.slimeX.append(x)
    robot.slimeY.append(y)

    currentPoint = util.Point(x,y).add(robot.initialLocation)
    currentAngle = theta
    destinationPoint = robot.maze.indicesToPoint(robot.path[0])
    print robot.maze.cellHeight(), robot.maze.cellWidth()
    print robot.maze.isPassable(robot.path[0])

    desiredTheta = math.atan2(float(destinationPoint.y - currentPoint.y), float(destinationPoint.x - currentPoint.x))
    if desiredTheta < 0:
        desiredTheta += math.pi * 2

    if util.nearAngle(desiredTheta, theta, 0.1):
        io.setForward(0.3)
        io.setRotational(0)
    else:
        io.setRotational(1.0)
        io.setForward(0)

    if closeToPoint(currentPoint, destinationPoint, 0.4):
        if len(robot.path) > 0:
            robot.path.pop(0)

# called when the stop button is pushed
def brainStop():
    for i in range(len(robot.slimeX)):
        robot.window.drawPoint(robot.slimeX[i], robot.slimeY[i], 'red')

# called when brain or world is reloaded (before setup)
def shutdown():
    pass

if __name__ == '__main__':
    m = RobotMaze(world,2.,2.,12.,12.)
    ans = m.indicesToPoint((3,5))
    print m.pointToIndices(ans)
