import os
import arcade

def load_tex(path: str):
    if not os.path.exists(path):
        return None
    try:
        return arcade.load_texture(path)
    except Exception:
        return None

def load_sound_safe(path: str):
    if not os.path.exists(path):
        return None
    try:
        return arcade.load_sound(path)
    except Exception:
        return None

def play(sound):
    if sound is None:
        return
    try:
        arcade.play_sound(sound)
    except Exception:
        pass

class Assets:
    def __init__(self):
        sp = "assets/sprites"
        self.floor = load_tex(os.path.join(sp, "floor.png"))
        self.wall = load_tex(os.path.join(sp, "wall.png"))

        self.pellet = [load_tex(os.path.join(sp, "pellet_0.png")), load_tex(os.path.join(sp, "pellet_1.png"))]
        self.power  = [load_tex(os.path.join(sp, "power_0.png")),  load_tex(os.path.join(sp, "power_1.png"))]
        self.goal   = [load_tex(os.path.join(sp, "goal_0.png")),   load_tex(os.path.join(sp, "goal_1.png"))]
        self.tp     = [load_tex(os.path.join(sp, "teleport_0.png")), load_tex(os.path.join(sp, "teleport_1.png"))]

        self.key = load_tex(os.path.join(sp, "key.png"))
        self.door = load_tex(os.path.join(sp, "door.png"))
        self.door_open = load_tex(os.path.join(sp, "door_open.png"))

        self.player = {
            "up":    [load_tex(os.path.join(sp, "player_up_0.png")),    load_tex(os.path.join(sp, "player_up_1.png"))],
            "down":  [load_tex(os.path.join(sp, "player_down_0.png")),  load_tex(os.path.join(sp, "player_down_1.png"))],
            "left":  [load_tex(os.path.join(sp, "player_left_0.png")),  load_tex(os.path.join(sp, "player_left_1.png"))],
            "right": [load_tex(os.path.join(sp, "player_right_0.png")), load_tex(os.path.join(sp, "player_right_1.png"))],
        }

        self.enemies = []
        for i in [1,2,3]:
            normal = [load_tex(os.path.join(sp, f"enemy{i}_0.png")), load_tex(os.path.join(sp, f"enemy{i}_1.png"))]
            fright = [load_tex(os.path.join(sp, f"enemy{i}_fright_0.png")), load_tex(os.path.join(sp, f"enemy{i}_fright_1.png"))]
            self.enemies.append({"normal": normal, "fright": fright})

        sd = "assets/sounds"
        self.snd_pickup = load_sound_safe(os.path.join(sd, "pickup.wav"))
        self.snd_power  = load_sound_safe(os.path.join(sd, "power.wav"))
        self.snd_hit    = load_sound_safe(os.path.join(sd, "hit.wav"))
        self.snd_win    = load_sound_safe(os.path.join(sd, "win.wav"))
        self.snd_click  = load_sound_safe(os.path.join(sd, "click.wav"))
