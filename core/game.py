from .board import Board
from .rule import check_win


class Game:
    def __init__(self, size=15):
        self.size = size
        self.board = Board(size)
        self.current_player = 1
        self.winner = 0
        self.win_line = None
        self.last_move = None

    def reset(self, starting_player=1):
        self.board.reset()
        self.current_player = starting_player
        self.winner = 0
        self.win_line = None
        self.last_move = None

    def play_move(self, x, y):
        """Attempt to place current_player at (x,y).
        Returns (placed:bool, won:bool)."""
        if self.winner != 0:
            return False, False
        placed = self.board.place(x, y, self.current_player)
        if not placed:
            return False, False
        # determine if this placement produced a winning contiguous line
        from .rule import get_win_line
        win_line = get_win_line(self.board.grid, x, y, self.current_player)
        self.last_move = (x, y)
        if win_line:
            self.winner = self.current_player
            self.win_line = win_line
            return True, True
        # switch turn
        self.current_player = 3 - self.current_player
        return True, False

    def is_full(self):
        return self.board.is_full()
