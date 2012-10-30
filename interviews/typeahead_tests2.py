from typeahead_search2 import *
import timeit
import time
import random
import math

def randomly_generate_data(n):
    data_types = ["user", "topic", "question", "board"]
    output = []
    for i in xrange(n):
        dtype = data_types[random.randint(0,3)]
        did = str(i)
        score = random.random()
        string = get_random_string(score*1000000000)
        output.append(Data(dtype, did, score, string))
    return output

def get_random_string(number):
    number = int(number)
    output = []
    while number > 256:
        output.append(chr(number % 256))
        number = number // 256
    return ''.join(output)

def create_data_storage(n):
    data_store = DataStorage()
    for data in randomly_generate_data(n):
        data_store.add_data(data)
    return data_store

def test_querying(num_results, prefix, data_store):
    print "Num Results: " + str(num_results) + "; Prefix: " + prefix
    start_time = time.clock()
    results = data_store.query(num_results, prefix)
    print time.clock() - start_time 

def test_multiple_queries():
    data_store = create_data_storage(50000)
    test_querying(1500, "hello my", data_store)
    test_querying(4500, "j", data_store)
    test_querying(9500, "s", data_store)
    test_querying(15500, "basd", data_store)

def test_example_input():
    data_store = DataStorage()
    node1 = Data("user", "u1", 1, "Adam D'Angelo")
    node2 = Data("user", "u2", 1.0, "Adam Black")
    node3 = Data("topic", "t1", 0.8, "Adam D'Angelo")
    node4 = Data("question", "q1", 0.5, "What does Adam D'Angelo do at Quora?")
    node5 = Data("question", "q2", 0.5, "How did Adam D'Angelo learn programming?")
    data_store.add_data(node1)
    data_store.add_data(node2)
    data_store.add_data(node3)
    data_store.add_data(node4)
    data_store.add_data(node5)
    print data_store.query(10, "Adam")
    print data_store.query(10, "Adam D'A")
    print data_store.query(10, "Adam Cheever")
    print data_store.query(10, "LEARN how")
    print data_store.query(1, "lear H")
    print data_store.query(0, "lea")
    print data_store.wquery(10, 0, [], [], "Adam D'A")
    print data_store.wquery(2, 1, [("topic", 9.99)], [], "Adam D'A")
    data_store.delete_data('u2')
    print data_store.query(2, "Adam")


if __name__ == '__main__':
    #test_multiple_queries()
    test_example_input()
