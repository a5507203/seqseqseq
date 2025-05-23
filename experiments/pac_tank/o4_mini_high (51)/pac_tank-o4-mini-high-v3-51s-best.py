import pygame
import random
from collections import deque

# Game constants
SCREEN_WIDTH, SCREEN_HEIGHT = 672, 744  # 28x31 grid * 24px
CELL_SIZE = 24
FPS = 60

# Colors
BLACK = (0, 0, 0)
NAVY = (10, 10, 50)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (200, 30, 30)
GREEN = (30, 200, 30)
BLUE = (30, 30, 200)
ORANGE = (255, 165, 0)

# Simple maze layout: 0 = path, 1 = wall
MAZE = [
    [1]*28,
    [1] + [0]*26 + [1],
    [1] + [0,1]*13 + [1],
    [1] + [0]*26 + [1],
] + [[1]*28] * 27  # fill out to 31 rows; replace with your design

# Utility functions
def grid_to_pixel(pos):
    x, y = pos
    return x * CELL_SIZE, y * CELL_SIZE

def pixel_to_grid(pos):
    x, y = pos
    return x // CELL_SIZE, y // CELL_SIZE

def neighbors(cell):
    x, y = cell
    for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        nx, ny = x+dx, y+dy
        if 0 <= nx < len(MAZE[0]) and 0 <= ny < len(MAZE):
            if MAZE[ny][nx] == 0:
                yield (nx, ny)

def bfs(start, goal):
    """Return next step towards goal via BFS, or None."""
    queue = deque([start])
    prev = {start: None}
    while queue:
        cur = queue.popleft()
        if cur == goal:
            break
        for nb in neighbors(cur):
            if nb not in prev:
                prev[nb] = cur
                queue.append(nb)
    if goal not in prev:
        return None
    # backtrack
    step = goal
    while prev[step] != start:
        step = prev[step]
    return step

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(topleft=grid_to_pixel(pos))
        self.grid_pos = pos
        self.dir = (0, 0)
        self.speed = 3  # pixels per frame
        self.powered = False
        self.power_timer = 0

    def update(self, walls):
        # Move pixel-wise, then update grid_pos if centered
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.dir = (-1, 0)
        if keys[pygame.K_RIGHT]: self.dir = (1, 0)
        if keys[pygame.K_UP]: self.dir = (0, -1)
        if keys[pygame.K_DOWN]: self.dir = (0, 1)

        dx, dy = self.dir
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        # collide with walls
        for w in walls:
            if self.rect.colliderect(w):
                # undo move
                self.rect.x -= dx * self.speed
                self.rect.y -= dy * self.speed
                break

        # update grid_pos if near center
        gx, gy = pixel_to_grid(self.rect.center)
        self.grid_pos = (gx, gy)

        if self.powered:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.powered = False
                self.image.fill(YELLOW)

class Tank(pygame.sprite.Sprite):
    def __init__(self, pos, patrol_points):
        super().__init__()
        self.base_rate = 180  # frames between shots
        self.shoot_rate = self.base_rate
        self.shoot_timer = random.randint(0, self.shoot_rate)
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=grid_to_pixel(pos))
        self.grid_pos = pos
        self.speed = 2
        self.dir = (0, 0)
        self.patrol = patrol_points
        self.patrol_i = 0
        self.mode = 'patrol'  # or 'chase'

    def update(self, player, walls, bullets_group):
        # Determine mode
        if abs(self.grid_pos[0] - player.grid_pos[0]) + abs(self.grid_pos[1] - player.grid_pos[1]) < 8:
            self.mode = 'chase'
        else:
            self.mode = 'patrol'

        # Decide next grid target
        if self.mode == 'chase':
            next_cell = bfs(self.grid_pos, player.grid_pos)
        else:
            target = self.patrol[self.patrol_i]
            if self.grid_pos == target:
                self.patrol_i = (self.patrol_i + 1) % len(self.patrol)
                target = self.patrol[self.patrol_i]
            next_cell = bfs(self.grid_pos, target)

        if next_cell:
            dx = next_cell[0] - self.grid_pos[0]
            dy = next_cell[1] - self.grid_pos[1]
            self.dir = (dx, dy)
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
            gx, gy = pixel_to_grid(self.rect.center)
            self.grid_pos = (gx, gy)

        # Shooting
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            bx = self.grid_pos[0] + self.dir[0]
            by = self.grid_pos[1] + self.dir[1]
            if 0 <= bx < len(MAZE[0]) and 0 <= by < len(MAZE) and MAZE[by][bx] == 0:
                bullets_group.add(Bullet((bx, by)))
            self.shoot_timer = self.shoot_rate

    def power_up(self):
        self.shoot_rate = max(30, int(self.shoot_rate * 0.9))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((CELL_SIZE//2, CELL_SIZE//2))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect()
        self.rect.center = grid_to_pixel(pos)[0] + CELL_SIZE//2, grid_to_pixel(pos)[1] + CELL_SIZE//2
        self.grid_pos = pos

class Pellet(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((CELL_SIZE//4, CELL_SIZE//4))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = grid_to_pixel(pos)[0] + CELL_SIZE//2, grid_to_pixel(pos)[1] + CELL_SIZE//2
        self.grid_pos = pos

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((CELL_SIZE//2, CELL_SIZE//2))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = grid_to_pixel(pos)[0] + CELL_SIZE//2, grid_to_pixel(pos)[1] + CELL_SIZE//2
        self.grid_pos = pos

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Tank Fusion")
        self.clock = pygame.time.Clock()
        self.score = 0

        # Sprite groups
        self.walls = []
        self.player_group = pygame.sprite.GroupSingle()
        self.tanks = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.pellets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        self.load_maze()
        self.spawn_player()
        self.spawn_pellets()
        self.spawn_tanks()
        self.spawn_powerups()

    def load_maze(self):
        for y, row in enumerate(MAZE):
            for x, cell in enumerate(row):
                if cell == 1:
                    wall = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    self.walls.append(wall)

    def spawn_player(self):
        start = (1, 1)
        self.player_group.add(Player(start))

    def spawn_pellets(self):
        for y, row in enumerate(MAZE):
            for x, cell in enumerate(row):
                if cell == 0 and (x,y) not in [(1,1)]:
                    self.pellets.add(Pellet((x,y)))

    def spawn_tanks(self):
        # Example patrol routes
        patrol1 = [(26,1),(26,3),(24,3),(24,1)]
        self.tanks.add(Tank((26,1), patrol1))

    def spawn_powerups(self):
        for _ in range(3):
            while True:
                x = random.randint(1, len(MAZE[0]) - 2)
                y = random.randint(1, len(MAZE) - 2)
                if MAZE[y][x] == 0:
                    self.powerups.add(PowerUp((x,y)))
                    break

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False

            self.update()
            self.draw()

        pygame.quit()

    def update(self):
        player = self.player_group.sprite
        player.update(self.walls)

        # Update tanks
        for tank in self.tanks:
            tank.update(player, self.walls, self.bullets)

        # Collisions: player & pellets
        eaten = pygame.sprite.spritecollide(player, self.pellets, True)
        self.score += len(eaten) * 10

        # player & bullets
        bullets_eaten = pygame.sprite.spritecollide(player, self.bullets, True)
        self.score += len(bullets_eaten) * 50

        # tanks absorb bullets
        for tank in self.tanks:
            hits = pygame.sprite.spritecollide(tank, self.bullets, True)
            for _ in hits:
                tank.power_up()

        # player & powerups
        pu = pygame.sprite.spritecollide(player, self.powerups, True)
        if pu:
            player.powered = True
            player.power_timer = FPS * 8
            player.image.fill(GREEN)

        # player eats tanks when powered
        if player.powered:
            dead = pygame.sprite.spritecollide(player, self.tanks, True)
            self.score += len(dead) * 500
            # respawn after delay
            for _ in dead:
                self.spawn_tanks()

    def draw(self):
        self.screen.fill(NAVY)
        # draw walls
        for w in self.walls:
            pygame.draw.rect(self.screen, BLUE, w)
        # draw pellets, bullets, powerups
        self.pellets.draw(self.screen)
        self.bullets.draw(self.screen)
        self.powerups.draw(self.screen)
        # draw sprites
        self.player_group.draw(self.screen)
        self.tanks.draw(self.screen)
        # draw score
        font = pygame.font.SysFont(None, 36)
        txt = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(txt, (10, SCREEN_HEIGHT - 40))
        pygame.display.flip()

if __name__ == "__main__":
    Game().run()