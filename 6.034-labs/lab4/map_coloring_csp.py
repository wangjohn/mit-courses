#!/usr/bin/env python
"""
Implementation of the Map coloring problem from 2006 Quiz 2
"""
import sys
from csp import CSP, Variable, BinaryConstraint, solve_csp_problem, \
    basic_constraint_checker

def map_coloring_csp_problem():
    constraints = []

    variables = []
    # order of the variables here is the order given in the problem
    variables.append(Variable("MA", ["B"]))
    variables.append(Variable("TX", ["R"]))
    variables.append(Variable("NE", ["R", "B", "Y"]))
    variables.append(Variable("OV", ["R", "B", "Y"]))
    variables.append(Variable("SE", ["R", "B", "Y"]))
    variables.append(Variable("GL", ["R", "B", "Y"]))
    variables.append(Variable("MID",["R", "B", "Y"]))
    variables.append(Variable("MW", ["R", "B", "Y"]))
    variables.append(Variable("SO", ["R", "B"]))
    variables.append(Variable("NY", ["R", "B"]))
    variables.append(Variable("FL", ["R", "B"]))

    # these are all variable pairing of adjacent seats
    edges = [("NE", "NY"),
             ("NE", "MA"),
             ("MA", "NY"),
             ("GL", "NY"),
             ("GL", "OV"),
             ("MID", "NY"),
             ("OV", "NY"),
             ("OV", "MID"),
             ("MW", "OV"),
             ("MW", "TX"),
             ("TX", "SO"),
             ("SO", "OV"),
             ("SO", "FL"),
             ("FL", "SE"),
             ("SE", "MID"),
             ("SE", "SO")]
    # duplicate the edges the other way.
    all_edges = []
    for edge in edges:
        all_edges.append((edge[0], edge[1]))
        all_edges.append((edge[1], edge[0]))
        
    forbidden = [("R", "B"), ("B", "R"), ("Y", "Y")]
    
    # not allowed constraints:
    def forbidden_edge(val_a, val_b, name_a, name_b):
        if (val_a, val_b) in forbidden or (val_b, val_a) in forbidden:
            return False
        return True

    for pair in all_edges:
        constraints.append(
            BinaryConstraint(pair[0], pair[1],
                             forbidden_edge,
                             "R-B, B-R, Y-Y edges are not allowed"))

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

    solve_csp_problem(map_coloring_csp_problem, checker, verbose=True)
