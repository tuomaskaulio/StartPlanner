"""Application entry point."""

from __future__ import annotations

import sys
from importlib import resources

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from startplanner.gui.main_window import MainWindow


def _app_icon() -> QIcon:
    icon_path = resources.files("startplanner") / "resources" / "icon.png"
    with resources.as_file(icon_path) as path:
        return QIcon(str(path))


def main() -> int:
    app = QApplication(sys.argv)
    app.setWindowIcon(_app_icon())
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
