from examset import *
import math

class GeneticAlgorithm:
    def __init__(self, initial_examsets, population_size, mutation_function, max_iterations, parent_population_size):
        self.examsets = initial_examsets
        self.population_size = population_size
        self.mutation_function = mutation_function
        self.iteration = 0
        self.max_iterations = max_iterations
        self.top_10 = []

        # parent population size defaults to 25% of the population size
        self.parent_population_size = (parent_population_size if parent_population_size else len(population_size)*0.25)

    def breed(self):
        """Performs the genetic algorithm, going until we finish the total number of iterations."""
        while self.iteration < self.max_iterations:
            mutation_rate = self.mutation_function(self.iteration, self.max_iterations, 2)
            crossover_rate = self.mutation_function(self.iteration, self.max_iterations, 3.5)
            num_to_cross = round(0.30*(self.population_size-self.parent_population_size))
            num_to_mutate = round(0.70*(self.population_size-self.parent_population_size))
            self._breed_iteration(num_to_cross, num_to_mutate, mutation_rate, crossover_rate)
            self.iteration += 1
        return self.examsets

    def _get_random_indices(self, n):
        """Gets n random indices and returns them in a list. None of the indices are repeated."""
        indices = {}
        while len(indices) < n:
            new_index = round(random.random()*self.parent_population_size)
            if new_index in indices:
                indices[new_index] = True
        return indices.keys()

    def breed_iteration(self, num_to_cross, num_to_mutate, mutation_rate, crossover_rate):
        # sort the current examsets and obtain the top lambda in terms of entropy.
        self.examsets = sorted(self.examsets, key = lambda e : e.get_entropy(), reverse=True)
        parents = self.examsets[:self.parent_population_size]
        new_examsets = []

        # get a new set of top 10
        self.top_10 += self.examsets[:10]
        self.top_10 = sorted(self.top_10, key = lambda e : e.get_entropy(), reverse=True)[:10]

        # keep crossing until we have the requisite number of examsets
        # note that we don't care about crossing two pairs that have already
        # been crossed.
        while num_crossed < num_to_cross:
            # cross two examsets that are in the current parental set
            cross_indices = self._get_random_indices(2)
            examset = parents[cross_indices[0]].crossover(parents[cross_indices[1]])
            new_examsets.append(examset)

        while num_mutated < num_to_mutate:
            # mutate an examset into a new examset
            parent_to_mutate = parents[self._get_random_indices(1)[0]]
            new_examsets.append(parent_to_mutate.mutate())

        # new iteration will consist of the new examsets and the old parents 
        # TODO: figure out if I should include the parents in the next iteration or not.
        self.examsets = new_examsets

def mutation_rate_function(iteration, max_iterations, scaling_factor=2):
    """As the iterations increase, mutation rate goes down and instead of exploring the
       same space, incremental improvements are stressed.
    """
    eiter = scaling_factor*math.exp(float(iteration)/max_iterations)
    return 1.0-(eiter/(1+eiter))

if __name__ == '__main__':
    iterations = 300
    for i in xrange(iterations):
        print mutation_rate_function(i, iterations)
