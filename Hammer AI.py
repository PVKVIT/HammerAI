
import sys
import os
import json
import time
import math
import traceback
import threading
import datetime
import re
from typing import Optional, List, Dict, Any

# ── Third-party imports ────────────────────────────────────────────────────────
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QSplitter, QVBoxLayout,
        QHBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit,
        QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
        QScrollArea, QFrame, QComboBox, QDoubleSpinBox, QSpinBox,
        QMenuBar, QMenu, QAction, QFileDialog, QStatusBar,
        QMessageBox, QDialog, QGroupBox, QToolBar, QSizePolicy,
        QProgressBar, QSlider, QTabWidget, QToolButton, QStackedWidget,
        QInputDialog, QStyle, QCheckBox, QDialogButtonBox
    )
    from PyQt5.QtCore import (
        Qt, QThread, pyqtSignal, QTimer, QSize, QRect, QPoint
    )
    from PyQt5.QtGui import (
        QFont, QColor, QPalette, QIcon, QPixmap, QPainter, QPen,
        QBrush, QLinearGradient, QTextCursor, QPolygon
    )
    HAS_PYQT5 = True
except ImportError:
    HAS_PYQT5 = False
    print("PyQt5 not found. Install: pip install PyQt5")

try:
    import pyvista as pv
    from pyvistaqt import QtInteractor
    HAS_PYVISTA = True
except ImportError:
    HAS_PYVISTA = False
    print("PyVista/pyvistaqt not found. Install: pip install pyvista pyvistaqt")

try:
    import cadquery as cq
    import numpy as np
    HAS_CADQUERY = True
except ImportError:
    HAS_CADQUERY = False
    print("CadQuery not found. Install: pip install cadquery")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("requests not found. Install: pip install requests")

# ── Constants ──────────────────────────────────────────────────────────────────
APP_NAME = "HammerAI"
APP_VERSION = "1.1.0"
AUTOSAVE_PATH = "cad_session.json"
SETTINGS_PATH = "cad_settings.json"
GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)

# ── Theme Definitions ──────────────────────────────────────────────────────────
THEMES: Dict[str, Dict[str, str]] = {
    "Dark Hacker": {
        "bg": "#0d1117", "panel": "#161b22", "border": "#30363d",
        "text": "#c9d1d9", "accent": "#3fb950", "hover": "#238636",
        "dim": "#8b949e", "danger": "#f85149",
        "user_bg": "#1f3a2d", "user_bd": "#2ea043",
    },
    "Midnight Blue": {
        "bg": "#0a0e1a", "panel": "#111827", "border": "#1e3a5f",
        "text": "#e2e8f0", "accent": "#3b82f6", "hover": "#2563eb",
        "dim": "#64748b", "danger": "#ef4444",
        "user_bg": "#1e3a5f", "user_bd": "#3b82f6",
    },
    "Solarized Dark": {
        "bg": "#002b36", "panel": "#073642", "border": "#586e75",
        "text": "#839496", "accent": "#268bd2", "hover": "#2aa198",
        "dim": "#586e75", "danger": "#dc322f",
        "user_bg": "#073642", "user_bd": "#268bd2",
    },
    "Light": {
        "bg": "#f6f8fa", "panel": "#ffffff", "border": "#d0d7de",
        "text": "#24292f", "accent": "#1a7f37", "hover": "#2da44e",
        "dim": "#57606a", "danger": "#cf222e",
        "user_bg": "#dafbe1", "user_bd": "#2da44e",
    },
}


def build_stylesheet(t: Dict[str, str]) -> str:
    """Generate full QSS stylesheet from a theme palette dict."""
    return f"""
QWidget {{
    background-color: {t['bg']};
    color: {t['text']};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
}}
QMainWindow {{ background-color: {t['bg']}; }}
QMenuBar {{
    background-color: {t['panel']};
    color: {t['text']};
    border-bottom: 1px solid {t['border']};
    padding: 2px;
}}
QMenuBar::item:selected {{
    background-color: {t['hover']};
    color: #ffffff;
    border-radius: 3px;
}}
QMenu {{
    background-color: {t['panel']};
    border: 1px solid {t['border']};
    color: {t['text']};
}}
QMenu::item:selected {{ background-color: {t['hover']}; }}
QToolBar {{
    background-color: {t['panel']};
    border: none;
    border-bottom: 1px solid {t['border']};
    spacing: 4px;
    padding: 3px 6px;
}}
QPushButton {{
    background-color: {t['panel']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: 4px;
    padding: 5px 12px;
    min-height: 24px;
}}
QPushButton:hover {{
    background-color: {t['hover']};
    border-color: {t['accent']};
    color: #ffffff;
}}
QPushButton:pressed {{ background-color: {t['hover']}; }}
QPushButton:disabled {{
    background-color: {t['panel']};
    color: {t['dim']};
    border-color: {t['panel']};
}}
QToolButton {{
    background-color: {t['panel']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: 4px;
    padding: 4px 10px;
}}
QToolButton:hover {{
    background-color: {t['hover']};
    color: #ffffff;
}}
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {{
    background-color: {t['panel']};
    border: 1px solid {t['border']};
    border-radius: 4px;
    color: {t['text']};
    padding: 4px 8px;
    selection-background-color: {t['accent']};
}}
QLineEdit:focus, QTextEdit:focus {{ border-color: {t['accent']}; }}
QComboBox {{
    background-color: {t['panel']};
    border: 1px solid {t['border']};
    border-radius: 4px;
    color: {t['text']};
    padding: 4px 8px;
    min-height: 24px;
}}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background-color: {t['panel']};
    border: 1px solid {t['border']};
    selection-background-color: {t['hover']};
    color: {t['text']};
}}
QScrollBar:vertical {{
    background-color: {t['bg']};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background-color: {t['border']};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background-color: {t['accent']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar:horizontal {{
    background-color: {t['bg']};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background-color: {t['border']};
    border-radius: 4px;
    min-width: 20px;
}}
QListWidget {{
    background-color: {t['panel']};
    border: 1px solid {t['border']};
    border-radius: 4px;
    outline: none;
}}
QListWidget::item {{ padding: 4px 8px; border-radius: 2px; }}
QListWidget::item:selected {{ background-color: {t['hover']}; color: #ffffff; }}
QListWidget::item:hover {{ background-color: {t['panel']}; }}
QTreeWidget {{
    background-color: {t['panel']};
    border: 1px solid {t['border']};
    border-radius: 4px;
    outline: none;
}}
QTreeWidget::item {{ padding: 2px 4px; }}
QTreeWidget::item:selected {{ background-color: {t['hover']}; }}
QTreeWidget::item:hover {{ background-color: {t['panel']}; }}
QGroupBox {{
    border: 1px solid {t['border']};
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 6px;
    color: {t['dim']};
    font-size: 11px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 4px;
    color: {t['accent']};
}}
QStatusBar {{
    background-color: {t['panel']};
    border-top: 1px solid {t['border']};
    color: {t['dim']};
    font-size: 11px;
}}
QTabWidget::pane {{
    border: 1px solid {t['border']};
    background-color: {t['panel']};
}}
QTabBar::tab {{
    background-color: {t['bg']};
    color: {t['dim']};
    border: 1px solid {t['border']};
    padding: 6px 12px;
    border-bottom: none;
}}
QTabBar::tab:selected {{
    background-color: {t['panel']};
    color: {t['accent']};
    border-top: 2px solid {t['accent']};
}}
QSplitter::handle {{
    background-color: {t['border']};
    width: 2px;
    height: 2px;
}}
QLabel#section_title {{
    color: {t['accent']};
    font-weight: bold;
    font-size: 12px;
    border-bottom: 1px solid {t['border']};
    padding-bottom: 4px;
}}
QFrame#separator {{
    background-color: {t['border']};
    max-height: 1px;
}}
QCheckBox {{
    color: {t['text']};
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {t['border']};
    border-radius: 3px;
    background: {t['panel']};
}}
QCheckBox::indicator:checked {{
    background: {t['accent']};
    border-color: {t['accent']};
}}
QSlider::groove:horizontal {{
    height: 4px;
    background: {t['border']};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    width: 14px;
    height: 14px;
    background: {t['accent']};
    border-radius: 7px;
    margin: -5px 0;
}}
QSlider::sub-page:horizontal {{
    background: {t['accent']};
    border-radius: 2px;
}}
QProgressBar {{
    background-color: {t['panel']};
    border: none;
    border-radius: 2px;
}}
QProgressBar::chunk {{
    background-color: {t['accent']};
    border-radius: 2px;
}}
"""


# ── Active theme (mutable, updated by Settings) ────────────────────────────────
_current_theme_name = "Dark Hacker"
_current_theme = THEMES["Dark Hacker"]


def current_stylesheet() -> str:
    """Return QSS for the currently active theme."""
    return build_stylesheet(_current_theme)


# ── Hex Logo Widget ────────────────────────────────────────────────────────────

class _HexLogo(QLabel):
    """Custom painted hexagonal CAD logo used in the splash screen."""

    def __init__(self, size: int = 64, parent=None):
        super().__init__(parent)
        self._sz = size
        self.setFixedSize(size, size)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        cx, cy = self._sz / 2, self._sz / 2
        r = self._sz / 2 - 4

        grad = QLinearGradient(0, 0, self._sz, self._sz)
        grad.setColorAt(0, QColor("#238636"))
        grad.setColorAt(1, QColor("#0d1117"))

        pts = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            pts.append(QPoint(int(cx + r * math.cos(angle)),
                               int(cy + r * math.sin(angle))))
        poly = QPolygon(pts)
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor("#3fb950"), 1.5))
        painter.drawPolygon(poly)

        painter.setPen(QPen(QColor("#ffffff"), 2))
        painter.setFont(QFont("Consolas", int(self._sz * 0.38), QFont.Bold))
        painter.drawText(QRect(0, 0, self._sz, self._sz), Qt.AlignCenter, "C")
        painter.end()


# ── Splash Screen ──────────────────────────────────────────────────────────────

class SplashScreen(QWidget):
    """
    SolidWorks-inspired animated splash screen displayed before
    the main window appears.
    """

    finished = pyqtSignal()

    _TIPS = [
        "Initializing CAD engine...",
        "Loading component library...",
        "Preparing 3D viewport...",
        "Connecting workflow manager...",
        "Setting up AI interface...",
        "Almost ready...",
    ]

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setFixedSize(680, 400)
        self._progress = 0
        self._tip_idx = 0
        self._build_ui()
        self._center()
        self._start_animation()

    def _center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
        )

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        content = QWidget()
        content.setStyleSheet("background-color: #0d1117; border: 1px solid #30363d;")
        clyt = QVBoxLayout(content)
        clyt.setContentsMargins(48, 40, 48, 32)
        clyt.setSpacing(0)

        # Brand row
        brand_row = QHBoxLayout()
        brand_row.setSpacing(16)

        logo = _HexLogo(size=72)
        brand_row.addWidget(logo)

        title_col = QVBoxLayout()
        title_col.setSpacing(4)

        name_lbl = QLabel(APP_NAME.upper())
        name_lbl.setStyleSheet(
            "color: #ffffff; font-size: 32px; font-weight: bold; "
            "font-family: 'Consolas', monospace; letter-spacing: 4px;"
        )
        title_col.addWidget(name_lbl)

        sub_lbl = QLabel("CAD Assistant")
        sub_lbl.setStyleSheet(
            "color: #3fb950; font-size: 10px; letter-spacing: 3px; "
            "font-family: 'Consolas', monospace;"
        )
        title_col.addWidget(sub_lbl)
        brand_row.addLayout(title_col)
        brand_row.addStretch()

        ver_lbl = QLabel(f"v{APP_VERSION}")
        ver_lbl.setStyleSheet("color: #484f58; font-size: 11px;")
        ver_lbl.setAlignment(Qt.AlignRight | Qt.AlignTop)
        brand_row.addWidget(ver_lbl)
        clyt.addLayout(brand_row)
        clyt.addSpacing(36)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #21262d; border: none; max-height: 1px;")
        clyt.addWidget(sep)
        clyt.addSpacing(28)

        for feat in [
            "●  Generative CAD from natural language prompts",
            "●  Interactive 3D visualization & stress simulation",
            "●  Manufacturing cost & feasibility analysis",
            "●  Versioned workflow history & component library",
        ]:
            lbl = QLabel(feat)
            lbl.setStyleSheet("color: #8b949e; font-size: 11px; margin: 2px 0;")
            clyt.addWidget(lbl)

        clyt.addStretch()

        self.tip_label = QLabel(self._TIPS[0])
        self.tip_label.setStyleSheet("color: #484f58; font-size: 11px;")
        clyt.addWidget(self.tip_label)
        clyt.addSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setStyleSheet("""
            QProgressBar { background-color: #21262d; border: none; border-radius: 2px; }
            QProgressBar::chunk { background-color: #3fb950; border-radius: 2px; }
        """)
        clyt.addWidget(self.progress_bar)
        clyt.addSpacing(16)

        footer_row = QHBoxLayout()
        copy_lbl = QLabel("© 2025 HammerAI")
        copy_lbl.setStyleSheet("color: #21262d; font-size: 10px;")
        footer_row.addWidget(copy_lbl)
        footer_row.addStretch()
        powered_lbl = QLabel("Powered by Google Gemini · CadQuery · PyVista")
        powered_lbl.setStyleSheet("color: #21262d; font-size: 10px;")
        footer_row.addWidget(powered_lbl)
        clyt.addLayout(footer_row)

        layout.addWidget(content)

    def _start_animation(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(35)

    def _tick(self):
        self._progress += 1
        self.progress_bar.setValue(self._progress)
        tip_at = min(int(self._progress / 100 * len(self._TIPS)), len(self._TIPS) - 1)
        if tip_at != self._tip_idx:
            self._tip_idx = tip_at
            self.tip_label.setText(self._TIPS[self._tip_idx])
        if self._progress >= 100:
            self._timer.stop()
            QTimer.singleShot(300, self.finished.emit)


# ── Settings Window ────────────────────────────────────────────────────────────

class SettingsWindow(QDialog):
    """Settings dialog: API key, theme selection, visibility, panel sizes."""

    settings_applied = pyqtSignal(dict)

    def __init__(self, current_settings: Dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(540, 560)
        self.setStyleSheet(current_stylesheet())
        self._settings = dict(current_settings)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        tabs = QTabWidget()

        # ── API Tab ───────────────────────────────────────────────────────────
        api_tab = QWidget()
        api_lyt = QVBoxLayout(api_tab)
        api_lyt.setContentsMargins(12, 12, 12, 12)
        api_lyt.setSpacing(10)

        t = QLabel("API Configuration")
        t.setObjectName("section_title")
        api_lyt.addWidget(t)

        api_lyt.addWidget(QLabel("Gemini API Key:"))
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("AIza...")
        self.api_key_edit.setText(self._settings.get("api_key", ""))
        api_lyt.addWidget(self.api_key_edit)

        show_chk = QCheckBox("Show API key")
        show_chk.toggled.connect(
            lambda v: self.api_key_edit.setEchoMode(
                QLineEdit.Normal if v else QLineEdit.Password
            )
        )
        api_lyt.addWidget(show_chk)

        api_lyt.addWidget(QLabel("Gemini Model URL:"))
        self.model_url_edit = QLineEdit()
        self.model_url_edit.setText(
            self._settings.get("model_url", GEMINI_API_URL)
        )
        api_lyt.addWidget(self.model_url_edit)
        api_lyt.addStretch()
        tabs.addTab(api_tab, "🔑  API")

        # ── Theme Tab ─────────────────────────────────────────────────────────
        theme_tab = QWidget()
        theme_lyt = QVBoxLayout(theme_tab)
        theme_lyt.setContentsMargins(12, 12, 12, 12)
        theme_lyt.setSpacing(10)

        t2 = QLabel("Appearance")
        t2.setObjectName("section_title")
        theme_lyt.addWidget(t2)

        theme_lyt.addWidget(QLabel("Color Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEMES.keys()))
        self.theme_combo.setCurrentText(self._settings.get("theme", "Dark Hacker"))
        self.theme_combo.currentTextChanged.connect(self._preview_theme)
        theme_lyt.addWidget(self.theme_combo)

        note = QLabel(
            "Theme preview applies immediately.\n"
            "Click Apply or OK to save permanently."
        )
        note.setStyleSheet(f"color: {_current_theme['dim']}; font-size: 11px;")
        note.setWordWrap(True)
        theme_lyt.addWidget(note)
        theme_lyt.addStretch()
        tabs.addTab(theme_tab, "🎨  Theme")

        # ── Layout Tab ────────────────────────────────────────────────────────
        layout_tab = QWidget()
        layout_lyt = QVBoxLayout(layout_tab)
        layout_lyt.setContentsMargins(12, 12, 12, 12)
        layout_lyt.setSpacing(10)

        t3 = QLabel("Section Visibility")
        t3.setObjectName("section_title")
        layout_lyt.addWidget(t3)

        vis = self._settings.get("visibility", {})

        self.chk_toolbar = QCheckBox("Show Left Toolbar Panel")
        self.chk_toolbar.setChecked(vis.get("toolbar", True))
        layout_lyt.addWidget(self.chk_toolbar)

        self.chk_chat = QCheckBox("Show Chat Panel")
        self.chk_chat.setChecked(vis.get("chat", True))
        layout_lyt.addWidget(self.chk_chat)

        self.chk_statusbar = QCheckBox("Show Status Bar")
        self.chk_statusbar.setChecked(vis.get("statusbar", True))
        layout_lyt.addWidget(self.chk_statusbar)

        self.chk_feature_overlay = QCheckBox("Show Feature Tree Overlay in Viewport")
        self.chk_feature_overlay.setChecked(vis.get("feature_overlay", True))
        layout_lyt.addWidget(self.chk_feature_overlay)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("separator")
        layout_lyt.addWidget(sep)

        t4 = QLabel("Panel Sizes")
        t4.setObjectName("section_title")
        layout_lyt.addWidget(t4)

        layout_lyt.addWidget(QLabel("Left Toolbar Width (px):"))
        self.toolbar_width_spin = QSpinBox()
        self.toolbar_width_spin.setRange(140, 400)
        self.toolbar_width_spin.setValue(self._settings.get("toolbar_width", 200))
        layout_lyt.addWidget(self.toolbar_width_spin)

        layout_lyt.addWidget(QLabel("Chat Panel Width (px):"))
        self.chat_width_spin = QSpinBox()
        self.chat_width_spin.setRange(200, 600)
        self.chat_width_spin.setValue(self._settings.get("chat_width", 340))
        layout_lyt.addWidget(self.chat_width_spin)

        layout_lyt.addStretch()
        tabs.addTab(layout_tab, "📐  Layout")

        layout.addWidget(tabs)

        btn_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        btn_box.accepted.connect(self._accept)
        btn_box.rejected.connect(self.reject)
        btn_box.button(QDialogButtonBox.Apply).clicked.connect(self._apply)
        layout.addWidget(btn_box)

    def _preview_theme(self, name: str):
        global _current_theme, _current_theme_name
        if name in THEMES:
            _current_theme_name = name
            _current_theme = THEMES[name]
            QApplication.instance().setStyleSheet(current_stylesheet())

    def _collect(self) -> Dict:
        return {
            "api_key": self.api_key_edit.text().strip(),
            "model_url": self.model_url_edit.text().strip(),
            "theme": self.theme_combo.currentText(),
            "toolbar_width": self.toolbar_width_spin.value(),
            "chat_width": self.chat_width_spin.value(),
            "visibility": {
                "toolbar": self.chk_toolbar.isChecked(),
                "chat": self.chk_chat.isChecked(),
                "statusbar": self.chk_statusbar.isChecked(),
                "feature_overlay": self.chk_feature_overlay.isChecked(),
            }
        }

    def _apply(self):
        self.settings_applied.emit(self._collect())

    def _accept(self):
        self.settings_applied.emit(self._collect())
        self.accept()


# ── Gemini API Client ──────────────────────────────────────────────────────────

class GeminiClient:
    """Handles communication with the Google Gemini API."""

    SYSTEM_INSTRUCTION = (
        "You are a CAD code generator. "
        "ONLY RETURN VALID CADQUERY PYTHON CODE. NO TEXT. NO MARKDOWN. "
        "NO CODE FENCES. Do not wrap the code in triple backticks. "
        "The code must assign the final solid to a variable named 'result'. "
        "Use only cadquery (imported as cq). Do not use any other imports. "
        "Example: result = cq.Workplane('XY').box(10, 10, 10)"
    )

    def __init__(self):
        self.api_key: Optional[str] = None
        self.active: bool = False
        self.model_url: str = GEMINI_API_URL

    def set_api_key(self, key: str) -> bool:
        """Validate and store the API key."""
        if not key or len(key) < 10:
            return False
        self.api_key = key.strip()
        self.active = True
        return True

    def generate_cad_code(self, prompt: str, history: List[Dict]) -> str:
        """Send prompt to Gemini and return CADQuery code."""
        if not self.active or not HAS_REQUESTS:
            raise RuntimeError("API not active or requests library missing.")

        messages = []
        for msg in history[-6:]:
            if msg["role"] in ("user", "assistant"):
                messages.append({
                    "role": "user" if msg["role"] == "user" else "model",
                    "parts": [{"text": msg["content"]}]
                })
        messages.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "system_instruction": {"parts": [{"text": self.SYSTEM_INSTRUCTION}]},
            "contents": messages,
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024}
        }

        resp = requests.post(
            f"{self.model_url}?key={self.api_key}",
            json=payload,
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            text = text.strip()
            text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
            return text.strip()
        except (KeyError, IndexError) as exc:
            raise RuntimeError(f"Unexpected Gemini response: {data}") from exc


# ── Safety Executor ────────────────────────────────────────────────────────────

class SafetyExecutor:
    """Executes CADQuery scripts in a sandboxed namespace."""

    BANNED_PATTERNS = [
        r'\bimport\s+os\b', r'\bimport\s+sys\b', r'\bopen\s*\(',
        r'\bexec\s*\(', r'\beval\s*\(', r'__import__',
        r'\bsubprocess\b', r'\bshutil\b', r'\bpathlib\b', r'\bsocket\b',
    ]

    @classmethod
    def is_safe(cls, code: str) -> tuple:
        for pattern in cls.BANNED_PATTERNS:
            if re.search(pattern, code):
                return False, f"Blocked pattern: {pattern}"
        return True, ""

    @classmethod
    def execute(cls, code: str) -> Any:
        """Execute CADQuery code safely. Returns the 'result' variable."""
        safe, reason = cls.is_safe(code)
        if not safe:
            raise PermissionError(f"Code blocked: {reason}")
        namespace: Dict[str, Any] = {}
        if HAS_CADQUERY:
            namespace["cq"] = cq
        if HAS_PYVISTA:
            namespace["np"] = np
        exec(code, namespace)  # noqa: S102
        if "result" not in namespace:
            raise ValueError("Code must assign the solid to 'result'.")
        return namespace["result"]


# ── CAD Model Manager ──────────────────────────────────────────────────────────

class CADModelManager:
    """Manages the current CADQuery solid, mesh conversion, and properties."""

    def __init__(self):
        self.current_solid = None
        self.current_mesh: Optional["pv.PolyData"] = None
        self.current_code: str = ""

    def load_code(self, code: str) -> "pv.PolyData":
        solid = SafetyExecutor.execute(code)
        self.current_solid = solid
        self.current_code = code
        self.current_mesh = self._solid_to_mesh(solid)
        return self.current_mesh

    def _solid_to_mesh(self, solid) -> "pv.PolyData":
        if not HAS_CADQUERY or not HAS_PYVISTA:
            return pv.Sphere(radius=5)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            cq.exporters.export(solid, tmp_path)
            mesh = pv.read(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        return mesh

    def get_properties(self) -> Dict[str, Any]:
        if self.current_mesh is None:
            return {"volume": 0.0, "surface_area": 0.0, "bounding_box": None}
        mesh = self.current_mesh
        volume = abs(mesh.volume) if hasattr(mesh, "volume") else 0.0
        surface_area = mesh.area if hasattr(mesh, "area") else 0.0
        bounds = mesh.bounds
        bbox = {
            "x": bounds[1] - bounds[0],
            "y": bounds[3] - bounds[2],
            "z": bounds[5] - bounds[4]
        }
        return {"volume": volume, "surface_area": surface_area, "bounding_box": bbox}

    def get_vertex_count(self) -> int:
        if self.current_mesh is None:
            return 0
        return self.current_mesh.n_points


# ── Workflow Manager ───────────────────────────────────────────────────────────

class WorkflowManager:
    """Manages versioned history of CAD model states."""

    def __init__(self):
        self.versions: List[Dict[str, Any]] = []
        self.pointer: int = -1

    def add_version(self, code: str, description: str = ""):
        self.versions = self.versions[: self.pointer + 1]
        entry = {
            "id": len(self.versions) + 1,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "description": description or f"Version {len(self.versions) + 1}",
            "cad_code": code
        }
        self.versions.append(entry)
        self.pointer = len(self.versions) - 1

    def undo(self) -> Optional[Dict]:
        if self.pointer > 0:
            self.pointer -= 1
            return self.versions[self.pointer]
        return None

    def redo(self) -> Optional[Dict]:
        if self.pointer < len(self.versions) - 1:
            self.pointer += 1
            return self.versions[self.pointer]
        return None

    def reset(self):
        self.versions.clear()
        self.pointer = -1

    def to_serializable(self) -> List[Dict]:
        return self.versions[:]


# ── Prebuilt Component Library ─────────────────────────────────────────────────

COMPONENT_TEMPLATES: Dict[str, str] = {
    "Bolt": """import cadquery as cq
result = (
    cq.Workplane("XY")
    .circle(3).extrude(20)
    .faces(">Z").workplane()
    .circle(5).extrude(5)
)""",
    "Nut": """import cadquery as cq
result = (
    cq.Workplane("XY")
    .polygon(6, 10).extrude(5)
    .faces(">Z").workplane()
    .circle(3).cutThruAll()
)""",
    "Screw": """import cadquery as cq
result = (
    cq.Workplane("XY")
    .circle(2.5).extrude(18)
    .faces(">Z").workplane()
    .polygon(6, 6).extrude(4)
)""",
    "Washer": """import cadquery as cq
result = (
    cq.Workplane("XY")
    .circle(8).extrude(2)
    .faces(">Z").workplane()
    .circle(4).cutThruAll()
)""",
    "Coupling": """import cadquery as cq
result = (
    cq.Workplane("XY")
    .circle(8).extrude(20)
    .faces(">Z").workplane()
    .circle(5).cutThruAll()
    .faces("<Z").workplane()
    .circle(5).cutThruAll()
)""",
    "Connector": """import cadquery as cq
result = (
    cq.Workplane("XY")
    .box(20, 10, 5)
    .faces(">Z").workplane()
    .rarray(10, 1, 2, 1)
    .circle(2).cutThruAll()
)""",
}

# ── Manufacturing Estimation ───────────────────────────────────────────────────

MATERIALS_DB: Dict[str, Dict[str, float]] = {
    "Steel":          {"cost_per_cm3": 0.08,  "density": 7.85, "machining_factor": 1.2},
    "Aluminum":       {"cost_per_cm3": 0.15,  "density": 2.70, "machining_factor": 0.9},
    "Titanium":       {"cost_per_cm3": 1.20,  "density": 4.51, "machining_factor": 2.5},
    "PLA (3D Print)": {"cost_per_cm3": 0.05,  "density": 1.24, "machining_factor": 0.5},
    "ABS (3D Print)": {"cost_per_cm3": 0.06,  "density": 1.05, "machining_factor": 0.6},
}

METHOD_FACTORS: Dict[str, Dict[str, float]] = {
    "CNC":               {"cost_factor": 1.5, "speed_constant": 0.002, "energy_factor": 3.0},
    "3D Printing":       {"cost_factor": 0.8, "speed_constant": 0.005, "energy_factor": 1.5},
    "Injection Molding": {"cost_factor": 2.0, "speed_constant": 0.001, "energy_factor": 4.0},
}


class ManufacturingEstimator:
    @staticmethod
    def estimate(
        volume_cm3: float, surface_area_cm2: float,
        material_name: str, method_name: str
    ) -> Dict[str, float]:
        mat = MATERIALS_DB.get(material_name, MATERIALS_DB["Steel"])
        meth = METHOD_FACTORS.get(method_name, METHOD_FACTORS["CNC"])
        cost = volume_cm3 * mat["cost_per_cm3"] * meth["cost_factor"] * mat["machining_factor"]
        return {
            "cost_usd": round(cost, 2),
            "time_hours": round(surface_area_cm2 * meth["speed_constant"], 3),
            "energy_kwh": round(volume_cm3 * meth["energy_factor"] * 0.001, 4),
            "material_mass_g": round(volume_cm3 * mat["density"], 2),
        }


# ── Feature Tree Parser ────────────────────────────────────────────────────────

CADQUERY_OPS = [
    "box", "sphere", "cylinder", "cone", "torus", "wedge",
    "extrude", "revolve", "loft", "sweep",
    "fillet", "chamfer", "shell",
    "cut", "union", "intersect", "cutThruAll", "cutBlind",
    "hole", "cboreHole", "cskHole",
    "polygon", "circle", "rect", "slot",
    "workplane", "faces", "edges", "vertices",
    "rarray", "polarArray",
]


def parse_feature_tree(code: str) -> List[str]:
    """Extract CADQuery operation names from code text."""
    code_lower = code.lower()
    return [op for op in CADQUERY_OPS if op.lower() in code_lower]


# ── API Worker Thread ──────────────────────────────────────────────────────────

class APIWorker(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, client: GeminiClient, prompt: str, history: List[Dict]):
        super().__init__()
        self.client = client
        self.prompt = prompt
        self.history = history

    def run(self):
        try:
            self.response_ready.emit(
                self.client.generate_cad_code(self.prompt, self.history)
            )
        except Exception as exc:
            self.error_occurred.emit(str(exc))


# ── Simulation Window ──────────────────────────────────────────────────────────

class SimulationWindow(QDialog):
    def __init__(self, cad_manager: CADModelManager, parent=None):
        super().__init__(parent)
        self.cad_manager = cad_manager
        self.setWindowTitle("Stress Simulation")
        self.setMinimumSize(900, 650)
        self.setStyleSheet(current_stylesheet())
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        ctrl = QWidget()
        ctrl.setFixedWidth(240)
        cl = QVBoxLayout(ctrl)
        cl.setContentsMargins(4, 4, 4, 4)
        cl.setSpacing(8)

        t = QLabel("Simulation Parameters")
        t.setObjectName("section_title")
        cl.addWidget(t)

        for label, attr, rng, val, suffix in [
            ("Material", None, None, None, None),
            ("Applied Force (N)", "force_spin", (0.1, 1e6), 1000.0, " N"),
            ("Young's Modulus (GPa)", "youngs_spin", (0.1, 1000), 200.0, " GPa"),
            ("Poisson's Ratio", "poisson_spin", (0.01, 0.499), 0.3, ""),
        ]:
            grp = QGroupBox(label)
            gl = QVBoxLayout(grp)
            if attr is None:
                self.mat_combo = QComboBox()
                self.mat_combo.addItems(list(MATERIALS_DB.keys()))
                gl.addWidget(self.mat_combo)
            else:
                spin = QDoubleSpinBox()
                spin.setRange(*rng)
                spin.setValue(val)
                if suffix:
                    spin.setSuffix(suffix)
                if attr == "poisson_spin":
                    spin.setSingleStep(0.01)
                setattr(self, attr, spin)
                gl.addWidget(spin)
            cl.addWidget(grp)

        run_btn = QPushButton("▶  Run Simulation")
        run_btn.clicked.connect(self._run_simulation)
        cl.addWidget(run_btn)

        self.result_label = QLabel("Awaiting simulation...")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet(
            f"color: {_current_theme['accent']}; font-size: 11px;"
        )
        cl.addWidget(self.result_label)
        cl.addStretch()
        layout.addWidget(ctrl)

        if HAS_PYVISTA:
            self.plotter = QtInteractor(self)
            self.plotter.setMinimumSize(500, 500)
            self.plotter.enable_cell_picking(
                callback=self._on_cell_picked, show_message=False, font_size=10
            )
            layout.addWidget(self.plotter)
        else:
            layout.addWidget(QLabel("PyVista not available."))

    def _run_simulation(self):
        if not HAS_PYVISTA or self.cad_manager.current_mesh is None:
            self.result_label.setText("No model loaded.")
            return
        mesh = self.cad_manager.current_mesh.copy()
        pts = mesh.points
        distances = np.linalg.norm(pts - mesh.center, axis=1)
        falloff = (distances.max() or 1.0) * 0.5
        force = self.force_spin.value()
        youngs = self.youngs_spin.value() * 1e9
        sv = force * np.exp(-distances / falloff)
        sv = sv / sv.max() * (force / (youngs * 1e-9))
        mesh.point_data["Stress (MPa)"] = sv
        self.plotter.clear()
        self.plotter.add_mesh(mesh, scalars="Stress (MPa)", cmap="plasma",
                               show_edges=True, edge_color=_current_theme["border"])
        self.plotter.add_scalar_bar("Stress (MPa)", color=_current_theme["text"],
                                     background_color=_current_theme["panel"])
        self.plotter.set_background(_current_theme["bg"])
        self.plotter.reset_camera()
        self.result_label.setText(
            f"Peak Stress: {sv.max():.4f} MPa\n"
            f"Force: {force:.1f} N\nMaterial: {self.mat_combo.currentText()}"
        )

    def _on_cell_picked(self, cell):
        if cell is None or not HAS_PYVISTA or self.cad_manager.current_mesh is None:
            return
        mesh = self.cad_manager.current_mesh
        distances = np.linalg.norm(mesh.points - cell.center, axis=1)
        falloff = (mesh.bounds[1] - mesh.bounds[0]) * 0.3
        force = self.force_spin.value()
        youngs = self.youngs_spin.value() * 1e9
        stress = force * np.exp(-distances / falloff) / (youngs * 1e-9)
        self.result_label.setText(
            f"Cell stress: {stress.max():.4f} MPa\n"
            "Click 'Run Simulation' to refresh."
        )

    def closeEvent(self, event):
        if HAS_PYVISTA and hasattr(self, "plotter"):
            self.plotter.close()
        super().closeEvent(event)


# ── Manufacturing Window ───────────────────────────────────────────────────────

class ManufacturingWindow(QDialog):
    def __init__(self, cad_manager: CADModelManager, parent=None):
        super().__init__(parent)
        self.cad_manager = cad_manager
        self.setWindowTitle("Manufacturing Analysis")
        self.setMinimumSize(520, 420)
        self.setStyleSheet(current_stylesheet())
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        t = QLabel("Manufacturing Estimation")
        t.setObjectName("section_title")
        layout.addWidget(t)

        row = QHBoxLayout()
        for label, attr, items in [
            ("Material", "mat_combo", list(MATERIALS_DB.keys())),
            ("Method", "meth_combo", list(METHOD_FACTORS.keys())),
        ]:
            grp = QGroupBox(label)
            gl = QVBoxLayout(grp)
            cb = QComboBox()
            cb.addItems(items)
            gl.addWidget(cb)
            setattr(self, attr, cb)
            row.addWidget(grp)
        layout.addLayout(row)

        calc_btn = QPushButton("▶  Calculate")
        calc_btn.clicked.connect(self._calculate)
        layout.addWidget(calc_btn)

        self.results_label = QLabel("Enter parameters and click Calculate.")
        self.results_label.setStyleSheet(
            f"color: {_current_theme['text']}; font-size: 13px; "
            f"background-color: {_current_theme['panel']}; "
            f"border: 1px solid {_current_theme['border']}; "
            "border-radius: 4px; padding: 12px;"
        )
        self.results_label.setWordWrap(True)
        self.results_label.setMinimumHeight(180)
        self.results_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.results_label)

        btn_row = QHBoxLayout()
        for label, slot in [
            ("⚙  Optimize Cost", self._optimize_cost),
            ("⏱  Optimize Time", self._optimize_time),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

    def _calculate(self):
        props = self.cad_manager.get_properties()
        v_cm3 = props["volume"] / 1000.0
        s_cm2 = props["surface_area"] / 100.0
        r = ManufacturingEstimator.estimate(
            v_cm3, s_cm2, self.mat_combo.currentText(), self.meth_combo.currentText()
        )
        bbox = props["bounding_box"]
        bbox_str = (
            f"{bbox['x']:.1f} × {bbox['y']:.1f} × {bbox['z']:.1f} mm"
            if bbox else "N/A"
        )
        self.results_label.setText(
            f"  Material:         {self.mat_combo.currentText()}\n"
            f"  Method:           {self.meth_combo.currentText()}\n\n"
            f"  Estimated Cost:   ${r['cost_usd']:.2f}\n"
            f"  Est. Time:        {r['time_hours']:.3f} hours\n"
            f"  Energy Usage:     {r['energy_kwh']:.4f} kWh\n"
            f"  Material Mass:    {r['material_mass_g']:.2f} g\n\n"
            f"  Volume:           {v_cm3:.3f} cm³\n"
            f"  Surface Area:     {s_cm2:.3f} cm²\n"
            f"  Bounding Box:     {bbox_str}"
        )

    def _optimize_cost(self):
        QMessageBox.information(self, "Optimize Cost",
            "Suggested: 3D Printing with PLA for lowest material cost.")

    def _optimize_time(self):
        QMessageBox.information(self, "Optimize Time",
            "Suggested: Injection Molding for highest throughput.")


# ── Chat Panel ─────────────────────────────────────────────────────────────────

class ChatBubble(QFrame):
    def __init__(self, role: str, content: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        label = QLabel(content)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        t = _current_theme
        if role == "user":
            self.setStyleSheet(
                f"background-color: {t['user_bg']}; border: 1px solid {t['user_bd']}; "
                "border-radius: 8px; margin-left: 40px;"
            )
            label.setAlignment(Qt.AlignRight)
        elif role == "assistant":
            self.setStyleSheet(
                f"background-color: {t['panel']}; border: 1px solid {t['border']}; "
                "border-radius: 8px; margin-right: 40px;"
            )
            label.setAlignment(Qt.AlignLeft)
        else:
            self.setStyleSheet(
                f"background-color: {t['panel']}; border: 1px solid {t['border']}; "
                "border-radius: 6px; font-size: 11px;"
            )
            label.setStyleSheet(f"color: {t['dim']}; font-size: 11px;")
            label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)


class ChatPanel(QWidget):
    message_submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.history: List[Dict[str, str]] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        title = QLabel("AI Chat")
        title.setObjectName("section_title")
        layout.addWidget(title)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(6, 6, 6, 6)
        self.messages_layout.setSpacing(6)
        self.messages_layout.addStretch()
        self.scroll_area.setWidget(self.messages_container)
        layout.addWidget(self.scroll_area)

        input_row = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Describe the CAD model you want...")
        self.input_box.returnPressed.connect(self._submit)
        input_row.addWidget(self.input_box)

        send_btn = QPushButton("Send")
        send_btn.setFixedWidth(60)
        send_btn.clicked.connect(self._submit)
        input_row.addWidget(send_btn)
        layout.addLayout(input_row)

    def _submit(self):
        text = self.input_box.text().strip()
        if text:
            self.input_box.clear()
            self.message_submitted.emit(text)

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        bubble = ChatBubble(role, content)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        vsb = self.scroll_area.verticalScrollBar()
        vsb.setValue(vsb.maximum())

    def clear(self):
        self.history.clear()
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


# ── Overlay Feature Tree ───────────────────────────────────────────────────────

class OverlayFeatureTree(QFrame):
    """
    Semi-transparent feature tree overlay pinned inside the 3D viewport.
    Parented to the viewer container so it floats above the PyVista canvas.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("overlay_tree")
        self.setFixedWidth(210)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet(
            "QFrame#overlay_tree {"
            "  background-color: rgba(13, 17, 23, 185);"
            "  border: 1px solid rgba(48, 54, 61, 200);"
            "  border-radius: 6px;"
            "}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        header_row = QHBoxLayout()
        title = QLabel("⊞  Feature Tree")
        title.setStyleSheet(
            f"color: {_current_theme['accent']}; font-size: 11px; "
            "font-weight: bold; background: transparent; border: none;"
        )
        header_row.addWidget(title)
        header_row.addStretch()
        layout.addLayout(header_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(
            f"background-color: {_current_theme['border']}; "
            "border: none; max-height: 1px;"
        )
        layout.addWidget(sep)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet(
            "QTreeWidget {"
            "  background-color: transparent;"
            "  border: none;"
            "  color: #c9d1d9;"
            "  font-size: 11px;"
            "}"
            "QTreeWidget::item { padding: 1px 2px; }"
            "QTreeWidget::item:hover { background-color: rgba(63,185,80,40); }"
            "QTreeWidget::item:selected { background-color: rgba(63,185,80,80); }"
        )
        layout.addWidget(self.tree)

    _OP_ICONS: Dict[str, str] = {
        "box": "▬", "sphere": "●", "cylinder": "⬤", "extrude": "⬆",
        "fillet": "◉", "chamfer": "◈", "cut": "✂", "union": "⊕",
        "revolve": "↻", "shell": "◻", "hole": "◎", "workplane": "⊞",
    }

    def update_tree(self, code: str):
        """Rebuild the overlay tree from CADQuery code."""
        self.tree.clear()
        root = QTreeWidgetItem(self.tree, ["📦  Model"])
        root.setForeground(0, QColor(_current_theme["accent"]))
        for op in parse_feature_tree(code):
            icon = self._OP_ICONS.get(op.lower(), "◆")
            child = QTreeWidgetItem(root, [f"{icon}  {op}"])
            child.setForeground(0, QColor(_current_theme["text"]))
        self.tree.expandAll()
        # Resize height to fit content
        row_h = self.tree.sizeHintForRow(0) or 18
        item_count = self.tree.topLevelItem(0).childCount() + 1 if self.tree.topLevelItemCount() else 1
        self.tree.setFixedHeight(min(item_count * row_h + 8, 300))
        self.adjustSize()

    def clear_tree(self):
        self.tree.clear()
        self.adjustSize()


# ── Workspace Viewer ───────────────────────────────────────────────────────────

class WorkspaceViewer(QWidget):
    """3D viewer with a floating overlay feature tree in the top-left corner."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Container for both plotter and overlay
        self.viewer_container = QWidget(self)
        vc_lyt = QVBoxLayout(self.viewer_container)
        vc_lyt.setContentsMargins(0, 0, 0, 0)

        if HAS_PYVISTA:
            self.plotter = QtInteractor(self.viewer_container)
            self.plotter.set_background(_current_theme["bg"])
            self.plotter.add_axes(
                interactive=True,
                color=_current_theme["accent"],
                xlabel="X", ylabel="Y", zlabel="Z"
            )
            vc_lyt.addWidget(self.plotter)
        else:
            self.plotter = None
            ph = QLabel(
                "PyVista / pyvistaqt not installed.\n"
                "pip install pyvista pyvistaqt"
            )
            ph.setAlignment(Qt.AlignCenter)
            ph.setStyleSheet(f"color: {_current_theme['dim']};")
            vc_lyt.addWidget(ph)

        outer.addWidget(self.viewer_container)

        # Floating overlay tree — child of viewer_container
        self.overlay_tree = OverlayFeatureTree(self.viewer_container)
        self.overlay_tree.move(12, 12)
        self.overlay_tree.setVisible(True)
        self.overlay_tree.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay_tree.move(12, 12)
        self.overlay_tree.setMaximumHeight(
            max(60, self.viewer_container.height() - 24)
        )

    def toggle_overlay_tree(self) -> bool:
        """Toggle overlay visibility. Returns new visible state."""
        new_state = not self.overlay_tree.isVisible()
        self.overlay_tree.setVisible(new_state)
        return new_state

    def display_mesh(self, mesh: "pv.PolyData"):
        if self.plotter is None:
            return
        self.plotter.clear()
        self.plotter.add_mesh(
            mesh,
            color=_current_theme["accent"],
            show_edges=True,
            edge_color=_current_theme["border"],
            specular=0.5,
            smooth_shading=True
        )
        self.plotter.add_axes(color=_current_theme["accent"])
        self.plotter.set_background(_current_theme["bg"])
        self.plotter.reset_camera()
        self.overlay_tree.raise_()

    def update_feature_tree(self, code: str):
        self.overlay_tree.update_tree(code)
        self.overlay_tree.raise_()

    def reset_view(self):
        if self.plotter is not None:
            self.plotter.reset_camera()

    def clear_view(self):
        if self.plotter is not None:
            self.plotter.clear()
        self.overlay_tree.clear_tree()

    def closeEvent(self, event):
        if self.plotter is not None:
            self.plotter.close()
        super().closeEvent(event)


# ── Toolbar Panel ──────────────────────────────────────────────────────────────

class ToolbarPanel(QWidget):
    """Left-side vertical panel: library, workflow, analysis tools, view controls."""

    model_selected = pyqtSignal(str, str)
    version_selected = pyqtSignal(dict)
    open_simulation = pyqtSignal()
    open_manufacturing = pyqtSignal()
    toggle_feature_tree = pyqtSignal()

    def __init__(self, workflow_manager: WorkflowManager, parent=None):
        super().__init__(parent)
        self.workflow_manager = workflow_manager
        self.setFixedWidth(200)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.West)

        # Library tab
        lib_w = QWidget()
        ll = QVBoxLayout(lib_w)
        ll.setContentsMargins(4, 4, 4, 4)
        t1 = QLabel("Components")
        t1.setObjectName("section_title")
        ll.addWidget(t1)
        self.lib_list = QListWidget()
        for name in COMPONENT_TEMPLATES:
            self.lib_list.addItem(name)
        self.lib_list.itemDoubleClicked.connect(self._on_component_selected)
        ll.addWidget(self.lib_list)
        load_btn = QPushButton("Load Selected")
        load_btn.clicked.connect(self._on_component_selected_btn)
        ll.addWidget(load_btn)
        tabs.addTab(lib_w, "📦")

        # Workflow tab
        wf_w = QWidget()
        wl = QVBoxLayout(wf_w)
        wl.setContentsMargins(4, 4, 4, 4)
        t2 = QLabel("Workflow")
        t2.setObjectName("section_title")
        wl.addWidget(t2)
        self.wf_list = QListWidget()
        self.wf_list.itemDoubleClicked.connect(self._on_version_selected)
        wl.addWidget(self.wf_list)
        tabs.addTab(wf_w, "🕘")

        # Tools tab
        tools_w = QWidget()
        tl = QVBoxLayout(tools_w)
        tl.setContentsMargins(4, 4, 4, 4)
        tl.setSpacing(8)

        t3 = QLabel("Analysis Tools")
        t3.setObjectName("section_title")
        tl.addWidget(t3)

        sim_btn = QPushButton("⚡  Simulation")
        sim_btn.clicked.connect(self.open_simulation.emit)
        tl.addWidget(sim_btn)

        mfg_btn = QPushButton("🏭  Manufacturing")
        mfg_btn.clicked.connect(self.open_manufacturing.emit)
        tl.addWidget(mfg_btn)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("separator")
        tl.addWidget(sep)

        t4 = QLabel("View Controls")
        t4.setObjectName("section_title")
        tl.addWidget(t4)

        self.tree_toggle_btn = QPushButton("🌲  Hide Feature Tree")
        self.tree_toggle_btn.clicked.connect(self.toggle_feature_tree.emit)
        tl.addWidget(self.tree_toggle_btn)

        tl.addStretch()
        tabs.addTab(tools_w, "🔧")

        layout.addWidget(tabs)

    def update_tree_toggle_label(self, visible: bool):
        self.tree_toggle_btn.setText(
            "🌲  Hide Feature Tree" if visible else "🌲  Show Feature Tree"
        )

    def refresh_workflow(self):
        self.wf_list.clear()
        for v in self.workflow_manager.versions:
            label = f"v{v['id']} — {v['description']} — {v['timestamp']}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, v)
            self.wf_list.addItem(item)
        self.wf_list.scrollToBottom()

    def _on_component_selected(self, item: QListWidgetItem = None):
        if item is None:
            item = self.lib_list.currentItem()
        if item:
            name = item.text()
            code = COMPONENT_TEMPLATES.get(name, "")
            if code:
                self.model_selected.emit(name, code)

    def _on_component_selected_btn(self):
        item = self.lib_list.currentItem()
        if item:
            self._on_component_selected(item)

    def _on_version_selected(self, item: QListWidgetItem):
        data = item.data(Qt.UserRole)
        if data:
            self.version_selected.emit(data)


# ── Main Window ────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    """Primary application window coordinating all sub-components."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1400, 800)

        self.gemini = GeminiClient()
        self.cad_manager = CADModelManager()
        self.workflow_manager = WorkflowManager()
        self._api_worker: Optional[APIWorker] = None
        self._app_settings: Dict[str, Any] = self._load_settings()

        self._build_navbar()
        self._build_central()
        self._build_statusbar()
        self._setup_connections()
        self._apply_settings(self._app_settings)

        self.chat_panel.add_message(
            "system",
            "CA AssistantD ready. Enter your Gemini API key in the navbar."
        )
        self._update_status()
        self._autosave()

    # ── Settings ──────────────────────────────────────────────────────────────

    def _load_settings(self) -> Dict:
        defaults = {
            "api_key": "", "model_url": GEMINI_API_URL,
            "theme": "Dark Hacker", "toolbar_width": 200, "chat_width": 340,
            "visibility": {
                "toolbar": True, "chat": True,
                "statusbar": True, "feature_overlay": True,
            }
        }
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    defaults.update(json.load(f))
            except (json.JSONDecodeError, OSError):
                pass
        return defaults

    def _save_settings(self, settings: Dict):
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
        except OSError:
            pass

    def _apply_settings(self, settings: Dict):
        global _current_theme, _current_theme_name
        theme_name = settings.get("theme", "Dark Hacker")
        if theme_name in THEMES:
            _current_theme_name = theme_name
            _current_theme = THEMES[theme_name]
            QApplication.instance().setStyleSheet(current_stylesheet())

        key = settings.get("api_key", "")
        if key:
            self.api_key_input.setText(key)
            self.gemini.set_api_key(key)
            self.gemini.model_url = settings.get("model_url", GEMINI_API_URL)
            self._set_api_indicator(True)

        self.toolbar_panel.setFixedWidth(settings.get("toolbar_width", 200))
        self.chat_panel.setFixedWidth(settings.get("chat_width", 340))

        vis = settings.get("visibility", {})
        self.toolbar_panel.setVisible(vis.get("toolbar", True))
        self.chat_panel.setVisible(vis.get("chat", True))
        self.statusBar().setVisible(vis.get("statusbar", True))

        overlay_vis = vis.get("feature_overlay", True)
        if hasattr(self, "workspace"):
            self.workspace.overlay_tree.setVisible(overlay_vis)
            self.toolbar_panel.update_tree_toggle_label(overlay_vis)

        self._app_settings = settings
        if hasattr(self, "status_api"):
            self._update_status()

    # ── UI Construction ────────────────────────────────────────────────────────

    def _build_navbar(self):
        """
        Single unified QToolBar acting as the full navbar:
        Logo | File▾ | Edit actions | ──spacer── | API Key | Activate | ● | ⚙ Settings
        """
        self.navbar = QToolBar("Navigation")
        self.navbar.setMovable(False)
        self.navbar.setFloatable(False)
        self.navbar.setIconSize(QSize(16, 16))
        self.addToolBar(Qt.TopToolBarArea, self.navbar)

        # Logo
        logo_lbl = QLabel("  ⬡  HammerAI  ")
        logo_lbl.setStyleSheet(
            f"color: {_current_theme['accent']}; font-weight: bold; "
            "font-size: 14px; letter-spacing: 1px;"
        )
        self.navbar.addWidget(logo_lbl)

        vsep1 = QFrame()
        vsep1.setFrameShape(QFrame.VLine)
        vsep1.setStyleSheet(f"color: {_current_theme['border']};")
        self.navbar.addWidget(vsep1)

        # File dropdown
        file_btn = QToolButton()
        file_btn.setText("File ▾")
        file_btn.setPopupMode(QToolButton.InstantPopup)
        file_menu = QMenu(file_btn)
        for label, shortcut, slot in [
            ("⊕  New Project",  "Ctrl+N", self._new_project),
            ("💾  Save Model",  "Ctrl+S", self._save_model),
            ("📂  Load Model",  "Ctrl+O", self._load_model),
        ]:
            act = QAction(label, self)
            act.setShortcut(shortcut)
            act.triggered.connect(slot)
            file_menu.addAction(act)
        file_menu.addSeparator()
        exit_act = QAction("✕  Exit", self)
        exit_act.setShortcut("Ctrl+Q")
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)
        file_btn.setMenu(file_menu)
        self.navbar.addWidget(file_btn)

        vsep2 = QFrame()
        vsep2.setFrameShape(QFrame.VLine)
        vsep2.setStyleSheet(f"color: {_current_theme['border']};")
        self.navbar.addWidget(vsep2)

        # Edit actions
        for label, shortcut, slot in [
            ("↩ Undo",          "Ctrl+Z", self._undo),
            ("↪ Redo",          "Ctrl+Y", self._redo),
        ]:
            act = QAction(label, self)
            act.setShortcut(shortcut)
            act.triggered.connect(slot)
            self.navbar.addAction(act)

        self.navbar.addSeparator()

        for label, slot in [
            ("📎 Upload Sketch", self._upload_sketch),
            ("🗑 Clear Chat",    self._clear_chat),
            ("⟳ Restart",       self._restart),
        ]:
            act = QAction(label, self)
            act.triggered.connect(slot)
            self.navbar.addAction(act)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.navbar.addWidget(spacer)

        # API key section
        api_lbl = QLabel("API Key:")
        api_lbl.setStyleSheet(f"color: {_current_theme['dim']}; font-size: 11px;")
        self.navbar.addWidget(api_lbl)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("AIza...")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setFixedWidth(190)
        self.api_key_input.setFixedHeight(26)
        self.api_key_input.returnPressed.connect(self._activate_api)
        self.navbar.addWidget(self.api_key_input)

        activate_btn = QPushButton("Activate")
        activate_btn.setFixedWidth(70)
        activate_btn.setFixedHeight(26)
        activate_btn.clicked.connect(self._activate_api)
        self.navbar.addWidget(activate_btn)

        self.api_status_label = QLabel("●  OFF")
        self.api_status_label.setStyleSheet(
            f"color: {_current_theme['danger']}; font-size: 12px; font-weight: bold;"
        )
        self.navbar.addWidget(self.api_status_label)

        vsep3 = QFrame()
        vsep3.setFrameShape(QFrame.VLine)
        vsep3.setStyleSheet(f"color: {_current_theme['border']};")
        self.navbar.addWidget(vsep3)

        # Settings button
        settings_btn = QPushButton("⚙  Settings")
        settings_btn.setFixedHeight(26)
        settings_btn.clicked.connect(self._open_settings)
        self.navbar.addWidget(settings_btn)

        pad = QWidget()
        pad.setFixedWidth(8)
        self.navbar.addWidget(pad)

    def _build_central(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        self.toolbar_panel = ToolbarPanel(self.workflow_manager)
        main_layout.addWidget(self.toolbar_panel)

        self.workspace = WorkspaceViewer()
        main_layout.addWidget(self.workspace, stretch=3)

        self.chat_panel = ChatPanel()
        self.chat_panel.setFixedWidth(340)
        main_layout.addWidget(self.chat_panel)

    def _build_statusbar(self):
        self.status_api = QLabel("API: OFF")
        self.status_model = QLabel("MODEL: NONE")
        self.status_verts = QLabel("VERTICES: 0")
        sb = self.statusBar()
        sb.addPermanentWidget(QLabel("  "))
        sb.addPermanentWidget(self.status_api)
        sb.addPermanentWidget(QLabel("  |  "))
        sb.addPermanentWidget(self.status_model)
        sb.addPermanentWidget(QLabel("  |  "))
        sb.addPermanentWidget(self.status_verts)

    def _setup_connections(self):
        self.chat_panel.message_submitted.connect(self._on_chat_message)
        self.toolbar_panel.model_selected.connect(self._on_component_load)
        self.toolbar_panel.version_selected.connect(self._on_version_restore)
        self.toolbar_panel.open_simulation.connect(self._open_simulation)
        self.toolbar_panel.open_manufacturing.connect(self._open_manufacturing)
        self.toolbar_panel.toggle_feature_tree.connect(self._toggle_feature_tree)

    # ── Feature tree toggle ────────────────────────────────────────────────────

    def _toggle_feature_tree(self):
        visible = self.workspace.toggle_overlay_tree()
        self.toolbar_panel.update_tree_toggle_label(visible)

    # ── Settings ──────────────────────────────────────────────────────────────

    def _open_settings(self):
        dlg = SettingsWindow(self._app_settings, self)
        dlg.settings_applied.connect(self._apply_settings)
        dlg.settings_applied.connect(self._save_settings)
        dlg.exec_()

    # ── Signal Handlers ────────────────────────────────────────────────────────

    def _on_chat_message(self, text: str):
        self.chat_panel.add_message("user", text)
        cmd = text.lower().strip()
        if cmd == "reset view":
            self.workspace.reset_view()
            self.chat_panel.add_message("system", "View reset.")
            return
        if cmd == "clear model":
            self._clear_model()
            self.chat_panel.add_message("system", "Model cleared.")
            return
        for comp_name in COMPONENT_TEMPLATES:
            if f"load {comp_name.lower()}" == cmd:
                code = COMPONENT_TEMPLATES[comp_name]
                self._execute_and_display(code, f"Loaded {comp_name}")
                self.chat_panel.add_message("system", f"Loaded: {comp_name}")
                return
        if not self.gemini.active:
            self.chat_panel.add_message(
                "system",
                "API key not active. Enter it in the navbar and click Activate."
            )
            return
        self._send_to_gemini(text)

    def _send_to_gemini(self, prompt: str):
        if self._api_worker and self._api_worker.isRunning():
            self.chat_panel.add_message("system", "Still processing...")
            return
        self.chat_panel.add_message("system", "Generating CAD model...")
        self._api_worker = APIWorker(self.gemini, prompt, self.chat_panel.history)
        self._api_worker.response_ready.connect(self._on_api_response)
        self._api_worker.error_occurred.connect(self._on_api_error)
        self._api_worker.start()

    def _on_api_response(self, code: str):
        self.chat_panel.add_message("assistant", f"```python\n{code}\n```")
        try:
            self._execute_and_display(code, "AI generated model")
        except Exception:
            self.chat_panel.add_message(
                "system", f"Execution error:\n{traceback.format_exc()}"
            )

    def _on_api_error(self, error: str):
        self.chat_panel.add_message("system", f"API error: {error}")

    def _on_component_load(self, name: str, code: str):
        self._execute_and_display(code, f"Loaded {name}")
        self.chat_panel.add_message("system", f"Loaded component: {name}")

    def _on_version_restore(self, version: Dict):
        code = version.get("cad_code", "")
        if code:
            try:
                mesh = self.cad_manager.load_code(code)
                self.workspace.display_mesh(mesh)
                self.workspace.update_feature_tree(code)
                self._update_status()
                self.chat_panel.add_message("system", f"Restored: {version['description']}")
            except Exception as exc:
                self.chat_panel.add_message("system", f"Restore failed: {exc}")

    def _execute_and_display(self, code: str, description: str = ""):
        mesh = self.cad_manager.load_code(code)
        self.workspace.display_mesh(mesh)
        self.workspace.update_feature_tree(code)
        self.workflow_manager.add_version(code, description)
        self.toolbar_panel.refresh_workflow()
        self._update_status()
        self._autosave()

    def _set_api_indicator(self, active: bool):
        if active:
            self.api_status_label.setText("●  ON")
            self.api_status_label.setStyleSheet(
                f"color: {_current_theme['accent']}; font-size: 12px; font-weight: bold;"
            )
        else:
            self.api_status_label.setText("●  OFF")
            self.api_status_label.setStyleSheet(
                f"color: {_current_theme['danger']}; font-size: 12px; font-weight: bold;"
            )

    def _activate_api(self):
        key = self.api_key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "API Key", "Please enter a valid API key.")
            return
        if self.gemini.set_api_key(key):
            self._set_api_indicator(True)
            self.chat_panel.add_message("system", "Gemini API activated.")
            self._update_status()
            self._app_settings["api_key"] = key
            self._save_settings(self._app_settings)
        else:
            QMessageBox.warning(self, "API Key", "Invalid API key format.")

    def _undo(self):
        version = self.workflow_manager.undo()
        if version:
            self._on_version_restore(version)
        else:
            self.statusBar().showMessage("Nothing to undo.", 2000)

    def _redo(self):
        version = self.workflow_manager.redo()
        if version:
            self._on_version_restore(version)
        else:
            self.statusBar().showMessage("Nothing to redo.", 2000)

    def _upload_sketch(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Upload Sketch", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.svg);;All Files (*)"
        )
        if path:
            self.chat_panel.add_message(
                "system",
                f"Sketch uploaded: {os.path.basename(path)}\n"
                "(Sketch-to-CAD placeholder)"
            )

    def _clear_chat(self):
        self.chat_panel.clear()
        self.chat_panel.add_message("system", "Chat cleared.")

    def _clear_model(self):
        self.workspace.clear_view()
        self._update_status()

    def _restart(self):
        reply = QMessageBox.question(
            self, "Restart",
            "Clear all chat, model, and workflow history?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._clear_chat()
            self._clear_model()
            self.workflow_manager.reset()
            self.toolbar_panel.refresh_workflow()
            self.cad_manager.current_solid = None
            self.cad_manager.current_mesh = None
            self.cad_manager.current_code = ""
            self._update_status()
            self.chat_panel.add_message("system", "Session restarted.")

    def _new_project(self):
        self._restart()

    def _save_model(self):
        if not self.cad_manager.current_code:
            QMessageBox.information(self, "Save", "No model to save.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Model", "model.py", "Python Files (*.py);;All Files (*)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.cad_manager.current_code)
            self.statusBar().showMessage(f"Saved: {path}", 3000)

    def _load_model(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Model", "", "Python Files (*.py);;All Files (*)"
        )
        if path:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
            try:
                self._execute_and_display(code, f"Loaded: {os.path.basename(path)}")
                self.chat_panel.add_message(
                    "system", f"Loaded from {os.path.basename(path)}"
                )
            except Exception:
                self.chat_panel.add_message(
                    "system", f"Error:\n{traceback.format_exc()}"
                )

    def _open_simulation(self):
        SimulationWindow(self.cad_manager, self).exec_()

    def _open_manufacturing(self):
        ManufacturingWindow(self.cad_manager, self).exec_()

    def _update_status(self):
        active = self.gemini.active
        self.status_api.setText("API: ON" if active else "API: OFF")
        self.status_api.setStyleSheet(
            f"color: {_current_theme['accent'] if active else _current_theme['danger']};"
            " font-size: 11px;"
        )
        has_model = self.cad_manager.current_mesh is not None
        self.status_model.setText("MODEL: READY" if has_model else "MODEL: NONE")
        self.status_verts.setText(
            f"VERTICES: {self.cad_manager.get_vertex_count():,}"
        )

    def _autosave(self):
        session = {
            "timestamp": datetime.datetime.now().isoformat(),
            "api_active": self.gemini.active,
            "current_code": self.cad_manager.current_code,
            "workflow": self.workflow_manager.to_serializable()
        }
        try:
            with open(AUTOSAVE_PATH, "w", encoding="utf-8") as f:
                json.dump(session, f, indent=2)
        except OSError:
            pass

    def closeEvent(self, event):
        if hasattr(self.workspace, "plotter") and self.workspace.plotter:
            self.workspace.plotter.close()
        super().closeEvent(event)


# ── Entry Point ────────────────────────────────────────────────────────────────

def main():
    """Launch CAD Assistant with SolidWorks-style animated splash screen."""
    if not HAS_PYQT5:
        print("Cannot start: PyQt5 is required.")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setStyleSheet(current_stylesheet())

    try:
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        pass

    # Splash screen
    splash = SplashScreen()
    splash.show()
    app.processEvents()

    # MainWindow is created after splash finishes so PyVista
    # initializes inside the event loop safely.
    _wins: List = []

    def _launch():
        win = MainWindow()
        _wins.append(win)
        win.show()
        splash.close()

    splash.finished.connect(_launch)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()