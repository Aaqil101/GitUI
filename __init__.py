# ----- Built-In Modules -----
import sys
from pathlib import Path

# ----- PyQt6 Modules -----
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox

# ----- Core Modules -----
from core.config import get_default_paths
from core.pull_runner import GitPullRunner
from core.push_runner import GitPushRunner
from core.settings_manager import SettingsManager

# Create the single global Qt application (must exist before any widgets)
app = QApplication(sys.argv)

# All Paths
paths: dict[str, Path] = get_default_paths()


def main() -> None:
    """Main entry point for GitUI application."""
    # Initialize settings manager (loads settings from file)
    SettingsManager()

    # Load settings into config constants
    from core.config import load_settings_into_config

    load_settings_into_config()

    # Auto-delete old logs based on settings
    from core.log_manager import LogManager

    log_manager = LogManager()
    success, files_deleted = log_manager.auto_delete_old_logs()
    if success and files_deleted > 0:
        print(f"Auto-deleted {files_deleted} old log file(s)")

    testing: bool = "--test" in sys.argv

    if "--settings" in sys.argv:
        # Open settings dialog directly
        from ui.settings_dialog import SettingsDialog

        dialog = SettingsDialog()
        dialog.show()
        sys.exit(app.exec())

    elif "--git-pull" in sys.argv:
        window = GitPullRunner(testing=testing)
        window.show()
        sys.exit(app.exec())

    elif "--git-push" in sys.argv:
        window = GitPushRunner(testing=testing)
        window.show()
        sys.exit(app.exec())

    else:
        msg = QMessageBox()
        msg.setWindowTitle("Git Helper")
        msg.setText(
            "- Usage: python __init__.py --git-pull | --git-push | --settings\n- Add --test flag for test mode"
        )
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowIcon(QIcon(str(paths["msg_icon"])))
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        sys.exit(0)


if __name__ == "__main__":
    main()
