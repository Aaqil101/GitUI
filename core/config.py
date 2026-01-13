# ----- Built-In Modules -----
from enum import Enum
from pathlib import Path


# ══════════════════════════════════════════════════════════════════
# POWER OPTIONS ENUM
# ══════════════════════════════════════════════════════════════════
class PowerOption(Enum):
    """Enum for power options in Git Push runner."""

    SHUTDOWN = "shutdown"
    RESTART = "restart"
    SHUTDOWN_CANCEL = "shutdown_cancel"
    RESTART_CANCEL = "restart_cancel"

    @classmethod
    def get_display_name(cls, option: "PowerOption") -> str:
        """Get human-readable display name for a power option.

        Args:
            option: PowerOption enum value

        Returns:
            str: Display name for the option
        """
        display_names = {
            cls.SHUTDOWN: "Shutdown",
            cls.RESTART: "Restart",
            cls.SHUTDOWN_CANCEL: "Shutdown (Cancel)",
            cls.RESTART_CANCEL: "Restart (Cancel)",
        }
        return display_names.get(option, option.value)

    @classmethod
    def from_string(cls, value: str) -> "PowerOption":
        """Convert string value to PowerOption enum.

        Args:
            value: String value (e.g., 'shutdown', 'restart')

        Returns:
            PowerOption: Corresponding enum value, defaults to SHUTDOWN
        """
        for option in cls:
            if option.value == value:
                return option
        return cls.SHUTDOWN


# ══════════════════════════════════════════════════════════════════
# LOG AUTO-DELETE OPTIONS ENUM
# ══════════════════════════════════════════════════════════════════
class LogAutoDelete(Enum):
    """Enum for log auto-delete options."""

    DISABLED = "disabled"
    DAYS_7 = "7_days"
    DAYS_30 = "30_days"
    DAYS_60 = "60_days"
    DAYS_90 = "90_days"

    @classmethod
    def get_display_name(cls, option: "LogAutoDelete") -> str:
        """Get human-readable display name for a log auto-delete option.

        Args:
            option: LogAutoDelete enum value

        Returns:
            str: Display name for the option
        """
        display_names = {
            cls.DISABLED: "Disabled",
            cls.DAYS_7: "Older than 7 days",
            cls.DAYS_30: "Older than 30 days",
            cls.DAYS_60: "Older than 60 days",
            cls.DAYS_90: "Older than 90 days",
        }
        return display_names.get(option, option.value)

    @classmethod
    def from_string(cls, value: str) -> "LogAutoDelete":
        """Convert string value to LogAutoDelete enum.

        Args:
            value: String value (e.g., 'disabled', '7_days')

        Returns:
            LogAutoDelete: Corresponding enum value, defaults to DISABLED
        """
        for option in cls:
            if option.value == value:
                return option
        return cls.DISABLED

    def get_days(self) -> int | None:
        """Get the number of days for this option.

        Returns:
            int | None: Number of days, or None if disabled
        """
        days_map = {
            self.DISABLED: None,
            self.DAYS_7: 7,
            self.DAYS_30: 30,
            self.DAYS_60: 60,
            self.DAYS_90: 90,
        }
        return days_map.get(self, None)


# ══════════════════════════════════════════════════════════════════
# WINDOW CONFIGURATION (Loaded from settings)
# ══════════════════════════════════════════════════════════════════
WINDOW_WIDTH = 920  # Default, overridden by settings
WINDOW_HEIGHT = 620  # Default, overridden by settings
WINDOW_TITLE = "Git Sync"
WINDOW_ALWAYS_ON_TOP = True  # Default, overridden by settings

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
COLOR_LIGHT_BLUE = "#7aa2f7"
COLOR_DARK_BLUE = "#0078d7"
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
# FONT CONFIGURATION (Loaded from settings)
# ══════════════════════════════════════════════════════════════════
FONT_FAMILY = "JetBrainsMono Nerd Font"  # Default, overridden by settings
FONT_SIZE_TITLE = 13  # Default, overridden by settings
FONT_SIZE_HEADER = 12  # Default, overridden by settings
FONT_SIZE_SUBTITLE = 9
FONT_SIZE_LABEL = 11  # Default, overridden by settings
FONT_SIZE_STAT = 10  # Default, overridden by settings
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

# Settings Dialog Side Panel
SETTINGS_SIDE_PANEL_WIDTH_EXPANDED = 180
SETTINGS_SIDE_PANEL_WIDTH_COLLAPSED = 60
SETTINGS_SIDE_PANEL_ANIMATION_DURATION = 300

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
    """Get default paths for the application.

    Note: The 'github' path is now username-specific via GitHubPathManager.
    """
    from core.github_path_manager import GitHubPathManager
    from utils.resources import get_resource_path

    script_dir: Path = Path(__file__).resolve().parent.parent
    github_path_manager = GitHubPathManager()

    return {
        "script_dir": script_dir,
        "assets": get_resource_path("assets"),
        "github": github_path_manager.get_github_path(),
        "msg_icon": get_resource_path("assets/Message.ico"),
        "app_icon": get_resource_path("assets/Git.ico"),
    }


# ══════════════════════════════════════════════════════════════════
# TIMING CONFIGURATION (Loaded from settings)
# ══════════════════════════════════════════════════════════════════
SCAN_START_DELAY = 0  # Default, overridden by settings
TEST_MODE_START_DELAY = 100
OPERATIONS_START_DELAY = 100  # Default, overridden by settings
AUTO_CLOSE_DELAY = 1000  # Default, overridden by settings
AUTO_CLOSE_NO_REPOS_DELAY = 2000  # Default, overridden by settings
TIME_UPDATE_INTERVAL = 100

# ══════════════════════════════════════════════════════════════════
# POWER OPTIONS DIALOG CONFIGURATION (Loaded from settings)
# ══════════════════════════════════════════════════════════════════
POWER_DIALOG_WIDTH = 500
POWER_DIALOG_HEIGHT = 220
POWER_COUNTDOWN_SECONDS = 15  # Default, overridden by settings

# ══════════════════════════════════════════════════════════════════
# BUTTON CONFIGURATION
# ══════════════════════════════════════════════════════════════════
BUTTON_HEIGHT = 36
BUTTON_PADDING = (0, 16)

# ══════════════════════════════════════════════════════════════════
# PROGRESS BAR COLORS (Animation)
# ══════════════════════════════════════════════════════════════════
PROGRESS_COLORS: list[str] = [
    "#7aa2f7",  # Blue
    "#7dcfff",  # Cyan
    "#9ece6a",  # Green
    "#e0af68",  # Yellow
    "#ff9e64",  # Orange
    "#f7768e",  # Red
    "#bb9af7",  # Purple
]


# ══════════════════════════════════════════════════════════════════
# SETTINGS LOADER
# ══════════════════════════════════════════════════════════════════
def load_settings_into_config() -> None:
    """Load settings from SettingsManager and update config constants.

    This function should be called at application startup to apply saved settings.
    Settings marked with "Default, overridden by settings" comments will be updated.
    """
    from core.settings_manager import SettingsManager

    settings_manager = SettingsManager()
    settings = settings_manager.get_settings()

    # Update global variables with settings values
    global WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_ALWAYS_ON_TOP
    global FONT_FAMILY, FONT_SIZE_TITLE, FONT_SIZE_HEADER, FONT_SIZE_LABEL, FONT_SIZE_STAT
    global SCAN_START_DELAY, OPERATIONS_START_DELAY
    global AUTO_CLOSE_DELAY, AUTO_CLOSE_NO_REPOS_DELAY
    global POWER_COUNTDOWN_SECONDS

    # General settings
    WINDOW_WIDTH = settings.get("general", {}).get("window_width", WINDOW_WIDTH)
    WINDOW_HEIGHT = settings.get("general", {}).get("window_height", WINDOW_HEIGHT)
    WINDOW_ALWAYS_ON_TOP = settings.get("general", {}).get("window_always_on_top", WINDOW_ALWAYS_ON_TOP)
    AUTO_CLOSE_DELAY = settings.get("general", {}).get("auto_close_delay", AUTO_CLOSE_DELAY)
    AUTO_CLOSE_NO_REPOS_DELAY = settings.get("general", {}).get("auto_close_no_repos_delay", AUTO_CLOSE_NO_REPOS_DELAY)

    # Appearance settings
    FONT_FAMILY = settings.get("appearance", {}).get("font_family", FONT_FAMILY)
    FONT_SIZE_TITLE = settings.get("appearance", {}).get("font_size_title", FONT_SIZE_TITLE)
    FONT_SIZE_HEADER = settings.get("appearance", {}).get("font_size_header", FONT_SIZE_HEADER)
    FONT_SIZE_LABEL = settings.get("appearance", {}).get("font_size_label", FONT_SIZE_LABEL)
    FONT_SIZE_STAT = settings.get("appearance", {}).get("font_size_stat", FONT_SIZE_STAT)

    # Advanced settings
    SCAN_START_DELAY = settings.get("advanced", {}).get("scan_start_delay", SCAN_START_DELAY)
    OPERATIONS_START_DELAY = settings.get("advanced", {}).get("operations_start_delay", OPERATIONS_START_DELAY)

    # Git operations settings
    POWER_COUNTDOWN_SECONDS = settings.get("git_operations", {}).get("power_countdown_seconds", POWER_COUNTDOWN_SECONDS)
