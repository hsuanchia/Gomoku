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


def count_open_ends(grid, x, y, dx, dy, player):
    """Count how many open ends (empty spaces) exist in a line."""
    size = len(grid)
    open_count = 0
    # Check forward
    nx, ny = x + dx, y + dy
    if 0 <= nx < size and 0 <= ny < size and grid[ny][nx] == 0:
        open_count += 1
    # Check backward
    nx, ny = x - dx, y - dy
    if 0 <= nx < size and 0 <= ny < size and grid[ny][nx] == 0:
        open_count += 1
    return open_count


def evaluate_line(grid, x, y, dx, dy, player, opponent):
    """
    Evaluate a potential line. Returns score for this line.
    Higher score means better for the player.
    Emphasize both attacking and defending.
    """
    c_forward = count_in_direction(grid, x, y, dx, dy, player)
    c_backward = count_in_direction(grid, x, y, -dx, -dy, player)
    total = c_forward + c_backward + 1
    
    open_ends = count_open_ends(grid, x, y, dx, dy, player)
    
    # Scoring based on line length and openness - aggressive evaluation
    score = 0
    if total >= 5:
        score = 100000
    elif total == 4:
        score = 20000 + (open_ends * 8000)  # heavily increased
    elif total == 3:
        score = 2000 + (open_ends * 1000)   # increased
    elif total == 2:
        score = 200 + (open_ends * 100)     # increased
    elif total == 1:
        score = 20 + (open_ends * 10)       # increased
    
    return score


def evaluate(grid, player, opponent):
    """
    Advanced evaluation function.
    Returns a score: positive favors player, negative favors opponent.
    Emphasize defensive play to prevent opponent from winning.
    """
    score = 0
    size = len(grid)
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    
    # Evaluate all positions
    for y in range(size):
        for x in range(size):
            if grid[y][x] == player:
                # Score player's formations
                for dx, dy in directions:
                    score += evaluate_line(grid, x, y, dx, dy, player, opponent)
            elif grid[y][x] == opponent:
                # MUCH heavier penalty for opponent's formations to prioritize defense
                for dx, dy in directions:
                    opponent_score = evaluate_line(grid, x, y, dx, dy, opponent, player)
                    score -= opponent_score * 1.5  # increased from 1.1
    
    return score


def get_strategic_candidates(grid, player, opponent, limit=15):
    """
    Get the most strategic candidate moves.
    Prioritizes:
    1. Moves that complete a line (immediate win)
    2. Moves that block opponent's win
    3. Moves that create/extend lines
    4. Moves near existing pieces
    """
    size = len(grid)
    candidates = {}
    
    # Check all empty cells
    for y in range(size):
        for x in range(size):
            if grid[y][x] == 0:
                priority = 0
                
                # Check if this move wins
                grid[y][x] = player
                if get_win_line(grid, x, y, player):
                    priority = 1000000
                grid[y][x] = 0
                
                # Check if this blocks opponent's win
                if priority < 1000000:
                    grid[y][x] = opponent
                    if get_win_line(grid, x, y, opponent):
                        priority = 900000
                    grid[y][x] = 0
                
                # Check if near existing pieces
                if priority < 900000:
                    for dy in range(-2, 3):
                        for dx in range(-2, 3):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < size and 0 <= ny < size and grid[ny][nx] != 0:
                                priority += 100
                                break
                
                if priority > 0:
                    candidates[(x, y)] = priority
    
    # If no candidates, start from center
    if not candidates:
        center = size // 2
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = center + dx, center + dy
                if 0 <= nx < size and 0 <= ny < size:
                    candidates[(nx, ny)] = 50
    
    # Sort by priority and return top candidates
    sorted_candidates = sorted(candidates.items(), key=lambda item: item[1], reverse=True)
    return [pos for pos, _ in sorted_candidates[:limit]]


def alphabeta(grid, x, y, depth, alpha, beta, is_maximizing, player, opponent):
    """
    Alpha-beta minimax search with improved heuristics.
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
        candidates = get_strategic_candidates(grid, player, opponent, 10)
        for cx, cy in candidates:
            if grid[cy][cx] == 0:
                val = alphabeta(grid, cx, cy, depth - 1, alpha, beta, False, player, opponent)
                value = max(value, val)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break  # Beta cutoff
    else:
        value = float('inf')
        candidates = get_strategic_candidates(grid, opponent, player, 10)
        for cx, cy in candidates:
            if grid[cy][cx] == 0:
                val = alphabeta(grid, cx, cy, depth - 1, alpha, beta, True, player, opponent)
                value = min(value, val)
                beta = min(beta, value)
                if beta <= alpha:
                    break  # Alpha cutoff
    
    grid[y][x] = 0
    return value


def get_move(board, player, depth=4):
    """
    Find the best move for player using improved alpha-beta pruning.
    Uses stronger heuristics and deeper search.
    Returns (x, y) tuple or None if board is full.
    """
    opponent = 3 - player
    candidates = get_strategic_candidates(board, player, opponent, 12)
    
    if not candidates:
        # Board is full
        empties = [(x, y) for y in range(len(board)) for x in range(len(board)) if board[y][x] == 0]
        return random.choice(empties) if empties else None
    
    best_move = candidates[0]
    best_score = float('-inf')
    
    # Search with iterative deepening and move ordering
    for x, y in candidates:
        if board[y][x] == 0:
            score = alphabeta(board, x, y, depth - 1, float('-inf'), float('inf'), False, player, opponent)
            if score > best_score:
                best_score = score
                best_move = (x, y)
    
    return best_move
