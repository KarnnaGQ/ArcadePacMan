import arcade
from settings import (
    SCREEN_W, SCREEN_H, TILE,
    CAMERA_LERP,
    PELLET_SCORE, POWER_SCORE, KEY_SCORE, ENEMY_EAT_SCORE, WIN_BONUS,
    POWER_TIME, LIVES
)
from assets import Assets, play
from level import Level
from particles import burst, update as pupdate, draw as pdraw
from save import load_best_score, save_best_score

def clamp(v, a, b):
    return max(a, min(b, v))

def sign_dir(dx, dy):
    if abs(dx) > abs(dy):
        return (1,0) if dx > 0 else (-1,0) if dx < 0 else (1,0)
    if abs(dy) > 0:
        return (0,1) if dy > 0 else (0,-1)
    return (1,0)

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.assets = Assets()
        self.best = load_best_score()

    def on_show_view(self):
        arcade.set_background_color((10, 10, 15))

    def on_draw(self):
        self.clear()
        arcade.draw_text("PacMan", SCREEN_W/2, SCREEN_H*0.70,
                         (255, 220, 70), 40, anchor_x="center")
        arcade.draw_text("ENTER - Старт", SCREEN_W/2, SCREEN_H*0.48,
                         (190, 250, 255), 18, anchor_x="center")
        arcade.draw_text("H - Как играть", SCREEN_W/2, SCREEN_H*0.42,
                         (190, 250, 255), 16, anchor_x="center")
        arcade.draw_text("ESC - Выйти из игры", SCREEN_W/2, SCREEN_H*0.36,
                         (190, 250, 255), 16, anchor_x="center")
        arcade.draw_text(f"Лучший скор: {self.best}", SCREEN_W/2, SCREEN_H*0.24,
                         (120, 255, 120), 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.ENTER, arcade.key.RETURN, arcade.key.NUM_ENTER):
            play(self.assets.snd_click)
            self.window.show_view(GameView(self.assets, level_index=1, score=0, lives=LIVES))
        elif key == arcade.key.H:
            play(self.assets.snd_click)
            self.window.show_view(HowToView(self.assets))
        elif key == arcade.key.ESCAPE:
            arcade.close_window()

class HowToView(arcade.View):
    def __init__(self, assets):
        super().__init__()
        self.assets = assets

    def on_show_view(self):
        arcade.set_background_color((10, 10, 15))

    def on_draw(self):
        self.clear()
        arcade.draw_text("Как играть", SCREEN_W/2, SCREEN_H*0.78, (190,250,255), 36, anchor_x="center")
        txt = [
            "WASD - двигаться",
            "Пробел - рывок",
            "P - пауза",
            "Собери все очки, для того чтобы пройти на уровень",
            "Сильные очки позволяют есть призраков",
            "Ключ открывает дверь",
            "Зайдите в дверь как соберете все очки",
            "",
            "ENTER - вернуться в меню"
        ]
        y = SCREEN_H*0.65
        for line in txt:
            arcade.draw_text(line, SCREEN_W/2, y, (255,220,70), 16, anchor_x="center")
            y -= 28

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.ENTER, arcade.key.RETURN, arcade.key.NUM_ENTER, arcade.key.ESCAPE):
            self.window.show_view(MenuView())

class GameView(arcade.View):
    def __init__(self, assets: Assets, level_index: int, score: int, lives: int):
        super().__init__()
        self.assets = assets
        self.level_index = level_index
        self.score = score
        self.lives = lives

        self.level = Level(self.assets, index=self.level_index)
        self.blockers = arcade.SpriteList(use_spatial_hash=True)
        self.blockers.extend(self.level.walls)
        self.blockers.extend(self.level.doors)
        self.ph_player = arcade.PhysicsEngineSimple(self.level.player, self.blockers)

        self.keys = {"w": False, "a": False, "s": False, "d": False}
        self.pause = False

        self.power_left = 0.0
        self.invuln = 0.0
        self.tp_cd = 0.0

        # Camera2D (Arcade 3.x)
        self.cam = arcade.Camera2D()
        self.ui_cam = arcade.Camera2D()

        self.parts = []
        self.best = load_best_score()
        self.last_move = (1,0)

    def on_show_view(self):
        arcade.set_background_color((10, 10, 15))

    def _input_move(self):
        dx = (1 if self.keys["d"] else 0) - (1 if self.keys["a"] else 0)
        dy = (1 if self.keys["w"] else 0) - (1 if self.keys["s"] else 0)
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        if abs(dx)+abs(dy) > 0.01:
            self.last_move = sign_dir(dx, dy)
        self.level.player.set_move(dx, dy)

    def _camera_follow(self):
        px = self.level.player.center_x
        py = self.level.player.center_y

        tx = px - SCREEN_W / 2
        ty = py - SCREEN_H / 2

        max_x = max(0, self.level.width_px - SCREEN_W)
        max_y = max(0, self.level.height_px - SCREEN_H)
        tx = clamp(tx, 0, max_x)
        ty = clamp(ty, 0, max_y)

        target_cx = tx + SCREEN_W / 2
        target_cy = ty + SCREEN_H / 2

        cx, cy = self.cam.position
        nx = cx + (target_cx - cx) * CAMERA_LERP
        ny = cy + (target_cy - cy) * CAMERA_LERP
        self.cam.position = (nx, ny)
    def _collect(self):
        p = self.level.player

        got = arcade.check_for_collision_with_list(p, self.level.pellets)
        for it in got:
            self.score += PELLET_SCORE
            self.parts += burst(it.center_x, it.center_y, count=10, speed=2.2, color=(190,250,255))
            it.remove_from_sprite_lists()
            play(self.assets.snd_pickup)

        got2 = arcade.check_for_collision_with_list(p, self.level.powers)
        for it in got2:
            self.score += POWER_SCORE
            self.power_left = POWER_TIME
            self.parts += burst(it.center_x, it.center_y, count=26, speed=3.2, color=(120,255,120))
            it.remove_from_sprite_lists()
            play(self.assets.snd_power)

        got3 = arcade.check_for_collision_with_list(p, self.level.keys)
        for it in got3:
            self.score += KEY_SCORE
            p.has_key = True
            self.parts += burst(it.center_x, it.center_y, count=22, speed=3.0, color=(255,220,70))
            it.remove_from_sprite_lists()
            play(self.assets.snd_pickup)

        if p.has_key:
            if self.level.open_door_at_player():
                p.has_key = False
                self.ph_player = arcade.PhysicsEngineSimple(self.level.player, self.level.walls)
                play(self.assets.snd_click)

    def _teleport(self, dt):
        if self.tp_cd > 0:
            self.tp_cd = max(0.0, self.tp_cd - dt)
            return
        p = self.level.player
        hit = arcade.check_for_collision_with_list(p, self.level.teleports)
        if not hit:
            return
        partner = self.level.teleport_partner(hit[0].center_x, hit[0].center_y)
        if partner is None:
            return
        px, py = partner
        p.center_x = px
        p.center_y = py
        self.tp_cd = 0.7
        self.parts += burst(px, py, count=30, speed=3.6, color=(190,250,255))
        play(self.assets.snd_power)

    def _enemy_update(self, dt):
        for e in self.level.enemies:
            e.update_ai(dt, self.level, self.level.player, self.last_move, self.power_left)
            e.center_x += e.change_x
            e.center_y += e.change_y

    def _enemy_collide(self):
        if self.invuln > 0:
            return
        p = self.level.player
        hit = arcade.check_for_collision_with_list(p, self.level.enemies)
        if not hit:
            return

        if self.power_left > 0:
            for e in hit:
                self.score += ENEMY_EAT_SCORE
                self.parts += burst(e.center_x, e.center_y, count=32, speed=3.5, color=(255,170,80))
                e.remove_from_sprite_lists()
            return

        play(self.assets.snd_hit)
        self.lives -= 1
        self.invuln = 1.2
        self.parts += burst(p.center_x, p.center_y, count=40, speed=4.0, color=(255,80,90))

        p.center_x = TILE * 2
        p.center_y = TILE * 2

        if self.lives <= 0:
            if self.score > self.best:
                save_best_score(self.score)
            self.window.show_view(GameOverView(self.assets, self.score))

    def _win_check(self):
        if len(self.level.pellets) + len(self.level.powers) > 0:
            return
        p = self.level.player
        if arcade.check_for_collision_with_list(p, self.level.goals):
            self.score += WIN_BONUS
            play(self.assets.snd_win)

            next_i = self.level_index + 1
            if next_i <= 3:
                self.window.show_view(GameView(self.assets, next_i, self.score, self.lives))
            else:
                if self.score > self.best:
                    save_best_score(self.score)
                self.window.show_view(WinView(self.assets, self.score))

    def on_update(self, dt):
        if self.pause:
            return

        self._input_move()
        self.level.player.update_logic(dt)
        self.ph_player.update()

        self.level.animate_tiles(dt)
        self._enemy_update(dt)

        if self.power_left > 0:
            self.power_left = max(0.0, self.power_left - dt)
        if self.invuln > 0:
            self.invuln = max(0.0, self.invuln - dt)

        self._collect()
        self._teleport(dt)
        self._enemy_collide()
        self._win_check()

        self.parts = pupdate(self.parts, dt)
        self._camera_follow()

    def on_draw(self):
        self.clear()

        self.cam.use()
        self.level.floor.draw()
        self.level.walls.draw()
        self.level.pellets.draw()
        self.level.powers.draw()
        self.level.keys.draw()
        self.level.doors.draw()
        self.level.goals.draw()
        self.level.teleports.draw()

        self.level.enemies.draw()
        arcade.draw_sprite(self.level.player)

        pdraw(self.parts)        
        self.ui_cam.position = (SCREEN_W / 2, SCREEN_H / 2)
        self.ui_cam.use()

        arcade.draw_text(f"Очки: {self.score}", 16, SCREEN_H - 28, (190, 250, 255), 14)
        arcade.draw_text(f"Жизни: {self.lives}", 16, SCREEN_H - 50, (255, 80, 90), 12)
        arcade.draw_text(f"Уровень: {self.level_index}/3", SCREEN_W - 16, SCREEN_H - 28, (190, 250, 255), 12, anchor_x="right")

        best_now = max(self.best, self.score)
        arcade.draw_text(f"Лучший скор: {best_now}", SCREEN_W - 16, SCREEN_H - 50, (120, 255, 120), 12, anchor_x="right")

        if self.power_left > 0:
            arcade.draw_text(f"Сила: {self.power_left:0.1f}", SCREEN_W/2, SCREEN_H - 28, (120, 255, 120), 14, anchor_x="center")

        if self.pause:
            arcade.draw_text("Пауза", SCREEN_W/2, SCREEN_H/2, (255,220,70), 42, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W: self.keys["w"] = True
        if key == arcade.key.A: self.keys["a"] = True
        if key == arcade.key.S: self.keys["s"] = True
        if key == arcade.key.D: self.keys["d"] = True

        if key == arcade.key.SPACE:
            if self.level.player.try_dash():
                self.parts += burst(self.level.player.center_x, self.level.player.center_y, count=18, speed=2.8, color=(255,220,70))

        if key == arcade.key.P:
            self.pause = not self.pause
            play(self.assets.snd_click)

        if key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W: self.keys["w"] = False
        if key == arcade.key.A: self.keys["a"] = False
        if key == arcade.key.S: self.keys["s"] = False
        if key == arcade.key.D: self.keys["d"] = False

class GameOverView(arcade.View):
    def __init__(self, assets, score):
        super().__init__()
        self.assets = assets
        self.score = score
        self.best = load_best_score()

    def on_show_view(self):
        arcade.set_background_color((8, 8, 12))

    def on_draw(self):
        self.clear()
        arcade.draw_text("GAME OVER", SCREEN_W/2, SCREEN_H*0.62, (255, 80, 90), 48, anchor_x="center")
        self.ui_cam.position = (SCREEN_W / 2, SCREEN_H / 2)
        self.ui_cam.use()

        arcade.draw_text(f"SCORE: {self.score}", SCREEN_W/2, SCREEN_H*0.46, (190, 250, 255), 20, anchor_x="center")
        arcade.draw_text(f"BEST: {self.best}", SCREEN_W/2, SCREEN_H*0.40, (120, 255, 120), 16, anchor_x="center")
        arcade.draw_text("ENTER - RESTART", SCREEN_W/2, SCREEN_H*0.28, (255, 220, 70), 16, anchor_x="center")
        arcade.draw_text("ESC - MENU", SCREEN_W/2, SCREEN_H*0.23, (255, 220, 70), 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.ENTER, arcade.key.RETURN, arcade.key.NUM_ENTER):
            play(self.assets.snd_click)
            self.window.show_view(GameView(self.assets, 1, 0, LIVES))
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())

class WinView(arcade.View):
    def __init__(self, assets, score):
        super().__init__()
        self.assets = assets
        self.score = score
        self.best = load_best_score()

    def on_show_view(self):
        arcade.set_background_color((8, 12, 10))

    def on_draw(self):
        self.clear()
        arcade.draw_text("YOU WIN!", SCREEN_W/2, SCREEN_H*0.62, (120, 255, 120), 56, anchor_x="center")
        self.ui_cam.position = (SCREEN_W / 2, SCREEN_H / 2)
        self.ui_cam.use()

        arcade.draw_text(f"SCORE: {self.score}", SCREEN_W/2, SCREEN_H*0.46, (190, 250, 255), 20, anchor_x="center")
        arcade.draw_text(f"BEST: {self.best}", SCREEN_W/2, SCREEN_H*0.40, (120, 255, 120), 16, anchor_x="center")
        arcade.draw_text("ENTER - PLAY AGAIN", SCREEN_W/2, SCREEN_H*0.28, (255, 220, 70), 16, anchor_x="center")
        arcade.draw_text("ESC - MENU", SCREEN_W/2, SCREEN_H*0.23, (255, 220, 70), 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.ENTER, arcade.key.RETURN, arcade.key.NUM_ENTER):
            play(self.assets.snd_click)
            self.window.show_view(GameView(self.assets, 1, 0, LIVES))
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())
