from tester import make_test, get_tests

message = 'your trained neural-net on %s data must test with an accuracy of %1.3f'
expected_accuracy = 1.0

def neural_net_test_testanswer(val, original_val = None):
    return abs(val - expected_accuracy) < 0.01

network_maker_func = "make_neural_net_two_layer"
network_min_size = 3
max_iterations = 10000

def neural_net_size_testanswer(val, original_val = None):
    return val <= network_min_size

make_test(type = 'FUNCTION',
          getargs = lambda: [network_maker_func],
          testanswer = neural_net_size_testanswer,
          expected_val = "your network must have <= %d neural units"\
          %(network_min_size),
          name = 'neural_net_size_tester'
          )

make_test(type = 'FUNCTION',
          getargs = lambda: [network_maker_func,
                             'and_data',
                             'and_test_data',
                             max_iterations],
          testanswer = neural_net_test_testanswer,
          expected_val = message %("AND", expected_accuracy),
          name = 'neural_net_tester'
          )

make_test(type = 'FUNCTION',
          getargs = lambda: [network_maker_func,
                             'or_data',
                             'or_test_data',
                             max_iterations],
          testanswer = neural_net_test_testanswer,
          expected_val = message %("OR", expected_accuracy),
          name = 'neural_net_tester'
          )

make_test(type = 'FUNCTION',
          getargs = lambda: [network_maker_func,
                             'neq_data',
                             'neq_test_data',
                             max_iterations],
          testanswer = neural_net_test_testanswer,
          expected_val = message %("XOR", expected_accuracy),
          name = 'neural_net_tester'
          )

make_test(type = 'FUNCTION',
          getargs = lambda: [network_maker_func,
                             'equal_data',
                             'equal_test_data',
                             max_iterations],
          testanswer = neural_net_test_testanswer,
          expected_val = message %("EQUAL", expected_accuracy),
          name = 'neural_net_tester'
          )

make_test(type = 'FUNCTION',
          getargs = lambda: [network_maker_func,
                             'diag_band_data',
                             'diag_band_test_data',
                             max_iterations],
          testanswer = neural_net_test_testanswer,
          expected_val = message %("diagonal_band", expected_accuracy),
          name = 'neural_net_tester'
          )

challenging_network_maker_func = "make_neural_net_challenging"
challenging_network_min_size = 5

def challenging_neural_net_size_testanswer(val, original_val = None):
    return val <= challenging_network_min_size

make_test(type = 'FUNCTION',
          getargs = lambda: [challenging_network_maker_func],
          testanswer = challenging_neural_net_size_testanswer,
          expected_val = "your network must have <= %d neural units"\
          %(network_min_size),
          name = 'neural_net_size_tester'
          )

make_test(type = 'FUNCTION',
          getargs = lambda: [challenging_network_maker_func,
                             'letter_l_data',
                             'letter_l_test_data',
                             max_iterations],
          testanswer = neural_net_test_testanswer,
          expected_val = message %("letter-l", expected_accuracy),
          name = 'neural_net_tester'
          )

manual_weights_network_maker_func = "make_neural_net_with_weights"
manual_weights_network_max_iterations = 3000

make_test(type = 'FUNCTION',
          getargs = lambda: [manual_weights_network_maker_func,
                             'patch_data',
                             'patch_test_data',
                             manual_weights_network_max_iterations],
          testanswer = neural_net_test_testanswer,
          expected_val = message %("patchy", expected_accuracy),
          name = 'neural_net_tester'
          )

republican_newspaper_vote_getargs = "republican_newspaper_vote"

def republican_newspaper_vote_testanswer(val, original_val = None):
    return ( val in ('no', 'No', 'nay', 'Nay', 'NO') )

make_test(type = 'VALUE',
          getargs = republican_newspaper_vote_getargs,
          testanswer = republican_newspaper_vote_testanswer,
          expected_val = "no",
          name = republican_newspaper_vote_getargs
          )

def classifier_tester_1_getargs():
    return [ 'boost_1796', 'house_1796' ]

def classifier_tester_1_testanswer(val, original_val = None):
    [0.077586206896551727, 0.077586206896551727, 0.034482758620689655,
    0.051724137931034482, 0.025862068965517241, 0.025862068965517241, 0.0,
    0.0086206896551724137, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0]
    return (abs(val[0]-.077586 < 0.0001) and val[19] < 0.0001)

make_test(type = 'FUNCTION',
          getargs = classifier_tester_1_getargs,
          testanswer = classifier_tester_1_testanswer,
          expected_val = "A classifier that improves as much as would be expected by boosting, over 20 steps",
          name = 'classifier_tester'
          )

def most_misclassified_boost_1796_getargs():
    return [ 5 ]

def most_misclassified_boost_1796_testanswer(val, original_val = None):
    return ( len(val) == 5 and 'Dayton (New Jersey-98)' in val )

make_test(type = 'FUNCTION',
          getargs = most_misclassified_boost_1796_getargs,
          testanswer = most_misclassified_boost_1796_testanswer,
          expected_val = "Five hard-to-classify Congressmen including Dayton",
          name = 'most_misclassified_boost_1796'
          )


republican_sunset_vote_getargs = "republican_sunset_vote"

def republican_sunset_vote_testanswer(val, original_val = None):
    return ( val in ('no', 'No', 'nay', 'Nay') )

make_test(type = 'VALUE',
          getargs = republican_sunset_vote_getargs,
          testanswer = republican_sunset_vote_testanswer,
          expected_val = "'no'",
          name = republican_sunset_vote_getargs
          )


def most_misclassified_boost_getargs():
    return [ 5 ]

def most_misclassified_boost_testanswer(val, original_val = None):
    return len(val) == 5

make_test(type = 'FUNCTION',
          getargs = most_misclassified_boost_getargs,
          testanswer = most_misclassified_boost_testanswer,
          expected_val = "Five hard-to-classify Senators",
          name = 'most_misclassified_boost'
          )


def classifier_tester_2_getargs():
    return [ 'boost', 'senate_people' ]

def classifier_tester_2_testanswer(val, original_val = None):
    if abs(val[0]-.0098) > .0001: return False

    for x in xrange(10,len(val)):
        if val[x] > .0001:
            return False

    return True

make_test(type = 'FUNCTION',
          getargs = classifier_tester_2_getargs,
          testanswer = classifier_tester_2_testanswer,
          expected_val = "A classifier that improves as much as would be expected by boosting, over 20 steps",
          name = 'classifier_tester'
          )


vampires_idtree_getargs = "vampires_idtree_odd"

def vampires_idtree_testanswer(val, original_val = None):
    return ( val in ('accent') )

make_test(type = 'VALUE',
          getargs = vampires_idtree_getargs,
          testanswer = vampires_idtree_testanswer,
          expected_val = "accent",
          name = vampires_idtree_getargs
          )


vampires_worst_on_training_getargs = "vampires_worst_on_training"

def vampires_worst_on_training_testanswer(val, original_val = None):
    return ( val in ('svmr') )

make_test(type = 'VALUE',
          getargs = vampires_worst_on_training_getargs,
          testanswer = vampires_worst_on_training_testanswer,
          expected_val = "svmr",
          name = vampires_worst_on_training_getargs
          )


vampires_worst_on_test_getargs = "vampires_worst_on_test"

def vampires_worst_on_test_testanswer(val, original_val = None):
    return ( val in ('svms') )

make_test(type = 'VALUE',
          getargs = vampires_worst_on_test_getargs,
          testanswer = vampires_worst_on_test_testanswer,
          expected_val = "svms",
          name = vampires_worst_on_test_getargs
          )


best_brier_for_h004_getargs = "best_brier_for_h004"

def best_brier_for_h004_testanswer(val, original_val = None):
    return (val in ('maj', 'dt', 'knn', 'svml', 'svmp3', 'svmr', 'svms', 'nb'))

make_test(type = 'VALUE',
          getargs = best_brier_for_h004_getargs,
          testanswer = best_brier_for_h004_testanswer,
          expected_val = "just one algorithm (which one is tested online)",
          name = best_brier_for_h004_getargs
          )



min_disagreement_h004_getargs = "min_disagreement_h004"

def min_disagreement_h004_testanswer(val, original_val = None):
    return val and int(val) == val

make_test(type = 'VALUE',
          getargs = min_disagreement_h004_getargs,
          testanswer = min_disagreement_h004_testanswer,
          expected_val = "an integer value (which one is tested online)",
          name = min_disagreement_h004_getargs
          )



most_divisive_h004_getargs = "most_divisive_h004"

import re
def most_divisive_h004_testanswer(val, original_val = None):
    return (val and re.compile(r'^\d+$').match(val))

make_test(type = 'VALUE',
          getargs = most_divisive_h004_getargs,
          testanswer = most_divisive_h004_testanswer,
          expected_val = "a numeric bill id (which one is tested online)",
          name = most_divisive_h004_getargs
          )




classifiers_for_best_ensemble_getargs = "classifiers_for_best_ensemble"

def classifiers_for_best_ensemble_testanswer(val, original_val = None):
    from lab5 import boosted_ensemble, DATASET_STANDARDS, learners
    subset = {}
    for shortname in val:
        subset[shortname] = learners[shortname]
    accuracy, brier, auc = \
        boosted_ensemble("breast-cancer", subset,
                         DATASET_STANDARDS["breast-cancer"])
    print "Accuracy with best classifiers: "+str(accuracy)
    return (accuracy > .74)

make_test(type = 'VALUE',
          getargs = classifiers_for_best_ensemble_getargs,
          testanswer = classifiers_for_best_ensemble_testanswer,
          expected_val = "a list of classifiers' short names which as an ensemble with boosting get at least 74% on the breast-cancer dataset.",
          name = classifiers_for_best_ensemble_getargs
          )
