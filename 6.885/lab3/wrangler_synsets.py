import csv

with open('synsets_command.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    words = {}
    count = 0
    for row in reader:
        word = row[0].strip()
        words[word] = True
        count += 1

    print len(words)
    print count
