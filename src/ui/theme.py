# Dark Neon Theme

STYLESHEET = """
QWidget {
    background-color: #0A0A1A;
    color: #E0E0FF;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 14px;
}

QMainWindow {
    background-color: #0A0A1A;
}

/* ── Buttons ── */
QPushButton {
    background-color: #1A1A3A;
    color: #00FFFF;
    border: 2px solid #00FFFF;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #002244;
    border-color: #00FFFF;
    color: #FFFFFF;
}
QPushButton:pressed {
    background-color: #003366;
}
QPushButton:disabled {
    background-color: #111122;
    border-color: #333355;
    color: #444466;
}

QPushButton#btn_correct {
    background-color: #002200;
    color: #00FF88;
    border-color: #00FF88;
}
QPushButton#btn_wrong {
    background-color: #220000;
    color: #FF4444;
    border-color: #FF4444;
}
QPushButton#btn_neutral {
    background-color: #1A1A3A;
    color: #AAAACC;
    border-color: #333366;
}
QPushButton#btn_primary {
    background-color: #001133;
    color: #00FFFF;
    border-color: #00FFFF;
    font-size: 16px;
    padding: 14px 28px;
}
QPushButton#btn_boss {
    background-color: #1A0011;
    color: #FF00FF;
    border-color: #FF00FF;
    font-size: 16px;
    padding: 14px 28px;
}
QPushButton#btn_locked {
    background-color: #0D0D1A;
    color: #333355;
    border-color: #222244;
    font-size: 13px;
}

/* ── Text Input ── */
QTextEdit, QLineEdit {
    background-color: #0D0D2A;
    color: #E0E0FF;
    border: 2px solid #334466;
    border-radius: 8px;
    padding: 8px;
    font-size: 15px;
}
QTextEdit:focus, QLineEdit:focus {
    border-color: #00FFFF;
}

/* ── Labels ── */
QLabel#lbl_title {
    font-size: 26px;
    font-weight: bold;
    color: #00FFFF;
}
QLabel#lbl_subtitle {
    font-size: 14px;
    color: #8888AA;
}
QLabel#lbl_latin {
    font-size: 17px;
    color: #CCCCFF;
    font-style: italic;
    line-height: 1.6;
}
QLabel#lbl_xp {
    font-size: 13px;
    color: #FFD700;
    font-weight: bold;
}
QLabel#lbl_combo {
    font-size: 22px;
    font-weight: bold;
    color: #FF00FF;
}
QLabel#lbl_score {
    font-size: 48px;
    font-weight: bold;
    color: #00FF88;
}
QLabel#lbl_score_bad {
    font-size: 48px;
    font-weight: bold;
    color: #FF4444;
}
QLabel#lbl_timer {
    font-size: 36px;
    font-weight: bold;
    color: #FF6B00;
}
QLabel#lbl_timer_ok {
    font-size: 36px;
    font-weight: bold;
    color: #00FF88;
}
QLabel#lbl_section {
    font-size: 18px;
    font-weight: bold;
    color: #AAAAFF;
    padding: 6px 0px;
}
QLabel#lbl_hint {
    font-size: 12px;
    color: #666688;
}
QLabel#lbl_flash_good {
    font-size: 20px;
    font-weight: bold;
    color: #00FF88;
    background-color: #001100;
    border-radius: 8px;
    padding: 8px;
}
QLabel#lbl_flash_bad {
    font-size: 20px;
    font-weight: bold;
    color: #FF4444;
    background-color: #110000;
    border-radius: 8px;
    padding: 8px;
}

/* ── Progress Bar ── */
QProgressBar {
    background-color: #111133;
    border: 1px solid #333366;
    border-radius: 6px;
    text-align: center;
    color: #E0E0FF;
    height: 18px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0055FF, stop:1 #00FFFF);
    border-radius: 5px;
}

/* ── Frames / Cards ── */
QFrame#card {
    background-color: #0F0F22;
    border: 1px solid #223366;
    border-radius: 12px;
}
QFrame#card_highlight {
    background-color: #0F0F2A;
    border: 2px solid #00FFFF;
    border-radius: 12px;
}
QFrame#card_boss {
    background-color: #110011;
    border: 2px solid #FF00FF;
    border-radius: 12px;
}

/* ── Scroll ── */
QScrollArea {
    border: none;
}
QScrollBar:vertical {
    background: #0D0D1A;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #334466;
    border-radius: 4px;
    min-height: 20px;
}
"""

# Construction type → color mapping for word highlighting
CONSTRUCTION_BADGE_COLORS = {
    "AcI":                    ("#00FF88", "#001A0D"),
    "PPP":                    ("#00FFFF", "#001A1A"),
    "PPA (PC)":               ("#FF6B00", "#1A0D00"),
    "Ablativus absolutus":    ("#FFD700", "#1A1400"),
    "Gerundivum":             ("#FF00FF", "#1A001A"),
    "Gerundium":              ("#CC88FF", "#110022"),
    "ut-Satz":                ("#00AAFF", "#001122"),
    "Konditionalsatz":        ("#FF4444", "#1A0000"),
    "indirekter Fragesatz":   ("#FF00FF", "#1A001A"),
    "Relativsatz":            ("#88FFCC", "#001A11"),
    "Komparativ":             ("#FFAA00", "#1A1000"),
    "quo + Komparativ":       ("#FFD700", "#1A1400"),
    "Dativus finalis":        ("#FF6B00", "#1A0D00"),
    "Dativus possessoris":    ("#FF8C00", "#1A1100"),
    "Genitivus obiectivus":   ("#AA44FF", "#0F0022"),
    "Irrealis der Gegenwart": ("#FF0000", "#1A0000"),
    "PFA":                    ("#00FF00", "#001A00"),
    "Lokativ":                ("#44AAFF", "#000D1A"),
    "Infinitiv Präsens Passiv": ("#88CCFF", "#000E1A"),
    "Ablativus qualitatis":   ("#FFCC00", "#1A1400"),
    "Dativ (Bezug)":          ("#FF9900", "#1A1000"),
    "Relativsatz (konsekutiv)": ("#88FFCC", "#001A11"),
    "PPP (PC)":               ("#00FFFF", "#001A1A"),
}

ALL_CONSTRUCTION_TYPES = sorted(CONSTRUCTION_BADGE_COLORS.keys())
