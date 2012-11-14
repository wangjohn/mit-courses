class QuestionResult:
    """Class for storing the result of a question. Used when reading in data."""
    def __init__(self, question_id, student_id, correct):
        self.question_id = question_id  
        self.student_id = student_id
        self.correct = correct

class StudentResult:
    """Class for storing the result of a particular student's performance on 
       test exams. Created and populated when reading in data an processing it."""
    def __init__(self, question_results, student_id, num_correct, num_questions):
        self.question_results = question_results  # hash of question_id : QuestionResult
        self.student_id = student_id
        self.num_correct = num_correct
        self.num_questions = num_questions
        self.theta = 0

    def percentage_correct():
        return self.num_correct*1.0 / self.num_questions

class Question:
    """Class for one of the questions asked. Methods provide a question_id, 
       a probability of getting the question right, and the entropy."""
    def __init__(self, question_id, rj):
        self.question_id = question_id
        self.rj = rj
        self.entropy = get_entropy(self.rj) + get_entropy(1 - self.rj) 

class Student:
    """Potential student. This is a model of a random student taking a set of
       k questions. Used when creating an ExamSet and evaluating the set."""
    def __init__(self, questions):
        self.questions = questions
        self.k = len(self.questions)
        self.score_probabilities = None

    def get_score_dispersion(self):
        """Returns the max_score - min_score (range of the score possibilities."""
        self.get_score_probabilities()
        max_score = None
        min_score = None
        for score, prob in self.score_probabilities:
            if max_score == None or score > max_score:
                max_score = score
            if min_Score == None or score < min_score:
                min_score = score
        return max_score - min_score

    def get_score_probabilities(self):
        """Returns a list of tuples of (score, probability) for all of the 
           possible combinations of scores and their probabilities for a given
           student."""
        if not self.score_probabilities:
            self.score_probabilities = self._exponential_recursion(0, [(0,1)])
        return self.score_probabilities

    def _exponential_recursion(self, i, score_prob):
        # method for getting the score probabilities by doing all possible 
        # combinations of scores. 
        current_rj = self.questions[i].rj 
        new_score_prob = []
        for score, prob in score_prob:
            # create new tuples based on each of the previous scores.
            new_score = score + 1.0/current_rj
            incorrect = (score, prob*(1.0-current_rj))
            correct = (new_score, prob*1.0*current_rj)
            new_score_prob.append(incorrect)
            new_score_prob.append(correct)
        # recurse until we run out of questions
        if i+1 < len(self.questions):
            return self._exponential_recursion(i+1, new_score_prob)
        else:
            return new_score_prob

    def get_score_probabilities_approx(self):
        """Gets an approximation for the score probabilities, unless the 
           score probabilities are already computed."""
        if self.score_probabilities:
            return self.score_probabilities
        probs = [1] + [0 for x in xrange(self.k-1)]
        for q in xrange(1,self.k+1,1):
            new_probs = []
            for s in xrange(self.k+1):
                if s > q:
                    # if score is greater than q, no possible way to get that score
                    new_probs.append(0.0)
                else:
                    extra_term = 0
                    # recursive formula for new probability
                    if s-1 >= 0:
                        extra_term = probs[s-1]*self.questions[q].rj
                    new_probs.append(extra_term + probs[s]*(1.0-self.questions[q].rj))
            probs = new_probs
        self.score_probabilities = probs
        return probs
                
class Examset:
    """Class which represents an possible ExamSet to be given to a set of 
       students. The ExamSet contains a list of students and the possible 
       questions that will be posed."""
    def __init__(self, student_list, bin_size=None):
        self.students = student_list
        self.entropy = None
        self.bins = None
        if bin_size:
            self.bin_size = bin_size
        else:
            self.bin_size = self.compute_bin_size(student_list)


    def compute_bin_size(self, students):
        """Computes the bin size to use for computing entropies and 
           probabilities."""
        max_disp = None
        min_disp = None
        for student in students:
            disp = student.get_score_dispersion()
            if max_disp == None or disp > max_disp:
                max_disp = disp
            if min_disp == None or disp < max_disp:
                min_disp = disp
        # current heuristic is to take the minimum score dispersion and multiply by 2.5
        # we would rather have small bin size, then bins which are too large.
        self.bin_size = min_disp * 2.5
        return self.bin_size

    def compute_entropy(self):
        """Computes the entropy of the examset."""
        if self.entropy:
            return self.entropy
        if not self.bins:
            self.bins = self.build_histogram(self.bin_size)
        entropy = 0
        for cumulative_prob, count in self.bins.itervalues():
            avg_prob = cumulative_prob * 1.0 / count
            entropy += get_entropy(avg_prob)
        self.entropy = entropy
        return entropy

    def build_histogram(self, bin_size):
        """Returns a dictionary where keys are the bin, and the values
           are an array of the total cumulative probability prob and the count
           so that we have [prob, count]."""
        bins = {}
        # bins that give the total cumulative probability, and count of 
        # the number of occurrences
        for student in self.students:
            score_probabilities = student.get_score_probabilities()
            for (score, prob) in score_probabilities:
                current_bin = score // bin_size
                if current_bin in bins:
                    bins[current_bin][0] += prob
                    bins[current_bin][1] += 1 
                else:
                    bins[current_bin] = [prob, 1]
        return bins
 
class ComputeProbabilities:
    """Class for reading in the question results and creating students."""
    def __init__(self, question_results):
        self.question_results = question_results
	self.student_results = self._create_students()
        self.questions_students_dict = self._create_questions_students_dict()
        
        # hash of question_id : Question where the Questions have rj computed 
        self.questions = self.compute_rj(self)

    def _create_students(self):
        students = {}

        # students is a hash that stores a student id as a key and contains 
        # a StudentResult object
        for question in self.question_results:
            if question.student_id in students:
                # if studentResult for the id is already in the hash, change it.
                students[question.student_id].question_results[question.question_id] = question
                students[question.student_id].num_questions += 1
                if question.correct:
                    students[question.student_id].num_correct += 1
            else:
                # if the student id is not in the hash, create a new StudentResult object and add it
                if students[question.student_id].correct:
                    num_correct = 1
                else:
                    num_correct = 0
                stud_result = StudentResult({question.question_id : question}, question.student_id, num_correct, 1)
                students[question.student_id] = stud_result
        return students

    def _create_questions_students_dict(self):
        # creates a dictionary of all the questions, with the value of the dictionary 
        # being all of the students who were given that question in the training data.
        qs_dict = {}
        for student_id, student_result in self.student_results.iteritems():
            for question_result in student_result.question_results:
                # check if the question_id is already in the dictionary
                # and add the student id to the list accordingly
                if question_result.question_id in qs_dict:
                    qs_dict[question_result.question_id].append(student_result)
                else:
                    qs_dict[question_result.question_id] = [student_result]
        return qs_dict

    def compute_rj_uar_assumption(self):
        """Method which just takes the sample means, and uses these as the probabilities of getting
           a question correct."""
        question_list = {}
        for question_id, students_list in self.questions_students_dict:
            count = 0
            correct = 0
            for student in students_list:
                correct += student.question_results[question_id].correct
                count += 1
            rj = correct * 1.0 / count
            question = Question(question_id, rj)
            # add the question to the question_list hash
            question_list[question_id] = question
        return question_list 

    def compute_rj(self):
        """Method which iteratively computes the probability of a given question begin asked."""
        raise "Unimplemented"
 


class GreedyAssignment:
    def __init__(self, question_results, student_results):
        self.question_results = question_results
        self.student_results = student_results

def get_entropy(rj):
    return rj*math.log(1.0/rj)
