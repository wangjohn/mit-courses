# Section 3: Algebraic simplification

# This code implements a simple computer algebra system, which takes in an
# expression made of nested sums and products, and simplifies it into a
# single sum of products. The goal is described in more detail in the
# problem set writeup.

# Much of this code is already implemented. We provide you with a
# representation for sums and products, and a top-level simplify() function
# which applies the associative law in obvious cases. For example, it
# turns both (a + (b + c)) and ((a + b) + c) into the simpler expression
# (a + b + c).

# However, the code has a gap in it: it cannot simplify expressions that are
# multiplied together. In interesting cases of this, you will need to apply
# the distributive law.

# Your goal is to fill in the do_multiply() function so that multiplication
# can be simplified as intended. 

# Testing will be mathematical:  If you return a flat list that
# evaluates to the same value as the original expression, you will
# get full credit.


# We've already defined the data structures that you'll use to symbolically
# represent these expressions, as two classes called Sum and Product,
# defined below. These classes both descend from the abstract Expression class.
#
# The top level function that will be called is the .simplify() method of an
# Expression.
#
# >>> expr = Sum([1, Sum([2, 3])])
# >>> expr.simplify()
# Sum([1, 2, 3])


### Expression classes _____________________________________________________

# Expressions will be represented as "Sum()" and "Product()" objects.
# These objects can be treated just like lists (they inherit from the
# "list" class), but you can test for their type using the "isinstance()"
# function.  For example:
#
# >>> isinstance(Sum([1,2,3]), Sum)
# True
# >>> isinstance(Product([1,2,3]), Product)
# True
# >>> isinstance(Sum([1,2,3]), Expression) # Sums and Products are both Expressions
# True

from depth import depth

class Expression:
    "This abstract class does nothing on its own."
    pass

class Sum(list, Expression):
    """
    A Sum acts just like a list in almost all regards, except that this code
    can tell it is a Sum using isinstance(), and we add useful methods
    such as simplify().

    Because of this:
      * You can index into a sum like a list, as in term = sum[0].
      * You can iterate over a sum with "for term in sum:".
      * You can convert a sum to an ordinary list with the list() constructor:
         the_list = list(the_sum)
      * You can convert an ordinary list to a sum with the Sum() constructor:
         the_sum = Sum(the_list)
    """
    def __repr__(self):
        return "Sum(%s)" % list.__repr__(self)
    
    def simplify(self):
        """
        This is the starting point for the task you need to perform. It
        removes unnecessary nesting and applies the associative law.
        """
        terms = self.flatten()
        if len(terms) == 1:
            return simplify_if_possible(terms)
        else:
            return Sum([simplify_if_possible(term) for term in terms]).flatten()

    def flatten(self):
        """Simplifies nested sums."""
        terms = []
        for term in self:
            if isinstance(term, Sum):
                terms += list(term)
            else:
                terms.append(term)
        return Sum(terms)


class Product(list, Expression):
    """
    See the documentation above for Sum. A Product acts almost exactly
    like a list, and can be converted to and from a list when necessary.
    """
    def __repr__(self):
        return "Product(%s)" % list.__repr__(self)
    
    def simplify(self):
        """
        To simplify a product, we need to multiply all its factors together
        while taking things like the distributive law into account. This
        method calls multiply() repeatedly, leading to the code you will
        need to write.
        """
        factors = []
        for factor in self:
            if isinstance(factor, Product):
                factors += list(factor)
            else:
                factors.append(factor)
        result = factors[0]
        #for factor in factors:
        n =0
        while n < len(factors) -1:
            n += 1
            result = multiply(simplify_if_possible(result), simplify_if_possible(factors[n]))
        #if depth(result) > 1:
          #  self.simplify(result)
        return result.flatten()

    def flatten(self):
        """Simplifies nested products."""
        factors = []
        for factor in self:
            if isinstance(factor, Product):
                factors += list(factor)
            else:
                factors.append(factor)
        return Product(factors)

def simplify_if_possible(expr):
    """
    A helper function that guards against trying to simplify a non-Expression.
    """
    if isinstance(expr, Expression):
        return expr.simplify()
    else:
        return expr

# You may find the following helper functions to be useful.
# "multiply" is provided for you; but you will need to write "do_multiply"
# if you would like to use it.

def multiply(expr1, expr2):
    """
    This function makes sure that its arguments are represented as either a
    Sum or a Product, and then passes the hard work onto do_multiply.
    """
    # Simple expressions that are not sums or products can be handled
    # in exactly the same way as products -- they just have one thing in them.
    if not isinstance(expr1, Expression): expr1 = Product([expr1])
    if not isinstance(expr2, Expression): expr2 = Product([expr2])
    return do_multiply(expr1, expr2)


def do_multiply(expr1, expr2):
    """
    You have two Expressions, and you need to make a simplified expression
    representing their product. They are guaranteed to be of type Expression
    -- that is, either Sums or Products -- by the multiply() function that
    calls this one.

    So, you have four cases to deal with:
    * expr1 is a Sum, and expr2 is a Sum
    * expr1 is a Sum, and expr2 is a Product
    * expr1 is a Product, and expr2 is a Sum
    * expr1 is a Product, and expr2 is a Product

    You need to create Sums or Products that represent what you get by
    applying the algebraic rules of multiplication to these expressions,
    and simplifying.

    Look above for details on the Sum and Product classes. The Python operator
    '*' will not help you.
    """
    if isinstance(expr1, Sum) and isinstance(expr2, Product): #Sum * Product
        result = do_multiply(expr2, expr1)

    elif isinstance(expr1, Product) and isinstance(expr2, Sum):
        result = []
        for e2 in expr2:
            result.append(Product([e2] + expr1))
        result = Sum(result)

    elif isinstance(expr1, Product) and isinstance(expr2, Product):
        result = Product(expr1 + expr2)
    else: #isinstance(expr1, Sum) and isinstance(expr2, Sum): #Sum * Sum
        result = []
        for e1 in expr1:
            for e2 in expr2:
                result.append(Product([e1] + [e2]))
        result = Sum(result)


    return result #use depth. depth 2 for products, depth 1 sums. or len(1)?    

    # Replace this with your solution.
    #raise NotImplementedError

if __name__ == "__main__":
    
    """
    e1 = Sum([1, 2, Sum([3, 4, 5])])
    print(e1)
    e1 = e1.simplify()
    print(e1)
    
    expr = Sum([1, Sum([2, 3])])
    expr = expr.simplify()
    print(expr)

    
    p1 = Product([Sum([1, 2]), Sum([3, 4])])
    p1 = p1.simplify()
    print(p1, "\n")
    """
    p2 = Product([Sum([3, 5]), Sum([10, 20])])
    p2 = p2.simplify()
    print("\n", p2)

    p3 = Product([Sum([2, 4]), Sum([20, 40]), Sum([200, 300])])
    p3 = p3.simplify()
    print("\n", p3)

    #returns correct answer, except with a 1 added at the beginning.
    p4 = Product([Product([10, 100]), Product([2, 4]), Product([50, 500])])
    p4 = p4.simplify()
    print("\n", p4)
    
    """
    p2 = Product([Sum([100, 10]), Sum([2, 20]), Sum([2, 4])])
    p2=p2.simplify()
    print("\n", p2, "\n")
    """
    """
    p3 = [1, 2, 3]
    p4 = [4, 5, 6]
    print("\n\n", Sum(p3))
    print(Product(p3))
    print(Sum([p3, p4]))
    print(Product([p3, p4]))
    print(p3 + p4)
    p5 = []
    p5.append(p3)
    p5.append(p4)
    p5=Product(p5)
    print(p5)
    """
