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

# Create the single global Qt application (must exist before any widgets)
app = QApplication(sys.argv)

# All Paths
paths: dict[str, Path] = get_default_paths()


def main() -> None:
    """Main entry point for GitUI application."""
    testing: bool = "--test" in sys.argv

    if "--git-pull" in sys.argv:
        window = GitPullRunner(testing=testing)
        window.show()
        sys.exit(app.exec())

    elif "--git-push" in sys.argv:
        window = GitPushRunner(testing=testing)
        window.show()
        sys.exit(app.exec())

    else:
        print("- Usage: python __init__.py --git-pull | --git-push")
        print("- Add --test flag for test mode")
        msg = QMessageBox()
        msg.setWindowTitle("Git Helper")
        msg.setText(
            "- Usage: python __init__.py --git-pull | --git-push\n- Add --test flag for test mode"
        )
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowIcon(QIcon(str(paths["msg_icon"])))
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        sys.exit(0)


if __name__ == "__main__":
    main()
