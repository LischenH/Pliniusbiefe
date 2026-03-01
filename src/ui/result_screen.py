# Result Screen: shown after completing a mode

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class ResultScreen(QWidget):
    back_to_dungeon = Signal()
    retry = Signal()

    def __init__(self, mode_name: str, xp_gained: int, score_pct: int,
                 dungeon_title: str, unlocked_next: bool = False, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 32, 48, 32)
        root.setSpacing(20)
        root.setAlignment(Qt.AlignCenter)

        # Mode label
        lbl_mode = QLabel(mode_name)
        lbl_mode.setAlignment(Qt.AlignCenter)
        lbl_mode.setStyleSheet("color: #8888AA; font-size: 14px;")
        root.addWidget(lbl_mode)

        # Dungeon
        lbl_dungeon = QLabel(dungeon_title)
        lbl_dungeon.setAlignment(Qt.AlignCenter)
        lbl_dungeon.setStyleSheet("color: #AAAAFF; font-size: 18px; font-weight: bold;")
        root.addWidget(lbl_dungeon)

        # Score
        if score_pct >= 85:
            color = "#00FF88"
            msg = "MEISTER!"
            emoji = "🏆"
        elif score_pct >= 70:
            color = "#FFD700"
            msg = "GUT GEMACHT!"
            emoji = "⭐"
        elif score_pct >= 50:
            color = "#FF6B00"
            msg = "WEITER ÜBEN!"
            emoji = "💪"
        else:
            color = "#FF4444"
            msg = "RETRY!"
            emoji = "🔄"

        lbl_emoji = QLabel(emoji)
        lbl_emoji.setAlignment(Qt.AlignCenter)
        lbl_emoji.setStyleSheet("font-size: 56px;")
        root.addWidget(lbl_emoji)

        lbl_score = QLabel(f"{score_pct}%")
        lbl_score.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(52)
        font.setBold(True)
        lbl_score.setFont(font)
        lbl_score.setStyleSheet(f"color: {color};")
        root.addWidget(lbl_score)

        lbl_msg = QLabel(msg)
        lbl_msg.setAlignment(Qt.AlignCenter)
        lbl_msg.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: bold;")
        root.addWidget(lbl_msg)

        # XP gained
        lbl_xp = QLabel(f"+{xp_gained} XP verdient")
        lbl_xp.setAlignment(Qt.AlignCenter)
        lbl_xp.setStyleSheet("color: #FFD700; font-size: 18px; font-weight: bold;")
        root.addWidget(lbl_xp)

        # Unlock message
        if unlocked_next:
            lbl_unlock = QLabel("🔓 Nächster Dungeon freigeschaltet!")
            lbl_unlock.setAlignment(Qt.AlignCenter)
            lbl_unlock.setStyleSheet(
                "color: #00FF88; font-size: 15px; font-weight: bold; "
                "background-color: #001A00; border-radius: 8px; padding: 8px;"
            )
            root.addWidget(lbl_unlock)

        root.addSpacing(16)

        # Buttons
        btn_row = QHBoxLayout()
        btn_back = QPushButton("🏠 Zurück zur Karte")
        btn_back.setObjectName("btn_primary")
        btn_back.clicked.connect(self.back_to_dungeon.emit)

        btn_retry = QPushButton("🔄 Nochmal")
        btn_retry.setObjectName("btn_neutral")
        btn_retry.setStyleSheet(
            "background-color: #1A1A3A; color: #AAAACC; border: 2px solid #333366; "
            "border-radius: 8px; font-size: 14px; font-weight: bold; padding: 10px 20px;"
        )
        btn_retry.clicked.connect(self.retry.emit)

        btn_row.addWidget(btn_retry)
        btn_row.addWidget(btn_back)
        root.addLayout(btn_row)
