import re
from utils import *
try:
    set()
except NameError:
    from sets import Set as set, ImmutableSet as frozenset

try:
    sorted([])
except NameError:
    def sorted(lst):
        new_lst = list(lst)
        new_lst.sort()
        return new_lst


### We've tried to keep the functions you will need for
### back-chaining at the top of this file. Keep in mind that you
### can get at this documentation from a Python prompt:
###
### >>> import production
### >>> help(production)

def forward_chain(rules, data, apply_only_one=False, verbose=False):
    """
    Apply a list of IF-expressions (rules) through a set of data
    in order.  Return the modified data set that results from the
    rules.

    Set apply_only_one=True to get the behavior we describe in
    class.  When it's False, a rule that fires will do so for
    _all_ possible bindings of its variables at the same time,
    making the code considerably more efficient. In the end, only
    DELETE rules will act differently.
    """
    old_data = ()

    while set(old_data) != set(data):
        old_data = list(data)
        for condition in rules:
            data = condition.apply(data, apply_only_one, verbose)
            if set(data) != set(old_data):
                break

    return data

def instantiate(template, values_dict):
    """
    Given an expression ('template') with variables in it,
    replace those variables with values from values_dict.

    For example:
    >>> instantiate("sister (?x) {?y)", {'x': 'Lisa', 'y': 'Bart'})
    => "sister Lisa Bart"
    """
    if (isinstance(template, AND) or isinstance(template, OR) or
        isinstance(template, NOT)):

        return template.__class__(*[populate(x, values_dict) 
                                    for x in template])
    elif isinstance(template, basestring):
        return AIStringToPyTemplate(template) % values_dict
    else: raise ValueError, "Don't know how to populate a %s" % \
      type(template)

# alternate name for instantiate
populate = instantiate

def match(template, AIStr):
    """
    Given two strings, 'template': a string containing variables
    of the form '(?x)', and 'AIStr': a string that 'template'
    matches, with certain variable substitutions.

    Returns a dictionary of the set of variables that would need
    to be substituted into template in order to make it equal to
    AIStr, or None if no such set exists.
    """
    try:
        return re.match( AIStringToRegex(template), 
                         AIStr ).groupdict()
    except AttributeError: # The re.match() expression probably
                           # just returned None
        return None

def is_variable(str):
    """Is 'str' a variable, of the form '(?x)'?"""
    return isinstance(str, basestring) and str[0] == '(' and \
      str[-1] == ')' and re.search( AIStringToRegex(str) )

def variables(exp):
    """
    Return a dictionary containing the names of all variables in
    'exp' as keys, or None if there are no such variables.
    """
    try:
        return re.search( AIStringToRegex(exp).groupdict() )
    except AttributeError: # The re.match() expression probably
                           # just returned None
        return None
        
class IF(object):
    """
    A conditional rule.

    This should have the form IF( antecedent, THEN(consequent) ),
    or IF( antecedent, THEN(consequent), DELETE(delete_clause) ).

    The antecedent is an expression or AND/OR tree with variables
    in it, determining under what conditions the rule can fire.

    The consequent is an expression or list of expressions that
    will be added when the rule fires. Variables can be filled in
    from the antecedent.

    The delete_clause is an expression or list of expressions
    that will be deleted when the rule fires. Again, variables
    can be filled in from the antecedent.
    """
    def __init__(self, conditional, action = None, 
                 delete_clause = ()):
        # Deal with an edge case imposed by type_encode()
        if type(conditional) == list and action == None:
            return apply(self.__init__, conditional)
        
        # Allow 'action' to be either a single string or an
        # iterable list of strings
        if isinstance(action, basestring):
            action = [ action ]

        self._conditional = conditional
        self._action = action
        self._delete_clause = delete_clause

    def apply(self, rules, apply_only_one=False, verbose=False):
        """
        Return a new set of data updated by the conditions and
        actions of this IF statement.

        If 'apply_only_one' is True, after adding one datum,
        return immediately instead of continuing. This is the
        behavior described in class, but it is slower.
        """
        new_rules = set(rules)
        old_rules_count = len(new_rules)
        bindings = RuleExpression().test_term_matches(
            self._conditional, new_rules)

        for k in bindings:
            for a in self._action:
                new_rules.add( populate(a, k) )
                if len(new_rules) != old_rules_count:
                    if verbose:
                        print "Rule:", self
                        print "Added:", populate(a, k)
                    if apply_only_one:
                        return tuple(sorted(new_rules))
            for d in self._delete_clause:
                try:
                    new_rules.remove( populate(d, k) )
                    if len(new_rules) != old_rules_count:
                        if verbose:
                            print "Rule:", self
                            print "Deleted:", populate(d, k)
                        if apply_only_one:
                            return tuple(sorted(new_rules))
                except KeyError:
                    pass
                    
        return tuple(sorted(new_rules)) # Uniquify and sort the
                                        # output list


    def __str__(self):
        return "IF(%s, %s)" % (str(self._conditional), 
                               str(self._action))

    def antecedent(self):
        return self._conditional

    def consequent(self):
        return self._action

    __repr__ = __str__

class RuleExpression(list):
    """
    The parent class of AND, OR, and NOT expressions.

    Just like Sums and Products from lab 0, RuleExpressions act
    like lists wherever possible. For convenience, you can leave
    out the brackets when initializing them: AND([1, 2, 3]) ==
    AND(1, 2, 3).
    """
    def __init__(self, *args):
        if (len(args) == 1 and isinstance(args[0], list)
            and not isinstance(args[0], RuleExpression)):
            args = args[0]
        list.__init__(self, args)
    
    def conditions(self):
        """
        Return the conditions contained by this
        RuleExpression. This is the same as converting it to a
        list.
        """
        return list(self)

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, 
                           ', '.join([repr(x) for x in self]) )

    __repr__ = __str__
        
    def test_term_matches(self, condition, rules, 
                          context_so_far = None):
        """
        Given an expression which might be just a string, check
        it against the rules.
        """
        rules = set(rules)
        if context_so_far == None: context_so_far = {}

        # Deal with nesting first If we're a nested term, we
        # already have a test function; use it
        if not isinstance(condition, basestring):
            return condition.test_matches(rules, context_so_far)

        # Hm; no convenient test function here
        else:
            return self.basecase_bindings(condition, 
                                          rules, context_so_far)

    def basecase_bindings(self, condition, rules, context_so_far):
        for rule in rules:
            bindings = match(condition, rule)
            if bindings is None: continue
            try:
                context = NoClobberDict(context_so_far)
                context.update(bindings)
                yield context
            except ClobberedDictKey:
                pass

    def get_condition_vars(self):
        if hasattr(self, '_condition_vars'):
            return self._condition_vars

        condition_vars = set()

        for condition in self:
            if isinstance(condition, RuleExpression):
                condition_vars |= condition.get_condition_vars()
            else:
                condition_vars |= AIStringVars(condition)
                
        return condition_vars

    def test_matches(self, rules):
        raise NotImplementedError

    def __eq__(self, other):
        return type(self) == type(other) and list.__eq__(self, other)

    def __hash__(self):
        return hash((self.__class__.__name__, list(self)))

class AND(RuleExpression):
    """A conjunction of patterns, all of which must match."""
    class FailMatchException(Exception):
        pass
    
    def test_matches(self, rules, context_so_far = {}):
        return self._test_matches_iter(rules, list(self))

    def _test_matches_iter(self, rules, conditions = None, 
                           cumulative_dict = None):
        """
        Recursively generate all possible matches.
        """
        # Set default values for variables.  We can't set these
        # in the function header because values defined there are
        # class-local, and we need these to be reinitialized on
        # each function call.
        if cumulative_dict == None:
            cumulative_dict = NoClobberDict()

        # If we have no more conditions to analyze, pass the
        # dictionary that we've accumulated back up the
        # function-call stack.
        if len(conditions) == 0:
            yield cumulative_dict
            return
            
        # Recursive Case
        condition = conditions[0]
        for bindings in self.test_term_matches(condition, rules,
                                               cumulative_dict):
            bindings = NoClobberDict(bindings)
            
            try:
                bindings.update(cumulative_dict)
                for bindings2 in self._test_matches_iter(rules,
                  conditions[1:], bindings):
                    yield bindings2
            except ClobberedDictKey:
                pass

            
class OR(RuleExpression):
    """A disjunction of patterns, one of which must match."""
    def test_matches(self, rules, context_so_far = {}):
        for condition in self:
            for bindings in self.test_term_matches(condition, rules):
                yield bindings

class NOT(RuleExpression):
    """A RuleExpression for negation. A NOT clause must only have
    one part."""
    def test_matches(self, data, context_so_far = {}):
        assert len(self) == 1 # We're unary; we can only process
                              # one condition

        try:
            new_key = populate(self[0], context_so_far)
        except KeyError:
            new_key = self[0]

        matched = False
        for x in self.test_term_matches(new_key, data):
            matched = True

        if matched:
            return
        else:
            yield NoClobberDict()


class THEN(list):
    """
    A THEN expression is a container with no interesting semantics.
    """
    def __init__(self, *args):
        if (len(args) == 1 and isinstance(args[0], list)
            and not isinstance(args[0], RuleExpression)):
            args = args[0]
        super(list, self).__init__()
        for a in args:
            self.append(a)

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join([repr(x) for x in self]) )

    __repr__ = __str__


class DELETE(THEN):
    """
    A DELETE expression is a container with no interesting
    semantics. That's why it's exactly the same as THEN.
    """
    pass

def uniq(lst):
    """
    this is like list(set(lst)) except that it gets around
    unhashability by stringifying everything.  If str(a) ==
    str(b) then this will get rid of one of them.
    """
    seen = {}
    result = []
    for item in lst:
        if not seen.has_key(str(item)):
            result.append(item)
            seen[str(item)]=True
    return result

def simplify(node):
    """
    Given an AND/OR tree, reduce it to a canonical, simplified
    form, as described in the lab.

    You should do this to the expressions you produce by backward
    chaining.
    """
    if not isinstance(node, RuleExpression): return node
    branches = uniq([simplify(x) for x in node])
    if isinstance(node, AND):
        return _reduce_singletons(_simplify_and(branches))
    elif isinstance(node, OR):
        return _reduce_singletons(_simplify_or(branches))
    else: return node

def _reduce_singletons(node):
    if not isinstance(node, RuleExpression): return node
    if len(node) == 1: return node[0]
    return node

def _simplify_and(branches):
    for b in branches:
        if b == FAIL: return FAIL
    pieces = []
    for branch in branches:
        if isinstance(branch, AND): pieces.extend(branch)
        else: pieces.append(branch)
    return AND(*pieces)

def _simplify_or(branches):
    for b in branches:
        if b == PASS: return PASS
    pieces = []
    for branch in branches:
        if isinstance(branch, OR): pieces.extend(branch)
        else: pieces.append(branch)
    return OR(*pieces)

PASS = AND()
FAIL = OR()
run_conditions = forward_chain

