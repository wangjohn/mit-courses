a = ['99', 'f0', '11', '31', '3f', 'f6', '9d', '52']
b = ['89', 'fa', '1f', '34', '38', 'eb', '8c', '59']

letter_frequency = {
    'a': 8.1, 
    'b': 1.5, 
    'c': 2.8, 
    'd': 4.3,  
    'e': 12.7,
    'f': 2.2,
    'g': 2.0,
    'h': 6.1,
    'i': 7.0,
    'j': 0.1,
    'k': 0.8,
    'l': 4.0,
    'm': 2.4,
    'n': 6.7,
    'o': 7.5,
    'p': 1.9,
    'q': 0.1,
    'r': 6.0,
    's': 6.3,
    't': 9.1,
    'u': 2.8,
    'v': 1.0,
    'w': 2.3,
    'x': 0.2,
    'y': 1.9,
    'z': 0.1
}



def all_pairs():
    pair_map = {}
    for i in xrange(256):
        for j in xrange(256):
            val = i ^ j
            if val in pair_map:
                pair_map[val].append((i,j))
            else:
                pair_map[val] = [(i,j)]
    return pair_map

def decrypt(a, b):
    xored = []
    for i in zip(a,b):
        xored.append(int(i[0], 16) ^ int(i[1], 16))

    possible_pairs = []
    pair_map = all_pairs()
    for val in xored:
        possible_pairs.append(pair_map[val])

    new_possible_pairs = []
    for pairs in possible_pairs:
        sorted_pairs = parse_pairs(pairs)
        sorted_pairs = [(chr(i[0]), chr(i[1])) for i in sorted_pairs] 
        new_possible_pairs.append(sorted_pairs)
    
    return new_possible_pairs

def parse_pairs(pairs):
    parsed = []
    for pair in pairs:
        if letter(pair[0]) and letter(pair[1]):
            parsed.append(pair)

    parsed = sorted(parsed, key=lambda pair : prob(pair), reverse=True)
    return parsed

def prob(pair):
    return letter_frequency[chr(pair[0]).lower()] * letter_frequency[chr(pair[1]).lower()]

def letter(number):
    #return (65 <= number and number <= 90) or (97 <= number and number <= 122)
    return (97 <= number and number <= 122)

for result in decrypt(a,b):
    print result
