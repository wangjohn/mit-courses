import splay

def build_splay_tree(nodes):
    t = splay.SplayTree()
    for node in nodes:
        t.insert(node)
    return t

if __name__ == '__main__':
    t = build_splay_tree([6,5,4,3,2,1])
    print t.find_by_sequence([1]).key
    print t.find_by_sequence([1,1]).key
