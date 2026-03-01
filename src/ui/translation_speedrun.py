# Translation Speedrun: Translate Latin against the clock

import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from src.engine.game_engine import engine
from src.ui.hud_widget import CountdownTimer, FlashLabel, make_separator


class TranslationSpeedrunWidget(QWidget):
    finished = Signal(int, int)  # xp_gained, score_pct

    def __init__(self, dungeon: dict, parent=None):
        super().__init__(parent)
        self.dungeon = dungeon
        self.sentences = dungeon["sentences"][:]
        random.shuffle(self.sentences)
        self.idx = 0
        self.total_score = 0
        self.xp_this_mode = 0
        self.rounds = len(self.sentences)

        self._build_ui()
        self._load_sentence()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 20, 32, 20)
        root.setSpacing(14)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("🏃 TRANSLATION SPEEDRUN")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #FF6B00;")
        self.lbl_progress = QLabel(f"1 / {self.rounds}")
        self.lbl_progress.setStyleSheet("color: #8888AA; font-size: 14px;")
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(self.lbl_progress)
        root.addLayout(hdr)
        root.addWidget(make_separator())

        instr = QLabel("⚡ Übersetze so schnell und genau wie möglich!")
        instr.setStyleSheet("color: #AAAACC; font-size: 13px;")
        root.addWidget(instr)

        # Timer
        self.timer = CountdownTimer(60)
        self.timer.timeout.connect(self._on_timeout)
        root.addWidget(self.timer, 0, Qt.AlignHCenter)

        # Latin sentence card
        self.card = QFrame()
        self.card.setStyleSheet(
            "background-color: #0A0A1A; border: 2px solid #FF6B00; border-radius: 14px; padding: 20px;"
        )
        card_layout = QVBoxLayout(self.card)
        self.lbl_latin = QLabel()
        self.lbl_latin.setWordWrap(True)
        self.lbl_latin.setAlignment(Qt.AlignCenter)
        font = QFont("Georgia", 16, QFont.Bold)
        self.lbl_latin.setFont(font)
        self.lbl_latin.setStyleSheet("color: #CCCCFF; font-style: italic;")
        card_layout.addWidget(self.lbl_latin)
        root.addWidget(self.card)

        # Hint: first keyword
        self.lbl_hint = QLabel()
        self.lbl_hint.setStyleSheet("color: #445566; font-size: 12px; font-style: italic;")
        root.addWidget(self.lbl_hint)

        # Input
        self.text_input = QTextEdit()
        self.text_input.setFixedHeight(90)
        self.text_input.setPlaceholderText("Deutsche Übersetzung hier eintippen...")
        root.addWidget(self.text_input)

        # Flash
        self.flash = FlashLabel()
        root.addWidget(self.flash)

        # Score + German answer (after submit)
        self.result_frame = QFrame()
        self.result_frame.setStyleSheet(
            "background-color: #0D0D22; border: 1px solid #334466; border-radius: 12px; padding: 12px;"
        )
        res_layout = QVBoxLayout(self.result_frame)
        self.lbl_result_score = QLabel()
        self.lbl_result_score.setAlignment(Qt.AlignCenter)
        self.lbl_result_german = QLabel()
        self.lbl_result_german.setWordWrap(True)
        self.lbl_result_german.setStyleSheet("color: #AAAACC; font-size: 13px;")
        self.lbl_keywords_found = QLabel()
        self.lbl_keywords_found.setWordWrap(True)
        self.lbl_keywords_found.setStyleSheet("color: #888899; font-size: 12px;")
        res_layout.addWidget(self.lbl_result_score)
        res_layout.addWidget(self.lbl_result_german)
        res_layout.addWidget(self.lbl_keywords_found)
        self.result_frame.hide()
        root.addWidget(self.result_frame)

        # Buttons
        btn_row = QHBoxLayout()
        self.btn_submit = QPushButton("✅ Überprüfen")
        self.btn_submit.setObjectName("btn_primary")
        self.btn_submit.setStyleSheet(
            "background-color: #1A0D00; color: #FF6B00; border: 2px solid #FF6B00; "
            "border-radius: 8px; font-size: 15px; font-weight: bold; padding: 12px 24px;"
        )
        self.btn_submit.clicked.connect(self._submit)

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

        # Give a subtle hint (first keyword)
        kw = s.get("keywords", [])
        hint_word = kw[0] if kw else ""
        self.lbl_hint.setText(f"Hinweis: Schlüsselwort → \"{hint_word}\"" if hint_word else "")

        self.text_input.clear()
        self.text_input.setEnabled(True)
        self.result_frame.hide()
        self.btn_submit.show()
        self.btn_next.hide()
        self.flash.hide()
        self.timer.reset(60)
        self.timer.start()
        self.text_input.setFocus()

    def _on_timeout(self):
        self._submit(timed_out=True)

    def _submit(self, timed_out: bool = False):
        self.timer.stop()
        self.text_input.setEnabled(False)
        s = self.sentences[self.idx]
        typed = self.text_input.toPlainText().strip()

        reward_key, pct = engine.score_translation(s, typed)
        xp, mult = engine.add_xp(reward_key)
        self.xp_this_mode += xp
        self.total_score += pct

        if pct >= 90:
            engine.hit_combo()
            self.flash.flash_good(f"🚀 PERFEKT! +{xp} XP  ×{mult:.1f}")
            score_color = "#00FF88"
        elif pct >= 65:
            engine.hit_combo()
            self.flash.flash_good(f"👍 GUT! {pct}%  +{xp} XP")
            score_color = "#FFD700"
        else:
            engine.break_combo()
            msg = "⏱ TIME'S UP!" if timed_out else f"💀 {pct}%"
            self.flash.flash_bad(msg)
            score_color = "#FF4444"

        # Show result
        self.lbl_result_score.setText(f"{pct}%")
        self.lbl_result_score.setStyleSheet(
            f"font-size: 36px; font-weight: bold; color: {score_color};"
        )
        self.lbl_result_german.setText(f"🇩🇪 {s['german']}")

        # Show which keywords were found
        keywords = s.get("keywords", [])
        typed_lower = typed.lower()
        found = [k for k in keywords if k.lower() in typed_lower]
        missed = [k for k in keywords if k.lower() not in typed_lower]
        kw_text = ""
        if found:
            kw_text += f"✅ Gefunden: {', '.join(found)}  "
        if missed:
            kw_text += f"❌ Fehlt: {', '.join(missed)}"
        self.lbl_keywords_found.setText(kw_text)

        self.result_frame.show()
        self.btn_submit.hide()
        self.btn_next.show()

    def _next(self):
        self.idx += 1
        self._load_sentence()

    def _finish(self):
        avg = int(self.total_score / max(self.rounds, 1))
        self.finished.emit(self.xp_this_mode, avg)
