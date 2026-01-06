# ----- Build-In Modules -----
from dataclasses import dataclass


@dataclass
class Color:
    """Color codes for everything."""

    # Status colors
    SUCCESS: str = "#9ece6a"
    FAILED: str = "#f7768e"
    PENDING: str = "#e0af68"
    QUEUED: str = "#7aa2f7"
    MISSING: str = "#bb9af7"
    SCANNING: str = "#e0af68"
    COMPLETE: str = "#9ece6a"

    # For random colors
    Orange: str = "#ff9e64"
    SoftOrange: str = "#ffb86c"
    Cyan: str = "#7dcfff"
    BrightCyan: str = "#2ac3de"
    Blue: str = "#7aa2f7"
    Aqua: str = "#73daca"

    @classmethod
    def get(cls, status: str, default: str = "#c0caf5") -> str:
        """Get color for status."""
        color_map: dict[str, str] = {
            "SUCCESS": cls.SUCCESS,
            "FAILED": cls.FAILED,
            "PENDING": cls.PENDING,
            "QUEUED": cls.QUEUED,
            "MISSING": cls.MISSING,
            "SCANNING": cls.SCANNING,
            "COMPLETE": cls.COMPLETE,
        }
        return color_map.get(status, default)

    @classmethod
    def random_color(cls) -> str:
        """Get a list of random colors."""
        return [
            cls.Orange,
            cls.SoftOrange,
            cls.Cyan,
            cls.BrightCyan,
            cls.Blue,
            cls.Aqua,
        ]
