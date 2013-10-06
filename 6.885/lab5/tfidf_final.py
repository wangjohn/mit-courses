import sys
from mrjob.protocol import JSONValueProtocol
from mrjob.job import MRJob
from term_tools import get_terms

class MRTfIdf(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol
    OUTPUT_PROTOCOL = JSONValueProtocol

    def mapper(self, key, data):
        yield (data['sender'], data['term']), data['tfidf']

    def reducer(self, key, results):
        sender, term = key
        tfidf_sum = 0
        tfidf_count = 0
        for result in results:
            tfidf_sum += result
            tfidf_count += 1
        tfidf_average = float(tfidf_sum) / tfidf_count
        yield (sender, term, tfidf_average), {'sender': sender, 'term': term, 'tfidf': tfidf_average, 'tfidf_sum': tfidf_sum, 'tfidf_count': tfidf_count}

if __name__ == '__main__':
        MRTfIdf.run()
