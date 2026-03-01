# Construction Hunt: Identify highlighted constructions

import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

from src.engine.game_engine import engine, CONSTRUCTION_COLORS
from src.ui.theme import CONSTRUCTION_BADGE_COLORS, ALL_CONSTRUCTION_TYPES
from src.ui.hud_widget import FlashLabel, make_separator


def _make_distractors(correct: str, n: int = 3) -> list[str]:
    """Pick n plausible wrong construction types."""
    options = [t for t in ALL_CONSTRUCTION_TYPES if t != correct]
    random.shuffle(options)
    return options[:n]


def _highlight_html(latin: str, start_idx: int, end_idx: int, color: str, bg: str) -> str:
    """Build HTML with a highlighted span of words [start_idx..end_idx]."""
    words = latin.split()
    parts = []
    for i, w in enumerate(words):
        if start_idx <= i <= end_idx:
            parts.append(
                f'<span style="background-color:{bg}; color:{color}; '
                f'border-radius:3px; padding:2px 4px; font-weight:bold;">{w}</span>'
            )
        else:
            parts.append(f'<span style="color:#9999CC;">{w}</span>')
    return " ".join(parts)


class ConstructionHuntWidget(QWidget):
    finished = Signal(int, int)  # xp_gained, score_pct

    def __init__(self, dungeon: dict, parent=None):
        super().__init__(parent)
        self.dungeon = dungeon

        # Flatten all construction challenges from this dungeon
        self.challenges = []
        for sentence in dungeon["sentences"]:
            for c in sentence.get("constructions", []):
                if c.get("end", c["start"]) >= c["start"]:
                    self.challenges.append({
                        "sentence": sentence,
                        "construction": c,
                    })

        if not self.challenges:
            # Fallback: no constructions annotated — skip
            QTimer.singleShot(100, lambda: self.finished.emit(0, 80))
            return

        random.shuffle(self.challenges)
        self.idx = 0
        self.correct_count = 0
        self.xp_this_mode = 0
        self._answered = False

        self._build_ui()
        self._load_challenge()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 20, 32, 20)
        root.setSpacing(14)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("🎯 KONSTRUKTIONSJAGD")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #FF00FF;")
        self.lbl_progress = QLabel(f"1 / {len(self.challenges)}")
        self.lbl_progress.setStyleSheet("color: #8888AA; font-size: 14px;")
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(self.lbl_progress)
        root.addLayout(hdr)
        root.addWidget(make_separator())

        instr = QLabel("🔍 Welche Konstruktion steckt in den markierten Wörtern?")
        instr.setStyleSheet("color: #AAAACC; font-size: 13px;")
        root.addWidget(instr)

        # Latin sentence with highlight
        self.card = QFrame()
        self.card.setStyleSheet(
            "background-color: #0A0A22; border: 2px solid #FF00FF; border-radius: 14px; padding: 20px;"
        )
        card_layout = QVBoxLayout(self.card)
        self.lbl_latin = QLabel()
        self.lbl_latin.setWordWrap(True)
        self.lbl_latin.setAlignment(Qt.AlignCenter)
        self.lbl_latin.setTextFormat(Qt.RichText)
        font = QFont("Georgia", 15)
        self.lbl_latin.setFont(font)
        card_layout.addWidget(self.lbl_latin)
        root.addWidget(self.card)

        # Combo display
        self.lbl_combo_display = QLabel("")
        self.lbl_combo_display.setAlignment(Qt.AlignCenter)
        self.lbl_combo_display.setStyleSheet("color: #FF00FF; font-size: 16px; font-weight: bold;")
        root.addWidget(self.lbl_combo_display)

        # Answer buttons (2x2 grid)
        self.btn_grid = QGridLayout()
        self.answer_buttons: list[QPushButton] = []
        for i in range(4):
            btn = QPushButton("...")
            btn.setMinimumHeight(52)
            btn.setStyleSheet(
                "background-color: #111133; color: #AAAAFF; border: 2px solid #334466; "
                "border-radius: 8px; font-size: 13px; font-weight: bold; padding: 8px;"
            )
            btn.clicked.connect(lambda checked, b=i: self._answer(b))
            self.answer_buttons.append(btn)
            self.btn_grid.addWidget(btn, i // 2, i % 2)
        root.addLayout(self.btn_grid)

        # Flash
        self.flash = FlashLabel()
        root.addWidget(self.flash)

        # Explanation (shown after answer)
        self.lbl_explanation = QLabel()
        self.lbl_explanation.setWordWrap(True)
        self.lbl_explanation.setStyleSheet(
            "color: #AACCFF; font-size: 13px; background-color: #080818; "
            "border-radius: 8px; padding: 10px;"
        )
        self.lbl_explanation.hide()
        root.addWidget(self.lbl_explanation)

        self.btn_next = QPushButton("⏭ Weiter →")
        self.btn_next.setObjectName("btn_primary")
        self.btn_next.clicked.connect(self._next)
        self.btn_next.hide()
        root.addWidget(self.btn_next, 0, Qt.AlignHCenter)

        root.addStretch()

    def _load_challenge(self):
        if self.idx >= len(self.challenges):
            self._finish()
            return

        ch = self.challenges[self.idx]
        s = ch["sentence"]
        c = ch["construction"]
        self.lbl_progress.setText(f"{self.idx + 1} / {len(self.challenges)}")
        self._answered = False
        self._correct_btn_idx = None

        # Build highlighted HTML
        ctype = c["type"]
        fg, bg = CONSTRUCTION_BADGE_COLORS.get(ctype, ("#00FFFF", "#001A1A"))
        start = c.get("start", 0)
        end = c.get("end", start)
        html = _highlight_html(s["latin"], start, end, fg, bg)
        self.lbl_latin.setText(html)

        # Build answer options
        distractors = _make_distractors(ctype, 3)
        options = distractors + [ctype]
        random.shuffle(options)
        self._correct_idx = options.index(ctype)

        for i, btn in enumerate(self.answer_buttons):
            btn.setText(options[i])
            btn.setEnabled(True)
            fg2, _ = CONSTRUCTION_BADGE_COLORS.get(options[i], ("#AAAAFF", "#111133"))
            btn.setStyleSheet(
                f"background-color: #111133; color: {fg2}; border: 2px solid #334466; "
                f"border-radius: 8px; font-size: 13px; font-weight: bold; padding: 8px;"
            )

        self.lbl_explanation.hide()
        self.btn_next.hide()
        self.flash.hide()
        self.lbl_combo_display.setText(f"🔥 COMBO ×{engine.combo}" if engine.combo > 1 else "")

    def _answer(self, btn_idx: int):
        if self._answered:
            return
        self._answered = True
        ch = self.challenges[self.idx]
        c = ch["construction"]
        correct = btn_idx == self._correct_idx

        # Color buttons
        for i, btn in enumerate(self.answer_buttons):
            btn.setEnabled(False)
            if i == self._correct_idx:
                btn.setStyleSheet(
                    "background-color: #002200; color: #00FF88; border: 2px solid #00FF88; "
                    "border-radius: 8px; font-size: 13px; font-weight: bold; padding: 8px;"
                )
            elif i == btn_idx and not correct:
                btn.setStyleSheet(
                    "background-color: #220000; color: #FF4444; border: 2px solid #FF4444; "
                    "border-radius: 8px; font-size: 13px; font-weight: bold; padding: 8px;"
                )

        if correct:
            engine.hit_combo()
            xp, mult = engine.add_xp("construction_correct")
            self.xp_this_mode += xp
            self.correct_count += 1
            self.flash.flash_good(f"✅ RICHTIG! +{xp} XP  ×{mult:.1f}")
            self.lbl_combo_display.setText(f"🔥 COMBO ×{engine.combo}")
        else:
            engine.break_combo()
            engine.add_xp("construction_wrong")
            self.flash.flash_bad(f"❌ FALSCH! → {c['type']}")
            self.lbl_combo_display.setText("")

        engine.record_construction(c["type"], correct)

        # Show explanation
        self.lbl_explanation.setText(
            f"💡 <b>{c['type']}</b>: {c.get('explanation', '')}"
        )
        self.lbl_explanation.show()
        self.btn_next.show()

    def _next(self):
        self.idx += 1
        self._load_challenge()

    def _finish(self):
        total = len(self.challenges)
        pct = int(100 * self.correct_count / max(total, 1))
        self.finished.emit(self.xp_this_mode, pct)
