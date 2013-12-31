import imagematrix

class ResizeableImage(imagematrix.ImageMatrix):
    def best_seam(self):
        self.memo = {}
        self.parent = {} 
        for i in range(self.width):
            self.memo[(i,0)] = 0
        for j in range(1, self.height):
            for i in range(self.width):
                min_list = []
                if i == 0:
                    tuple_list = [(i, j-1), (i+1, j-1)]
                elif i == (self.width - 1):
                    tuple_list = [(i, j-1), (i-1, j-1)]
                else:
                    tuple_list = [(i,j-1), (i-1, j-1), (i+1, j-1)]
                for tup in tuple_list:
                    min_list.append(self.memo[tup])
                minimum = min(min_list)
                self.memo[(i,j)] = minimum + self.energy(i,j)
                for k in range(len(min_list)):
                    if min_list[k] == minimum:
                        self.parent[(i,j)] = tuple_list[k]
        return self.get_coordinates()

    def get_coordinates(self):
        coordinates = []
        min_energy = imagematrix.sys.maxint
        for i in range(self.width):
            if self.memo[(i, self.height - 1)] < min_energy:
                min_energy = self.memo[(i, self.height - 1)]
                position = (i, self.height - 1)
        coordinates.append(position)
        while position[1] > 0:
            coordinates.append(self.parent[position])
            position = self.parent[position]
        coordinates.reverse()
        return coordinates

    def remove_best_seam(self):
        self.remove_seam(self.best_seam())
