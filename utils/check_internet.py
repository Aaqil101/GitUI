# ----- Built-In Modules -----
import socket

# ----- PyQt6 Modules -----
from PyQt6.QtCore import QTimer

# ----- Utils Modules -----
from utils.color import Color
from utils.icons import Icons


class InternetChecker:
    """Mixin class to add internet checking functionality to GitPullRunner."""

    def _check_internet_status(self) -> None:
        """Check internet and update UI accordingly."""
        self.has_internet: bool = self._check_internet()

        if self.has_internet:
            self._update_subtitle("Ready", Color.SUCCESS)
            self.retry_button.setVisible(False)
        else:
            self._update_subtitle("No Connection", Color.FAILED)
            self._update_scan_status(
                "No internet connection", Color.FAILED, Icons.WARNING
            )
            self.retry_button.setVisible(True)

    def _on_retry_clicked(self) -> None:
        """Handle retry button click."""
        self._update_scan_status("Checking connection...", Color.SCANNING, Icons.SEARCH)
        self.retry_button.setEnabled(False)

        # Check after a short delay to show the status update
        QTimer.singleShot(500, self._perform_retry_check)

    def _perform_retry_check(self) -> None:
        """Perform the actual retry check."""
        self._check_internet_status()
        self.retry_button.setEnabled(True)

        if self.has_internet:
            self._update_scan_status(
                "Scanning repositories...", Color.SCANNING, Icons.SEARCH
            )
            # Reset scan flag and start scan after successful connection
            self._scan_started = False
            QTimer.singleShot(100, self._start_scan)

    @staticmethod
    def _check_internet() -> bool:
        """Check if internet connection is available."""
        try:
            # Try to connect to a reliable host (Google DNS)
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
