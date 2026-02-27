import arcade
from settings import PLAYER_SPEED, PLAYER_DASH_SPEED, PLAYER_DASH_TIME, PLAYER_DASH_COOLDOWN

class Player(arcade.Sprite):
    def __init__(self, tex_by_dir):
        super().__init__()
        self.tex_by_dir = tex_by_dir
        self.dir = "right"
        self.frame = 0
        self.anim_t = 0.0
        self.texture = self.tex_by_dir[self.dir][0]

        self.vx = 0.0
        self.vy = 0.0

        self.dash_left = 0.0
        self.dash_cd = 0.0

        self.has_key = False

    def set_move(self, dx, dy):
        if abs(dx) > abs(dy):
            if dx > 0: self.dir = "right"
            if dx < 0: self.dir = "left"
        elif abs(dy) > 0:
            if dy > 0: self.dir = "up"
            if dy < 0: self.dir = "down"

        self.vx = dx * PLAYER_SPEED
        self.vy = dy * PLAYER_SPEED

    def try_dash(self):
        if self.dash_cd > 0:
            return False
        if abs(self.vx) + abs(self.vy) < 0.01:
            return False
        self.dash_left = PLAYER_DASH_TIME
        self.dash_cd = PLAYER_DASH_COOLDOWN
        return True

    def update_logic(self, dt):
        if self.dash_cd > 0:
            self.dash_cd = max(0.0, self.dash_cd - dt)

        mul = 1.0
        if self.dash_left > 0:
            self.dash_left = max(0.0, self.dash_left - dt)
            mul = PLAYER_DASH_SPEED / PLAYER_SPEED

        self.change_x = self.vx * mul
        self.change_y = self.vy * mul

        moving = abs(self.change_x) + abs(self.change_y) > 0.01
        if moving:
            self.anim_t += dt
            if self.anim_t >= 0.10:
                self.anim_t = 0.0
                self.frame = 1 - self.frame
        else:
            self.frame = 0

        self.texture = self.tex_by_dir[self.dir][self.frame]
