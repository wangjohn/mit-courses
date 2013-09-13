# Mazes
from lib601.search import search

# set up lists of strings to represent the four test mazes
smallMazeText = [line.strip() for line in open('smallMaze.txt').readlines()]
mediumMazeText = [line.strip() for line in open('mediumMaze.txt').readlines()]
largeMazeText = [line.strip() for line in open('largeMaze.txt').readlines()]
hugeMazeText = [line.strip() for line in open('hugeMaze.txt').readlines()]

class Maze:
    def __init__(self, mazeText):
        self.mazeText = mazeText
        self.height = len(mazeText)
        self.width = len(mazeText[0])
        self.start = self._findLetter("S")
        self.goal = self._findLetter("G")

    def isPassable(self, (r,c)):
        if c < 0 or c >= self.width or r < 0 or r >= self.height:
            return False
        return self.mazeText[r][c] != "#"

    def _findLetter(self, letter):
        for row in xrange(len(self.mazeText)):
            for col in xrange(len(self.mazeText)):
                if self.mazeText[row][col] == letter:
                    return (row, col)


class MazeSearchNode:
    def __init__(self, maze, currentCell, parentNode):
        self.maze = maze
        self.state = currentCell
        self.parent = parentNode

    def getChildren(self):
        row, col = self.state
        children = []
        for i in xrange(-1,2,1):
            for j in xrange(-1,2,1):
                if (i != 0 and j == 0) or (i == 0 and j != 0):
                    tup = (row+i, col+j)
                    if self._isNode(tup) and not self._isBacktracking(tup):
                        children.append(MazeSearchNode(self.maze, tup, self))
        return children

    def _isNode(self, tup):
        return self.maze.isPassable(tup)

    def _isBacktracking(self, tup):
        return self.parent != None and self.parent.state == tup

    def getPath(self):
        path = []
        node = self
        while node.parent != None:
            path.append(node.state)
            node = node.parent

        return path

def reachedGoal(state, goal):
    return state == goal

if __name__ == '__main__':
    m = Maze(largeMazeText)
    f = lambda state: reachedGoal(state, m.goal)
    result = search(MazeSearchNode(m, m.start, None), f)
    print result
    print len(result) + 1
