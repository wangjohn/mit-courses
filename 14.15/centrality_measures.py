def centrality(matrix):
  size = len(matrix)
  triples = {}
  triangles = {}
  for i in xrange(size):
    for j in xrange(size):
      for k in xrange(size):
        if matrix[i][j] == 1 and matrix[j][k] == 1:
          triples[sorted([i,j,k])] = 1
          if matrix[k][i] == 1:
            trianges[sorted([i,j,k])] = 1

  return 3.0*triangles.size()/triples.size()

def average_path_length(matrix):
  size = len(matrix)
  shortest_paths = floyd_warshall(matrix)
  total_sum = sum([sum(row) for row in shortest_paths])

  return float(total_sum) / (size**2 - size)

def floyd_warshall(matrix):
  size = len(matrix)
  shortest_paths = [[sys.maxint for i in size] for i in size]
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

if __name__ == '__main__':
  matrix = [[1]]
  print centrality(matrix)
  print average_path_length(matrix)


