# Shared HUD widgets: XP bar, Combo display, Timer

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar, QFrame
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from src.engine.game_engine import engine, LEVEL_THRESHOLDS


class HUDBar(QWidget):
    """Top HUD: Level | XP bar | Combo | Session XP"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(56)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 4)
        layout.setSpacing(16)

        # Level title
        self.lbl_level = QLabel("⚔️ Tiro")
        self.lbl_level.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 14px;")

        # XP progress bar
        self.xp_bar = QProgressBar()
        self.xp_bar.setFixedHeight(14)
        self.xp_bar.setRange(0, 500)
        self.xp_bar.setValue(0)
        self.xp_bar.setTextVisible(False)

        # Session XP
        self.lbl_session = QLabel("+0 XP")
        self.lbl_session.setObjectName("lbl_xp")
        self.lbl_session.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 13px; min-width: 80px;")

        # Combo
        self.lbl_combo = QLabel("COMBO x1")
        self.lbl_combo.setStyleSheet("color: #FF00FF; font-weight: bold; font-size: 15px; min-width: 110px;")

        layout.addWidget(self.lbl_level)
        layout.addWidget(self.xp_bar, 1)
        layout.addWidget(self.lbl_session)
        layout.addWidget(self.lbl_combo)

        self.setStyleSheet("background-color: #0D0D22; border-bottom: 1px solid #223366;")
        self.refresh()

    def refresh(self):
        title, emoji, curr, nxt = engine.get_level()
        self.lbl_level.setText(f"{emoji} {title}")
        rel_xp = max(0, engine.total_xp - curr)
        span = max(1, nxt - curr)
        self.xp_bar.setRange(0, span)
        self.xp_bar.setValue(min(rel_xp, span))

        combo = engine.combo
        if combo >= 5:
            color = "#FF00FF"
        elif combo >= 3:
            color = "#FF6B00"
        elif combo >= 2:
            color = "#FFD700"
        else:
            color = "#8888AA"
        self.lbl_combo.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 15px; min-width: 110px;")
        self.lbl_combo.setText(f"COMBO ×{combo}")
        self.lbl_session.setText(f"+{engine.session_xp} XP")


class CountdownTimer(QWidget):
    """Big countdown timer with color feedback."""
    timeout = Signal()

    def __init__(self, seconds: int = 60, parent=None):
        super().__init__(parent)
        self.total = seconds
        self.remaining = seconds

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.lbl = QLabel(f"⏱ {seconds}")
        self.lbl.setObjectName("lbl_timer_ok")
        self.lbl.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(28)
        font.setBold(True)
        self.lbl.setFont(font)
        layout.addWidget(self.lbl)

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

    def start(self):
        self.remaining = self.total
        self._update_label()
        self._timer.start()

    def stop(self):
        self._timer.stop()

    def reset(self, seconds: int = None):
        self.stop()
        if seconds:
            self.total = seconds
            self.remaining = seconds
        else:
            self.remaining = self.total
        self._update_label()

    def _tick(self):
        self.remaining -= 1
        self._update_label()
        if self.remaining <= 0:
            self._timer.stop()
            self.timeout.emit()

    def _update_label(self):
        r = self.remaining
        if r > self.total * 0.5:
            color = "#00FF88"
            name = "lbl_timer_ok"
        elif r > self.total * 0.25:
            color = "#FF6B00"
            name = "lbl_timer"
        else:
            color = "#FF2222"
            name = "lbl_timer"
        self.lbl.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 28px;")
        self.lbl.setText(f"⏱ {r}")


class FlashLabel(QLabel):
    """Label that flashes a color then fades."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.hide()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def flash_good(self, text: str, ms: int = 1200):
        self.setObjectName("lbl_flash_good")
        self.setStyleSheet("font-size: 20px; font-weight: bold; color: #00FF88; "
                           "background-color: #001100; border-radius: 8px; padding: 8px;")
        self.setText(text)
        self.show()
        self._timer.start(ms)

    def flash_bad(self, text: str, ms: int = 1200):
        self.setObjectName("lbl_flash_bad")
        self.setStyleSheet("font-size: 20px; font-weight: bold; color: #FF4444; "
                           "background-color: #110000; border-radius: 8px; padding: 8px;")
        self.setText(text)
        self.show()
        self._timer.start(ms)


def make_separator():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet("color: #223366; background-color: #223366; max-height: 1px;")
    return line
