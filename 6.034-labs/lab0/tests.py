import math
import random
random.seed() # Change to "random.seed(n)" to have the random tests always return the same value

answers = {}

ANSWER_1_getargs = 'VALUE' # Special case to get the value named "FOO_getargs"

def ANSWER_1_testanswer(ans, original_val = None):
    return ( str(ans) == "2" )

ANSWER_1_expected = 2


def cube_1_getargs():
    return [10]

def cube_1_testanswer(ans, original_val = None):
    return ( ans == 1000 )

cube_1_expected = 1000


def cube_2_getargs():
    return [1]

def cube_2_testanswer(ans, original_val = None):
    return ( ans == 1 )

cube_2_expected = 1


def cube_3_getargs():
    return [-5]

def cube_3_testanswer(ans, original_val = None):
    return ( ans == -125 )

cube_3_expected = -125


cube_4_randnum = 0

def cube_4_getargs():
    answers['cube_4_randnum'] = [ random.randint(1,1000) ]
    return answers['cube_4_randnum']

def in_range(a,b,max_delta):
    return (a >= b - max_delta and a <= b + max_delta)

def cube_4_testanswer(ans, original_val = None):
    if original_val == None:
        original_val = answers['cube_4_randnum']

    return ( original_val[0]**3 == ans )

cube_4_expected = "a number between 1 and 1000000000 (this test is randomly generated)"


def factorial_1_getargs():
    return [1]

def factorial_1_testanswer(ans, original_val = None):
    return ( ans == 1 )

factorial_1_expected = 1


def factorial_2_getargs():
    return [5]

def factorial_2_testanswer(ans, original_val = None):
    return ( ans == 120 )

factorial_2_expected = 120


factorial_3_randnum = 0

def factorial_3_getargs():
    answers['factorial_3_randnum'] = [ random.randint(1,12) ]
    return answers['factorial_3_randnum']

def factorial_3_testanswer(ans, original_val = None):
    if original_val == None:
        original_val = answers['factorial_3_randnum']
    for i in xrange(1, original_val[0]+1):
        ans /= float(i)

    return in_range(ans, 1, 0.0001)

factorial_3_expected = "a number between 1! and 30! (this test is randomly generated)"


def count_pattern_1_getargs():
    return [[2,3], [1,2,3,2,3,4,3,4,5]]

def count_pattern_1_testanswer(ans, original_val = None):
    return (ans == 2)

count_pattern_1_expected = 2


def count_pattern_2_getargs():
    return [ [1, [2,3]], [1, [2,3], 2, 3, 1, [2,3,4]] ]

def count_pattern_2_testanswer(ans, original_val = None):
    return ( ans == 1 )

count_pattern_2_expected = 1


def count_pattern_3_getargs():
    answers['count_pattern_3_random'] = random.randint(1,10)
    answers['count_pattern_3_random'] = [[1,2,3,2,3], [1,2,3,2,3]*answers['count_pattern_3_random']]
    return answers['count_pattern_3_random']

def count_pattern_3_testanswer(ans, original_val = None):
    if original_val == None:
        original_val = answers['count_pattern_3_random']
        
    return ( len(original_val[1])/5 == ans )

count_pattern_3_expected = "an integer between 1 and 10 (this test is randomly generated)"


def depth_1_getargs():
    return ['x']

def depth_1_testanswer(ans, original_val = None):
    return (ans == 0)

depth_1_expected = 0


def depth_2_getargs():
    return [['expt', 'x', 2]]

def depth_2_testanswer(ans, original_val = None):
    return (ans == 1)

depth_2_expected = 1


def depth_3_getargs():
    return [['+', ['expt', 'x', 2], ['expt', 'y', 2]]]

def depth_3_testanswer(ans, original_val = None):
    return (ans == 2)

depth_3_expected = 2


def depth_4_getargs():
    return [['/', ['expt', 'x', 5], ['expt', ['-', ['expt', 'x', 2], '1'], ['/', 5, 2]]]]

def depth_4_testanswer(ans, original_val = None):
    return (ans == 4)

depth_4_expected = 4


sample_tree = [[[1, 2], 3], 7, [4, [5, 6]], [8, 9, 10]]

def tree_ref_1_getargs():
    return [sample_tree, [3,1]]

def tree_ref_1_testanswer(ans, original_val = None):
    return ( ans == 9 )

tree_ref_1_expected = 9


def tree_ref_2_getargs():
    return [ sample_tree, [0] ]

def tree_ref_2_testanswer(ans, original_val = None):
    return ( ans == [[1,2],3] )

tree_ref_2_expected = [[1,2],3]


tree_ref_3_random = 0
def tree_ref_3_getargs():
    answers['tree_ref_3_random'] = [ sample_tree, [random.randint(0,len(sample_tree)-1)] ]
    return answers['tree_ref_3_random']

def tree_ref_3_testanswer(ans, original_val = None):
    if original_val == None:
        original_val = answers['tree_ref_3_random']
        
    return ( ans == sample_tree[original_val[1][0]] )

tree_ref_3_expected = "(this test is randomly generated)"


    
from algebra import Sum, Product, Expression

def is_flat(lst, allowed_nesting = 2):
    if isinstance(lst, Sum):
        for elt in lst:
            if isinstance(elt, Product):
                if not is_flat(elt, allowed_nesting=allowed_nesting-1):
                    return False
            elif isinstance(elt, (list, tuple)):
                return False

        return True

    elif isinstance(lst, Product) and allowed_nesting != 0:
        for elt in lst:
            if isinstance(elt, Product):
                if not is_flat(elt, allowed_nesting=allowed_nesting-1):
                    return False
            elif isinstance(elt, (list, tuple)):
                return False

        return True

    elif allowed_nesting == 0:
        for elt in lst:
            if isinstance(elt, (list, tuple)):
                return False

        return True
    else:
        return False

    
def is_list(lst):
    return isinstance(lst, (list, tuple))

def substitute_vars(lst, context = {}):
    retVal = lst.__class__()
    for elt in lst:
        if isinstance(elt, (list, tuple)):
            retVal.append(substitute_vars(elt, context))
        elif elt in context:
            retVal.append(context[elt])
        else:
            retVal.append(elt)

    return retVal


def evaluator(lst, context = {}):

    if isinstance(lst, Sum):
        retVal = 0
        for elt in lst:
            if elt in context.keys():
                elt = context[elt]

            if isinstance(elt, Expression):
                retVal += evaluator(elt, context)
            else:
                retVal += elt
#        print retVal
        return retVal
    
    elif isinstance(lst, Product):        
        retVal = 1
        for elt in lst:
            if elt in context.keys():
                elt = context[elt]

            if isinstance(elt, Expression):
                retVal *= evaluator(elt, context)
            else:
                retVal *= elt

#        print retVal
        return retVal    
        
             
def distribution_1_getargs():
    return [ encode_sumprod(Sum([1, Product([3, 1])])) ]

def distribution_1_testanswer(ans, original_val = None):
    ans = decode_sumprod(ans)
    return ( evaluator(ans) == 4 and is_flat(ans) )

distribution_1_expected = "A simplified Expression that evaluates to 4"
             
             
def distribution_2_getargs():
    return [ encode_sumprod(Product([1, Sum([3, 1])])) ]

def distribution_2_testanswer(ans, original_val = None):
    ans = decode_sumprod(ans)
    return ( evaluator(ans) == 4 and is_flat(ans) )

distribution_2_expected = "A simplified Expression that evaluates to 4"

             
def distribution_3_getargs():
    return [ encode_sumprod(Product([2, Sum([3, 4])])) ]

def distribution_3_testanswer(ans, original_val = None):
    ans = decode_sumprod(ans)
    return ( evaluator(ans) == 14 and is_flat(ans) )
             
distribution_3_expected = "A simplified Expression that evaluates to '14'"

             
def distribution_4_getargs():
    return [ encode_sumprod(Sum([2, Product([3, Product([8, Sum([3, 12]), 5])]) ])) ]
                          

def distribution_4_testanswer(ans, original_val = None):
    ans = decode_sumprod(ans)
    return ( evaluator(ans) == 1802 and is_flat(ans) )
             
distribution_4_expected = "A flat expression that evaluates to 1802"

distribution_5_random = []
             
def distribution_5_getargs():
    answers['distribution_5_random'] = [ encode_sumprod(Sum([2*random.randint(1,50), Product([3, Product([8, Sum(['x', 'y']), 5])]) ])) ]
    return answers['distribution_5_random']

def distribution_5_testanswer(ans, original_val = None):
    ans = decode_sumprod(ans)
    if original_val == None:
        original_val = answers['distribution_5_random']

    original_val = [ decode_sumprod( original_val[0] ) ]
        
    context = {'x': random.randint(1,50), 'y': random.randint(1,50)}

    return ( evaluator(ans, context) == evaluator(original_val[0], context) and is_flat(ans) )

distribution_5_expected = "(this test is randomly generated)"


# Just accept the survey answers as-is
#def survey_answer_getargs():
#    return []
#
#def survey_answer_testanswer(ans, original_val = None):
#    return True

def encode_sumprod(lst):
    retVal = []

    if isinstance(lst, Sum):
        retVal.append('Sum')
    elif isinstance(lst, Product):
        retVal.append('Product')

    for elt in lst:
        if isinstance(elt, (Sum, Product)):
            retVal.append( encode_sumprod(elt) )
        else:
            retVal.append(elt)

    return retVal


def decode_sumprod(lst):
    retVal = []

    for elt in lst[1:]:
        if isinstance(elt, (list, tuple)):
            retVal.append(decode_sumprod(elt))
        else:
            retVal.append(elt)

    if lst[0] == 'Sum':
        retVal = Sum(retVal)
    else:
        retVal = Product(retVal)

    return retVal
            
