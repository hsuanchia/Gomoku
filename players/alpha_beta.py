import random
from core.rule import get_win_line


def count_in_direction(grid, x, y, dx, dy, player):
    """Count consecutive stones of player in direction (dx, dy) from (x, y)."""
    size = len(grid)
    count = 0
    nx, ny = x + dx, y + dy
    while 0 <= nx < size and 0 <= ny < size and grid[ny][nx] == player:
        count += 1
        nx += dx
        ny += dy
    return count


def evaluate(grid, player, opponent):
    """
    Evaluate the board position.
    Returns a score: positive favors player, negative favors opponent.
    Emphasize both attacking and defending.
    """
    score = 0
    size = len(grid)
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    
    for y in range(size):
        for x in range(size):
            if grid[y][x] == player:
                # Evaluate all directions from this player piece
                for dx, dy in directions:
                    c_forward = count_in_direction(grid, x, y, dx, dy, player)
                    c_backward = count_in_direction(grid, x, y, -dx, -dy, player)
                    total = c_forward + c_backward + 1
                    
                    # Score based on line length - aggressive evaluation
                    if total >= 5:
                        score += 100000
                    elif total == 4:
                        score += 15000  # increased from 10000
                    elif total == 3:
                        score += 1000   # increased from 500
                    elif total == 2:
                        score += 100    # increased from 50
                    elif total == 1:
                        score += 10
                        
            elif grid[y][x] == opponent:
                # DEFENSIVE: Heavily penalize opponent's formations
                for dx, dy in directions:
                    c_forward = count_in_direction(grid, x, y, dx, dy, opponent)
                    c_backward = count_in_direction(grid, x, y, -dx, -dy, opponent)
                    total = c_forward + c_backward + 1
                    
                    # Much higher penalty to prioritize blocking opponent threats
                    if total >= 5:
                        score -= 150000  # increased from 100000
                    elif total == 4:
                        score -= 25000   # heavily increased from 10000
                    elif total == 3:
                        score -= 1500    # increased from 500
                    elif total == 2:
                        score -= 150     # increased from 50
                    elif total == 1:
                        score -= 10
    
    return score


def get_candidates(grid, player, opponent, limit=12):
    """
    Get the most promising candidate moves.
    Prioritizes moves near existing pieces.
    """
    size = len(grid)
    candidates = set()
    
    # Collect empty cells adjacent to existing pieces
    for y in range(size):
        for x in range(size):
            if grid[y][x] != 0:
                # Add neighbors
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < size and 0 <= ny < size and grid[ny][nx] == 0:
                            candidates.add((nx, ny))
    
    # If no candidates (empty board), start from center
    if not candidates:
        center = size // 2
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = center + dx, center + dy
                if 0 <= nx < size and 0 <= ny < size:
                    candidates.add((nx, ny))
    
    return list(candidates)[:limit]


def alphabeta(grid, x, y, depth, alpha, beta, is_maximizing, player, opponent):
    """
    Alpha-beta minimax search.
    is_maximizing: True if searching for player's best move, False for opponent.
    """
    size = len(grid)
    current_player = player if is_maximizing else opponent
    
    # Place the move
    grid[y][x] = current_player
    
    # Check for immediate win
    if get_win_line(grid, x, y, current_player):
        grid[y][x] = 0
        return 100000 if is_maximizing else -100000
    
    # Depth limit: evaluate and return
    if depth == 0:
        score = evaluate(grid, player, opponent)
        grid[y][x] = 0
        return score
    
    if is_maximizing:
        value = float('-inf')
        candidates = get_candidates(grid, player, opponent, 8)
        for cx, cy in candidates:
            if grid[cy][cx] == 0:
                val = alphabeta(grid, cx, cy, depth - 1, alpha, beta, False, player, opponent)
                value = max(value, val)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break  # Beta cutoff
    else:
        value = float('inf')
        candidates = get_candidates(grid, opponent, player, 8)
        for cx, cy in candidates:
            if grid[cy][cx] == 0:
                val = alphabeta(grid, cx, cy, depth - 1, alpha, beta, True, player, opponent)
                value = min(value, val)
                beta = min(beta, value)
                if beta <= alpha:
                    break  # Alpha cutoff
    
    grid[y][x] = 0
    return value


def get_move(board, player, depth=3):
    """
    Find the best move for player using alpha-beta pruning.
    Returns (x, y) tuple or None if board is full.
    """
    opponent = 3 - player
    candidates = get_candidates(board, player, opponent, 10)
    
    if not candidates:
        # Board is full
        empties = [(x, y) for y in range(len(board)) for x in range(len(board)) if board[y][x] == 0]
        return random.choice(empties) if empties else None
    
    best_move = candidates[0]
    best_score = float('-inf')
    
    for x, y in candidates:
        if board[y][x] == 0:
            score = alphabeta(board, x, y, depth - 1, float('-inf'), float('inf'), False, player, opponent)
            if score > best_score:
                best_score = score
                best_move = (x, y)
    
    return best_move
