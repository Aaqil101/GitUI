# ----- Build-In Modules -----
from dataclasses import dataclass

# ----- PyQt6 Modules -----
from PyQt6.QtCore import QObject, pyqtSignal

# ----- Local Modules -----
from base.base_worker import BaseOperationWorker


@dataclass
class PushResult:
    """Data class for push operation result."""

    status: str  # "SUCCESS", "ERROR", "MISSING", "SKIPPED", "CANCELLED"
    repo_name: str
    repo_path: str
    error_message: str = ""
    is_excluded: bool = False  # True if repo is excluded


class GitPushWorker(BaseOperationWorker):
    """Worker to run git push on a single repository."""

    class Signals(QObject):
        finished = pyqtSignal(object)  # emits PushResult
        error = pyqtSignal(str)  # emits error message

    def __init__(
        self, repo_name: str, repo_path: str, commit_prefix: str = "Shutdown"
    ) -> None:
        """Initialize GitPushWorker with custom commit prefix.

        Args:
            repo_name: Name of repository
            repo_path: Absolute path to repository
            commit_prefix: Commit message prefix (e.g., "Shutdown", "Restart")
        """
        self.commit_prefix = commit_prefix
        super().__init__(repo_name, repo_path)

    def _create_signals(self) -> QObject:
        """Create and return the Signals object for this worker."""
        return self.Signals()

    def _get_powershell_command(self) -> str:
        """Return the PowerShell command to execute."""
        return f"""
            $ErrorActionPreference = "Stop"
            $repoPath = '{self.repo_path}'
            $repoName = '{self.repo_name}'
            $commitPrefix = '{self.commit_prefix}'

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

                # Check for uncommitted changes
                $gitStatus = git status --porcelain 2>&1

                if (-not $gitStatus) {{
                    # No changes, repository is clean
                    [PSCustomObject]@{{
                        Status = "SUCCESS"
                        RepoName = $repoName
                        ErrorMessage = "No changes to commit"
                    }} | ConvertTo-Json -Compress
                    exit 0
                }}

                # Stage all changes
                $null = git add . 2>&1
                if ($LASTEXITCODE -ne 0) {{
                    [PSCustomObject]@{{
                        Status = "ERROR"
                        RepoName = $repoName
                        ErrorMessage = "Failed to stage changes"
                    }} | ConvertTo-Json -Compress
                    exit 0
                }}

                # Get current timestamp and user
                $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                $currentUser = $env:USERNAME

                # Get list of changed files
                $changes = git status --porcelain
                $modifiedFiles = @()

                foreach ($change in $changes) {{
                    $status = $change.Substring(0, 2).Trim()
                    $file = $change.Substring(3)

                    $changeType = switch ($status) {{
                        'M' {{ 'Modified' }}
                        'A' {{ 'Added' }}
                        'D' {{ 'Deleted' }}
                        'R' {{ 'Renamed' }}
                        'C' {{ 'Copied' }}
                        'U' {{ 'Updated' }}
                        '??' {{ 'Untracked' }}
                        default {{ $status }}
                    }}

                    $modifiedFiles += "- ${{changeType}}: $file"
                }}

                # Create commit message with dynamic prefix
                $commitTitle = "$commitPrefix commit by $currentUser on $timestamp"
                $commitBody = "Changed files:`n" + ($modifiedFiles -join "`n")
                $commitMessage = "$commitTitle`n`n$commitBody"

                # Save commit message to temp file
                $tempFile = [System.IO.Path]::GetTempFileName()
                $commitMessage | Out-File -FilePath $tempFile -Encoding UTF8

                # Commit changes
                $null = git commit -F $tempFile 2>&1
                if ($LASTEXITCODE -ne 0) {{
                    Remove-Item -Path $tempFile -Force -ErrorAction SilentlyContinue
                    [PSCustomObject]@{{
                        Status = "ERROR"
                        RepoName = $repoName
                        ErrorMessage = "Failed to commit changes"
                    }} | ConvertTo-Json -Compress
                    exit 0
                }}

                # Clean up temp file
                Remove-Item -Path $tempFile -Force -ErrorAction SilentlyContinue

                # Push changes
                $pushOutput = git push 2>&1 | Out-String
                if ($LASTEXITCODE -ne 0) {{
                    [PSCustomObject]@{{
                        Status = "ERROR"
                        RepoName = $repoName
                        ErrorMessage = "Failed to push: $pushOutput"
                    }} | ConvertTo-Json -Compress
                    exit 0
                }}

                # Success
                [PSCustomObject]@{{
                    Status = "SUCCESS"
                    RepoName = $repoName
                }} | ConvertTo-Json -Compress
                exit 0

            }} catch {{
                [PSCustomObject]@{{
                    Status = "ERROR"
                    RepoName = $repoName
                    ErrorMessage = $_.Exception.Message
                }} | ConvertTo-Json -Compress
                exit 0
            }}
        """

    def _create_result_from_data(self, data: dict) -> PushResult:
        """Create result object from parsed JSON.

        Args:
            data: Dictionary from JSON parsing

        Returns:
            PushResult: Push operation result
        """
        return PushResult(
            status=data.get("Status", "ERROR"),
            repo_name=data.get("RepoName", self.repo_name),
            repo_path=self.repo_path,
            error_message=data.get("ErrorMessage", ""),
        )

    def _get_error_result(self, error_message: str, duration: float) -> PushResult:
        """Return error PushResult.

        Args:
            error_message: Error message string
            duration: Execution duration (unused for operation workers)

        Returns:
            PushResult: Error result
        """
        return PushResult(
            status="ERROR",
            repo_name=self.repo_name,
            repo_path=self.repo_path,
            error_message=error_message,
        )
