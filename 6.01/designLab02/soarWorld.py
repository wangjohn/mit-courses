"""
Read in a soar simulated world file and represent its walls as lists
of line segments.
"""

import os
import ast
from datetime import datetime
import lib601.util as util
reload(util)
#from plotWindow import PlotWindow
import dw

class SoarWorld:
    """
    Represents a world in the same way as the soar simulator
    """
    def __init__(self, path):
        """
        @param path: String representing location of world file
        """
        self.walls = []
        """
        Walls represented as list of pairs of endpoints
        """
        self.wallSegs = []
        """
        Walls represented as list of C{util.lineSeg}
        """
        # set the global world
        global world
        world = self
        # execute the file for side effect on world
        execfile(path)
        # put in the boundary walls
        (dx, dy) = self.dimensions
        wall((0,0), (0,dy))
        wall((0,0), (dx,0))
        wall((dx,0), (dx,dy))
        wall((0,dy), (dx,dy))
        
    def initialLoc(self, x, y):
        # Initial robot location
        self.initialRobotLoc = util.Point(x,y)
    def dims(self, dx, dy):
        # x and y dimensions
        self.dimensions = (dx, dy)
    def addWall(self, (xlo, ylo), (xhi, yhi)):
        # walls are defined by two points
        self.walls.append((util.Point(xlo, ylo), util.Point(xhi, yhi)))
        # also store representation as line segments
        self.wallSegs.append(util.LineSeg(util.Point(xlo, ylo),
                                          util.Point(xhi, yhi)))

### Gross stuff that lets the soar world file change the global world
def initialRobotLoc(x,y):
    world.initialLoc(x,y)
def dimensions(x,y):
    world.dims(x,y)
def wall(p1, p2):
    world.addWall(p1, p2)        
### Gross stuff that lets the soar world file change the global world


###
# Function to generate plotWindow plot of soar world
###

def pythonic_from_ast(node):
    if isinstance(node,ast.Str):
        return node.s
    elif isinstance(node,ast.Num):
        return node.n
    elif isinstance(node,ast.List):
        return [pythonic_from_ast(i) for i in node.elts]
    elif isinstance(node,ast.Tuple):
        return tuple(pythonic_from_ast(i) for i in node.elts)
    elif isinstance(node,ast.Dict):
        return {pythonic_from_ast(k):pythonic_from_ast(v) for (k,v) in zip(node.keys,node.values)}
    else:
        raise Exception

def plotSoarWorld(path_to_world,plotWin=None,linestyle='k',title=None):
    if plotWin is None:
        if title is None:
            title = "Soar World Plot: {}, -- {}".format(os.path.basename(path_to_world), datetime.now().strftime("%b %d, '%y; %I:%M:%S %p")) 
        plotWin = PlotWindow(title)
    body = ast.parse(open(path_to_world).read()).body
    walls = []
    offset = (0,0)
    dim = (0,0)
    for elt in body:
        if isinstance(elt, ast.Expr) and isinstance(elt.value, ast.Call):
            #everything we care about falls here (i think)
            if isinstance(elt.value.func, ast.Name):
                args = tuple(pythonic_from_ast(i) for i in elt.value.args)
                if elt.value.func.id == 'initialRobotLoc':
                    offset = args
                elif elt.value.func.id == 'wall':
                    walls.append(args)
                elif elt.value.func.id == 'dimensions':
                    dim = args
    
    xmin = -offset[0]
    xmax = xmin + dim[0]
    ymin = -offset[1]
    ymax = ymin + dim[1]
    plotWin._plot([xmin,xmin], [ymin,ymax], linestyle)
    plotWin.hold(True)
    plotWin._plot([xmax,xmax], [ymin,ymax], linestyle)
    plotWin._plot([xmin,xmax], [ymin,ymin], linestyle)
    plotWin._plot([xmin,xmax], [ymax,ymax], linestyle)
    #now add in walls
    for wall in walls:
        plotWin._plot([i[0]-offset[0] for i in wall], [i[1]-offset[1] for i in wall], linestyle)
    #square output
    plotWin.axis([xmin,xmax,ymin,ymax])
    plotWin.set_aspect('equal')
    return plotWin

def plotSoarWorldDW(path_to_world, plotWin = None, linestyle='k', title = None,
                    windowSize = 600):
    body = ast.parse(open(path_to_world).read()).body
    walls = []
    offset = (0,0)
    dim = (0,0)
    for elt in body:
        if isinstance(elt, ast.Expr) and isinstance(elt.value, ast.Call):
            #everything we care about falls here (i think)
            if isinstance(elt.value.func, ast.Name):
                args = tuple(pythonic_from_ast(i) for i in elt.value.args)
                if elt.value.func.id == 'initialRobotLoc':
                    offset = args
                elif elt.value.func.id == 'wall':
                    walls.append(args)
                elif elt.value.func.id == 'dimensions':
                    dim = args

    # Robot's location needs to be (0, 0)
    # In the world definition, y decreases from the top
    xmin = -offset[0]
    xmax = xmin + dim[0]
    ymin = -offset[1]
    ymax = ymin + dim[1]

    print 'x, y', (xmin, xmax), (ymin,  ymax)
    print 'window size', windowSize, int(windowSize * float(dim[1])/dim[0])
    print 'dim', dim

    if plotWin is None:
        if title is None:
            title = "Soar World Plot: {}, -- {}".\
                    format(os.path.basename(path_to_world),
                           datetime.now().strftime("%b %d, '%y; %I:%M:%S %p")) 
        eps = 0.1 * dim[0]
        plotWin = dw.DrawingWindow(windowSize,
                                    int(windowSize * float(dim[1])/dim[0]),
                                    xmin-eps, xmax+eps, ymin-eps, ymax+eps,
                                    title = title)

    plotWin.drawLineSeg(xmin, ymin, xmin, ymax)
    plotWin.drawLineSeg(xmin, ymax, xmax, ymax)
    plotWin.drawLineSeg(xmax, ymax, xmax, ymin)
    plotWin.drawLineSeg(xmax, ymin, xmin, ymin)
    #now add in walls
    for wall in walls:
        plotWin.drawPath([xmin+i[0] for i in wall],
                         [ymin+i[1] for i in wall], color = 'black')
    return (plotWin, util.Point(offset[0], offset[1]))
