from production import IF, AND, OR, NOT, THEN, run_conditions
import production as lab
from tester import make_test, get_tests, type_encode, type_decode
from zookeeper import ZOOKEEPER_RULES
import random
random.seed()

try:
    set()
except NameError:
    from sets import Set as set, ImmutableSet as frozenset

### TEST 1 ###

test_short_answer_1_getargs = "ANSWER_1"

def test_short_answer_1_testanswer(val, original_val = None):
    return str(val) == '2'

# The antecedent checks data, it does not add any -- it lists the
# questions asked to see if the rule should fire.

make_test(type = 'VALUE',
          getargs = test_short_answer_1_getargs,
          testanswer = test_short_answer_1_testanswer,
          expected_val = "2",
          name = test_short_answer_1_getargs
          )


### TEST 2 ###

test_short_answer_2_getargs = "ANSWER_2"

def test_short_answer_2_testanswer(val, original_val = None):
    return str(val) == 'no'

# Because 'not' is coded in two separate ways.  You and I can
# tell what was meant to happen, but the forward chaining doesn't
# understand English, it just sees meaningless bits, and those do
# not match, in this case.

make_test(type = 'VALUE',
          getargs = test_short_answer_2_getargs,
          testanswer = test_short_answer_2_testanswer,
          expected_val = "no",
          name = test_short_answer_2_getargs
          )


### TEST 3 ###

test_short_answer_3_getargs = "ANSWER_3"

def test_short_answer_3_testanswer(val, original_val = None):
    return str(val) == '2'

# The answer is 2 because, as it says in the lab description, "A
# NOT clause should not introduce new variables - the matcher
# won't know what to do with them."  In forward chaining, let's
# suppose there were no assertions of the form '(?x) is dead',
# then we would try to instantiate the consequent, but what would
# we fill the variable with?  So we cannot forward chain.  Let's
# suppose instead that we found 'Polly is dead' so we did not
# instantiate the consequent.  But then in backward chaining, we
# might need 'Martha is pining for the fjords', and nothing says
# that 'Martha is dead' so it would work -- and different forward
# and backward chaining results would be a disaster.  So NOT
# statements in the antecedent must not have any variables.
# 
# You will also note that one pines for the fjords,
# metaphorically speaking, when one *is* dead.  But that's an
# error in knowledge discovery or entry, not in programming.

make_test(type = 'VALUE',
          getargs = test_short_answer_3_getargs,
          testanswer = test_short_answer_3_testanswer,
          expected_val = "2",
          name = test_short_answer_3_getargs
          )


### TEST 4 ###

test_short_answer_4_getargs = "ANSWER_4"

def test_short_answer_4_testanswer(val, original_val = None):
    return str(val) == '1'

# Rule 1's preconditions, that some one thing both have feathers
# and a beak, are met by the data when that thing is Pendergast.
# The consequent changes the data, so the rule fires.

make_test(type = 'VALUE',
          getargs = test_short_answer_4_getargs,
          testanswer = test_short_answer_4_testanswer,
          expected_val = "1",
          name = test_short_answer_4_getargs
          )


### TEST 5 ###

test_short_answer_5_getargs = "ANSWER_5"

def test_short_answer_5_testanswer(val, original_val = None):
    return str(val) == '0'

# The preconditions for Rule 2 are met, but the consequent is
# already present, so it doesn't fire.  Same for Rule 1.  So no
# rule fires.

make_test(type = 'VALUE',
          getargs = test_short_answer_5_getargs,
          testanswer = test_short_answer_5_testanswer,
          expected_val = "0",
          name = test_short_answer_5_getargs
          )


### TEST 6 ###

transitive_rule_1_getargs = "TEST_RESULTS_TRANS1"

def transitive_rule_1_testanswer(val, original_val = None):
    return ( set(val)  == set([ 'a beats b', 
                                'b beats c', 'a beats c' ]) )

# This test checks to make sure that your transitive rule
# produces the correct set of statements given the a/b/c data.

make_test(type = 'VALUE',
          getargs = transitive_rule_1_getargs,
          testanswer = transitive_rule_1_testanswer,
          expected_val = "[ 'a beats b', 'b beats c', 'a beats c' ]",
          name = transitive_rule_1_getargs
          )


### TEST 7 ###

transitive_rule_2_getargs = "TEST_RESULTS_TRANS2"

def transitive_rule_2_testanswer(val, original_val = None):
    return ( set(val) 
             == set([ 'rock beats rock',
                      'rock beats scissors',
                      'rock beats paper',
                      'scissors beats rock',
                      'scissors beats scissors',
                      'scissors beats paper',
                      'paper beats rock',
                      'paper beats scissors',
                      'paper beats paper' ]) )

# This test checks to make sure that your transitive rule produces
# the correct set of statements given the rock-paper-scissors data.

make_test(type = 'VALUE',
          getargs = transitive_rule_2_getargs,
          testanswer = transitive_rule_2_testanswer,
          expected_val = "[ 'rock beats rock', 'rock beats scissors', 'rock beats paper', 'scissors beats rock', 'scissors beats scissors', 'scissors beats paper', 'paper beats rock', 'paper beats scissors', 'paper beats paper' ]",
          name = transitive_rule_2_getargs
          )


### TEST 8 ###

family_rules_1_getargs = "TEST_RESULTS_1"
expected_family_relations = [
    'brother bob alice',
    'sister alice bob',
    'father chuck bob',
    'son bob chuck',
    'daughter alice chuck',
    'father chuck alice' ]
    
def family_rules_1_testanswer(val, original_val = None):
    return ( set( [ x for x in val
                    if x.split()[0] in (
                                         'father',
                                         'son',
                                         'daughter',
                                         'brother',
                                         'sister',
                                         ) ] )
             == set(expected_family_relations))

# This test checks to make sure that your family rules produce
# the correct set of statements given the alice/bob/chuck data.
# Note that it ignores all statements that don't contain any of
# the words 'father', 'son', 'daughter', 'brother', or 'sister',
# so you can include extra statements if it helps you.

make_test(type = 'VALUE',
          getargs = family_rules_1_getargs,
          testanswer = family_rules_1_testanswer,
          expected_val = "added family relations should include: " + str(expected_family_relations),
          name = family_rules_1_getargs
          )


### TEST 9 ###

family_rules_2_getargs = 'TEST_RESULTS_2'

def family_rules_2_testanswer(val, original_val = None):
    return ( set( [ x for x in val
                    if x.split()[0] == 'cousin' ] )
             == set([ 'cousin c1 c3',
                      'cousin c1 c4',
                      'cousin c2 c3',
                      'cousin c2 c4',
                      'cousin c3 c1',
                      'cousin c3 c2',
                      'cousin c4 c1',
                      'cousin c4 c2',
                      'cousin d1 d2',
                      'cousin d2 d1',
                      'cousin d3 d4',
                      'cousin d4 d3' ]) )

# This test checks to make sure that your family rules produce
# the correct set of statements given the a/b/c/d data.

make_test(type = 'VALUE',
          getargs = family_rules_2_getargs,
          testanswer = family_rules_2_testanswer,
          expected_val = "Results including " + str([ 'cousin c1 c3',
                               'cousin c1 c4',
                               'cousin c2 c3',
                               'cousin c2 c4',
                               'cousin c3 c1',
                               'cousin c3 c2',
                               'cousin c4 c1',
                               'cousin c4 c2',
                               'cousin d1 d2',
                               'cousin d2 d1',
                               'cousin d3 d4',
                               'cousin d4 d3' ]),
          name = family_rules_2_getargs
          )


### TEST 10 ###

def tree_map(lst, fn):
    if isinstance(lst, (list, tuple)):
        return fn([ tree_map(elt, fn) for elt in lst ])
    else:
        return lst

def backchain_to_goal_tree_1_getargs():
    return [ (),  'stuff'  ]

def backchain_to_goal_tree_1_testanswer(val, original_val = None):
    return ( val == 'stuff' or val == [ 'stuff' ])

# This test checks to make sure that your backchainer produces
# the correct goal tree given a hypothesis and an empty set of
# rules.  The goal tree should contain only the hypothesis.

make_test(type = 'FUNCTION_ENCODED_ARGS',
          getargs = backchain_to_goal_tree_1_getargs,
          testanswer = backchain_to_goal_tree_1_testanswer,
          expected_val = '[ \'stuff\' ]',
          name = "backchain_to_goal_tree"
          )


### TEST 11 ###

def backchain_to_goal_tree_2_getargs():
    return [ ZOOKEEPER_RULES,  'alice is an albatross'  ]

result_bc_2 = OR('alice is an albatross',
                 AND(OR('alice is a bird',
                        'alice has feathers',
                        AND('alice flies',
                            'alice lays eggs')),
                     'alice is a good flyer'))

def backchain_to_goal_tree_2_testanswer(val, original_val = None):
    return ( tree_map(type_encode(val), frozenset) ==
             tree_map(type_encode(result_bc_2), frozenset))

# This test checks to make sure that your backchainer produces
# the correct goal tree given the hypothesis 'alice is an
# albatross' and using the ZOOKEEPER_RULES.

make_test(type = 'FUNCTION_ENCODED_ARGS',
          getargs = backchain_to_goal_tree_2_getargs,
          testanswer = backchain_to_goal_tree_2_testanswer,
          expected_val = str(result_bc_2)
          )


### TEST 12 ###

def backchain_to_goal_tree_3_getargs():
    return [ ZOOKEEPER_RULES,  'geoff is a giraffe'  ]

result_bc_3 = OR('geoff is a giraffe',
                 AND(OR('geoff is an ungulate',
                        AND(OR('geoff is a mammal',
                               'geoff has hair',
                               'geoff gives milk'),
                            'geoff has hoofs'),
                        AND(OR('geoff is a mammal',
                               'geoff has hair',
                               'geoff gives milk'),
                            'geoff chews cud')),
                     'geoff has long legs',
                     'geoff has long neck',
                     'geoff has tawny color',
                     'geoff has dark spots'))
    
def backchain_to_goal_tree_3_testanswer(val, original_val = None):
    return ( tree_map(type_encode(val), frozenset) ==
             tree_map(type_encode(result_bc_3), frozenset))

# This test checks to make sure that your backchainer produces
# the correct goal tree given the hypothesis 'geoff is a giraffe'
# and using the ZOOKEEPER_RULES.

make_test(type = 'FUNCTION_ENCODED_ARGS',
          getargs = backchain_to_goal_tree_3_getargs,
          testanswer = backchain_to_goal_tree_3_testanswer,
          expected_val = str(result_bc_3)
          )

          
### TEST 13 ###

def backchain_to_goal_tree_4_getargs():
    return [ [ IF( AND( '(?x) has (?y)',
                        '(?x) has (?z)' ),
                   THEN( '(?x) has (?y) and (?z)' ) ),
               IF( '(?x) has rhythm and music',
                   THEN( '(?x) could not ask for anything more' ) ) ], 
             'gershwin could not ask for anything more' ]

result_bc_4 = OR('gershwin could not ask for anything more',
                 'gershwin has rhythm and music', 
                 AND('gershwin has rhythm',
                     'gershwin has music'))

def backchain_to_goal_tree_4_testanswer(val, original_val = None):
    return ( tree_map(type_encode(val), frozenset) ==
             tree_map(type_encode(result_bc_4), frozenset) )

# This test checks to make sure that your backchainer produces
# the correct goal tree given the hypothesis 'gershwin could not
# ask for anything more' and using the rules defined in
# backchain_to_goal_tree_4_getargs() above.

make_test(type = 'FUNCTION_ENCODED_ARGS',
          getargs = backchain_to_goal_tree_4_getargs,
          testanswer = backchain_to_goal_tree_4_testanswer,
          expected_val = str(result_bc_4)
          )
          

### TEST 14 ###

ARBITRARY_EXP = (
    IF( AND( 'a (?x)',
             'b (?x)' ),
        THEN( 'c d' '(?x) e' )),
    IF( OR( '(?y) f e',
            '(?y) g' ),
        THEN( 'h (?y) j' )),
    IF( AND( 'h c d j',
             'h i j' ),
        THEN( 'zot' )),
    IF( '(?z) i',
        THEN( 'i (?z)' ))
    )
  
def backchain_to_goal_tree_5_getargs():
    return [ ARBITRARY_EXP, 'zot' ]

result_bc_5 = OR('zot',
                 AND('h c d j',
                     OR('h i j', 'i f e', 'i g', 'g i')))

def backchain_to_goal_tree_5_testanswer(val, original_args = None):
    return ( tree_map(type_encode(val), frozenset) ==
             tree_map(type_encode(result_bc_5), frozenset))

# This test checks to make sure that your backchainer produces
# the correct goal tree given the hypothesis 'zot' and using the
# rules defined in ARBITRARY_EXP above.

make_test(type = 'FUNCTION_ENCODED_ARGS',
          getargs = backchain_to_goal_tree_5_getargs,
          testanswer = backchain_to_goal_tree_5_testanswer,
          expected_val = str(result_bc_5)
          )
          

### TEST 15 ###

HOW_MANY_HOURS_THIS_PSET_TOOK_getargs = 'HOW_MANY_HOURS_THIS_PSET_TOOK'

def HOW_MANY_HOURS_THIS_PSET_TOOK_testanswer(val, original_val = None):
    return ( val != '' and val != None)

make_test(type = 'VALUE',
          getargs = HOW_MANY_HOURS_THIS_PSET_TOOK_getargs,
          testanswer = HOW_MANY_HOURS_THIS_PSET_TOOK_testanswer,
          expected_val = '[a number of hours]',
          name = HOW_MANY_HOURS_THIS_PSET_TOOK_getargs
          )


### TEST 16 ###

WHAT_I_FOUND_INTERESTING_getargs = 'WHAT_I_FOUND_INTERESTING'

def WHAT_I_FOUND_INTERESTING_testanswer(val, original_val = None):
    return ( val != '' and val != None)

make_test(type = 'VALUE',
          getargs = WHAT_I_FOUND_INTERESTING_getargs,
          testanswer = WHAT_I_FOUND_INTERESTING_testanswer,
          expected_val = '[an interesting thing]',
          name = WHAT_I_FOUND_INTERESTING_getargs
          )


### TEST 17 ###

WHAT_I_FOUND_BORING_getargs = 'WHAT_I_FOUND_BORING'

def WHAT_I_FOUND_BORING_testanswer(val, original_val = None):
    return ( val != '' and val != None)

make_test(type = 'VALUE',
          getargs = WHAT_I_FOUND_BORING_getargs,
          testanswer = WHAT_I_FOUND_BORING_testanswer,
          expected_val = '[a boring thing]',
          name = WHAT_I_FOUND_BORING_getargs
          )

