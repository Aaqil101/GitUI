# ----- Build-In Modules -----
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

# ----- PyQt6 Modules -----
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal


@dataclass
class RepoStatus:
    """Data class for repository status."""

    name: str
    path: str
    behind: int


@dataclass
class ScanResult:
    """Data class for scan results."""

    repos: list[RepoStatus]
    duration: float


class PowerShellScannerWorker(QRunnable):
    """Worker to run PowerShell repository scanner."""

    class Signals(QObject):
        finished = pyqtSignal(object)  # emits ScanResult
        error = pyqtSignal(str)  # emits error message
        progress = pyqtSignal(int, int)  # emits (current, total)

    def __init__(self, github_path: Path) -> None:
        super().__init__()
        self.github_path: Path = github_path
        self.signals = self.Signals()
        self._is_running = True

    def _safe_emit_progress(self, current: int, total: int) -> None:
        """Safely emit progress signal."""
        try:
            if self._is_running and hasattr(self, "signals") and self.signals:
                self.signals.progress.emit(current, total)
        except RuntimeError:
            # Signals object was deleted, application is closing
            self._is_running = False

    def _safe_emit_error(self, message: str) -> None:
        """Safely emit error signal."""
        try:
            if self._is_running and hasattr(self, "signals") and self.signals:
                self.signals.error.emit(message)
        except RuntimeError:
            # Signals object was deleted, application is closing
            self._is_running = False

    def _safe_emit_finished(self, result: ScanResult) -> None:
        """Safely emit finished signal."""
        try:
            if self._is_running and hasattr(self, "signals") and self.signals:
                self.signals.finished.emit(result)
        except RuntimeError:
            # Signals object was deleted, application is closing
            self._is_running = False

    def run(self) -> None:
        """Execute PowerShell script to check for updates."""
        import time

        start_time: float = time.time()

        try:
            # First, count total repositories
            count_command: str = f"""
                $githubPath = '{self.github_path}'
                $repositories = Get-ChildItem -Path $githubPath -Directory |
                                Where-Object {{ Test-Path "$($_.FullName)\\.git" }}
                $repositories.Count
                """
            count_result: subprocess.CompletedProcess[str] = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    count_command,
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            total_repos: int = (
                int(count_result.stdout.strip())
                if count_result.stdout.strip().isdigit()
                else 0
            )
            self._safe_emit_progress(0, total_repos)

            if not self._is_running:
                return

            # PowerShell command to run the check function
            ps_command: str = f"""
                $githubPath = '{self.github_path}'

                # Pre-filter git repos
                $repositories = Get-ChildItem -Path $githubPath -Directory |
                                Where-Object {{ Test-Path "$($_.FullName)\\.git" }}

                $total = $repositories.Count
                $completed = 0

                # Parallel processing
                $results = $repositories | ForEach-Object -Parallel {{
                    $repoPath = $_.FullName
                    $repoName = $_.Name

                    # Fetch updates
                    $null = git -C $repoPath fetch --quiet 2>&1

                    # Get upstream branch and check commits behind
                    $upstream = git -C $repoPath rev-parse --abbrev-ref '@{{upstream}}' 2>$null

                    if ($LASTEXITCODE -eq 0 -and $upstream) {{
                        $behind = git -C $repoPath rev-list --count "HEAD..$upstream" 2>$null

                        if ($LASTEXITCODE -eq 0 -and $behind -and [int]$behind -gt 0) {{
                            [PSCustomObject]@{{
                                Name = $repoName
                                Path = $repoPath
                                Behind = [int]$behind
                            }}
                        }}
                    }}
                }} -ThrottleLimit 30

                # Output as JSON
                if ($results) {{
                    $results | ConvertTo-Json -Compress
                }} else {{
                    '[]'
                }}
                """

            result: subprocess.CompletedProcess[str] = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    ps_command,
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            duration: float = time.time() - start_time

            if not self._is_running:
                return

            if result.returncode != 0:
                self._safe_emit_error(f"PowerShell error: {result.stderr[:200]}")
                self._safe_emit_finished(ScanResult(repos=[], duration=duration))
                return

            # Parse JSON output
            output: str = result.stdout.strip()
            if not output or output == "[]":
                self._safe_emit_finished(ScanResult(repos=[], duration=duration))
                return

            # Handle both single object and array
            data = json.loads(output)
            if isinstance(data, dict):
                data = [data]

            # Convert to RepoStatus objects
            repos: list[RepoStatus] = [
                RepoStatus(name=item["Name"], path=item["Path"], behind=item["Behind"])
                for item in data
            ]

            self._safe_emit_finished(ScanResult(repos=repos, duration=duration))

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self._safe_emit_error("Timeout: Repository scan took too long")
            self._safe_emit_finished(ScanResult(repos=[], duration=duration))
        except json.JSONDecodeError as e:
            duration = time.time() - start_time
            self._safe_emit_error(f"Failed to parse results: {str(e)}")
            self._safe_emit_finished(ScanResult(repos=[], duration=duration))
        except Exception as e:
            duration = time.time() - start_time
            self._safe_emit_error(f"Unexpected error: {str(e)[:200]}")
            self._safe_emit_finished(ScanResult(repos=[], duration=duration))

    def stop(self) -> None:
        """Stop the worker gracefully."""
        self._is_running = False
