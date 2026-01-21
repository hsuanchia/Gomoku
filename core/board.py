class Board:
    def __init__(self, size=15):
        self.size = size
        self.reset()

    def reset(self):
        self.grid = [[0] * self.size for _ in range(self.size)]

    def place(self, x, y, player):
        """Place a stone for player at (x,y). Return True if placed."""
        if 0 <= x < self.size and 0 <= y < self.size and self.grid[y][x] == 0:
            self.grid[y][x] = player
            return True
        return False

    def is_full(self):
        return all(self.grid[y][x] != 0 for y in range(self.size) for x in range(self.size))

    def empty_cells(self):
        return [(x, y) for y in range(self.size) for x in range(self.size) if self.grid[y][x] == 0]
