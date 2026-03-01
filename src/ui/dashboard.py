# Dashboard: Dungeon Map + Mode Selection

import json
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from src.engine.progress import is_dungeon_unlocked
from src.ui.hud_widget import make_separator


DATA_PATH = Path(__file__).parent.parent.parent / "data" / "texts.json"


def load_dungeons() -> list[dict]:
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)["dungeons"]


class DungeonCard(QFrame):
    """Card for one dungeon (Teil I–X)."""
    selected = Signal(dict)

    def __init__(self, dungeon: dict, unlocked: bool, best_score: int, parent=None):
        super().__init__(parent)
        self.dungeon = dungeon
        self.unlocked = unlocked
        self.best_score = best_score

        if unlocked:
            if best_score >= 85:
                border_color = "#00FF88"
                glow = "box-shadow: 0 0 12px #00FF88;"
            elif best_score >= 70:
                border_color = "#FFD700"
                glow = ""
            else:
                border_color = "#00FFFF"
                glow = ""
        else:
            border_color = "#222244"
            glow = ""

        self.setStyleSheet(
            f"background-color: #0D0D22; border: 2px solid {border_color}; "
            f"border-radius: 12px; padding: 12px; {glow}"
        )
        self.setFixedHeight(130)
        self.setCursor(Qt.PointingHandCursor if unlocked else Qt.ForbiddenCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        top = QHBoxLayout()
        emoji = dungeon.get("boss_emoji", "🏛️")
        lbl_emoji = QLabel(emoji)
        lbl_emoji.setStyleSheet("font-size: 22px;")

        lbl_title = QLabel(dungeon["title"])
        lbl_title.setStyleSheet(
            f"color: {'#00FFFF' if unlocked else '#333355'}; "
            f"font-size: 15px; font-weight: bold;"
        )

        lock_icon = "" if unlocked else "🔒"
        lbl_lock = QLabel(lock_icon)
        lbl_lock.setStyleSheet("font-size: 16px;")

        top.addWidget(lbl_emoji)
        top.addWidget(lbl_title)
        top.addStretch()
        top.addWidget(lbl_lock)
        layout.addLayout(top)

        lbl_sub = QLabel(dungeon["subtitle"])
        lbl_sub.setWordWrap(True)
        lbl_sub.setStyleSheet(
            f"color: {'#8888AA' if unlocked else '#222244'}; font-size: 12px;"
        )
        layout.addWidget(lbl_sub)

        # Score bar
        if best_score > 0 and unlocked:
            score_color = "#00FF88" if best_score >= 85 else "#FFD700" if best_score >= 70 else "#FF6B00"
            lbl_score = QLabel(f"Best: {best_score}% {'★' if best_score >= 85 else ''}")
            lbl_score.setStyleSheet(f"color: {score_color}; font-size: 12px; font-weight: bold;")
            layout.addWidget(lbl_score)
        elif not unlocked:
            thresh = dungeon.get("unlock_threshold", 70)
            lbl_locked = QLabel(f"🔒 Erfordert {thresh}% im vorherigen Teil")
            lbl_locked.setStyleSheet("color: #333355; font-size: 11px;")
            layout.addWidget(lbl_locked)

    def mousePressEvent(self, event):
        if self.unlocked:
            self.selected.emit(self.dungeon)


class ModeSelector(QWidget):
    """Choose which game mode to play for a dungeon."""
    mode_chosen = Signal(str, dict)  # mode_key, dungeon
    back = Signal()

    def __init__(self, dungeon: dict, best_score: int, parent=None):
        super().__init__(parent)
        self.dungeon = dungeon

        root = QVBoxLayout(self)
        root.setContentsMargins(40, 24, 40, 24)
        root.setSpacing(16)

        # Back button + title
        back_btn = QPushButton("← Zurück zur Karte")
        back_btn.setStyleSheet(
            "background-color: transparent; color: #8888AA; border: none; "
            "font-size: 13px; text-align: left; padding: 0;"
        )
        back_btn.clicked.connect(self.back.emit)
        root.addWidget(back_btn, 0, Qt.AlignLeft)

        # Boss intro
        boss_card = QFrame()
        boss_card.setStyleSheet(
            "background-color: #110011; border: 2px solid #FF00FF; border-radius: 14px; padding: 20px;"
        )
        boss_layout = QVBoxLayout(boss_card)

        emoji = dungeon.get("boss_emoji", "🏛️")
        lbl_boss = QLabel(f"{emoji}  {dungeon['boss_name']}")
        lbl_boss.setAlignment(Qt.AlignCenter)
        lbl_boss.setStyleSheet("color: #FF00FF; font-size: 22px; font-weight: bold;")
        boss_layout.addWidget(lbl_boss)

        lbl_sub = QLabel(f"{dungeon['title']} — {dungeon['subtitle']}")
        lbl_sub.setAlignment(Qt.AlignCenter)
        lbl_sub.setStyleSheet("color: #AA88AA; font-size: 14px;")
        boss_layout.addWidget(lbl_sub)

        if best_score > 0:
            score_color = "#00FF88" if best_score >= 85 else "#FFD700" if best_score >= 70 else "#FF6B00"
            lbl_prev = QLabel(f"Bester Score: {best_score}%")
            lbl_prev.setAlignment(Qt.AlignCenter)
            lbl_prev.setStyleSheet(f"color: {score_color}; font-size: 13px;")
            boss_layout.addWidget(lbl_prev)

        root.addWidget(boss_card)

        # Mode buttons
        root.addWidget(make_separator())
        lbl_choose = QLabel("Wähle deinen Angriffsmodus:")
        lbl_choose.setStyleSheet("color: #AAAACC; font-size: 14px; font-weight: bold;")
        root.addWidget(lbl_choose)

        modes = [
            ("echo",        "⚡ Echo Mode",              "Satz merken → auswendig tippen",              "#00FFFF"),
            ("construction","🎯 Konstruktionsjagd",       "Konstruktionen blitzschnell erkennen",         "#FF00FF"),
            ("speedrun",    "🏃 Translation Speedrun",    "Übersetze gegen die Uhr",                      "#FF6B00"),
            ("boss",        "💀 BOSS FIGHT",              "Komplette mündliche Prüfungssimulation",       "#FF00FF"),
        ]

        for mode_key, label, desc, color in modes:
            btn = QPushButton()
            btn.setFixedHeight(64)
            btn.setStyleSheet(
                f"background-color: #0D0D22; color: {color}; "
                f"border: 2px solid {color}; border-radius: 10px; "
                f"font-size: 15px; font-weight: bold; text-align: left; padding: 0 20px;"
            )
            btn_layout = QHBoxLayout(btn)
            btn_layout.setContentsMargins(16, 0, 16, 0)
            lbl_name = QLabel(label)
            lbl_name.setStyleSheet(f"color: {color}; font-size: 15px; font-weight: bold; background: transparent; border: none;")
            lbl_desc = QLabel(desc)
            lbl_desc.setStyleSheet("color: #888899; font-size: 12px; background: transparent; border: none;")
            btn_v = QVBoxLayout()
            btn_v.addWidget(lbl_name)
            btn_v.addWidget(lbl_desc)
            btn_layout.addLayout(btn_v)

            btn.clicked.connect(lambda checked, mk=mode_key: self.mode_chosen.emit(mk, self.dungeon))
            root.addWidget(btn)

        root.addStretch()


class Dashboard(QWidget):
    """Main dungeon map screen."""
    play_mode = Signal(str, dict)  # mode_key, dungeon

    def __init__(self, progress: dict, parent=None):
        super().__init__(parent)
        self.progress = progress
        self.dungeons = load_dungeons()
        self._mode_selector: ModeSelector | None = None
        self._build_ui()

    def _build_ui(self):
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

        self._map_widget = self._build_map()
        self._root_layout.addWidget(self._map_widget)

    def _build_map(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 24, 32, 32)
        layout.setSpacing(20)

        # Title
        lbl_title = QLabel("🏛️  PLINIUS: MEMORY RAID")
        lbl_title.setStyleSheet("font-size: 28px; font-weight: bold; color: #00FFFF;")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)

        lbl_sub = QLabel("Vesuvbrief — Wähle deinen Dungeon")
        lbl_sub.setStyleSheet("color: #8888AA; font-size: 14px;")
        lbl_sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_sub)

        # Weakness banner
        from src.engine.game_engine import engine
        weaknesses = engine.get_weaknesses()
        if weaknesses:
            weak_frame = QFrame()
            weak_frame.setStyleSheet(
                "background-color: #1A0A00; border: 1px solid #FF6B00; "
                "border-radius: 10px; padding: 10px;"
            )
            weak_layout = QVBoxLayout(weak_frame)
            lbl_w = QLabel("⚠️ Deine Schwächen — Diese Konstruktionen brauchst du noch:")
            lbl_w.setStyleSheet("color: #FF6B00; font-size: 13px; font-weight: bold;")
            weak_layout.addWidget(lbl_w)
            lbl_wlist = QLabel("  •  " + "\n  •  ".join(weaknesses[:4]))
            lbl_wlist.setStyleSheet("color: #CC8844; font-size: 12px;")
            weak_layout.addWidget(lbl_wlist)
            layout.addWidget(weak_frame)

        layout.addWidget(make_separator())

        # Grid of dungeon cards
        grid = QGridLayout()
        grid.setSpacing(12)
        for i, dungeon in enumerate(self.dungeons):
            did = dungeon["id"]
            thresh = dungeon.get("unlock_threshold", 70)
            unlocked = is_dungeon_unlocked(self.progress, did, thresh)
            best = self.progress.get("dungeon_scores", {}).get(str(did), 0)
            card = DungeonCard(dungeon, unlocked, best)
            card.selected.connect(self._on_dungeon_selected)
            grid.addWidget(card, i // 2, i % 2)

        layout.addLayout(grid)
        layout.addStretch()

        scroll.setWidget(container)
        return scroll

    def _on_dungeon_selected(self, dungeon: dict):
        did = dungeon["id"]
        best = self.progress.get("dungeon_scores", {}).get(str(did), 0)

        # Remove old mode selector if any
        if self._mode_selector:
            self._root_layout.removeWidget(self._mode_selector)
            self._mode_selector.deleteLater()
            self._mode_selector = None

        selector = ModeSelector(dungeon, best)
        selector.back.connect(self._show_map)
        selector.mode_chosen.connect(self.play_mode.emit)
        self._mode_selector = selector

        # Swap
        self._map_widget.hide()
        self._root_layout.addWidget(selector)

    def _show_map(self):
        if self._mode_selector:
            self._root_layout.removeWidget(self._mode_selector)
            self._mode_selector.deleteLater()
            self._mode_selector = None
        self._map_widget.show()

    def refresh_map(self):
        """Rebuild the map after progress changes."""
        old = self._map_widget
        self._map_widget = self._build_map()
        self._root_layout.insertWidget(0, self._map_widget)
        old.deleteLater()
        self._show_map()
