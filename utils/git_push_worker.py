# ----- Build-In Modules -----
import json
import subprocess
from dataclasses import dataclass

# ----- PyQt6 Modules -----
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal


@dataclass
class PushResult:
    """Data class for push operation result."""

    status: str  # "SUCCESS", "ERROR", "MISSING"
    repo_name: str
    repo_path: str
    error_message: str = ""


class GitPushWorker(QRunnable):
    """Worker to run git push on a single repository."""

    class Signals(QObject):
        finished = pyqtSignal(object)  # emits PushResult
        error = pyqtSignal(str)  # emits error message

    def __init__(self, repo_name: str, repo_path: str) -> None:
        super().__init__()
        self.repo_name: str = repo_name
        self.repo_path: str = repo_path
        self.signals = self.Signals()
        self._is_running = True

    def _safe_emit_finished(self, result: PushResult) -> None:
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

    def run(self) -> None:
        """Execute git push operation."""
        if not self._is_running:
            return

        # PowerShell script for git push (silent, no visual output)
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

                # Create commit message
                $commitTitle = "Shutdown commit by $currentUser on $timestamp"
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
                    PushResult(
                        status="ERROR",
                        repo_name=self.repo_name,
                        repo_path=self.repo_path,
                        error_message="No output from PowerShell script",
                    )
                )
                return

            data = json.loads(output)

            push_result = PushResult(
                status=data.get("Status", "ERROR"),
                repo_name=data.get("RepoName", self.repo_name),
                repo_path=self.repo_path,
                error_message=data.get("ErrorMessage", ""),
            )

            self._safe_emit_finished(push_result)

        except subprocess.TimeoutExpired:
            self._safe_emit_finished(
                PushResult(
                    status="ERROR",
                    repo_name=self.repo_name,
                    repo_path=self.repo_path,
                    error_message="Operation timed out",
                )
            )
        except json.JSONDecodeError as e:
            self._safe_emit_finished(
                PushResult(
                    status="ERROR",
                    repo_name=self.repo_name,
                    repo_path=self.repo_path,
                    error_message=f"Failed to parse result: {str(e)}",
                )
            )
        except Exception as e:
            self._safe_emit_finished(
                PushResult(
                    status="ERROR",
                    repo_name=self.repo_name,
                    repo_path=self.repo_path,
                    error_message=f"Unexpected error: {str(e)}",
                )
            )

    def stop(self) -> None:
        """Stop the worker gracefully."""
        self._is_running = False
