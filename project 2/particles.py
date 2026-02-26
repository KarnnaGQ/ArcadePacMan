import arcade
import random
import math

def burst(x, y, count=18, speed=3.0, life=0.35, color=(190, 250, 255)):
    parts = []
    for _ in range(count):
        ang_deg = random.random() * 360.0
        ang = math.radians(ang_deg)
        vx = math.cos(ang)
        vy = math.sin(ang)
        sp = speed * (0.5 + random.random())
        parts.append({
            "x": x, "y": y,
            "vx": vx * sp, "vy": vy * sp,
            "life": life * (0.65 + random.random() * 0.6),
            "t": 0.0,
            "r": 1 + random.random() * 3,
            "c": color
        })
    return parts

def update(parts, dt):
    alive = []
    for p in parts:
        p["t"] += dt
        if p["t"] >= p["life"]:
            continue
        p["x"] += p["vx"] * 60 * dt
        p["y"] += p["vy"] * 60 * dt
        p["vx"] *= 0.95
        p["vy"] *= 0.95
        alive.append(p)
    return alive

def draw(parts):
    for p in parts:
        k = 1.0 - (p["t"] / p["life"])
        a = int(210 * k)
        r = p["r"]
        c = p["c"]
        arcade.draw_circle_filled(p["x"], p["y"], r, (c[0], c[1], c[2], a))
