import pygame
import random
import sys
import math

# Game Constants
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
SPAWN_INTERVAL = 5  # seconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Pygame init
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chess Snake")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.grow = False

    def move(self):
        x, y = self.body[0]
        dx, dy = self.direction
        new_head = ((x + dx) % GRID_WIDTH, (y + dy) % GRID_HEIGHT)
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def draw(self, surf):
        for seg in self.body:
            r = pygame.Rect(seg[0]*CELL_SIZE, seg[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surf, GREEN, r)

class Apple:
    def __init__(self):
        self.position = self.random_pos(set())
    def random_pos(self, occupied):
        while True:
            p = (random.randrange(GRID_WIDTH), random.randrange(GRID_HEIGHT))
            if p not in occupied:
                return p
    def draw(self, surf):
        r = pygame.Rect(self.position[0]*CELL_SIZE, self.position[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surf, RED, r)

class Bullet:
    def __init__(self, pos, d):
        self.position = pos
        self.direction = d
    def move(self):
        x, y = self.position
        self.position = (x + self.direction[0], y + self.direction[1])
    def draw(self, surf):
        r = pygame.Rect(
            self.position[0]*CELL_SIZE + CELL_SIZE//4,
            self.position[1]*CELL_SIZE + CELL_SIZE//4,
            CELL_SIZE//2, CELL_SIZE//2)
        pygame.draw.rect(surf, YELLOW, r)

class ChessPiece:
    def __init__(self, t, pos):
        self.type = t
        self.position = pos
    def draw(self, surf):
        r = pygame.Rect(self.position[0]*CELL_SIZE, self.position[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surf, BLUE, r)

class Pawn(ChessPiece):
    def __init__(self, pos): super().__init__('pawn', pos); self.value = 5
    def move(self):
        x, y = self.position
        self.position = (x, (y-1) % GRID_HEIGHT)

class Knight(ChessPiece):
    moves = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
    def __init__(self, pos): super().__init__('knight', pos); self.value = 10
    def move(self):
        dx, dy = random.choice(self.moves)
        x, y = self.position
        self.position = ((x+dx)%GRID_WIDTH, (y+dy)%GRID_HEIGHT)
    def maybe_shoot(self, bullets):
        if random.random() < 0.5:
            d = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
            bullets.append(Bullet(self.position, d))

class Bishop(ChessPiece):
    dirs = [(1,1),(1,-1),(-1,1),(-1,-1)]
    def __init__(self, pos): super().__init__('bishop', pos); self.value = 15
    def move(self):
        dx, dy = random.choice(self.dirs)
        x, y = self.position
        self.position = ((x+dx)%GRID_WIDTH, (y+dy)%GRID_HEIGHT)

def run_game():
    snake = Snake()
    apple = Apple()
    chess_pieces = []
    bullets = []
    score = 0
    spawn_timer = SPAWN_INTERVAL
    move_timer = 0
    running = True

    while running:
        dt = clock.tick(10) / 1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                d = snake.direction
                if ev.key == pygame.K_UP and d != (0,1):    snake.direction = (0,-1)
                if ev.key == pygame.K_DOWN and d != (0,-1): snake.direction = (0,1)
                if ev.key == pygame.K_LEFT and d != (1,0):  snake.direction = (-1,0)
                if ev.key == pygame.K_RIGHT and d != (-1,0):snake.direction = (1,0)

        snake.move()
        head = snake.body[0]

        # spawn pieces
        spawn_timer -= dt
        if spawn_timer <= 0:
            pos = (random.randrange(GRID_WIDTH), random.randrange(GRID_HEIGHT))
            typ = random.choice(['pawn','knight','bishop'])
            if typ=='pawn':   chess_pieces.append(Pawn(pos))
            elif typ=='knight': chess_pieces.append(Knight(pos))
            else:              chess_pieces.append(Bishop(pos))
            spawn_timer = SPAWN_INTERVAL

        # move pieces
        move_timer += dt
        if move_timer >= 1:
            for p in chess_pieces:
                p.move()
                if isinstance(p, Knight): p.maybe_shoot(bullets)
            move_timer = 0

        # move bullets
        for b in bullets[:]:
            b.move()
            x,y = b.position
            if x<0 or x>=GRID_WIDTH or y<0 or y>=GRID_HEIGHT:
                bullets.remove(b)

        # collisions: bullet->head
        for b in bullets[:]:
            if b.position == head:
                bullets.remove(b)
                if snake.body: snake.body.pop()
                if not snake.body:
                    running = False
                    break

        # collisions: snake->piece
        for p in chess_pieces[:]:
            if p.position == head:
                score += p.value
                chess_pieces.remove(p)
                # no grow

        # snake eats apple
        if head == apple.position:
            score += 10
            snake.grow = True
            occupied = set(snake.body) | {p.position for p in chess_pieces}
            apple.position = apple.random_pos(occupied)

        # piece hits body
        for p in chess_pieces:
            if p.position in snake.body[1:]:
                running = False
                break

        # draw
        screen.fill(BLACK)
        snake.draw(screen)
        apple.draw(screen)
        for p in chess_pieces: p.draw(screen)
        for b in bullets:      b.draw(screen)
        # UI
        timer_text = max(0, math.ceil(spawn_timer))
        screen.blit(font.render(f"Score: {score}", True, WHITE), (5,5))
        screen.blit(font.render(f"Next piece in {timer_text}s", True, WHITE), (5,35))
        pygame.display.flip()

    return score

def game_over_screen(final_score):
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r: return True
                if ev.key == pygame.K_q: return False
        screen.fill(BLACK)
        screen.blit(font.render("GAME OVER", True, RED), (SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2-60))
        screen.blit(font.render(f"Final Score: {final_score}", True, WHITE), (SCREEN_WIDTH//2-110, SCREEN_HEIGHT//2))
        screen.blit(font.render("Press R to Restart or Q to Quit", True, WHITE), (SCREEN_WIDTH//2-180, SCREEN_HEIGHT//2+60))
        pygame.display.flip()
        clock.tick(5)

if __name__ == '__main__':
    while True:
        score = run_game()
        if not game_over_screen(score):
            break
    pygame.quit()
    sys.exit()