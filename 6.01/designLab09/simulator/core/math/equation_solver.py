"""
Solver for linear systems of equations.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from numpy import matrix
from numpy.linalg import solve

def solve_equations(equations):
  """
  Solves the given system of |equations|. |equations| should be a list
      of lists of terms summing to 0. Each term should be a tuple of the form
      (coeff, var), where coeff is a number and var is a variable (string).
      Constants can be represented by (const, None).
  Returns a dictionary mapping the variables in the equations to their
      their respective values, or raises an Exception if the system cannot be
      solved.
  """
  # variables in the system of equations
  var_list = list(reduce(set.union, (set(var for coeff, var in eqn if var)
      for eqn in equations)))
  # number of variables
  num_vars = len(var_list)
  # the index of each variable in |var_list|
  var_index = dict(zip(var_list, range(num_vars)))
  # matrices to solve system (Ax = b)
  A, b = [], []
  # populate matrices
  for equation in equations:
    coeffs, const = [0] * num_vars, 0
    for coeff, var in equation:
      if var:
        coeffs[var_index[var]] += coeff
      else:
        const -= coeff
    A.append(coeffs)
    b.append([const])
  try:
    # solve system
    x = solve(matrix(A), matrix(b))
    return dict(zip(var_list, [x[i, 0] for i in xrange(num_vars)]))
  except:
    raise Exception('Could not solve system of equations')
