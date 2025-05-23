import pygame
import sys
import random

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 640, 480
TILE_SIZE = 32
ROWS, COLS = HEIGHT // TILE_SIZE, WIDTH // TILE_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PacTank War")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)

# Maze layout
layout = [
    "####################",
    "#........#.........#",
    "#.####.#.#.#######.#",
    "#.#  #.#.#.#     #.#",
    "#.#  #.#.#.# ### #.#",
    "#.#  #.#.#.# # # #.#",
    "#.####.###.# # ###.#",
    "#..................#",
    "####################",
]

# Sprites
walls = []
pellets = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(walls, all_sprites)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect(topleft=(x, y))

class Pellet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(pellets, all_sprites)
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (4, 4), 4)
        self.rect = self.image.get_rect(center=(x+TILE_SIZE//2, y+TILE_SIZE//2))

class Bullet(pygame.sprite.Sprite):
    SPEED = 8
    def __init__(self, x, y, dx, dy, owner):
        super().__init__(bullets, all_sprites)
        self.image = pygame.Surface((6,6), pygame.SRCALPHA)
        pygame.draw.circle(self.image, owner.color, (3,3), 3)
        self.rect = self.image.get_rect(center=(x,y))
        self.dx, self.dy = dx * self.SPEED, dy * self.SPEED
        self.owner = owner
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if pygame.sprite.spritecollideany(self, walls):
            self.kill()
            return
        if self.owner == player:
            hit = pygame.sprite.spritecollide(self, enemies, True)
            if hit:
                self.kill()
        else:
            if pygame.sprite.collide_rect(self, player):
                pygame.quit()
                sys.exit()

class Tank(pygame.sprite.Sprite):
    SPEED = 2
    def __init__(self, x, y, color):
        super().__init__(all_sprites)
        self.image_orig = pygame.Surface((TILE_SIZE-4, TILE_SIZE-4), pygame.SRCALPHA)
        pygame.draw.rect(self.image_orig, color, self.image_orig.get_rect())
        pygame.draw.rect(self.image_orig, BLACK, (TILE_SIZE//2-4, TILE_SIZE//2-4, 8, 8))
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.dir = pygame.Vector2(1,0)
        self.color = color
        self.fire_cooldown = 0
    def rotate_image(self):
        angle = -self.dir.angle_to(pygame.Vector2(1,0))
        self.image = pygame.transform.rotate(self.image_orig, angle)
        self.rect = self.image.get_rect(center=self.rect.center)
    def move(self, dx, dy):
        if dx or dy:
            self.dir = pygame.Vector2(dx, dy).normalize()
            self.rotate_image()
        self.rect.x += dx * self.SPEED
        if pygame.sprite.spritecollideany(self, walls):
            self.rect.x -= dx * self.SPEED
        self.rect.y += dy * self.SPEED
        if pygame.sprite.spritecollideany(self, walls):
            self.rect.y -= dy * self.SPEED
    def fire(self):
        if self.fire_cooldown <= 0:
            bx = self.rect.centerx + self.dir.x * TILE_SIZE//2
            by = self.rect.centery + self.dir.y * TILE_SIZE//2
            Bullet(bx, by, self.dir.x, self.dir.y, self)
            self.fire_cooldown = 20
    def update(self):
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

class EnemyTank(Tank):
    def __init__(self, x, y):
        super().__init__(x, y, RED)
        enemies.add(self)
    def update(self):
        super().update()
        if random.randint(0, 100) < 2:
            dirs = [(1,0),(-1,0),(0,1),(0,-1)]
            dx, dy = random.choice(dirs)
            self.dir = pygame.Vector2(dx, dy)
            self.rotate_image()
        self.move(int(self.dir.x), int(self.dir.y))
        if random.randint(0,100) < 3:
            self.fire()

# Build level
for row_idx, row in enumerate(layout):
    for col_idx, ch in enumerate(row):
        x, y = col_idx * TILE_SIZE, row_idx * TILE_SIZE
        if ch == "#":
            Wall(x, y)
        elif ch == ".":
            Pellet(x, y)

# Create player and enemies
player = Tank(TILE_SIZE*1.5, TILE_SIZE*1.5, GREEN)
for _ in range(5):
    ex = random.randint(1, COLS-2)
    ey = random.randint(1, len(layout)-2)
    EnemyTank(ex*TILE_SIZE+TILE_SIZE//2, ey*TILE_SIZE+TILE_SIZE//2)

# Game loop
score = 0
font = pygame.font.SysFont(None, 24)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    keys = pygame.key.get_pressed()
    dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
    dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
    player.move(dx, dy)
    if keys[pygame.K_SPACE]:
        player.fire()

    all_sprites.update()

    # Pellet collection
    hits = pygame.sprite.spritecollide(player, pellets, True)
    score += len(hits)

    # Draw
    screen.fill(BLACK)
    all_sprites.draw(screen)
    score_surf = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_surf, (5, HEIGHT-25))
    pygame.display.flip()
    clock.tick(60)
