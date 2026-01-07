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
    files_changed: int


@dataclass
class ScanResult:
    """Data class for scan results."""

    repos: list[RepoStatus]
    duration: float


class PowerShellScannerWorker(BaseScannerWorker):
    """Worker to run PowerShell repository scanner for uncommitted changes."""

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

                # Check git status for uncommitted changes
                $status = git -C $repoPath status --porcelain=1 -b 2>&1

                if ($LASTEXITCODE -eq 0 -and $status) {{
                    # Split into lines and filter out empty lines
                    $lines = $status -split "`n" | Where-Object {{ $_.Trim() }}

                    # First line is branch info, rest are changes
                    $fileCount = ($lines | Select-Object -Skip 1).Count

                    if ($fileCount -gt 0) {{
                        [PSCustomObject]@{{
                            Name = $repoName
                            Path = $repoPath
                            FilesChanged = [int]$fileCount
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
            RepoStatus: Repository status with name, path, and files changed
        """
        return RepoStatus(
            name=item["Name"], path=item["Path"], files_changed=item["FilesChanged"]
        )
