from examset import *
import csv


def open_student_data(filename)
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

def run_algorithm(filename, num_students, num_questions_per_student, total_required_questions):
    question_results = open_student_data(filename)
    qa = QuestionAssignment(question_results, num_students, num_questions_per_student, total_required_questions)
    
    # get the examset from the greedy assignment
    greedy_examset = qa.greedy_assignment()
    
    # create a initial set of examsets to be used for the genetic algorithm
    initial_examset = [greedy_examset]
    for i in xrange(population_size - 1):
        initial_examset.append(greedy_examset.mutate())
