from pyspark import SparkContext
from operator import add

import json
import time
import math

allowed_senders = set([
    'kenneth.lay@enron.com',
    'jeff.skilling@enron.com',
    'andrew.fastow@enron.com',
    'rebecca.mark@enron.com'
    ])

def get_terms(text)
    return text.lower().split('[\s,.]')

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
    return term, math.log(count, 10)

print 'loading'
sc = SparkContext("local", "Simple App")
# Replace `lay-k.json` with `*.json` to get a whole lot more data.
lay = sc.textFile('s3n://AKIAJFDTPC4XX2LVETGA:<AWS KEY FROM PIAZZA>@6885public/enron/lay-k.json')
lay = lay.map(lambda x: json.loads(x))

sender_term_counts = lay.filter(lambda x: x['sender'] in allowed_senders)
                        .map(lambda x: compute_sender_term_count(x['sender'], x['text']))
                        .reduceByKey(add)
sender_totals = sender_term_counts.map(lambda x: (x[0][0], x[1])).reduceByKey(add).cache()
sender_term_frequencies = sender_term_counts.map(lambda x: (x[0], compute_sender_term_frequency(x[1], sender_totals[x[0][0]])))

document_counts = lay.map(lambda x: get_id_term_pair(x['mid'], x['text'])).distinct().map(lambda x: (x[1], 1.0)).reduceByKey(add)
document_idfs = document_counts.map(lambda x: compute_idf(term, count))

tfidfs = sender_term_frequencies.map(lambda x: (x[0], x[1]*document_idfs[x[0][1]]))
                                .groupBy(lambda x: x[0][0])
                                .map(lambda x: (x[0], sorted(x[1], reverse=True)[:10]))

for sender, results in tfidfs.collect():
    print ''
    print '------------------------'
    print sender
    for term in results
        print term

