import os
import arcade
import random
from settings import TILE, LEVELS_DIR
from player import Player
from enemy import Enemy

def read_level(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f.readlines()]
    lines = [ln for ln in lines if ln.strip() != ""]
    w = max(len(ln) for ln in lines)
    return [ln.ljust(w, " ") for ln in lines]

class Level:
    def __init__(self, assets, index: int):
        self.assets = assets
        self.index = index
        self.rng = random.Random(1337 + index)

        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self.floor = arcade.SpriteList(use_spatial_hash=True)
        self.pellets = arcade.SpriteList(use_spatial_hash=True)
        self.powers = arcade.SpriteList(use_spatial_hash=True)
        self.keys = arcade.SpriteList(use_spatial_hash=True)
        self.doors = arcade.SpriteList(use_spatial_hash=True)
        self.goals = arcade.SpriteList(use_spatial_hash=True)
        self.teleports = arcade.SpriteList(use_spatial_hash=True)
        self.enemies = arcade.SpriteList()
        self.player = None

        self.tp_points = []
        self.walkable = set()

        self.width_px = 0
        self.height_px = 0

        self._load()

    def _spr(self, tex, x, y, scale=2.0):
        s = arcade.Sprite()
        s.texture = tex
        s.center_x = x
        s.center_y = y
        s.scale = scale
        return s

    def _tile_center(self, c, r, rows):
        x = c * TILE + TILE / 2
        y = (rows - 1 - r) * TILE + TILE / 2
        return x, y

    def _tile_of(self, x, y):
        return (int(x // TILE), int(y // TILE))

    def _load(self):
        path = os.path.join(LEVELS_DIR, f"level{self.index}.txt")
        grid = read_level(path)

        rows = len(grid)
        cols = len(grid[0]) if rows else 0

        self.width_px = cols * TILE
        self.height_px = rows * TILE

        for r in range(rows):
            for c in range(cols):
                ch = grid[r][c]
                x, y = self._tile_center(c, r, rows)

                self.floor.append(self._spr(self.assets.floor, x, y))

                if ch == "#":
                    self.walls.append(self._spr(self.assets.wall, x, y))
                    continue

                
                if ch != "D":
                    self.walkable.add((c, rows-1-r))

                if ch == ".":
                    p = self._spr(self.assets.pellet[0], x, y)
                    p._anim = 0.0
                    self.pellets.append(p)

                elif ch == "o":
                    p = self._spr(self.assets.power[0], x, y)
                    p._anim = 0.0
                    self.powers.append(p)

                elif ch == "K":
                    self.keys.append(self._spr(self.assets.key, x, y))

                elif ch == "D":
                    self.doors.append(self._spr(self.assets.door, x, y))

                elif ch == "G":
                    g = self._spr(self.assets.goal[0], x, y)
                    g._anim = 0.0
                    self.goals.append(g)

                elif ch == "T":
                    t = self._spr(self.assets.tp[0], x, y)
                    t._anim = 0.0
                    self.teleports.append(t)
                    self.tp_points.append((x,y))

                elif ch == "P":
                    self.player = Player(self.assets.player)
                    self.player.center_x = x
                    self.player.center_y = y
                    self.player.scale = 2.0

                elif ch == "E":
                    role = ["chaser","ambusher","wander"][len(self.enemies) % 3]
                    pack = self.assets.enemies[len(self.enemies) % len(self.assets.enemies)]
                    e = Enemy(pack["normal"], pack["fright"], role=role)
                    e.center_x = x
                    e.center_y = y
                    e.scale = 2.0
                    self.enemies.append(e)

        if self.player is None:
            self.player = Player(self.assets.player)
            self.player.center_x = TILE * 2
            self.player.center_y = TILE * 2
            self.player.scale = 2.0

    def animate_tiles(self, dt):
        for s in self.pellets:
            s._anim += dt
            if s._anim >= 0.35:
                s._anim = 0.0
                s.texture = self.assets.pellet[1] if s.texture == self.assets.pellet[0] else self.assets.pellet[0]

        for s in self.powers:
            s._anim += dt
            if s._anim >= 0.18:
                s._anim = 0.0
                s.texture = self.assets.power[1] if s.texture == self.assets.power[0] else self.assets.power[0]

        for s in self.goals:
            s._anim += dt
            if s._anim >= 0.22:
                s._anim = 0.0
                s.texture = self.assets.goal[1] if s.texture == self.assets.goal[0] else self.assets.goal[0]

        for s in self.teleports:
            s._anim += dt
            if s._anim >= 0.16:
                s._anim = 0.0
                s.texture = self.assets.tp[1] if s.texture == self.assets.tp[0] else self.assets.tp[0]

    def pellet_tiles(self):
        out = []
        for s in self.pellets:
            out.append(self._tile_of(s.center_x, s.center_y))
        for s in self.powers:
            out.append(self._tile_of(s.center_x, s.center_y))
        return out

    def open_door_at_player(self):
        p = self.player
        hit = arcade.check_for_collision_with_list(p, self.doors)
        opened = []
        for d in hit:
            tx, ty = self._tile_of(d.center_x, d.center_y)
            self.walkable.add((tx, ty))
            d.texture = self.assets.door_open
            opened.append(d)
        for d in opened:
            d.remove_from_sprite_lists()
        return len(opened) > 0

    def teleport_partner(self, x, y):
        if len(self.tp_points) < 2:
            return None
        best = None
        bestd = -1
        for tx,ty in self.tp_points:
            d = abs(tx-x) + abs(ty-y)
            if d > bestd:
                bestd = d
                best = (tx,ty)
        if best == (x,y):
            for p in self.tp_points:
                if p != (x,y):
                    return p
        return best
