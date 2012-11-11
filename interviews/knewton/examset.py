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
        return self.num_correct*1.0 / self.num_questions

class Question:
    def __init__(self, question_id, rj):
        self.question_id = question_id
        self.rj = rj
        self.entropy = get_entropy(self.rj) + get_entropy(1 - self.rj) 

class Student:
    def __init__(self, questions):
        self.questions = questions
        self.k = len(self.questions)
        self.score_probabilities = None

    def get_score_dispersion(self):
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
        if not self.score_probabilities:
            self.score_probabilities = self._exponential_recursion(0, [(0,1)])
        return self.score_probabilities

    def _exponential_recursion(self, i, score_prob):
        current_rj = self.questions[i].rj 
        new_score_prob = []
        for score, prob in score_prob:
            new_score = score + 1.0/current_rj
            incorrect = (score, prob*(1.0-current_rj))
            correct = (new_score, prob*1.0*current_rj)
            new_score_prob.append(incorrect)
            new_score_prob.append(correct)
        if i+1 < len(self.questions):
            return self._exponential_recursion(i+1, new_score_prob)
        else:
            return new_score_prob

    def get_score_probabilities_approx(self):
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
    def __init__(self, student_list, bin_size=None):
        self.students = student_list
        self.entropy = None
        self.bins = None
        if bin_size:
            self.bin_size = bin_size
        else:
            self.bin_size = self.compute_bin_size(student_list)


    def compute_bin_size(self, students):
        max_disp = None
        for student in students:
            disp = student.get_score_dispersion()
            if max_disp == None or disp > max_disp:
                max_disp = disp
        self.bin_size = max_disp * 1.0 / 2
        return self.bin_size

    def compute_entropy(self):
        if self.entropy:
            return self.entropy
        if not self.bins:
            self.bins = self.build_histogram(self.bin_size)
        entropy = 0
        for (score, prob_array) in self.bins:
            avg_prob = prob_array[0] * 1.0 / prob_array[1]
            entropy += get_entropy(avg_prob)
        self.entropy = entropy
        return entropy

    def build_histogram(self, bin_size):
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

def get_entropy(rj):
    return rj*math.log(1.0/rj)
