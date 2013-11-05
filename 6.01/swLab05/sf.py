from lib601.poly import *

class SystemFunctional:
    def __init__(self, numerator, denominator):
        self.numerator = numerator
        self.denominator = denominator

    def poles(self):
        reversed_coeffs = list(self.denominator.coeffs)
        reversed_coeffs.reverse()
        poly = Polynomial(reversed_coeffs)
        return poly.roots()

    def poleMagnitudes(self):
        return [abs(r) for r in self.poles()]

    def dominantPole(self):
        max_magnitude = max(self.poleMagnitudes())
        for pole in self.poles():
            if abs(pole) == max_magnitude:
                return pole


######################################################################
##    Primitive SFs
######################################################################

def Gain(k):
    numerator = Polynomial([k,0])
    denominator = Polynomial([1])
    return SystemFunctional(numerator, denominator)

def R():
    numerator = Polynomial([1, 0])
    denominator = Polynomial([1])
    return SystemFunctional(numerator, denominator)


######################################################################
# Combining SFs
######################################################################

def Cascade(sf1, sf2):
    numerator = sf1.numerator * sf2.numerator
    denominator = sf1.denominator * sf2.denominator
    return SystemFunctional(numerator, denominator)

def FeedbackAdd(sf1, sf2):
    numerator = sf1.numerator * sf1.denominator * sf2.denominator
    denominator = sf1.denominator * (sf1.denominator * sf2.denominator - sf1.numerator * sf2.numerator)
    return SystemFunctional(numerator, denominator)

numerator = Polynomial([16, 1, 4])
denominator = Polynomial([4, 0, 1])
print SystemFunctional(numerator, denominator).poles()

