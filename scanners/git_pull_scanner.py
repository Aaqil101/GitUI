# ----- Build-In Modules -----
from dataclasses import dataclass
from pathlib import Path

# ----- PyQt6 Modules -----
from PyQt6.QtCore import QObject, pyqtSignal

# ----- Local Modules -----
from base.base_worker import BaseScannerWorker


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


class PowerShellScannerWorker(BaseScannerWorker):
    """Worker to run PowerShell repository scanner."""

    class Signals(QObject):
        finished = pyqtSignal(object)  # emits ScanResult
        error = pyqtSignal(str)  # emits error message
        progress = pyqtSignal(int, int)  # emits (current, total)

    def _create_signals(self) -> QObject:
        """Create and return the Signals object for this worker."""
        return self.Signals()

    def _get_powershell_command(self) -> str:
        """Return the PowerShell command to execute."""
        # Get all scan paths (GitHub + custom)
        from core.custom_paths_manager import CustomPathsManager

        custom_paths_mgr = CustomPathsManager()
        all_paths = custom_paths_mgr.get_all_scan_paths()

        # Build PowerShell array of paths
        paths_array = ", ".join([f'"{p}"' for p in all_paths])

        return f"""
            $scanPaths = @({paths_array})

            # Pre-filter git repos from all scan paths
            $repositories = $scanPaths | ForEach-Object {{
                if (Test-Path $_) {{
                    Get-ChildItem -Path $_ -Directory -ErrorAction SilentlyContinue |
                        Where-Object {{ Test-Path "$($_.FullName)\\.git" }}
                }}
            }}

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

    def _create_repo_status(self, item: dict) -> RepoStatus:
        """Create RepoStatus from JSON item.

        Args:
            item: Dictionary from JSON parsing

        Returns:
            RepoStatus: Repository status with name, path, and commits behind
        """
        return RepoStatus(name=item["Name"], path=item["Path"], behind=item["Behind"])
