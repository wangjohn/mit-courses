from lib601.plotWindow import PlotWindow
from soar.io import io
reload(io)

gain = 1 

# this function is called when the brain is loaded
def setup():
    pass

# this function is called when the start button is pushed
def brainStart():
    robot.distance = []

# this function is called 10 times per second
def step():
    sonars = io.getSonars()
    robot.distance.append(sonars[3])

    distance = sonars[3]
    if distance != 0.5:
        io.setForward(gain * (distance - 0.5))
    else:
        io.setForward(0)

# called when the stop button is pushed
def brainStop():
    p = PlotWindow()
    p.plot(robot.distance)

# called when brain or world is reloaded (before setup)
def shutdown():
    pass
