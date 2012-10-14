#!/usr/bin/env python
"""
Implementation of the Time traveling scheduling problem from
2009 Quiz 2
"""
import sys
from csp import CSP, Variable, BinaryConstraint, solve_csp_problem, \
    basic_constraint_checker

def ta_scheduling_csp_problem():
    constraints = []

    variables = []
    # order of the variables here is the order given in the problem
    # the domains are those pre-reduced in part A.
    # constraints
    variables.append(Variable("C", ["Mark", "Rob", "Sam"]))
    # optimal search
    variables.append(Variable("O", ["Mark", "Mike", "Sam"]))
    # games
    variables.append(Variable("G", ["Mark"]))
    # rules
    variables.append(Variable("R", ["Mark", "Mike", "Sam"]))
    # id-trees
    variables.append(Variable("I", ["Mark", "Rob", "Sam"]))
    # neural nets
    variables.append(Variable("N", ["Mike", "Sam"]))
    # svms
    variables.append(Variable("S", ["Rob"]))
    # boosting
    variables.append(Variable("B", ["Mike"]))
    
    # these are all variable pairing of adjacent seats
    edges = [("C", "R"),
             ("B", "I"),
             ("B", "S"),
             ("S", "O"),
             ("S", "G"),
             ("S", "R"),
             ("S", "N"),
             ("N", "G")]
    
    # not allowed constraints:
    def conflict(val_a, val_b, var_a, var_b):
        if val_a == val_b:
            return False
        return True

    for pair in edges:
        constraints.append(
            BinaryConstraint(pair[0], pair[1],
                             conflict,
                             "TA(subject_a) != TA(subject_b) constraint"))
    return CSP(constraints, variables)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        checker_type = sys.argv[1]
    else:
        checker_type = "dfs"
        
    if checker_type == "dfs":
        checker = basic_constraint_checker
    elif checker_type == "fc":
        import lab4
        checker = lab4.forward_checking
    elif checker_type == "fcps":
        import lab4
        checker = lab4.forward_checking_prop_singleton
    else:
        import lab4
        checker = lab4.forward_checking_prop_singleton

    solve_csp_problem(ta_scheduling_csp_problem, checker, verbose=True)
