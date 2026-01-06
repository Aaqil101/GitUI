# ----- PyQt6 Modules -----
from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, QVariantAnimation
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

# ----- Utils Modules -----
from utils.color import Color
from utils.icons import Icons


class RepoCard(QFrame):
    """A card widget representing a single repository."""

    def __init__(
        self, repo_name: str, behind_count: int = 0, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.repo_name: str = repo_name
        self.behind_count: int = behind_count
        self._current_status = "PENDING"
        self._animations: list = []

        self._setup_ui()
        self._apply_shadow()

    def _setup_ui(self) -> None:
        """Setup the card layout and widgets."""
        self.setFixedHeight(70)
        self.setObjectName("RepoCard")
        self._apply_base_style(hovered=False)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Left: repo info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        info_layout.setContentsMargins(0, 0, 0, 0)

        # Repo name row
        name_row = QHBoxLayout()
        name_row.setSpacing(8)
        name_row.setContentsMargins(0, 0, 0, 0)

        icon = QLabel(Icons.GIT_BRANCH)
        icon.setFont(QFont("JetBrainsMono Nerd Font", 12))
        icon.setStyleSheet("color: #7aa2f7; background: transparent; padding: 0;")
        name_row.addWidget(icon)

        name = QLabel(self.repo_name)
        name.setFont(QFont("JetBrainsMono Nerd Font", 11, QFont.Weight.Bold))
        name.setStyleSheet("color: #c0caf5; background: transparent; padding: 0;")
        name_row.addWidget(name)
        name_row.addStretch()

        info_layout.addLayout(name_row)

        # Commits behind
        if self.behind_count > 0:
            commits = QLabel(
                f"{self.behind_count} commit{'s' if self.behind_count != 1 else ''} behind"
            )
            commits.setFont(QFont("JetBrainsMono Nerd Font", 9))
            commits.setStyleSheet(
                "color: #565f89; background: transparent; padding: 0;"
            )
            info_layout.addWidget(commits)
        else:
            info_layout.addStretch()

        layout.addLayout(info_layout, 1)

        # Right: status badge
        self.status_label = QLabel("PENDING")
        self.status_label.setFont(
            QFont("JetBrainsMono Nerd Font", 9, QFont.Weight.Bold)
        )
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFixedSize(85, 28)
        self._update_status_style("PENDING")
        layout.addWidget(self.status_label)

    def _apply_base_style(self, hovered: bool = False) -> None:
        bg = "#2f3347" if hovered else "#24283b"
        self.setStyleSheet(
            f"""
            QFrame#RepoCard {{
                background-color: {bg};
                border-radius: 10px;
                border: 2px solid #414868;
            }}
            """
        )

    def _apply_shadow(self) -> None:
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(12)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(2)
        self.shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(self.shadow)

    def _update_status_style(self, status: str) -> None:
        color: str = Color.get(status)

        # Convert hex to RGB for opacity control
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)

        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: rgba({r}, {g}, {b}, 0.2);
                color: {color};
                border-radius: 14px;
                padding: 0;
            }}
            """
        )
        self.status_label.setText(status)

    def set_status(self, status: str) -> None:
        if status == self._current_status:
            return

        old_color = QColor(Color.get(self._current_status))
        new_color = QColor(Color.get(status))

        anim = QVariantAnimation(self)
        anim.setDuration(200)
        anim.setStartValue(old_color)
        anim.setEndValue(new_color)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.valueChanged.connect(lambda c: self._apply_animated_color(c, status))
        anim.start()
        self._animations.append(anim)
        self._current_status: str = status

    def _apply_animated_color(self, color: QColor, status: str) -> None:
        hex_color: str = color.name()

        # Convert hex to RGB for opacity control
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)

        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: rgba({r}, {g}, {b}, 0.2);
                color: {hex_color};
                border-radius: 14px;
                padding: 0;
            }}
            """
        )
        self.status_label.setText(status)

    def animate_fade_in(self, delay_ms: int = 0) -> None:
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity_effect)

        anim = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        anim.setDuration(300)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(self._apply_shadow)

        QTimer.singleShot(delay_ms, anim.start)
        self._animations.append(anim)

    def enterEvent(self, event) -> None:
        self._apply_base_style(hovered=True)
        if hasattr(self, "shadow") and self.shadow is not None:
            try:
                self.shadow.setBlurRadius(20)
                self.shadow.setYOffset(4)
            except RuntimeError:
                pass
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._apply_base_style(hovered=False)
        if hasattr(self, "shadow") and self.shadow is not None:
            try:
                self.shadow.setBlurRadius(12)
                self.shadow.setYOffset(2)
            except RuntimeError:
                pass
        super().leaveEvent(event)
