# ----- Built-In Modules -----
import getpass
import json
import os
import shutil
from pathlib import Path


class CustomPathsManager:
    """Singleton class for managing machine-specific custom repository paths.

    Handles loading, saving, and accessing custom repository paths stored in JSON format.
    Custom paths are machine-specific, stored in %appdata%\GitUI\custom_repositories.json.
    """

    _instance = None
    _custom_paths = None

    def __new__(cls):
        """Ensure only one instance of CustomPathsManager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._custom_paths = None
        return cls._instance

    def get_custom_paths_data(self) -> dict:
        """Get current custom paths data, loading from file if not already cached.

        Returns:
            dict: Current custom paths dictionary
        """
        if self._custom_paths is None:
            self._custom_paths = self.load_custom_paths()
        return self._custom_paths

    def load_custom_paths(self) -> dict:
        """Load custom paths from JSON file with fallback to empty structure.

        Returns:
            dict: Loaded custom paths
        """
        try:
            custom_paths_path = self.get_custom_paths_file()
            if custom_paths_path.exists():
                with open(custom_paths_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Custom paths file corrupted: {e}")
            # Backup corrupted file
            backup_path = self.get_custom_paths_file().with_suffix(".json.backup")
            try:
                shutil.copy(self.get_custom_paths_file(), backup_path)
                print(f"Corrupted custom paths backed up to: {backup_path}")
            except Exception as backup_error:
                print(f"Failed to backup corrupted custom paths: {backup_error}")
        except Exception as e:
            print(f"Error loading custom paths: {e}")

        # Return empty structure if loading failed
        return {"version": "1.0", "machines": {}}

    def save_custom_paths(self, paths_list: list[str]) -> bool:
        """Save custom paths for current machine to JSON file.

        Args:
            paths_list: List of custom repository paths

        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            # Load current custom paths
            custom_paths_data = self.get_custom_paths_data()

            # Update custom paths for current machine
            machine_name = self.get_current_machine_name()
            if "machines" not in custom_paths_data:
                custom_paths_data["machines"] = {}

            custom_paths_data["machines"][machine_name] = {"custom_paths": paths_list}

            # Save to file
            custom_paths_path = self.get_custom_paths_file()
            custom_paths_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to temp file first (atomic write)
            temp_path = custom_paths_path.with_suffix(".json.tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(custom_paths_data, f, indent=2)

            # Atomic rename
            temp_path.replace(custom_paths_path)
            self._custom_paths = custom_paths_data  # Update cached custom paths
            return True

        except Exception as e:
            print(f"Error saving custom paths: {e}")
            return False

    def get_custom_paths(self) -> list[Path]:
        """Get list of custom paths for current machine only.

        Returns:
            list[Path]: List of custom repository paths as Path objects
        """
        machine_name = self.get_current_machine_name()
        custom_paths_data = self.get_custom_paths_data()
        machine_data = custom_paths_data.get("machines", {}).get(machine_name, {})
        path_strings = machine_data.get("custom_paths", [])
        return [Path(p) for p in path_strings]

    def add_path(self, path: str) -> tuple[bool, str]:
        """Add new custom path with validation for current machine.

        Args:
            path: Path to add

        Returns:
            tuple[bool, str]: (Success, Error message if failed)
        """
        # Validate path
        is_valid, error_msg = self.validate_path(path)
        if not is_valid:
            return False, error_msg

        # Get current paths
        current_paths = [str(p) for p in self.get_custom_paths()]

        # Check if already exists
        if path in current_paths:
            return False, "Path already exists in custom paths"

        # Add new path
        current_paths.append(path)
        success = self.save_custom_paths(current_paths)

        if success:
            return True, ""
        else:
            return False, "Failed to save custom paths"

    def remove_path(self, path: str) -> bool:
        """Remove custom path from current machine.

        Args:
            path: Path to remove

        Returns:
            bool: True if remove successful, False otherwise
        """
        current_paths = [str(p) for p in self.get_custom_paths()]

        if path in current_paths:
            current_paths.remove(path)
            return self.save_custom_paths(current_paths)

        return True  # Already not in list

    def validate_path(self, path: str) -> tuple[bool, str]:
        """Check if path exists and is accessible.

        Args:
            path: Path to validate

        Returns:
            tuple[bool, str]: (Is valid, Error message if invalid)
        """
        try:
            path_obj = Path(path)

            # Check if path is absolute
            if not path_obj.is_absolute():
                return False, "Path must be an absolute path"

            # Check if path exists
            if not path_obj.exists():
                return False, "Path does not exist"

            # Check if path is a directory
            if not path_obj.is_dir():
                return False, "Path must be a directory"

            # Check if path is accessible (try to list contents)
            try:
                list(path_obj.iterdir())
            except PermissionError:
                return False, "No permission to access this directory"

            return True, ""

        except Exception as e:
            return False, f"Invalid path: {str(e)}"

    def get_all_scan_paths(self) -> list[Path]:
        """Get all paths to scan (GitHub + custom) for current machine.

        Returns:
            list[Path]: List of all paths to scan
        """
        from core.config import get_default_paths

        paths = [get_default_paths()["github"]]
        paths.extend(self.get_custom_paths())  # Machine-specific
        return paths

    def get_current_machine_name(self) -> str:
        """Get the current user's username.

        Returns:
            str: Username from getpass.getuser()
        """
        return getpass.getuser()

    def get_custom_paths_file(self) -> Path:
        """Get the path to the custom repositories JSON file.

        Returns:
            Path: Path to custom_repositories.json in %appdata%\GitUI\
        """
        appdata = os.getenv("APPDATA")
        if not appdata:
            # Fallback for non-Windows or missing APPDATA
            appdata = str(Path.home() / "AppData" / "Roaming")
        return Path(appdata) / "GitUI" / "custom_repositories.json"
