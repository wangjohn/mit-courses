#!/usr/bin/env python
"""
Implementation of the 9 by 9 sudoku problem
By: Justin Cullen for 6.034 Fall 2010
Date: Thursday, November 4th
"""
import sys
from csp import CSP, Variable, BinaryConstraint, solve_csp_problem, \
    basic_constraint_checker

#"Diabolical" sudoku. default test board . Specify boards in this format
grid = []
grid.append([0,0,0,9,2,0,0,0,0])
grid.append([0,0,6,8,0,3,0,0,0])
grid.append([1,9,0,0,7,0,0,0,6])
grid.append([2,3,0,0,4,0,1,0,0])
grid.append([0,0,1,0,0,0,7,0,0])
grid.append([0,0,8,0,3,0,0,2,9])
grid.append([7,0,0,0,8,0,0,9,1])
grid.append([0,0,0,5,0,7,2,0,0])
grid.append([0,0,0,0,6,4,0,0,0])


def sudoku_csp_problem(partial_grid=grid):

    #Ensure board is 9x9.  This could easily be extended to n^2 by n^2
    if len(partial_grid)<>9: 'Error: Board must be 9x9'

    for i in range(len(partial_grid)):
        if len(partial_grid[i])<>9:
            return 'Error: Board must be 9x9'

    # Initialize...
    constraints = []

    indices = [(i,j) for i in range(1,10) for j in range(1,10)]
    
    variables = []

    #Initialize variables with one variable for each square.
    for (i,j) in indices:
        if partial_grid[i-1][j-1]<>0:
            theval = [partial_grid[i-1][j-1]]
        else:
            theval = range(1,10)
            
        variables.append(Variable(str(i)+','+str(j),theval))

    #returns i coordinate of a variable
    def i(var):
        return var.get_name()[0]

    #returns j coordinate of a variable
    def j(var):
        return var.get_name()[2]
    
    #gives the 3x3 box a given square is in, they are numbered left to right, top to bottom.
    def getbox(stri,strj):
        i = int(stri)
        j = int(strj)
        if i<=3:
            if j<=3: return 1
            elif 4<=j<=6: return 2
            elif 7<=j<=9: return 3
        elif 4<=i<=6:
            if j<=3: return 4
            elif 4<=j<=6: return 5
            elif 7<=j<=9: return 6
        elif 7<=i<=9:
            if j<=3: return 7
            elif 4<=j<=6: return 8
            elif 7<=j<=9: return 9

        return 'Error: Please enter i,j in the correct range'
        

    # make list of all square sharing a row, column or box
    # no need to duplicate the other way around since this loops through all

    edges = []
    for v1 in variables:
        for v2 in variables:
            if v1<>v2 and (i(v1) == i(v2) or j(v1) == j(v2) or getbox(i(v1),j(v1)) == getbox(i(v2),j(v2))):
                edges.append((v1.get_name(),v2.get_name()))
            

    
    # not allowed to have same value for square:
    def nomatch_constraint(val_a, val_b, name_a, name_b):
        if val_a==val_b:
            return False
        return True


    for e in edges:
        constraints.append(
            BinaryConstraint(e[0], e[1],
                             nomatch_constraint,
                             "Cant match squares in same row, column, or box"))

    return CSP(constraints, variables)

# Outputs the solution given by the CSP in terms of an easily readible text form
def make_solution_readable(solution):
    solstate = solution[0]
    variables = [(v.get_name(),v.get_assigned_value()) for v in solstate.get_all_variables()]
    output = []
    for i in range(9):
        output.append([0,0,0,0,0,0,0,0,0])
    for (name,val) in variables:
        i = int(name[0])
        j = int(name[2])
        output[i-1][j-1] = val

    return output
        

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


    sol = solve_csp_problem(sudoku_csp_problem, checker, verbose=True)
    for row in make_solution_readable(sol):
        print row
