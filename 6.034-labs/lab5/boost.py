from sets import Set as set
from data_reader import *
import math
import orange_for_6034
import orange

class Classifier():
    """
    An abstract class for classification. BaseClassifiers, StandardClassifiers
    and BoostClassifiers inherit from this.
    """
    def __init__(self):
        raise NotImplementedError("This is an abstract class")
    def classify(self, obj):
        raise NotImplementedError
    def orange_classify(self, obj):
        raise NotImplementedError
    def error_rate(self, data, standard):
        """
        Compare this classifier to a StandardClassifier and compute the
        error rate.
        """
        score = 0
        total = len(data)
        for datum in data:
            if self.classify(datum) != standard.classify(datum): score += 1
        return float(score)/total


class StandardClassifier(Classifier):
    """
    A classifier that returns the gold standard value.

    In short, this classifier is one that, by designs, always returns the
    "right answer". Its reason for existence is so that you can compare other
    classifiers to it to test their accuracy.
    """
    def __init__(self, key, value):
        """
        Create a StandardClassifier.

        key: the dictionary key or list index that stores an object's correct
        class.

        value: the class value that will be represented as +1. All other values
        will be represented as -1.
        """
        self.key = key
        self.value = value

    def classify(self, obj):
        """
        If this object's class matches the given value, return +1. Otherwise,
        return -1.
        """
        if obj[self.key] == self.value: return 1
        else: return -1

    def orange_classify(self, obj):
        """
        If this object's class matches the given value, return +1. Otherwise,
        return 0.
        """
        if obj[self.key] == self.value: return 1
        else: return 0

    def __repr__(self):
        return "<StandardClassifier: %s=%s>" % (self.key, self.value)

# The gold standard classifier we will use throughout is
# standardPartyClassifier, which returns +1 for Republican or -1 for any other
# party. The other party might be Democrat, Independent, or (for the 1796 data
# set) Federalist.

standardPartyClassifier = StandardClassifier('party', 'Republican')


class BaseVoteClassifier(Classifier):
    """
    A simplistic classifier that classifies a legislator based on a single
    vote.
    """
    def __init__(self, index, value, votelist):
        """
        Make a base classifier that classifies a dictionary representing
        a legislator, based on one of their votes.

        index: the vote number to look up.
        value: the value to check for. The classifier will return 1 if it
               matches, and -1 if it doesn't.
        votelist: a list of dictionaries that the classifier can use to
                  look up the meanings of the votes.
        """
        self.index = index
        self.value = value
        self.votelist = votelist

    def classify(self, legislator):
        if legislator['votes'][self.index] == self.value: return 1
        else: return -1

    def orange_classify(self, legislator):
        if legislator['votes'][self.index] == self.value: return 1
        else: return 0

    def __str__(self):
        vote = vote_info(self.votelist[self.index])
        if self.value == 1: direction = 'YES'
        else: direction = 'NO'
        return "%s on %s" % (direction, vote)
    def __repr__(self):
        return "<BaseVoteClassifier: %s>" % self


def sigmoid(x):
    return (float(1)/(1+math.exp(-x)))

def error_to_alpha(error_rate):
    """
    Given an error rate, convert it to an alpha value -- that is, a weight to
    assign to a base classifier. Low error rates get high alpha values.
    """
    doubt = 1e-4
    error_rate = min(max(error_rate, doubt), 1-doubt)
    return (math.log(1-error_rate) - math.log(error_rate)) * 0.5

class BoostClassifier(Classifier):
    """
    A classifier that learns by composing several base classifiers using the
    AdaBoost algorithm.
    """
    def __init__(self, base_classifiers, data, standard):
        """
        Create a BoostClassifier.

        base_classifiers: A list of all possible base classifiers to use. Note
        that you automatically get the opposites of these classifiers as well.

        data: the list of data points. These should be classifiable both by the
        base classifiers and by the gold standard classifier.

        standard: the "gold standard" classifier that always returns the
        correct class for a data point.
        """
        self.base_classifiers = base_classifiers
        self.data = data 
        self.data_weights = [1.0/len(data) for d in data]
        self.classifiers = []
        self.standard = standard

    def classify(self, obj):
        """
        Once the boost classifier is trained, this function will use the
        weighted combination of the base classifiers it learned to output a
        final value.

        It should return a class of 1 if the weighted total is positive, and -1
        otherwise.

        obj: a data point to classify

        returns: int (+1 or -1)
        """
        # Fill me in! (the answer given is not correct!)
        return 1

    def orange_classify(self, obj):
        """
        For Orange classification, we need to return a value between 0 and 1,
        rather than either a -1 or a 1,

        This will be very similar to classify, but you'll want to use
        something like the sigmoid function defined above to give a
        different flavor to this answer.

        obj: a data point to classify

        returns: float (between 0 and 1)
        """
        # Fill me in! (the answer given is not correct!)
        return 1

    def best_classifier(self):
        """
        Returns the best base classifier for the current weights, along
        with its error rate.

        NOTE: the "best" classifier is the one that is the best at
        distinguishing the two sets of data points. We're not requiring,
        however, that it is the best at distinguishing them in the direction
        you asked for. That is, a very high error rate like 0.999 is just as
        good as a very low error rate like 0.001!

        Why are we doing this? Because it essentially lets us invert any
        base classifier. The mathematics of boosting means that it will
        automatically count classifiers with error rates _above_ 0.5 as having
        a negative weight, making them act just like their opposite classifier
        which would have a low error rate.

        As an example, this means that if one possible base classifier is
        "voted YES on legalizing ferrets", this could also recognize a class
        that "voted NO or abstained on legalizing ferrets" just by giving you
        the YES classifier with a negative alpha (= a high error rate).
        """
        best_error = 0.5
        best_classifier = None
        for classifier in set(self.base_classifiers) - set(self.classifiers):
            error = 0.0
            for datum, dweight in zip(self.data, self.data_weights):
                if classifier.classify(datum) != self.standard.classify(datum):
                    error += dweight
            if abs(error-0.5) > abs(best_error-0.5):
                best_error = error
                best_classifier = classifier
        if best_classifier is None:
            # none of the classifiers work?
            best_classifier = self.base_classifiers[0]
        return (best_classifier, best_error)

    def train(self, steps=10, verbose=False):
        """
        Run the AdaBoost algorithm for a specified number of steps.
        """
        for i in range(steps): self.step(verbose=verbose)

    def reset(self):
        """
        Reset the classifier to its untrained state.
        """
        self.data_weights = [1.0/len(self.data) for d in self.data]
        self.classifiers = []

    def renormalize_weights(self):
        """
        Ensure that the weights of the data points add up to 1.

        This should be called at every step. Even if your algorithm inherently
        makes the points add up to 1, you may eventually need to correct
        for floating-point drift.
        """
        total = sum(self.data_weights)
        self.data_weights = [w/total for w in self.data_weights]

    def step(self, verbose=False):
        """
        Run one step of boosting:

        * Renormalize the weights
        * Find the classifier that is best at distinguishing the classes
          given these weights
        * Update the weights based on the result of the classifier
        """
        self.renormalize_weights()
        best_classifier, best_error = self.best_classifier()
        if verbose:
            print "[error=%4.4f]" % best_error, best_classifier
        self.update_weights(best_error, best_classifier)
        self.classifiers.append((best_classifier, error_to_alpha(best_error)))

    def update_weights(self, best_error, best_classifier):
        """
        Follows the boosting algorithm to update the weights of the data points.

        best_error: number (int/float) that is the error of the best classifier
        best_classifier: Classifier instance which best classifies the data

        returns: Nothing (only updates self.data_weights)
        """
        # Fill me in!
        pass

    def __str__(self):
        classifier_part = '\n'.join(["%4.4f: %s" % (weight, c) for c, weight in
        self.classifiers])
        return "Boosting classifier:\n"+classifier_part

    def __repr__(self):
        return "<Boosting classifier: %r>" % self.classifiers

def make_vote_classifiers(votelist):
    """
    Given a list of votes, make two BaseVoteClassifiers for each vote
    and return them all in a list.
    """
    classifiers = []
    for index in range(len(votelist)):
        for value in (1, -1):
            classifiers.append(BaseVoteClassifier(index, value, votelist))
    return classifiers



########################################################################
# The following classes help integrate this boosting module with Orange's
# learners and classifiers.  You will not need to edit any code here.

#< OrangeWrapperClassifier

class OrangeWrapperClassifier(Classifier):
    def __init__(self, orange_classifier):
        self.classifier = orange_classifier
    def classify(self, datum):
        decision = self.classifier(datum)
        if decision <= 0:
            return -1
        else:
            return 1
    def orange_classify(self, datum):
        return self.classifier(datum)
    def __str__(self):
        return str(self.classifier)

#>
#< BoostOrangeClassifier

class BoostOrangeClassifier(orange.Classifier):
    def __init__(self, domain, classifier):
        self.classVar = domain.classVar
        self.classifier = classifier
    def __call__(self, example, what = orange.Classifier.GetValue):
        probability = self.classifier.orange_classify(example)

        answer = orange.Value(self.classVar, int(round(probability)))
        probabilities = orange.DiscDistribution(self.classVar)
        probabilities[answer] = probability
        if what == orange.Classifier.GetValue:
            return answer
        elif what == orange.Classifier.GetProbabilities:
            return probabilities
        else:
            return answer, probabilities
    def __str__(self):
        return str(self.classifier)

#>
#< BoostOrangeLearner

class BoostOrangeLearner(orange.Learner):
    # the BoostClassifier above is already a Learner in the Orange sense,
    # because Orange separates the training (Learner) from the classification,
    # but the BoostClassifier combines them.
    def __init__(self, learners, standard):
        self.learners = learners
        self.standard = standard

    def __call__(self, data, weightID=0):
        # FIXME: I have no idea what weightID is supposed to do.  :-/
        classifiers = []
        ourdata = data
        if isinstance(self.learners[self.learners.keys()[0]], orange.Learner):
            classifiers = [OrangeWrapperClassifier(self.learners[i](data))
                           for i in self.learners]
        else:
            classifiers = self.learners
        booster = BoostClassifier(classifiers, data, self.standard)
        booster.train(len(classifiers), verbose = False)
        return BoostOrangeClassifier(data.domain, booster)

#>
#< OrangeStandardClassifier

class OrangeStandardClassifier(Classifier):
    """
    A classifier that returns the gold standard value from an Orange datum.

    This is like StandardClassifier, but one you can use with other files,
    like iris.tab.  It doesn't need to remember the key, because in Orange
    data sets, there is already a distinguished value, rather than it being
    imposed from the outside.
    """
    def __init__(self, value):
        """
        Create a StandardClassifier.

        value: the class value that will be represented as +1. All other values
        will be represented as -1.
        """
        self.value = value

    def classify(self, obj):
        """
        If this object's class matches the given value, return +1. Otherwise,
        return -1.
        """
        if obj.getclass() == self.value: return 1
        else: return -1

    def orange_classify(self, obj):
        """
        If this object's class matches the given value, return +1. Otherwise,
        return 0.
        """
        if obj.getclass() == self.value: return 1
        else: return 0

    def __repr__(self):
        return "<OrangeStandardClassifier: %s>" % (self.value)

#>
