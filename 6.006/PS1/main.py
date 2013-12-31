import sys
import peak
import trace
import algorithms
import json
import utils

################################################################################
################################ The Main Method ###############################
################################################################################

def loadProblem(file = "problem.py", variable = "problemMatrix"):
    """
    Loads a matrix from a python file, and constructs a PeakProblem from it.
    """

    namespace = dict()
    with open(file) as handle:
        exec(handle.read(), namespace)
    return peak.createProblem(namespace[variable])

def main():
    if len(sys.argv) > 1:
        problem = loadProblem(sys.argv[1])
    else:
        problem = loadProblem(utils.getOpenFilename("problem.py"))

    # run all algorithms, gathering the traces and printing out the results as
    # we go
    algorithmList = [("Algorithm 1", algorithms.algorithm1),
                     ("Algorithm 2", algorithms.algorithm2),
                     ("Algorithm 3", algorithms.algorithm3),
                     ("Algorithm 4", algorithms.algorithm4)]

    steps = []
    
    for (name, function) in algorithmList:
        tracer = trace.TraceRecord()
        peak = function(problem, trace = tracer)
        steps.append(tracer.sequence)
        
        status = "is NOT a peak (INCORRECT!)"
        if problem.isPeak(peak):
            status = "is a peak"

        print(name + " : " + str(peak) + " => " + status)

    # write the trace out to a file
    with open("trace.jsonp", "w") as traceFile:
        traceFile.write("parse(")

        json.dump({
            "input" : problem.array,
            "steps" : steps
        }, traceFile)

        traceFile.write(")")

if __name__ == "__main__":
    main()
