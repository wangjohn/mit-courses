try:
    set()
except:
    from sets import Set as set

import math
import random
from data_reader import *

INFINITY = 1e100
def crosscheck_groups(people):
    # Split up the data in an interesting way.
    group1 = people[0::4] + people[3::4]
    group2 = people[1::4] + people[2::4]
    return group1, group2

def random_split_groups(people):
    # Split up the data randomly, into two groups of ~equal size
    group1 = random.sample(people, len(people)/2)
    group2 = [ x for x in people if not x in group1 ]
    return (group1, group2)
    
def evaluate(factory, group1, group2, verbose=0):
    score = 0
    for (test, train) in ((group1, group2), (group2, group1)):
        classifier = factory(train)
        for legislator in test:
            gold_standard = legislator['party']
            predicted = classifier(legislator)
            if gold_standard == predicted:
                score += 1
                if verbose >= 2:
                    print "%s: %s (correct)" % (legislator_info(legislator),
                    predicted)
            else:
                if verbose >= 1:
                    print "* %s: got %s, actually %s" %\
                    (legislator_info(legislator), predicted, gold_standard)
    if verbose >= 1:
        print "Accuracy: %d/%d" % (score, len(group1) + len(group2))
    return score

def hamming_distance(list1, list2):
    """ Calculate the Hamming distance between two lists """
    # Make sure we're working with lists
    # Sorry, no other iterables are permitted
    assert isinstance(list1, list)
    assert isinstance(list2, list)

    dist = 0

    # 'zip' is a Python builtin, documented at
    # <http://www.python.org/doc/lib/built-in-funcs.html>
    for item1, item2 in zip(list1, list2):
        if item1 != item2: dist += 1
    return dist

edit_distance = hamming_distance

def nearest_neighbors(distance, k=1):
    def nearest_neighbors_classifier(train):
        def classify_value(query):
            best_distance = INFINITY
            ordered = sorted(train, key=lambda x: distance(query['votes'],
            x['votes']))
            nearest = [x['party'] for x in ordered[:k]]
            best_class = None
            best_count = 0
            for party in nearest:
                count = nearest.count(party)
                if count > best_count:
                    best_count = count
                    best_class = party
            return best_class
        return classify_value
    return nearest_neighbors_classifier

def homogeneous_disorder(yes, no):
    result = 0
    if homogeneous_value(yes): result -= len(yes)
    if homogeneous_value(no): result -= len(no)
    return result

def partition(legislators, vote_index, vote_value):
    # Find the people who voted a particular way, and the people who didn't.
    # Yes, No, and Abstain/Absent count as three different options here.
    matched = []
    unmatched = []
    for leg in legislators:
        if leg['votes'][vote_index] == vote_value:
            matched.append(leg)
        else:
            unmatched.append(leg)
    return matched, unmatched

def homogeneous_value(lst):
    """If this list contains just a single value, return it."""
    assert isinstance(lst[0], str)
    for item in lst[1:]:
        if item != lst[0]: return None
    return lst[0]

class CongressIDTree(object):
    def __init__(self, legislators, vote_meanings, disorder_func=None):
        if disorder_func is None: disorder_func = homogeneous_disorder
        self.vote_meanings = vote_meanings
        homog_test = homogeneous_value([leg['party'] for leg in legislators])
        if homog_test:
            self.leaf_value = homog_test
        else:
            self.leaf_value = None
            best_disorder = INFINITY
            best_criterion = None
            for vote_index in xrange(len(legislators[0]['votes'])):
                for vote_value in [1, 0, -1]:
                    yes, no = partition(legislators, vote_index, vote_value)
                    if len(yes) == 0 or len(no) == 0: continue
                    disord = disorder_func([y['party'] for y in yes],
                                           [n['party'] for n in no])
                    if disord < best_disorder:
                        best_disorder = disord
                        best_criterion = (vote_index, vote_value)

            if best_criterion is None:
                # No reasonable criteria left, so give up
                self.leaf_value = 'Unknown'
                return
            vote_index, vote_value = best_criterion
            self.criterion = best_criterion
            self.disorder = best_disorder
            yes_class, no_class = partition(legislators, vote_index, vote_value)
            yes_values = [y['party'] for y in yes]
            no_values = [n['party'] for n in no]
            self.yes_branch = CongressIDTree(yes_class, vote_meanings,
            disorder_func)
            self.no_branch = CongressIDTree(no_class, vote_meanings,
            disorder_func)
    
    def classify(self, legislator):
        if self.leaf_value: return self.leaf_value
        vote_index, vote_value = self.criterion
        if legislator['votes'][vote_index] == vote_value:
            return self.yes_branch.classify(legislator)
        else:
            return self.no_branch.classify(legislator)

    def __str__(self):
        return '\n'+self._str(0)

    def _str(self, indent):
        if self.leaf_value:
            return str(self.leaf_value)
        
        vote_index, vote_value = self.criterion
        value_name = 'Abstain/Absent'
        if vote_value == -1: value_name = 'No'
        elif vote_value == 1: value_name = 'Yes'
        vote_name = vote_info(self.vote_meanings[vote_index])
        indentation = ' '*indent
        disord_string = 'Disorder: %s' % self.disorder
        yes_string = indentation+'+ '+self.yes_branch._str(indent+2)
        no_string = indentation+'- '+self.no_branch._str(indent+2)
        return ("%(disord_string)s\n%(indentation)s%(value_name)s on %(vote_name)s:"
                "\n%(yes_string)s\n%(no_string)s") % locals()


def idtree_maker(vote_meanings, disorder_func):
    def train_classifier(train):
        idtree = CongressIDTree(train, vote_meanings, disorder_func)
        def classify_value(query):
            return idtree.classify(query)
        return classify_value
    return train_classifier


