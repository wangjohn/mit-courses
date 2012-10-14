#!/usr/bin/env python
"""
Implementation of the Moose/Obama/Biden/McCain/Palin problem
from Quiz 2 of 2008.
"""
import sys
from csp import CSP, Variable, BinaryConstraint, solve_csp_problem, \
    basic_constraint_checker

def moose_csp_problem():
    constraints = []

    # We start with the reduced domain.
    # So the constraint that McCain must sit in seat 1 is already
    # covered.
    variables = []
    variables.append(Variable("1", ["Mc"]))
    variables.append(Variable("2", ["Y", "M", "P"]))
    variables.append(Variable("3", ["Y", "M", "O", "B"]))
    variables.append(Variable("4", ["Y", "M", "O", "B"]))
    variables.append(Variable("5", ["Y", "M", "O", "B"]))
    variables.append(Variable("6", ["Y", "M", "P"]))

    # these are all variable pairing of adjacent seats
    adjacent_pairs = [("1", "2"), ("2", "1"),
                      ("2", "3"), ("3", "2"),
                      ("3", "4"), ("4", "3"),
                      ("4", "5"), ("5", "4"),
                      ("5", "6"), ("6", "5"),
                      ("6", "1"), ("1", "6")]
    # now we construct the set of non-adjacent seat pairs.
    nonadjacent_pairs = []
    variable_names = ["1", "2", "3", "4", "5", "6"]
    for x in xrange(len(variable_names)):
        for y in xrange(x,len(variable_names)):
            if x == y:
                continue
            tup = (variable_names[x], variable_names[y])
            rev = (variable_names[y], variable_names[x])
            if tup not in adjacent_pairs:
                nonadjacent_pairs.append(tup)
            if rev not in adjacent_pairs:
                nonadjacent_pairs.append(rev)

    # all pairs is the set of all distinct seating pairs
    # this list is useful for checking where
    # the two seat are assigned to the same person.
    all_pairs = adjacent_pairs + nonadjacent_pairs

    # 1. The Moose is afraid of Palin
    def M_not_next_to_P(val_a, val_b, name_a, name_b):
        if (val_a == "M" and val_b == "P") or (val_a == "P" and val_b == "M"):
            return False
        return True
    for pair in adjacent_pairs:
        constraints.append(BinaryConstraint(pair[0], pair[1], M_not_next_to_P,
                                            "Moose can't be next to Palin"))

    # 2. Obama and Biden must sit next to each other.
    # This constraint can be directly phrased as:
    #
    #   for all sets of adjacents seats
    #      there must exist one pair where O & B are assigned
    #
    #   C(1,2) or C(2,3) or C(3,4) or ... or C(6,1)
    #
    # where C is a binary constraint that checks
    # whether the value of the two variables have values O and B
    #
    # However the way our checker works, the constraint needs to be
    # expressed as a big AND.
    # So that when any one of the binary constraints
    # fails the entire assignment fails.
    #
    # To turn our original OR formulation to an AND:
    # We invert the constraint condition as:
    #
    #  for all sets of nonadjacent seats
    #     there must *not* exist a pair where O & B are assigned.
    #
    #  not C(1,3) and not C(1,4) and not C(1,5) ... not C(6,4)
    #
    # Here C checks whether the values assigned are O and B.
    #
    # Finally, this is an AND of all the binary constraints as required.

    def OB_not_next_to_each_other(val_a, val_b, name_a, name_b):
        if (val_a == "O" and val_b == "B") or \
                (val_a == "B" and val_b == "O"):
            return False
        return True
    
    for pair in nonadjacent_pairs:
        constraints.append(
            BinaryConstraint(pair[0], pair[1],
                             OB_not_next_to_each_other,
                             "Obama, Biden must be next to each-other"))

    # 3. McCain and Palin must sit next to each other
    def McP_not_next_to_each_other(val_a, val_b, name_a, name_b):
        if (val_a == "P" and val_b == "Mc") or (val_a == "Mc" and val_b == "P"):
            return False
        return True

    for pair in nonadjacent_pairs:
        constraints.append(
            BinaryConstraint(pair[0], pair[1],
                             McP_not_next_to_each_other,
                             "McCain and Palin must be next to each other"))

    # 4. Obama + Biden can't sit next to Palin or McCain
    def OB_not_next_to_McP(val_a, val_b, name_a, name_b):
        if ((val_a == "O" or val_a == "B") \
                and (val_b == "Mc" or val_b == "P")) or \
                ((val_b == "O" or val_b == "B") \
                     and (val_a == "Mc" or val_a == "P")):
            return False
        return True
    for pair in adjacent_pairs:
        constraints.append(
            BinaryConstraint(pair[0], pair[1],
                             OB_not_next_to_McP,
                             "McCain, Palin can't be next to Obama, Biden"))

    # No two seats can be occupied by the same person
    def not_same_person(val_a, val_b, name_a, name_b):
        return val_a != val_b
    for pair in all_pairs:
        constraints.append(
            BinaryConstraint(pair[0], pair[1],
                             not_same_person,
                             "No two seats can be occupied by the same person"))
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
        checker = basic_constraint_checker

    solve_csp_problem(moose_csp_problem, checker, verbose=True)
