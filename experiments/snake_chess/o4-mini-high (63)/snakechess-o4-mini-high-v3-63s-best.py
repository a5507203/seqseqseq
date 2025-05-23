import pygame
import random
import time
import math
from collections import deque

# --- Configuration ---
GRID_SIZE = 20           # cells per row/column
CELL_SIZE = 30           # pixels per cell
WINDOW_SIZE = GRID_SIZE * CELL_SIZE
FPS = 15

SPAWN_INTERVAL = 10.0    # seconds between new chess piece spawns
PIECE_MOVE_INTERVAL = 1.0  # seconds between chess piece moves

# Piece values
VALUES = {'pawn': 5, 'knight': 10, 'bishop': 15}

# Knight bullet speed (cells per frame)
BULLET_SPEED = 1

# Directions
DIRS_CARDINAL = [(1,0), (-1,0), (0,1), (0,-1)]
DIRS_DIAGONAL = [(1,1), (1,-1), (-1,1), (-1,-1)]
KNIGHT_DIRS = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]

# Colors
COLOR_BG     = (30, 30, 30)
COLOR_GRID   = (50, 50, 50)
COLOR_SNAKE  = (0, 200, 0)
COLOR_APPLE  = (200, 0, 0)
COLOR_TEXT   = (255, 255, 255)
COLOR_BULLET = (255, 255, 0)
COLOR_PAWN   = (180, 180, 180)
COLOR_KNIGHT = (150, 100, 200)
COLOR_BISHOP = (200, 150, 50)

pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 40))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# --- Helper Functions ---
def wrap(pos):
    """Wrap a position around the grid edges."""
    x, y = pos
    return (x % GRID_SIZE, y % GRID_SIZE)

def rand_empty_cell(occupied):
    """Return a random cell not in occupied set."""
    while True:
        c = (random.randrange(GRID_SIZE), random.randrange(GRID_SIZE))
        if c not in occupied:
            return c

# --- Game Objects ---
class Snake:
    def __init__(self):
        self.body = deque([(GRID_SIZE//2, GRID_SIZE//2),
                           (GRID_SIZE//2-1, GRID_SIZE//2),
                           (GRID_SIZE//2-2, GRID_SIZE//2)])
        self.dir = (1, 0)
        self.grow = 0

    def head(self):
        return self.body[0]

    def step(self):
        new_head = wrap((self.head()[0] + self.dir[0],
                         self.head()[1] + self.dir[1]))
        self.body.appendleft(new_head)
        if self.grow > 0:
            self.grow -= 1
        else:
            self.body.pop()

    def change_dir(self, d):
        # Prevent reversing
        if (d[0] == -self.dir[0] and d[1] == -self.dir[1]):
            return
        self.dir = d

class ChessPiece:
    def __init__(self, kind):
        self.kind = kind  # 'pawn','knight','bishop'
        self.pos = None
        # pawns get a random cardinal direction
        if kind == 'pawn':
            self.dir = random.choice(DIRS_CARDINAL)
        else:
            self.dir = None

    def move(self):
        x, y = self.pos
        if self.kind == 'pawn':
            dx, dy = self.dir
            self.pos = wrap((x+dx, y+dy))
        elif self.kind == 'bishop':
            dx, dy = random.choice(DIRS_DIAGONAL)
            self.pos = wrap((x+dx, y+dy))
        elif self.kind == 'knight':
            dx, dy = random.choice(KNIGHT_DIRS)
            self.pos = wrap((x+dx, y+dy))

    def draw(self, surf):
        cx = self.pos[0]*CELL_SIZE + CELL_SIZE//2
        cy = self.pos[1]*CELL_SIZE + CELL_SIZE//2
        if self.kind == 'pawn':
            pygame.draw.circle(surf, COLOR_PAWN, (cx, cy), CELL_SIZE//3)
        elif self.kind == 'bishop':
            text = font.render('B', True, COLOR_BISHOP)
            surf.blit(text, (cx-8, cy-12))
        elif self.kind == 'knight':
            text = font.render('N', True, COLOR_KNIGHT)
            surf.blit(text, (cx-8, cy-12))

class Bullet:
    def __init__(self, pos, dir):
        self.pos = pos
        self.dir = dir

    def step(self):
        self.pos = (self.pos[0] + self.dir[0], self.pos[1] + self.dir[1])

# --- Initialize Game State ---
snake = Snake()
apple = rand_empty_cell(set(snake.body))
pieces = []
bullets = []
score = 0

last_spawn = time.time()
next_spawn = last_spawn + SPAWN_INTERVAL
last_piece_move = time.time()

running = True
game_over = False

# --- Main Loop ---
while running:
    dt = clock.tick(FPS) / 1000.0
    now = time.time()

    # --- Input ---
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_UP:
                snake.change_dir((0, -1))
            elif e.key == pygame.K_DOWN:
                snake.change_dir((0, 1))
            elif e.key == pygame.K_LEFT:
                snake.change_dir((-1, 0))
            elif e.key == pygame.K_RIGHT:
                snake.change_dir((1, 0))

    if not game_over:
        # --- Snake Move ---
        snake.step()
        head = snake.head()

        # Check self-collision
        if head in list(snake.body)[1:]:
            game_over = True

        # Apple collision
        if head == apple:
            snake.grow += 1
            score += 10
            apple = rand_empty_cell(set(snake.body) | {p.pos for p in pieces})

        # Chess piece capture
        for p in pieces:
            if head == p.pos:
                score += VALUES[p.kind]
                pieces.remove(p)
                break  # only one

        # --- Spawn Chess Pieces ---
        if now >= next_spawn:
            kind = random.choice(['pawn','knight','bishop'])
            occupied = set(snake.body) | {apple} | {p.pos for p in pieces}
            new = ChessPiece(kind)
            new.pos = rand_empty_cell(occupied)
            pieces.append(new)
            last_spawn = now
            next_spawn = last_spawn + SPAWN_INTERVAL

        # --- Move Pieces & Knights Shoot ---
        if now - last_piece_move >= PIECE_MOVE_INTERVAL:
            last_piece_move = now
            # Move each piece
            for p in pieces:
                p.move()
                # Pawn/knight/bishop collide with snake body
                if p.pos in snake.body:
                    game_over = True
                # Knights shoot
                if p.kind == 'knight':
                    # shoot toward snake head (cardinal)
                    dx = snake.head()[0] - p.pos[0]
                    dy = snake.head()[1] - p.pos[1]
                    if abs(dx) > abs(dy):
                        dir = (int(math.copysign(1, dx)), 0)
                    else:
                        dir = (0, int(math.copysign(1, dy)))
                    bullets.append(Bullet(p.pos, dir))

        # --- Move Bullets ---
        for b in bullets[:]:
            b.step()
            x,y = b.pos
            # bullet off-grid -> remove
            if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
                bullets.remove(b)
                continue
            # hit snake?
            if b.pos in snake.body:
                # shorten snake by 1
                if len(snake.body) > 0:
                    snake.body.pop()
                bullets.remove(b)
                if len(snake.body) == 0:
                    game_over = True

    # --- Draw ---
    screen.fill(COLOR_BG)
    # grid
    for x in range(0, WINDOW_SIZE, CELL_SIZE):
        pygame.draw.line(screen, COLOR_GRID, (x,0), (x,WINDOW_SIZE))
    for y in range(0, WINDOW_SIZE, CELL_SIZE):
        pygame.draw.line(screen, COLOR_GRID, (0,y), (WINDOW_SIZE,y))

    # apple
    ax, ay = apple
    pygame.draw.circle(screen, COLOR_APPLE,
                       (ax*CELL_SIZE+CELL_SIZE//2, ay*CELL_SIZE+CELL_SIZE//2),
                       CELL_SIZE//2 - 2)

    # snake
    for seg in snake.body:
        pygame.draw.rect(screen, COLOR_SNAKE,
                         (seg[0]*CELL_SIZE+1, seg[1]*CELL_SIZE+1,
                          CELL_SIZE-2, CELL_SIZE-2))

    # chess pieces
    for p in pieces:
        p.draw(screen)

    # bullets
    for b in bullets:
        bx, by = b.pos
        pygame.draw.rect(screen, COLOR_BULLET,
                         (bx*CELL_SIZE+CELL_SIZE//3,
                          by*CELL_SIZE+CELL_SIZE//3,
                          CELL_SIZE//3, CELL_SIZE//3))

    # UI text
    txt_score = font.render(f"Score: {score}", True, COLOR_TEXT)
    spawn_in = max(0, int(math.ceil(next_spawn - now)))
    txt_spawn = font.render(f"Next piece spawn in {spawn_in}s", True, COLOR_TEXT)
    screen.blit(txt_score, (10, WINDOW_SIZE+8))
    screen.blit(txt_spawn, (150, WINDOW_SIZE+8))

    # game over
    if game_over:
        go = font.render("GAME OVER! Press ESC to quit.", True, (200,50,50))
        screen.blit(go, (WINDOW_SIZE//2-120, WINDOW_SIZE//2-10))

    pygame.display.flip()

    # handle exit on game over
    if game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

pygame.quit()