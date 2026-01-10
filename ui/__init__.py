"""UI components and styles."""

from ui.components import (
    apply_icon_shadow,
    apply_subtitle_shadow,
    apply_title_shadow,
    create_icon_label,
    create_panel_widget,
    create_progress_bar,
    create_stat_row,
    create_text_label,
)
from ui.power_options_panel import PowerOptionsSignals, create_power_options_panel
from ui.styles import (
    CARD_CONTAINER_STYLE,
    HEADER_PANEL_STYLE,
    PANEL_STYLE,
    PROGRESS_SEGMENT_DEFAULT_STYLE,
    RETRY_BUTTON_STYLE,
    SCROLL_AREA_STYLE,
    WINDOW_STYLE,
    get_button_style,
    get_progress_segment_style,
    get_separator_style,
)

__all__ = [
    # Components
    "apply_icon_shadow",
    "apply_subtitle_shadow",
    "apply_title_shadow",
    "create_icon_label",
    "create_panel_widget",
    "create_progress_bar",
    "create_stat_row",
    "create_text_label",
    # Panels
    "create_power_options_panel",
    "PowerOptionsSignals",
    # Styles
    "CARD_CONTAINER_STYLE",
    "HEADER_PANEL_STYLE",
    "PANEL_STYLE",
    "PROGRESS_SEGMENT_DEFAULT_STYLE",
    "RETRY_BUTTON_STYLE",
    "SCROLL_AREA_STYLE",
    "WINDOW_STYLE",
    "get_button_style",
    "get_progress_segment_style",
    "get_separator_style",
]
