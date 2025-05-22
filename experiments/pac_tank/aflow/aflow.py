import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TANK_SIZE = 40
PELLET_SIZE = 20
ENEMY_SIZE = 40
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battlefield Game")

# Tank class
class Tank:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, TANK_SIZE, TANK_SIZE)
        self.speed = 5

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.rect.x = max(0, min(SCREEN_WIDTH - TANK_SIZE, self.rect.x))
        self.rect.y = max(0, min(SCREEN_HEIGHT - TANK_SIZE, self.rect.y))

    def draw(self):
        pygame.draw.rect(screen, GREEN, self.rect)

# Pellet class
class Pellet:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, SCREEN_WIDTH - PELLET_SIZE), 
                                 random.randint(0, SCREEN_HEIGHT - PELLET_SIZE), 
                                 PELLET_SIZE, PELLET_SIZE)

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

# Enemy class
class Enemy:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, SCREEN_WIDTH - ENEMY_SIZE), 
                                 random.randint(0, SCREEN_HEIGHT - ENEMY_SIZE), 
                                 ENEMY_SIZE, ENEMY_SIZE)
        self.speed = 2

    def move(self):
        direction = random.choice([(self.speed, 0), (-self.speed, 0), (0, self.speed), (0, -self.speed)])
        self.rect.x += direction[0]
        self.rect.y += direction[1]
        self.rect.x = max(0, min(SCREEN_WIDTH - ENEMY_SIZE, self.rect.x))
        self.rect.y = max(0, min(SCREEN_HEIGHT - ENEMY_SIZE, self.rect.y))

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)

# Main game loop
def main():
    clock = pygame.time.Clock()
    tank = Tank()
    pellets = [Pellet() for _ in range(10)]
    enemies = [Enemy() for _ in range(5)]
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        tank.move(dx, dy)

        # Check for collisions with pellets
        for pellet in pellets[:]:
            if tank.rect.colliderect(pellet.rect):
                pellets.remove(pellet)
                score += 1

        # Move enemies
        for enemy in enemies:
            enemy.move()

        # Draw everything
        screen.fill(BLACK)
        tank.draw()
        for pellet in pellets:
            pellet.draw()
        for enemy in enemies:
            enemy.draw()

        # Display score
        font = pygame.font.Font(None, 36)
        text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
