# Echo Mode: See sentence → it hides → type it from memory

import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont

from src.engine.game_engine import engine
from src.ui.hud_widget import CountdownTimer, FlashLabel, make_separator


class EchoModeWidget(QWidget):
    finished = Signal(int, int)  # xp_gained, score_pct

    def __init__(self, dungeon: dict, parent=None):
        super().__init__(parent)
        self.dungeon = dungeon
        self.sentences = dungeon["sentences"][:]
        random.shuffle(self.sentences)
        self.idx = 0
        self.total_score = 0
        self.rounds = len(self.sentences)
        self.xp_this_mode = 0
        self._phase = "show"  # show | hidden | result

        self._build_ui()
        self._load_sentence()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 20, 32, 20)
        root.setSpacing(14)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("⚡ ECHO MODE")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #00FFFF;")
        self.lbl_progress = QLabel(f"1 / {self.rounds}")
        self.lbl_progress.setStyleSheet("color: #8888AA; font-size: 14px;")
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(self.lbl_progress)
        root.addLayout(hdr)
        root.addWidget(make_separator())

        # Instructions
        self.lbl_instruction = QLabel("📖 Merke dir den Satz! Er verschwindet in 5 Sekunden.")
        self.lbl_instruction.setStyleSheet("color: #AAAACC; font-size: 13px;")
        root.addWidget(self.lbl_instruction)

        # Countdown bar
        self.timer = CountdownTimer(5)
        self.timer.timeout.connect(self._hide_sentence)
        root.addWidget(self.timer, 0, Qt.AlignHCenter)

        # Latin sentence display (card)
        self.card = QFrame()
        self.card.setObjectName("card_highlight")
        self.card.setStyleSheet(
            "background-color: #0A0A22; border: 2px solid #00FFFF; border-radius: 14px; padding: 20px;"
        )
        card_layout = QVBoxLayout(self.card)
        self.lbl_latin = QLabel()
        self.lbl_latin.setObjectName("lbl_latin")
        self.lbl_latin.setWordWrap(True)
        self.lbl_latin.setAlignment(Qt.AlignCenter)
        font = QFont("Georgia", 16, QFont.Bold)
        self.lbl_latin.setFont(font)
        self.lbl_latin.setStyleSheet("color: #CCCCFF; font-style: italic; line-height: 1.8;")
        card_layout.addWidget(self.lbl_latin)
        root.addWidget(self.card)

        # Text input (hidden initially)
        self.lbl_type_hint = QLabel("⌨️ Tippe den Satz so genau wie möglich nach:")
        self.lbl_type_hint.setStyleSheet("color: #8888AA; font-size: 13px;")
        self.lbl_type_hint.hide()
        root.addWidget(self.lbl_type_hint)

        self.text_input = QTextEdit()
        self.text_input.setFixedHeight(90)
        self.text_input.setPlaceholderText("Latein hier eintippen...")
        self.text_input.hide()
        root.addWidget(self.text_input)

        # Timer for typing phase
        self.typing_timer = CountdownTimer(45)
        self.typing_timer.timeout.connect(self._submit)
        self.typing_timer.hide()
        root.addWidget(self.typing_timer, 0, Qt.AlignHCenter)

        # Flash feedback
        self.flash = FlashLabel()
        root.addWidget(self.flash)

        # Result area (hidden initially)
        self.result_frame = QFrame()
        self.result_frame.setObjectName("card")
        self.result_frame.setStyleSheet(
            "background-color: #0D0D22; border: 1px solid #334466; border-radius: 12px; padding: 12px;"
        )
        res_layout = QVBoxLayout(self.result_frame)
        self.lbl_result_score = QLabel()
        self.lbl_result_score.setAlignment(Qt.AlignCenter)
        self.lbl_result_german = QLabel()
        self.lbl_result_german.setWordWrap(True)
        self.lbl_result_german.setStyleSheet("color: #AAAACC; font-size: 13px;")
        res_layout.addWidget(self.lbl_result_score)
        res_layout.addWidget(self.lbl_result_german)
        self.result_frame.hide()
        root.addWidget(self.result_frame)

        # Bottom buttons
        btn_row = QHBoxLayout()
        self.btn_submit = QPushButton("✅ Überprüfen")
        self.btn_submit.setObjectName("btn_primary")
        self.btn_submit.clicked.connect(self._submit)
        self.btn_submit.hide()

        self.btn_next = QPushButton("⏭ Weiter →")
        self.btn_next.setObjectName("btn_primary")
        self.btn_next.clicked.connect(self._next)
        self.btn_next.hide()

        btn_row.addWidget(self.btn_submit)
        btn_row.addWidget(self.btn_next)
        root.addLayout(btn_row)

        root.addStretch()

    def _load_sentence(self):
        if self.idx >= len(self.sentences):
            self._finish()
            return

        s = self.sentences[self.idx]
        self.lbl_progress.setText(f"{self.idx + 1} / {self.rounds}")
        self.lbl_latin.setText(s["latin"])
        self.lbl_instruction.setText("📖 Merke dir den Satz! Er verschwindet in 5 Sekunden.")

        # Reset UI to "show" phase
        self.card.show()
        self.lbl_latin.show()
        self.lbl_type_hint.hide()
        self.text_input.hide()
        self.text_input.clear()
        self.typing_timer.hide()
        self.btn_submit.hide()
        self.btn_next.hide()
        self.result_frame.hide()
        self.flash.hide()

        self._phase = "show"
        self.timer.reset(5)
        self.timer.show()
        self.timer.start()

    def _hide_sentence(self):
        """Phase: sentence hidden, user must type."""
        self._phase = "hidden"
        self.lbl_latin.setText("❓  ❓  ❓")
        self.lbl_latin.setStyleSheet("color: #334466; font-style: italic; font-size: 22px;")
        self.timer.hide()
        self.lbl_instruction.setText("✍️ Wie lautete der Satz?")
        self.lbl_type_hint.show()
        self.text_input.show()
        self.text_input.setFocus()
        self.btn_submit.show()
        self.typing_timer.reset(45)
        self.typing_timer.show()
        self.typing_timer.start()

    def _submit(self):
        self.typing_timer.stop()
        self.typing_timer.hide()
        s = self.sentences[self.idx]
        typed = self.text_input.toPlainText().strip()
        reward_key, pct = engine.score_echo(s["latin"], typed)

        xp, mult = engine.add_xp(reward_key)
        self.xp_this_mode += xp

        if pct >= 90:
            engine.hit_combo()
            self.flash.flash_good(f"✨ PERFEKT! +{xp} XP  (×{mult:.1f})")
            score_color = "#00FF88"
        elif pct >= 70:
            engine.hit_combo()
            self.flash.flash_good(f"👍 GUT! {pct}%  +{xp} XP")
            score_color = "#FFD700"
        else:
            engine.break_combo()
            self.flash.flash_bad(f"💀 {pct}% — Weiter üben!")
            score_color = "#FF4444"

        self.total_score += pct
        self.btn_submit.hide()

        # Show answer + German
        self.lbl_latin.setText(s["latin"])
        self.lbl_latin.setStyleSheet("color: #CCCCFF; font-style: italic;")
        self.lbl_result_score.setText(f"Score: {pct}%")
        self.lbl_result_score.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {score_color};")
        self.lbl_result_german.setText(f"🇩🇪 {s['german']}")
        self.result_frame.show()
        self.btn_next.show()

    def _next(self):
        self.idx += 1
        self._load_sentence()

    def _finish(self):
        avg = int(self.total_score / max(self.rounds, 1))
        self.finished.emit(self.xp_this_mode, avg)
