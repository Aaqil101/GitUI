# ----- Built-In Modules -----
import getpass
import json
import os
import shutil
from pathlib import Path


class ExcludeManager:
    """Singleton class for managing user-specific repository exclusions.

    Handles loading, saving, and checking repository exclusions stored in JSON format.
    Exclusions are user-specific, stored in %appdata%\\GitUI\\exclude_repositories.json.
    """

    _instance = None
    _exclusions = None

    def __new__(cls):
        """Ensure only one instance of ExcludeManager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._exclusions = None
        return cls._instance

    def get_exclusions(self) -> dict:
        """Get current exclusions, loading from file if not already cached.

        Returns:
            dict: Current exclusions dictionary
        """
        if self._exclusions is None:
            self._exclusions = self.load_exclusions()
        return self._exclusions

    def load_exclusions(self) -> dict:
        """Load exclusions from JSON file with fallback to empty structure.

        Returns:
            dict: Loaded exclusions
        """
        try:
            exclusions_path: Path = self.get_exclusions_path()
            if exclusions_path.exists():
                with open(exclusions_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Exclusions file corrupted: {e}")
            # Backup corrupted file
            backup_path: Path = self.get_exclusions_path().with_suffix(".json.backup")
            try:
                shutil.copy(self.get_exclusions_path(), backup_path)
                print(f"Corrupted exclusions backed up to: {backup_path}")
            except Exception as backup_error:
                print(f"Failed to backup corrupted exclusions: {backup_error}")
        except Exception as e:
            print(f"Error loading exclusions: {e}")

        # Return empty structure if loading failed
        return {"version": "1.0", "users": {}}

    def save_exclusions(self, excluded_repos: list[str]) -> bool:
        """Save exclusions for current user to JSON file.

        Args:
            excluded_repos: List of repository names to exclude

        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            # Load current exclusions
            exclusions = self.get_exclusions()

            # Update exclusions for current user
            user_name: str = self.get_current_user_name()
            if "users" not in exclusions:
                exclusions["users"] = {}

            exclusions["users"][user_name] = {"excluded_repos": excluded_repos}

            # Save to file
            exclusions_path: Path = self.get_exclusions_path()
            exclusions_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to temp file first (atomic write)
            temp_path: Path = exclusions_path.with_suffix(".json.tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(exclusions, f, indent=2)

            # Atomic rename
            temp_path.replace(exclusions_path)
            self._exclusions = exclusions  # Update cached exclusions
            return True

        except Exception as e:
            print(f"Error saving exclusions: {e}")
            return False

    def is_excluded(self, repo_name: str) -> bool:
        """Check if repository is excluded on current user.

        Args:
            repo_name: Repository name (not full path) to check

        Returns:
            bool: True if excluded, False otherwise
        """
        user_name: str = self.get_current_user_name()
        exclusions = self.get_exclusions()
        user_data = exclusions.get("users", {}).get(user_name, {})
        excluded_repos = user_data.get("excluded_repos", [])
        return repo_name in excluded_repos

    def get_excluded_repos(self) -> list[str]:
        """Get list of excluded repositories for current user.

        Returns:
            list[str]: List of excluded repository names
        """
        user_name: str = self.get_current_user_name()
        exclusions = self.get_exclusions()
        user_data = exclusions.get("users", {}).get(user_name, {})
        return user_data.get("excluded_repos", [])

    def add_exclusion(self, repo_name: str) -> bool:
        """Add repository to exclusion list for current user.

        Args:
            repo_name: Repository name to exclude

        Returns:
            bool: True if add successful, False otherwise
        """
        excluded_repos: list[str] = self.get_excluded_repos()
        if repo_name not in excluded_repos:
            excluded_repos.append(repo_name)
            return self.save_exclusions(excluded_repos)
        return True  # Already excluded

    def remove_exclusion(self, repo_name: str) -> bool:
        """Remove repository from exclusion list for current user.

        Args:
            repo_name: Repository name to remove from exclusions

        Returns:
            bool: True if remove successful, False otherwise
        """
        excluded_repos: list[str] = self.get_excluded_repos()
        if repo_name in excluded_repos:
            excluded_repos.remove(repo_name)
            return self.save_exclusions(excluded_repos)
        return True  # Already not excluded

    def get_current_user_name(self) -> str:
        """Get the current user's username.

        Returns:
            str: Username from getpass.getuser()
        """
        return getpass.getuser()

    def get_exclusions_path(self) -> Path:
        """Get the path to the exclusions JSON file.

        Returns:
            Path: Path to exclude_repositories.json in %appdata%\\GitUI\\
        """
        appdata = os.getenv("APPDATA")
        if not appdata:
            # Fallback for non-Windows or missing APPDATA
            appdata = str(Path.home() / "AppData" / "Roaming")
        return Path(appdata) / "GitUI" / "exclude_repositories.json"
