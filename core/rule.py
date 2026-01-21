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
            # Debug: report winning detection (useful when investigating false positives)
            try:
                print(f"check_win: player={player} win at {(x,y)} dir={(dx,dy)} count={count}")
            except Exception:
                pass
            return True
    return False


def get_win_line(grid, x, y, player, win_len=5):
    """Return a list of coordinates [(x,y),...] that form the contiguous winning line
    including the placed stone at (x,y). Returns None if no win is found."""
    size = len(grid)
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dx, dy in directions:
        coords = [(x, y)]
        # forward
        nx, ny = x, y
        while True:
            nx += dx
            ny += dy
            if 0 <= nx < size and 0 <= ny < size and grid[ny][nx] == player:
                coords.append((nx, ny))
            else:
                break
        # backward
        nx, ny = x, y
        while True:
            nx -= dx
            ny -= dy
            if 0 <= nx < size and 0 <= ny < size and grid[ny][nx] == player:
                coords.insert(0, (nx, ny))
            else:
                break
        if len(coords) >= win_len:
            return coords
    return None
