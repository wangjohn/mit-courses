from lib601.search import SearchNode,search

class FGWCSearchNode(SearchNode):
    def __init__(self, state, parent):
        SearchNode.__init__(self, state)
        self.parent = parent

    def getChildren(self):
        objectsWithFarmer = self._objectsWithFarmer(self.state)
        potential_states = []
        potential_states.append(self._changeTuple(self.state, [0]))
        for i in objectsWithFarmer:
            potential_states.append(self._changeTuple(self.state, [0, i]))

        return [FGWCSearchNode(state, self) for state in potential_states if self._isLegal(state)]

    def _changeTuple(self, state, states_to_change):
        list_result = []
        for i in xrange(len(state)):
            if i in states_to_change:
                if state[i] == 'R':
                    list_result.append('L')
                else:
                    list_result.append('R')
            else:
                list_result.append(state[i])
        return (list_result[0], list_result[1], list_result[2], list_result[3])

    def _objectsWithFarmer(self, state):
        objects = []
        for i in xrange(len(state)): 
            if state[i] == state[0] and i > 0:
                objects.append(i)
        return objects

    def _isLegal(self, state):
        if (state[1] == state[3] and state[0] != state[1]) or (state[1] == state[2] and state[0] != state[1]):
            return False
        return True

def goalTest(s):
    return s == ('R', 'R', 'R', 'R')

if __name__ == '__main__':
    print 100*(1.05)**(24)
