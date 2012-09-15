class Node:

    def __init__(self, key):
        self.key = key
        self.left = self.right = None
        self.depth = 0

    def __str__(self):
        if self.key == None:
            return ''
        else:
            return str(self.key)

    # assuming there are no duplicate keys
    def insert(self, node):
        if node.key < self.key:
            if self.left == None:
                node.depth = self.depth + 1
                self.left = node
            else:
                self.left.insert(node)
        elif node.key > self.key:
            if self.right == None:
                node.depth = self.depth + 1
                self.right = node
            else:
                self.right.insert(node)

class Tree:

    def __init__(self):
        self.root = Node(None)
        self.depth = 0
        self.max_key_length = 0

    def __str__(self):
        output = ''
        nodes = [self.root]
        counter = 0
        total_tree_width = 2**(self.depth)*self.max_key_length
        while counter <= self.depth:
            width = total_tree_width / 2**(counter) + 1
            new_node_list = []
            for node in nodes:
                if node == None:
                    string_char = ""
                    new_node_list.extend([None, None])
                else:
                    string_char = str(node)
                    new_node_list.append(node.left)
                    new_node_list.append(node.right)
                output += string_char.center(width)        
            counter += 1
            output += "\n"
            nodes = new_node_list
        return output

    def insert(self, node):
        if self.root == None:
            self.root = node
        else:
            self.root.insert(node)
        if self.max_key_length < len(str(node.key)):
            self.max_key_length = len(str(node.key))
        if self.depth < node.depth:
            self.depth = node.depth

def round_power_of_two(x):
    power = 0
    while 2**(power) < x:
        power += 1
    return 2**(power)

if __name__ == '__main__':
    t = Tree()
    for i in xrange(2,-1,-1):
        t.insert(Node(i))
    print str(t)
