import csv
import os
from settings import HIGHSCORES_PATH, DATA_DIR

def _ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(HIGHSCORES_PATH), exist_ok=True)

def load_best_score() -> int:
    _ensure_dirs()
    if not os.path.exists(HIGHSCORES_PATH):
        return 0
    try:
        with open(HIGHSCORES_PATH, "r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            return 0
        return max(int(r.get("best_score", 0)) for r in rows)
    except Exception:
        return 0

def save_best_score(best_score: int):
    _ensure_dirs()
    current = load_best_score()
    if best_score <= current:
        return
    with open(HIGHSCORES_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["best_score"])
        w.writeheader()
        w.writerow({"best_score": int(best_score)})
