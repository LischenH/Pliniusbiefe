# Main Window: orchestrates all screens

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QLabel
from PySide6.QtCore import Qt

from src.ui.theme import STYLESHEET
from src.ui.hud_widget import HUDBar
from src.ui.dashboard import Dashboard
from src.ui.echo_mode import EchoModeWidget
from src.ui.construction_hunt import ConstructionHuntWidget
from src.ui.translation_speedrun import TranslationSpeedrunWidget
from src.ui.boss_fight import BossFightWidget
from src.ui.result_screen import ResultScreen
from src.engine.game_engine import engine
from src.engine.progress import (
    load_progress, save_progress, update_dungeon_score, is_dungeon_unlocked
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚔️ Plinius: Memory Raid")
        self.resize(900, 700)
        self.setMinimumSize(720, 560)
        self.setStyleSheet(STYLESHEET)

        # Load progress
        self.progress = load_progress()
        engine.total_xp = self.progress.get("total_xp", 0)
        engine.max_combo = self.progress.get("max_combo", 0)
        engine.weakness_tracker = self.progress.get("weakness_tracker", {})
        self.progress["sessions"] = self.progress.get("sessions", 0) + 1

        # Root widget
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # HUD
        self.hud = HUDBar()
        root_layout.addWidget(self.hud)

        # Stacked pages
        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack, 1)

        self.setCentralWidget(root)

        # Dashboard
        self.dashboard = Dashboard(self.progress)
        self.dashboard.play_mode.connect(self._launch_mode)
        self.stack.addWidget(self.dashboard)

        # Active mode widget (swapped in/out)
        self._active_mode_widget: QWidget | None = None
        self._current_mode_key: str = ""
        self._current_dungeon: dict = {}

    # ──────────────────────────────────────────────

    def _launch_mode(self, mode_key: str, dungeon: dict):
        self._current_mode_key = mode_key
        self._current_dungeon = dungeon

        # Remove previous mode widget
        if self._active_mode_widget:
            self.stack.removeWidget(self._active_mode_widget)
            self._active_mode_widget.deleteLater()
            self._active_mode_widget = None

        widget = self._create_mode_widget(mode_key, dungeon)
        if widget is None:
            return

        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)
        self._active_mode_widget = widget

    def _create_mode_widget(self, mode_key: str, dungeon: dict) -> QWidget | None:
        if mode_key == "echo":
            w = EchoModeWidget(dungeon)
            w.finished.connect(self._on_mode_finished)
            return w
        elif mode_key == "construction":
            w = ConstructionHuntWidget(dungeon)
            w.finished.connect(self._on_mode_finished)
            return w
        elif mode_key == "speedrun":
            w = TranslationSpeedrunWidget(dungeon)
            w.finished.connect(self._on_mode_finished)
            return w
        elif mode_key == "boss":
            w = BossFightWidget(dungeon)
            w.finished.connect(self._on_mode_finished)
            return w
        return None

    def _on_mode_finished(self, xp_gained: int, score_pct: int):
        dungeon = self._current_dungeon
        mode_key = self._current_mode_key

        # Update progress
        did = dungeon["id"]
        update_dungeon_score(self.progress, did, score_pct)
        self.progress["total_xp"] = engine.total_xp
        self.progress["max_combo"] = engine.max_combo
        self.progress["weakness_tracker"] = engine.weakness_tracker
        save_progress(self.progress)

        # Check if next dungeon is now unlocked
        next_id = did + 1
        unlocked_next = is_dungeon_unlocked(self.progress, next_id, 70)

        mode_names = {
            "echo": "⚡ Echo Mode",
            "construction": "🎯 Konstruktionsjagd",
            "speedrun": "🏃 Translation Speedrun",
            "boss": "💀 Boss Fight",
        }

        # Show result screen
        result = ResultScreen(
            mode_name=mode_names.get(mode_key, mode_key),
            xp_gained=xp_gained,
            score_pct=score_pct,
            dungeon_title=f"{dungeon['title']} — {dungeon['subtitle']}",
            unlocked_next=unlocked_next,
        )
        result.back_to_dungeon.connect(self._back_to_dashboard)
        result.retry.connect(lambda: self._launch_mode(mode_key, dungeon))

        if self._active_mode_widget:
            self.stack.removeWidget(self._active_mode_widget)
            self._active_mode_widget.deleteLater()
            self._active_mode_widget = None

        self.stack.addWidget(result)
        self.stack.setCurrentWidget(result)
        self._active_mode_widget = result

        self.hud.refresh()

    def _back_to_dashboard(self):
        if self._active_mode_widget:
            self.stack.removeWidget(self._active_mode_widget)
            self._active_mode_widget.deleteLater()
            self._active_mode_widget = None

        self.dashboard.refresh_map()
        self.stack.setCurrentWidget(self.dashboard)
        self.hud.refresh()

    def closeEvent(self, event):
        self.progress["total_xp"] = engine.total_xp
        self.progress["max_combo"] = engine.max_combo
        self.progress["weakness_tracker"] = engine.weakness_tracker
        save_progress(self.progress)
        super().closeEvent(event)
