import os
import sys
import pygame
from players import random as random_ai
from core.game import Game

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

# clock
clock = pygame.time.Clock()

# Game state (moved to core.game.Game)
game = Game(BOARD_SIZE)
mode = 'menu'  # 'menu', 'playing', 'game_over'

# Player settings
human_player = 1  # 1=black, 2=white
# Opponent AI player (None to disable AI)
AI_PLAYER = 2


# menu step for multi-stage menu: 'choose_mode' -> 'choose_color'
menu_step = 'choose_mode'
# whether the selected match mode uses AI opponent
vs_ai = False

# UI transient state
hover_cell = None


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


# win detection moved to core.rule.check_win via core.game.Game


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
	grid = game.board.grid
	for yy in range(BOARD_SIZE):
		for xx in range(BOARD_SIZE):
			if grid[yy][xx] != 0:
				center = (int(BOARD_ORIGIN_X + xx * CELL_SIZE), int(BOARD_ORIGIN_Y + yy * CELL_SIZE))
				color = (0, 0, 0) if grid[yy][xx] == 1 else (255, 255, 255)
				pygame.draw.circle(screen, color, center, max(2, int(CELL_SIZE // 2 - 2)))


def draw_highlights():
	# last move marker
	if game.last_move:
		lx, ly = game.last_move
		center = (int(BOARD_ORIGIN_X + lx * CELL_SIZE), int(BOARD_ORIGIN_Y + ly * CELL_SIZE))
		r = max(2, int(CELL_SIZE // 2 - 2))
		pygame.draw.circle(screen, (0, 150, 255), center, r + 6, 3)

	# hover preview (semi-transparent)
	if hover_cell and mode == 'playing' and game.winner == 0:
		hx, hy = hover_cell
		center = (int(BOARD_ORIGIN_X + hx * CELL_SIZE), int(BOARD_ORIGIN_Y + hy * CELL_SIZE))
		r = max(2, int(CELL_SIZE // 2 - 2))
		s = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
		pygame.draw.circle(s, (0, 255, 0, 120), (r + 4, r + 4), r)
		screen.blit(s, (center[0] - (r + 4), center[1] - (r + 4)))

	# winning line highlight (if any)
	if game.win_line:
		for (wx, wy) in game.win_line:
			center = (int(BOARD_ORIGIN_X + wx * CELL_SIZE), int(BOARD_ORIGIN_Y + wy * CELL_SIZE))
			r = max(2, int(CELL_SIZE // 2 - 2))
			pygame.draw.circle(screen, (255, 60, 60), center, r + 6, 4)


def reset_board(starting_player=1):
	"""Reset core game state and switch to playing mode."""
	game.reset(starting_player)
	global mode
	mode = 'playing'


def start_game(as_player):
	global human_player, AI_PLAYER, vs_ai, menu_step
	human_player = as_player
	if vs_ai:
		AI_PLAYER = 3 - human_player
	else:
		AI_PLAYER = None
	reset_board(starting_player=1)
	menu_step = 'choose_mode'


def draw_menu():
	screen.fill((40, 40, 60))
	title = BIG_FONT.render('Gomoku', True, (255, 255, 255))
	screen.blit(title, ((WINDOW_W - title.get_width()) // 2, 60))
	# Buttons
	b_w = 260
	b_h = 56
	bx = (WINDOW_W - b_w) // 2
	by = 180
	if menu_step == 'choose_mode':
		btn_hvh = Button((bx, by, b_w, b_h), 'Human vs Human')
		btn_hvai = Button((bx, by + 96, b_w, b_h), 'Human vs AI')
		btn_hvh.draw(screen)
		btn_hvai.draw(screen)
		return btn_hvh, btn_hvai
	else:
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
	if game.winner == 0:
		msg = 'Draw'
	else:
		if human_player == game.winner:
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
	global AI_PLAYER, winner, current_player, mode, screen, vs_ai, menu_step, hover_cell

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
					if menu_step == 'choose_mode':
						# choose match type
						if bx <= mx <= bx + 260 and by <= my <= by + 56:
							vs_ai = False
							menu_step = 'choose_color'
						elif bx <= mx <= bx + 260 and by + 96 <= my <= by + 96 + 56:
							vs_ai = True
							menu_step = 'choose_color'
					else:
						# choose color then start
						if bx <= mx <= bx + 260 and by <= my <= by + 56:
							start_game(1)
						if bx <= mx <= bx + 260 and by + 96 <= my <= by + 96 + 56:
							start_game(2)

			elif mode == 'playing':
				if event.type == pygame.MOUSEMOTION:
					# update hover cell for highlighting
					hc = get_cell(event.pos)
					if hc and game.board.grid[hc[1]][hc[0]] == 0:
						hover_cell = hc
					else:
						hover_cell = None

				if event.type == pygame.MOUSEBUTTONDOWN and game.winner == 0:
					mx, my = event.pos
					# check top-right buttons first
					for b in in_top_buttons:
						if b.collidepoint((mx, my)):
							if b.text == 'Restart':
								reset_board(starting_player=1)
							elif b.text == 'Menu':
								mode = 'menu'
								menu_step = 'choose_mode'
								vs_ai = False
							break
					else:
						# place piece: if AI is disabled both players are human; otherwise only
						# the configured human_player may place when it's their turn.
						if AI_PLAYER is None or human_player == game.current_player:
							cell = get_cell(event.pos)
							if cell:
								x, y = cell
								placed, won = game.play_move(x, y)
								if placed:
									# prevent extra mouse events causing multiple placements
									pygame.event.clear(pygame.MOUSEBUTTONDOWN)
									if won:
										mode = 'game_over'

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
		if mode == 'playing' and game.winner == 0 and AI_PLAYER is not None and game.current_player == AI_PLAYER:
			move = random_ai.get_move(game.board.grid, game.current_player)
			if move:
				x, y = move
				placed, won = game.play_move(x, y)
				if placed:
					# clear mouse events which might have accumulated
					pygame.event.clear(pygame.MOUSEBUTTONDOWN)
					if won:
						mode = 'game_over'
			pygame.time.wait(150)

		# Drawing
		if mode == 'menu':
			menu_buttons = draw_menu()
		else:
			draw_board()
			draw_pieces()
			draw_highlights()
			in_top_buttons = draw_top_right()
			if mode == 'game_over':
				gameover_restart = draw_game_over()

		pygame.display.flip()
		clock.tick(60)


if __name__ == '__main__':
	main()

