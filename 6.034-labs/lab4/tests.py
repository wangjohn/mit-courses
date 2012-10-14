from tester import make_test, get_tests

from mat_vec_ops import *
from classify import *

import operator
import math

# CSP tests

import csp
from moose_csp import moose_csp_problem

EXPECTED_FC_MOOSE_TREE = """ROOT
	1=Mc(c,1)
		2=Y(c,2)
			3=M(c,3)
				4=O(c,4)
					5=B(f,5)
				4=B(c,6)
					5=O(f,7)
			3=O(c,8)
				4=M(f,9)
				4=B(c,10)
					5=M(f,11)
			3=B(c,12)
				4=M(f,13)
				4=O(c,14)
					5=M(f,15)
		2=M(c,16)
			3=Y(c,17)
				4=O(c,18)
					5=B(f,19)
				4=B(c,20)
					5=O(f,21)
			3=O(c,22)
				4=Y(f,23)
				4=B(c,24)
					5=Y(c,25)
						6=P(*,26)
			3=B(u,-)
		2=P(u,-)
"""

EXPECTED_FCPS_MOOSE_TREE = """ROOT
	1=Mc(c,1)
		2=Y(c,2)
			3=M(f,3)
			3=O(f,4)
			3=B(f,5)
		2=M(c,6)
			3=Y(f,7)
			3=O(c,8)
				4=B(c,9)
					5=Y(c,10)
						6=P(*,11)
			3=B(u,-)
		2=P(u,-)
"""

def csp_test_1_getargs():
    return [ "moose_csp_problem", "forward_checking" ]

def csp_test_1_testanswer(val, original_val = None):
    return ( val == EXPECTED_FC_MOOSE_TREE )

make_test(type = 'FUNCTION',
          getargs = csp_test_1_getargs,
          testanswer = csp_test_1_testanswer,
          expected_val = EXPECTED_FC_MOOSE_TREE,
          name = 'csp_solver_tree'
          )

def csp_test_2_getargs():
    return [ "moose_csp_problem", "forward_checking_prop_singleton" ]

def csp_test_2_testanswer(val, original_val = None):
    return ( val == EXPECTED_FCPS_MOOSE_TREE )

make_test(type = 'FUNCTION',
          getargs = csp_test_2_getargs,
          testanswer = csp_test_2_testanswer,
          expected_val = EXPECTED_FCPS_MOOSE_TREE,
          name = 'csp_solver_tree'
          )

# KNN tests

def euclidean_distance_1_getargs():
    return [ [1,2,3], [4,5,6] ]

def euclidean_distance_1_testanswer(val, original_val = None):
    return ( abs(val - math.sqrt(27)) < 0.00001 )

make_test(type = 'FUNCTION',
          getargs = euclidean_distance_1_getargs,
          testanswer = euclidean_distance_1_testanswer,
          expected_val = math.sqrt(27),
          name = 'euclidean_distance'
          )


senate_people = read_congress_data('S110.ord')
senate_votes = read_vote_data('S110desc.csv')

house_people = read_congress_data('H110.ord')
house_votes = read_vote_data('H110desc.csv')

last_senate_people = read_congress_data('S109.ord')
last_senate_votes = read_vote_data('S109desc.csv')


def euclidean_distance_1_getargs():
    return [ [1,2,3], [4,5,6] ]

def euclidean_distance_1_testanswer(val, original_val = None):
    return ( abs(val - math.sqrt(27)) < 0.00001 )

make_test(type = 'FUNCTION',
          getargs = euclidean_distance_1_getargs,
          testanswer = euclidean_distance_1_testanswer,
          expected_val = math.sqrt(27),
          name = 'euclidean_distance'
          )

def euclidean_distance_2_getargs():
    return [ [0,0], [3,4] ]

def euclidean_distance_2_testanswer(val, original_val = None):
    return ( abs(val - math.sqrt(25)) < 0.00001 )

make_test(type = 'FUNCTION',
          getargs = euclidean_distance_2_getargs,
          testanswer = euclidean_distance_2_testanswer,
          expected_val = 5,
          name = 'euclidean_distance'
          )

def euclidean_distance_3_getargs():
    return [ [random_list(3), random_list(3)] for x in xrange(30) ]

def euclidean_distance_3_testanswer(val, original_val = None):
    return len(val) == 30 and all([validate_euclidean_distance(list1, list2, ans) for (ans, (list1, list2)) in zip(val, original_val) ])
                                  

def disorder_1_getargs():
    return [ ['Democrat','Democrat','Democrat'], ['Republican',"Republican"]]
def disorder_1_testanswer(val, original_val=None):
    return (abs(val - 0) < 0.0001)
make_test(type="FUNCTION",
          getargs = disorder_1_getargs,
          testanswer = disorder_1_testanswer,
          expected_val = 0,
          name='information_disorder')

def disorder_2_getargs():
    return [ ['Democrat','Republican'], ['Democrat',"Republican"]]
def disorder_2_testanswer(val, original_val=None):
    return (abs(val - 1) < 0.0001)
make_test(type="FUNCTION",
          getargs = disorder_2_getargs,
          testanswer = disorder_2_testanswer,
          expected_val = 1,
          name='information_disorder')

def disorder_3_getargs():
    return [ ['Democrat','Democrat','Democrat','Republican'],
             ['Democrat','Republican',"Republican"]]
def disorder_3_testanswer(val, original_val=None):
    return (abs(val - 0.8571428) < 0.0001)
make_test(type="FUNCTION",
          getargs = disorder_3_getargs,
          testanswer = disorder_3_testanswer,
          expected_val = 0.8571428,
          name='information_disorder')



make_test(type = 'MULTIFUNCTION',
          getargs = euclidean_distance_3_getargs,
          testanswer = euclidean_distance_3_testanswer,
          expected_val = '(the test cases for this test are randomly generated; answers will vary, but must be valid Euclidean distances)',
          name = 'euclidean_distance'
          )


def eval_test_1_getargs():
    senate_group1, senate_group2 = crosscheck_groups(senate_people)
    return [ 'my_classifier', senate_group1, senate_group2 ]

def eval_test_1_testanswer(val, original_val = None):
    return ( val >= 97 )

make_test(type = 'FUNCTION',
          getargs = eval_test_1_getargs,
          testanswer = eval_test_1_testanswer,
          expected_val = "Less than or equal to 3 miscategorizations",
          name = 'eval_test'
          )

## This test was rejected on grounds that it's not actually deterministic
## Feel free to run it, by un-commenting this block, if you're curious.
#def eval_test_2_getargs():
#    senate_group1, senate_group2 = crosscheck_groups(senate_people)
#    return [ ['my_classifier'] + list(random_split_groups(senate_people)) for x in xrange(20) ]
#
#def eval_test_2_testanswer(val, original_val = None):
#    return ( val <= 5 )
#
#make_test(type = 'MULTIFUNCTION',
#          getargs = eval_test_2_getargs,
#          testanswer = eval_test_2_testanswer,
#          expected_val = "Less than or equal to 3 miscategorizations",
#          name = 'eval_test'
#          )

rep_classified_getargs = "rep_classified"

def rep_classified_testanswer(val, original_val = None):
    return ( val >= 430 )

make_test(type = 'VALUE',
          getargs = rep_classified_getargs,
          testanswer = rep_classified_testanswer,
          expected_val = "430 or larger",
          name = rep_classified_getargs
          )

senator_classified_getargs = "senator_classified"

def senator_classified_testanswer(val, original_val = None):
    return ( val >= 90 )

make_test(type = 'VALUE',
          getargs = senator_classified_getargs,
          testanswer = senator_classified_testanswer,
          expected_val = "90 or larger",
          name = senator_classified_getargs
          )

old_senator_classified_getargs = "old_senator_classified"

def old_senator_classified_testanswer(val, original_val = None):
    return ( val >= 95 )

make_test(type = 'VALUE',
          getargs = old_senator_classified_getargs,
          testanswer = old_senator_classified_testanswer,
          expected_val = "95 or larger",
          name = old_senator_classified_getargs
          )


