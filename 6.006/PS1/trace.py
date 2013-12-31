import peak

################################################################################
########################### Class for Tracing Execution ########################
################################################################################

class TraceRecord(object):
    """
    A class for storing the trace of an algorithm, to be exported and displayed
    using the HTML visualizer.
    """

    def __init__(self):
        """
        Initialize the trace to empty.

        RUNTIME: O(1)
        """

        self.sequence = []

    def getMaximum(self, arguments, maximum):
        """
        A function for recording the fact that the getMaximum function of
        some subproblem has been called.

        RUNTIME: O(1)
        """

        self.sequence.append({
            "type" : "findingMaximum",
            "coords" : arguments
        })

        self.sequence.append({
            "type" : "foundMaximum",
            "coord" : maximum
        })

    def getBetterNeighbor(self, neighbor, better):
        """
        A function for recording the fact that the getBetterNeighbor function
        of some subproblem has been called.

        RUNTIME: O(1)
        """

        self.sequence.append({
            "type" : "findingNeighbor",
            "coord" : neighbor
        })

        if (neighbor != better):
            self.sequence.append({
                "type" : "foundNeighbor",
                "coord" : better
            })

    def setProblemDimensions(self, subproblem):
        """
        A function for recording the fact that the dimensions of the currently
        studied subproblem have changed.

        RUNTIME: O(1)
        """

        self.sequence.append({
            "type" : "subproblem",
            "startRow" : subproblem.startRow,
            "numRows" : subproblem.numRow,
            "startCol" : subproblem.startCol,
            "numCols" : subproblem.numCol
        })

    def setBestSeen(self, bestSeen):
        """
        A function for recording the fact that the variable "bestSeen" has been
        updated.

        RUNTIME: O(1)
        """

        self.sequence.append({
            "type" : "bestSeen",
            "coord" : bestSeen
        })

    def foundPeak(self, peak):
        """
        A function for recording the fact that the peak has been found.

        RUNTIME: O(1)
        """

        self.sequence.append({
            "type" : "foundPeak",
            "coord" : peak
        })
