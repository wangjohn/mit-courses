import rubik

def shortest_path(start, end):
    """
    Using 2-way BFS, finds the shortest path from start_position to
    end_position. Returns a list of moves. 

    You can use the rubik.quarter_twists move set.
    Each move can be applied using rubik.perm_apply
    """

    moves = rubik.quarter_twists

    parentS = {}
    parentE = {}
    parentS[start] = None
    parentE[end] = None

    start_current_positions = set()
    end_current_positions = set()
    start_current_positions.add(start)
    end_current_positions.add(end)

    if end in parentS:
        return get_moves(parentS, parentE, end)

    for i in range(7):
        start_next_positions = set()
        for position in start_current_positions:
            for move in moves:
                next_position = rubik.perm_apply(move, position)
                if next_position not in parentS:
                    parentS[next_position] = (position, move)
                    start_next_positions.add(next_position)
                    if next_position in parentE:
                        return get_moves(parentS,
                                              parentE,
                                              next_position)
                    
        start_current_positions = start_next_positions
        end_next_positions = set()
        for position in end_current_positions:
            for move in moves:
                next_position = rubik.perm_apply(move, position)
                if next_position not in parentE:
                    parentE[next_position] = (position, move)
                    end_next_positions.add(next_position)
                    if next_position in parentS:
                        return get_moves(parentS,
                                              parentE,
                                              next_position)

        end_current_positions = end_next_positions

    return None

def get_moves(parentS, parentE, position):
    start_moves = []
    current_position = position
    while parentS[current_position] is not None:
        (current_position, move) = parentS[current_position]
        start_moves.insert(0, move)

    end_moves = []
    current_position = position
    while parentE[current_position] is not None:
        (current_position, move) = parentE[current_position]
        end_moves.append(rubik.perm_inverse(move))
    
    return start_moves + end_moves

    
