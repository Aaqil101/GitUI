# ----- Built-In Modules-----
from pathlib import Path

# ----- PyQt6 Modules -----
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QFont, QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

# ----- Config Imports -----
from core.config import (
    COLOR_DARK_BLUE,
    COLOR_ORANGE,
    COLOR_RED,
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


class ResetConfirmationDialog(QDialog):
    """Custom dialog for confirming settings reset with options.

    Features:
    - Tokyo Night themed styling matching main application
    - Checkboxes to choose what to reset
    - Reset/Cancel buttons with hover effects
    - Centered positioning
    """

    def __init__(self, parent=None) -> None:
        """Initialize the reset confirmation dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.reset_custom_paths = False
        self.reset_exclusions = False
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("Reset to Defaults")
        self.setFixedSize(550, 380)
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

        # Warning message
        warning = self._create_warning()
        main_layout.addWidget(warning)

        # Options section
        options = self._create_options()
        main_layout.addWidget(options)

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
        icon_label = QLabel(Icons.WARNING)
        icon_label.setFont(QFont(FONT_FAMILY, 18))
        icon_label.setStyleSheet(f"color: {COLOR_ORANGE};")
        layout.addWidget(icon_label)

        # Title
        title_label = QLabel("Reset to Defaults")
        title_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_LABEL + 2, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {THEME_TEXT_PRIMARY};")
        layout.addWidget(title_label)

        layout.addStretch()

        return widget

    def _create_warning(self) -> QWidget:
        """Create the warning message section.

        Returns:
            QWidget: Warning widget
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Main message
        message = QLabel(
            "Are you sure you want to reset settings to their default values?\n"
            "This action cannot be undone."
        )
        message.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        message.setStyleSheet(f"color: {THEME_TEXT_PRIMARY};")
        message.setWordWrap(True)
        layout.addWidget(message)

        return widget

    def _create_options(self) -> QWidget:
        """Create the options section with checkboxes.

        Returns:
            QWidget: Options widget
        """
        widget = QWidget()
        widget.setObjectName("options_container")
        widget.setStyleSheet(
            f"""
            #options_container {{
                background-color: {THEME_BG_SECONDARY};
                border-radius: 8px;
                padding: 16px;
            }}
            """
        )
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Section title
        title = QLabel("What should be reset?")
        title.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {THEME_TEXT_PRIMARY};")
        layout.addWidget(title)

        # Settings checkbox (always checked, disabled)
        settings_checkbox = QCheckBox("Application settings")
        settings_checkbox.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        settings_checkbox.setChecked(True)
        settings_checkbox.setEnabled(False)
        settings_checkbox.setStyleSheet(
            f"""
            QCheckBox {{
                color: {THEME_TEXT_SECONDARY};
                spacing: 8px;
                padding: 4px;
                border-radius: 4px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 3px;
                background-color: rgba(158, 206, 106, 0.3);
                border: 1px solid #9ece6a;
            }}
            QCheckBox::indicator:checked {{
                image: url(assets/Check.png);
                background-color: #9ece6a;
                border: 1px solid #9ece6a;
            }}
            QCheckBox:disabled {{
                color: {THEME_TEXT_SECONDARY};
                opacity: 0.7;
            }}
            """
        )
        layout.addWidget(settings_checkbox)

        # Custom paths checkbox
        self.custom_paths_checkbox = QCheckBox("Custom repository paths")
        self.custom_paths_checkbox.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        self.custom_paths_checkbox.setStyleSheet(
            f"""
            QCheckBox {{
                color: {THEME_TEXT_SECONDARY};
                spacing: 8px;
                padding: 4px;
                border-radius: 4px;
            }}
            QCheckBox:hover {{
                background-color: rgba(255, 158, 100, 0.08);
                color: {THEME_TEXT_PRIMARY};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 3px;
                background-color: rgba(255, 255, 255, 0.04);
                border: 1px solid transparent;
            }}
            QCheckBox::indicator:checked {{
                image: url(assets/Check.png);
                background-color: {COLOR_ORANGE};
                border: 1px solid {COLOR_ORANGE};
            }}
            QCheckBox::indicator:hover {{
                border: 1px solid {COLOR_ORANGE};
            }}
            QCheckBox:focus {{
                background-color: rgba(255, 158, 100, 0.08);
                color: {THEME_TEXT_PRIMARY};
                outline: none;
            }}
            """
        )
        layout.addWidget(self.custom_paths_checkbox)

        # Exclusions checkbox
        self.exclusions_checkbox = QCheckBox("Repository exclusions")
        self.exclusions_checkbox.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        self.exclusions_checkbox.setStyleSheet(
            f"""
            QCheckBox {{
                color: {THEME_TEXT_SECONDARY};
                spacing: 8px;
                padding: 4px;
                border-radius: 4px;
            }}
            QCheckBox:hover {{
                background-color: rgba(255, 158, 100, 0.08);
                color: {THEME_TEXT_PRIMARY};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 3px;
                background-color: rgba(255, 255, 255, 0.04);
                border: 1px solid transparent;
            }}
            QCheckBox::indicator:checked {{
                image: url(assets/Check.png);
                background-color: {COLOR_ORANGE};
                border: 1px solid {COLOR_ORANGE};
            }}
            QCheckBox::indicator:hover {{
                border: 1px solid {COLOR_ORANGE};
            }}
            QCheckBox:focus {{
                background-color: rgba(255, 158, 100, 0.08);
                color: {THEME_TEXT_PRIMARY};
                outline: none;
            }}
            """
        )
        layout.addWidget(self.exclusions_checkbox)

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
            QPushButton:focus {{
                background-color: rgba(255, 255, 255, 0.08);
                border-bottom: 2px solid {COLOR_DARK_BLUE};
                outline: none;
            }}
            """
        )
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        # Reset button
        reset_btn = HoverIconButton(
            normal_icon=Icons.REFRESH,
            hover_icon=Icons.REFRESH,
            text="Reset",
        )
        reset_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        reset_btn.setFixedHeight(36)
        reset_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        reset_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(247, 118, 142, 0.2);
                color: {COLOR_RED};
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(247, 118, 142, 0.3);
                border-bottom: 2px solid {COLOR_RED};
            }}
            QPushButton:pressed {{
                background-color: rgba(247, 118, 142, 0.4);
            }}
            QPushButton:focus {{
                background-color: rgba(247, 118, 142, 0.3);
                border-bottom: 2px solid {COLOR_RED};
                outline: none;
            }}
            """
        )
        reset_btn.clicked.connect(self._on_reset_clicked)
        layout.addWidget(reset_btn)

        # Set Reset as default button (Enter key)
        reset_btn.setDefault(True)

        return bar

    def _on_reset_clicked(self) -> None:
        """Handle reset button click and store checkbox states."""
        self.reset_custom_paths = self.custom_paths_checkbox.isChecked()
        self.reset_exclusions = self.exclusions_checkbox.isChecked()
        self.accept()

    def get_reset_options(self) -> tuple[bool, bool]:
        """Get the reset options selected by user.

        Returns:
            tuple[bool, bool]: (reset_custom_paths, reset_exclusions)
        """
        return (self.reset_custom_paths, self.reset_exclusions)
