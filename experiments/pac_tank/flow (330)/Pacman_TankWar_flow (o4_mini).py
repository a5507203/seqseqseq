
"""Pac-Man Tank War: a single-file pygame game combining Pac-Man maze with Tank War combat.

Controls:
  Arrow keys or WASD – move tank
  Space – shoot shell
  ESC or window close – quit"""

import pygame, sys, random, collections, time

# --- Constants ---
WINDOW_WIDTH, WINDOW_HEIGHT = 640, 480
CELL_SIZE = 32
GRID_COLS = WINDOW_WIDTH // CELL_SIZE
GRID_ROWS = WINDOW_HEIGHT // CELL_SIZE
FPS = 60
INITIAL_LIVES = 3
SCORE_PER_GHOST = 100
SCORE_PER_POWERUP = 50
EXTRA_LIFE_THRESHOLD = 1000

# Colors
BG_COLOR               = (  0,   0,   0)
WALL_COLOR             = (  0,   0, 255)
TANK_COLOR             = (255, 255,   0)
GHOST_NORMAL_COLOR     = (255,   0,   0)
GHOST_VULNERABLE_COLOR = (  0, 255, 255)
SHELL_COLOR            = (255, 255, 255)
POWERUP_COLOR          = (255, 165,   0)
UI_COLOR               = (255, 255, 255)

def generate_map():
    """Build grid with walls, power-ups, and spawn markers."""
    grid = [[0]*GRID_COLS for _ in range(GRID_ROWS)]
    # border walls
    for r in range(GRID_ROWS):
        grid[r][0] = grid[r][GRID_COLS-1] = 1
    for c in range(GRID_COLS):
        grid[0][c] = grid[GRID_ROWS-1][c] = 1
    # internal blocks
    for r in range(2, GRID_ROWS-2, 2):
        for c in range(2, GRID_COLS-2, 2):
            grid[r][c] = 1
            if random.choice([True, False]):
                grid[r][c+1] = 1
            else:
                grid[r+1][c] = 1
    # place power-ups on odd cells
    for r in range(1, GRID_ROWS-1):
        for c in range(1, GRID_COLS-1):
            if grid[r][c]==0 and r%2 and c%2:
                grid[r][c] = 2
    # tank spawn bottom center
    sr, sc = GRID_ROWS-2, GRID_COLS//2
    grid[sr][sc] = 3
    # ghost spawns around center
    cr, cc = GRID_ROWS//2, GRID_COLS//2
    for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        grid[cr+dr][cc+dc] = 4
    return grid

game_map = generate_map()
# precompute static data
tank_spawn = next((r,c) for r in range(GRID_ROWS)
                  for c in range(GRID_COLS) if game_map[r][c]==3)
ghost_spawns = [(r,c) for r in range(GRID_ROWS)
                for c in range(GRID_COLS) if game_map[r][c]==4]
wall_rects = [pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
              for r in range(GRID_ROWS) for c in range(GRID_COLS)
              if game_map[r][c]==1]

class Tank:
    """Player-controlled tank with movement, shooting, lives, and score."""
    def __init__(self, row, col):
        self.row, self.col = row, col
        self.dir_x = self.dir_y = 0
        self.speed = 5.0
        self.lives = INITIAL_LIVES
        self.score = 0
        self.next_extra = EXTRA_LIFE_THRESHOLD
        self.shell = None  # only one shell at a time

    def move(self, grid, dt):
        # attempt move and check wall collision
        nr = self.row + self.dir_y * self.speed * dt
        nc = self.col + self.dir_x * self.speed * dt
        if grid[int(nr)][int(nc)] != 1:
            self.row, self.col = nr, nc

    def shoot(self):
        # fire shell if none active and tank has direction
        if not self.shell and (self.dir_x or self.dir_y):
            self.shell = Shell(self.row, self.col,
                               self.dir_x, self.dir_y)

class Ghost:
    """Enemy that chases tank using BFS or wanders when vulnerable."""
    def __init__(self, row, col):
        self.row, self.col = row, col
        self.dir_x, self.dir_y = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        self.speed = 3.0
        self.state = "normal"
        self.vuln_timer = 0

    def update(self, grid, target, dt):
        # vulnerable countdown
        if self.state=="vulnerable":
            self.vuln_timer -= dt
            if self.vuln_timer<=0:
                self.state="normal"
        # choose direction
        if self.state=="normal":
            step = self.bfs_move(grid,
                                 (int(self.row),int(self.col)),
                                 (int(target.row),int(target.col)))
            if step:
                self.dir_x, self.dir_y = step
        elif random.random()<0.02:
            # random wander
            self.dir_x, self.dir_y = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        # move and bounce on wall
        nr = self.row + self.dir_y * self.speed * dt
        nc = self.col + self.dir_x * self.speed * dt
        if grid[int(nr)][int(nc)]!=1:
            self.row, self.col = nr, nc
        else:
            self.dir_x, self.dir_y = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

    def bfs_move(self, grid, start, goal):
        # BFS to pick next step toward goal
        q = collections.deque([start])
        prev = {start: None}
        while q:
            u = q.popleft()
            if u==goal: break
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                v = (u[0]+dy, u[1]+dx)
                if (0<=v[0]<GRID_ROWS and 0<=v[1]<GRID_COLS
                    and v not in prev and grid[v[0]][v[1]]!=1):
                    prev[v] = u
                    q.append(v)
        if goal not in prev:
            return None
        cur = goal
        while prev[cur]!=start:
            cur = prev[cur]
        return (cur[1]-start[1], cur[0]-start[0])

class Shell:
    """Projectile fired by tank; deactivates on wall hit or collision."""
    def __init__(self, row, col, dx, dy):
        self.row, self.col = row, col
        self.dir_x, self.dir_y = dx, dy
        self.speed = 8.0
        self.active = True

    def update(self, grid, dt):
        if not self.active:
            return
        # move and check wall collision
        self.row += self.dir_y * self.speed * dt
        self.col += self.dir_x * self.speed * dt
        if grid[int(self.row)][int(self.col)]==1:
            self.active = False

class PowerUp:
    """Collectible that increases score and temporarily speeds tank."""
    def __init__(self, row, col):
        self.row, self.col = row, col
        self.active = True

    def apply_to(self, tank):
        tank.score += SCORE_PER_POWERUP
        tank.speed *= 1.1
        pygame.time.set_timer(pygame.USEREVENT+1, 5000)

# --- Pygame setup ---
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pac-Man Tank War")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# instantiate entities
tank = Tank(tank_spawn[0]+0.5, tank_spawn[1]+0.5)
ghosts = [Ghost(r+0.5, c+0.5) for r,c in ghost_spawns]
powerups = [PowerUp(r+0.5, c+0.5)
            for r in range(GRID_ROWS) for c in range(GRID_COLS)
            if game_map[r][c]==2]

running = True
win = lose = False

# --- Drawing helpers ---
def draw_map(s):
    s.fill(BG_COLOR)
    for rect in wall_rects:
        pygame.draw.rect(s, WALL_COLOR, rect)

def draw_powerups(s):
    for pu in powerups:
        x = int(pu.col*CELL_SIZE + CELL_SIZE/2)
        y = int(pu.row*CELL_SIZE + CELL_SIZE/2)
        pygame.draw.circle(s, POWERUP_COLOR, (x,y), CELL_SIZE//4)

def draw_tank(s):
    x = int(tank.col*CELL_SIZE + CELL_SIZE/2)
    y = int(tank.row*CELL_SIZE + CELL_SIZE/2)
    pygame.draw.circle(s, TANK_COLOR, (x,y), CELL_SIZE//2-2)

def draw_ghosts(s):
    for g in ghosts:
        x = int(g.col*CELL_SIZE + CELL_SIZE/2)
        y = int(g.row*CELL_SIZE + CELL_SIZE/2)
        color = (GHOST_VULNERABLE_COLOR if g.state=="vulnerable" else GHOST_NORMAL_COLOR)
        pygame.draw.circle(s, color, (x,y), CELL_SIZE//2-2)

def draw_shell(s):
    s_obj = tank.shell
    if s_obj:
        x = int(s_obj.col*CELL_SIZE)
        y = int(s_obj.row*CELL_SIZE)
        pygame.draw.circle(s, SHELL_COLOR, (x,y), 4)

def draw_ui(s):
    s_surf = font.render(f"Score: {tank.score}", True, UI_COLOR)
    l_surf = font.render(f"Lives: {tank.lives}", True, UI_COLOR)
    s.blit(s_surf, (10,10))
    s.blit(l_surf, (10,30))

# --- Main game loop ---
while running:
    dt = clock.tick(FPS)/1000.0
    # event handling
    for e in pygame.event.get():
        if e.type==pygame.QUIT or (e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE):
            running=False
        elif e.type==pygame.KEYDOWN:
            if e.key in (pygame.K_UP,pygame.K_w):    tank.dir_x, tank.dir_y = 0,-1
            if e.key in (pygame.K_DOWN,pygame.K_s):  tank.dir_x, tank.dir_y = 0,1
            if e.key in (pygame.K_LEFT,pygame.K_a):  tank.dir_x, tank.dir_y = -1,0
            if e.key in (pygame.K_RIGHT,pygame.K_d): tank.dir_x, tank.dir_y = 1,0
            if e.key==pygame.K_SPACE: tank.shoot()
        elif e.type==pygame.USEREVENT+1:
            tank.speed /= 1.1  # reset speed

    # update tank and shell
    tank.move(game_map, dt)
    if tank.shell:
        tank.shell.update(game_map, dt)
        if not tank.shell.active:  # remove inactive shell
            tank.shell = None

    # update ghosts
    for g in ghosts:
        g.update(game_map, tank, dt)

    # collect power-ups
    for pu in powerups:
        if pu.active and int(tank.row)==int(pu.row) and int(tank.col)==int(pu.col):
            pu.active=False
            pu.apply_to(tank)
    # discard inactive power-ups
    powerups = [pu for pu in powerups if pu.active]

    # shell vs ghost collisions
    s_obj = tank.shell
    if s_obj:
        for g in ghosts:
            if s_obj.active and int(s_obj.row)==int(g.row) and int(s_obj.col)==int(g.col):
                s_obj.active=False
                tank.score += SCORE_PER_GHOST
                # extra life?
                if tank.score>=tank.next_extra:
                    tank.lives+=1
                    tank.next_extra+=EXTRA_LIFE_THRESHOLD
                # respawn ghost vulnerable
                sr,sc = random.choice(ghost_spawns)
                g.row, g.col = sr+0.5, sc+0.5
                g.state, g.vuln_timer = "vulnerable", 5.0
        if s_obj and not s_obj.active:
            tank.shell = None

    # ghost vs tank collisions
    for g in ghosts:
        if int(tank.row)==int(g.row) and int(tank.col)==int(g.col):
            if g.state=="normal":
                tank.lives -=1
                # reset tank position
                tr,tc = tank_spawn
                tank.row, tank.col = tr+0.5, tc+0.5
                if tank.lives<=0:
                    lose, running = True, False
            else:
                g.state="normal"

    # check win
    if not powerups:
        win, running = True, False

    # render
    draw_map(screen)
    draw_powerups(screen)
    draw_tank(screen)
    draw_ghosts(screen)
    draw_shell(screen)
    draw_ui(screen)
    pygame.display.flip()

# end screen
screen.fill(BG_COLOR)
msg = "You Win!" if win else "Game Over"
end = font.render(msg, True, UI_COLOR)
screen.blit(end, (WINDOW_WIDTH//2-50, WINDOW_HEIGHT//2-10))
pygame.display.flip()
time.sleep(2)
pygame.quit()
sys.exit()
