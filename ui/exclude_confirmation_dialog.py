# ----- Built-In Modules-----
from pathlib import Path

# ----- PyQt6 Modules -----
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

# ----- Config Imports -----
from core.config import (
    COLOR_ORANGE,
    COLOR_RED,
    FONT_FAMILY,
    FONT_SIZE_HEADER,
    FONT_SIZE_LABEL,
    FONT_SIZE_STAT,
    THEME_BG_PRIMARY,
    THEME_TEXT_PRIMARY,
    THEME_TEXT_SECONDARY,
    get_default_paths,
)

# ----- Settings Import -----
from core.settings_manager import SettingsManager

# ----- Utils Imports -----
from utils.center import position_center
from utils.icons import Icons


class ExcludeConfirmationDialog(QDialog):
    """Confirmation dialog for excluded repositories with countdown timer.

    Shows when an excluded repository has uncommitted changes.
    Auto-skips after timeout if no user response.
    """

    def __init__(self, repo_name: str, parent=None) -> None:
        """Initialize the exclude confirmation dialog.

        Args:
            repo_name: Name of the excluded repository
            parent: Parent widget
        """
        super().__init__(parent)
        self.repo_name: str = repo_name
        self.user_choice = None  # 'push', 'skip', or 'cancel_all'

        # Get timeout from settings
        settings = SettingsManager().get_settings()
        self.timeout_seconds = settings.get("git_operations", {}).get(
            "exclude_confirmation_timeout", 5
        )
        self.time_left = self.timeout_seconds

        self._init_ui()
        self._start_countdown()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("Excluded Repository Detected")
        self.setFixedSize(500, 300)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setModal(True)

        # Set window icon
        paths: dict[str, Path] = get_default_paths()
        self.setWindowIcon(QIcon(str(paths["app_icon"])))

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 20, 24, 20)

        # Background styling
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {THEME_BG_PRIMARY};
            }}
            """
        )

        # Header with warning icon
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        warning_icon = QLabel(Icons.WARNING)
        warning_icon.setFont(QFont(FONT_FAMILY, FONT_SIZE_HEADER + 4))
        warning_icon.setStyleSheet(f"color: {COLOR_ORANGE}; padding: 0;")
        header_layout.addWidget(warning_icon)

        header_label = QLabel("Excluded Repository Detected")
        header_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_HEADER, QFont.Weight.Bold))
        header_label.setStyleSheet(f"color: {THEME_TEXT_PRIMARY}; padding: 0;")
        header_layout.addWidget(header_label, 1)

        main_layout.addLayout(header_layout)

        # Repository name
        repo_label = QLabel(f"Repository: {self.repo_name}")
        repo_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_LABEL))
        repo_label.setStyleSheet(
            f"color: {THEME_TEXT_PRIMARY}; padding: 8px 0; font-weight: bold;"
        )
        main_layout.addWidget(repo_label)

        # Message
        message = QLabel(
            "This repository is excluded on this machine\n"
            "but has uncommitted changes."
        )
        message.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        message.setStyleSheet(f"color: {THEME_TEXT_SECONDARY}; padding: 0;")
        message.setWordWrap(True)
        main_layout.addWidget(message)

        # Countdown label
        self.countdown_label = QLabel(f"Auto-skipping in {self.time_left} seconds...")
        self.countdown_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        self.countdown_label.setStyleSheet(
            f"color: {COLOR_ORANGE}; padding: 8px 0; font-style: italic;"
        )
        main_layout.addWidget(self.countdown_label)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        # Push Anyway button
        push_btn = QPushButton(f"{Icons.GIT_PUSH}  Push Anyway")
        push_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        push_btn.setFixedHeight(36)
        push_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(158, 206, 106, 0.1);
                color: #9ece6a;
                border: 1px solid rgba(158, 206, 106, 0.3);
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(158, 206, 106, 0.2);
                border: 1px solid #9ece6a;
            }}
            QPushButton:pressed {{
                background-color: rgba(158, 206, 106, 0.3);
            }}
            """
        )
        push_btn.clicked.connect(lambda: self._on_choice("push"))
        buttons_layout.addWidget(push_btn)

        # Skip This Repo button
        skip_btn = QPushButton(f"{Icons.SKIP}  Skip This Repo")
        skip_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        skip_btn.setFixedHeight(36)
        skip_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(255, 158, 100, 0.1);
                color: {COLOR_ORANGE};
                border: 1px solid rgba(255, 158, 100, 0.3);
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 158, 100, 0.2);
                border: 1px solid {COLOR_ORANGE};
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 158, 100, 0.3);
            }}
            """
        )
        skip_btn.clicked.connect(lambda: self._on_choice("skip"))
        buttons_layout.addWidget(skip_btn)

        # Cancel All button
        cancel_btn = QPushButton(f"{Icons.CANCEL}  Cancel All")
        cancel_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        cancel_btn.setFixedHeight(36)
        cancel_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(247, 118, 142, 0.1);
                color: {COLOR_RED};
                border: 1px solid rgba(247, 118, 142, 0.3);
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(247, 118, 142, 0.2);
                border: 1px solid {COLOR_RED};
            }}
            QPushButton:pressed {{
                background-color: rgba(247, 118, 142, 0.3);
            }}
            """
        )
        cancel_btn.clicked.connect(lambda: self._on_choice("cancel_all"))
        buttons_layout.addWidget(cancel_btn)

        main_layout.addLayout(buttons_layout)

        # Center dialog on screen
        position_center(self)

    def _start_countdown(self) -> None:
        """Start the countdown timer."""
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_countdown)
        self.timer.start(1000)  # Update every second

        # Auto-select "skip" after timeout
        QTimer.singleShot(self.timeout_seconds * 1000, self._auto_skip)

    def _update_countdown(self) -> None:
        """Update countdown label every second."""
        self.time_left -= 1
        if self.time_left >= 0:
            self.countdown_label.setText(
                f"Auto-skipping in {self.time_left} seconds..."
            )

    def _auto_skip(self) -> None:
        """Auto-select 'skip' if no user choice made."""
        if self.user_choice is None:
            self._on_choice("skip")

    def _on_choice(self, choice: str) -> None:
        """Handle user choice.

        Args:
            choice: User's choice ('push', 'skip', or 'cancel_all')
        """
        if self.user_choice is not None:
            return  # Already made a choice

        self.user_choice: str = choice
        self.timer.stop()

        # Update countdown label to show selection
        choice_labels: dict[str, str] = {
            "push": "Pushing repository...",
            "skip": "Skipping repository...",
            "cancel_all": "Cancelling all operations...",
        }
        self.countdown_label.setText(choice_labels.get(choice, "Processing..."))
        self.countdown_label.setStyleSheet(f"color: #9ece6a; padding: 8px 0;")

        # Close dialog
        self.accept()

    def get_choice(self) -> str:
        """Get the user's choice.

        Returns:
            str: 'push', 'skip', or 'cancel_all'
        """
        return self.user_choice if self.user_choice else "skip"
