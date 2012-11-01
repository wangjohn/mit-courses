"""
A set of utility functions for reading in the data format used by Keith T.
Poole on voteview.com.

You can download additional data that will work with these functions, for
any Congress going back to the 1st, on that site.
"""
import csv
from copy import deepcopy

def legislator_info(legislator):
    district = ''
    if legislator['district'] > 0: district = '-%s' % legislator['district']
    return "%s (%s%s)" % (legislator['name'], legislator['state'], district)

def vote_info(vote):
    if not vote['name']: return vote['number']
    return "%s: %s" % (vote['number'], vote['name'])

def is_interesting(vote):
    return (vote['name'] != '')

def title_case(str):
    chars = list(str)
    chars[0] = chars[0].upper()
    for i in range(1, len(chars)):
        if chars[i-1] not in ' -': chars[i] = chars[i].lower()
    return ''.join(chars)

state_codes = {}
f = open('states.dat')
for line in f:
    state_codes[int(line[0:2])] = title_case(line[6:].strip())
f.close()

party_codes = {}
f = open('party3.dat')
for line in f:
    party_codes[int(line[2:6])] = line[8:].strip()
f.close()

def vote_meaning(n):
    if n in [1, 2, 3]: return 1
    elif n in [4, 5, 6]: return -1
    else: return 0

def read_congress_data(filename):
    """
    Reads a database of Congressional information in the format that comes
    from Keith T. Poole's voteview.com.
    """
    f = open(filename)
    legislators = []
    for line in f:
        line = line.rstrip()
        person = {}
        person['state'] = state_codes[int(line[8:10])]
        person['district'] = int(line[10:12])
        person['party'] = party_codes[int(line[19:23])]
        name = line[25:36].strip()
        person['name'] = title_case(name.replace("  ", ", "))
        person['votes'] = [vote_meaning(int(x)) for x in line[36:]]
        legislators.append(person)
    f.close()
    return legislators

def read_vote_data(filename):
    """
    Reads a CSV file of data on the votes that were taken.
    """
    f = open(filename)
    csv_reader = csv.reader(f)
    votes = []
    for row in csv_reader:
        if row[0] == "date":
            continue # first line with column headers
        vote = {}
        vote['date'] = row[0]
        vote['id'] = str(row[2])
        if vote['id'] == '':
            vote['id'] = str(len(votes))
        vote['number'] = row[3]
        vote['motion'] = row[4]
        vote['name'] = row[6]
        vote['result'] = row[5]
        votes.append(vote)
    f.close()
    return votes

def limit_votes(legislators, votes, n):
    indices = [i for i in xrange(len(legislators[0]['votes'])-1, -1, -1) if
    is_interesting(votes[i])][:n]

    newleg = []
    for leg in legislators:
        leg = deepcopy(leg)
        leg['votes'] = [leg['votes'][i] for i in indices]
        found_any_votes = False
        for vote in leg['votes']:
            if vote != 0:
                found_any_votes = True
                break
        if found_any_votes: newleg.append(leg)
    newvotes = [votes[i] for i in indices]
    return newleg, newvotes
