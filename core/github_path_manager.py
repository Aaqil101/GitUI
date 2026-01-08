# ----- Built-In Modules -----
import getpass
import json
import os
import shutil
from pathlib import Path


class GitHubPathManager:
    """Singleton class for managing user-specific GitHub repository paths.

    Handles loading, saving, and accessing GitHub paths stored in JSON format.
    GitHub paths are user-specific, stored in %appdata%\\GitUI\\github_paths.json.
    """

    _instance = None
    _github_paths = None

    def __new__(cls):
        """Ensure only one instance of GitHubPathManager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._github_paths = None
        return cls._instance

    def get_github_paths_data(self) -> dict:
        """Get current GitHub paths data, loading from file if not already cached.

        Returns:
            dict: Current GitHub paths dictionary
        """
        if self._github_paths is None:
            self._github_paths = self.load_github_paths()
        return self._github_paths

    def load_github_paths(self) -> dict:
        """Load GitHub paths from JSON file with fallback to empty structure.

        Returns:
            dict: Loaded GitHub paths
        """
        try:
            github_paths_path: Path = self.get_github_paths_file()
            if github_paths_path.exists():
                with open(github_paths_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except json.JSONDecodeError as e:
            print(f"GitHub paths file corrupted: {e}")
            # Backup corrupted file
            backup_path: Path = self.get_github_paths_file().with_suffix(".json.backup")
            try:
                shutil.copy(self.get_github_paths_file(), backup_path)
                print(f"Corrupted GitHub paths backed up to: {backup_path}")
            except Exception as backup_error:
                print(f"Failed to backup corrupted GitHub paths: {backup_error}")
        except Exception as e:
            print(f"Error loading GitHub paths: {e}")

        # Return empty structure if loading failed
        return {"version": "1.0", "users": {}}

    def save_github_path(self, path: str) -> bool:
        """Save GitHub path for current user to JSON file.

        Args:
            path: GitHub repository path

        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            # Load current GitHub paths
            github_paths_data = self.get_github_paths_data()

            # Update GitHub path for current user
            user_name = self.get_current_user_name()
            if "users" not in github_paths_data:
                github_paths_data["users"] = {}

            github_paths_data["users"][user_name] = {"github_path": path}

            # Save to file
            github_paths_path: Path = self.get_github_paths_file()
            github_paths_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to temp file first (atomic write)
            temp_path: Path = github_paths_path.with_suffix(".json.tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(github_paths_data, f, indent=2)

            # Atomic rename
            temp_path.replace(github_paths_path)
            self._github_paths = github_paths_data  # Update cached GitHub paths
            return True

        except Exception as e:
            print(f"Error saving GitHub path: {e}")
            return False

    def get_github_path(self) -> Path:
        """Get GitHub path for current user only.

        Returns:
            Path: GitHub repository path as Path object
        """
        user_name: str = self.get_current_user_name()
        github_paths_data = self.get_github_paths_data()
        user_data = github_paths_data.get("users", {}).get(user_name, {})
        path_string = user_data.get("github_path", str(Path.home() / "Documents" / "GitHub"))
        return Path(path_string)

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

    def get_current_user_name(self) -> str:
        """Get the current user's username.

        Returns:
            str: Username from getpass.getuser()
        """
        return getpass.getuser()

    def get_github_paths_file(self) -> Path:
        """Get the path to the GitHub paths JSON file.

        Returns:
            Path: Path to github_paths.json in %appdata%\\GitUI\\
        """
        appdata = os.getenv("APPDATA")
        if not appdata:
            # Fallback for non-Windows or missing APPDATA
            appdata = str(Path.home() / "AppData" / "Roaming")
        return Path(appdata) / "GitUI" / "github_paths.json"
