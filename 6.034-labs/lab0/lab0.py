# This is the file you'll use to submit most of Lab 0.

# Certain problems may ask you to modify other files to accomplish a certain
# task. There are also various other files that make the problem set work, and
# generally you will _not_ be expected to modify or even understand this code.
# Don't get bogged down with unnecessary work.


# Section 1: Problem set logistics ___________________________________________

# This is a multiple choice question. You answer by replacing
# the symbol 'fill-me-in' with a number, corresponding to your answer.

# You get to check multiple choice answers using the tester before you
# submit them! So there's no reason to worry about getting them wrong.
# Often, multiple-choice questions will be intended to make sure you have the
# right ideas going into the problem set. Run the tester right after you
# answer them, so that you can make sure you have the right answers.

# What version of Python do we *recommend* (not "require") for this course?
#   1. Python v2.3
#   2. Python v2.5 or Python v2.6
#   3. Python v3.0
# Fill in your answer in the next line of code ("1", "2", or "3"):

ANSWER_1 = '2'


# Section 2: Programming warmup _____________________________________________

# Problem 2.1: Warm-Up Stretch

def cube(x):
    return x**3

def factorial(x):
    return (x*factorial(x-1) if x > 1 else 1)

def count_pattern(pattern, lst):
    counter = 0; 
    pattlen = len(pattern);

    for idx, x in enumerate(lst):
        if(lst[idx:pattlen+idx]==pattern):
            counter = counter +1
    return counter;

# Problem 2.2: Expression depth

def depth(expr):
    if isinstance(expr, (list, tuple)):
        return max([depth(sub_expr) for sub_expr in expr]) + 1
    else:
        return 0

# Problem 2.3: Tree indexing

def tree_ref(tree, index):
    if isinstance(index, int):
        return tree[index]
    elif len(index) <= 1:
        return tree[index[0]]
    else: 
        return tree_ref(tree[index.pop(0)], index)


# Section 3: Symbolic algebra

# Your solution to this problem doesn't go in this file.
# Instead, you need to modify 'algebra.py' to complete the distributer.

from algebra import Sum, Product, simplify_if_possible
from algebra_utils import distribution, encode_sumprod, decode_sumprod

# Section 4: Survey _________________________________________________________

# Please answer these questions inside the double quotes.

# When did you take 6.01?
WHEN_DID_YOU_TAKE_601 = "Have not yet taken it"

# How many hours did you spend per 6.01 lab?
HOURS_PER_601_LAB = "0"

# How well did you learn 6.01?
HOW_WELL_I_LEARNED_601 = "N/A"

# How many hours did this lab take?
HOURS = "3"
