class QuestionResult:
    def __init__(self, question_id, student_id, correct):
        self.question_id = question_id
        self.student_id = student_id
        self.correct = correct

class StudentResult:
    def __init__(self, question_results, student_id, num_correct, num_questions):
        self.question_results = question_results
        self.student_id = student_id
        self.num_correct = num_correct
        self.num_questions = num_questions
        self.theta = 0

    def percentage_correct():
        return self.num_correct * 1.0 / self.num_questions

class Question:
    def __init__(self, question_id, rj):
        self.question_id = question_id
        self.rj = rj
        self.entropy = get_entropy(self.rj) + get_entropy(1 - self.rj) 

class Student:
    def __init__(self, questions, k=5):
        self.questions = questions
        self.k = k
        self.score_probabilities = None

    def get_score_probabilities(self):
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
    def __init__(self, num_students):
        self.students = [None for i in xrange(num_students)]
        self.entropy = None

    def compute_entropy(self):
        total_score_probabilities = []
        for student in self.students:
            student.score_probabilities

def get_entropy(rj):
    return rj*math.log(1.0/rj)

