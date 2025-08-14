import pygame
import random
from collections import deque

# Constants
CELL_SIZE = 24
MAZE_ROWS = 21
MAZE_COLS = 21
FPS = 60

# Colors
def color(r, g, b):
    return (r, g, b)
BLACK  = color(0, 0, 0)
WHITE  = color(255, 255, 255)
BLUE   = color(0, 0, 255)
RED    = color(255, 0, 0)
YELLOW = color(255, 255, 0)

# Maze with layout, empty cell listing, and drawing
class Maze:
    def __init__(self, layout):
        self.layout = layout
        self.rows = len(layout)
        self.cols = len(layout[0])

    def empty_cells(self):
        cells = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.layout[r][c] == 0:
                    cells.append((r, c))
        return cells

    def draw(self, screen):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.layout[r][c] == 1:
                    rect = pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, BLUE, rect)

# Standard pellet in maze
class Pellet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 6
        self.value = 10
    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size//2)

# Power-up item that allows Pac-Man to eat tanks
class PowerUpItem:
    def __init__(self, x, y, duration_seconds=5):
        self.x = x
        self.y = y
        self.size = CELL_SIZE - 8
        self.color = WHITE
        self.value = 100
        self.duration_frames = duration_seconds * FPS
    def draw(self, screen):
        rect = pygame.Rect(self.x - self.size//2, self.y - self.size//2,
                           self.size, self.size)
        pygame.draw.rect(screen, self.color, rect)

# Persistent bullet placed by tanks; moves until wall then stops
class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction  # (dx, dy)
        self.speed = 4
        self.size = 6
        self.active = True  # moves while active, then remains as pellet

    def update(self, maze):
        if not self.active:
            return
        new_x = self.x + self.direction[0] * self.speed
        new_y = self.y + self.direction[1] * self.speed
        col = int(new_x // CELL_SIZE)
        row = int(new_y // CELL_SIZE)
        # stop if hit wall
        if row < 0 or row >= maze.rows or col < 0 or col >= maze.cols or maze.layout[row][col] == 1:
            self.active = False
        else:
            self.x, self.y = new_x, new_y

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.size//2)

# Player (Pac-Man)
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = CELL_SIZE - 4
        self.color = YELLOW
        self.speed = 2
        self.direction = (0, 0)
        self.score = 0
        self.powered = False
        self.power_timer = 0

    def update(self, maze, pellets, bullets_list, items_list, enemy_tanks, frame_count):
        # Movement
        new_x = self.x + self.direction[0] * self.speed
        new_y = self.y + self.direction[1] * self.speed
        col = int(new_x // CELL_SIZE)
        row = int(new_y // CELL_SIZE)
        if 0 <= row < maze.rows and 0 <= col < maze.cols and maze.layout[row][col] == 0:
            self.x, self.y = new_x, new_y

        # Collect pellets
        for pellet in pellets[:]:
            if self._collides(pellet.x, pellet.y, pellet.size):
                pellets.remove(pellet)
                self.score += pellet.value

        # Collect bullets
        for bullet in bullets_list[:]:
            if self._collides(bullet.x, bullet.y, bullet.size):
                bullets_list.remove(bullet)
                self.score += 50

        # Collect power-ups
        for item in items_list[:]:
            if self._collides(item.x, item.y, item.size):
                items_list.remove(item)
                self.powered = True
                self.power_timer = item.duration_frames
                self.score += item.value

        # Powered state timer
        if self.powered:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.powered = False

        # Eat enemy tanks
        if self.powered:
            for tank in enemy_tanks[:]:
                if self._collides(tank.x, tank.y, tank.size):
                    enemy_tanks.remove(tank)
                    self.score += 200

    def draw(self, screen):
        col = BLUE if self.powered else self.color
        pygame.draw.circle(screen, col, (int(self.x), int(self.y)), self.size//2)

    def _collides(self, ox, oy, osize):
        return (abs(self.x - ox) < (self.size + osize)/2) and (abs(self.y - oy) < (self.size + osize)/2)

# Enemy tank with patrol, BFS chase, shooting, and bullet absorption
class EnemyTank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = CELL_SIZE - 4
        self.color = RED
        self.mode = 'patrol'
        self.speed = 2
        self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        self.shoot_cooldown = FPS * 2  # frames
        self.last_shot = 0

    def update(self, maze, player, frame_count, bullets_list):
        # Absorb bullets
        for bullet in bullets_list[:]:
            if self._collides(bullet.x, bullet.y, bullet.size):
                bullets_list.remove(bullet)
                self._absorb()

        # Mode switch
        dx = player.x - self.x
        dy = player.y - self.y
        if dx*dx + dy*dy < (6*CELL_SIZE)**2:
            self.mode = 'chase'
        else:
            self.mode = 'patrol'

        # Movement
        if self.mode == 'patrol':
            self._patrol(maze)
        else:
            self._chase_bfs(maze, player)

        # Shooting
        if frame_count - self.last_shot > self.shoot_cooldown:
            bullets_list.extend(self._shoot())
            self.last_shot = frame_count

    def _patrol(self, maze):
        new_x = self.x + self.direction[0]*self.speed
        new_y = self.y + self.direction[1]*self.speed
        if not self._hit_wall(new_x, new_y, maze):
            self.x, self.y = new_x, new_y
        else:
            self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

    def _chase_bfs(self, maze, player):
        start = (int(self.y//CELL_SIZE), int(self.x//CELL_SIZE))
        goal  = (int(player.y//CELL_SIZE), int(player.x//CELL_SIZE))
        path = self._bfs(maze, start, goal)
        if path and len(path) > 1:
            nr, nc = path[1]
            dr, dc = nr - start[0], nc - start[1]
            self.x += dc * self.speed
            self.y += dr * self.speed
        else:
            self._patrol(maze)

    def _bfs(self, maze, start, goal):
        rows, cols = maze.rows, maze.cols
        vis = [[False]*cols for _ in range(rows)]
        parent = [[None]*cols for _ in range(rows)]
        q = deque([start]); vis[start[0]][start[1]] = True
        dirs = [(-1,0),(1,0),(0,-1),(0,1)]
        while q:
            r, c = q.popleft()
            if (r,c) == goal: break
            for dr, dc in dirs:
                nr, nc = r+dr, c+dc
                if 0<=nr<rows and 0<=nc<cols and not vis[nr][nc] and maze.layout[nr][nc]==0:
                    vis[nr][nc]=True; parent[nr][nc]=(r,c); q.append((nr,nc))
        if not vis[goal[0]][goal[1]]:
            return None
        path=[]; node=goal
        while node:
            path.append(node)
            node = parent[node[0]][node[1]]
        return path[::-1]

    def _shoot(self):
        shots=[]
        for d in [(1,0),(-1,0),(0,1),(0,-1)]:
            bx = self.x + d[0]*(self.size//2)
            by = self.y + d[1]*(self.size//2)
            shots.append(Bullet(bx, by, d))
        return shots

    def _hit_wall(self, x, y, maze):
        col = int(x//CELL_SIZE); row = int(y//CELL_SIZE)
        if row<0 or row>=maze.rows or col<0 or col>=maze.cols:
            return True
        return maze.layout[row][col]==1

    def _absorb(self):
        floor_cd = FPS//2
        self.shoot_cooldown = max(floor_cd, self.shoot_cooldown - FPS//4)

    def _collides(self, ox, oy, os):
        return (abs(self.x-ox)<(self.size+os)/2) and (abs(self.y-oy)<(self.size+os)/2)

    def draw(self, screen):
        rect = pygame.Rect(self.x-self.size//2, self.y-self.size//2,
                           self.size, self.size)
        pygame.draw.rect(screen, self.color, rect)

# Main game function
def main():
    pygame.init()
    screen = pygame.display.set_mode((MAZE_COLS*CELL_SIZE, MAZE_ROWS*CELL_SIZE))
    pygame.display.set_caption("Pac-Tank Maze")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # Create a simple border maze
    layout = [[1]*MAZE_COLS] + [[1]+[0]*(MAZE_COLS-2)+[1] for _ in range(MAZE_ROWS-2)] + [[1]*MAZE_COLS]
    maze = Maze(layout)

    # Initialize pellets
    pellets = []
    for (r,c) in maze.empty_cells():
        x = c*CELL_SIZE + CELL_SIZE//2
        y = r*CELL_SIZE + CELL_SIZE//2
        pellets.append(Pellet(x, y))

    bullets_list = []
    items_list = []

    player = Player(CELL_SIZE*2+CELL_SIZE//2, CELL_SIZE*2+CELL_SIZE//2)
    enemy_tanks = []
    spawn_pts = [(MAZE_ROWS-3,MAZE_COLS-3),(MAZE_ROWS-3,2),(2,MAZE_COLS-3)]
    for (r,c) in spawn_pts:
        x = c*CELL_SIZE + CELL_SIZE//2
        y = r*CELL_SIZE + CELL_SIZE//2
        enemy_tanks.append(EnemyTank(x, y))

    frame_count = 0
    running = True
    while running:
        clock.tick(FPS)
        frame_count += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:    player.direction = (0, -1)
                elif event.key == pygame.K_DOWN: player.direction = (0, 1)
                elif event.key == pygame.K_LEFT: player.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT:player.direction = (1, 0)
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    player.direction = (0, 0)

        # Spawn power-up occasionally
        if frame_count % (FPS*20) == 0 and len(items_list) < 2:
            r, c = random.choice(maze.empty_cells())
            x = c*CELL_SIZE + CELL_SIZE//2
            y = r*CELL_SIZE + CELL_SIZE//2
            items_list.append(PowerUpItem(x, y))

        # Updates
        player.update(maze, pellets, bullets_list, items_list, enemy_tanks, frame_count)
        for bullet in bullets_list:
            bullet.update(maze)
        for tank in enemy_tanks:
            tank.update(maze, player, frame_count, bullets_list)

        # Game over if collide with tank while not powered
        if not player.powered:
            for tank in enemy_tanks:
                if player._collides(tank.x, tank.y, tank.size):
                    running = False

        # Draw phase
        screen.fill(BLACK)
        maze.draw(screen)
        for pellet in pellets:   pellet.draw(screen)
        for bullet in bullets_list:   bullet.draw(screen)
        for item in items_list:   item.draw(screen)
        player.draw(screen)
        for tank in enemy_tanks:   tank.draw(screen)

        # Score display
        score_surf = font.render(f"Score: {player.score}", True, WHITE)
        screen.blit(score_surf, (10, 10))
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()

