# ----- Built-In Modules -----
import json
import os
from datetime import datetime, timedelta
from pathlib import Path


class LogManager:
    """Singleton for managing operation logs per repository.

    Logs are stored in %APPDATA%/GitUI/log/<repo-name>/ with timestamped
    log files: pull-YYYY-MM-DD-HH-MM-SS.log and push-YYYY-MM-DD-HH-MM-SS.log
    """

    _instance = None

    def __new__(cls):
        """Ensure only one instance of LogManager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_log_directory(self) -> Path:
        """Get the base log directory path.

        Returns:
            Path: Path to %APPDATA%/GitUI/log/
        """
        appdata = os.getenv("APPDATA")
        if not appdata:
            appdata = str(Path.home() / "AppData" / "Roaming")
        return Path(appdata) / "GitUI" / "log"

    def _sanitize_repo_name(self, repo_name: str) -> str:
        """Sanitize repo name for use as folder name.

        Args:
            repo_name: Repository name to sanitize

        Returns:
            str: Sanitized name safe for use as folder name
        """
        invalid_chars = '<>:"/\\|?*'
        sanitized: str = repo_name
        for char in invalid_chars:
            sanitized = sanitized.replace(char, "_")
        return sanitized

    def _get_timestamp_filename(self, operation: str) -> str:
        """Generate timestamped filename for log.

        Args:
            operation: 'pull' or 'push'

        Returns:
            str: Filename like 'pull-2024-01-11-10-30-45.log'
        """
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        return f"{operation}-{timestamp}.log"

    def get_repo_log_directory(self, repo_name: str) -> Path:
        """Get the log directory for a specific repository.

        Args:
            repo_name: Name of the repository

        Returns:
            Path: Path to repository's log directory
        """
        return self.get_log_directory() / self._sanitize_repo_name(repo_name)

    def get_pull_log_path(self, repo_name: str) -> Path:
        """Get path to timestamped pull log for repository.

        Args:
            repo_name: Name of the repository

        Returns:
            Path: Path to pull log file with timestamp
        """
        return self.get_repo_log_directory(repo_name) / self._get_timestamp_filename(
            "pull"
        )

    def get_push_log_path(self, repo_name: str) -> Path:
        """Get path to timestamped push log for repository.

        Args:
            repo_name: Name of the repository

        Returns:
            Path: Path to push log file with timestamp
        """
        return self.get_repo_log_directory(repo_name) / self._get_timestamp_filename(
            "push"
        )

    def log_pull_operation(self, result) -> bool:
        """Log a pull operation result.

        Args:
            result: PullResult object with status, repo_name, error_message,
                   warnings, and conflict_files

        Returns:
            bool: True if logging succeeded
        """
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": result.status,
            "error_message": result.error_message,
            "warnings": result.warnings if hasattr(result, "warnings") else [],
            "conflict_files": result.conflict_files or [],
        }
        return self._write_log_entry(self.get_pull_log_path(result.repo_name), entry)

    def log_push_operation(self, result, commit_prefix: str = "") -> bool:
        """Log a push operation result.

        Args:
            result: PushResult object with status, repo_name, error_message,
                   warnings, and is_excluded
            commit_prefix: The commit prefix used (e.g., "Shutdown")

        Returns:
            bool: True if logging succeeded
        """
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": result.status,
            "error_message": result.error_message,
            "warnings": result.warnings if hasattr(result, "warnings") else [],
            "is_excluded": result.is_excluded,
            "commit_prefix": commit_prefix,
        }
        return self._write_log_entry(self.get_push_log_path(result.repo_name), entry)

    def log_test_pull_operation(self, repo_name: str, status: str = "SUCCESS") -> bool:
        """Log a test pull operation for test mode.

        Args:
            repo_name: Name of the repository
            status: Operation status (default: SUCCESS)

        Returns:
            bool: True if logging succeeded
        """
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
            "error_message": "",
            "warnings": ["Test mode - no actual operation performed"],
            "conflict_files": [],
        }
        return self._write_log_entry(self.get_pull_log_path(repo_name), entry)

    def log_test_push_operation(
        self, repo_name: str, status: str = "SUCCESS", commit_prefix: str = "Shutdown"
    ) -> bool:
        """Log a test push operation for test mode.

        Args:
            repo_name: Name of the repository
            status: Operation status (default: SUCCESS)
            commit_prefix: The commit prefix used (default: Shutdown)

        Returns:
            bool: True if logging succeeded
        """
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
            "error_message": "",
            "warnings": ["Test mode - no actual operation performed"],
            "is_excluded": False,
            "commit_prefix": commit_prefix,
        }
        return self._write_log_entry(self.get_push_log_path(repo_name), entry)

    def _write_log_entry(self, log_path: Path, entry: dict) -> bool:
        """Write a log entry to file.

        Args:
            log_path: Path to log file
            entry: Log entry dictionary

        Returns:
            bool: True if write succeeded
        """
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(entry, indent=4))
            return True
        except Exception as e:
            print(f"Error writing log: {e}")
            return False

    def clear_logs(self, days: int | None = None) -> tuple[bool, int, str]:
        """Clear log files, optionally only those older than specified days.

        Args:
            days: If provided, only delete logs older than this many days.
                  If None, delete all logs.

        Returns:
            tuple: (success, files_deleted, error_message)
                - success: True if logs were cleared successfully
                - files_deleted: Number of log files deleted
                - error_message: Error description if failed, empty string if success
        """
        import shutil

        log_dir = self.get_log_directory()
        files_deleted = 0

        if not log_dir.exists():
            return True, 0, ""

        try:
            if days is None:
                # Clear all logs
                for repo_dir in log_dir.iterdir():
                    if repo_dir.is_dir():
                        for log_file in repo_dir.iterdir():
                            if log_file.is_file():
                                files_deleted += 1

                # Remove the entire log directory and recreate it empty
                shutil.rmtree(log_dir)
                log_dir.mkdir(parents=True, exist_ok=True)
            else:
                # Clear logs older than specified days
                cutoff_date = datetime.now() - timedelta(days=days)

                for repo_dir in log_dir.iterdir():
                    if repo_dir.is_dir():
                        for log_file in repo_dir.iterdir():
                            if log_file.is_file():
                                # Get file modification time
                                file_mtime = datetime.fromtimestamp(
                                    log_file.stat().st_mtime
                                )
                                if file_mtime < cutoff_date:
                                    log_file.unlink()
                                    files_deleted += 1

                        # Remove empty repo directories
                        if not any(repo_dir.iterdir()):
                            repo_dir.rmdir()

            return True, files_deleted, ""
        except PermissionError as e:
            return False, 0, f"Permission denied: {e}"
        except Exception as e:
            return False, 0, f"Error clearing logs: {e}"

    def get_log_stats_by_age(self, days: int) -> dict:
        """Get statistics about logs older than specified days.

        Args:
            days: Number of days threshold

        Returns:
            dict: Statistics including total_files, total_size_bytes, repo_count
                  for logs older than the specified days
        """
        log_dir = self.get_log_directory()
        stats = {
            "total_files": 0,
            "total_size_bytes": 0,
            "repo_count": 0,
        }

        if not log_dir.exists():
            return stats

        cutoff_date = datetime.now() - timedelta(days=days)
        repos_with_old_logs: set[str] = set()

        try:
            for repo_dir in log_dir.iterdir():
                if repo_dir.is_dir():
                    for log_file in repo_dir.iterdir():
                        if log_file.is_file():
                            file_mtime = datetime.fromtimestamp(
                                log_file.stat().st_mtime
                            )
                            if file_mtime < cutoff_date:
                                stats["total_files"] += 1
                                stats["total_size_bytes"] += log_file.stat().st_size
                                repos_with_old_logs.add(repo_dir.name)

            stats["repo_count"] = len(repos_with_old_logs)
        except Exception:
            pass

        return stats

    def get_log_stats(self) -> dict:
        """Get statistics about the log directory.

        Returns:
            dict: Statistics including total_files, total_size_bytes, repo_count
        """
        log_dir = self.get_log_directory()
        stats = {
            "total_files": 0,
            "total_size_bytes": 0,
            "repo_count": 0,
        }

        if not log_dir.exists():
            return stats

        try:
            for repo_dir in log_dir.iterdir():
                if repo_dir.is_dir():
                    stats["repo_count"] += 1
                    for log_file in repo_dir.iterdir():
                        if log_file.is_file():
                            stats["total_files"] += 1
                            stats["total_size_bytes"] += log_file.stat().st_size
        except Exception:
            pass

        return stats
