import Tkinter
import math
import lib601.util as util

# You should ignore this class; its sole purpose is graphical.
# The class you should modify is DynamicRobotMaze, near the end of this file.
class GraphicsMaze:
    def color_from_prob(self, p):
        v = int((1-p)*255.99)
        return "#%02x%02x%02x" % (v,v,v)

    def __init__(self,height,width):
        self.height = height
        self.width = width
        self.window = Tkinter.Toplevel()
        self.window.title('Dynamic Map')
        self.cell_size=5
        self.canvas = Tkinter.Canvas(self.window, width=(self.cell_size+1)*width, height=(self.cell_size+1)*height)
        self.canvas.pack()
        self.drawnCells = {}
        self.to_color = {}
        for r in xrange(self.height):
            for c in xrange(self.width):
                loc = (r,c)
                x0 = loc[1]*(self.cell_size+1)-1
                x1 = x0+self.cell_size
                y0 = loc[0]*(self.cell_size+1)-1
                y1 = y0 + self.cell_size
                self.drawnCells[loc] = self.canvas.create_rectangle(x0,y0,x1,y1,fill='white',outline='white')
                self.to_color[loc] = 'white'
        self.by_color = {}
        self.showSet = False
        self.showClear = False
        self.showPassable = False
        self.doHeatMap = False
        self.setVar = Tkinter.IntVar()
        self.clearVar = Tkinter.IntVar()
        self.passVar = Tkinter.IntVar()
        self.heatVar = Tkinter.IntVar()
        self.setButton = Tkinter.Checkbutton(self.window, text='Show sonarHit', variable=self.setVar, command=self.doSetClear)
        self.clearButton = Tkinter.Checkbutton(self.window, text='Show sonarPass', variable=self.clearVar, command=self.doSetClear)
        self.heatMapButton = Tkinter.Checkbutton(self.window, text='Show Probabilities', variable=self.heatVar, command=self.doSetClear)
        self.passButton = Tkinter.Checkbutton(self.window, text='Show Passable', variable=self.passVar, command=self.doSetClear)
        self.setButton.pack()
        self.clearButton.pack()
        self.heatMapButton.pack()
        self.passButton.pack()
        self.dirty = {}

    def doSetClear(self):
        self.showSet = bool(self.setVar.get())
        self.showClear = bool(self.clearVar.get())
        self.showPassable = bool(self.passVar.get())
        self.doHeatMap = bool(self.heatVar.get())
        if not self.doHeatMap:
            self.redrawWorld()

    def render(self):
        for (loc,color) in self.dirty.iteritems():
            self.blitCell(loc,color)
        self.dirty = {}

    def markCell(self,cell,color):
        if self.to_color[cell] != color:
            self.dirty[cell] = color
            self.to_color[cell] = color

    def markCells(self,cells,color):
        for cell in cells:
            self.markCell(cell,color)

    def heatMap(self):
        for r in xrange(self.height):
            for c in xrange(self.width):
                self.markCell((r,c),self.color_from_prob(self.probOccupied((r,c))))
                
    def markNotPassable(self):
        for r in xrange(self.height):
            for c in xrange(self.width):
                if not self.isPassable((r,c)) and self.isClear((r,c)):
                    self.markCell((r,c),'red')

    def blitCell(self,loc,color):
        self.canvas.itemconfigure(self.drawnCells[loc], fill=color, outline=color)
        self.by_color[color] = self.by_color.get(color,set())
        self.by_color[color].add(loc)
       
    def sonarHitGraphics(self,(r,c)):
        if self.showSet:
            self.markCell((r,c),'orange')
        else:
            self.clearCell((r,c))
    
    def sonarPassGraphics(self,(r,c)):
        if self.showSet:
            self.markCell((r,c),'cyan')
        else:
            self.clearCell((r,c))

    def clearCell(self,loc):
        if self.doHeatMap:
            self.markCell(loc,self.color_from_prob(self.probOccupied(loc)))
        else:
            if self.isClear(loc):
                self.markCell(loc,'white')
            else:
                self.markCell(loc,'black')
 
    def clearColor(self,color):
        for loc in self.by_color.get(color,[]):
            self.clearCell(loc)
        self.by_color[color] = set()

    def redrawWorld(self):
        for r in xrange(self.height):
            for c in xrange(self.width):
                if self.isClear((r,c)): #abstract method, provided by subclasses
                    self.markCell((r,c),'white')
                else:
                    self.markCell((r,c),'black')

def getMarkovModel():

    prior = 
    transition = 
    observation = 
    markov.StateEstimator(prior, transition, observation)

def observationFunction(d, prob = 0.1):
    if d < 1.5:
        return dist.mixture(dist.uniformDist([5]), dist.triangleDist(d, 0.009, 0, 5), prob)
    else:
        return dist.mixture(dist.uniformDist([5]), dist.squareDist(0, 1.5), 1.0 - prob)

def transitionFunction(d):


class DynamicRobotMaze(GraphicsMaze):
    def __init__(self, height, width, x0, y0, x1, y1):
        GraphicsMaze.__init__(self, height, width) #do not remove
        self.x0,self.x1 = x0,x1
        self.y0,self.y1 = y0,y1
        self.width, self.height = width, height
        self.grid = [[True for c in xrange(width)] for r in xrange(height)]

    def pointToIndices(self, point):
        ix = int(math.floor((point.x-self.x0)*self.width/(self.x1-self.x0)))
        iix = min(max(0,ix),self.width-1)
        iy = int(math.floor((point.y-self.y0)*self.height/(self.y1-self.y0)))
        iiy = min(max(0,iy),self.height-1)
        return ((self.height-1-iiy,iix))

    def indicesToPoint(self, (r,c)):
        x = self.x0 + (c+0.5)*(self.x1-self.x0)/self.width
        y = self.y0 + (self.height-r-0.5)*(self.y1-self.y0)/self.height
        return util.Point(x,y)

    def isClear(self,(r,c)):
        if not (0 <= r < self.height and 0 <= c < self.width):
            return False
        return self.grid[r][c]

    def isPassable(self,(r,c)):
        paddingWidth = int(.5 / (float(self.width) / (self.x1 - self.x0))) + 2
        paddingHeight = int(.5 / (float(self.height) / (self.y1 - self.y0))) + 2

        for i in xrange(r - paddingWidth, r + paddingWidth + 1):
            for j in xrange(c - paddingHeight, c + paddingHeight + 1):
                if not self.isClear((i,j)):
                    return False

        return True

    def probOccupied(self,(r,c)):

        return float(not self.grid[r][c])

    def sonarHit(self,(r,c)):
        self.grid[r][c] = False
        #don't remove graphics command below
        self.sonarHitGraphics((r,c))
    
    def sonarPass(self,(r,c)):
        self.grid[r][c] = True
        #don't remove graphics command below
        self.sonarPassGraphics((r,c))
