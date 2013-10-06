import sys
from mrjob.protocol import JSONValueProtocol
from mrjob.job import MRJob
from term_tools import get_terms

class MRWordCount(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol
    OUTPUT_PROTOCOL = JSONValueProtocol

    def mapper(self, key, email):
        email_terms = get_terms(email['text'])
        for term in email_terms:
            yield (term, email['mid']), (1, len(email_terms), email['sender'])

    def reducer(self, term, values):
        count = 0
        total = 0
        for value in values:
            subcount, total, sender = value
            count += subcount
        yield None, {'term': term[0], 'mid': term[1], 'word_count': count, 'words_in_document': total, 'sender': sender}

if __name__ == '__main__':
        MRWordCount.run()
