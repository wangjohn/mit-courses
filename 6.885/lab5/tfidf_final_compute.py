import sys
from mrjob.protocol import JSONValueProtocol
from mrjob.job import MRJob
from term_tools import get_terms
import math

allowed_senders = set([
    'kenneth.lay@enron.com',
    'jeff.skilling@enron.com',
    'andrew.fastow@enron.com',
    'rebecca.mark@enron.com'
     ])

class MRTfIdf(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol
    OUTPUT_PROTOCOL = JSONValueProtocol

    def mapper(self, key, data):
        if data['sender'] in allowed_senders:
            yield data['term'], (data['tfidf_sum'], data['tfidf_count'])

    def reducer(self, term, results):
        total_sum = 0
        total_count = 0
        for result in results:
            current_sum, current_count = result
            total_sum += current_sum
            total_count += current_count
        tfidf = float(total_sum) / float(total_count)
        yield tfidf, {'tfidf': tfidf, 'term': term}

if __name__ == '__main__':
        MRTfIdf.run()
