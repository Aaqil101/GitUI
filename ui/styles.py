# ----- Built-In Modules -----
from core.config import (
    THEME_BG_PRIMARY,
    THEME_BG_SECONDARY,
    THEME_TEXT_PRIMARY,
    THEME_BORDER,
    BUTTON_BORDER_RADIUS,
    PANEL_BORDER_RADIUS,
)

# ══════════════════════════════════════════════════════════════════
# WINDOW STYLES
# ══════════════════════════════════════════════════════════════════
WINDOW_STYLE = f"""
    QWidget {{
        background-color: {THEME_BG_PRIMARY};
        color: {THEME_TEXT_PRIMARY};
    }}
"""

# ══════════════════════════════════════════════════════════════════
# PANEL STYLES
# ══════════════════════════════════════════════════════════════════
PANEL_STYLE = f"""
    background-color: {THEME_BG_SECONDARY};
    border-radius: {PANEL_BORDER_RADIUS}px;
"""

HEADER_PANEL_STYLE = f"""
    QWidget {{
        background-color: {THEME_BG_SECONDARY};
        border-radius: {PANEL_BORDER_RADIUS}px;
        padding: 8px;
    }}
"""

# ══════════════════════════════════════════════════════════════════
# SCROLL AREA STYLES
# ══════════════════════════════════════════════════════════════════
SCROLL_AREA_STYLE = f"""
    QScrollArea {{
        background-color: transparent;
        border: none;
    }}
    QScrollBar:vertical {{
        background-color: {THEME_BG_PRIMARY};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {THEME_BORDER};
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: #565f89;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}
"""

# ══════════════════════════════════════════════════════════════════
# BUTTON STYLES
# ══════════════════════════════════════════════════════════════════
def get_button_style(bg_color: str, text_color: str) -> str:
    """Generate button stylesheet with hover and pressed states."""
    # Calculate lighter and darker shades (simple hex color manipulation)
    # For simplicity, we'll use fixed hover/pressed colors
    hover_color = "#89b4fa" if bg_color == "#7aa2f7" else bg_color
    pressed_color = "#5a8cd7" if bg_color == "#7aa2f7" else bg_color

    return f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            border-radius: {BUTTON_BORDER_RADIUS}px;
            padding: 0 16px;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
        QPushButton:pressed {{
            background-color: {pressed_color};
        }}
    """


RETRY_BUTTON_STYLE = get_button_style("#7aa2f7", THEME_BG_PRIMARY)

# ══════════════════════════════════════════════════════════════════
# PROGRESS BAR STYLES
# ══════════════════════════════════════════════════════════════════
PROGRESS_BAR_CONTAINER_STYLE = f"""
    background-color: {THEME_BG_PRIMARY};
    border-radius: 6px;
"""

PROGRESS_SEGMENT_DEFAULT_STYLE = f"""
    background-color: {THEME_BORDER};
    border-radius: 2px;
"""


def get_progress_segment_style(color: str) -> str:
    """Get styled progress segment with specific color."""
    return f"""
        background-color: {color};
        border-radius: 2px;
    """


# ══════════════════════════════════════════════════════════════════
# SEPARATOR STYLES
# ══════════════════════════════════════════════════════════════════
def get_separator_style(color: str = THEME_BORDER) -> str:
    """Get separator line stylesheet."""
    return f"background-color: {color};"


# ══════════════════════════════════════════════════════════════════
# CARD STYLES
# ══════════════════════════════════════════════════════════════════
CARD_CONTAINER_STYLE = "background-color: transparent;"

# ══════════════════════════════════════════════════════════════════
# STAT ROW STYLES
# ══════════════════════════════════════════════════════════════════
STAT_ROW_STYLE = "background: transparent;"
