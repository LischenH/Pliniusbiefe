# Game Engine: XP, Combo, Scoring

import json
import random


CONSTRUCTION_COLORS = {
    "AcI":                    "#00FF88",
    "PPP":                    "#00FFFF",
    "PPA (PC)":               "#FF6B00",
    "Ablativus absolutus":    "#FFD700",
    "Gerundivum":             "#FF00FF",
    "Gerundium":              "#CC88FF",
    "ut-Satz":                "#00AAFF",
    "Konditionalsatz":        "#FF4444",
    "indirekter Fragesatz":   "#FF00FF",
    "Relativsatz":            "#88FFCC",
    "Komparativ":             "#FFAA00",
    "quo + Komparativ":       "#FFD700",
    "Dativus finalis":        "#FF6B00",
    "Dativus possessoris":    "#FF8C00",
    "Genitivus obiectivus":   "#AA44FF",
    "Irrealis der Gegenwart": "#FF0000",
    "PFA":                    "#00FF00",
    "Lokativ":                "#44AAFF",
    "Infinitiv Präsens Passiv": "#88CCFF",
    "Ablativus qualitatis":   "#FFCC00",
    "Dativ (Bezug)":          "#FF9900",
}

COMBO_MULTIPLIERS = {1: 1.0, 2: 1.2, 3: 1.5, 4: 1.5, 5: 2.0}

XP_REWARDS = {
    "echo_perfect":         100,
    "echo_good":             60,
    "echo_partial":          30,
    "construction_correct":  50,
    "construction_wrong":     0,
    "translation_perfect":  120,
    "translation_good":      70,
    "translation_partial":   35,
    "boss_perfect":         300,
    "boss_good":            180,
    "boss_fail":             20,
}

LEVEL_THRESHOLDS = [
    (0,    "Tiro",           "⚔️"),
    (500,  "Miles",          "🛡️"),
    (1200, "Centurio",       "🏛️"),
    (2500, "Tribunus",       "📜"),
    (5000, "Legatus",        "🦅"),
    (9000, "Consul",         "👑"),
    (15000,"Plinius d.Ä.",   "🌋"),
]


class GameEngine:
    def __init__(self):
        self.total_xp: int = 0
        self.combo: int = 0
        self.max_combo: int = 0
        self.session_xp: int = 0
        self.weakness_tracker: dict = {}  # construction_type -> {correct, total}

    def add_xp(self, reward_key: str) -> tuple[int, float]:
        """Add XP with combo multiplier. Returns (xp_gained, multiplier)."""
        base = XP_REWARDS.get(reward_key, 0)
        mult = COMBO_MULTIPLIERS.get(min(self.combo, 5), 2.0)
        gained = int(base * mult)
        self.total_xp += gained
        self.session_xp += gained
        return gained, mult

    def hit_combo(self):
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)

    def break_combo(self):
        self.combo = 0

    def record_construction(self, ctype: str, correct: bool):
        if ctype not in self.weakness_tracker:
            self.weakness_tracker[ctype] = {"correct": 0, "total": 0}
        self.weakness_tracker[ctype]["total"] += 1
        if correct:
            self.weakness_tracker[ctype]["correct"] += 1

    def get_level(self) -> tuple[str, str, int, int]:
        """Returns (title, emoji, current_level_xp, next_level_xp)."""
        level_data = ("Tiro", "⚔️", 0, 500)
        for i, (thresh, title, emoji) in enumerate(LEVEL_THRESHOLDS):
            if self.total_xp >= thresh:
                next_thresh = LEVEL_THRESHOLDS[i + 1][0] if i + 1 < len(LEVEL_THRESHOLDS) else thresh + 10000
                level_data = (title, emoji, thresh, next_thresh)
        return level_data

    def get_weaknesses(self) -> list[str]:
        """Return construction types with < 70% accuracy, sorted worst first."""
        weak = []
        for ctype, data in self.weakness_tracker.items():
            if data["total"] >= 3:
                acc = data["correct"] / data["total"]
                if acc < 0.7:
                    weak.append((ctype, acc))
        weak.sort(key=lambda x: x[1])
        return [w[0] for w in weak]

    def score_echo(self, original: str, typed: str) -> tuple[str, int]:
        """Score echo mode. Returns (reward_key, percent)."""
        orig_words = original.lower().replace(",", "").replace(";", "").replace(".", "").split()
        typed_words = typed.lower().replace(",", "").replace(";", "").replace(".", "").split()
        if not orig_words:
            return "echo_partial", 0
        correct = sum(1 for w in typed_words if w in orig_words)
        pct = int(100 * correct / len(orig_words))
        if pct >= 95:
            return "echo_perfect", pct
        elif pct >= 70:
            return "echo_good", pct
        else:
            return "echo_partial", pct

    def score_translation(self, sentence: dict, typed: str) -> tuple[str, int]:
        """Score translation by keyword matching. Returns (reward_key, percent)."""
        keywords = [k.lower() for k in sentence.get("keywords", [])]
        typed_lower = typed.lower()
        hits = sum(1 for k in keywords if k in typed_lower)
        pct = int(100 * hits / len(keywords)) if keywords else 50
        if pct >= 90:
            return "translation_perfect", pct
        elif pct >= 65:
            return "translation_good", pct
        else:
            return "translation_partial", pct


# Global singleton
engine = GameEngine()
