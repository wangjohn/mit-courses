import math
import lib601.poly as poly
import lib601.sf as sf

def wallFollowerModel(K, T=0.1, V=0.1):
    multipliedResult = K*(T**2)*V
    num1 = poly.Polynomial([multipliedResult, 0, 0])
    den1 = poly.Polynomial([1, -2, 1])
    top = sf.SystemFunctional(num1, den1)
    return sf.FeedbackSubtract(top, sf.SystemFunctional(poly.Polynomial([1]),poly.Polynomial([1])))

if __name__ == '__main__':
    print wallFollowerModel(0.5).dominantPole()
    print wallFollowerModel(1.0).dominantPole()
    print wallFollowerModel(20.0).dominantPole()

    print 2*math.pi / 0.0223
    print 2*math.pi / 0.0316
    print 2*math.pi / 0.141
