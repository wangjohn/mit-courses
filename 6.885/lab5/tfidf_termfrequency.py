import sys
from mrjob.protocol import JSONValueProtocol
from mrjob.job import MRJob
from term_tools import get_terms
import math

class MRTermFrequency(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol
    OUTPUT_PROTOCOL = JSONValueProtocol

    def mapper(self, key, data):
        yield data['term'], (data['mid'], data['word_count'], data['words_in_document'], data['sender'])

    def reducer(self, term, results):
        results = list(results)
        for result in results:
            mid, word_count, words_in_document, sender = result
            yield None, {'term': term, 'mid': mid, 'word_count': word_count, 'words_in_document': words_in_document, 'documents_with_word': len(results), 'tfidf': (float(word_count) / words_in_document) * math.log(516893.0 / len(results), 10), 'sender': sender}

if __name__ == '__main__':
        MRTermFrequency.run()
