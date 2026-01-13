# ----- Built-In Modules -----
import os
from pathlib import Path

# ----- PyQt6 Modules -----
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QLabel, QWidget

# ----- Core Imports -----
from core.base_runner import BaseGitRunner
from core.config import (
    AUTO_CLOSE_DELAY,
    AUTO_CLOSE_NO_REPOS_DELAY,
    COLOR_GREEN,
    OPERATIONS_START_DELAY,
    THEME_TEXT_DIM,
)

# ----- Workers Imports -----
from scanners.git_push_scanner import PowerShellScannerWorker, RepoStatus, ScanResult

# ----- UI Imports -----
from ui.power_options_panel import create_power_options_panel

# ----- Utils Imports -----
from utils.color import Color
from utils.icons import Icons
from workers.git_push_worker import GitPushWorker, PushResult


class GitPushRunner(BaseGitRunner):
    """Git Push Runner - handles pushing commits to repositories."""

    def __init__(self, testing: bool = False) -> None:
        """Initialize the Git Push Runner.

        Args:
            testing: If True, run in test mode without actual git operations
        """
        super().__init__(testing)
        self.power_option = None  # Stores selected power option
        self.power_options_panel = None  # Power options panel widget
        self.power_options_signals = None  # Power options signals object
        self.is_cancelling = False  # Flag to prevent more operations when cancelling

    def _get_operation_config(self) -> dict:
        """Return push-specific configuration."""
        return {
            "title": "Git Push Runner",
            "icon": Icons.GIT_PUSH_OCT,
            "header_text": "Repositories to Push",
            "stat_labels": {
                "repos": "Repos with Changes",
                "items": "Files to Commit",
                "operation_success": "Successfully Pushed",
            },
        }

    def _show_scan_summary(
        self, repos_count: int, items_count: int, total_scanned: int
    ) -> None:
        """Display push-specific scan summary."""
        if repos_count > 0:
            self.summary_repos.setText(
                f"{Icons.GIT_BRANCH} {repos_count} repo{'s' if repos_count != 1 else ''} with changes"
            )
            self.summary_repos.setStyleSheet("color: #7aa2f7; padding: 0;")
        else:
            self.summary_repos.setText(
                f"{Icons.GIT_BRANCH} {total_scanned} repos scanned"
            )
            self.summary_repos.setStyleSheet(f"color: {THEME_TEXT_DIM}; padding: 0;")

        if items_count > 0:
            self.summary_commits.setText(
                f"{Icons.GIT_COMMIT} {items_count} file{'s' if items_count != 1 else ''} to commit"
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
        """Update stats panel with push-specific values."""
        # Find the value label by object name
        scanned_labels = self.stat_scanned.findChildren(QLabel)
        if scanned_labels:
            scanned_labels[-1].setText(str(total_scanned))

        behind_labels = self.stat_behind.findChildren(QLabel)
        if behind_labels:
            behind_labels[-1].setText(str(repos_count))

        commits_labels = self.stat_commits.findChildren(QLabel)
        if commits_labels:
            commits_labels[-1].setText(str(items_count))

    def _update_operation_stats(self, success: int, failed: int) -> None:
        """Update push operation stats."""
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
        """Start the push scan."""
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
            total_files: int = sum(r.files_changed for r in result.repos)
            self._update_scan_status(
                f"Found {count} repo{'s' if count != 1 else ''} with changes",
                Color.COMPLETE,
                Icons.CHECK,
            )
            self._show_scan_summary(count, total_files, total_repos)
        else:
            self._update_scan_status(
                "All repositories up to date", Color.QUEUED, Icons.CHECK
            )
            self._show_scan_summary(0, 0, total_repos)

        for row, repo in enumerate(self.repositories):
            self._update_card(row, repo.name, "PENDING", repo.files_changed)

        if result.repos:
            self._show_power_options_panel()
        else:
            QTimer.singleShot(AUTO_CLOSE_NO_REPOS_DELAY, self.close)

    def _show_power_options_panel(self) -> None:
        """Show the power options panel in the left sidebar."""
        if self.power_options_panel is None and self.left_panel_layout:
            self.power_options_panel, self.power_options_signals = (
                create_power_options_panel(self)
            )
            self.power_options_signals.option_selected.connect(
                self._on_power_option_selected
            )

            # Insert panel before the last item (stretch)
            self.left_panel_layout.insertWidget(
                self.left_panel_layout.count() - 1, self.power_options_panel
            )

        if self.power_options_panel:
            # Resize window to 800 height to accommodate power options panel
            self.setFixedSize(self.width(), 800)
            # Re-center window after resize
            from utils.center import position_center

            position_center(self)

            self.power_options_panel.setVisible(True)
            self.power_options_panel.start_countdown()

    def _on_power_option_selected(self, option: str) -> None:
        """Handle power option selection.

        Args:
            option: Selected power option (shutdown, restart, shutdown_cancel, restart_cancel)
        """
        self.power_option = option

        # Start operations
        if self.testing:
            QTimer.singleShot(OPERATIONS_START_DELAY, self._simulate_transitions)
        else:
            QTimer.singleShot(OPERATIONS_START_DELAY, self._run_operations)

    # ══════════════════════════════════════════════════════════════════
    # PUSH OPERATIONS
    # ══════════════════════════════════════════════════════════════════
    def _run_operations(self) -> None:
        """Execute git push operations."""
        self.completed_count = 0
        self.success_count = 0
        self.failed_count = 0
        self.total_count: int = len(self.repositories)

        for row, repo_status in enumerate(self.repositories):
            repo = Path(repo_status.path)

            if not repo.is_dir() or not (repo / ".git").is_dir():
                self._update_card(
                    row, repo_status.name, "MISSING", repo_status.files_changed
                )
                self.completed_count += 1
                self.failed_count += 1
                self._update_operation_stats(self.success_count, self.failed_count)
                continue

            self._update_card(
                row, repo_status.name, "QUEUED", repo_status.files_changed
            )

            # Check if operations are being cancelled
            if not self.is_cancelling:
                self._execute_push(row, repo_status.name, repo_status.path)

    def _execute_push(self, row: int, repo_name: str, repo_path: str) -> None:
        """Execute a single push operation."""
        # Check if repository is excluded
        from pathlib import Path

        from core.exclude_manager import ExcludeManager

        exclude_mgr = ExcludeManager()
        repo_folder_name = Path(repo_path).name

        if exclude_mgr.is_excluded(repo_folder_name):
            # Show exclusion confirmation dialog
            from ui.exclude_confirmation_dialog import ExcludeConfirmationDialog

            dialog = ExcludeConfirmationDialog(repo_folder_name, self, self.testing)
            dialog.exec()
            choice = dialog.get_choice()

            if choice == "skip":
                # Skip this repository
                result = PushResult(
                    status="SKIPPED",
                    repo_name=repo_name,
                    repo_path=repo_path,
                    error_message="Skipped (excluded repository)",
                    is_excluded=True,
                )
                self._on_push_finished(row, result)
                return
            elif choice == "manual_push":
                # Show manual push instructions
                self._show_manual_push_dialog(repo_name, repo_path)
                result = PushResult(
                    status="SKIPPED",
                    repo_name=repo_name,
                    repo_path=repo_path,
                    error_message="User chose manual push",
                    is_excluded=True,
                )
                self._on_push_finished(row, result)
                return
            # else choice == "push" - continue normally

        commit_prefix = self._get_commit_prefix()
        worker = GitPushWorker(repo_name, repo_path, commit_prefix=commit_prefix)
        worker.signals.finished.connect(
            lambda result: self._on_push_finished(row, result)
        )
        self.threadpool.start(worker)

    def _get_commit_prefix(self) -> str:
        """Get commit message prefix based on selected power option.

        Returns:
            str: Commit message prefix (e.g., "Shutdown", "Restart")
        """
        if self.power_option == "shutdown":
            return "Shutdown"
        elif self.power_option == "restart":
            return "Restart"
        elif self.power_option == "shutdown_cancel":
            return "Shutdown (Cancelled)"
        elif self.power_option == "restart_cancel":
            return "Restart (Cancelled)"
        else:
            # Fallback (should never happen)
            return "Shutdown"

    def _show_manual_push_dialog(self, repo_name: str, repo_path: str) -> None:
        """Show dialog with instructions for manual push.

        Args:
            repo_name: Repository name
            repo_path: Full path to repository
        """
        from PyQt6.QtWidgets import QMessageBox

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Manual Push Required")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(
            f"Please manually push changes from the following repository:\n\n"
            f"Repository: {repo_name}\n"
            f"Path: {repo_path}\n\n"
            f"You can use your preferred Git client or command line to push the changes."
        )
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

        # Check if we should complete
        if self.completed_count >= self.total_count:
            self._handle_completion()

    def _on_push_finished(self, row: int, result: PushResult) -> None:
        """Handle push operation completion."""
        # Log the operation result
        from core.log_manager import LogManager

        commit_prefix = (
            self._get_commit_prefix() if hasattr(self, "power_option") else ""
        )
        LogManager().log_push_operation(result, commit_prefix)

        # Map result status to card status
        if result.status == "SUCCESS":
            status = "SUCCESS"
        elif result.status in ["SKIPPED", "CANCELLED"]:
            status = "SKIPPED"
        else:
            status = "FAILED"

        if row in self.cards:
            self.cards[row].set_status(status)

        # Update counters
        if status == "SUCCESS":
            self.success_count += 1
        elif status == "SKIPPED":
            # Skipped counts as neither success nor failure
            pass
        else:
            self.failed_count += 1

        self.completed_count += 1
        self._update_operation_stats(self.success_count, self.failed_count)

        if self.completed_count >= self.total_count:
            self._handle_completion()

    def _handle_completion(self) -> None:
        """Handle completion of all push operations and execute power action."""
        # Check if failed_count exists (it won't in test mode)
        all_successful = getattr(self, "failed_count", 0) == 0

        if self.testing:
            # Test mode - just show what would happen
            print(f"[TEST MODE] Would execute power action: {self.power_option}")
            QTimer.singleShot(AUTO_CLOSE_DELAY, self.close)
        elif all_successful and self.power_option in ["shutdown", "restart"]:
            self.close()

            if self.power_option == "shutdown":
                os.system("shutdown /s /t 5")
            elif self.power_option == "restart":
                os.system("shutdown /r /t 5")
        else:
            QTimer.singleShot(AUTO_CLOSE_DELAY, self.close)

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

        # Log test operations
        from core.log_manager import LogManager

        log_manager = LogManager()
        for name, _, status in test_repos:
            log_manager.log_test_push_operation(name, status)

        # Show power options panel in test mode too
        QTimer.singleShot(1000, self._show_power_options_panel)

    def _simulate_transitions(self) -> None:
        """Simulate status transitions for test mode."""
        # Simulate exclusion dialog if any repos are excluded
        from core.exclude_manager import ExcludeManager

        exclude_mgr = ExcludeManager()
        excluded_repos = exclude_mgr.get_excluded_repos()

        # If there are excluded repos, show dialog for the first test repo that matches
        if excluded_repos:
            test_repo_names = [
                "startup-shutdown",
                "dotfiles",
                "nvim-config",
                "portfolio-site",
                "scripts-collection",
                "api-project",
            ]
            for repo_name in test_repo_names:
                if exclude_mgr.is_excluded(repo_name):
                    # Show exclusion confirmation dialog for this repo
                    from ui.exclude_confirmation_dialog import ExcludeConfirmationDialog

                    dialog = ExcludeConfirmationDialog(repo_name, self, self.testing)
                    dialog.exec()
                    choice = dialog.get_choice()

                    print(
                        f"[TEST MODE] Exclusion dialog result for {repo_name}: {choice}"
                    )
                    break  # Only show dialog for first excluded repo

        # Call parent implementation for card transitions
        super()._simulate_transitions()

        # Simulate power action after transitions complete (test mode only)
        QTimer.singleShot(2000, self._handle_completion)
