import arcade
import random
from settings import TILE, ENEMY_SPEED, ENEMY_CHASE_SPEED

DIRS = [(1,0), (-1,0), (0,1), (0,-1)]

def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

class Enemy(arcade.Sprite):
    """Grid-walker with BFS pathfinding + Pac-like roles."""
    def __init__(self, frames_normal, frames_fright, role="chaser"):
        super().__init__()
        self.frames_normal = frames_normal
        self.frames_fright = frames_fright
        self.role = role

        self.frame = 0
        self.anim_t = 0.0
        self.texture = frames_normal[0]

        self.speed = ENEMY_SPEED
        self.target_tile = None
        self.path = []
        self.repath_cd = 0.0
        self.frightened = False

    def _anim(self, dt):
        self.anim_t += dt
        if self.anim_t >= 0.16:
            self.anim_t = 0.0
            self.frame = 1 - self.frame
        frames = self.frames_fright if self.frightened else self.frames_normal
        self.texture = frames[self.frame]

    def _tile_of(self, x, y):
        return (int(x // TILE), int(y // TILE))

    def _center_of(self, tx, ty):
        return (tx * TILE + TILE/2, ty * TILE + TILE/2)

    def _bfs_path(self, start, goal, walkable):
        if start == goal:
            return []
        q = [start]
        prev = {start: None}
        qi = 0
        while qi < len(q):
            cur = q[qi]; qi += 1
            if cur == goal:
                break
            cx, cy = cur
            for dx,dy in DIRS:
                nb = (cx+dx, cy+dy)
                if nb in prev: 
                    continue
                if nb not in walkable:
                    continue
                prev[nb] = cur
                q.append(nb)
        if goal not in prev:
            return []
        path = []
        cur = goal
        while cur is not None and cur != start:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return path

    def _pick_target(self, player_tile, player_dir, pellets_tiles, walkable, rng):
        if self.role == "chaser":
            return player_tile

        if self.role == "ambusher":
            dx,dy = player_dir
            tx,ty = player_tile
            for k in [4,3,2,1]:
                cand = (tx + k*dx, ty + k*dy)
                if cand in walkable:
                    return cand
            return player_tile

        # wander
        if pellets_tiles:
            return rng.choice(pellets_tiles)
        return rng.choice(tuple(walkable))

    def update_ai(self, dt, level, player, player_dir, power_left):
        self._anim(dt)

        self.frightened = power_left > 0.0
        self.speed = (ENEMY_SPEED * 0.85) if self.frightened else ENEMY_CHASE_SPEED

        self.repath_cd = max(0.0, self.repath_cd - dt)

        start = self._tile_of(self.center_x, self.center_y)
        player_tile = self._tile_of(player.center_x, player.center_y)

        pellets_tiles = level.pellet_tiles()
        target = self._pick_target(player_tile, player_dir, pellets_tiles, level.walkable, level.rng)

        if self.frightened:
            samples = [level.rng.choice(tuple(level.walkable)) for _ in range(10)]
            target = max(samples, key=lambda t: manhattan(t, player_tile))

        if (self.target_tile != target) or (not self.path) or (self.repath_cd == 0.0):
            self.target_tile = target
            self.path = self._bfs_path(start, target, level.walkable)
            self.repath_cd = 0.20

        if self.path:
            nx, ny = self.path[0]
            cx, cy = self._center_of(nx, ny)
            dx = cx - self.center_x
            dy = cy - self.center_y
            dist = (dx*dx + dy*dy) ** 0.5
            if dist < 1.0:
                self.center_x, self.center_y = cx, cy
                self.path.pop(0)
                self.change_x = 0
                self.change_y = 0
                return
            ux = dx / dist
            uy = dy / dist
            self.change_x = ux * self.speed
            self.change_y = uy * self.speed
        else:
            self.change_x = 0
            self.change_y = 0
