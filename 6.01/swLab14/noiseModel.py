import random

def noisify(d,gridSquareSize):
    r = random.random()
    if d != 5:
        if r > .99:
            d = 5
        elif r > .97:
            d = random.uniform(gridSquareSize,d)
    else:
        if r > .98:
            d = random.uniform(gridSquareSize,1.5)
    return d
