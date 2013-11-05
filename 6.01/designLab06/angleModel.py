import lib601.poly as poly
import lib601.sf as sf
from lib601.optimize import bisection

def angleModel(Kp, Ka):
    T = 0.1
    V = 0.1
    plant1 = sf.SystemFunctional(poly.Polynomial([T, 0]), poly.Polynomial([-1, 1]))
    smallFeedbackNum = sf.Cascade(plant1, sf.Gain(Ka))
    smallFeedbackDen = sf.Gain(1)
    smallFeedback = sf.FeedbackSubtract(smallFeedbackNum, smallFeedbackDen)

    firstCascade = sf.Cascade(sf.Gain(float(Kp) / Ka), smallFeedback)
    plant2 = sf.SystemFunctional(poly.Polynomial([T*V, 0]), poly.Polynomial([-1,1]))
    secondCascade = sf.Cascade(firstCascade, plant2)

    return sf.FeedbackSubtract(secondCascade, sf.Gain(1))

# Given Kp, return the value of Ka for which the system converges most
# quickly, within the range KaMin, KaMax.

def bestKa(Kp, KaMin, KaMax):
    function = lambda ka : abs(angleModel(Kp, ka).dominantPole())

    goodKa = bisection(function, KaMin, KaMax)
    return (goodKa[0], angleModel(Kp, goodKa[0]).dominantPole())

if __name__ == '__main__':
    for kp in [1, 3, 10, 30, 100, 300]:
        print kp, bestKa(kp, -100.0, 100.0)
