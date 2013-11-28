class DDist:
    def __init__(self, dictionary):
        if not (abs(sum(dictionary.values())-1) < 1e-6 and min(dictionary.values()) >= 0.0):
            raise Exception, "Probabilities must be nonnegative, and must sum to 1"
        self.d = dictionary

    def prob(self, elt):
        if elt in self.d:
            return self.d[elt]
        else:
            return 0.0

    def support(self):
        return [item for item, prob in self.d.iteritems() if prob > 0]

    def __repr__(self):
        return "DDist(%r)" % self.d

    __str__ = __repr__

    def project(self, mapFunc):
        dictionary = {}
        for a in self.support():
            aprime = mapFunc(a)
            if aprime in dictionary:
                dictionary[aprime] += self.prob(a)
            else:
                dictionary[aprime] = self.prob(a)
        return DDist(dictionary)

    def condition(self, testFunc):
        valid_supports = []
        total_sum = 0

        for element in self.support():
            if testFunc(element):
                total_sum += self.prob(element)
                valid_supports.append(element)

        dictionary = {}
        for element in valid_supports:
            dictionary[element] = float(self.prob(element)) / total_sum
        return DDist(dictionary)

    def bayesianUpdate(self, PBgA, b):
        ab = makeJointDistribution(self, PBgA)
        result = ab.condition(lambda x: x[1] == b)
        dictionary = {}
        for tup in result.support():
            dictionary[tup[0]] = result.prob(tup)
        return DDist(dictionary)

        bprob = 0
        for a in self.support():
            bprob += PBgA(a).prob(b)

        dictionary = {}
        for a in self.support():
            dictionary[a] = float(PBgA(a).prob(b)) * self.prob(a) / bprob
        return DDist(dictionary)

def m(x):
    return x[0]

def makeJointDistribution(PA, PBgA):
    dictionary = {}
    for a_element in PA.support():
        a_prob = PA.prob(a_element)
        pbga_dist = PBgA(a_element)
        for b_element in pbga_dist.support():
            b_prob = pbga_dist.prob(b_element)

            ab_element = (a_element, b_element)
            ab_prob = float(b_prob) * a_prob
            dictionary[ab_element] = ab_prob

    return DDist(dictionary)

def totalProbability(PA, PBgA):
    dictionary = {}
    for a in PA.support():
        for b in PBgA(a).support():
            prob = PBgA(a).prob(b) * PA.prob(a)

            if b in dictionary:
                dictionary[b] += prob
            else:
                dictionary[b] = prob
    return DDist(dictionary)

if __name__ == '__main__':
    CarAndSelectAndHost = DDist({(2, 1, 3): 0.1111111111111111, (1, 2, 3): 0.1111111111111111, (1, 3, 2): 0.1111111111111111, (3, 2, 1): 0.1111111111111111, (1, 1, 3): 0.05555555555555555, (3, 3, 2): 0.05555555555555555, (3, 1, 2): 0.1111111111111111, (2, 2, 1): 0.05555555555555555, (3, 3, 1): 0.05555555555555555, (2, 2, 3): 0.05555555555555555, (1, 1, 2): 0.05555555555555555, (2, 3, 1): 0.1111111111111111})
    pH3GivenS1 = CarAndSelectAndHost.condition(lambda x: x[1] == 1).project(lambda x: x[2]).prob(3)
    print CarAndSelectAndHost.condition(lambda x: x[2] == 3 and x[1] == 1)
    pC2GivenH3S1 = CarAndSelectAndHost.condition(lambda x: x[2] == 3 and x[1] == 1).prob((2, 1, 3))
    pC1GivenH3S1 = CarAndSelectAndHost.condition(lambda x: x[2] == 3 and x[1] == 1).prob((1, 1, 3))
    print float(pC2GivenH3S1) / pC1GivenH3S1

