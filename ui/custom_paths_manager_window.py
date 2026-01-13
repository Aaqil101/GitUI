# ----- Built-In Modules -----
from pathlib import Path

# ----- PyQt6 Modules -----
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QFont, QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
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
    THEME_BG_SECONDARY,
    THEME_TEXT_PRIMARY,
    THEME_TEXT_SECONDARY,
    get_default_paths,
)

# ----- Manager Imports -----
from core.custom_paths_manager import CustomPathsManager

# ----- UI Component Imports -----
from ui.settings_components import HoverIconButton

# ----- Utils Imports -----
from utils.center import position_center
from utils.icons import Icons


class CustomPathsManagerWindow(QDialog):
    """Dedicated window for managing custom repository paths.

    Features:
    - Large, easy-to-read list of custom paths
    - Add/Remove buttons with multi-selection support
    - Folder browser dialog for adding paths
    - Save/Cancel buttons
    - Tokyo Night themed styling
    """

    def __init__(self, parent=None) -> None:
        """Initialize the custom paths manager window.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.custom_paths_manager = CustomPathsManager()
        self.original_paths: list[Path] = (
            self.custom_paths_manager.get_custom_paths().copy()
        )
        self._init_ui()
        self._load_paths()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("Manage Custom Repository Paths")
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
            "Add additional folders to scan for repositories during Git Pull and Git Push operations.\n"
            "These paths will be scanned in addition to your GitHub folder."
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
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel(Icons.FOLDER_OPEN)
        icon_label.setFont(QFont(FONT_FAMILY, 18))
        icon_label.setStyleSheet(f"color: {COLOR_ORANGE};")
        layout.addWidget(icon_label)

        # Title
        title_label = QLabel("Custom Repository Paths")
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
        self.list_widget.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT - 1))
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_widget.setStyleSheet(
            f"""
            QListWidget {{
                background-color: rgba(255, 255, 255, 0.04);
                color: {THEME_TEXT_PRIMARY};
                border-radius: 6px;
                padding: 4px;
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

        # Add button
        add_btn = HoverIconButton(
            normal_icon=Icons.ADD,
            hover_icon=Icons.ADDED,
            pressed_icon=Icons.ADDED_FOLDER,
            text="Add",
        )
        add_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        add_btn.setFixedHeight(32)
        add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        add_btn.setStyleSheet(
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
        add_btn.clicked.connect(self._on_add_clicked)
        layout.addWidget(add_btn)

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
            normal_icon=Icons.CANCEL_OUTLINE,
            hover_icon=Icons.CANCEL,
            text="Cancel",
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

    def _load_paths(self) -> None:
        """Load current custom paths into the list widget."""
        self.list_widget.clear()
        paths: list[Path] = self.custom_paths_manager.get_custom_paths()
        for path in sorted(paths):
            item = QListWidgetItem(path)
            self.list_widget.addItem(item)

    def _on_add_clicked(self) -> None:
        """Handle adding custom repository paths (supports multiple selection)."""
        from PyQt6.QtWidgets import QAbstractItemView, QFileDialog, QListView, QTreeView

        # Create file dialog with multi-selection enabled
        dialog = QFileDialog(self)
        dialog.setFixedSize(900, 600)
        dialog.setWindowTitle("Select Custom Repository Folder(s)")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)

        # Enable multi-selection by getting the list view and setting selection mode
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
            invalid_paths = []
            duplicate_paths = []

            for folder in folders:
                # Check if already exists
                if folder in existing_items:
                    duplicate_paths.append(folder)
                    continue

                # Validate path
                is_valid, error_msg = self.custom_paths_manager.validate_path(folder)
                if not is_valid:
                    invalid_paths.append(f"{folder}: {error_msg}")
                    continue

                # Add to list widget
                item = QListWidgetItem(folder)
                self.list_widget.addItem(item)
                existing_items.append(folder)  # Track for duplicate checking
                added_count += 1

            # Show summary if there were any issues
            messages = []
            if added_count > 0:
                messages.append(f"Successfully added {added_count} folder(s).")
            if duplicate_paths:
                messages.append(f"\nSkipped {len(duplicate_paths)} duplicate path(s).")
            if invalid_paths:
                messages.append(f"\nSkipped {len(invalid_paths)} invalid path(s):")
                for invalid in invalid_paths[:5]:  # Show max 5 errors
                    messages.append(f"  • {invalid}")
                if len(invalid_paths) > 5:
                    messages.append(f"  ... and {len(invalid_paths) - 5} more")

            if messages:
                if invalid_paths or (duplicate_paths and added_count == 0):
                    QMessageBox.warning(self, "Add Folders", "\n".join(messages))
                else:
                    QMessageBox.information(self, "Add Folders", "\n".join(messages))

    def _on_remove_clicked(self) -> None:
        """Handle Remove Selected button click."""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select one or more paths to remove.",
            )
            return

        # Confirm removal
        count: int = len(selected_items)
        path_text = "path" if count == 1 else "paths"
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove {count} custom {path_text}?",
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
        paths: list[str] = [
            self.list_widget.item(i).text() for i in range(self.list_widget.count())
        ]

        # Save to manager
        if self.custom_paths_manager.save_custom_paths(paths):
            # Show restart notification
            QMessageBox.information(
                self,
                "Restart Required",
                "Custom paths saved successfully.\n\nPlease restart the application for changes to take effect.",
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Save Failed",
                "Failed to save custom paths. Please try again.",
            )

    def _on_cancel_clicked(self) -> None:
        """Handle Cancel button click."""
        # Check if changes were made
        current_paths: list[str] = [
            self.list_widget.item(i).text() for i in range(self.list_widget.count())
        ]

        if set(current_paths) != set(self.original_paths):
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
