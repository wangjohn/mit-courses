import rubik

def shortest_path(start, end):
    """
    Using 2-way BFS, finds the shortest path from start_position to
    end_position. Returns a list of moves. 
    Assumes the rubik.quarter_twists move set.
    """

    moves = rubik.quarter_twists

    # These dictionaries will have positions as keys, and
    # (parent_position, move_used_to_reach_position) as values. 
    start_parent = {} # For BFS starting at start
    end_parent = {}   # For BFS starting at end

    start_current_level_positions = set()
    end_current_level_positions = set()

    start_parent[start] = None
    start_current_level_positions.add(start)

    end_parent[end] = None
    end_current_level_positions.add(end)
    if end in start_parent: # Check if we're done.
        return calculate_path(start_parent, end_parent, end)

    for i in range(7):
        # Because we know the diameter is 14, we don't need more than
        # 7 iterations from each side.

        # Expand from start.
        start_next_level_positions = set()
        for position in start_current_level_positions:
            for move in moves:
                next_position = rubik.perm_apply(move, position)
                if next_position not in start_parent:
                    start_parent[next_position] = (position, move)
                    start_next_level_positions.add(next_position)
                    if next_position in end_parent: # Check if we're done.
                        return calculate_path(start_parent,
                                              end_parent,
                                              next_position)
        start_current_level_positions = start_next_level_positions

        # Expand from end.
        end_next_level_positions = set()
        for position in end_current_level_positions:
            for move in moves:
                next_position = rubik.perm_apply(move, position)
                if next_position not in end_parent:
                    end_parent[next_position] = (position, move)
                    end_next_level_positions.add(next_position)
                    if next_position in start_parent: # Check if we're done.
                        return calculate_path(start_parent,
                                              end_parent,
                                              next_position)
        end_current_level_positions = end_next_level_positions

    return None # There is no path from start to end

def calculate_path(start_parent, end_parent, position):
    """
    Assumes start_parent and end_parent are as specified in shortest_path.
    Assumes position is in both start_parent and end_parent.
    Returns a list of moves to get from start to end.
    """
    start_half = []
    current_position = position
    while(start_parent[current_position] is not None):
        pair = start_parent[current_position]
        parent_position = pair[0]
        move = pair[1]
        current_position = parent_position
        # move inserted at beginning, because we are walking back to start.
        start_half.insert(0, move)

    end_half = []
    current_position = position
    while(end_parent[current_position] is not None):
        pair = end_parent[current_position]
        parent_position = pair[0]
        move = pair[1]
        # Inverse is taken, because move wass originally away from end.
        inverse_move = rubik.perm_inverse(move)
        current_position = parent_position
        end_half.append(inverse_move)
    
    return start_half + end_half
