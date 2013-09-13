class SearchNode:
    def __init__(self,state,parent):
        self.state = state
        self.parent = parent

    def getPath(self):
        path = [self.state]
        node = self
        while node.parent:
            path.append(node.parent.state)
            node = node.parent

        path.reverse()
        return path

class KnightSearchNode(SearchNode):
    moves = [(1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]

    def __init__(self, boardX, boardY,state,parent=None):
        self.boardX = boardX
        self.boardY = boardY
        SearchNode.__init__(self,state,parent)

    def getChildren(self):
        out = []
        x,y = self.state
        for dx,dy in self.moves:
            nx,ny = x+dx,y+dy
            if (-1<nx<self.boardX) and (-1<ny<self.boardY):
                out.append(KnightSearchNode(self.boardX,self.boardY,(nx,ny),self))
        return out

def search(startNode, goalTest, dfs=False):
    paths = [[startNode]]
    visited_nodes = {}
    while len(paths) > 0:
        current_path = paths.pop(0)
        node = current_path[-1]
        children = node.getChildren()
        for child in children:
            if child.state not in visited_nodes:
                new_path = list(current_path)
                new_path.append(child)
                if goalTest(child.state):
                    return [n.state for n in new_path]
                else:
                    visited_nodes[child.state] = True
                    if dfs:
                        paths.insert(0, new_path)
                    else:
                        paths.append(new_path)
    return None

class WordLadderSearchNode(SearchNode):
    def __init__(self, state, parent):
        SearchNode.__init__(self, state, parent)

    def getChildren(self):
        children = []
        for i in xrange(len(self.state)):
            for letter in self._getLetters():
                new_word = self.state[:i] + letter + self.state[i+1:]
                if is_valid_word(new_word):
                    children.append(WordLadderSearchNode(new_word, self.state))
        return children

    def _getLetters(self):
        return [chr(i) for i in xrange(97,123,1)]

if __name__ == '__main__':
    k = KnightSearchNode(8,8,(0,0),None)
    result = search(k,lambda s: s==(7,7),dfs=True)
    ans = valid_path(result)
    print ans
