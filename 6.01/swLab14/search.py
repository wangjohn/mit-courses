class SearchNode:
    def __init__(self,state,parent,cost):
        self.state = state
        self.parent = parent
        self.cost = cost

    def getChildren(self):
        return []

    def getPath(self):
        out = []
        current = self
        while current is not None:
            out.append(current.state)
            current = current.parent
        return out[::-1]

class MazeSearchNode(SearchNode):
    def __init__(self,maze,state,parent,cost):
        self.maze = maze
        SearchNode.__init__(self,state,parent,cost)

    def getChildren(self):
        r,c = self.state
        out = []
        for (dr,dc) in [(1,0),(0,1),(-1,0),(0,-1)]:
            nr,nc = r+dr,c+dc
            if self.maze.isPassable((nr,nc)):
                out.append(MazeSearchNode(self.maze,(nr,nc),self,self.cost+1.0))
        for (dr,dc) in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            if all(self.maze.isPassable(i) for i in [(r+dr,c),(r,c+dc),(r+dr,c+dc)]):
                out.append(MazeSearchNode(self.maze,(r+dr,c+dc),self,self.cost+2**0.5))
        return out

def ucSearch(startNode, goalTest, heuristic=lambda s: 0):
    if goalTest(startNode.state):
        return startNode.getPath()
    agenda = [(startNode,startNode.cost+heuristic(startNode.state))]
    expanded = set()
    while len(agenda) > 0:
        agenda.sort(key=lambda n: n[1])
        node,priority = agenda.pop(0)
        if node.state not in expanded:
            expanded.add(node.state)
            if len(expanded)%1000==0: print "Expanded",len(expanded),"states"
            if goalTest(node.state):
                print "Expanded",len(expanded),"states"
                return node.getPath()
            for child in node.getChildren():
                if child.state not in expanded:
                    agenda.append((child,child.cost+heuristic(child.state)))
    print "Expanded",len(expanded),"states"
    return None
