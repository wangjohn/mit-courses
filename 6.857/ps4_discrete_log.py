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
    self.problem_statement = problem_statement
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

  def check_result(self, result_a, result_b, z):
    ga_mod_p = self.repeated_squaring(self.problem_statement.g, result_a, self.prime)
    hb_mod_p = self.repeated_squaring(self.problem_statement.h, result_b, self.prime)

    return (ga_mod_p * hb_mod_p % self.prime) == (z % self.prime)

  # Solves the equation for m:
  #   m * value = z mod p
  # This method solves the above by finding the inverse of value and multiplying
  # it with z to obtain m.
  def find_offset_inverse(self, value, z):
    return (self.find_inverse(value)*z) % self.prime

  ########################
  #### Helper methods ####
  ########################

  def repeated_squaring(self, base, exponent, modulo):
    value = base
    current_exponent = 1
    while current_exponent*2 <= exponent:
      current_exponent *= 2
      value = value**2 % modulo

    # finish off the calculation
    for i in xrange(current_exponent, exponent):
      value = value*base % modulo

    return value

  def find_inverse(self, value):
    return self.modular_inverse(value, self.prime)

  def modular_inverse(self, a, p):
    x, y = self.extended_gcd(a, p)
    return x % p

  def extended_gcd(self, a, b):
    if b == 0:
      return (1, 0)

    q = a / b
    r = a % b
    (s, t) = self.extended_gcd(b, r)
    return (t, s - q*t)


if __name__ == '__main__':
  #  'john': 146689,
  #  'hrishi': 22801,
  #  'mari': 58081
  z = 146689 * 22801 * 58081

  ps = ProblemStatement(40,524309,524731,550242371759,519522491680,503576381150)
  discrete_log = QuadraticDiscreteLog(ps)
  a, b = discrete_log.solve_problem(z)
  print "a,b = ", a,b
  print discrete_log.check_result(a, b, z)
