import os
import sys
import random
import pprint
import utils

def randomProblem(rows = 10, columns = 10, max = 1000):
    """
    Generate a random matrix, with the specified number of rows and
    columns.  Each number is distributed uniformly at random between
    zero and the specified maximum.
    """

    result = []

    for i in range(rows):
        resultRow = []

        for j in range(columns):
            resultRow.append(random.randint(0, max))

        result.append(resultRow)

    return result

def main():
    filename = None
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    (rows, cols) = (10, 10)
    if len(sys.argv) > 3:
        (rows, cols) = (int(sys.argv[2]), int(sys.argv[3]))

    maximum = rows * cols * 2
    if len(sys.argv) > 4:
        maximum = int(sys.argv[4])
    
    generated = randomProblem(rows, cols, maximum)

    print("Generated a matrix with %d row and %d columns." % (rows, cols))
    if filename is None:
        filename = utils.getSaveFilename("problem.py")
        if filename is None:
            return

    with open(filename, "w") as outputFile:
        outputFile.write("problemMatrix = ")
        pprint.pprint(generated, outputFile)

if __name__ == "__main__":
    main()
