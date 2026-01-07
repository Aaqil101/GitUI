# ----- PyQt6 Modules -----
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QFont
from PyQt6.QtWidgets import QPushButton

# ----- Config Imports -----
from core.config import (
    COLOR_ORANGE,
    FONT_FAMILY,
    FONT_SIZE_LABEL,
    THEME_TEXT_PRIMARY,
)

# ----- Utils Imports -----
from utils.icons import Icons


def create_settings_button(parent=None) -> QPushButton:
    """Create a settings button with gear icon.

    Factory function that creates a styled settings button matching
    the Tokyo Night theme and glass morphism design.

    Args:
        parent: Parent widget (optional)

    Returns:
        QPushButton: Styled settings button
    """
    button = QPushButton(f"{Icons.SETTINGS}  Settings", parent)
    button.setFont(QFont(FONT_FAMILY, FONT_SIZE_LABEL))
    button.setFixedHeight(36)
    button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    button.setStyleSheet(
        f"""
        QPushButton {{
            background-color: rgba(255, 255, 255, 0.04);
            color: {THEME_TEXT_PRIMARY};
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            padding: 6px 12px;
            text-align: left;
            font-weight: normal;
        }}
        QPushButton:hover {{
            background-color: rgba(255, 255, 255, 0.08);
            border: 1px solid {COLOR_ORANGE};
            color: #f5e6d3;
        }}
        QPushButton:pressed {{
            background-color: rgba(255, 255, 255, 0.12);
            color: #ffd700;
        }}
        """
    )

    return button
