from examset import *
from genetic_algorithm import *
import csv

class Settings:
    """This is class which instantiates all the settings in the problem. In 
       particular, it takes care of the settings related to the genetic 
       algorithm, and also the settings which are inherently related to 
       the problem."""
    def __init__(self):
        self._init_genetic_algorithm_settings()
        self._init_problem_settings()

    def _init_problem_settings(self):
        self.num_students = 13000 
        self.num_questions_per_student = 5
        self.total_required_questions = 200

    def _init_genetic_algorithm_settings(self):
        self.population_size = 100
        self.parent_population_size = int(self.population_size*0.25)
        self.max_iterations = 100
        

def open_student_data(filename):
    # open file with filename and create some question_result objects.
    results = []
    with open(filename, 'rb') as f:
        reader = csv.reader(f, delimiter=";")
        first_row = reader.next()
        for row in reader:
            question_id = row[0]
            student_id = row[1]
            correct = int(row[2])
            results.append(QuestionResult(question_id, student_id, correct))
    return results

def write_result(examset, filename):
    with open(filename, 'wb') as f:
        writer = csv.write(f, delimiter=";")
        header = ["Student ID", "Question 1 ID", "Question 2 ID", "Question 3 ID", "Question 4 ID", "Question 5 ID"] 
        writer.writerow(header)
        for student in examset:
            line = [student.student_id]
            line += [question_id for question_id in student.questions.iterkeys()]
            writer.writerow(line)


def run_algorithm(input_filename, output_filename, settings):
    print "Beginning to read in data..."
    question_results = open_student_data(input_filename)
    print "Finished reading data, setting up data structures..."
    qa = QuestionAssignment(question_results, settings.num_students, settings.num_questions_per_student, settings.total_required_questions)
    print "Finished setting up data structures."

    print "Beginning greedy assignment algorithm."
    # get the examset from the greedy assignment
    greedy_examset = qa.greedy_assignment()
    print "Finished greedy assignment. Entropy of ExamSet: %s" % str(greedy_examset.compute_entropy())
    
    print "Initializing genetic algorithm."
    # create a initial set of examsets to be used for the genetic algorithm
    all_questions_pqs = qa.get_probabilistic_question_set_all_questions()
    initial_examsets = [greedy_examset]
    for i in xrange(settings.population_size - 1):
        # mutate the original greedy examset using a mutation rate of 0.25
        initial_examsets.append(greedy_examset.mutate(0.25, all_questions_pqs))
        # output a print statement every multiple of 10
        if i % 10 == 0:
            print "  Mutating initial dataset, finished mutating %s out of %s" % (str(i), str(settings.population_size)) 

    print "Starting up genetic algorithm."
    # now start up the genetic algorithm.
    genetic = GeneticAlgorithm(initial_examsets, settings.population_size, settings.max_iterations, settings.parent_population_size, settings.total_required_questions, all_questions_pqs)

    # breed and find the top 10. Take the top one and output it.
    top_10 = genetic.breed()
    print "Finished genetic algorithm."

    print "Writing results to: " + output_filename
    write_result(top_10[0], output_filename)
    print "Finished."
    
if __name__ == '__main__':
    settings_default = Settings()
    run_algorithm('astudentData.csv', 'resultExamset.csv', settings_default)
