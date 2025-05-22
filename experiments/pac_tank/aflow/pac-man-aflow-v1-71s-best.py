import pygame
import random
import sys

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
TILE_SIZE = 30
MAZE_WIDTH = SCREEN_WIDTH // TILE_SIZE
MAZE_HEIGHT = SCREEN_HEIGHT // TILE_SIZE
FPS = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Game Classes
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.score = 0

    def move(self, direction):
        new_x = self.x + direction[0]
        new_y = self.y + direction[1]
        if 0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT:
            self.x = new_x
            self.y = new_y

    def collect(self, pellets):
        if (self.x, self.y) in pellets:
            self.score += 1
            pellets.remove((self.x, self.y))

class Tank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.bullets = []

    def move(self):
        new_x = self.x + self.direction[0]
        new_y = self.y + self.direction[1]
        if 0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT:
            self.x = new_x
            self.y = new_y
        else:
            self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

    def shoot(self):
        bullet_direction = self.direction
        bullet_x = self.x + bullet_direction[0]
        bullet_y = self.y + bullet_direction[1]
        if 0 <= bullet_x < MAZE_WIDTH and 0 <= bullet_y < MAZE_HEIGHT:
            self.bullets.append((bullet_x, bullet_y))

def draw_maze(screen, player, tanks, pellets):
    screen.fill(BLACK)
    # Draw player
    pygame.draw.rect(screen, YELLOW, (player.x * TILE_SIZE, player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    # Draw tanks
    for tank in tanks:
        pygame.draw.rect(screen, RED, (tank.x * TILE_SIZE, tank.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    # Draw pellets
    for pellet in pellets:
        pygame.draw.circle(screen, WHITE, (pellet[0] * TILE_SIZE + TILE_SIZE // 2, pellet[1] * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 4)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pac-Tank Game")
    clock = pygame.time.Clock()

    # Initialize game objects
    player = Player(1, 1)
    tanks = [Tank(random.randint(0, MAZE_WIDTH - 1), random.randint(0, MAZE_HEIGHT - 1)) for _ in range(3)]
    pellets = [(x, y) for x in range(MAZE_WIDTH) for y in range(MAZE_HEIGHT) if (x, y) != (player.x, player.y)]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player.move(UP)
        if keys[pygame.K_DOWN]:
            player.move(DOWN)
        if keys[pygame.K_LEFT]:
            player.move(LEFT)
        if keys[pygame.K_RIGHT]:
            player.move(RIGHT)

        player.collect(pellets)

        for tank in tanks:
            tank.move()
            if random.random() < 0.1:  # Random chance to shoot
                tank.shoot()

        draw_maze(screen, player, tanks, pellets)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()