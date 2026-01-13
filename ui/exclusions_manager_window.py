# ----- Built-In Modules -----
from pathlib import Path

# ----- PyQt6 Modules -----
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QFont, QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

# ----- Config Imports -----
from core.config import (
    COLOR_DARK_BLUE,
    COLOR_ORANGE,
    FONT_FAMILY,
    FONT_SIZE_HEADER,
    FONT_SIZE_STAT,
    THEME_BG_PRIMARY,
    THEME_TEXT_PRIMARY,
    THEME_TEXT_SECONDARY,
    get_default_paths,
)

# ----- Manager Imports -----
from core.exclude_manager import ExcludeManager

# ----- UI Component Imports -----
from ui.settings_components import HoverIconButton

# ----- Utils Imports -----
from utils.center import position_center
from utils.icons import Icons


class ExclusionsManagerWindow(QDialog):
    """Dedicated window for managing repository exclusions.

    Features:
    - Large, easy-to-read list of excluded repositories
    - Add/Remove buttons with multi-selection support
    - Save/Cancel buttons
    - Tokyo Night themed styling
    """

    def __init__(self, parent=None) -> None:
        """Initialize the exclusions manager window.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.exclude_manager = ExcludeManager()
        self.original_exclusions: list[str] = (
            self.exclude_manager.get_excluded_repos().copy()
        )
        self._init_ui()
        self._load_exclusions()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("Manage Excluded Repositories")
        self.setFixedSize(700, 500)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setModal(True)

        # Set window icon
        paths: dict[str, Path] = get_default_paths()
        self.setWindowIcon(QIcon(str(paths["app_icon"])))

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # Background styling
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {THEME_BG_PRIMARY};
            }}
            """
        )

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # Description
        desc = QLabel(
            "Manage repositories that should be excluded from Git Push operations.\n"
            "When an excluded repository has uncommitted changes, you'll be prompted before pushing."
        )
        desc.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        desc.setStyleSheet(f"color: {THEME_TEXT_SECONDARY}; padding: 0 0 8px 0;")
        desc.setWordWrap(True)
        main_layout.addWidget(desc)

        # List section
        list_section = self._create_list_section()
        main_layout.addWidget(list_section, 1)  # Stretch to fill space

        # Button bar
        button_bar = self._create_button_bar()
        main_layout.addWidget(button_bar)

        # Center window on screen
        position_center(self)

    def _create_header(self) -> QWidget:
        """Create the header section with icon and title.

        Returns:
            QWidget: Header widget
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Icon
        icon_label = QLabel(Icons.EXCLUDE)
        icon_label.setFont(QFont(FONT_FAMILY, 17))
        icon_label.setStyleSheet(f"color: {COLOR_ORANGE};")
        layout.addWidget(icon_label)

        # Title
        title_label = QLabel("Excluded Repositories")
        title_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_HEADER, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {THEME_TEXT_PRIMARY};")
        layout.addWidget(title_label)

        layout.addStretch()

        return widget

    def _create_list_section(self) -> QWidget:
        """Create the list section with add/remove buttons.

        Returns:
            QWidget: List section widget
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_widget.setStyleSheet(
            f"""
            QListWidget {{
                background-color: rgba(255, 255, 255, 0.04);
                color: {THEME_TEXT_PRIMARY};
                border-radius: 6px;
                padding: 2px;
            }}
            QListWidget::item {{
                padding: 2px;
                border-radius: 4px;
                margin: 2px 0;
            }}
            QListWidget::item:selected {{
                background-color: rgba(122, 162, 247, 0.3);
            }}
            QListWidget::item:hover {{
                color: {THEME_TEXT_PRIMARY};
                background-color: rgba(255, 255, 255, 0.06);
            }}
            QListWidget::item:selected:!active {{
                color: {THEME_TEXT_PRIMARY};
                background: rgba(255, 255, 255, 0.08);
            }}
            QListWidget:focus {{
                color: {THEME_TEXT_PRIMARY};
                background-color: rgba(255, 255, 255, 0.06);
                outline: none;
            }}
            """
        )
        layout.addWidget(self.list_widget)

        # Buttons row
        buttons_row = self._create_list_buttons()
        layout.addWidget(buttons_row)

        return widget

    def _create_list_buttons(self) -> QWidget:
        """Create add/remove buttons for the list.

        Returns:
            QWidget: Buttons row widget
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addStretch()

        # Add Text button
        add_text_btn = HoverIconButton(
            normal_icon=Icons.ADD,
            hover_icon=Icons.ADDED,
            pressed_icon=Icons.ADDED_FOLDER,
            text="Add Text",
        )
        add_text_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        add_text_btn.setFixedHeight(32)
        add_text_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        add_text_btn.setToolTip("Manually type repository names (comma-separated)")
        add_text_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(158, 206, 106, 0.2);
                color: #9ece6a;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(158, 206, 106, 0.3);
                border-bottom: 2px solid #9ece6a;
            }}
            QPushButton:pressed {{
                background-color: rgba(158, 206, 106, 0.4);
            }}
            QPushButton:focus {{
                background-color: rgba(158, 206, 106, 0.3);
                border-bottom: 2px solid #9ece6a;
                outline: none;
            }}
            """
        )
        add_text_btn.clicked.connect(self._on_add_text_clicked)
        layout.addWidget(add_text_btn)

        # Add Browse button
        add_browse_btn = HoverIconButton(
            normal_icon=Icons.FOLDER_OUTLINE,
            hover_icon=Icons.FOLDER,
            pressed_icon=Icons.FOLDER_OPEN,
            text="Browse",
        )
        add_browse_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        add_browse_btn.setFixedHeight(32)
        add_browse_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        add_browse_btn.setToolTip(
            "Select repository folders from file system (multi-select)"
        )
        add_browse_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(158, 206, 106, 0.2);
                color: #9ece6a;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(158, 206, 106, 0.3);
                border-bottom: 2px solid #9ece6a;
            }}
            QPushButton:pressed {{
                background-color: rgba(158, 206, 106, 0.4);
            }}
            QPushButton:focus {{
                background-color: rgba(158, 206, 106, 0.3);
                border-bottom: 2px solid #9ece6a;
                outline: none;
            }}
            """
        )
        add_browse_btn.clicked.connect(self._on_add_browse_clicked)
        layout.addWidget(add_browse_btn)

        # Remove button
        remove_btn = HoverIconButton(
            normal_icon=Icons.TRASH_OUTLINE,
            hover_icon=Icons.TRASH,
            pressed_icon=Icons.TRASH_OCT,
            text="Remove",
        )
        remove_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        remove_btn.setFixedHeight(32)
        remove_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        remove_btn.setToolTip("Remove selected repositories from exclusion list")
        remove_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(247, 118, 142, 0.2);
                color: #f7768e;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(247, 118, 142, 0.3);
                border-bottom: 2px solid #f7768e;
            }}
            QPushButton:pressed {{
                background-color: rgba(247, 118, 142, 0.4);
            }}
            QPushButton:focus {{
                background-color: rgba(247, 118, 142, 0.3);
                border-bottom: 2px solid #f7768e;
                outline: none;
            }}
            """
        )
        remove_btn.clicked.connect(self._on_remove_clicked)
        layout.addWidget(remove_btn)

        return widget

    def _create_button_bar(self) -> QWidget:
        """Create the bottom button bar with Save/Cancel.

        Returns:
            QWidget: Button bar widget
        """
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        layout.addStretch()

        # Cancel button
        cancel_btn = HoverIconButton(
            normal_icon=Icons.CANCEL_OUTLINE, hover_icon=Icons.CANCEL, text="Cancel"
        )
        cancel_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        cancel_btn.setFixedHeight(36)
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.04);
                color: {THEME_TEXT_PRIMARY};
                border-radius: 6px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.08);
                border-bottom: 2px solid {COLOR_DARK_BLUE};
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.12);
            }}
            QPushButton:focus {{
                background-color: rgba(255, 255, 255, 0.08);
                border-bottom: 2px solid {COLOR_DARK_BLUE};
                outline: none;
            }}
            """
        )
        cancel_btn.clicked.connect(self._on_cancel_clicked)
        layout.addWidget(cancel_btn)

        # Save button
        save_btn = HoverIconButton(
            normal_icon=Icons.SAVE,
            hover_icon=Icons.CONTENT_SAVE,
            pressed_icon=Icons.CONTENT_SAVE_CHECK,
            text="Save",
        )
        save_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        save_btn.setFixedHeight(36)
        save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(158, 206, 106, 0.2);
                color: #9ece6a;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(158, 206, 106, 0.3);
                border-bottom: 2px solid #9ece6a;
            }}
            QPushButton:pressed {{
                background-color: rgba(158, 206, 106, 0.4);
            }}
            QPushButton:focus {{
                background-color: rgba(158, 206, 106, 0.3);
                border-bottom: 2px solid #9ece6a;
                outline: none;
            }}
            """
        )
        save_btn.clicked.connect(self._on_save_clicked)
        layout.addWidget(save_btn)

        # Set Save as default button (Enter key)
        save_btn.setDefault(True)

        return bar

    def _load_exclusions(self) -> None:
        """Load current exclusions into the list widget."""
        self.list_widget.clear()
        exclusions: list[str] = self.exclude_manager.get_excluded_repos()
        for repo_name in sorted(exclusions):
            item = QListWidgetItem(repo_name)
            self.list_widget.addItem(item)

    def _on_add_text_clicked(self) -> None:
        """Handle Add Text button click - manually type repository names."""
        from ui.add_exclusion_dialog import AddExclusionDialog

        dialog = AddExclusionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            input_text: str = dialog.get_input_text()
            if not input_text:
                return

            # Split by commas and clean up
            repo_names: list[str] = [
                name.strip() for name in input_text.split(",") if name.strip()
            ]

            # Get existing items to check for duplicates
            existing_items: list[str] = [
                self.list_widget.item(i).text() for i in range(self.list_widget.count())
            ]

            added_count = 0
            duplicate_count = 0

            for repo_name in repo_names:
                if repo_name in existing_items:
                    duplicate_count += 1
                    continue

                item = QListWidgetItem(repo_name)
                self.list_widget.addItem(item)
                existing_items.append(repo_name)
                added_count += 1

            # Show feedback message
            if added_count > 0:
                msg: str = f"Added {added_count} repository"
                if added_count > 1:
                    msg += "ies"
                if duplicate_count > 0:
                    msg += f" ({duplicate_count} duplicate{'s' if duplicate_count > 1 else ''} skipped)"
                QMessageBox.information(self, "Repositories Added", msg)
            elif duplicate_count > 0:
                QMessageBox.warning(
                    self,
                    "Duplicates Detected",
                    f"All {duplicate_count} repository names already exist in the list.",
                )

    def _on_add_browse_clicked(self) -> None:
        """Handle Browse button click - select repository folders from file system."""
        from PyQt6.QtWidgets import QAbstractItemView, QFileDialog, QListView, QTreeView

        # Create file dialog with multi-selection enabled
        dialog = QFileDialog(self)
        dialog.setFixedSize(900, 600)
        dialog.setWindowTitle("Select Repository Folder(s)")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)

        # Enable multi-selection
        list_view = dialog.findChild(QListView, "listView")
        if list_view:
            list_view.setSelectionMode(
                QAbstractItemView.SelectionMode.ExtendedSelection
            )
        tree_view = dialog.findChild(QTreeView)
        if tree_view:
            tree_view.setSelectionMode(
                QAbstractItemView.SelectionMode.ExtendedSelection
            )

        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            folders: list[str] = dialog.selectedFiles()

            # Get existing items
            existing_items: list[str] = [
                self.list_widget.item(i).text() for i in range(self.list_widget.count())
            ]

            # Track results
            added_count = 0
            duplicate_count = 0

            for folder in folders:
                # Extract repository name from path
                repo_name = Path(folder).name

                # Check if already exists
                if repo_name in existing_items:
                    duplicate_count += 1
                    continue

                # Add to list widget
                item = QListWidgetItem(repo_name)
                self.list_widget.addItem(item)
                existing_items.append(repo_name)
                added_count += 1

            # Show summary
            if added_count > 0:
                msg: str = f"Added {added_count} repository"
                if added_count > 1:
                    msg += "ies"
                if duplicate_count > 0:
                    msg += f" ({duplicate_count} duplicate{'s' if duplicate_count > 1 else ''} skipped)"
                QMessageBox.information(self, "Repositories Added", msg)
            elif duplicate_count > 0:
                QMessageBox.warning(
                    self,
                    "Duplicates Detected",
                    f"All {duplicate_count} repository names already exist in the list.",
                )

    def _on_remove_clicked(self) -> None:
        """Handle Remove Selected button click."""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select one or more repositories to remove.",
            )
            return

        # Confirm removal
        count: int = len(selected_items)
        repo_text = "repository" if count == 1 else "repositories"
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove {count} {repo_text} from exclusions?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove items in reverse order to avoid index issues
            for item in selected_items:
                self.list_widget.takeItem(self.list_widget.row(item))

    def _on_save_clicked(self) -> None:
        """Handle Save button click."""
        # Get all items from list
        exclusions: list[str] = [
            self.list_widget.item(i).text() for i in range(self.list_widget.count())
        ]

        # Save to manager
        if self.exclude_manager.save_exclusions(exclusions):
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Save Failed",
                "Failed to save exclusions. Please try again.",
            )

    def _on_cancel_clicked(self) -> None:
        """Handle Cancel button click."""
        # Check if changes were made
        current_exclusions: list[str] = [
            self.list_widget.item(i).text() for i in range(self.list_widget.count())
        ]

        if set(current_exclusions) != set(self.original_exclusions):
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Discard them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return

        self.reject()
