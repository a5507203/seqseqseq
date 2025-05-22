import pygame
import random

# Constants
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20
TILE_SIZE = 30
FPS = 60

# Colors
COLORS = [
    (255, 0, 0),   # Red
    (0, 255, 0),   # Green
    (0, 0, 255),   # Blue
    (255, 255, 0), # Yellow
    (255, 165, 0), # Orange
    (128, 0, 128), # Purple
    (0, 255, 255)  # Cyan
]

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]]   # J
]

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Bejeweled Fusion")
        self.clock = pygame.time.Clock()
        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.current_tetromino = self.new_tetromino()
        self.next_tetromino = self.new_tetromino()
        self.score = 0
        self.fall_time = 0
        self.fall_speed = 500  # milliseconds
        self.running = True

    def new_tetromino(self):
        shape = random.choice(SHAPES)
        color = random.choice(COLORS)
        return {'shape': shape, 'color': color, 'x': GRID_WIDTH // 2 - len(shape[0]) // 2, 'y': 0}

    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = COLORS[self.grid[y][x]] if self.grid[y][x] else (0, 0, 0)
                pygame.draw.rect(self.screen, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 0)
                pygame.draw.rect(self.screen, (200, 200, 200), (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

    def draw_tetromino(self, tetromino):
        shape = tetromino['shape']
        color = tetromino['color']
        for y, row in enumerate(shape):
            for x, value in enumerate(row):
                if value:
                    pygame.draw.rect(self.screen, color, ((tetromino['x'] + x) * TILE_SIZE, (tetromino['y'] + y) * TILE_SIZE, TILE_SIZE, TILE_SIZE), 0)

    def lock_tetromino(self):
        shape = self.current_tetromino['shape']
        color_index = COLORS.index(self.current_tetromino['color'])
        for y, row in enumerate(shape):
            for x, value in enumerate(row):
                if value:
                    self.grid[self.current_tetromino['y'] + y][self.current_tetromino['x'] + x] = color_index
        self.clear_lines()
        self.current_tetromino = self.next_tetromino
        self.next_tetromino = self.new_tetromino()

    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                lines_to_clear.append(y)
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [0] * GRID_WIDTH)
            self.score += 100

    def move_tetromino(self, dx):
        self.current_tetromino['x'] += dx
        if self.check_collision():
            self.current_tetromino['x'] -= dx

    def rotate_tetromino(self):
        self.current_tetromino['shape'] = [list(row) for row in zip(*self.current_tetromino['shape'][::-1])]
        if self.check_collision():
            self.current_tetromino['shape'] = [list(row) for row in zip(*self.current_tetromino['shape'])][::-1]

    def check_collision(self):
        shape = self.current_tetromino['shape']
        for y, row in enumerate(shape):
            for x, value in enumerate(row):
                if value:
                    grid_x = self.current_tetromino['x'] + x
                    grid_y = self.current_tetromino['y'] + y
                    if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y >= GRID_HEIGHT or (grid_y >= 0 and self.grid[grid_y][grid_x]):
                        return True
        return False

    def drop_tetromino(self):
        self.current_tetromino['y'] += 1
        if self.check_collision():
            self.current_tetromino['y'] -= 1
            self.lock_tetromino()

    def run(self):
        while self.running:
            self.screen.fill((0, 0, 0))
            self.fall_time += self.clock.get_time()
            if self.fall_time >= self.fall_speed:
                self.drop_tetromino()
                self.fall_time = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.move_tetromino(-1)
                    if event.key == pygame.K_RIGHT:
                        self.move_tetromino(1)
                    if event.key == pygame.K_DOWN:
                        self.drop_tetromino()
                    if event.key == pygame.K_UP:
                        self.rotate_tetromino()

            self.draw_grid()
            self.draw_tetromino(self.current_tetromino)
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()