
def BibInsert(tree, x):
    if global_min == null || x < global_min:
        global_min = x
    if tree.u == 2:
        tree.A[x] = 1
    else:
        BibInsert(tree.blocks[high(x)], low(x))
        BibInsert(tree.summary, high(x))

def BibMin(tree):
    if tree.u == 2:
        if tree.A[0] == 1:
            return 0
        elif tree.A[1] == 1:
            return 1
        else:
            return null
    else:
        i = BibMin(tree.summary)
        if i == null:
            return null
        else :
            j = BibMin(tree.blocks[i])
            return index(i,j)

def BibSuccessor(tree, x):
    if tree.u == 2:
        if x == 0 and tree.A[1] == 1:
            return 1
        else:
            return null
    else:
        i = BibSuccessor(tree.blocks[high(x)], low(x))
        if i == null:
            return index(high(x), i)
        else:
            i = BibSuccessor(tree.summary, high(x))
            if i == null:
                return null
            else:
                j = BibMin(tree.blocks[i])
                return index(i,j)

def BibDelete(tree, x):
    if tree.u == 2:
        tree.A[x] = 0
        if x == global_min:
            global_min = BibMin(tree)
    else:
        BibDelete(tree.blocks[high(x)], low(x))
        if tree.blocks[high(x)][0] is empty and 
                BibSuccessor(tree.blocks[high(x)], 0) == null:
            BibDelete(tree.summary, high(x))
        if x == global_min:
            global_min = BibMin(tree)





def BibInsert(tree, x):
    if tree is empty:
        tree.min = tree.max = x
        return
    if x < tree.min:
        x, tree.min = tree.min, x
    if x > tree.max:
        x, tree.max = tree.max, x
    if v.summary[high(x)] == 0:
        BibInsert(v.summary, high(x))
    BibInsert(v.blocks[high(x)], low(x))

def BibMin(tree):
    return tree.min

def BibDelete(tree, x):
    if tree is empty or x < tree.min or x > tree.max:
        return null
    if x == tree.min
        s = tree.summary.min
        if s == null: 
            tree.min = tree.max
        else:
            tree.min = tree.bocks[s].min
            BibDelete(tree.bocks[s], tree.min)
            if tree.bocks[s].min == null:
                BibDelete(tree.summary, s)
    elif x == tree.max:
        do the same but opposite
    else:
        BibDelete(s.bocks[high(x)], low(x))
        if S.blocks[high(x)].min == null:
            BibDelete(tree.summary, high(x))
            BibDelete(tree.blocks, low(x))


T(n) = 2 T(sqrt(n)) + 1
Let S(k) = T(2^k) = T(n), then
S(k) = 2 S(k/2) + 1
S(k) = O(k lg k)
lg n = k 
T(n) = O(lg n lg lg n)



