# ----- Built-In Modules -----
import subprocess
from pathlib import Path

# ----- PyQt6 Modules -----
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMessageBox

# ----- Core Imports -----
from core.base_runner import BaseGitRunner
from core.config import (
    COLOR_GREEN,
    THEME_TEXT_DIM,
    OPERATIONS_START_DELAY,
    AUTO_CLOSE_DELAY,
    AUTO_CLOSE_NO_REPOS_DELAY,
)

# ----- Utils Imports -----
from utils.color import Color
from utils.icons import Icons

# ----- Workers Imports -----
from scanners.git_pull_scanner import PowerShellScannerWorker, RepoStatus, ScanResult
from workers.git_pull_worker import GitPullWorker, PullResult


class GitPullRunner(BaseGitRunner):
    """Git Pull Runner - handles pulling updates from repositories."""

    def _get_operation_config(self) -> dict:
        """Return pull-specific configuration."""
        return {
            "title": "Git Pull Runner",
            "icon": Icons.GIT_PULL,
            "header_text": "Repositories to Update",
            "stat_labels": {
                "repos": "Repos Behind",
                "items": "Commits to Pull",
                "operation_success": "Successfully Pulled",
            },
        }

    def _show_scan_summary(
        self, repos_count: int, items_count: int, total_scanned: int
    ) -> None:
        """Display pull-specific scan summary."""
        if repos_count > 0:
            self.summary_repos.setText(
                f"{Icons.GIT_BRANCH} {repos_count} repo{'s' if repos_count != 1 else ''} behind"
            )
            self.summary_repos.setStyleSheet("color: #7aa2f7; padding: 0;")
        else:
            self.summary_repos.setText(
                f"{Icons.GIT_BRANCH} {total_scanned} repos scanned"
            )
            self.summary_repos.setStyleSheet(f"color: {THEME_TEXT_DIM}; padding: 0;")

        if items_count > 0:
            self.summary_commits.setText(
                f"{Icons.GIT_COMMIT} {items_count} commit{'s' if items_count != 1 else ''} to pull"
            )
            self.summary_commits.setStyleSheet(f"color: {COLOR_GREEN}; padding: 0;")
        else:
            self.summary_commits.setText(f"{Icons.CHECK} All up to date")
            self.summary_commits.setStyleSheet(f"color: {THEME_TEXT_DIM}; padding: 0;")

        self.summary_widget.setVisible(True)
        self._update_stats(repos_count, items_count, total_scanned)

    def _update_stats(
        self, repos_count: int, items_count: int, total_scanned: int
    ) -> None:
        """Update stats panel with pull-specific values."""
        self.stat_scanned.findChild(QMessageBox, "value") or self.stat_scanned.findChildren(
            QMessageBox
        )
        # Find the value label by object name
        for widget in self.stat_scanned.findChildren(QMessageBox):
            if widget.objectName() == "value":
                widget.setText(str(total_scanned))
                break
        else:
            # Fallback: find by QLabel type
            from PyQt6.QtWidgets import QLabel

            value_labels = self.stat_scanned.findChildren(QLabel)
            if value_labels:
                value_labels[-1].setText(str(total_scanned))

        # Update other stats similarly
        for widget in self.stat_behind.findChildren(QMessageBox):
            if widget.objectName() == "value":
                widget.setText(str(repos_count))
                break
        else:
            from PyQt6.QtWidgets import QLabel

            value_labels = self.stat_behind.findChildren(QLabel)
            if value_labels:
                value_labels[-1].setText(str(repos_count))

        for widget in self.stat_commits.findChildren(QMessageBox):
            if widget.objectName() == "value":
                widget.setText(str(items_count))
                break
        else:
            from PyQt6.QtWidgets import QLabel

            value_labels = self.stat_commits.findChildren(QLabel)
            if value_labels:
                value_labels[-1].setText(str(items_count))

    def _update_operation_stats(self, success: int, failed: int) -> None:
        """Update pull operation stats."""
        from PyQt6.QtWidgets import QLabel

        success_labels = self.stat_success.findChildren(QLabel)
        if success_labels:
            success_labels[-1].setText(str(success))

        failed_labels = self.stat_failed.findChildren(QLabel)
        if failed_labels:
            failed_labels[-1].setText(str(failed))

    # ══════════════════════════════════════════════════════════════════
    # SCANNING
    # ══════════════════════════════════════════════════════════════════
    def _start_scan(self) -> None:
        """Start the pull scan."""
        super()._start_scan()

        self.worker = PowerShellScannerWorker(self.github_path)
        self.worker.signals.finished.connect(self._on_scan_finished)
        self.worker.signals.error.connect(self._on_scan_error)
        self.worker.signals.progress.connect(self._on_progress_update)
        self.threadpool.start(self.worker)

    def _on_scan_finished(self, result: ScanResult) -> None:
        """Handle scan completion."""
        if self.is_closing:
            return

        self.dot_timer.stop()
        if hasattr(self, "time_update_timer"):
            self.time_update_timer.stop()

        self.time_label.setText(f"{result.duration:.2f}s")
        self.time_label.setStyleSheet(f"color: {COLOR_GREEN}; padding: 0;")

        self._set_progress_complete(COLOR_GREEN)

        self.repositories = result.repos
        self._clear_cards()

        total_repos: int = (
            int(self.progress_label.text().split("/")[1])
            if "/" in self.progress_label.text()
            else len(result.repos)
        )
        self.progress_label.setText(f"{total_repos}/{total_repos}")
        self.progress_label.setStyleSheet(f"color: {COLOR_GREEN}; padding: 0;")

        if result.repos:
            count: int = len(result.repos)
            total_behind: int = sum(r.behind for r in result.repos)
            self._update_scan_status(
                f"Found {count} repo{'s' if count != 1 else ''} behind",
                Color.COMPLETE,
                Icons.CHECK,
            )
            self._show_scan_summary(count, total_behind, total_repos)
        else:
            self._update_scan_status(
                "All repositories up to date", Color.QUEUED, Icons.CHECK
            )
            self._show_scan_summary(0, 0, total_repos)

        for row, repo in enumerate(self.repositories):
            self._update_card(row, repo.name, "PENDING", repo.behind)

        if result.repos:
            QTimer.singleShot(OPERATIONS_START_DELAY, self._run_operations)
        else:
            QTimer.singleShot(AUTO_CLOSE_NO_REPOS_DELAY, self.close)

    # ══════════════════════════════════════════════════════════════════
    # PULL OPERATIONS
    # ══════════════════════════════════════════════════════════════════
    def _run_operations(self) -> None:
        """Execute git pull operations."""
        self.completed_count = 0
        self.success_count = 0
        self.failed_count = 0
        self.total_count: int = len(self.repositories)

        for row, repo_status in enumerate(self.repositories):
            repo = Path(repo_status.path)

            if not repo.is_dir() or not (repo / ".git").is_dir():
                self._update_card(row, repo_status.name, "MISSING", repo_status.behind)
                self.completed_count += 1
                self.failed_count += 1
                self._update_operation_stats(self.success_count, self.failed_count)
                continue

            self._update_card(row, repo_status.name, "QUEUED", repo_status.behind)
            self._execute_pull(row, repo_status.name, repo_status.path)

    def _execute_pull(self, row: int, repo_name: str, repo_path: str) -> None:
        """Execute a single pull operation."""
        worker = GitPullWorker(repo_name, repo_path)
        worker.signals.finished.connect(
            lambda result: self._on_pull_finished(row, result)
        )
        worker.signals.conflict_detected.connect(self._on_conflict_detected)
        self.threadpool.start(worker)

    def _on_pull_finished(self, row: int, result: PullResult) -> None:
        """Handle pull operation completion."""
        status = "SUCCESS" if result.status == "SUCCESS" else "FAILED"

        if row in self.cards:
            self.cards[row].set_status(status)

        if status == "SUCCESS":
            self.success_count += 1
        else:
            self.failed_count += 1

        self.completed_count += 1
        self._update_operation_stats(self.success_count, self.failed_count)

        if self.completed_count >= self.total_count:
            QTimer.singleShot(AUTO_CLOSE_DELAY, self.close)

    def _on_conflict_detected(self, repo_name: str, repo_path: str) -> None:
        """Handle merge conflicts by opening GitHub Desktop."""
        ps_command: str = f"""
            function Find-GitDesktop {{
                $paths = @(
                    "$env:LOCALAPPDATA\\GitHubDesktop\\GitHubDesktop.exe",
                    "$env:PROGRAMFILES\\GitHub Desktop\\GitHubDesktop.exe",
                    "${{env:PROGRAMFILES(X86)}}\\GitHub Desktop\\GitHubDesktop.exe"
                )

                foreach ($path in $paths) {{
                    if (Test-Path -LiteralPath $path) {{ return $path }}
                }}
                return $null
            }}

            $gitDesktopPath = Find-GitDesktop

            if ($gitDesktopPath) {{
                Start-Process -FilePath $gitDesktopPath -ArgumentList "--open-in-shell" -WorkingDirectory '{repo_path}'
            }} else {{
                try {{
                    Start-Process "github" -ArgumentList "." -WorkingDirectory '{repo_path}' -ErrorAction Stop
                }} catch {{
                    # Could not open Git Desktop
                    exit 1
                }}
            }}
        """

        try:
            subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    ps_command,
                ],
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=10,
            )

            # Show message to user
            QMessageBox.information(
                self,
                "Merge Conflicts Detected",
                f"Repository: {repo_name}\n\n"
                "Merge conflicts have been detected.\n"
                "GitHub Desktop has been opened for you to resolve them.\n\n"
                "After resolving conflicts, the pull operation will be marked as FAILED.\n"
                "Please run the pull again after resolving.",
            )
        except Exception:
            pass  # Silently fail if cannot open Git Desktop

    # ══════════════════════════════════════════════════════════════════
    # TEST MODE
    # ══════════════════════════════════════════════════════════════════
    def _populate_test_data(self) -> None:
        """Populate test mode data."""
        self._update_scan_status("Test Mode - Simulating", "#bb9af7", Icons.LIGHTBULB)
        self.progress_label.setText("24/24")
        self.progress_label.setStyleSheet("color: #bb9af7; padding: 0;")
        self.folder_icon.setStyleSheet("color: #bb9af7; padding: 0;")
        self.time_label.setText("1.24s")
        self.time_label.setStyleSheet("color: #bb9af7; padding: 0;")

        self._set_progress_complete("#bb9af7")

        test_repos = [
            ("startup-shutdown", 3, "PENDING"),
            ("dotfiles", 1, "QUEUED"),
            ("nvim-config", 5, "SUCCESS"),
            ("portfolio-site", 2, "FAILED"),
            ("scripts-collection", 1, "MISSING"),
            ("api-project", 12, "PENDING"),
        ]

        total_commits: int = sum(b for _, b, _ in test_repos)
        self._show_scan_summary(len(test_repos), total_commits, 24)
        self._update_operation_stats(2, 1)

        for row, (name, behind, status) in enumerate(test_repos):
            self._update_card(row, name, status, behind)

        self._simulate_transitions()
