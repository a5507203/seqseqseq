
import sys
import random
import pygame
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
GRID_COLS = 20
GRID_ROWS = 20
CELL_SIZE = WINDOW_WIDTH // GRID_COLS
FPS = 60

# Directions
class Dir(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

@dataclass
class Position:
    x: int
    y: int

    def wrap(self):
        self.x %= GRID_COLS
        self.y %= GRID_ROWS

    def __add__(self, other: Tuple[int, int]):
        return Position(self.x + other[0], self.y + other[1])

@dataclass
class Snake:
    body: List[Position] = field(default_factory=lambda: [Position(GRID_COLS//2, GRID_ROWS//2)])
    direction: Dir = Dir.RIGHT

    def head(self) -> Position:
        return self.body[0]

    def move(self):
        new_head = self.head() + self.direction.value
        new_head.wrap()
        self.body.insert(0, new_head)

    def grow(self):
        self.move()

    def shrink(self):
        if self.body:
            self.body.pop()

    def advance(self, grow: bool = False):
        if grow:
            self.grow()
        else:
            self.move()
            self.body.pop()

@dataclass
class Apple:
    pos: Position

class PieceType(Enum):
    PAWN = 5
    KNIGHT = 10
    BISHOP = 15

@dataclass
class ChessPiece:
    pos: Position
    value: int

    def move(self):
        raise NotImplementedError

@dataclass
class Pawn(ChessPiece):
    def __init__(self, pos: Position):
        super().__init__(pos, PieceType.PAWN.value)

    def move(self):
        self.pos.y += 1
        self.pos.wrap()

@dataclass
class Knight(ChessPiece):
    shoot_cooldown: float = 0.0

    def __init__(self, pos: Position):
        super().__init__(pos, PieceType.KNIGHT.value)

    def move(self):
        moves = [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]
        dx, dy = random.choice(moves)
        self.pos.x += dx
        self.pos.y += dy
        self.pos.wrap()

@dataclass
class Bishop(ChessPiece):
    def __init__(self, pos: Position):
        super().__init__(pos, PieceType.BISHOP.value)

    def move(self):
        moves = [(1,1),(1,-1),(-1,1),(-1,-1)]
        dx, dy = random.choice(moves)
        self.pos.x += dx
        self.pos.y += dy
        self.pos.wrap()

@dataclass
class Bullet:
    pos: Position
    direction: Tuple[int,int]

    def update(self):
        self.pos.x += self.direction[0]
        self.pos.y += self.direction[1]
        self.pos.wrap()

@dataclass
class GameState:
    snake: Snake = field(default_factory=Snake)
    apples: List[Apple] = field(default_factory=list)
    pieces: List[ChessPiece] = field(default_factory=list)
    bullets: List[Bullet] = field(default_factory=list)
    score: int = 0
    next_spawn_timer: float = 3.0 # seconds until next piece
    piece_move_timer: float = 1.0  # seconds until pieces move

    def spawn_apple(self):
        while True:
            pos = Position(random.randrange(GRID_COLS), random.randrange(GRID_ROWS))
            if pos not in [a.pos for a in self.apples] and pos not in [p.pos for p in self.pieces] and pos not in self.snake.body:
                self.apples.append(Apple(pos))
                break

    def spawn_piece(self):
        cls = random.choice([Pawn, Knight, Bishop])
        pos = Position(random.randrange(GRID_COLS), random.randrange(GRID_ROWS))
        if pos in self.snake.body or pos in [a.pos for a in self.apples]:
            return
        self.pieces.append(cls(pos))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.snake.direction != Dir.DOWN:
                    self.snake.direction = Dir.UP
                elif event.key == pygame.K_DOWN and self.snake.direction != Dir.UP:
                    self.snake.direction = Dir.DOWN
                elif event.key == pygame.K_LEFT and self.snake.direction != Dir.RIGHT:
                    self.snake.direction = Dir.LEFT
                elif event.key == pygame.K_RIGHT and self.snake.direction != Dir.LEFT:
                    self.snake.direction = Dir.RIGHT

    def update(self, dt: float):
        self.snake.advance()
        head = self.snake.head()
        
        # Handle apple collision
        for apple in self.apples[:]:
            if apple.pos == head:
                self.score += 10
                self.snake.grow()
                self.apples.remove(apple)
                break
        
        # Handle piece collision
        for piece in self.pieces[:]:
            if piece.pos == head:
                self.score += piece.value
                self.pieces.remove(piece)
                break

        # Move chess pieces
        self.next_spawn_timer -= dt
        if self.next_spawn_timer <= 0:
            self.spawn_piece()
            self.next_spawn_timer = 3.0

        self.piece_move_timer -= dt
        if self.piece_move_timer <= 0:
            for piece in self.pieces[:]:
                piece.move()
                if piece.pos in self.snake.body:
                    pygame.quit()
                    sys.exit()
            self.piece_move_timer = 1.0

        # Knight bullets
        for piece in self.pieces:
            if isinstance(piece, Knight):
                piece.shoot_cooldown -= dt
                if piece.shoot_cooldown <= 0:
                    direction = self._bullet_dir_towards_snake(piece.pos)
                    if direction != (0, 0):
                        self.bullets.append(Bullet(Position(piece.pos.x, piece.pos.y), direction))
                    piece.shoot_cooldown = 2.0
        
        # Update bullets
        for bullet in list(self.bullets):
            bullet.update()
            if bullet.pos == head:
                self.snake.shrink()
                self.bullets.remove(bullet)
                if not self.snake.body:
                    pygame.quit()
                    sys.exit()
        
    def _bullet_dir_towards_snake(self, start: Position) -> Tuple[int,int]:
        hx, hy = self.snake.head().x, self.snake.head().y
        dx = 1 if hx > start.x else -1 if hx < start.x else 0
        dy = 1 if hy > start.y else -1 if hy < start.y else 0
        return dx, dy

    def draw(self, screen):
        screen.fill((0,0,0))
        # Draw grid
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, (40,40,40), rect, 1)
        # Draw snake
        for seg in self.snake.body:
            r = pygame.Rect(seg.x*CELL_SIZE, seg.y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (0,255,0), r)
        # Draw apples
        for apple in self.apples:
            r = pygame.Rect(apple.pos.x*CELL_SIZE, apple.pos.y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (255,0,0), r)
        # Draw pieces
        for piece in self.pieces:
            color = (200,200,0) if isinstance(piece, Pawn) else (0,0,255) if isinstance(piece, Knight) else (255,0,255)
            r = pygame.Rect(piece.pos.x*CELL_SIZE, piece.pos.y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, r)
        # Draw bullets
        for bullet in self.bullets:
            r = pygame.Rect(bullet.pos.x*CELL_SIZE+CELL_SIZE//4, bullet.pos.y*CELL_SIZE+CELL_SIZE//4, CELL_SIZE//2, CELL_SIZE//2)
            pygame.draw.rect(screen, (255,255,255), r)
        # Draw score and spawn timer
        font = pygame.font.SysFont(None, 24)
        score_surf = font.render(f"Score: {self.score}", True, (255,255,255))
        timer_surf = font.render(f"Next in: {self.next_spawn_timer:.1f}s", True, (255,255,255))
        screen.blit(score_surf, (10,10))
        screen.blit(timer_surf, (10,30))
        pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    state = GameState()
    for _ in range(3):
        state.spawn_apple()
    while True:
        dt = clock.tick(FPS) / 1000.0
        state.handle_input()
        state.update(dt)
        state.draw(screen)

if __name__ == "__main__":
    main()
