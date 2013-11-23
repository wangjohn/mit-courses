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
    Weather = DDist({'rain': 0.6, 'sun': 0.4})
    ActivityGivenWeather = lambda x: DDist({'computer': 0.8, 'outside': 0.2}) if x == 'rain' else DDist({'computer': 0.3, 'outside': 0.7})
    QuantumGivenActivity = lambda x: DDist({'keyboard': 0.8, 'bed': 0.2}) if x == 'computer' else DDist({'keyboard': 0.2, 'bed': 0.8})
    pRainGivenComputer = Weather.bayesianUpdate(ActivityGivenWeather, 'computer').prob('rain')

    WeatherAndActivity = makeJointDistribution(Weather, ActivityGivenWeather)
    QGA = lambda x: QuantumGivenActivity(x[1])
    WeatherAndActivityAndQuantum = makeJointDistribution(WeatherAndActivity, QGA)
    WeatherAndActivityAndQuantum = WeatherAndActivityAndQuantum.project(lambda x: (x[0][0], x[0][1], x[1]))

    pSunAndOutside = makeJointDistribution(Weather, ActivityGivenWeather).prob(('sun', 'outside'))
    pComputer = WeatherAndActivityAndQuantum.project(lambda x: x[1]).prob('computer')
    WeatherAndQuantum = WeatherAndActivityAndQuantum.project(lambda x: (x[0], x[2]))

    pRainGivenKeyboard = WeatherAndQuantum.condition(lambda x: x[1] == 'keyboard').prob(('rain', 'keyboard'))
    pRainGivenBed = WeatherAndQuantum.condition(lambda x: x[1] == 'bed').prob(('rain', 'bed'))

    print float(pRainGivenKeyboard) / pRainGivenBed
