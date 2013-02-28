import csv
import sys

def centrality(matrix):
  size = len(matrix)
  triples = 0
  triangles = 0
  for i in xrange(size):
    for j in xrange(size):
      for k in xrange(j+1,size):
        if matrix[i][j] == 1 and matrix[i][k] == 1:
          triples += 1
          if matrix[j][k] == 1:
            triangles += 1

  print triangles
  print triples
  return float(triangles)/((triples))

def average_path_length(matrix):
  size = len(matrix)
  shortest_paths = floyd_warshall(matrix)

  adjusted_sp = []
  for row in shortest_paths:
    adjusted_sp.append([i for i in row if i < sys.maxint])

  total_sum = sum([sum(row) for row in adjusted_sp])

  return float(total_sum) / (size**2 - size)

def floyd_warshall(matrix):
  size = len(matrix)
  shortest_paths = [[sys.maxint for i in xrange(size)] for i in xrange(size)]
  for i in xrange(size):
    shortest_paths[i][i] = 0
    for j in xrange(size):
      if matrix[i][j] == 1:
        shortest_paths[i][j] = 1

  for i in xrange(size):
    for j in xrange(size):
      for k in xrange(size):
        if shortest_paths[i][k] + shortest_paths[k][j] < shortest_paths[i][j]:
          shortest_paths[i][j] = shortest_paths[i][k] + shortest_paths[k][j]

  return shortest_paths

def csv_to_matrix(filename):
  matrix = []
  with open(filename, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
      new_row = [int(i) for i in row]
      matrix.append(new_row)
  return matrix

if __name__ == '__main__':
  matrix = csv_to_matrix('les_miserable.csv')
  print centrality(matrix)
  print average_path_length(matrix)


