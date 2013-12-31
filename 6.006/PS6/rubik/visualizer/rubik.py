# rubik.py
# Author: Ronald L. Rivest
# Modified: Michael Lieberman
# Last updated: October 24, 2008
#
# Routines to work with Rubik's 2x2x2 cube

"""
We'll call the six sides, as usual:
   Front Back   Up Down   Left Right
or F, B, U, D, L, R.

Permutations:

We'll number the cubie positions starting
at 0, front to back, up to down, left to right.
We give an alphabetic name to the cubies as well,
by listing the faces it contains, starting with
F or B, in clockwise order (looking in from outside).
   0th cubie = FLU
   1st cubie = FUR
   2nd cubie = FDL
   3rd cubie = FRD
   4th cubie = BUL
   5th cubie = BRU
   6th cubie = BLD
   7th cubie = BDR
Each cubie has three faces, so we have 24 face
positions.  We'll label them as 0 to 23, but also
with a 3-letter name that specifies the name
of the cubie it is on, cyclically rotated to
put the name of the face first (so cubie FLU
has faces flu, luf, and ufl, on sides F, L,
and U, respectively). We'll use lower case
here for clarity.  Here are the face names,
written as variables for later convenience.
We also save each number in a second variable,
where the positions are replaced by the colors that
would be there if the cube were solved and had its
orange-yellow-blue cubie in position 7, with yellow
facing down.
"""
# flu refers to the front face (because f is first) of the cubie that
# has a front face, a left face, and an upper face.
# yob refers to the colors yellow, orange, blue that are on the
# respective faces if the cube is in the solved position.
rgw = flu = 0 # (0-th cubie; front face)
gwr = luf = 1 # (0-th cubie; left face)
wrg = ufl = 2 # (0-th cubie; up face)

rwb = fur = 3 # (1-st cubie; front face)
wbr = urf = 4 # (1-st cubie; up face)
brw = rfu = 5 # (1-st cubie; right face)

ryg = fdl = 6 # (2-nd cubie; front face)
ygr = dlf = 7 # (2-nd cubie; down face)
gry = lfd = 8 # (2-nd cubie; left face)

rby = frd = 9 #  (3-rd cubie; front face)
byr = rdf = 10 # (3-rd cubie; right face)
yrb = dfr = 11 # (3-rd cubie; down face)

owg = bul = 12 # (4-th cubie; back face)
wgo = ulb = 13 # (4-th cubie; up face)
gow = lbu = 14 # (4-th cubie; left face)

obw = bru = 15 # (5-th cubie; back face)
bwo = rub = 16 # (5-th cubie; right face)
wob = ubr = 17 # (5-th cubie; up face)

ogy = bld = 18 # (6-th cubie; back face)
gyo = ldb = 19 # (6-th cubie; left face)
yog = dbl = 20 # (6-th cubie; down face)

oyb = bdr = 21 # (7-th cubie; back face)
ybo = drb = 22 # (7-th cubie; down face)
boy = rbd = 23 # (7-th cubie; right face)

"""
A permutation p on 0,1,...,n-1 is represented as
a list of length n-1.  p[i] = j means of course
that p maps i to j.

When operating on a list c (e.g. a list of length
24 of colors), then  p * c
is the rearranged list of colors:
   (p * c)[i] = c[p[i]]    for all i
Thus, p[i] is the location of where the color of
position i will come from; p[i] = j means that
the color at position j moves to position i.
"""

####################################################
### Permutation operations
####################################################

def perm_apply(perm, position):
    """
    Apply permutation perm to a list position (e.g. of faces).
    Face in position p[i] moves to position i.
    """
    return tuple([position[i] for i in perm])

def perm_inverse(p):
    """
    Return the inverse of permutation p.
    """
    n = len(p)
    q = [0]*n
    for i in xrange(n):
        q[p[i]] = i
    return tuple(q)

def perm_to_string(p):
    """
    Convert p to string, slightly more compact
    than list printing.
    """
    s = "("
    for x in p: s = s + "%2d "%x
    s += ")"
    return s

###################################################
### Make standard permutations of faces
###################################################
# Identity: equal to (0, 1, 2, ..., 23).
I = (flu, luf, ufl, fur, urf, rfu, fdl, dlf, lfd, frd, rdf, dfr,     bul, ulb, lbu, bru, rub, ubr, bld, ldb, dbl, bdr, drb, rbd)

"""
When any of the following Rubik's cube permutations are applied, the
three faces on a cubie naturally stay together:
{0,1,2}, {3,4,5}, ..., {21,22,23}.
"""

# Front face rotated clockwise.
F = (fdl, dlf, lfd, flu, luf, ufl, frd, rdf, dfr, fur, urf, rfu, 
     bul, ulb, lbu, bru, rub, ubr, bld, ldb, dbl, bdr, drb, rbd)
# Front face rotated counter-clockwise.
Fi = perm_inverse(F)

# Left face rotated clockwise.
L = (ulb, lbu, bul, fur, urf, rfu, ufl, flu, luf, frd, rdf, dfr,
     dbl, bld, ldb, bru, rub, ubr, dlf, lfd, fdl, bdr, drb, rbd)
# Left face rotated counter-clockwise.
Li = perm_inverse(L)

# Upper face rotated clockwise.
U = (rfu, fur, urf, rub, ubr, bru, fdl, dlf, lfd, frd, rdf, dfr,
     luf, ufl, flu, lbu, bul, ulb, bld, ldb, dbl, bdr, drb, rbd)
# Upper face rotated counter-clockwise.
Ui = perm_inverse(U)

# All 6 possible moves (assuming that the lower-bottom-right cubie
# stays fixed).
quarter_twists = (F, Fi, L, Li, U, Ui)

quarter_twists_names = {}
quarter_twists_names[F] = 'F'
quarter_twists_names[Fi] = 'Fi'
quarter_twists_names[L] = 'L'
quarter_twists_names[Li] = 'Li'
quarter_twists_names[U] = 'U'
quarter_twists_names[Ui] = 'Ui'

def input_configuration():
    """
    Prompts a user to input the current configuration of the cube, and
    translates that into a permutation.
    """
    position = [-1]*24

    cubie = raw_input("""
    Look for the cubie with yellow, blue, and orange faces (it has the
    Rubiks mark). Put this cubie in the lower-back-right corner with
    the yellow face down. We will call this cubie #7.

    Now look at the cubie in the upper-front-left corner. We will call
    this cubie #0. Starting with its front face, and going clockwise,
    input the colors of the faces (e.g. yob, if the colors are yellow,
    orange, and blue):
    cubie #0: """)
    position[0] = eval(cubie)
    position[1] = eval(cubie[1:] + cubie[0])
    position[2] = eval(cubie[2] + cubie[:2])
    cubie = raw_input("""
    Now enter cubie #1, which is to the right of cubie #0, again
    starting with the front face and going clockwise:
    cubie #1: """)
    position[3] = eval(cubie)
    position[4] = eval(cubie[1:] + cubie[0])
    position[5] = eval(cubie[2] + cubie[:2])
    cubie = raw_input("""
    Now enter cubie #2, which is beneath cubie #0:
    cubie #2: """)
    position[6] = eval(cubie)
    position[7] = eval(cubie[1:] + cubie[0])
    position[8] = eval(cubie[2] + cubie[:2])
    cubie = raw_input("""
    Now enter cubie #3, to the right of cubie #2:
    cubie #3: """)
    position[9] = eval(cubie)
    position[10] = eval(cubie[1:] + cubie[0])
    position[11] = eval(cubie[2] + cubie[:2])
    cubie = raw_input("""
    Now enter cubie #4, which is behind cubie #0. Start with the back
    face, and go clockwise:
    cubie #4: """)
    position[12] = eval(cubie)
    position[13] = eval(cubie[1:] + cubie[0])
    position[14] = eval(cubie[2] + cubie[:2])
    cubie = raw_input("""
    Now enter cubie #5, which is to the right of cubie #4:
    cubie #5: """)
    position[15] = eval(cubie)
    position[16] = eval(cubie[1:] + cubie[0])
    position[17] = eval(cubie[2] + cubie[:2])
    cubie = raw_input("""
    Now enter cubie #6, which is beneath cubie #4:
    cubie #6: """)
    position[18] = eval(cubie)
    position[19] = eval(cubie[1:] + cubie[0])
    position[20] = eval(cubie[2] + cubie[:2])
    print """We already know cubie #7, so we're done."""
    cubie = 'oyb'
    position[21] = eval(cubie)
    position[22] = eval(cubie[1:] + cubie[0])
    position[23] = eval(cubie[2] + cubie[:2])

    return tuple(position)
