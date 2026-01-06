# ----- Build-In Modules -----
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

# ----- PyQt6 Modules -----
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal


@dataclass
class PullResult:
    """Data class for pull operation result."""

    status: str  # "SUCCESS", "CONFLICT", "ERROR", "MISSING"
    repo_name: str
    repo_path: str
    error_message: str = ""
    conflict_files: list[str] = None

    def __post_init__(self):
        if self.conflict_files is None:
            self.conflict_files = []


class GitPullWorker(QRunnable):
    """Worker to run git pull on a single repository."""

    class Signals(QObject):
        finished = pyqtSignal(object)  # emits PullResult
        error = pyqtSignal(str)  # emits error message
        conflict_detected = pyqtSignal(str, str)  # emits (repo_name, repo_path)

    def __init__(self, repo_name: str, repo_path: str) -> None:
        super().__init__()
        self.repo_name: str = repo_name
        self.repo_path: str = repo_path
        self.signals = self.Signals()
        self._is_running = True

    def _safe_emit_finished(self, result: PullResult) -> None:
        """Safely emit finished signal."""
        try:
            if self._is_running and hasattr(self, "signals") and self.signals:
                self.signals.finished.emit(result)
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

    def _safe_emit_conflict(self, repo_name: str, repo_path: str) -> None:
        """Safely emit conflict detected signal."""
        try:
            if self._is_running and hasattr(self, "signals") and self.signals:
                self.signals.conflict_detected.emit(repo_name, repo_path)
        except RuntimeError:
            # Signals object was deleted, application is closing
            self._is_running = False

    def run(self) -> None:
        """Execute git pull operation."""
        if not self._is_running:
            return

        # PowerShell script for git pull with stash/pop logic
        ps_command = f"""
            $ErrorActionPreference = "Stop"
            $repoPath = '{self.repo_path}'
            $repoName = '{self.repo_name}'

            # Check if repository exists
            if (-not (Test-Path -LiteralPath $repoPath)) {{
                [PSCustomObject]@{{
                    Status = "MISSING"
                    RepoName = $repoName
                    ErrorMessage = "Repository path does not exist"
                }} | ConvertTo-Json -Compress
                exit 0
            }}

            try {{
                Set-Location -LiteralPath $repoPath

                # Attempt pull
                $pullOutput = git pull 2>&1 | Out-String

                if ($LASTEXITCODE -eq 0) {{
                    # Success on first attempt
                    [PSCustomObject]@{{
                        Status = "SUCCESS"
                        RepoName = $repoName
                    }} | ConvertTo-Json -Compress
                    exit 0
                }}

                # Check if failure is due to local changes
                if ($pullOutput -match "error: Your local changes|would be overwritten|Please commit your changes or stash them") {{
                    # Stash local changes
                    $stashOutput = git stash push -m "Auto-stash $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" 2>&1 | Out-String

                    if ($LASTEXITCODE -ne 0) {{
                        [PSCustomObject]@{{
                            Status = "ERROR"
                            RepoName = $repoName
                            ErrorMessage = "Failed to stash changes: $stashOutput"
                        }} | ConvertTo-Json -Compress
                        exit 0
                    }}

                    # Retry pull
                    $pullOutput = git pull 2>&1 | Out-String

                    if ($LASTEXITCODE -ne 0) {{
                        [PSCustomObject]@{{
                            Status = "ERROR"
                            RepoName = $repoName
                            ErrorMessage = "Pull failed after stashing: $pullOutput"
                        }} | ConvertTo-Json -Compress
                        exit 0
                    }}

                    # Restore stashed changes
                    $popOutput = git stash pop 2>&1 | Out-String

                    if ($LASTEXITCODE -ne 0) {{
                        # Check for merge conflicts
                        $status = git status --porcelain 2>&1
                        if ($status -match "^(UU|AA|DD) ") {{
                            # Extract conflict files
                            $conflictFiles = git diff --name-only --diff-filter=U 2>&1 | Out-String
                            $filesArray = $conflictFiles -split "`n" | Where-Object {{ $_ -ne "" }}

                            [PSCustomObject]@{{
                                Status = "CONFLICT"
                                RepoName = $repoName
                                ErrorMessage = "Merge conflicts detected"
                                ConflictFiles = $filesArray
                            }} | ConvertTo-Json -Compress
                            exit 0
                        }}

                        [PSCustomObject]@{{
                            Status = "ERROR"
                            RepoName = $repoName
                            ErrorMessage = "Failed to restore stash: $popOutput"
                        }} | ConvertTo-Json -Compress
                        exit 0
                    }}

                    # Success after stash/pop
                    [PSCustomObject]@{{
                        Status = "SUCCESS"
                        RepoName = $repoName
                    }} | ConvertTo-Json -Compress
                    exit 0
                }} else {{
                    # Other error
                    [PSCustomObject]@{{
                        Status = "ERROR"
                        RepoName = $repoName
                        ErrorMessage = $pullOutput
                    }} | ConvertTo-Json -Compress
                    exit 0
                }}
            }} catch {{
                [PSCustomObject]@{{
                    Status = "ERROR"
                    RepoName = $repoName
                    ErrorMessage = $_.Exception.Message
                }} | ConvertTo-Json -Compress
                exit 0
            }}
        """

        try:
            result = subprocess.run(
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
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            if not self._is_running:
                return

            # Parse JSON output
            output = result.stdout.strip()
            if not output:
                self._safe_emit_finished(
                    PullResult(
                        status="ERROR",
                        repo_name=self.repo_name,
                        repo_path=self.repo_path,
                        error_message="No output from PowerShell script",
                    )
                )
                return

            data = json.loads(output)

            pull_result = PullResult(
                status=data.get("Status", "ERROR"),
                repo_name=data.get("RepoName", self.repo_name),
                repo_path=self.repo_path,
                error_message=data.get("ErrorMessage", ""),
                conflict_files=data.get("ConflictFiles", []),
            )

            # If conflict detected, emit special signal
            if pull_result.status == "CONFLICT":
                self._safe_emit_conflict(self.repo_name, self.repo_path)

            self._safe_emit_finished(pull_result)

        except subprocess.TimeoutExpired:
            self._safe_emit_finished(
                PullResult(
                    status="ERROR",
                    repo_name=self.repo_name,
                    repo_path=self.repo_path,
                    error_message="Operation timed out",
                )
            )
        except json.JSONDecodeError as e:
            self._safe_emit_finished(
                PullResult(
                    status="ERROR",
                    repo_name=self.repo_name,
                    repo_path=self.repo_path,
                    error_message=f"Failed to parse result: {str(e)}",
                )
            )
        except Exception as e:
            self._safe_emit_finished(
                PullResult(
                    status="ERROR",
                    repo_name=self.repo_name,
                    repo_path=self.repo_path,
                    error_message=f"Unexpected error: {str(e)}",
                )
            )

    def stop(self) -> None:
        """Stop the worker gracefully."""
        self._is_running = False
