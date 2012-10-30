#!/usr/bin/python
# -*- coding: ascii -*-

from quora_typeahead_search import *

class PrefixNodeTester:
    def __init__(self):
        self.tests_failed = 0

    def create_data(self, data_list):
        output = []
        for i in data_list:
            new_data = Data(str(i), i, i, str(i))
            output.append(new_data)
        return output

    def test_addition_of_data(self):
        node = PrefixNode('')
        indices =  [2,10,3,2,10,3,10,3,3]
        new_data = self.create_data(indices)
        for data_obj in new_data:
            node.insert_new_data(data_obj)
        assert len(indices) == len(node.data)
        for i in [2,3,10]:
            assert len(node.data_by_type[str(i)]) == sum([1 for x in indices if x == i])
            

    def test_binary_search(self):
        node = PrefixNode('')
        # test binary search on indices without duplicates
        indices = [2,4,5,7,10,15,16,25,34,49]
        node.data = self.create_data(indices)
        for i in xrange(len(indices)):
            assert i == node._binary_search(indices[i], 0, len(node.data)-1, node.data)

        # test binary search on indices with duplicates
        indices.insert(4, 10)
        indices.insert(4, 10)
        indices.insert(4, 10)
        indices.insert(1, 4)
        node.data = self.create_data(indices)
        
        assert node._binary_search(10, 0, len(node.data)-1, node.data) in range(5,9)
        assert node._binary_search(4, 0, len(node.data)-1, node.data) in range(1,3)

    def run_all_tests(self):
        self.test_binary_search()
        self.test_addition_of_data()

class PrefixTreeTester:
    def __init__(self):
        self.tests_failed = 0

    def test_adding_nodes(self):
        prefix = 'hello'
        tree = PrefixTree()
        tree.add_prefix(prefix)
        node = tree.root
        for char in prefix:
            assert char in node.children
            node = node.children[char]
        assert tree.find_prefix(prefix).in_tree

    def test_deleting_nodes(self):
        prefix = 'hello'
        tree = PrefixTree()
        tree.add_prefix(prefix)
        tree.delete_prefix(prefix)
        assert len(tree.root.children) == 0

        tree.add_prefix(prefix)
        tree.add_prefix('bottle')
        tree.delete_prefix(prefix)
        assert len(tree.root.children) == 1
        assert tree.root.children['b']
        tree.delete_prefix('bottle')
        assert len(tree.root.children) == 0

    def test_total_merge(self):
        node_list = [[3,5,6,8,10],[4,5,10,22,34],[1,3,5,6,8]]
        tree = PrefixTree()
        result = tree._total_merge(node_list, 100)
        expected = [x for y in node_list for x in y]
        expected.sort()
        assert expected == result

        node_list = [[3,5,6,8,10],[4,5,10,22,34],[1,3,5,6,8],[1,2,3,4,5,6,7,8,9],[5,7,8,9,10,11]]
        result = tree._total_merge(node_list, 100)
        expected = [x for y in node_list for x in y]
        expected.sort()
        assert expected == result

    def test_querying_nodes(self):
        tree = PrefixTree()
        node1 = Data("user", "u1", 1, "Adam D'Angelo")
        node2 = Data("user", "u2", 1.0, "Adam Black")
        node3 = Data("topic", "t1", 0.8, "Adam D'Angelo")
        node4 = Data("question", "q1", "0.5", "What does Adam D'Angelo do at Quora?")
        node5 = Data("question", "q2", 0.5, "How did Adam D'Angelo learn programming?")
        tree.add_data(node1)
        tree.add_data(node2)
        tree.add_data(node3)
        tree.add_data(node4)
        tree.add_data(node5)
        print tree.query(10, "Adam")
        print tree.query(10, "Adam D'A")
        print tree.query(10, "Adam Cheever")
        
    def run_all_tests(self):
        self.test_adding_nodes()
        self.test_deleting_nodes()
        self.test_total_merge()
        self.test_querying_nodes()

if __name__ == '__main__':
    tree_tester = PrefixTreeTester()
    tree_tester.run_all_tests()

    node_tester = PrefixNodeTester()
    node_tester.run_all_tests()

     
