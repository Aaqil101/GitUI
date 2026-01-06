# ----- PyQt6 Modules -----
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QApplication


def position_center(self) -> None:
    """Position window in center of screen."""
    screen_geometry: QRect = QApplication.primaryScreen().availableGeometry()
    x: int = screen_geometry.width() // 2 - self.width() // 2
    y: int = screen_geometry.height() // 2 - self.height() // 2
    self.move(x, y)


if __name__ == "__main__":
    print("This module is intended to be imported, not run directly.")
