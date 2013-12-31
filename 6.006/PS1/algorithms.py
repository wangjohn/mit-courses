import peak
import trace

################################################################################
################################## Algorithms ##################################
################################################################################

def algorithm1(problem, trace = None):
    # if it's empty, we're done 
    if problem.numRow <= 0 or problem.numCol <= 0:
        return None

    # the recursive subproblem will involve half the number of columns
    mid = problem.numCol // 2

    # information about the two subproblems
    (subStartR, subNumR) = (0, problem.numRow)
    (subStartC1, subNumC1) = (0, mid)
    (subStartC2, subNumC2) = (mid + 1, problem.numCol - (mid + 1))

    subproblems = []
    subproblems.append((subStartR, subStartC1, subNumR, subNumC1))
    subproblems.append((subStartR, subStartC2, subNumR, subNumC2))

    # get a list of all locations in the dividing column
    divider = crossProduct(range(problem.numRow), [mid])

    # find the maximum in the dividing column
    bestLoc = problem.getMaximum(divider, trace)

    # see if the maximum value we found on the dividing line has a better
    # neighbor (which cannot be on the dividing line, because we know that
    # this location is the best on the dividing line)
    neighbor = problem.getBetterNeighbor(bestLoc, trace)

    # this is a peak, so return it
    if neighbor == bestLoc:
        if not trace is None: trace.foundPeak(bestLoc)
        return bestLoc
   
    # otherwise, figure out which subproblem contains the neighbor, and
    # recurse in that half
    sub = problem.getSubproblemContaining(subproblems, neighbor)
    if not trace is None: trace.setProblemDimensions(sub)
    result = algorithm1(sub, trace)
    return problem.getLocationInSelf(sub, result)

def algorithm2(problem, location = (0, 0), trace = None):
    # if it's empty, we're done 
    if problem.numRow <= 0 or problem.numCol <= 0:
        return None

    nextLocation = problem.getBetterNeighbor(location, trace)

    if nextLocation == location:
        # there is no better neighbor, so return this peak
        if not trace is None: trace.foundPeak(location)
        return location
    else:
        # there is a better neighbor, so move to the neighbor and recurse
        return algorithm2(problem, nextLocation, trace)

def algorithm3(problem, bestSeen = None, trace = None):
    # if it's empty, we're done 
    if problem.numRow <= 0 or problem.numCol <= 0:
        return None

    midRow = problem.numRow // 2
    midCol = problem.numCol // 2

    # first, get the list of all subproblems
    subproblems = []

    (subStartR1, subNumR1) = (0, midRow)
    (subStartR2, subNumR2) = (midRow + 1, problem.numRow - (midRow + 1))
    (subStartC1, subNumC1) = (0, midCol)
    (subStartC2, subNumC2) = (midCol + 1, problem.numCol - (midCol + 1))

    subproblems.append((subStartR1, subStartC1, subNumR1, subNumC1))
    subproblems.append((subStartR1, subStartC2, subNumR1, subNumC2))
    subproblems.append((subStartR2, subStartC1, subNumR2, subNumC1))
    subproblems.append((subStartR2, subStartC2, subNumR2, subNumC2))

    # find the best location on the cross (the middle row combined with the
    # middle column)
    cross = []

    cross.extend(crossProduct([midRow], range(problem.numCol)))
    cross.extend(crossProduct(range(problem.numRow), [midCol]))

    crossLoc = problem.getMaximum(cross, trace)
    neighbor = problem.getBetterNeighbor(crossLoc, trace)

    # update the best we've seen so far based on this new maximum
    if bestSeen is None or problem.get(neighbor) > problem.get(bestSeen):
        bestSeen = neighbor
        if not trace is None: trace.setBestSeen(bestSeen)

    # return if we can't see any better neighbors
    if neighbor == crossLoc:
        if not trace is None: trace.foundPeak(crossLoc)
        return crossLoc

    # figure out which subproblem contains the largest number we've seen so
    # far, and recurse
    sub = problem.getSubproblemContaining(subproblems, bestSeen)
    newBest = sub.getLocationInSelf(problem, bestSeen)
    if not trace is None: trace.setProblemDimensions(sub)
    result = algorithm3(sub, newBest, trace)
    return problem.getLocationInSelf(sub, result)

def algorithm4(problem, bestSeen = None, rowSplit = True, trace = None):
    # if it's empty, we're done 
    if problem.numRow <= 0 or problem.numCol <= 0:
        return None

    subproblems = []
    divider = []

    if rowSplit:
        # the recursive subproblem will involve half the number of rows
        mid = problem.numRow // 2

        # information about the two subproblems
        (subStartR1, subNumR1) = (0, mid)
        (subStartR2, subNumR2) = (mid + 1, problem.numRow - (mid + 1))
        (subStartC, subNumC) = (0, problem.numCol)

        subproblems.append((subStartR1, subStartC, subNumR1, subNumC))
        subproblems.append((subStartR2, subStartC, subNumR2, subNumC))

        # get a list of all locations in the dividing column
        divider = crossProduct([mid], range(problem.numCol))
    else:
        # the recursive subproblem will involve half the number of columns
        mid = problem.numCol // 2

        # information about the two subproblems
        (subStartR, subNumR) = (0, problem.numRow)
        (subStartC1, subNumC1) = (0, mid)
        (subStartC2, subNumC2) = (mid + 1, problem.numCol - (mid + 1))

        subproblems.append((subStartR, subStartC1, subNumR, subNumC1))
        subproblems.append((subStartR, subStartC2, subNumR, subNumC2))

        # get a list of all locations in the dividing column
        divider = crossProduct(range(problem.numRow), [mid])

    # find the maximum in the dividing row or column
    bestLoc = problem.getMaximum(divider, trace)
    neighbor = problem.getBetterNeighbor(bestLoc, trace)

    # update the best we've seen so far based on this new maximum
    if bestSeen is None or problem.get(neighbor) > problem.get(bestSeen):
        bestSeen = neighbor
        if not trace is None: trace.setBestSeen(bestSeen)

    # return when we know we've found a peak
    if neighbor == bestLoc and problem.get(bestLoc) >= problem.get(bestSeen):
        if not trace is None: trace.foundPeak(bestLoc)
        return bestLoc

    # figure out which subproblem contains the largest number we've seen so
    # far, and recurse, alternating between splitting on rows and splitting
    # on columns
    sub = problem.getSubproblemContaining(subproblems, bestSeen)
    newBest = sub.getLocationInSelf(problem, bestSeen)
    if not trace is None: trace.setProblemDimensions(sub)
    result = algorithm4(sub, newBest, not rowSplit, trace)
    return problem.getLocationInSelf(sub, result)


################################################################################
################################ Helper Methods ################################
################################################################################


def crossProduct(list1, list2):
    """
    Returns all pairs with one item from the first list and one item from 
    the second list.  (Cartesian product of the two lists.)

    The code is equivalent to the following list comprehension:
        return [(a, b) for a in list1 for b in list2]
    but for easier reading and analysis, we have included more explicit code.
    """

    answer = []
    for a in list1:
        for b in list2:
            answer.append ((a, b))
    return answer
