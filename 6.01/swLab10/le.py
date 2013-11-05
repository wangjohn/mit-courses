"""
Tools for solving systems of linear equations
"""

#solve a system of equations
#hartz, fall 2012
def solveEquations(eqnlist, verbose = False):
    """
    Solve a system of linear equations.  Raises an exception if the number of
    variables is not equal to the number of equations.

    @param eqnlist: the list of equations to be solved.  Each equation is a
    list of tuples (coefficient, variable) such that the sum of coeff*var for
    each pair equals to zero.  If variable is C{None}, then the associated
    coefficient is taken to be a constant term

    @param verbose: If C{True}, prints extra information

    @return: A mapping from variable names to solutions.
    """
    #construct dictionary mapping variable names to vector indices
    #to facilitate expressing the system in matrix form
    name_to_index = {}
    if verbose:
        print 'Solving system of linear equations:'
    for eqn in eqnlist:
        if verbose:
            print eqn
        for (coeff,var) in eqn:
            if var is not None and var not in name_to_index:
                name_to_index[var] = len(name_to_index)

    #make sure we have the right number of equations vs variables
    num_vars = len(name_to_index)
    num_eqns = len(eqnlist)
    if num_vars != num_eqns:
        raise Exception, 'Number of variables (%d) does not match number of equations (%d)' % (num_vars,num_eqns)

    #construct matrix form from our Pythonic representation
    A = []
    b = []
    for eqn in eqnlist:
        a_ins = [0]*num_vars #row to be added to A
        const = 0
        for (coeff,var) in eqn:
            if var is not None:
                a_ins[name_to_index[var]] += coeff #add so that same var can show up twice in one equation
            else:
                const -= coeff
        b.append(const)
        A.append(a_ins)

    #solve matrix equation using Gauss-Jordan elimination
    x = gaussSolve(A,b, verbose=verbose)

    #create and return mapping from variable names to solutions
    index_to_name = {ix:n for (n,ix) in name_to_index.iteritems()}
    if verbose:
        print
        print 'Solution:'
        for ix in xrange(len(x)):
            print '%s = %f' % (index_to_name[ix], x[ix])
    return {index_to_name[ix]:x[ix] for ix in xrange(len(x))}
    


## Gauss-Jordan Elimination as implemented by Numerical Recipes in C
## Python version by Tomas Lozano-Perez (tlp) and Adam Hartz (hartz)
def gaussSolve(A, b, verbose=False):
    """
    Solve Ax=b using Gauss-Jordan elimination

    @param A: the matrix A, as a list of lists

    @param b: the vector b, as a list

    @param verbose: If C{True}, prints extra information

    @return: the solution vector x, as a list
    """
    #make copies because this works in place...
    A = [[float(j) for j in i] for i in A]
    b = [float(i) for i in b]
    if verbose:
        print 'Solving Ax=b'
        print 'with A:'
        for row in A:
            print row
        print
        print 'and b:'
        print 'transpose(%s)' % b
    indexc = len(b)*[0]
    indexr = len(b)*[0]
    ipiv = len(b)*[0]
    for i in xrange(len(b)):
        big = 0.0
        for j in xrange(len(b)):
            if ipiv[j] != 1:
                for k in xrange(len(b)):
                    if ipiv[k] == 0:
                        if abs(A[j][k]) >= big:
                            big = abs(A[j][k])
                            irow = j;
                            icol = k;
                    elif ipiv[k] > 1:
                        raise Exception, "Error: Singular Matrix"
        ipiv[icol] += 1
        if irow != icol:
            for l in xrange(len(b)): 
                A[irow][l],A[icol][l] = A[icol][l],A[irow][l]
            b[irow],b[icol] = b[icol],b[irow]
        indexr[i] = irow
        indexc[i] = icol
        if A[icol][icol] == 0.0:
            raise Exception, "Error: Singular Matrix"
        pivinv = 1.0/A[icol][icol]
        A[icol][icol] = 1.0
        for l in xrange(len(b)): 
            A[icol][l] *= pivinv
        b[icol] *= pivinv
        for ll in xrange(len(b)):
            if ll != icol:
                dum = A[ll][icol]
                A[ll][icol] = 0.0
                for l in xrange(len(b)): 
                    A[ll][l] -= A[icol][l]*dum
                b[ll] -= b[icol]*dum
    for l in xrange(len(b)-1, -1, -1):
        if indexr[l] != indexc[l]:
            for k in xrange(len(b)):
                A[k][indexr[l]],A[k][indexc[l]] = A[k][indexc[l]],A[k][indexr[l]]
    if verbose:
        print
        print 'Solution: x = transpose(%s)' % b
    return b
