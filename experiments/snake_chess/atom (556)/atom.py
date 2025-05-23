import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 20 # Size of grid cells
WIDTH, HEIGHT = 800, 600
FPS = 15

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0) # Snake
RED = (255, 0, 0) # Apple
BLUE = (0, 0, 255) # Knight
PURPLE = (128, 0, 128) # Bishop
YELLOW = (255, 255, 0) # Pawn

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake and Chess")
clock = pygame.time.Clock()

class Snake:
    def __init__(self):
        self.body = [(4, 4), (4, 3), (4, 2)] # Initial position
        self.direction = (1, 0)  # Initial direction (moving right)
        self.score = 0
        self.length = len(self.body)

    def grow(self):
        self.body.append((0, 0))  # Placeholder to grow
        self.length += 1

    def move(self):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        self.body = [new_head] + self.body[:-1]  # Move snake

    def draw(self):
        for segment in self.body:
            pygame.draw.rect(screen, GREEN, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

class Apple:
    def __init__(self):
        self.position = self.spawn()

    def spawn(self):
        return (random.randint(0, WIDTH // GRID_SIZE - 1), random.randint(0, HEIGHT // GRID_SIZE - 1))

    def draw(self):
        pygame.draw.rect(screen, RED, (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

class ChessPiece:
    def __init__(self, piece_type, position):
        self.piece_type = piece_type
        self.position = position

    def move(self):
        # Logic for movement based on piece type
        if self.piece_type == 'knight':
            # Implement knight move logic
            pass  # Placeholder for move logic

    def draw(self):
        if self.piece_type == 'knight':
            pygame.draw.rect(screen, BLUE, (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        elif self.piece_type == 'bishop':
            pygame.draw.rect(screen, PURPLE, (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        elif self.piece_type == 'pawn':
            pygame.draw.rect(screen, YELLOW, (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def game_loop():
    snake = Snake()
    apple = Apple()
    chess_pieces = []
    last_piece_spawn_time = time.time()

    running = True
    while running:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Handle direction changes
                if event.key == pygame.K_UP and snake.direction != (0, 1):
                    snake.direction = (0, -1)
                elif event.key == pygame.K_DOWN and snake.direction != (0, -1):
                    snake.direction = (0, 1)
                elif event.key == pygame.K_LEFT and snake.direction != (1, 0):
                    snake.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and snake.direction != (-1, 0):
                    snake.direction = (1, 0)

        # Move the snake and check for collisions
        snake.move()
        snake.draw()
        apple.draw()

        # Check for apple collision
        if snake.body[0] == apple.position:
            snake.grow()
            snake.score += 10
            apple.position = apple.spawn()

        # Spawn chess pieces at regular intervals
        if time.time() - last_piece_spawn_time > 3:  # Every 3 seconds
            piece_type = random.choice(['pawn', 'knight', 'bishop'])
            chess_piece = ChessPiece(piece_type, (random.randint(0, WIDTH // GRID_SIZE - 1),
                                                  random.randint(0, HEIGHT // GRID_SIZE - 1)))
            chess_pieces.append(chess_piece)
            last_piece_spawn_time = time.time()

        # Move chess pieces, check for collisions
        for chess_piece in chess_pieces:
            chess_piece.move()
            chess_piece.draw()
            if chess_piece.position in snake.body:
                running = False  # Game over if snake collides with chess piece

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    game_loop()