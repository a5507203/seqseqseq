import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Piece values
PIECE_VALUES = {'pawn': 5, 'knight': 10, 'bishop': 15}

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Game classes
class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.length = 1
        self.score = 0

    def move(self):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = ((head_x + dir_x) % GRID_WIDTH, (head_y + dir_y) % GRID_HEIGHT)
        self.body.insert(0, new_head)
        if len(self.body) > self.length:
            self.body.pop()

    def grow(self):
        self.length += 1
        self.score += 10

    def capture_piece(self, piece_value):
        self.score += piece_value

    def get_head(self):
        return self.body[0]

class ChessPiece:
    def __init__(self, piece_type):
        self.type = piece_type
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        self.alive = True

    def move(self):
        if self.type == 'pawn':
            # Pawns don't move in this implementation
            pass
        elif self.type == 'knight':
            # Knights can shoot bullets
            pass
        elif self.type == 'bishop':
            # Bishops don't move in this implementation
            pass

# Game setup
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Chess")
    clock = pygame.time.Clock()

    snake = Snake()
    apples = [(random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))]
    chess_pieces = [ChessPiece(random.choice(['pawn', 'knight', 'bishop'])) for _ in range(3)]
    next_piece_spawn_time = 5
    last_piece_spawn_time = time.time()

    running = True
    while running:
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != DOWN:
                    snake.direction = UP
                elif event.key == pygame.K_DOWN and snake.direction != UP:
                    snake.direction = DOWN
                elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                    snake.direction = LEFT
                elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                    snake.direction = RIGHT

        # Move snake
        snake.move()

        # Check for apple collision
        if snake.get_head() in apples:
            apples.remove(snake.get_head())
            snake.grow()
            apples.append((random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)))

        # Check for chess piece collision
        for piece in chess_pieces:
            if piece.alive and snake.get_head() == piece.position:
                piece.alive = False
                snake.capture_piece(PIECE_VALUES[piece.type])

        # Draw snake
        for segment in snake.body:
            pygame.draw.rect(screen, GREEN, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Draw apples
        for apple in apples:
            pygame.draw.rect(screen, RED, (apple[0] * GRID_SIZE, apple[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Draw chess pieces
        for piece in chess_pieces:
            if piece.alive:
                color = BLUE if piece.type == 'knight' else WHITE
                pygame.draw.rect(screen, color, (piece.position[0] * GRID_SIZE, piece.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Display score
        font = pygame.font.SysFont(None, 35)
        score_text = font.render(f'Score: {snake.score}', True, WHITE)
        screen.blit(score_text, (10, 10))

        # Update display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()