import lib601.plotWindow as plotWindow
from lib601.sm import *


def wallFinderModel(K,start):
    T = 0.1
    m3 = FeedbackAdd(R(start), Gain(1))
    m5 = Cascade(Gain(-K*T), m3)

    m6 = Cascade(R(start), Gain(-1))
    return FeedbackAdd(m5, m6)

# code to plot simulation results
K = -7
plotWindow.PlotWindow().plot(wallFinderModel(K,1.2).transduce(100*[.5]))
