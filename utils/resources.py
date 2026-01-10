# ----- Built-In Modules -----
import sys
from pathlib import Path

# ----- PyQt6 Modules -----
from PyQt6.QtGui import QIcon


def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to resource, works for dev and for PyInstaller.

    Args:
        relative_path: Relative path to resource from project root

    Returns:
        Path: Absolute path to resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # Running in development mode
        base_path = Path(__file__).parent.parent

    return base_path / relative_path


def get_icon(icon_name: str) -> QIcon:
    """Get QIcon from assets folder with proper resource path handling.

    Args:
        icon_name: Icon filename (e.g., "Git.ico", "Check.png")

    Returns:
        QIcon: QIcon object loaded from resource path
    """
    icon_path = get_resource_path(f"assets/{icon_name}")

    # If resource doesn't exist, try fallback paths
    if not icon_path.exists():
        # Try project root / assets
        icon_path = Path(__file__).parent.parent / "assets" / icon_name

    return QIcon(str(icon_path))


# Icon constants for easy import
class ResourceIcons:
    """Icon resource constants."""

    APP_ICON = "Git.ico"
    APP_ICON_PNG = "Git.png"
    MESSAGE_ICON = "Message.ico"
    MESSAGE_ICON_PNG = "Message.png"
    CHECK_ICON = "Check.png"
