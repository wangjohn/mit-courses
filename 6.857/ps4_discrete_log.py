class ProblemStatement:
  def __init__(self, i, r, s, p, g, h):
    self.i = i
    self.r = r
    self.s = s
    self.p = p
    self.g = g
    self.h = h

class QuadraticDiscreteLog:
  def __init__(self, problem_statement):
    self.problem_statement = problem_statment
    self.prime = problem_statement.p

  def solve_problem(self, z):
    result_cache = {}

    g_to_a = self.problem_statement.g
    for a in xrange(self.problem_statement.r):
      g_to_a = g_to_a * a
      mga = self.find_offset_inverse(g_to_a, z) % self.prime
      result_cache[mga] = a

    h_to_b = self.problem_statement.h
    for b in xrange(self.problem_statement.s):
      h_to_b = h_to_b * b

      current_key = h_to_b % self.prime
      if current_key in result_cache:
        return (result_cache[current_key], b)

    raise "No Results Found"

  # Solves the equation for m:
  #   m * value = z mod p
  # This method solves the above by finding the inverse of value and multiplying
  # it with z to obtain m.
  def find_offset_inverse(self, value, z):
    return (find_inverse(value)*z) % self.prime

  ########################
  #### Helper methods ####
  ########################

  def find_inverse(self, value):
    return modular_inverse(value, self.prime)

  def modular_inverse(a, p):
    x, y = extended_gcd(a, p)
    return x % p

  def extended_gcd(a, b):
    if b == 0:
      return (1, 0)

    q = a / b
    r = a % b
    (s, t) = extended_gcd(b, r)
    return (t, s - q*t)
