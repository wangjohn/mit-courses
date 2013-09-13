import lib601.gfx as gfx
from soar.io import io

UPPER_BOUND = 0.4
LOWER_BOUND = 0.2
WALL_DISTANCE = 0.3
BUFFER = 0.1
FORWARD_ROLL_VELOCITY = 0.1
BACKWARD_ROLL_VELOCITY = -0.1
# this function is called when the brain is (re)loaded
def setup():
    pass

# this function is called when the start button is pushed
def brainStart():
    pass

# this function is called 10 times per second
def step():
    #io.sonarMonitor(True)

    #read in the sonar readings from the robot.
    #s will be a list of 8 values, with the value at index
    #0 representing the left-most sonar
    sonars = io.getSonars()
    #boundary_finder(sonars)
    boundary_follower(sonars)
    
def turn_right(distance):
    io.setRotational(-0.1* distance)

def turn_left(distance):
    io.setRotational(0.1*distance)

def boundary_follower(sonars):
    if sonars[7] > UPPER_BOUND:
        turn_right(sonars[7]- UPPER_BOUND)
    elif sonars[7] < LOWER_BOUND:
        turn_left(-sonars[7]+ LOWER_BOUND)
    else:
        io.setRotational(0)

    forward_boundary(sonars)

def forward_boundary(sonars):
    turned_left = False
    for i in xrange(len(sonars)):
        if sonars[i] < WALL_DISTANCE and i >= 3:
            turn_left(0.7)
            io.setForward(0)
            turned_left = True
            
    if not turned_left:
        io.setForward(FORWARD_ROLL_VELOCITY)

def boundary_finder(sonars):
    if sonars[3] > WALL_DISTANCE + BUFFER:
        print 'setting forward velocity'
        io.setForward(FORWARD_ROLL_VELOCITY)
    elif sonars[3] < WALL_DISTANCE - BUFFER:
        print 'setting other velocity'
        io.setForward(BACKWARD_ROLL_VELOCITY)
    else:
        io.setForward(0)
    print sonars[3]   

# called when the stop button is pushed
def brainStop():
    pass

# called when brain or world is reloaded (before setup)
def shutdown():
    pass
