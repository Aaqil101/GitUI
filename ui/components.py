# ----- PyQt6 Modules -----
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QWidget,
)

# ----- Config Imports -----
from core.config import (
    FONT_FAMILY,
    FONT_SIZE_STAT,
    FONT_SIZE_ICON,
    SHADOW_BLUR_ICON,
    SHADOW_BLUR_TITLE,
    SHADOW_BLUR_SUBTITLE,
    SHADOW_OFFSET_X,
    SHADOW_OFFSET_Y_ICON,
    SHADOW_OFFSET_Y_TITLE,
    SHADOW_OFFSET_Y_SUBTITLE,
    SHADOW_OPACITY,
    SEGMENT_WIDTH,
    SEGMENT_HEIGHT,
    SEGMENT_SPACING,
    PROGRESS_BAR_SEGMENTS,
)

# ----- Style Imports -----
from ui.styles import (
    PROGRESS_BAR_CONTAINER_STYLE,
    PROGRESS_SEGMENT_DEFAULT_STYLE,
    STAT_ROW_STYLE,
)


# ══════════════════════════════════════════════════════════════════
# SHADOW EFFECTS
# ══════════════════════════════════════════════════════════════════
def apply_shadow_effect(
    widget: QWidget,
    blur_radius: int = SHADOW_BLUR_ICON,
    offset_x: int = SHADOW_OFFSET_X,
    offset_y: int = SHADOW_OFFSET_Y_ICON,
    opacity: int = SHADOW_OPACITY,
) -> None:
    """Apply drop shadow effect to a widget."""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur_radius)
    shadow.setXOffset(offset_x)
    shadow.setYOffset(offset_y)
    shadow.setColor(QColor(0, 0, 0, opacity))
    widget.setGraphicsEffect(shadow)


def apply_icon_shadow(widget: QWidget) -> None:
    """Apply icon-specific shadow effect."""
    apply_shadow_effect(
        widget,
        blur_radius=SHADOW_BLUR_ICON,
        offset_y=SHADOW_OFFSET_Y_ICON,
    )


def apply_title_shadow(widget: QWidget) -> None:
    """Apply title-specific shadow effect."""
    apply_shadow_effect(
        widget,
        blur_radius=SHADOW_BLUR_TITLE,
        offset_y=SHADOW_OFFSET_Y_TITLE,
    )


def apply_subtitle_shadow(widget: QWidget) -> None:
    """Apply subtitle-specific shadow effect."""
    apply_shadow_effect(
        widget,
        blur_radius=SHADOW_BLUR_SUBTITLE,
        offset_y=SHADOW_OFFSET_Y_SUBTITLE,
    )


# ══════════════════════════════════════════════════════════════════
# LABEL CREATION
# ══════════════════════════════════════════════════════════════════
def create_icon_label(
    icon_text: str, font_size: int, color: str, fixed_size: tuple[int, int] = None
) -> QLabel:
    """Create an icon label with specified properties."""
    icon_label = QLabel(icon_text)
    icon_label.setFont(QFont(FONT_FAMILY, font_size))
    icon_label.setStyleSheet(f"color: {color}; padding: 0;")

    if fixed_size:
        icon_label.setFixedSize(*fixed_size)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    return icon_label


def create_text_label(
    text: str,
    font_size: int,
    color: str,
    bold: bool = False,
    alignment: Qt.AlignmentFlag = None,
    fixed_width: int = None,
) -> QLabel:
    """Create a text label with specified properties."""
    label = QLabel(text)
    weight = QFont.Weight.Bold if bold else QFont.Weight.Normal
    label.setFont(QFont(FONT_FAMILY, font_size, weight))
    label.setStyleSheet(f"color: {color}; padding: 0;")

    if alignment:
        label.setAlignment(alignment)

    if fixed_width:
        label.setFixedWidth(fixed_width)

    return label


# ══════════════════════════════════════════════════════════════════
# PROGRESS BAR
# ══════════════════════════════════════════════════════════════════
def create_progress_bar(segment_count: int = PROGRESS_BAR_SEGMENTS) -> tuple[QWidget, list[QLabel]]:
    """
    Create an animated progress bar with segments.

    Returns:
        tuple: (container_widget, list_of_segment_labels)
    """
    bar_container = QWidget()
    bar_container.setFixedHeight(16)
    bar_container.setStyleSheet(PROGRESS_BAR_CONTAINER_STYLE)

    bar_layout = QHBoxLayout(bar_container)
    bar_layout.setContentsMargins(4, 4, 4, 4)
    bar_layout.setSpacing(SEGMENT_SPACING)

    segments: list[QLabel] = []
    for _ in range(segment_count):
        seg = QLabel()
        seg.setFixedSize(SEGMENT_WIDTH, SEGMENT_HEIGHT)
        seg.setStyleSheet(PROGRESS_SEGMENT_DEFAULT_STYLE)
        segments.append(seg)
        bar_layout.addWidget(seg)

    return bar_container, segments


# ══════════════════════════════════════════════════════════════════
# STAT ROW
# ══════════════════════════════════════════════════════════════════
def create_stat_row(icon: str, label: str, value: str, color: str) -> QWidget:
    """
    Create a statistics row widget with icon, label, and value.

    Args:
        icon: Icon text (Nerd Font unicode)
        label: Label text
        value: Value text
        color: Color for icon and value

    Returns:
        QWidget: The stat row widget
    """
    row = QWidget()
    row.setStyleSheet(STAT_ROW_STYLE)

    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 2, 0, 2)
    layout.setSpacing(12)

    # Icon
    icon_lbl = QLabel(icon)
    icon_lbl.setFont(QFont(FONT_FAMILY, FONT_SIZE_ICON))
    icon_lbl.setStyleSheet(f"color: {color}; padding: 0;")
    icon_lbl.setFixedWidth(24)
    icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(icon_lbl)

    # Label
    text_lbl = QLabel(label)
    text_lbl.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
    text_lbl.setStyleSheet("color: #a9b1d6; padding: 0;")
    layout.addWidget(text_lbl, 1)

    # Value
    value_lbl = QLabel(value)
    value_lbl.setFont(QFont(FONT_FAMILY, FONT_SIZE_ICON))
    value_lbl.setStyleSheet(f"color: {color}; padding: 0; font-weight: bold;")
    value_lbl.setObjectName("value")
    value_lbl.setFixedWidth(40)
    value_lbl.setAlignment(
        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
    )
    layout.addWidget(value_lbl)

    return row


# ══════════════════════════════════════════════════════════════════
# PANEL WIDGETS
# ══════════════════════════════════════════════════════════════════
def create_panel_widget(min_height: int = None) -> QWidget:
    """Create a styled panel widget."""
    widget = QWidget()
    if min_height:
        widget.setMinimumHeight(min_height)
    return widget
