# ----- Build-In Modules -----
import json
import subprocess
import time
from abc import abstractmethod
from pathlib import Path

# ----- PyQt6 Modules -----
from PyQt6.QtCore import QObject, QRunnable


class BaseWorker(QRunnable):
    """Abstract base class for all QRunnable workers.

    Provides common infrastructure including:
    - Signal safety patterns with RuntimeError handling
    - Graceful shutdown via stop() method and _is_running flag
    - PowerShell subprocess execution with standard configuration
    - Template method run() with comprehensive error handling
    - Abstract methods for subclasses to implement operation-specific logic
    """

    def __init__(self) -> None:
        super().__init__()
        self._is_running = True
        self.signals = self._create_signals()

    @abstractmethod
    def _create_signals(self) -> QObject:
        """Create and return the Signals object for this worker."""
        pass

    @abstractmethod
    def _get_powershell_command(self) -> str:
        """Return the PowerShell command to execute."""
        pass

    @abstractmethod
    def _parse_result(self, output: str, duration: float):
        """Parse subprocess output and return appropriate result."""
        pass

    @abstractmethod
    def _get_timeout(self) -> int:
        """Return timeout in seconds for subprocess."""
        pass

    @abstractmethod
    def _get_error_result(self, error_message: str, duration: float):
        """Return appropriate error result object."""
        pass

    def _use_no_window(self) -> bool:
        """Override to use CREATE_NO_WINDOW flag.

        Returns:
            bool: False by default. Override to return True for silent execution.
        """
        return False

    def _safe_emit(self, signal, *args) -> None:
        """Generic safe signal emission with RuntimeError handling.

        Args:
            signal: The pyqtSignal to emit
            *args: Arguments to pass to the signal
        """
        try:
            if self._is_running and hasattr(self, "signals") and self.signals:
                signal.emit(*args)
        except RuntimeError:
            # Signals object was deleted, application is closing
            self._is_running = False

    def _safe_emit_finished(self, result) -> None:
        """Safely emit finished signal.

        Args:
            result: The result object to emit
        """
        self._safe_emit(self.signals.finished, result)

    def _safe_emit_error(self, message: str) -> None:
        """Safely emit error signal.

        Args:
            message: Error message string
        """
        self._safe_emit(self.signals.error, message)

    def _run_powershell(
        self, command: str, timeout: int, use_create_no_window: bool = False
    ) -> subprocess.CompletedProcess:
        """Execute PowerShell command with standard configuration.

        Args:
            command: PowerShell command string to execute
            timeout: Timeout in seconds
            use_create_no_window: Whether to use CREATE_NO_WINDOW flag

        Returns:
            subprocess.CompletedProcess: The completed process result
        """
        kwargs = {
            "capture_output": True,
            "text": True,
            "timeout": timeout,
        }

        if use_create_no_window:
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

        return subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                command,
            ],
            **kwargs,
        )

    def run(self) -> None:
        """Execute the worker operation.

        Template method that handles the common execution flow:
        1. Get PowerShell command from subclass
        2. Execute PowerShell subprocess
        3. Parse result via subclass
        4. Handle errors (TimeoutExpired, JSONDecodeError, Exception)
        """
        start_time: float = time.time()

        try:
            if not self._is_running:
                return

            # Template method: subclasses provide command
            command: str = self._get_powershell_command()
            timeout: int = self._get_timeout()

            # Execute PowerShell
            result = self._run_powershell(
                command, timeout, use_create_no_window=self._use_no_window()
            )

            duration: float = time.time() - start_time

            if not self._is_running:
                return

            if result.returncode != 0:
                self._safe_emit_error(f"PowerShell error: {result.stderr[:200]}")
                self._safe_emit_finished(self._get_error_result("", duration))
                return

            # Template method: subclasses parse output
            output = result.stdout.strip()
            parsed_result = self._parse_result(output, duration)
            self._safe_emit_finished(parsed_result)

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self._safe_emit_error("Timeout: Operation took too long")
            self._safe_emit_finished(self._get_error_result("Timeout", duration))
        except json.JSONDecodeError as e:
            duration = time.time() - start_time
            self._safe_emit_error(f"Failed to parse results: {str(e)}")
            self._safe_emit_finished(self._get_error_result("Parse error", duration))
        except Exception as e:
            duration = time.time() - start_time
            self._safe_emit_error(f"Unexpected error: {str(e)[:200]}")
            self._safe_emit_finished(self._get_error_result(str(e), duration))

    def stop(self) -> None:
        """Stop the worker gracefully."""
        self._is_running = False


class BaseScannerWorker(BaseWorker):
    """Abstract base class for scanner workers.

    Extends BaseWorker with scanner-specific patterns:
    - Repository counting before scanning for progress tracking
    - JSON array parsing (handles empty results, single dict → array)
    - Progress signal emission
    - Returns ScanResult(repos=[], duration=X) on errors
    """

    def __init__(self, github_path: Path) -> None:
        self.github_path: Path = github_path
        super().__init__()

    def _safe_emit_progress(self, current: int, total: int) -> None:
        """Safely emit progress signal.

        Args:
            current: Current progress count
            total: Total items count
        """
        self._safe_emit(self.signals.progress, current, total)

    def _get_timeout(self) -> int:
        """Return scanner timeout (120 seconds)."""
        return 120

    def _count_repositories(self) -> int:
        """Count total git repositories in github_path.

        Returns:
            int: Number of git repositories found
        """
        count_command: str = f"""
            $githubPath = '{self.github_path}'
            $repositories = Get-ChildItem -Path $githubPath -Directory |
                            Where-Object {{ Test-Path "$($_.FullName)\\.git" }}
            $repositories.Count
            """

        try:
            result = self._run_powershell(count_command, timeout=10)
            return int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
        except Exception:
            return 0

    def run(self) -> None:
        """Execute scanner with progress tracking.

        Overrides BaseWorker.run() to add repository counting
        before executing the main scanning operation.
        """
        # Count repos first for progress tracking
        total_repos = self._count_repositories()
        self._safe_emit_progress(0, total_repos)

        if not self._is_running:
            return

        # Call parent run() for main execution
        super().run()

    @abstractmethod
    def _create_repo_status(self, item: dict):
        """Create RepoStatus from JSON item.

        Args:
            item: Dictionary from JSON parsing

        Returns:
            RepoStatus: Appropriate RepoStatus dataclass instance
        """
        pass

    def _parse_result(self, output: str, duration: float):
        """Parse JSON array into ScanResult.

        Args:
            output: JSON string output from PowerShell
            duration: Execution duration in seconds

        Returns:
            ScanResult: Scan result with repos list and duration
        """
        # Import here to avoid circular dependency
        from scanners.git_pull_scanner import ScanResult

        if not output or output == "[]":
            return ScanResult(repos=[], duration=duration)

        # Handle both single object and array
        data = json.loads(output)
        if isinstance(data, dict):
            data = [data]

        # Convert to RepoStatus objects using subclass method
        repos = [self._create_repo_status(item) for item in data]
        return ScanResult(repos=repos, duration=duration)

    def _get_error_result(self, error_message: str, duration: float):
        """Return empty ScanResult.

        Args:
            error_message: Error message (unused for scanners)
            duration: Execution duration in seconds

        Returns:
            ScanResult: Empty scan result
        """
        # Import here to avoid circular dependency
        from scanners.git_pull_scanner import ScanResult

        return ScanResult(repos=[], duration=duration)


class BaseOperationWorker(BaseWorker):
    """Abstract base class for operation workers (pull/push).

    Extends BaseWorker with operation-specific patterns:
    - Repository existence validation
    - CREATE_NO_WINDOW flag for silent execution
    - JSON single-object parsing
    - Returns typed result objects (PullResult/PushResult)
    """

    def __init__(self, repo_name: str, repo_path: str) -> None:
        self.repo_name: str = repo_name
        self.repo_path: str = repo_path
        super().__init__()

    def _get_timeout(self) -> int:
        """Return operation timeout (120 seconds)."""
        return 120

    def _use_no_window(self) -> bool:
        """All operation workers use CREATE_NO_WINDOW."""
        return True

    @abstractmethod
    def _create_result_from_data(self, data: dict):
        """Create result object from parsed JSON.

        Args:
            data: Dictionary from JSON parsing

        Returns:
            Result object (PullResult or PushResult)
        """
        pass

    def _parse_result(self, output: str, duration: float):
        """Parse JSON into operation result.

        Args:
            output: JSON string output from PowerShell
            duration: Execution duration in seconds

        Returns:
            Result object created by subclass
        """
        if not output:
            return self._get_error_result("No output from PowerShell script", duration)

        data = json.loads(output)
        return self._create_result_from_data(data)
