# ----- Build-In Modules -----
from dataclasses import dataclass

# ----- PyQt6 Modules -----
from PyQt6.QtCore import QObject, pyqtSignal

# ----- Local Modules -----
from base.base_worker import BaseOperationWorker


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


class GitPullWorker(BaseOperationWorker):
    """Worker to run git pull on a single repository."""

    class Signals(QObject):
        finished = pyqtSignal(object)  # emits PullResult
        error = pyqtSignal(str)  # emits error message
        conflict_detected = pyqtSignal(str, str)  # emits (repo_name, repo_path)

    def _create_signals(self) -> QObject:
        """Create and return the Signals object for this worker."""
        return self.Signals()

    def _safe_emit_conflict(self, repo_name: str, repo_path: str) -> None:
        """Safely emit conflict detected signal.

        Args:
            repo_name: Name of repository with conflict
            repo_path: Path to repository with conflict
        """
        self._safe_emit(self.signals.conflict_detected, repo_name, repo_path)

    def _get_powershell_command(self) -> str:
        """Return the PowerShell command to execute."""
        return f"""
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

    def _create_result_from_data(self, data: dict) -> PullResult:
        """Create result object from parsed JSON.

        Args:
            data: Dictionary from JSON parsing

        Returns:
            PullResult: Pull operation result
        """
        result = PullResult(
            status=data.get("Status", "ERROR"),
            repo_name=data.get("RepoName", self.repo_name),
            repo_path=self.repo_path,
            error_message=data.get("ErrorMessage", ""),
            conflict_files=data.get("ConflictFiles", []),
        )

        # If conflict detected, emit special signal
        if result.status == "CONFLICT":
            self._safe_emit_conflict(self.repo_name, self.repo_path)

        return result

    def _get_error_result(self, error_message: str, duration: float) -> PullResult:
        """Return error PullResult.

        Args:
            error_message: Error message string
            duration: Execution duration (unused for operation workers)

        Returns:
            PullResult: Error result
        """
        return PullResult(
            status="ERROR",
            repo_name=self.repo_name,
            repo_path=self.repo_path,
            error_message=error_message,
        )
