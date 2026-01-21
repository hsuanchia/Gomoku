import random

def get_move(board, player):
    """Return a random empty (x, y) tuple from the board or None if full."""
    empties = [(x, y) for y, row in enumerate(board) for x, v in enumerate(row) if v == 0]
    if not empties:
        return None
    return random.choice(empties)
