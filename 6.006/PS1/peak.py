import trace

################################################################################
########################### Class for Peak Problems ############################
################################################################################

class PeakProblem(object):
    """
    A class representing an instance of a peak-finding problem.
    """

    def __init__(self, array, bounds):
        """
        A method for initializing an instance of the PeakProblem class.
        Takes an array and an argument indicating which rows to include.

        RUNTIME: O(1)
        """

        (startRow, startCol, numRow, numCol) = bounds

        self.array = array
        self.bounds = bounds
        self.startRow = startRow
        self.startCol = startCol
        self.numRow = numRow
        self.numCol = numCol

    def get(self, location):
        """
        Returns the value of the array at the given location, offset by
        the coordinates (startRow, startCol).

        RUNTIME: O(1)
        """

        (r, c) = location
        if not (0 <= r and r < self.numRow):
            return 0
        if not (0 <= c and c < self.numCol):
            return 0
        return self.array[self.startRow + r][self.startCol + c]

    def getBetterNeighbor(self, location, trace = None):
        """
        If (r, c) has a better neighbor, return the neighbor.  Otherwise,
        return the location (r, c).

        RUNTIME: O(1)
        """

        (r, c) = location
        best = location

        if r - 1 >= 0 and self.get((r - 1, c)) > self.get(best):
            best = (r - 1, c)
        if c - 1 >= 0 and self.get((r, c - 1)) > self.get(best):
            best = (r, c - 1)
        if r + 1 < self.numRow and self.get((r + 1, c)) > self.get(best):
            best = (r + 1, c)
        if c + 1 < self.numCol and self.get((r, c + 1)) > self.get(best):
            best = (r, c + 1)

        if not trace is None: trace.getBetterNeighbor(location, best)

        return best
    
    def getMaximum(self, locations, trace = None):
        """
        Finds the location in the current problem with the greatest value.

        RUNTIME: O(len(locations))
        """
   
        (bestLoc, bestVal) = (None, 0)
    
        for loc in locations:
            if bestLoc is None or self.get(loc) > bestVal:
                (bestLoc, bestVal) = (loc, self.get(loc))
    
        if not trace is None: trace.getMaximum(locations, bestLoc)

        return bestLoc

    def isPeak(self, location):
        """
        Returns true if the given location is a peak in the current subproblem.

        RUNTIME: O(1)
        """

        return (self.getBetterNeighbor(location) == location)

    def getSubproblem(self, bounds):
        """
        Returns a subproblem with the given bounds.  The bounds is a quadruple
        of numbers: (starting row, starting column, # of rows, # of columns).

        RUNTIME: O(1)
        """

        (sRow, sCol, nRow, nCol) = bounds
        newBounds = (self.startRow + sRow, self.startCol + sCol, nRow, nCol)
        return PeakProblem(self.array, newBounds)

    def getSubproblemContaining(self, boundList, location):
        """
        Returns the subproblem containing the given location.  Picks the first
        of the subproblems in the list which satisfies that constraint, and
        then constructs the subproblem using getSubproblem().

        RUNTIME: O(len(boundList))
        """

        (row, col) = location
        for (sRow, sCol, nRow, nCol) in boundList:
            if sRow <= row and row < sRow + nRow:
                if sCol <= col and col < sCol + nCol:
                    return self.getSubproblem((sRow, sCol, nRow, nCol))

        # shouldn't reach here
        return self

    def getLocationInSelf(self, problem, location):
        """
        Remaps the location in the given problem to the same location in
        the problem that this function is being called from.

        RUNTIME: O(1)
        """

        (row, col) = location
        newRow = row + problem.startRow - self.startRow
        newCol = col + problem.startCol - self.startCol
        return (newRow, newCol)

################################################################################
################################ Helper Methods ################################
################################################################################

def getDimensions(array):
    """
    Gets the dimensions for a two-dimensional array.  The first dimension
    is simply the number of items in the list; the second dimension is the
    length of the shortest row.  This ensures that any location (row, col)
    that is less than the resulting bounds will in fact map to a valid
    location in the array.

    RUNTIME: O(len(array))
    """

    rows = len(array)
    cols = 0
    
    for row in array:
        if len(row) > cols:
            cols = len(row)
    
    return (rows, cols)

def createProblem(array):
    """
    Constructs an instance of the PeakProblem object for the given array,
    using bounds derived from the array using the getDimensions function.
   
    RUNTIME: O(len(array))
    """

    (rows, cols) = getDimensions(array)
    return PeakProblem(array, (0, 0, rows, cols))
