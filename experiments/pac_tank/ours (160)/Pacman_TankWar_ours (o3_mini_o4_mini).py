
import pygame
import random
import sys
from collections import deque

# Constants
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20
COLS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE
FPS = 60

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
FLASH_COLOR = (255, 100, 100)

# Directions
DIRS = {
    'UP': (0, -1),
    'DOWN': (0, 1),
    'LEFT': (-1, 0),
    'RIGHT': (1, 0)
}
DIR_VECTORS = list(DIRS.values())

# Special item types
SPECIAL_ITEM_DURATION = 7000  # milliseconds
SPECIAL_ITEM_SPAWN_INTERVAL = 15000  # milliseconds

# Player invulnerability blinking frequency
BLINK_INTERVAL = 250  # milliseconds


def generate_maze(cols, rows):
    """
    Generate a maze using recursive backtracking.
    Maze grid: 1 = wall, 0 = path
    """

    maze = [[1 for _ in range(cols)] for _ in range(rows)]

    def carve_passages(cx, cy):
        maze[cy][cx] = 0
        directions = list(DIRS.values())
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = cx + dx * 2, cy + dy * 2
            if 0 <= nx < cols and 0 <= ny < rows and maze[ny][nx] == 1:
                maze[cy + dy][cx + dx] = 0
                carve_passages(nx, ny)

    # Start carving from (1,1)
    carve_passages(1, 1)

    # Make sure start and some other spots are open
    maze[1][1] = 0
    maze[rows - 2][cols - 2] = 0

    return maze


def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def bfs_path(start, goal, maze):
    """
    Breadth-first search to find path from start to goal in maze.
    Returns list of positions or empty list if no path.
    """
    if start == goal:
        return [start]

    queue = deque()
    queue.append((start, [start]))
    visited = set()
    visited.add(start)
    while queue:
        (x, y), path = queue.popleft()
        for dx, dy in DIR_VECTORS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] == 0:
                if (nx, ny) == goal:
                    return path + [(nx, ny)]
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
    return []


class Player:
    def __init__(self, x, y, maze):
        self.x = x
        self.y = y
        self.maze = maze
        self.pixel_x = x * CELL_SIZE
        self.pixel_y = y * CELL_SIZE
        self.speed = 4  # pixels per frame
        self.move_dir = (0, 0)
        self.target_cell = (x, y)
        self.moving = False
        self.score = 0
        self.special_mode = False
        self.special_mode_end_time = 0
        self.blink = False
        self.blink_timer = 0

    def can_move(self, dx, dy):
        nx, ny = self.x + dx, self.y + dy
        return 0 <= nx < COLS and 0 <= ny < ROWS and self.maze[ny][nx] == 0

    def set_direction(self, dx, dy):
        if (dx, dy) == (0, 0):
            return
        if self.moving:
            # Only allow direction change if aligned to cell
            if self.pixel_x % CELL_SIZE == 0 and self.pixel_y % CELL_SIZE == 0:
                if self.can_move(dx, dy):
                    self.move_dir = (dx, dy)
                    self.target_cell = (self.x + dx, self.y + dy)
        else:
            if self.can_move(dx, dy):
                self.move_dir = (dx, dy)
                self.target_cell = (self.x + dx, self.y + dy)
                self.moving = True

    def update(self, pellets, bullets, special_items, enemies):
        # Move player pixel-wise toward target_cell
        if self.moving:
            target_px = self.target_cell[0] * CELL_SIZE
            target_py = self.target_cell[1] * CELL_SIZE
            dx = dy = 0
            if self.pixel_x < target_px:
                dx = min(self.speed, target_px - self.pixel_x)
            elif self.pixel_x > target_px:
                dx = -min(self.speed, self.pixel_x - target_px)
            if self.pixel_y < target_py:
                dy = min(self.speed, target_py - self.pixel_y)
            elif self.pixel_y > target_py:
                dy = -min(self.speed, self.pixel_y - target_py)
            self.pixel_x += dx
            self.pixel_y += dy

            if self.pixel_x == target_px and self.pixel_y == target_py:
                self.x, self.y = self.target_cell
                self.moving = False

                # Automatically continue moving in the same direction if possible
                next_x, next_y = self.x + self.move_dir[0], self.y + self.move_dir[1]
                if self.can_move(self.move_dir[0], self.move_dir[1]):
                    self.target_cell = (next_x, next_y)
                    self.moving = True

        # Collect pellets
        if (self.x, self.y) in pellets:
            pellets.remove((self.x, self.y))
            self.score += 10

        # Collect bullets (persistent bullets act as pellets)
        if (self.x, self.y) in bullets.positions():
            bullets.collect_at(self.x, self.y)
            self.score += 20

        # Collect special items
        for item in special_items[:]:
            if (self.x, self.y) == (item.x, item.y):
                special_items.remove(item)
                self.activate_special_mode()

        # If in special mode, update timer and blinking
        now = pygame.time.get_ticks()
        if self.special_mode:
            if now >= self.special_mode_end_time:
                self.special_mode = False
                self.blink = False
            else:
                # Blink effect for visual feedback
                if now - self.blink_timer > BLINK_INTERVAL:
                    self.blink = not self.blink
                    self.blink_timer = now

        # Check collision with enemies
        for enemy in enemies:
            if (self.x, self.y) == (enemy.x, enemy.y):
                if self.special_mode:
                    # Eat enemy tank
                    enemy.respawn()
                    self.score += 100
                else:
                    # Player loses - game over
                    return 'dead'
        return 'alive'

    def activate_special_mode(self):
        self.special_mode = True
        self.special_mode_end_time = pygame.time.get_ticks() + SPECIAL_ITEM_DURATION
        self.blink = True
        self.blink_timer = pygame.time.get_ticks()

    def draw(self, screen):
        pos = (self.pixel_x + CELL_SIZE // 2, self.pixel_y + CELL_SIZE // 2)
        if self.special_mode and self.blink:
            color = FLASH_COLOR
        else:
            color = YELLOW
        pygame.draw.circle(screen, color, pos, CELL_SIZE // 2 - 2)


class Bullets:
    """
    Manage all bullets in the maze.
    Bullets do not move once shot; they remain on the cell until collected or absorbed.
    """

    def __init__(self):
        self.bullets = []  # List of bullets: each bullet is (x, y, direction), direction for reference only

    def add(self, x, y, direction):
        # Only add bullet if no bullet already present at position
        if not any(b.x == x and b.y == y for b in self.bullets):
            self.bullets.append(Bullet(x, y, direction))

    def positions(self):
        return [(b.x, b.y) for b in self.bullets]

    def collect_at(self, x, y):
        for b in self.bullets:
            if b.x == x and b.y == y:
                self.bullets.remove(b)
                return True
        return False

    def absorb_at(self, x, y):
        """
        Remove bullet at (x,y) to be absorbed by tank.
        Returns True if bullet absorbed, else False.
        """
        for b in self.bullets:
            if b.x == x and b.y == y:
                self.bullets.remove(b)
                return True
        return False

    def draw(self, screen):
        for bullet in self.bullets:
            bullet.draw(screen)


class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction  # direction vector, unused for movement since bullets are static

    def draw(self, screen):
        px = self.x * CELL_SIZE + CELL_SIZE // 2
        py = self.y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, WHITE, (px, py), 5)


class Tank:
    def __init__(self, x, y, maze, bullets):
        self.spawn_x = x
        self.spawn_y = y
        self.x = x
        self.y = y
        self.maze = maze
        self.bullets = bullets  # Reference to Bullets manager to add bullets
        self.shooting_rate = 1.0  # bullets per second
        self.last_shot_time = 0
        self.chase_range = 8  # Manhattan distance to switch modes
        self.mode = 'patrol'  # or 'chase'
        self.patrol_path = self.generate_patrol_path()
        self.patrol_index = 0
        self.speed = 1  # cells per second (tank moves slower than player)
        self.pixel_x = x * CELL_SIZE
        self.pixel_y = y * CELL_SIZE
        self.move_dir = (0, 0)
        self.target_cell = (x, y)
        self.moving = False
        self.powered_up = False
        self.power_up_time = 0  # time when powered-up status ends
        self.move_accumulator = 0  # accumulator for movement timing

    def respawn(self):
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.pixel_x = self.x * CELL_SIZE
        self.pixel_y = self.y * CELL_SIZE
        self.mode = 'patrol'
        self.shooting_rate = 1.0
        self.powered_up = False
        self.power_up_time = 0
        self.patrol_index = 0
        self.moving = False
        self.move_dir = (0, 0)
        self.target_cell = (self.x, self.y)

    def generate_patrol_path(self):
        """
        Generate a simple square patrol path around the tank's spawn position.
        If no neighbors, stay in place.
        """
        path = []
        cx, cy = self.x, self.y
        # Try to build a small loop around starting pos
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and self.maze[ny][nx] == 0:
                path.append((nx, ny))
        if not path:
            path.append((cx, cy))
        return path

    def can_move(self, x, y):
        return 0 <= x < COLS and 0 <= y < ROWS and self.maze[y][x] == 0

    def move_towards(self, target_x, target_y):
        """
        Move one step towards target_x, target_y using simple heuristic BFS pathfinding.
        """
        path = bfs_path((self.x, self.y), (target_x, target_y), self.maze)
        if len(path) > 1:
            next_pos = path[1]
            self.set_target(next_pos[0], next_pos[1])

    def set_target(self, tx, ty):
        if (tx, ty) == (self.x, self.y):
            self.moving = False
            self.move_dir = (0, 0)
            self.target_cell = (self.x, self.y)
            return
        dx = tx - self.x
        dy = ty - self.y
        if abs(dx) + abs(dy) == 1 and self.can_move(tx, ty):
            self.move_dir = (dx, dy)
            self.target_cell = (tx, ty)
            self.moving = True

    def update_position(self, dt):
        """
        Move pixel-wise toward target cell at self.speed cells per second.
        """
        if not self.moving:
            return

        pixels_per_sec = self.speed * CELL_SIZE
        pixels_to_move = pixels_per_sec * dt

        target_px = self.target_cell[0] * CELL_SIZE
        target_py = self.target_cell[1] * CELL_SIZE

        dx = dy = 0
        if self.pixel_x < target_px:
            dx = min(pixels_to_move, target_px - self.pixel_x)
        elif self.pixel_x > target_px:
            dx = -min(pixels_to_move, self.pixel_x - target_px)

        if self.pixel_y < target_py:
            dy = min(pixels_to_move, target_py - self.pixel_y)
        elif self.pixel_y > target_py:
            dy = -min(pixels_to_move, self.pixel_y - target_py)

        self.pixel_x += dx
        self.pixel_y += dy

        if self.pixel_x == target_px and self.pixel_y == target_py:
            self.x, self.y = self.target_cell
            self.moving = False

    def patrol(self):
        if not self.patrol_path:
            return
        target = self.patrol_path[self.patrol_index]
        if (self.x, self.y) == target:
            self.patrol_index = (self.patrol_index + 1) % len(self.patrol_path)
            target = self.patrol_path[self.patrol_index]
        self.set_target(*target)

    def chase(self, player):
        if manhattan_distance((self.x, self.y), (player.x, player.y)) <= self.chase_range:
            self.move_towards(player.x, player.y)

    def absorb_bullets(self, bullets):
        """
        Absorb bullets on current cell to power up shooting rate.
        """
        if bullets.absorb_at(self.x, self.y):
            self.shooting_rate = min(self.shooting_rate + 0.5, 5.0)
            self.powered_up = True
            self.power_up_time = pygame.time.get_ticks() + 10000  # powered up lasts 10 seconds

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= 1000 / self.shooting_rate:
            # Shoot bullet in a random valid direction (if possible)
            directions = DIR_VECTORS.copy()
            random.shuffle(directions)
            for dx, dy in directions:
                bx, by = self.x + dx, self.y + dy
                if self.can_move(bx, by):
                    # Add bullet to bullets manager
                    self.bullets.add(bx, by, (dx, dy))
                    self.last_shot_time = now
                    break

    def update_mode(self, player):
        dist = manhattan_distance((self.x, self.y), (player.x, player.y))
        if self.mode == 'patrol' and dist <= self.chase_range:
            self.mode = 'chase'
        elif self.mode == 'chase' and dist > self.chase_range:
            self.mode = 'patrol'

    def update(self, player, bullets, dt):
        # Update powered-up status expiration
        if self.powered_up and pygame.time.get_ticks() > self.power_up_time:
            self.powered_up = False
            self.shooting_rate = max(self.shooting_rate - 1.0, 1.0)

        self.update_mode(player)

        if not self.moving:
            if self.mode == 'patrol':
                self.patrol()
            elif self.mode == 'chase':
                self.chase(player)

        self.update_position(dt)
        self.absorb_bullets(bullets)
        self.shoot()

    def draw(self, screen):
        px = int(self.pixel_x)
        py = int(self.pixel_y)
        rect = pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)
        color = ORANGE if self.powered_up else GREY
        pygame.draw.rect(screen, color, rect.inflate(-4, -4))
        # Draw eyes for direction feedback
        eye_radius = 3
        cx, cy = px + CELL_SIZE // 2, py + CELL_SIZE // 2
        # Simple eyes on left and right side
        pygame.draw.circle(screen, BLACK, (cx - 5, cy - 3), eye_radius)
        pygame.draw.circle(screen, BLACK, (cx + 5, cy - 3), eye_radius)


class SpecialItem:
    """
    Special item that allows player to eat tanks temporarily.
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.blink = False
        self.blink_timer = 0

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.blink_timer > BLINK_INTERVAL:
            self.blink = not self.blink
            self.blink_timer = now

    def draw(self, screen):
        px = self.x * CELL_SIZE + CELL_SIZE // 2
        py = self.y * CELL_SIZE + CELL_SIZE // 2
        color = GREEN if self.blink else WHITE
        pygame.draw.circle(screen, color, (px, py), CELL_SIZE // 3)
        # Draw a star or special shape
        pygame.draw.circle(screen, BLACK, (px, py), CELL_SIZE // 3, 2)


def find_free_position(maze, exclude_positions):
    """
    Find a random free position in maze that is not in exclude_positions.
    """
    free_positions = [(x, y) for y in range(ROWS) for x in range(COLS) if maze[y][x] == 0 and (x, y) not in exclude_positions]
    if free_positions:
        return random.choice(free_positions)
    else:
        return None


def draw_maze(screen, maze):
    for y in range(ROWS):
        for x in range(COLS):
            if maze[y][x] == 1:
                pygame.draw.rect(screen, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def draw_pellets(screen, pellets):
    for x, y in pellets:
        px = x * CELL_SIZE + CELL_SIZE // 2
        py = y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, WHITE, (px, py), 4)


def draw_text(screen, text, x, y, size=24, color=WHITE):
    font = pygame.font.SysFont("Arial", size, bold=True)
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Tank Maze")
    clock = pygame.time.Clock()

    # Generate maze
    maze = generate_maze(COLS, ROWS)

    # Generate pellets on all walkable cells except player start and tank starts
    pellets = []
    for y in range(ROWS):
        for x in range(COLS):
            if maze[y][x] == 0:
                pellets.append((x, y))

    # Initialize player position (safe start)
    player_start = (1, 1)
    if player_start in pellets:
        pellets.remove(player_start)

    # Initialize Bullets manager
    bullets = Bullets()

    # Initialize tanks at random free positions, avoiding player start
    tanks = []
    exclude_positions = {player_start}
    tank_starts = []
    for _ in range(3):
        pos = find_free_position(maze, exclude_positions)
        if pos is None:
            break
        tank_starts.append(pos)
        exclude_positions.add(pos)

    for pos in tank_starts:
        tanks.append(Tank(pos[0], pos[1], maze, bullets))

    # Remove tanks' start positions from pellets to avoid immediate collection
    for pos in tank_starts:
        if pos in pellets:
            pellets.remove(pos)

    # Initialize player
    player = Player(player_start[0], player_start[1], maze)

    # Special items list
    special_items = []
    last_special_spawn = pygame.time.get_ticks()

    # Game state
    game_over = False
    game_over_timer = 0

    while True:
        dt = clock.tick(FPS) / 1000.0  # delta time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if not game_over:
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[pygame.K_UP]:
                dx, dy = DIRS['UP']
            elif keys[pygame.K_DOWN]:
                dx, dy = DIRS['DOWN']
            elif keys[pygame.K_LEFT]:
                dx, dy = DIRS['LEFT']
            elif keys[pygame.K_RIGHT]:
                dx, dy = DIRS['RIGHT']

            player.set_direction(dx, dy)

            # Update player
            player_status = player.update(pellets, bullets, special_items, tanks)
            if player_status == 'dead':
                game_over = True
                game_over_timer = pygame.time.get_ticks()

            # Update tanks
            for tank in tanks:
                tank.update(player, bullets, dt)

            # Update special items
            for item in special_items:
                item.update()

            # Spawn special item at intervals
            now = pygame.time.get_ticks()
            if now - last_special_spawn > SPECIAL_ITEM_SPAWN_INTERVAL:
                # Spawn special item at random free location not occupied by player/tanks/pellets/bullets
                occupied = set(pellets) | set(bullets.positions()) | {(player.x, player.y)} | {(t.x, t.y) for t in tanks} | {(item.x, item.y) for item in special_items}
                pos = find_free_position(maze, occupied)
                if pos:
                    special_items.append(SpecialItem(pos[0], pos[1]))
                last_special_spawn = now

        # Drawing
        screen.fill(BLACK)
        draw_maze(screen, maze)
        draw_pellets(screen, pellets)
        bullets.draw(screen)
        for item in special_items:
            item.draw(screen)
        player.draw(screen)
        for tank in tanks:
            tank.draw(screen)

        draw_text(screen, f"Score: {player.score}", 10, 10)
        if player.special_mode:
            remaining = max(0, (player.special_mode_end_time - pygame.time.get_ticks()) // 1000)
            draw_text(screen, f"Special Mode: {remaining}s", 10, 40, size=20, color=GREEN)

        if game_over:
            draw_text(screen, "GAME OVER", WIDTH // 2 - 100, HEIGHT // 2 - 30, size=48, color=RED)
            draw_text(screen, "Press R to Restart or Q to Quit", WIDTH // 2 - 180, HEIGHT // 2 + 20, size=24, color=RED)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                main()
                return
            if keys[pygame.K_q]:
                pygame.quit()
                sys.exit()

        pygame.display.flip()


if __name__ == "__main__":
    main()
