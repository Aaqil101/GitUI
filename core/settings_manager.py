# ----- Built-In Modules -----
import json
import os
import shutil
from pathlib import Path


class SettingsManager:
    """Singleton class for managing application settings.

    Handles loading, saving, and accessing settings stored in JSON format.
    Settings are stored in %appdata%\\GitUI\\settings.json.
    """

    _instance = None
    _settings = None

    def __new__(cls):
        """Ensure only one instance of SettingsManager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._settings = None
        return cls._instance

    def get_settings(self) -> dict:
        """Get current settings, loading from file if not already cached.

        Returns:
            dict: Current settings dictionary
        """
        if self._settings is None:
            self._settings = self.load_settings()
        return self._settings

    def load_settings(self) -> dict:
        """Load settings from JSON file with fallback to defaults.

        Returns:
            dict: Loaded settings merged with defaults
        """
        try:
            settings_path: Path = self.get_settings_path()
            if settings_path.exists():
                with open(settings_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    return self._merge_with_defaults(loaded)
        except json.JSONDecodeError as e:
            print(f"Settings file corrupted: {e}")
            # Backup corrupted file
            backup_path: Path = self.get_settings_path().with_suffix(".json.backup")
            try:
                shutil.copy(self.get_settings_path(), backup_path)
                print(f"Corrupted settings backed up to: {backup_path}")
            except Exception as backup_error:
                print(f"Failed to backup corrupted settings: {backup_error}")
        except Exception as e:
            print(f"Error loading settings: {e}")

        # Return defaults if loading failed
        return self._get_default_settings()

    def save_settings(self, settings: dict) -> bool:
        """Save settings to JSON file with atomic write.

        Args:
            settings: Settings dictionary to save

        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            settings_path: Path = self.get_settings_path()
            settings_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to temp file first (atomic write)
            temp_path: Path = settings_path.with_suffix(".json.tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)

            # Atomic rename
            temp_path.replace(settings_path)
            self._settings = settings  # Update cached settings
            return True

        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def reset_to_defaults(self) -> bool:
        """Reset settings to default values.

        Returns:
            bool: True if reset successful, False otherwise
        """
        default_settings = self._get_default_settings()
        return self.save_settings(default_settings)

    def get_settings_path(self) -> Path:
        """Get the path to the settings JSON file.

        Returns:
            Path: Path to settings.json in %appdata%\\GitUI\\
        """
        appdata = os.getenv("APPDATA")
        if not appdata:
            # Fallback for non-Windows or missing APPDATA
            appdata = str(Path.home() / "AppData" / "Roaming")
        return Path(appdata) / "GitUI" / "settings.json"

    def _merge_with_defaults(self, loaded: dict) -> dict:
        """Merge loaded settings with defaults to handle new settings.

        Args:
            loaded: Loaded settings from file

        Returns:
            dict: Merged settings with all default keys present
        """
        defaults = self._get_default_settings()

        # Deep merge: iterate through all categories
        for category, values in defaults.items():
            if category not in loaded:
                loaded[category] = values
            elif isinstance(values, dict):
                # Merge category-level settings
                for key, default_val in values.items():
                    if key not in loaded[category]:
                        loaded[category][key] = default_val

        return loaded

    def _get_default_settings(self) -> dict:
        """Get default settings dictionary.

        Returns:
            dict: Default settings with all categories and values
        """
        return {
            "version": "1.0",
            "general": {
                "window_always_on_top": True,
                "window_width": 920,
                "window_height": 620,
                "auto_close_delay": 1000,
                "auto_close_no_repos_delay": 2000,
            },
            "git_operations": {
                "powershell_throttle_limit": 30,
                "scan_timeout": 300,
                "operation_timeout": 60,
                "power_countdown_seconds": 15,
                "default_power_option": "shutdown",
                "exclude_confirmation_timeout": 5,
                "exclude_repos_affect_pull": False,
            },
            "appearance": {
                "font_family": "JetBrainsMono Nerd Font",
                "font_size_title": 13,
                "font_size_header": 12,
                "font_size_label": 11,
                "font_size_stat": 10,
                "enable_animations": True,
                "animation_duration": 300,
                "power_buttons_icon_only": True,
            },
            "advanced": {
                "test_mode_default": False,
                "scan_start_delay": 0,
                "operations_start_delay": 100,
            },
        }
