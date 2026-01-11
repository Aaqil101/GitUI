# ----- Built-In Modules-----
from pathlib import Path

# ----- PyQt6 Modules -----
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QFont, QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

# ----- Config Imports -----
from core.config import (
    COLOR_DARK_BLUE,
    COLOR_ORANGE,
    FONT_FAMILY,
    FONT_SIZE_LABEL,
    FONT_SIZE_STAT,
    THEME_BG_PRIMARY,
    THEME_BG_SECONDARY,
    THEME_TEXT_PRIMARY,
    THEME_TEXT_SECONDARY,
    get_default_paths,
)

# ----- UI Component Imports -----
from ui.settings_components import HoverIconButton

# ----- Utils Imports -----
from utils.center import position_center
from utils.icons import Icons


class AddExclusionDialog(QDialog):
    """Custom dialog for adding excluded repositories.

    Features:
    - Tokyo Night themed styling matching main application
    - Text input for repository names (comma-separated support)
    - Add/Cancel buttons with hover effects
    - Centered positioning
    """

    def __init__(self, parent=None) -> None:
        """Initialize the add exclusion dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("Add Excluded Repository")
        self.setFixedSize(500, 250)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setModal(True)

        # Set window icon
        paths: dict[str, Path] = get_default_paths()
        self.setWindowIcon(QIcon(str(paths["app_icon"])))

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # Background styling
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {THEME_BG_PRIMARY};
            }}
            """
        )

        # Header section
        header = self._create_header()
        main_layout.addWidget(header)

        # Input section
        input_section = self._create_input_section()
        main_layout.addWidget(input_section)

        main_layout.addStretch()

        # Button bar
        button_bar = self._create_button_bar()
        main_layout.addWidget(button_bar)

        # Center dialog on screen
        position_center(self)

    def _create_header(self) -> QWidget:
        """Create the header section with icon and title.

        Returns:
            QWidget: Header widget
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel(Icons.EXCLUDE)
        icon_label.setFont(QFont(FONT_FAMILY, 18))
        icon_label.setStyleSheet(f"color: {COLOR_ORANGE};")
        layout.addWidget(icon_label)

        # Title
        title_label = QLabel("Add Excluded Repository")
        title_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_LABEL + 2, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {THEME_TEXT_PRIMARY};")
        layout.addWidget(title_label)

        layout.addStretch()

        return widget

    def _create_input_section(self) -> QWidget:
        """Create the input section with instructions and text field.

        Returns:
            QWidget: Input section widget
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Instruction label
        instruction_label = QLabel(
            "Enter repository name(s) - separate multiple with commas:"
        )
        instruction_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        instruction_label.setStyleSheet(f"color: {THEME_TEXT_SECONDARY};")
        layout.addWidget(instruction_label)

        # Note label
        note_label = QLabel("(not full paths)")
        note_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT - 1))
        note_label.setStyleSheet(
            f"color: {THEME_TEXT_SECONDARY}; font-style: italic; padding-left: 4px;"
        )
        layout.addWidget(note_label)

        # Text input
        self.text_input = QLineEdit()
        self.text_input.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        self.text_input.setPlaceholderText("e.g., MyRepo1, MyRepo2, MyRepo3")
        self.text_input.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {THEME_BG_SECONDARY};
                color: {THEME_TEXT_PRIMARY};
                border-radius: 6px;
                padding: 10px 12px;
                border: 2px solid transparent;
            }}
            QLineEdit:focus {{
                background-color: rgba(255, 255, 255, 0.06);
                border: 2px solid {COLOR_DARK_BLUE};
            }}
            QLineEdit::placeholder {{
                color: {THEME_TEXT_SECONDARY};
                font-style: italic;
            }}
            """
        )
        layout.addWidget(self.text_input)

        return widget

    def _create_button_bar(self) -> QWidget:
        """Create the bottom button bar.

        Returns:
            QWidget: Button bar widget
        """
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        layout.addStretch()

        # Cancel button
        cancel_btn = HoverIconButton(
            normal_icon=Icons.CANCEL_OUTLINE,
            hover_icon=Icons.CANCEL,
            text="Cancel",
        )
        cancel_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        cancel_btn.setFixedHeight(36)
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.04);
                color: {THEME_TEXT_PRIMARY};
                border-radius: 6px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.08);
                border-bottom: 2px solid {COLOR_DARK_BLUE};
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.12);
            }}
            """
        )
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        # Add button
        add_btn = HoverIconButton(
            normal_icon=Icons.ADD,
            hover_icon=Icons.ADDED,
            pressed_icon=Icons.ADDED_FOLDER,
            text="Add",
        )
        add_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        add_btn.setFixedHeight(36)
        add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        add_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(158, 206, 106, 0.2);
                color: #9ece6a;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(158, 206, 106, 0.3);
                border-bottom: 2px solid #9ece6a;
            }}
            QPushButton:pressed {{
                background-color: rgba(158, 206, 106, 0.4);
            }}
            """
        )
        add_btn.clicked.connect(self.accept)
        layout.addWidget(add_btn)

        # Set Add as default button (Enter key)
        add_btn.setDefault(True)

        return bar

    def get_input_text(self) -> str:
        """Get the input text from the dialog.

        Returns:
            str: Input text from text field
        """
        return self.text_input.text().strip()
