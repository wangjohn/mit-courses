"""In order to obtain fast query performance, we need to be able to merge extremely quickly among an arbitrary set of children."""

class Data:
    def __init__(self, data_type, data_id, score, data_string):
        self.data_type = data_type
        self.data_id = data_id
        self.score = score
        self.data_string = data_string
        self.boosted_score = None

    def get_boosted_score(self, weights):
        """Boosts the score, and temporarily stores the boosted score
        in the self.boosted_score variable. Make sure that the boosted
        score is cleared after you are finished with the
        calculations using the boosted scores"""
        # we could do reduce(mul, weights), but this is slower than 
        # the for loop
        self.boosted_score = self.score
        for weight in weights:
            self.boosted_score *= weight
        return self.boosted_score

    def clear_boosted_score(self):
        self.boosted_score = None

class PrefixNode:
    """This node object is a node in the PrefixTree. It stores data
    in three different ways:

        self.data - a list of all the data objects in this prefix node,
        sorted by score, breaking ties by how recently that data object
        was added to the structure.
        
        self.data_by_id - a hash keyed on id's of the data objects.

        self.data_by_type - a hash keyed on the types of the data 
        objects. Each data type in the hash has a list of data 
        objects with that type, sorted by score, breaking ties 
        by how recently objects were added.
    """

    def __init__(self, char, in_tree=False):
        self.char = char
        self.children = {}
        self.data = []
        self.data_by_id = {}
        self.data_by_type = {}
        self.in_tree = in_tree

    def insert_new_data(self, new_data):
        """Inserts a new data object into the data structure. The
        new data_id cannot conflict with any data_id that is already
        in the structure."""
        self.data_by_id[new_data.data_id] = new_data
        # binary search insertion into the array so we always have
        # a sorted list of data
        insertion_index = self._get_insertion_index(new_data.score, self.data)
        self.data.insert(insertion_index, new_data)

        # sort the data by type lists as well
        if new_data.data_type in self.data_by_type:
            type_index = self._get_insertion_index(new_data.score, self.data_by_type[new_data.data_type])
            self.data_by_type[new_data.data_type].insert(type_index, new_data)
        else:
            self.data_by_type[new_data.data_type] = [new_data]

    def _get_insertion_index(self, score, array):
        """Helper method for identifying where to insert a score into 
        the array, making sure to put it at the front of the sublist
        of non-unique scores in the array."""
        index = self._binary_search(score, 0, len(array)-1, array)
        # move all the way to the left, and insert at the front of 
        # the sublist with equal values
        while index > 0 and array[index-1].score == score:
            index -= 1
        return index

    def _binary_search(self, key, start, end, array):
        mid = start + ((end - start) // 2)
        if end <= start:
            return start
        if array[mid].score > key:
            return self._binary_search(key, start, mid-1, array)
        elif array[mid].score < key:
            return self._binary_search(key, start+1, end, array)
        else:
            return mid

    def delete_data(self, data_id):
        """Method which deletes a given data_id from the structure. 
        If the data_id is not in the data structure, this method
        will do nothing."""
        item = self.data_by_id[data_id] 
        # make sure the item is stored in the structure
        if not item:
            return 

        # delete from all the lists
        del self.data_by_id[data_id]
        self.delete_from_list(item, self.data)
        self.delete_from_list(item, self.data_by_type[item.data_type])

    def _delete_from_list(self, item, array):
        """Helper method which deletes an item from an array. Finds 
        the item through binary search then scanning."""
        item_score = item.score
        index = self._binary_search(item_score, 0, len(array)-1, array)
        if array[index] == item:
            array.pop(index)
            return
        # otherwise move left and search for the item
        while counter > 0 and array[counter-1].score == item_score:
            counter -= 1
            if array[counter] == item:
                array.pop(counter)
                return
        # finally finish it off by moving right
        counter = index
        while counter < len(array)-1 and array[counter+1].score == item_score:
            counter += 1
            if array[counter] == item:
                array.pop(counter)
                return

class PrefixTree:
    def __init__(self):
        self.root = PrefixNode('', True)
        self.data_ids = {}
    
    def find_prefix(self, prefix):
        """Returns a node in the prefix tree which contains 
        the prefix's data, or None if there is no such node.
        """
        node = self.root
        for char in prefix:
            # follow all the way down the tree unless we find a char which isn't in
            # the tree, then return None
            if char in node.children: 
                node = node.children[char]
            else:
                return None 
        return node

    def add_data(self, new_data):
        prefix = new_data.data_string
        node = self.add_prefix(prefix)
        node.insert_new_data(new_data)
        self.data_ids[new_data.data_id] = new_data

    def delete_data(self, data_id):
        if self.data_ids[data_id]:
            node = self.data_ids[data_id]
            del self.data_ids[data_id]
            node.delete_data(data_id)

    def query(self, num_results, prefix):
        top_node = self.find_prefix(prefix)
        children = self._get_all_children(top_node)
        node_list = [child.data for child in children]
        # use a heuristic to figure out whether we want to do a total merge,
        # or whether we want to use a heap.
        if 

    def _total_merge(self, node_list, num_results):
        """Merges all of the node lists together into a single sorted
        list of data objects"""
        node_list_len = len(node_list)
        if node_list_len == 1:
            return node_list[0]
        elif node_list_len == 2:
            # go through a standard merge procedure
            left_counter = 0
            right_counter = 0
            output = []
            # keep looping until we reach the end of the lists, or until we reach the total number of results
            while left_counter < len(node_list[0]) or right_counter < len(node_list[1]) and len(output) < num_results:
                if left_counter >= len(node_list[0]):
                    output.extend(node_list[1][right_counter:])
                    return output
                elif right_counter >= len(node_list[1]):
                    output.extend(node_list[0][left_counter:])
                    return output
                elif get_score(node_list[0][left_counter]) < get_score(node_list[1][right_counter]): 
                    output.append(node_list[0][left_counter])
                    left_counter += 1
                else:
                    output.append(node_list[1][right_counter])
                    right_counter += 1
            return output
        else:
            # break the node_list apart and recursively call total_merge
            left_list = node_list[:(node_list_len//2)]
            right_list = node_list[(node_list_len//2):]
            left_output = self._total_merge(left_list, num_results)
            right_output = self._total_merge(right_list, num_results)
            return self._total_merge([left_output, right_output], num_results)

    def _heap_merge(self, node_list, num_results):
        """Merges the lists together using a priority queue which
        always gets the smallest element from the items."""
        indices = [0 for i in xrange(len(node_list))]
        finished_lists = {}
        starting_list = []
        for i in xrange(len(node_list)):
            starting_list.append(node_list[i][0])
        heap = MinHeap(starting_list)
        
        output = []
        while len(output) < num_results and node_list:
            current_min, list_index = heap.delete_min()
            output.append(current_min)
            indices[list_index] += 1
            if indices[list_index] < len(num_results[list_index]):
                new_node = node_list[list_index][indices[list_index]]
                heap.insert(new_node, list_index)
            else:
                finished_lists[list_index] = True
                if len(finished_lists) == len(num_results):
                    return output
        return output

    def _get_all_children(self, node):
        """Does a DFS to search for all nodes in the tree under
        the node given."""
        output_nodes = []
        for child_node in node.children.itervalues():
            if child_node.in_tree:
                output_nodes.append(child_node)
            output_nodes.extend(self._get_all_children(child_node))
        return output_nodes

    def add_prefix(self, prefix):
        node = self.root
        for i in xrange(len(prefix)):
            char = prefix[i]
            if char in node.children:
                node = node.children[char]
            else:
                if i == len(prefix) - 1:
                    new_node = PrefixNode(char, True)
                else:
                    new_node = PrefixNode(char, False)
                node.children[char] = new_node
                node = new_node
        return node

    def delete_prefix(self, prefix):
        node = self.root
        path = []
        for char in prefix:
            if char in node.children:
                path.append(node)
                node = node.children[char]
            else:
                break
        # go backwards on the path and delete all traces of the prefix.
        # also clean up afterwards so we don't have any hanging paths.
        path.reverse()
        node = path[0]
        del node.children[prefix[-1]]
        for i in xrange(1, len(path)):
            last_node = path[i-1]
            node = path[i]
            if len(last_node.children) == 0 and not last_node.in_tree:
                del node.children[last_node.char] 

def get_score(input_val):
    if isinstance(input_val, int):
        return integer

class MinHeap:
    def __init__(self, starting_data):
        self.size = len(starting_data)
        self.heap = starting_data
        self.node_ids = {}
        self._build_heap()

    def _heapify(self, index):
        l = 2*index
        r = 2*index+1
        if l <= self.size and get_score(self.heap[l]) < get_score(self.heap[index]):
            smallest = l
        else:
            smallest = index
        if r <= self.size and get_score(self.heap[r]) < get_score(self.heap[smallest]):
            smallest = r
        if largest != index:
            self.heap[smallest], self.heap[index] = self.heap[index], self.heap[smallest]
            self._heapify(smallest)

    def _build_heap(self):
        for i in xrange(len(self.heap)):
            node = self.heap[i]
            self.node_ids[node.data_id] = i
        for i in xrange(self.size//2,0,-1):
            self._heapify(i)

    def insert(self, node, list_index):
        if len(self.heap) >= self.size:
            # do nothing, the heap is already full
            return None
        self.node_ids[node.data_id] = list_index
        self.heap.append(node)
        # sift upwards
        index = len(self.heap)-1
        parent_index = index//2
        while get_score(self.heap[parent_index]) > get_score(self.heap[index]):
            self.heap[parent_index], self.heap[index] = self.heap[index], self.heap[parent_index]
            index = parent_index
            parent_index = index//2
        return index

    def delete_min(self):
        self.heap[-1], self.heap[0] = self.heap[0], self.heap[-1]
        min_node = self.heap.pop()
        list_index = self.node_ids[min_node.data_id]
        del self.node_ids[min_node.data_id]
        self._heapify(0)
        return (min_node, data_id)

    def add_node_and_remove_min(self, node):
        """Method adds node into the heap will removing and returning the minimum element."""
        min_node = self.delete_min()
        self.insert(node)
        return min_node
        
