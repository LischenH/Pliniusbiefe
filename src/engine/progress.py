# Progress: Save/Load to local JSON

import json
import os
from pathlib import Path


SAVE_PATH = Path(__file__).parent.parent.parent / "data" / "progress.json"


def load_progress() -> dict:
    if SAVE_PATH.exists():
        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return _default_progress()


def save_progress(data: dict):
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _default_progress() -> dict:
    return {
        "total_xp": 0,
        "dungeon_scores": {},   # dungeon_id -> best_score (0-100)
        "weakness_tracker": {},
        "sessions": 0,
        "max_combo": 0,
    }


def update_dungeon_score(progress: dict, dungeon_id: int, score: int):
    key = str(dungeon_id)
    current = progress["dungeon_scores"].get(key, 0)
    progress["dungeon_scores"][key] = max(current, score)


def is_dungeon_unlocked(progress: dict, dungeon_id: int, unlock_threshold: int) -> bool:
    if dungeon_id == 1:
        return True
    prev_key = str(dungeon_id - 1)
    prev_score = progress["dungeon_scores"].get(prev_key, 0)
    return prev_score >= unlock_threshold
