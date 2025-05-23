import pygame
import random

# Constants
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
FPS = 60

# Colors
COLORS = {
    'I': (0, 255, 255),
    'J': (0, 0, 255),
    'L': (255, 165, 0),
    'O': (255, 255, 0),
    'S': (0, 255, 0),
    'T': (128, 0, 128),
    'Z': (255, 0, 0),
    'GEM_COLORS': [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
}

# Game Initialization
pygame.init()
screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
clock = pygame.time.Clock()

# Grid and Score
grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
score = 0

# Main Game Loop
def game_loop():
    global score
    running = True
    while running:
        screen.fill((0, 0, 0))  # Clear screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
          
        # Handle tetromino actions and logic here
        # Drawing grid, scores, and next tetromino

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

# Start the game
game_loop()