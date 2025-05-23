import pygame
import random
import sys

# --- Configuration Constants ---
CELL_SIZE = 30
COLUMNS = 10
ROWS = 20
GRID_WIDTH = COLUMNS * CELL_SIZE
GRID_HEIGHT = ROWS * CELL_SIZE
PREVIEW_SIZE = 4 * CELL_SIZE
WINDOW_WIDTH = GRID_WIDTH + PREVIEW_SIZE + 40
WINDOW_HEIGHT = GRID_HEIGHT + 60
FPS = 60
DROP_EVENT = pygame.USEREVENT + 1
DROP_INTERVAL = 1000  # milliseconds

# --- Colors ---
COLORS = {
    'I': (0, 240, 240),
    'J': (0, 0, 240),
    'L': (240, 160, 0),
    'O': (240, 240, 0),
    'S': (0, 240, 0),
    'T': (160, 0, 240),
    'Z': (240, 0, 0),
}
EMPTY_COLOR = (40, 40, 40)
BG_COLOR = (0, 0, 0)
GRID_LINE_COLOR = (50, 50, 50)

# --- Tetromino Shapes ---
SHAPES = {
    'I': [
        [(0,1),(1,1),(2,1),(3,1)],
        [(2,0),(2,1),(2,2),(2,3)],
    ],
    'J': [
        [(0,0),(0,1),(1,1),(2,1)],
        [(1,0),(2,0),(1,1),(1,2)],
        [(0,1),(1,1),(2,1),(2,2)],
        [(1,0),(1,1),(0,2),(1,2)],
    ],
    'L': [
        [(2,0),(0,1),(1,1),(2,1)],
        [(1,0),(1,1),(1,2),(2,2)],
        [(0,1),(1,1),(2,1),(0,2)],
        [(0,0),(1,0),(1,1),(1,2)],
    ],
    'O': [
        [(1,0),(2,0),(1,1),(2,1)],
    ],
    'S': [
        [(1,0),(2,0),(0,1),(1,1)],
        [(1,0),(1,1),(2,1),(2,2)],
    ],
    'T': [
        [(1,0),(0,1),(1,1),(2,1)],
        [(1,0),(1,1),(2,1),(1,2)],
        [(0,1),(1,1),(2,1),(1,2)],
        [(1,0),(0,1),(1,1),(1,2)],
    ],
    'Z': [
        [(0,0),(1,0),(1,1),(2,1)],
        [(2,0),(1,1),(2,1),(1,2)],
    ],
}

# --- Helper Classes ---
class Piece:
    def __init__(self, shape):
        self.shape = shape
        self.rotations = SHAPES[shape]
        self.rotation = 0
        self.color = COLORS[shape]
        # Start at top-center
        self.x = COLUMNS // 2 - 2
        self.y = -2
        self.px = self.x * CELL_SIZE
        self.py = self.y * CELL_SIZE
        self.drop_speed = CELL_SIZE / (DROP_INTERVAL / FPS)

    @property
    def blocks(self):
        return [(self.x + bx, self.y + by) for bx, by in self.rotations[self.rotation]]

    def rotate(self, grid):
        prev = self.rotation
        self.rotation = (self.rotation + 1) % len(self.rotations)
        if not grid.valid(self):
            self.rotation = prev

    def move(self, dx, dy, grid):
        self.x += dx
        self.y += dy
        if not grid.valid(self):
            self.x -= dx
            self.y -= dy
            return False
        return True

    def update_pixels(self):
        self.px = self.x * CELL_SIZE
        self.py = self.y * CELL_SIZE

class Grid:
    def __init__(self):
        self.cells = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]

    def inside(self, x, y):
        return 0 <= x < COLUMNS and y < ROWS

    def valid(self, piece):
        for x, y in piece.blocks:
            if not self.inside(x, y) or (y >= 0 and self.cells[y][x] is not None):
                return False
        return True

    def lock_piece(self, piece):
        for x, y in piece.blocks:
            if y >= 0:
                self.cells[y][x] = piece.color

    def clear_lines(self):
        cleared = 0
        for y in range(ROWS - 1, -1, -1):
            if all(self.cells[y][x] is not None for x in range(COLUMNS)):
                del self.cells[y]
                self.cells.insert(0, [None for _ in range(COLUMNS)])
                cleared += 1
        return cleared

    def find_matches(self):
        matched = set()
        # horizontal
        for y in range(ROWS):
            run = []
            last = None
            for x in range(COLUMNS):
                color = self.cells[y][x]
                if color and color == last:
                    run.append((x, y))
                else:
                    if len(run) >= 3:
                        matched.update(run)
                    run = [(x, y)] if color else []
                last = color
            if len(run) >= 3:
                matched.update(run)
        # vertical
        for x in range(COLUMNS):
            run = []
            last = None
            for y in range(ROWS):
                color = self.cells[y][x]
                if color and color == last:
                    run.append((x, y))
                else:
                    if len(run) >= 3:
                        matched.update(run)
                    run = [(x, y)] if color else []
                last = color
            if len(run) >= 3:
                matched.update(run)
        return matched

    def collapse(self):
        for x in range(COLUMNS):
            stack = [self.cells[y][x] for y in range(ROWS) if self.cells[y][x] is not None]
            for y in range(ROWS-1, -1, -1):
                self.cells[y][x] = stack.pop() if stack else None

    def resolve(self, score):
        chain = 0
        total_score = 0
        while True:
            lines = self.clear_lines()
            if lines:
                chain += 1
                total_score += lines * 100 * chain
                self.collapse()
                continue
            matches = self.find_matches()
            if matches:
                chain += 1
                total_score += len(matches) * 50 * chain
                for x, y in matches:
                    self.cells[y][x] = None
                self.collapse()
                continue
            break
        return total_score

# --- Main Game Class ---
class TetrisBejeweled:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris-Bejeweled Fusion")
        self.clock = pygame.time.Clock()
        self.grid = Grid()
        self.score = 0
        self.current = self.next_piece()
        self.next = self.next_piece()
        pygame.time.set_timer(DROP_EVENT, DROP_INTERVAL)
        self.font = pygame.font.SysFont('consolas', 24)

    def next_piece(self):
        return Piece(random.choice(list(SHAPES.keys())))

    def draw_grid(self):
        for y in range(ROWS):
            for x in range(COLUMNS):
                color = self.grid.cells[y][x] or EMPTY_COLOR
                rect = pygame.Rect(20 + x*CELL_SIZE, 20 + y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, GRID_LINE_COLOR, rect, 1)

    def draw_piece(self, piece, preview=False):
        for bx, by in piece.rotations[piece.rotation]:
            x = bx + (piece.x if not preview else 0)
            y = by + (piece.y if not preview else 0)
            px = 20 + x*CELL_SIZE + (0 if not preview else GRID_WIDTH + 40)
            py = 20 + y*CELL_SIZE + (0 if not preview else 0)
            pygame.draw.rect(self.screen, piece.color, (px, py, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(self.screen, GRID_LINE_COLOR, (px, py, CELL_SIZE, CELL_SIZE), 1)

    def draw_preview(self):
        text = self.font.render("Next:", True, (255,255,255))
        self.screen.blit(text, (GRID_WIDTH + 40, 20))
        self.draw_piece(self.next, preview=True)

    def draw_score(self):
        text = self.font.render(f"Score: {self.score}", True, (255,255,255))
        self.screen.blit(text, (GRID_WIDTH + 40, PREVIEW_SIZE + 40))

    def run(self):
        running = True
        drop_speed = 1
        while running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == DROP_EVENT:
                    if not self.current.move(0, 1, self.grid):
                        self.grid.lock_piece(self.current)
                        self.score += self.grid.resolve(self.score)
                        self.current = self.next
                        self.next = self.next_piece()
                        if not self.grid.valid(self.current):
                            running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.current.move(-1, 0, self.grid)
                    elif event.key == pygame.K_RIGHT:
                        self.current.move(1, 0, self.grid)
                    elif event.key == pygame.K_DOWN:
                        self.current.move(0, 1, self.grid)
                    elif event.key == pygame.K_UP:
                        self.current.rotate(self.grid)
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            self.current.update_pixels()

            # Render
            self.screen.fill(BG_COLOR)
            self.draw_grid()
            self.draw_piece(self.current)
            self.draw_preview()
            self.draw_score()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TetrisBejeweled()
    game.run()
