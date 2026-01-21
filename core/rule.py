def check_win(grid, x, y, player, win_len=5):
    """Return True if placing `player` at (x,y) on `grid` makes `player` have win_len in a row."""
    size = len(grid)
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dx, dy in directions:
        count = 1
        for d in [1, -1]:
            nx, ny = x, y
            while True:
                nx += dx * d
                ny += dy * d
                if 0 <= nx < size and 0 <= ny < size and grid[ny][nx] == player:
                    count += 1
                else:
                    break
        if count >= win_len:
            return True
    return False
