#!/usr/bin/env python
"""
Implementation of the Time traveling scheduling problem from
2009 Quiz 2
"""
import sys
from csp import CSP, Variable, BinaryConstraint, solve_csp_problem, \
    basic_constraint_checker

def time_traveling_csp_problem():
    constraints = []

    variables = []
    # order of the variables here is the order given in the problem
    variables.append(Variable("T", ["1"]))
    variables.append(Variable("L", ["1", "2", "3", "4"]))
    variables.append(Variable("B", ["1", "2", "3", "4"]))
    variables.append(Variable("C", ["1", "2", "3", "4"]))
    variables.append(Variable("S", ["1", "2", "3", "4"]))
    variables.append(Variable("P", ["1", "2", "3", "4"]))
    variables.append(Variable("N", ["1", "2", "3", "4"]))
    
    # these are all variable pairing of adjacent seats
    edges = [("C", "P"),
             ("C", "L"),
             ("C", "N"),
             ("C", "B"),
             ("B", "C"),
             ("B", "N"),
             ("N", "B"),
             ("N", "C"),
             ("N", "P"),
             ("N", "L"),
             ("N", "T"),
             ("T", "N"),
             ("T", "L"),
             ("L", "T"),
             ("L", "N"),
             ("L", "P"),
             ("P", "L"),
             ("P", "N"),
             ("P", "C"),
             ("P", "S"),
             ("S", "P")]
    
    # not allowed constraints:
    def conflict(val_a, val_b, var_a, var_b):
        if val_a == val_b:
            return False
        return True

    for pair in edges:
        constraints.append(
            BinaryConstraint(pair[0], pair[1],
                             conflict,
                             "Time conflict"))
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

    solve_csp_problem(time_traveling_csp_problem, checker, verbose=True)
