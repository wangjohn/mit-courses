import lib601.sf as sf
import lib601.poly as poly
from lib601.plotWindow import PlotWindow
import rl

def makeSF(K):
    num = poly.Polynomial([K, 0])
    den = poly.Polynomial([K, -1, 1])
    return sf.SystemFunctional(num, den)

def viewRootLocus():
    # make an instance of RootLocus and start the viewer with K = 0.01
    rl.RootLocus(makeSF).view(0.01)

def stemplot(response):
    PlotWindow().stem(range(len(response)), response)

def bisection(f, xmin, xmax, threshold=1e-4):
    xmid = float(xmin + xmax) / 2.0
    midslope = (f(xmid + threshold) - f(xmid - threshold)) / (2*threshold)
    if (abs(xmin - xmax) < threshold) or abs(midslope) < threshold:
        return (xmid, f(xmid))

    if midslope < 0:
        return bisection(f, xmid, xmax, threshold)
    elif midslope > 0:
        return bisection(f, xmin, xmid, threshold)

if __name__ == '__main__':
    import math
    ans = bisection(math.cos, math.pi/2, 3*math.pi/2, 1e-6)
    print (3.1415919045757366, -0.9999999999997194), ans
