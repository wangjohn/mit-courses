class SM:
    startState = None

    def getStartState(self):
        return self.startState

    def getNextValues(self, state, inp):
        newState = state
        output = inp
        return (newState, output)

    def start(self):
        self.state = self.getStartState()

    def step(self, inp):
        (s, o) = self.getNextValues(self.state, inp)
        self.state = s
        return o

    def transduce(self, inps):
        result = []
        self.start()
        for i in inps:
            result.append(self.step(i))
        return result

######################################################################
#    block diagram components
######################################################################
class R(SM):
    def __init__(self, startState):
        self.startState = startState

    def getNextValues(self, state, inp):
        return (inp, state)

class Gain(SM):
    def __init__(self, K):
        self.startState = K

    def getNextValues(self, state, inp):
        return (state, state * inp)

######################################################################
#    Compositions
######################################################################
class Cascade(SM):
    def __init__(self, m1, m2):
        self.m1 = m1
        self.m2 = m2
        self.startState = (self.m1.getStartState(), self.m2.getStartState())

    def getNextValues(self, state, inp):
        firstState, firstIn = self.m1.getNextValues(state[0], inp)
        secondState, secondIn = self.m2.getNextValues(state[1], firstIn)
        return ((firstState, secondState), secondIn)

class FeedbackAdd(SM):
    def __init__(self, m1, m2):
        self.m1 = m1
        self.m2 = m2

    def getStartState(self):
        # Start state is tuple of start states of the two machines
        return (self.m1.getStartState(), self.m2.getStartState())

    def getNextValues(self, state, inp):
        (s1, s2) = state
        # Find the output of m2 by propagating an arbitrary input through
        # the cascade of m1 and m2
        (ignore, o1) = self.m1.getNextValues(s1, 99999999)
        (ignore, o2) = self.m2.getNextValues(s2, o1)
        # Now get a real new state and output
        (newS1, output) = self.m1.getNextValues(s1, inp+o2)
        (newS2, o2) = self.m2.getNextValues(s2, output)
        return ((newS1, newS2), output)

if __name__ == '__main__':
    print 'a'
