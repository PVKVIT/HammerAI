"""
HammerAI — Entry Point
Run this file to launch the application.
"""

import sys
from typing import List

def main():
    """Launch HammerAI CAD Assistant with animated splash screen."""
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt, QTimer

    from config.constants import APP_NAME, APP_VERSION
    from ui.splash import SplashScreen
    from ui.theme import current_stylesheet

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setStyleSheet(current_stylesheet())

    try:
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        pass

    splash = SplashScreen()
    splash.show()
    app.processEvents()

    _wins: List = []

    def _launch():
        from ui.main_window import MainWindow
        win = MainWindow()
        _wins.append(win)
        win.show()
        splash.close()

    splash.finished.connect(_launch)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
