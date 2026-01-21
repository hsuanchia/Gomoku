import os
import sys
import pygame
from players import random as random_ai

# If running the script directly, add project root to sys.path so sibling
# packages (like `players`) can be imported.
if __name__ == '__main__' and __package__ is None:
	sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# -----------------
# Global constants / variables
# -----------------
BOARD_SIZE = 15

# Initial window size (will be resizable)
INIT_WINDOW = 680
# Top UI bar height (reserve space so buttons don't overlap board)
TOP_BAR = 72

pygame.init()

# window dimensions (updated on resize)
WINDOW_W = INIT_WINDOW
WINDOW_H = INIT_WINDOW

# dynamic layout values (computed by update_layout)
MARGIN = 40
CELL_SIZE = 40.0
BOARD_PIXEL = CELL_SIZE * (BOARD_SIZE - 1)
BOARD_ORIGIN_X = 0
BOARD_ORIGIN_Y = TOP_BAR + MARGIN

screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE | pygame.SWSURFACE)
pygame.display.set_caption("Gomoku")

clock = pygame.time.Clock()

# Game state
board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
current_player = 1
winner = 0
mode = 'menu'  # 'menu', 'playing', 'game_over'

# Player settings
human_player = 1  # 1=black, 2=white
# Opponent AI player (None to disable AI)
AI_PLAYER = 2


# Choose a font that supports CJK characters on Windows fallback list
def choose_font(names, size):
	for n in names:
		try:
			f = pygame.font.SysFont(n, size)
			return f
		except Exception:
			continue
	return pygame.font.Font(None, size)

FONT = choose_font(['Microsoft JhengHei', 'Arial Unicode MS', 'Noto Sans CJK JP', None], 28)
BIG_FONT = choose_font(['Microsoft JhengHei', 'Arial Unicode MS', 'Noto Sans CJK JP', None], 48)


def update_layout(width, height):
	global WINDOW_W, WINDOW_H, MARGIN, CELL_SIZE, BOARD_PIXEL, BOARD_ORIGIN_X, BOARD_ORIGIN_Y
	WINDOW_W, WINDOW_H = width, height
	MARGIN = max(12, int(min(WINDOW_W, WINDOW_H) * 0.05))
	avail = min(WINDOW_W, max(0, WINDOW_H - TOP_BAR)) - 2 * MARGIN
	if avail < 20:
		avail = 20
	CELL_SIZE = avail / (BOARD_SIZE - 1)
	BOARD_PIXEL = CELL_SIZE * (BOARD_SIZE - 1)
	BOARD_ORIGIN_X = (WINDOW_W - BOARD_PIXEL) / 2
	BOARD_ORIGIN_Y = TOP_BAR + MARGIN


# -----------------
# Function and class definitions
# -----------------
class Button:
	def __init__(self, rect, text, fg=(0, 0, 0), bg=(200, 200, 200)):
		self.rect = pygame.Rect(rect)
		self.text = text
		self.fg = fg
		self.bg = bg

	def draw(self, surf):
		pygame.draw.rect(surf, self.bg, self.rect)
		pygame.draw.rect(surf, (0, 0, 0), self.rect, 2)
		txt = FONT.render(self.text, True, self.fg)
		tw, th = txt.get_size()
		surf.blit(txt, (self.rect.x + (self.rect.w - tw) // 2, self.rect.y + (self.rect.h - th) // 2))

	def collidepoint(self, pos):
		return self.rect.collidepoint(pos)


def get_cell(pos):
	mx, my = pos
	dx = mx - BOARD_ORIGIN_X
	dy = my - BOARD_ORIGIN_Y
	x = round(dx / CELL_SIZE)
	y = round(dy / CELL_SIZE)
	if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
		return x, y
	return None


def check_win(x, y, player):
	directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
	for dx, dy in directions:
		count = 1
		for d in [1, -1]:
			nx, ny = x, y
			while True:
				nx += dx * d
				ny += dy * d
				if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[ny][nx] == player:
					count += 1
				else:
					break
		if count >= 5:
			return True
	return False


def draw_board():
	# background
	screen.fill((249, 214, 91))  # 木頭色
	# top bar background
	pygame.draw.rect(screen, (60, 60, 80), (0, 0, WINDOW_W, TOP_BAR))
	# grid
	for i in range(BOARD_SIZE):
		x = BOARD_ORIGIN_X + i * CELL_SIZE
		pygame.draw.line(screen, (0, 0, 0), (x, BOARD_ORIGIN_Y), (x, BOARD_ORIGIN_Y + CELL_SIZE * (BOARD_SIZE - 1)))
		y = BOARD_ORIGIN_Y + i * CELL_SIZE
		pygame.draw.line(screen, (0, 0, 0), (BOARD_ORIGIN_X, y), (BOARD_ORIGIN_X + CELL_SIZE * (BOARD_SIZE - 1), y))


def draw_pieces():
	for yy in range(BOARD_SIZE):
		for xx in range(BOARD_SIZE):
			if board[yy][xx] != 0:
				center = (int(BOARD_ORIGIN_X + xx * CELL_SIZE), int(BOARD_ORIGIN_Y + yy * CELL_SIZE))
				color = (0, 0, 0) if board[yy][xx] == 1 else (255, 255, 255)
				pygame.draw.circle(screen, color, center, max(2, int(CELL_SIZE // 2 - 2)))


def reset_board(starting_player=1):
	global board, current_player, winner, mode
	board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
	current_player = starting_player
	winner = 0
	mode = 'playing'


def start_game(as_player):
	global human_player, AI_PLAYER
	human_player = as_player
	AI_PLAYER = 3 - human_player
	reset_board(starting_player=1)


def draw_menu():
	screen.fill((40, 40, 60))
	title = BIG_FONT.render('Gomoku', True, (255, 255, 255))
	screen.blit(title, ((WINDOW_W - title.get_width()) // 2, 60))
	# Buttons
	b_w = 260
	b_h = 56
	bx = (WINDOW_W - b_w) // 2
	by = 180
	btn_black = Button((bx, by, b_w, b_h), 'Play as Black (先手)')
	btn_white = Button((bx, by + 96, b_w, b_h), 'Play as White (後手)')
	btn_black.draw(screen)
	btn_white.draw(screen)
	return btn_black, btn_white


def draw_top_right():
	# Draw small control buttons at top-right within the top bar
	btns = []
	padding = 10
	w = 100
	h = 36
	x0 = WINDOW_W - w - padding
	y0 = (TOP_BAR - h) // 2
	btn_restart = Button((x0, y0, w, h), 'Restart')
	btn_menu = Button((x0, y0 + h + 6, w, h), 'Menu')
	btns.append(btn_restart)
	btns.append(btn_menu)
	for b in btns:
		b.draw(screen)
	return btns


def draw_game_over():
	# overlay
	s = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
	s.fill((0, 0, 0, 140))
	screen.blit(s, (0, 0))
	# message
	if winner == 0:
		msg = 'Draw'
	else:
		if human_player == winner:
			msg = 'You win!'
		else:
			msg = 'You lose!'
	txt = BIG_FONT.render(msg, True, (255, 255, 255))
	rect = txt.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 - 30))
	screen.blit(txt, rect)
	# restart button
	btn = Button((WINDOW_W // 2 - 70, WINDOW_H // 2 + 20, 140, 44), 'Restart')
	btn.draw(screen)
	return btn


# -----------------
# Main
# -----------------
def main():
	update_layout(WINDOW_W, WINDOW_H)
	menu_buttons = ()
	in_top_buttons = []
	gameover_restart = None
	global AI_PLAYER, winner, current_player, mode, screen

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			if event.type == pygame.VIDEORESIZE:
				# handle window resize
				update_layout(event.w, event.h)
				screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE | pygame.SWSURFACE)
				
			if mode == 'menu':
				if event.type == pygame.MOUSEBUTTONDOWN:
					mx, my = event.pos
					bx = (WINDOW_W - 260) // 2
					by = 180
					if bx <= mx <= bx + 260 and by <= my <= by + 56:
						start_game(1)
					if bx <= mx <= bx + 260 and by + 96 <= my <= by + 96 + 56:
						start_game(2)

			elif mode == 'playing':
				if event.type == pygame.MOUSEBUTTONDOWN and winner == 0:
					mx, my = event.pos
					# check top-right buttons first
					for b in in_top_buttons:
						if b.collidepoint((mx, my)):
							if b.text == 'Restart':
								reset_board(starting_player=1)
							elif b.text == 'Menu':
								mode = 'menu'
							break
					else:
						# place piece if human's turn
						if human_player == current_player:
							cell = get_cell(event.pos)
							if cell:
								x, y = cell
								if board[y][x] == 0:
									board[y][x] = current_player
									if check_win(x, y, current_player):
										winner = current_player
										mode = 'game_over'
									else:
										current_player = 3 - current_player

				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_a:
						# toggle AI for opponent
						if AI_PLAYER is None:
							AI_PLAYER = 3 - human_player
							print('Random AI enabled')
						else:
							AI_PLAYER = None
							print('Random AI disabled')

			elif mode == 'game_over':
				if event.type == pygame.MOUSEBUTTONDOWN:
					mx, my = event.pos
					if gameover_restart and gameover_restart.collidepoint((mx, my)):
						reset_board(starting_player=1)

		# AI move handling
		if mode == 'playing' and winner == 0 and AI_PLAYER is not None and current_player == AI_PLAYER:
			move = random_ai.get_move(board, current_player)
			if move:
				x, y = move
				board[y][x] = current_player
				if check_win(x, y, current_player):
					winner = current_player
					mode = 'game_over'
				else:
					current_player = 3 - current_player
			pygame.time.wait(150)

		# Drawing
		if mode == 'menu':
			menu_buttons = draw_menu()
		else:
			draw_board()
			draw_pieces()
			in_top_buttons = draw_top_right()
			if mode == 'game_over':
				gameover_restart = draw_game_over()

		pygame.display.flip()
		clock.tick(60)


if __name__ == '__main__':
	main()

