# ----- PyQt6 Modules -----
from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QCursor, QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

# ----- Config Imports -----
from core.config import (
    FONT_FAMILY,
    FONT_SIZE_STAT,
    POWER_COUNTDOWN_SECONDS,
    PowerOption,
    STATS_PANEL_PADDING,
)

# ----- Manager Imports -----
from core.settings_manager import SettingsManager

# ----- Style Imports -----
from ui.styles import PANEL_STYLE

# ----- Utils Imports -----
from utils.icons import Icons


class PowerOptionsSignals(QObject):
    """Signals for power options panel."""

    # Emits: shutdown, restart, shutdown_cancel, restart_cancel
    option_selected = pyqtSignal(str)


def create_power_options_panel(parent=None) -> tuple[QWidget, PowerOptionsSignals]:
    """Create the power options panel.

    Args:
        parent: Parent widget

    Returns:
        tuple: (panel_widget, signals_object)
    """
    # Create signals object
    signals = PowerOptionsSignals()

    # Get settings
    settings_manager = SettingsManager()
    settings = settings_manager.get_settings()
    icon_only = settings.get("appearance", {}).get("power_buttons_icon_only", True)
    default_option_str = settings.get("git_operations", {}).get(
        "default_power_option", "shutdown"
    )
    default_option = PowerOption.from_string(default_option_str)

    # Create panel widget
    widget = QWidget(parent)
    widget.setStyleSheet(PANEL_STYLE)
    widget.default_power_option = default_option

    layout = QVBoxLayout(widget)
    layout.setSpacing(12)
    layout.setContentsMargins(*STATS_PANEL_PADDING)

    # Title with larger icon
    title_layout = QHBoxLayout()
    title_layout.setSpacing(8)
    title_layout.setContentsMargins(0, 0, 0, 0)

    # Icon label
    icon_label = QLabel(Icons.POWER)
    icon_label.setFont(QFont(FONT_FAMILY, 18))  # Larger icon size
    icon_label.setStyleSheet("color: white; padding: 0;")
    title_layout.addWidget(icon_label)

    # Title text
    title_text = QLabel("Power Options")
    title_text.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
    title_text.setStyleSheet("color: white; padding: 0;")
    title_layout.addWidget(title_text)

    title_layout.addStretch()

    title_widget = QWidget()
    title_widget.setLayout(title_layout)
    layout.addWidget(title_widget)

    # Countdown label - show the default power option name
    default_option_name = PowerOption.get_display_name(default_option)
    countdown_label = QLabel(
        f"Auto-selecting '{default_option_name}' in {POWER_COUNTDOWN_SECONDS}s..."
    )
    countdown_label.setFont(QFont(FONT_FAMILY, 10))
    countdown_label.setStyleSheet("color: #7aa2f7; padding: 0;")
    countdown_label.setWordWrap(True)
    layout.addWidget(countdown_label)

    # Buttons layout - horizontal for icon-only, 2x2 grid for text
    if icon_only:
        # Horizontal single line for icons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        shutdown_btn = _create_icon_button(Icons.SHUTDOWN, "#EF4444")
        shutdown_btn.setToolTip(
            "Commits with 'Shutdown commit by...', pushes, then shuts down system"
        )
        buttons_layout.addWidget(shutdown_btn)

        restart_btn = _create_icon_button(Icons.RESTART, "#3B82F6")
        restart_btn.setToolTip(
            "Commits with 'Restart commit by...', pushes, then restarts system"
        )
        buttons_layout.addWidget(restart_btn)

        shutdown_cancel_btn = _create_icon_button(
            f"{Icons.SHUTDOWN} {Icons.CANCEL}", "#F59E0B"
        )
        shutdown_cancel_btn.setToolTip(
            "Commits with 'Shutdown (Cancelled) commit by...', pushes, NO system action"
        )
        buttons_layout.addWidget(shutdown_cancel_btn)

        restart_cancel_btn = _create_icon_button(
            f"{Icons.RESTART} {Icons.CANCEL}", "#10B981"
        )
        restart_cancel_btn.setToolTip(
            "Commits with 'Restart (Cancelled) commit by...', pushes, NO system action"
        )
        buttons_layout.addWidget(restart_cancel_btn)

        layout.addLayout(buttons_layout)
    else:
        # 2x2 grid for text buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(8)

        # Row 1: Shutdown and Restart
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        shutdown_btn = _create_text_button("Shutdown", "#EF4444")
        shutdown_btn.setToolTip(
            "Commits with 'Shutdown commit by...', pushes, then shuts down system"
        )
        row1.addWidget(shutdown_btn)

        restart_btn = _create_text_button("Restart", "#3B82F6")
        restart_btn.setToolTip(
            "Commits with 'Restart commit by...', pushes, then restarts system"
        )
        row1.addWidget(restart_btn)

        buttons_layout.addLayout(row1)

        # Row 2: Shutdown (Cancel) and Restart (Cancel)
        row2 = QHBoxLayout()
        row2.setSpacing(8)

        shutdown_cancel_btn = _create_text_button("Shutdown (Cancel)", "#F59E0B")
        shutdown_cancel_btn.setToolTip(
            "Commits with 'Shutdown (Cancelled) commit by...', pushes, NO system action"
        )
        row2.addWidget(shutdown_cancel_btn)

        restart_cancel_btn = _create_text_button("Restart (Cancel)", "#10B981")
        restart_cancel_btn.setToolTip(
            "Commits with 'Restart (Cancelled) commit by...', pushes, NO system action"
        )
        row2.addWidget(restart_cancel_btn)

        buttons_layout.addLayout(row2)

        layout.addLayout(buttons_layout)

    # Store references and state in widget
    widget.countdown_label = countdown_label
    widget.shutdown_btn = shutdown_btn
    widget.restart_btn = restart_btn
    widget.shutdown_cancel_btn = shutdown_cancel_btn
    widget.restart_cancel_btn = restart_cancel_btn
    widget.power_option = None
    widget.countdown_timer = None
    widget.time_left = POWER_COUNTDOWN_SECONDS
    widget.signals = signals

    # Connect button clicks
    shutdown_btn.clicked.connect(lambda: _on_button_clicked(widget, "shutdown"))
    restart_btn.clicked.connect(lambda: _on_button_clicked(widget, "restart"))
    shutdown_cancel_btn.clicked.connect(
        lambda: _on_button_clicked(widget, "shutdown_cancel")
    )
    restart_cancel_btn.clicked.connect(
        lambda: _on_button_clicked(widget, "restart_cancel")
    )

    # Add start_countdown method to widget
    widget.start_countdown = lambda: _start_countdown(widget)
    widget.stop_countdown = lambda: _stop_countdown(widget)

    return widget, signals


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """
    Convert a hex color (e.g. '#ff5555') to an rgba() string with alpha.
    """
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    alpha = max(0.0, min(1.0, alpha))
    return f"rgba({r}, {g}, {b}, {alpha:.2f})"


def _create_icon_button(icon: str, color: str) -> QPushButton:
    """Create a modern styled power option button with icon only.

    Args:
        icon (str):
            Icon character(s), typically from a Nerd Font or icon font.
        color (str):
            Accent color used as the single source for both visual emphasis and
            background styling. The color is parsed (e.g. hex format) and converted
            to RGBA with different alpha values for normal, hover, pressed, and
            disabled states.

    Returns:
        QPushButton: Styled button with large icon
    """
    button = QPushButton(icon)
    button.setFixedHeight(40)
    # Large font for icon visibility
    button.setFont(QFont(FONT_FAMILY, 18, QFont.Weight.Bold))
    button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    # Clean button style matching settings button
    button.setStyleSheet(
        f"""
        QPushButton {{
            background-color: {_hex_to_rgba(color, 0.03)};
            color: {_hex_to_rgba(color, 0.9)};
            text-align: center;
            font-weight: bold;
            padding: 4px 8px;
            border: none;
            border-radius: 6px;
            white-space: nowrap;
        }}
        QPushButton:hover {{
            background-color: #222;
            color: {color};
            border-bottom: 2px solid {color};
            font-style: unset;
        }}
        QPushButton:pressed {{
            background-color: {_hex_to_rgba(color, 0.15)};
            color: #ffd700;
        }}
        QPushButton:disabled {{
            background-color: {_hex_to_rgba(color, 0.02)};
            color: rgba(255, 255, 255, 0.3);
        }}
        """
    )

    return button


def _create_text_button(text: str, color: str) -> QPushButton:
    """Create a modern styled power option button with text only.

    Args:
        text: Button text
        color (str):
            Accent color used as the single source for both visual emphasis and
            background styling. The color is parsed (e.g. hex format) and converted
            to RGBA with different alpha values for normal, hover, pressed, and
            disabled states.

    Returns:
        QPushButton: Styled button with text
    """
    button = QPushButton(text)
    button.setFixedHeight(40)
    # Normal font for text
    button.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT, QFont.Weight.Bold))
    button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    # Clean button style matching settings button
    button.setStyleSheet(
        f"""
        QPushButton {{
            background-color: {_hex_to_rgba(color, 0.03)};
            color: {_hex_to_rgba(color, 0.9)};
            text-align: center;
            font-weight: bold;
            padding: 4px 8px;
            border: none;
            border-radius: 6px;
            white-space: nowrap;
        }}
        QPushButton:hover {{
            background-color: #222;
            color: {color};
            border-bottom: 2px solid {color};
            font-style: unset;
        }}
        QPushButton:pressed {{
            background-color: {_hex_to_rgba(color, 0.15)};
            color: #ffd700;
        }}
        QPushButton:disabled {{
            background-color: {_hex_to_rgba(color, 0.02)};
            color: rgba(255, 255, 255, 0.3);
        }}
        """
    )

    return button


def _start_countdown(widget: QWidget) -> None:
    """Start the countdown timer and auto-selection."""
    widget.time_left = POWER_COUNTDOWN_SECONDS
    widget.countdown_timer = QTimer()
    widget.countdown_timer.timeout.connect(lambda: _update_countdown(widget))
    widget.countdown_timer.start(1000)

    # Auto-select default option after countdown
    QTimer.singleShot(
        POWER_COUNTDOWN_SECONDS * 1000, lambda: _auto_select_default(widget)
    )


def _update_countdown(widget: QWidget) -> None:
    """Update countdown label every second."""
    widget.time_left -= 1
    if widget.time_left >= 0:
        default_option_name = PowerOption.get_display_name(widget.default_power_option)
        widget.countdown_label.setText(
            f"Auto-selecting '{default_option_name}' in {widget.time_left}s..."
        )


def _auto_select_default(widget: QWidget) -> None:
    """Auto-select the default power option if no option selected."""
    if widget.power_option is None:
        _on_button_clicked(widget, widget.default_power_option.value)


def _on_button_clicked(widget: QWidget, option: str) -> None:
    """Handle power option button click.

    Args:
        widget: The panel widget
        option: Selected power option (shutdown, restart, shutdown_cancel, restart_cancel)
    """
    if widget.power_option is not None:
        return  # Already selected

    widget.power_option = option

    # Stop countdown timer
    if widget.countdown_timer:
        widget.countdown_timer.stop()

    # Update countdown label to show selection
    option_names: dict[str, str] = {
        "shutdown": f"{Icons.SHUTDOWN} Shutdown",
        "restart": f"{Icons.RESTART} Restart",
        "shutdown_cancel": f"{Icons.SHUTDOWN} {Icons.CANCEL} Shutdown (Cancel)",
        "restart_cancel": f"{Icons.RESTART} {Icons.CANCEL} Restart (Cancel)",
    }
    widget.countdown_label.setText(f"Selected: {option_names.get(option, option)}")
    widget.countdown_label.setStyleSheet("color: #9ece6a; padding: 0;")

    # Disable all buttons
    for btn in [
        widget.shutdown_btn,
        widget.restart_btn,
        widget.shutdown_cancel_btn,
        widget.restart_cancel_btn,
    ]:
        btn.setEnabled(False)

    # Emit signal
    widget.signals.option_selected.emit(option)


def _stop_countdown(widget: QWidget) -> None:
    """Stop the countdown timer."""
    if widget.countdown_timer:
        widget.countdown_timer.stop()
