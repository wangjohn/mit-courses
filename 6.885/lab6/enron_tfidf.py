from pyspark import SparkContext
from operator import add

import re
import json
import time
import math

allowed_senders = set([
    'kenneth.lay@enron.com',
    'jeff.skilling@enron.com',
    'andrew.fastow@enron.com',
    'rebecca.mark@enron.com'
    ])

senders_regex = re.compile(r"(kenneth\.lay|jeff\.skilling|jeff\.skilling|andrew\.fastow|rebecca\.mark)")

def get_terms(text):
    pattern = re.compile(r"[\s\w]")
    return pattern.split(text.lower())

def compute_sender_term_count(sender, text):
    terms = get_terms(text)
    for term in terms:
        yield (sender, term), 1.0

def compute_sender_term_frequency(term_count, total):
    return float(term_count) / total

def get_id_term_pair(doc_id, text):
    terms = get_terms(text)
    for term in terms:
        yield doc_id, term

def compute_idf(term, count):
    return term, math.log( 516893.0 / float(count), 10)

def is_valid_sender(sender):
    return re.search(senders_regex, sender)

print 'loading'
sc = SparkContext("local", "Simple App")
# Replace `lay-k.json` with `*.json` to get a whole lot more data.
lay = sc.textFile('s3n://AKIAJFDTPC4XX2LVETGA:lJPMR8IqPw2rsVKmsSgniUd+cLhpItI42Z6DCFku@6885public/enron/lay-k.json')
lay = lay.map(lambda x: json.loads(x))

sender_term_counts = lay.filter(lambda x: is_valid_sender(x['sender'])) \
                        .flatMap(lambda x: compute_sender_term_count(x['sender'], x['text'])) \
                        .reduceByKey(add)

print 'sender term counts'
print sender_term_counts.take(5)

sender_totals = sender_term_counts.map(lambda x: (x[0][0], x[1])).reduceByKey(add).collectAsMap()
sender_term_frequencies = sender_term_counts.map(lambda x: (x[0], compute_sender_term_frequency(x[1], sender_totals[x[0][0]])))

print 'found sender term frequencies'
print sender_term_frequencies.take(5)

print lay.flatMap(lambda x: get_id_term_pair(x['mid'], x['text'])).distinct().take(5)
document_counts = lay.flatMap(lambda x: get_id_term_pair(x['mid'], x['text'])).distinct().map(lambda x: (x[1], 1.0)).reduceByKey(add)
print document_counts.take(20)
document_idfs = document_counts.map(lambda x: compute_idf(x[0], x[1]))

print 'found document idfs'
print document_idfs.take(5)
document_idfs = document_idfs.collectAsMap()
tfidfs = sender_term_frequencies.map(lambda x: (x[0], x[1]*document_idfs[x[0][1]])) \
                                .groupBy(lambda x: x[0][0]) \
                                .map(lambda x: (x[0], sorted(x[1], key=lambda j: j[1], reverse=True)[:10]))

prin 'finished computing tfidfs'

for sender, results in tfidfs.collect():
    print ''
    print '------------------------'
    print sender
    for term, tfidf in results:
        print term, tfidf

