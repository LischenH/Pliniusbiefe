# Boss Fight Mode: Full oral-exam simulation

import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame, QStackedWidget
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

from src.engine.game_engine import engine
from src.ui.hud_widget import CountdownTimer, FlashLabel, make_separator


STYLISTIC_QUESTIONS = [
    ("Nenne ein Stilmittel in diesem Satz!", "stylistic_devices"),
]

CONSTRUCTION_PROMPTS = [
    "Welche grammatische Konstruktion steckt im Satz?",
    "Erkenne die Konstruktion und benenne sie!",
    "Was für eine Konstruktion ist das?",
]


class BossFightWidget(QWidget):
    """4-phase boss fight: prep → translate → grammar → stylistics → score."""
    finished = Signal(int, int)  # xp, score_pct

    def __init__(self, dungeon: dict, parent=None):
        super().__init__(parent)
        self.dungeon = dungeon
        self.sentences = [s for s in dungeon["sentences"] if s.get("constructions") or s.get("stylistic_devices")]
        if not self.sentences:
            self.sentences = dungeon["sentences"][:]
        random.shuffle(self.sentences)
        self.sentence_idx = 0
        self.round_scores = []
        self.xp_this_mode = 0
        self.total_rounds = min(len(self.sentences), 3)  # max 3 boss rounds

        self._build_ui()
        self._start_round()

    # ──────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 20, 32, 20)
        root.setSpacing(14)

        # Header
        hdr = QHBoxLayout()
        boss_label = QLabel(f"💀 BOSS FIGHT — {self.dungeon['boss_name']}  {self.dungeon['boss_emoji']}")
        boss_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FF00FF;")
        self.lbl_round = QLabel(f"Runde 1 / {self.total_rounds}")
        self.lbl_round.setStyleSheet("color: #8888AA;")
        hdr.addWidget(boss_label)
        hdr.addStretch()
        hdr.addWidget(self.lbl_round)
        root.addLayout(hdr)
        root.addWidget(make_separator())

        # Phase label
        self.lbl_phase = QLabel("⏳ Vorbereitung")
        self.lbl_phase.setStyleSheet("color: #FFAA00; font-size: 16px; font-weight: bold;")
        root.addWidget(self.lbl_phase)

        # Timer
        self.timer = CountdownTimer(30)
        self.timer.timeout.connect(self._phase_timeout)
        root.addWidget(self.timer, 0, Qt.AlignHCenter)

        # Boss HP bar (visual)
        self.lbl_hp = QLabel("❤️❤️❤️")
        self.lbl_hp.setStyleSheet("font-size: 22px;")
        self.lbl_hp.setAlignment(Qt.AlignCenter)
        root.addWidget(self.lbl_hp)

        # Sentence card
        self.card = QFrame()
        self.card.setStyleSheet(
            "background-color: #110011; border: 2px solid #FF00FF; border-radius: 14px; padding: 20px;"
        )
        card_layout = QVBoxLayout(self.card)
        self.lbl_latin = QLabel()
        self.lbl_latin.setWordWrap(True)
        self.lbl_latin.setAlignment(Qt.AlignCenter)
        font = QFont("Georgia", 16, QFont.Bold)
        self.lbl_latin.setFont(font)
        self.lbl_latin.setStyleSheet("color: #DDAAFF; font-style: italic;")
        card_layout.addWidget(self.lbl_latin)
        root.addWidget(self.card)

        # Question label
        self.lbl_question = QLabel("")
        self.lbl_question.setWordWrap(True)
        self.lbl_question.setStyleSheet("color: #AAAAFF; font-size: 14px; font-weight: bold;")
        root.addWidget(self.lbl_question)

        # Text input
        self.text_input = QTextEdit()
        self.text_input.setFixedHeight(80)
        self.text_input.setPlaceholderText("Antwort hier eintippen...")
        self.text_input.hide()
        root.addWidget(self.text_input)

        # Flash
        self.flash = FlashLabel()
        root.addWidget(self.flash)

        # Answer reveal
        self.lbl_answer = QLabel()
        self.lbl_answer.setWordWrap(True)
        self.lbl_answer.setStyleSheet(
            "color: #AACCFF; font-size: 13px; background-color: #080818; "
            "border-radius: 8px; padding: 10px;"
        )
        self.lbl_answer.hide()
        root.addWidget(self.lbl_answer)

        # Self-assessment buttons (for boss fight: user rates own answer)
        self.btn_row = QHBoxLayout()
        self.btn_correct = QPushButton("✅ Richtig!")
        self.btn_correct.setObjectName("btn_correct")
        self.btn_correct.setStyleSheet(
            "background-color: #002200; color: #00FF88; border: 2px solid #00FF88; "
            "border-radius: 8px; font-size: 14px; font-weight: bold; padding: 10px 20px;"
        )
        self.btn_correct.clicked.connect(lambda: self._phase_result(True))
        self.btn_correct.hide()

        self.btn_wrong = QPushButton("❌ Falsch")
        self.btn_wrong.setObjectName("btn_wrong")
        self.btn_wrong.setStyleSheet(
            "background-color: #220000; color: #FF4444; border: 2px solid #FF4444; "
            "border-radius: 8px; font-size: 14px; font-weight: bold; padding: 10px 20px;"
        )
        self.btn_wrong.clicked.connect(lambda: self._phase_result(False))
        self.btn_wrong.hide()

        self.btn_next_phase = QPushButton("⏭ Weiter →")
        self.btn_next_phase.setObjectName("btn_primary")
        self.btn_next_phase.clicked.connect(self._advance_phase)
        self.btn_next_phase.hide()

        self.btn_row.addWidget(self.btn_correct)
        self.btn_row.addWidget(self.btn_wrong)
        self.btn_row.addWidget(self.btn_next_phase)
        root.addLayout(self.btn_row)

        root.addStretch()

    # ──────────────────────────────────────────────
    # Phase management
    # ──────────────────────────────────────────────

    def _start_round(self):
        if self.sentence_idx >= self.total_rounds:
            self._finish_all()
            return

        self._phase_scores = []
        self._current_phase = "prep"
        s = self.sentences[self.sentence_idx]

        self.lbl_round.setText(f"Runde {self.sentence_idx + 1} / {self.total_rounds}")
        hp_hearts = "❤️" * (self.total_rounds - self.sentence_idx)
        empty_hearts = "🖤" * self.sentence_idx
        self.lbl_hp.setText(hp_hearts + empty_hearts)

        self.lbl_latin.setText(s["latin"])
        self.lbl_phase.setText("⏳ VORBEREITUNG — Lies den Satz!")
        self.lbl_question.setText("Bereite dich vor: Übersetzung • Konstruktionen • Stilmittel")
        self.text_input.hide()
        self.text_input.clear()
        self.lbl_answer.hide()
        self._set_buttons_hidden()
        self.btn_next_phase.show()
        self.btn_next_phase.setText("🚀 Ich bin bereit!")

        self.timer.reset(30)
        self.timer.start()

    def _advance_phase(self):
        self.timer.stop()
        s = self.sentences[self.sentence_idx]
        self.lbl_answer.hide()
        self._set_buttons_hidden()
        self.text_input.clear()

        if self._current_phase == "prep":
            self._current_phase = "translate"
            self.lbl_phase.setText("📖 PHASE 1 — Übersetze!")
            self.lbl_question.setText("Übersetze den Satz ins Deutsche:")
            self.text_input.show()
            self.text_input.setFocus()
            self.btn_next_phase.show()
            self.btn_next_phase.setText("✅ Übersetzung fertig")
            self.timer.reset(60)
            self.timer.start()

        elif self._current_phase == "translate":
            # Score translation, then go to grammar
            typed = self.text_input.toPlainText().strip()
            reward_key, pct = engine.score_translation(s, typed)
            self._phase_scores.append(pct)
            self._show_answer(f"🇩🇪 Musterlösung: {s['german']}")
            self.text_input.hide()
            self._current_phase = "grammar"

        elif self._current_phase == "grammar":
            self.lbl_answer.hide()
            constructions = s.get("constructions", [])
            if constructions:
                c = random.choice(constructions)
                self._expected_answer = c["type"]
                self._expected_explanation = c.get("explanation", "")
                self.lbl_phase.setText("🔬 PHASE 2 — Grammatik!")
                q = random.choice(CONSTRUCTION_PROMPTS)
                self.lbl_question.setText(q)
                self.text_input.show()
                self.text_input.setFocus()
                self.btn_next_phase.show()
                self.btn_next_phase.setText("✅ Antwort geben")
                self.timer.reset(30)
                self.timer.start()
                self._current_phase = "grammar_answer"
            else:
                self._phase_scores.append(80)  # No constructions: partial credit
                self._current_phase = "stylistics"
                self._advance_phase()

        elif self._current_phase == "grammar_answer":
            typed = self.text_input.toPlainText().strip()
            correct_hint = self._expected_answer.lower()
            typed_lower = typed.lower()
            auto_pct = 100 if any(part in typed_lower for part in correct_hint.split()) else 30
            self._show_answer(
                f"✔ Konstruktion: <b>{self._expected_answer}</b><br>"
                f"💡 {self._expected_explanation}"
            )
            self.text_input.hide()
            self._current_phase = "grammar_rate"
            self.btn_correct.show()
            self.btn_wrong.show()

        elif self._current_phase == "stylistics":
            devices = s.get("stylistic_devices", [])
            if devices:
                d = random.choice(devices)
                self.lbl_phase.setText("🎨 PHASE 3 — Stilmittel!")
                self.lbl_question.setText(
                    f"Nenne das Stilmittel und erkläre seine Wirkung:\n"
                    f"(Tipp: schau dir die Wortstellung und Wiederholungen an!)"
                )
                self._expected_stylistic = d["name"]
                self._expected_stylistic_fn = d["function"]
                self.text_input.show()
                self.text_input.setFocus()
                self.btn_next_phase.show()
                self.btn_next_phase.setText("✅ Antwort geben")
                self.timer.reset(30)
                self.timer.start()
                self._current_phase = "stylistics_answer"
            else:
                self._phase_scores.append(80)
                self._current_phase = "done"
                self._advance_phase()

        elif self._current_phase == "stylistics_answer":
            self.text_input.hide()
            self._show_answer(
                f"✔ Stilmittel: <b>{self._expected_stylistic}</b><br>"
                f"💡 Funktion: {self._expected_stylistic_fn}"
            )
            self._current_phase = "stylistics_rate"
            self.btn_correct.show()
            self.btn_wrong.show()

        elif self._current_phase == "done":
            self._end_round()

    def _phase_result(self, correct: bool):
        self.btn_correct.hide()
        self.btn_wrong.hide()
        self._phase_scores.append(100 if correct else 20)
        if correct:
            engine.hit_combo()
            xp, mult = engine.add_xp("construction_correct")
            self.xp_this_mode += xp
            self.flash.flash_good(f"✅ Gut! +{xp} XP")
        else:
            engine.break_combo()
            self.flash.flash_bad("❌ Nächste Runde!")

        self._current_phase = "done" if self._current_phase == "stylistics_rate" else "stylistics"
        self.btn_next_phase.show()
        self.btn_next_phase.setText("⏭ Weiter →")

    def _show_answer(self, html: str):
        self.lbl_answer.setText(html)
        self.lbl_answer.setTextFormat(Qt.RichText)
        self.lbl_answer.show()
        self.btn_next_phase.show()
        self.btn_next_phase.setText("⏭ Weiter →")

    def _set_buttons_hidden(self):
        self.btn_correct.hide()
        self.btn_wrong.hide()
        self.btn_next_phase.hide()

    def _phase_timeout(self):
        self._advance_phase()

    def _end_round(self):
        scores = self._phase_scores
        avg = int(sum(scores) / max(len(scores), 1))
        self.round_scores.append(avg)

        if avg >= 85:
            xp, mult = engine.add_xp("boss_perfect")
            self.xp_this_mode += xp
            engine.hit_combo()
            self.flash.flash_good(f"💥 BOSS HURT! {avg}%  +{xp} XP")
        elif avg >= 60:
            xp, _ = engine.add_xp("boss_good")
            self.xp_this_mode += xp
            self.flash.flash_good(f"👊 TREFFER! {avg}%  +{xp} XP")
        else:
            xp, _ = engine.add_xp("boss_fail")
            self.xp_this_mode += xp
            engine.break_combo()
            self.flash.flash_bad(f"😵 {avg}% — Retry!")

        self.sentence_idx += 1
        QTimer.singleShot(1500, self._start_round)

    def _finish_all(self):
        total = int(sum(self.round_scores) / max(len(self.round_scores), 1))
        self.finished.emit(self.xp_this_mode, total)
