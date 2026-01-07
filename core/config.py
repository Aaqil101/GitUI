# ----- Built-In Modules -----
from pathlib import Path

# ══════════════════════════════════════════════════════════════════
# WINDOW CONFIGURATION
# ══════════════════════════════════════════════════════════════════
WINDOW_WIDTH = 920
WINDOW_HEIGHT = 620
WINDOW_TITLE = "Git Sync"
WINDOW_ALWAYS_ON_TOP = True

# ══════════════════════════════════════════════════════════════════
# THEME - TOKYO NIGHT
# ══════════════════════════════════════════════════════════════════
THEME_BG_PRIMARY = "#1a1b26"
THEME_BG_SECONDARY = "#24283b"
THEME_TEXT_PRIMARY = "#c0caf5"
THEME_TEXT_SECONDARY = "#9aa4d1"
THEME_TEXT_SUBTLE = "#a9b1d6"
THEME_TEXT_DIM = "#565f89"
THEME_BORDER = "#414868"

# Color Accents
COLOR_BLUE = "#7aa2f7"
COLOR_CYAN = "#7dcfff"
COLOR_GREEN = "#9ece6a"
COLOR_YELLOW = "#e0af68"
COLOR_ORANGE = "#ff9e64"
COLOR_RED = "#f7768e"
COLOR_PURPLE = "#bb9af7"

# Status Colors
COLOR_SUCCESS = "#9ece6a"
COLOR_FAILED = "#f7768e"
COLOR_PENDING = "#e0af68"
COLOR_QUEUED = "#7aa2f7"
COLOR_SCANNING = "#7dcfff"
COLOR_COMPLETE = "#9ece6a"

# ══════════════════════════════════════════════════════════════════
# FONT CONFIGURATION
# ══════════════════════════════════════════════════════════════════
FONT_FAMILY = "JetBrainsMono Nerd Font"
FONT_SIZE_TITLE = 13
FONT_SIZE_HEADER = 12
FONT_SIZE_SUBTITLE = 9
FONT_SIZE_LABEL = 11
FONT_SIZE_STAT = 10
FONT_SIZE_ICON = 14
FONT_SIZE_ICON_LARGE = 16
FONT_SIZE_ICON_HEADER = 15

# ══════════════════════════════════════════════════════════════════
# LAYOUT CONFIGURATION
# ══════════════════════════════════════════════════════════════════
LEFT_PANEL_WIDTH = 400
PANEL_SPACING = 20
PANEL_MARGINS = (24, 24, 24, 24)
SECTION_SPACING = 16
HEADER_HEIGHT = 90
SCANNER_PANEL_PADDING = (20, 16, 20, 16)
STATS_PANEL_PADDING = (20, 16, 20, 16)
CARD_AREA_PADDING = (0, 0, 8, 0)

# Border Radius
PANEL_BORDER_RADIUS = 12
BUTTON_BORDER_RADIUS = 8
PROGRESS_BAR_RADIUS = 6
SEGMENT_RADIUS = 2

# ══════════════════════════════════════════════════════════════════
# ANIMATION CONFIGURATION
# ══════════════════════════════════════════════════════════════════
PROGRESS_BAR_SEGMENTS = 23
ANIMATION_INTERVAL = 150
FADE_IN_DURATION = 300
ANIMATION_EASING = "OutCubic"

# Progress Segment Size
SEGMENT_WIDTH = 8
SEGMENT_HEIGHT = 8
SEGMENT_SPACING = 3

# Shadow Configuration
SHADOW_BLUR_ICON = 12
SHADOW_BLUR_TITLE = 15
SHADOW_BLUR_SUBTITLE = 10
SHADOW_OFFSET_X = 0
SHADOW_OFFSET_Y_ICON = 2
SHADOW_OFFSET_Y_TITLE = 2
SHADOW_OFFSET_Y_SUBTITLE = 1
SHADOW_OPACITY = 70


# ══════════════════════════════════════════════════════════════════
# PATH CONFIGURATION
# ══════════════════════════════════════════════════════════════════
def get_default_paths() -> dict[str, Path]:
    """Get default paths for the application."""
    script_dir: Path = Path(__file__).resolve().parent.parent
    return {
        "script_dir": script_dir,
        "assets": script_dir / "assets",
        "github": Path.home() / "Documents" / "GitHub",
        "msg_icon": script_dir / "assets" / "Message.ico",
        "app_icon": script_dir / "assets" / "Git.ico",
    }


# ══════════════════════════════════════════════════════════════════
# TIMING CONFIGURATION
# ══════════════════════════════════════════════════════════════════
SCAN_START_DELAY = 0
TEST_MODE_START_DELAY = 100
OPERATIONS_START_DELAY = 100
AUTO_CLOSE_DELAY = 1000
AUTO_CLOSE_NO_REPOS_DELAY = 2000
TIME_UPDATE_INTERVAL = 100

# ══════════════════════════════════════════════════════════════════
# POWER OPTIONS DIALOG CONFIGURATION
# ══════════════════════════════════════════════════════════════════
POWER_DIALOG_WIDTH = 500
POWER_DIALOG_HEIGHT = 220
POWER_COUNTDOWN_SECONDS = 5

# ══════════════════════════════════════════════════════════════════
# BUTTON CONFIGURATION
# ══════════════════════════════════════════════════════════════════
BUTTON_HEIGHT = 36
BUTTON_PADDING = (0, 16)

# ══════════════════════════════════════════════════════════════════
# PROGRESS BAR COLORS (Animation)
# ══════════════════════════════════════════════════════════════════
PROGRESS_COLORS = [
    "#7aa2f7",  # Blue
    "#7dcfff",  # Cyan
    "#9ece6a",  # Green
    "#e0af68",  # Yellow
    "#ff9e64",  # Orange
    "#f7768e",  # Red
    "#bb9af7",  # Purple
]
