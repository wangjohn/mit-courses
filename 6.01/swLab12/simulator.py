"""
6.01 S13 Software Lab 12.
"""

__author__ = 'Michael Mekonnen <mikemeko@mit.edu> and Adam Hartz <hartz@mit.edu>'

from Tkinter import Canvas
from Tkinter import Entry
from Tkinter import Label
from Tkinter import LEFT
from Tkinter import RIGHT
from Tkinter import StringVar
from Tkinter import Tk
from Tkinter import Frame
from Tkinter import Button

class Simulator(Tk):
    """
    Simulator for the estimation process in SL12.
    """

    def __init__(self, sm, se, ideal):
        Tk.__init__(self)
        self.title('SL12 State Estimation Simulator')
        self._ugly_hidden_init(sm,se,ideal)

    def _ugly_hidden_init(self, hmm, se, ideal):
        self.hmm = hmm
        self.hmm.initialize()
        self.se = se
        self.se.reset()
        self.ideal = ideal
        self.numStates = len(ideal)
        self._CELL_SIZE = 50
        self._MARGIN = 5
        self._CELL_WIDTH = self._CELL_SIZE + 2 * self._MARGIN
        self._setupUI()

    def _setupUI(self):
        """
        Setup UI.
        """
        self.resizable(width=False, height=False)
       
        #world drawing
        self.world = [Canvas(self, width=self._CELL_SIZE, height=self._CELL_SIZE) for i in xrange(self.numStates)]
        self.worldLabel = Label(self, text='World:')
        self.worldLabel.grid(row=1, column=0)
        for ix in xrange(len(self.world)):
            self.world[ix].grid(row=1, column=ix+2)
      
        #ideal readings labels
        self.idealVars = [StringVar() for i in self.ideal]
        self.idealMarks = [Label(self, textvariable=i) for i in self.idealVars]
        self.idealLabel = Label(self, text='Ideal Readings:')
        self.idealLabel.grid(row=3, column=0)
        for ix in xrange(len(self.idealMarks)):
            self.idealMarks[ix].grid(row=3, column=ix+2)

        #obs model
        self.obsgraph = [Canvas(self, width=self._CELL_SIZE, height=self._CELL_SIZE) for i in xrange(self.numStates)]
        self.obsVar = StringVar()
        self.obsLabel = Label(self, textvariable=self.obsVar)
        self.obsLabel.grid(row=5, column=0)
        for ix in xrange(len(self.obsgraph)):
            self.obsgraph[ix].grid(row=5, column=ix+2)
        self.obsVars = [StringVar() for i in self.obsgraph]
        self.obsMarks = [Label(self, textvariable=i) for i in self.obsVars]
        for ix in xrange(len(self.obsMarks)):
            self.obsMarks[ix].grid(row=6, column=ix+2)

        #prior belief
        self.priorgraph = [Canvas(self, width=self._CELL_SIZE, height=self._CELL_SIZE) for i in xrange(self.numStates)]
        self.priorLabel = Label(self, text='Prior: ')
        self.priorLabel.grid(row=8, column=0)
        for ix in xrange(len(self.priorgraph)):
            self.priorgraph[ix].grid(row=8, column=ix+2)
        self.priorVars = [StringVar() for i in self.priorgraph]
        self.priorMarks = [Label(self, textvariable=i) for i in self.priorVars]
        for ix in xrange(len(self.priorMarks)):
            self.priorMarks[ix].grid(row=9, column=ix+2)
       
        #after transition update
        self.aftertransgraph = [Canvas(self, width=self._CELL_SIZE, height=self._CELL_SIZE) for i in xrange(self.numStates)]
        self.aftertransVar = StringVar()
        self.aftertransLabel = Label(self, textvariable=self.aftertransVar)
        self.aftertransLabel.grid(row=14, column=0)
        for ix in xrange(len(self.aftertransgraph)):
            self.aftertransgraph[ix].grid(row=14, column=ix+2)
        self.aftertransVars = [StringVar() for i in self.aftertransgraph]
        self.aftertransMarks = [Label(self, textvariable=i) for i in self.aftertransVars]
        for ix in xrange(len(self.aftertransMarks)):
            self.aftertransMarks[ix].grid(row=15, column=ix+2)
        
        #after observation update
        self.posteriorgraph = [Canvas(self, width=self._CELL_SIZE, height=self._CELL_SIZE) for i in xrange(self.numStates)]
        self.posteriorVar = StringVar()
        self.posteriorLabel = Label(self, textvariable=self.posteriorVar)
        self.posteriorLabel.grid(row=11, column=0)
        for ix in xrange(len(self.posteriorgraph)):
            self.posteriorgraph[ix].grid(row=11, column=ix+2)
        self.posteriorVars = [StringVar() for i in self.posteriorgraph]
        self.posteriorMarks = [Label(self, textvariable=i) for i in self.posteriorVars]
        for ix in xrange(len(self.posteriorMarks)):
            self.posteriorMarks[ix].grid(row=12, column=ix+2)

        Label(self, text='Actions: ').grid(row=17,column=0)
        Button(self,text='Transition',command=self._step).grid(row=17,column=2,columnspan=2)
        Button(self,text='Reset',command=self._reset).grid(row=17,column=4,columnspan=2)

        self.observation = StringVar()
        self.obsLabel = Label(self, textvariable=self.observation, height=1)
        self.obsLabel.grid(row=4,column=0)
        self._drawWorld()

    def _step(self):
        """
        Step the state machine and state estimator based on the given action.
        """
        
        obs = self.hmm.makeObservation()
        self.hmm.transition()
        self._drawWorld()
        self.observation.set('Observed %d' % obs)

        self._drawGraph(self.obsgraph,self.obsVars,[self.se.obsModel(i).prob(obs) for i in xrange(self.numStates)])
        self.obsVar.set('P(O=%d|S)' % obs)

        self._drawGraph(self.priorgraph,self.priorVars,[self.se.belief.prob(i) for i in xrange(self.numStates)])
        
        self.se.observe(obs)
        self._drawGraph(self.posteriorgraph,self.posteriorVars,[self.se.belief.prob(i) for i in xrange(self.numStates)])
        self.posteriorVar.set('After Observing %d:' % obs)

        self.se.transition()
        self._drawGraph(self.aftertransgraph,self.aftertransVars,[self.se.belief.prob(i) for i in xrange(self.numStates)])
        self.aftertransVar.set('After Transition:')



    def _drawGraph(self,graphvar,labelvar,values):
        '''
        Make our rudimentary bar graph
        '''
        for ((box,label),val) in zip(zip(graphvar,labelvar),values):
            box.create_rectangle(0,
                                 0,
                                 self._CELL_SIZE,
                                 self._CELL_SIZE, fill='white', outline='white') #clear
            box.create_rectangle(0,
                                 (1-val)*self._CELL_SIZE,
                                 self._CELL_SIZE,
                                 self._CELL_SIZE, fill='blue', outline='blue')
            label.set('%.04f' % val)
        

    def _drawWorld(self):
        for i in xrange(len(self.world)):
            self.world[i].create_rectangle(0,
                                 0,
                                 self._CELL_SIZE,
                                 self._CELL_SIZE, fill='white', outline='white') #clear
            if i == self.hmm.state:
                so3 = int(self._CELL_SIZE/3.)
                self.world[i].create_oval(so3,so3,2*so3,2*so3,fill='red')
            
            self.idealVars[i].set('%d' % self.ideal[i])

    def _reset(self):
        self.update_idletasks()
        self._ugly_hidden_init(self.hmm,self.se,self.ideal)
        self.update_idletasks()
        for i in (self.priorVars, self.obsVars, self.aftertransVars, self.posteriorVars):
            for j in i:
                j.set('          ')
        self.update()

    def simulate(self):
        """
        Start simulation.
        """
        self.mainloop()
