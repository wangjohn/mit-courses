
def minreplace():
    BST = BinarySearchTree()
    for i in range(n):
        NewNode = BSTNode()
        NewNode.key = A[i]
        NewNode.left = i - 1
        NewNode.right = i + 1
        BST.insert(NewNode)
    
    lakes = []
    while BST.empty() == False:
        m = BST.PopMin()
        l = m.left
        r = m.right
        if not (BST.isMinIndex(l) || BST.isMaxIndex(r)):
            nextmin = min(A[l], A[r])
            while A[l] == nextmin:
                BST.remove(A[l])
                l = l - 1
            while A[r] == nextmin:
                BST.remove(A[r])
                r = r + 1
            NewNode = BSTNode()
            NewNode.key = nextmin
            NewNode.left = l
            NewNode.right = r
            BST.insert(NewNode)
            lakes.append((l,r))

    max_objective = 0 
    best_lake = None
    for (l, r) in lakes:
        if ObjectiveFunction(l, r) > max_objective:
            max_objective = ObjectiveFunction(l, r)
            best_lake = (l, r)
    
    return (l,r)

def ObjectiveFunction(l, r):
    return r-l-1-(1/100)*min(A[l], A[r])

