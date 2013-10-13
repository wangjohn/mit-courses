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


print 'loading'
sc = SparkContext("local", "Simple App")
# Replace `lay-k.json` with `*.json` to get a whole lot more data.
lay = sc.textFile('s3n://AKIAJFDTPC4XX2LVETGA:<AWS KEY FROM PIAZZA>@6885public/enron/lay-k.json')

filtered_lay = lay.map(lambda x: json.loads(x)).filter(lambda x: x['sender'] in allowed_senders)

terms = lay.flatMap(lambda x: [{ 'term': term, 'mid': x['mid'] } for term in x['text'].lower().split('[\s,.]')]).cache()

frequencies = terms.reduceByKey(add)
print frequencies

doc_frequencies = terms.distinct().map(lambda x: x['term']).countByKey().map(lambda x: (x[0], math.log(x[1], 10)))
print doc_frequencies
