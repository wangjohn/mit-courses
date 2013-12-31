def BFS_Aug(s, Adj, ER, k):
    level = {s: 0}
    parent = {s: None}
    max_strength = {s: 1}
    i = 1
    frontier = [s]
    while frontier:
        next_list = []
        next_l2 = []
        for u in frontier:
            for v in Adj[u]:
                if v not in level:
                    level[v] = i
                    parent[v] = u
                    max_strength(v) = ER(u,v) * max_strength(u)
                    next_list.append(v)
                if ER(u, v)*max_strength(u) > max_strength(v):
                    max_strength(v) = ER(u,v) * max_strength(u)
                    next_list.append(v)
            if i <= k:
                frontier = next_list
            else:
                frontier = []
            i += 1
            
