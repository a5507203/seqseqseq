import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
BLOCK_SIZE = 30             # Size of a single grid block in pixels
grid_width = 10             # Width of the playfield in blocks
grid_height = 20            # Height of the playfield in blocks
SCREEN_WIDTH = BLOCK_SIZE * (grid_width + 6)   # Extra space for next-piece preview and score
SCREEN_HEIGHT = BLOCK_SIZE * grid_height
FPS = 60

# Colors (R, G, B)
COLORS = {
    'I': (0, 240, 240),
    'J': (0, 0, 240),
    'L': (240, 160, 0),
    'O': (240, 240, 0),
    'S': (0, 240, 0),
    'T': (160, 0, 240),
    'Z': (240, 0, 0),
    'BG': (30, 30, 30),
    'GRID': (50, 50, 50),
    'TEXT': (255, 255, 255)
}

# Tetromino shape formats (4x4 grids, rotation states)
SHAPES = {
    'I': [
        ['....', 'IIII', '....', '....'],
        ['..I.', '..I.', '..I.', '..I.']
    ],
    'J': [
        ['J..', 'JJJ', '...', '...'],
        ['.JJ', '.J.', '.J.', '...'],
        ['...', 'JJJ', '..J', '...'],
        ['.J.', '.J.', 'JJ.', '...']
    ],
    'L': [
        ['..L', 'LLL', '...', '...'],
        ['.L.', '.L.', '.LL', '...'],
        ['...', 'LLL', 'L..', '...'],
        ['LL.', '.L.', '.L.', '...']
    ],
    'O': [
        ['.OO.', '.OO.', '....', '....']
    ],
    'S': [
        ['.SS', 'SS.', '...', '...'],
        ['.S.', '.SS', '..S', '...']
    ],
    'T': [
        ['.T.', 'TTT', '...', '...'],
        ['.T.', '.TT', '.T.', '...'],
        ['...', 'TTT', '.T.', '...'],
        ['.T.', 'TT.', '.T.', '...']
    ],
    'Z': [
        ['ZZ.', '.ZZ', '...', '...'],
        ['..Z', '.ZZ', '.Z.', '...']
    ]
}

class Tetromino:
    def __init__(self, shape_key):
        self.shape_key = shape_key
        self.rotations = SHAPES[shape_key]
        self.rotation = 0
        # Start near the top center of the grid
        self.x = grid_width // 2 - 2
        self.y = 0
        self.color = COLORS[shape_key]

    def image(self):
        return self.rotations[self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.rotations)

    def draw(self, surface, offset_x, offset_y):
        pattern = self.image()
        for row_idx, row in enumerate(pattern):
            for col_idx, cell in enumerate(row):
                if cell != '.':
                    px = offset_x + (self.x + col_idx) * BLOCK_SIZE
                    py = offset_y + (self.y + row_idx) * BLOCK_SIZE
                    pygame.draw.rect(surface, self.color, (px, py, BLOCK_SIZE, BLOCK_SIZE))

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Each cell: None or dict with {'color':(R,G,B), 'type':'gem'}
        self.cells = [[None for _ in range(width)] for _ in range(height)]

    def valid_position(self, tetromino, adj_x=0, adj_y=0):
        pattern = tetromino.image()
        for r, row in enumerate(pattern):
            for c, cell in enumerate(row):
                if cell != '.':
                    x = tetromino.x + c + adj_x
                    y = tetromino.y + r + adj_y
                    if x < 0 or x >= self.width or y < 0 or y >= self.height:
                        return False
                    if self.cells[y][x] is not None:
                        return False
        return True

    def lock_tetromino(self, tetromino):
        pattern = tetromino.image()
        for r, row in enumerate(pattern):
            for c, cell in enumerate(row):
                if cell != '.':
                    x = tetromino.x + c
                    y = tetromino.y + r
                    if 0 <= y < self.height and 0 <= x < self.width:
                        self.cells[y][x] = {'color': tetromino.color, 'type': 'gem'}

    def clear_full_lines(self):
        cleared = 0
        new_cells = []
        for row in self.cells:
            if all(cell is not None for cell in row):
                cleared += 1
            else:
                new_cells.append(row)
        for _ in range(cleared):
            new_cells.insert(0, [None for _ in range(self.width)])
        self.cells = new_cells
        return cleared

    def find_matches(self):
        to_clear = set()
        # Horizontal
        for y in range(self.height):
            x = 0
            while x < self.width:
                run = []
                color = None
                while x < self.width and self.cells[y][x] is not None and (color is None or self.cells[y][x]['color'] == color):
                    color = self.cells[y][x]['color']
                    run.append((x, y))
                    x += 1
                if len(run) >= 3:
                    to_clear.update(run)
                if not run:
                    x += 1
        # Vertical
        for x in range(self.width):
            y = 0
            while y < self.height:
                run = []
                color = None
                while y < self.height and self.cells[y][x] is not None and (color is None or self.cells[y][x]['color'] == color):
                    color = self.cells[y][x]['color']
                    run.append((x, y))
                    y += 1
                if len(run) >= 3:
                    to_clear.update(run)
                if not run:
                    y += 1
        return to_clear

    def clear_matches(self, match_cells):
        count = len(match_cells)
        for (x, y) in match_cells:
            self.cells[y][x] = None
        return count

    def apply_gravity(self):
        for x in range(self.width):
            stack = [self.cells[y][x] for y in range(self.height) if self.cells[y][x] is not None]
            for y in range(self.height-1, -1, -1):
                if stack:
                    self.cells[y][x] = stack.pop()
                else:
                    self.cells[y][x] = None

    def draw(self, surface, offset_x, offset_y):
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                rect = (offset_x + x*BLOCK_SIZE, offset_y + y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(surface, COLORS['GRID'], rect, 1)
                if cell is not None:
                    pygame.draw.rect(surface, cell['color'], rect)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("TetriBejeweled")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    grid = Grid(grid_width, grid_height)
    current = Tetromino(random.choice(list(SHAPES.keys())))
    next_piece = Tetromino(random.choice(list(SHAPES.keys())))
    score = 0
    chain_multiplier = 1

    DROP_EVENT = pygame.USEREVENT + 1
    drop_speed = 500  # milliseconds per down-step
    pygame.time.set_timer(DROP_EVENT, drop_speed)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == DROP_EVENT:
                if grid.valid_position(current, adj_y=1):
                    current.y += 1
                else:
                    grid.lock_tetromino(current)
                    lines = grid.clear_full_lines()
                    if lines > 0:
                        score += lines * 100 * chain_multiplier
                        chain_multiplier += 1
                    matched = grid.find_matches()
                    while matched:
                        count = grid.clear_matches(matched)
                        grid.apply_gravity()
                        score += count * 10 * chain_multiplier
                        chain_multiplier += 1
                        matched = grid.find_matches()
                    chain_multiplier = 1
                    current = next_piece
                    next_piece = Tetromino(random.choice(list(SHAPES.keys())))
                    if not grid.valid_position(current):
                        running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and grid.valid_position(current, adj_x=-1):
                    current.x -= 1
                elif event.key == pygame.K_RIGHT and grid.valid_position(current, adj_x=1):
                    current.x += 1
                elif event.key == pygame.K_DOWN and grid.valid_position(current, adj_y=1):
                    current.y += 1
                elif event.key == pygame.K_UP:
                    current.rotate()
                    if not grid.valid_position(current):
                        current.rotate()  # revert

        # Draw everything
        screen.fill(COLORS['BG'])
        grid.draw(screen, 0, 0)
        current.draw(screen, 0, 0)

        # Next-piece preview
        preview_x = grid_width * BLOCK_SIZE + 20
        preview_y = 50
        label = font.render("Next:", True, COLORS['TEXT'])
        screen.blit(label, (preview_x, preview_y - 40))
        temp = Tetromino(next_piece.shape_key)
        temp.draw(screen, preview_x, preview_y)

        # Score display
        score_surf = font.render(f"Score: {score}", True, COLORS['TEXT'])
        screen.blit(score_surf, (preview_x, SCREEN_HEIGHT - 50))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()