
class Data:
    def __init__(self, data_type, data_id, score, data_string):
        self.data_type = data_type
        self.data_id = data_id
        self.score = score
        self.data_string = data_string
        self.boosted_score = None

    def get_boosted_score(self, weights):
        """Boosts the score, and temporarily stores the boosted score
            in the self.boosted_score variable. Make sure that the boosted
            score is cleared after you are finished with the
            calculations using the boosted scores"""
        # we could do reduce(mul, weights), but this is slower than 
        # the loop
        self.boosted_score = self.score
        for weight in weights:
            self.boosted_score *= weight
        return self.boosted_score

    def clear_boosted_score(self):
        self.boosted_score = None


class DataStorage:
    def __init__(self):
        self.strings = {}
