# ----- PyQt6 Modules -----
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QCursor
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

# ----- Config Imports -----
from core.config import (
    COLOR_ORANGE,
    FONT_FAMILY,
    FONT_SIZE_HEADER,
    FONT_SIZE_LABEL,
    FONT_SIZE_STAT,
    THEME_BG_PRIMARY,
    THEME_BG_SECONDARY,
    THEME_TEXT_PRIMARY,
    THEME_TEXT_SECONDARY,
    get_default_paths,
)

# ----- Manager Imports -----
from core.settings_manager import SettingsManager
from core.exclude_manager import ExcludeManager
from core.custom_paths_manager import CustomPathsManager

# ----- UI Component Imports -----
from ui.settings_components import (
    create_checkbox_row,
    create_list_manager,
    create_path_selector,
    create_settings_section,
    create_spinbox_row,
)

# ----- Utils Imports -----
from utils.center import position_center
from utils.icons import Icons


class SettingsDialog(QDialog):
    """Settings dialog with side panel navigation and multi-page content area.

    Features:
    - Side panel navigation (General, Git Operations, Appearance, Advanced)
    - Main content area with scrollable settings pages
    - Save/Cancel/Reset buttons
    - Restart detection for settings requiring app restart
    """

    settings_saved = pyqtSignal(bool)  # Emits restart_needed flag

    def __init__(self, parent=None):
        """Initialize the settings dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.settings_manager = SettingsManager()
        self.exclude_manager = ExcludeManager()
        self.custom_paths_manager = CustomPathsManager()

        # Deep copy current settings to allow cancellation
        self.current_settings = self._deep_copy_dict(
            self.settings_manager.get_settings()
        )
        self.original_settings = self._deep_copy_dict(self.current_settings)
        self.restart_needed = False

        # UI component references (populated in page creation methods)
        self.ui_components = {}

        self._init_ui()

    def _deep_copy_dict(self, d: dict) -> dict:
        """Deep copy a dictionary recursively.

        Args:
            d: Dictionary to copy

        Returns:
            dict: Deep copy of dictionary
        """
        result = {}
        for key, value in d.items():
            if isinstance(value, dict):
                result[key] = self._deep_copy_dict(value)
            elif isinstance(value, list):
                result[key] = value.copy()
            else:
                result[key] = value
        return result

    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Settings")
        self.setFixedSize(800, 550)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setModal(True)

        # Set window icon
        paths = get_default_paths()
        self.setWindowIcon(QIcon(str(paths["app_icon"])))

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Background styling
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {THEME_BG_PRIMARY};
            }}
            """
        )

        # Side panel
        self.side_panel = self._create_side_panel()
        main_layout.addWidget(self.side_panel)

        # Content area
        self.content_area = self._create_content_area()
        main_layout.addWidget(self.content_area, 1)

        # Center dialog on screen
        position_center(self)

    def _create_side_panel(self) -> QWidget:
        """Create the side panel navigation.

        Returns:
            QWidget: Side panel widget
        """
        panel = QWidget()
        panel.setFixedWidth(180)
        panel.setStyleSheet(
            f"""
            QWidget {{
                background-color: {THEME_BG_SECONDARY};
            }}
            """
        )

        layout = QVBoxLayout(panel)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QLabel(f"{Icons.SETTINGS}  Settings")
        header.setFont(QFont(FONT_FAMILY, FONT_SIZE_HEADER, QFont.Weight.Bold))
        header.setStyleSheet(
            f"""
            QLabel {{
                color: {THEME_TEXT_PRIMARY};
                padding: 20px 16px;
                background-color: rgba(122, 162, 247, 0.1);
                border-bottom: 1px solid rgba(122, 162, 247, 0.3);
            }}
            """
        )
        layout.addWidget(header)

        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        self.nav_list.setStyleSheet(
            f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                color: {THEME_TEXT_SECONDARY};
                padding: 14px 16px;
                border-left: 3px solid transparent;
            }}
            QListWidget::item:selected {{
                background-color: rgba(122, 162, 247, 0.2);
                color: {THEME_TEXT_PRIMARY};
                border-left: 3px solid #7aa2f7;
            }}
            QListWidget::item:hover {{
                background-color: rgba(255, 255, 255, 0.04);
            }}
            """
        )

        # Navigation items
        nav_items = [
            f"{Icons.FOLDER}  General",
            f"{Icons.GIT_PUSH}  Git Operations",
            f"{Icons.PALETTE}  Appearance",
            f"{Icons.ADVANCED}  Advanced",
        ]

        for item_text in nav_items:
            item = QListWidgetItem(item_text)
            self.nav_list.addItem(item)

        self.nav_list.setCurrentRow(0)
        self.nav_list.currentRowChanged.connect(self._on_nav_item_clicked)
        layout.addWidget(self.nav_list)

        return panel

    def _create_content_area(self) -> QWidget:
        """Create the main content area with stacked pages.

        Returns:
            QWidget: Content area widget
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self._create_general_page())
        self.stacked_widget.addWidget(self._create_git_ops_page())
        self.stacked_widget.addWidget(self._create_appearance_page())
        self.stacked_widget.addWidget(self._create_advanced_page())

        layout.addWidget(self.stacked_widget, 1)

        # Bottom button bar
        button_bar = self._create_button_bar()
        layout.addWidget(button_bar)

        return container

    def _create_general_page(self) -> QWidget:
        """Create the General settings page.

        Returns:
            QWidget: General settings page
        """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet(
            f"""
            QScrollArea {{
                border: none;
                background-color: {THEME_BG_PRIMARY};
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {THEME_BG_PRIMARY};
            }}
            """
        )

        content = QWidget()
        content.setStyleSheet(f"background-color: {THEME_BG_PRIMARY};")
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 20, 24, 20)

        # Repository Paths Section
        layout.addWidget(create_settings_section("Repository Paths", Icons.FOLDER))

        github_path_widget, github_path_edit = create_path_selector(
            "GitHub Repositories Folder",
            self.current_settings["general"]["github_path"],
            lambda: None,  # No real-time callback needed
        )
        self.ui_components["github_path"] = github_path_edit
        layout.addWidget(github_path_widget)

        # Custom Repository Paths
        custom_paths = [str(p) for p in self.custom_paths_manager.get_custom_paths()]
        custom_paths_widget, custom_paths_list = create_list_manager(
            "Custom Repository Paths (scanned in addition to GitHub folder)",
            custom_paths,
            self._on_add_custom_path,
            self._on_remove_custom_path,
        )
        self.ui_components["custom_paths_list"] = custom_paths_list
        layout.addWidget(custom_paths_widget)

        # Repository Exclusions Section
        layout.addWidget(
            create_settings_section("Repository Exclusions", Icons.EXCLUDE)
        )

        # Username display
        username_label = QLabel(
            f"Current User: {self.exclude_manager.get_current_machine_name()}"
        )
        username_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        username_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLOR_ORANGE};
                padding: 4px 0;
                font-style: italic;
            }}
            """
        )
        layout.addWidget(username_label)

        # Excluded repositories list
        excluded_repos = self.exclude_manager.get_excluded_repos()
        exclude_widget, exclude_list = create_list_manager(
            "Excluded Repositories (by repository name, not path)",
            excluded_repos,
            self._on_add_exclusion,
            self._on_remove_exclusion,
        )
        self.ui_components["exclude_list"] = exclude_list
        layout.addWidget(exclude_widget)

        # Exclude confirmation timeout
        timeout_widget, timeout_spin = create_spinbox_row(
            "Exclude Confirmation Timeout",
            self.current_settings["git_operations"]["exclude_confirmation_timeout"],
            1,
            60,
            "seconds",
            "How long to wait for user response when excluded repo has changes",
        )
        self.ui_components["exclude_timeout"] = timeout_spin
        layout.addWidget(timeout_widget)

        # Window Behavior Section
        layout.addWidget(create_settings_section("Window Behavior", Icons.WINDOW))

        always_on_top_widget, always_on_top_check = create_checkbox_row(
            "Always keep window on top",
            self.current_settings["general"]["window_always_on_top"],
            "Window stays above other windows",
        )
        self.ui_components["always_on_top"] = always_on_top_check
        layout.addWidget(always_on_top_widget)

        width_widget, width_spin = create_spinbox_row(
            "Window Width",
            self.current_settings["general"]["window_width"],
            600,
            2000,
            "px",
            "Width of the main window",
            restart_required=True,
        )
        self.ui_components["window_width"] = width_spin
        layout.addWidget(width_widget)

        height_widget, height_spin = create_spinbox_row(
            "Window Height",
            self.current_settings["general"]["window_height"],
            400,
            1200,
            "px",
            "Height of the main window",
            restart_required=True,
        )
        self.ui_components["window_height"] = height_spin
        layout.addWidget(height_widget)

        # Auto-Close Delays Section
        layout.addWidget(create_settings_section("Auto-Close Delays", Icons.TIMER))

        auto_close_widget, auto_close_spin = create_spinbox_row(
            "After Operations Complete",
            self.current_settings["general"]["auto_close_delay"],
            0,
            10000,
            "ms",
            "Delay before closing window after all operations complete",
        )
        self.ui_components["auto_close_delay"] = auto_close_spin
        layout.addWidget(auto_close_widget)

        no_repos_widget, no_repos_spin = create_spinbox_row(
            "When No Repositories Need Updates",
            self.current_settings["general"]["auto_close_no_repos_delay"],
            0,
            10000,
            "ms",
            "Delay before closing when scan finds no repositories needing updates",
        )
        self.ui_components["auto_close_no_repos_delay"] = no_repos_spin
        layout.addWidget(no_repos_widget)

        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    def _create_git_ops_page(self) -> QWidget:
        """Create the Git Operations settings page.

        Returns:
            QWidget: Git Operations settings page
        """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet(
            f"""
            QScrollArea {{
                border: none;
                background-color: {THEME_BG_PRIMARY};
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {THEME_BG_PRIMARY};
            }}
            """
        )

        content = QWidget()
        content.setStyleSheet(f"background-color: {THEME_BG_PRIMARY};")
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 20, 24, 20)

        # Performance Section
        layout.addWidget(create_settings_section("Performance", Icons.PERFORMANCE))

        throttle_widget, throttle_spin = create_spinbox_row(
            "PowerShell Throttle Limit",
            self.current_settings["git_operations"]["powershell_throttle_limit"],
            1,
            100,
            "concurrent operations",
            "Number of parallel PowerShell operations (higher = faster but more resource-intensive)",
            restart_required=True,
        )
        self.ui_components["throttle_limit"] = throttle_spin
        layout.addWidget(throttle_widget)

        scan_timeout_widget, scan_timeout_spin = create_spinbox_row(
            "Scan Timeout",
            self.current_settings["git_operations"]["scan_timeout"],
            10,
            600,
            "seconds",
            "Maximum time to wait for repository scanning to complete",
        )
        self.ui_components["scan_timeout"] = scan_timeout_spin
        layout.addWidget(scan_timeout_widget)

        op_timeout_widget, op_timeout_spin = create_spinbox_row(
            "Operation Timeout",
            self.current_settings["git_operations"]["operation_timeout"],
            10,
            600,
            "seconds",
            "Maximum time to wait for individual git operations (pull/push)",
        )
        self.ui_components["operation_timeout"] = op_timeout_spin
        layout.addWidget(op_timeout_widget)

        # Power Options Section
        layout.addWidget(create_settings_section("Power Options", Icons.POWER))

        power_countdown_widget, power_countdown_spin = create_spinbox_row(
            "Power Countdown Duration",
            self.current_settings["git_operations"]["power_countdown_seconds"],
            1,
            60,
            "seconds",
            "Countdown timer before auto-selecting power option (Git Push only)",
        )
        self.ui_components["power_countdown"] = power_countdown_spin
        layout.addWidget(power_countdown_widget)

        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    def _create_appearance_page(self) -> QWidget:
        """Create the Appearance settings page.

        Returns:
            QWidget: Appearance settings page
        """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet(
            f"""
            QScrollArea {{
                border: none;
                background-color: {THEME_BG_PRIMARY};
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {THEME_BG_PRIMARY};
            }}
            """
        )

        content = QWidget()
        content.setStyleSheet(f"background-color: {THEME_BG_PRIMARY};")
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 20, 24, 20)

        # Font Configuration Section
        layout.addWidget(
            create_settings_section("Font Configuration", Icons.FONT)
        )

        font_family_widget, font_family_edit = create_path_selector(
            "Font Family (requires Nerd Font for icons)",
            self.current_settings["appearance"]["font_family"],
            lambda: None,
        )
        # Disable browse button for font family (not a path)
        for child in font_family_widget.findChildren(QPushButton):
            if "Browse" in child.text():
                child.setVisible(False)
        self.ui_components["font_family"] = font_family_edit
        layout.addWidget(font_family_widget)

        font_title_widget, font_title_spin = create_spinbox_row(
            "Font Size - Title",
            self.current_settings["appearance"]["font_size_title"],
            8,
            24,
            "pt",
            "Font size for main title text",
            restart_required=True,
        )
        self.ui_components["font_size_title"] = font_title_spin
        layout.addWidget(font_title_widget)

        font_header_widget, font_header_spin = create_spinbox_row(
            "Font Size - Header",
            self.current_settings["appearance"]["font_size_header"],
            8,
            24,
            "pt",
            "Font size for section headers",
            restart_required=True,
        )
        self.ui_components["font_size_header"] = font_header_spin
        layout.addWidget(font_header_widget)

        font_label_widget, font_label_spin = create_spinbox_row(
            "Font Size - Label",
            self.current_settings["appearance"]["font_size_label"],
            8,
            24,
            "pt",
            "Font size for labels",
            restart_required=True,
        )
        self.ui_components["font_size_label"] = font_label_spin
        layout.addWidget(font_label_widget)

        font_stat_widget, font_stat_spin = create_spinbox_row(
            "Font Size - Stat",
            self.current_settings["appearance"]["font_size_stat"],
            8,
            24,
            "pt",
            "Font size for statistics and small text",
            restart_required=True,
        )
        self.ui_components["font_size_stat"] = font_stat_spin
        layout.addWidget(font_stat_widget)

        # Animations Section
        layout.addWidget(create_settings_section("Animations", Icons.ANIMATION))

        enable_anim_widget, enable_anim_check = create_checkbox_row(
            "Enable Animations",
            self.current_settings["appearance"]["enable_animations"],
            "Enable UI animations and transitions",
        )
        self.ui_components["enable_animations"] = enable_anim_check
        layout.addWidget(enable_anim_widget)

        anim_duration_widget, anim_duration_spin = create_spinbox_row(
            "Animation Duration",
            self.current_settings["appearance"]["animation_duration"],
            100,
            1000,
            "ms",
            "Duration of UI animations",
            restart_required=True,
        )
        self.ui_components["animation_duration"] = anim_duration_spin
        layout.addWidget(anim_duration_widget)

        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    def _create_advanced_page(self) -> QWidget:
        """Create the Advanced settings page.

        Returns:
            QWidget: Advanced settings page
        """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet(
            f"""
            QScrollArea {{
                border: none;
                background-color: {THEME_BG_PRIMARY};
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {THEME_BG_PRIMARY};
            }}
            """
        )

        content = QWidget()
        content.setStyleSheet(f"background-color: {THEME_BG_PRIMARY};")
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 20, 24, 20)

        # Startup Section
        layout.addWidget(create_settings_section("Startup", Icons.STARTUP))

        test_mode_widget, test_mode_check = create_checkbox_row(
            "Test Mode by Default",
            self.current_settings["advanced"]["test_mode_default"],
            "Start in test mode (simulated operations) by default",
        )
        self.ui_components["test_mode_default"] = test_mode_check
        layout.addWidget(test_mode_widget)

        scan_delay_widget, scan_delay_spin = create_spinbox_row(
            "Scan Start Delay",
            self.current_settings["advanced"]["scan_start_delay"],
            0,
            5000,
            "ms",
            "Delay before starting repository scan",
            restart_required=True,
        )
        self.ui_components["scan_start_delay"] = scan_delay_spin
        layout.addWidget(scan_delay_widget)

        ops_delay_widget, ops_delay_spin = create_spinbox_row(
            "Operations Start Delay",
            self.current_settings["advanced"]["operations_start_delay"],
            0,
            5000,
            "ms",
            "Delay before starting git operations",
            restart_required=True,
        )
        self.ui_components["operations_start_delay"] = ops_delay_spin
        layout.addWidget(ops_delay_widget)

        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    def _create_button_bar(self) -> QWidget:
        """Create the bottom button bar.

        Returns:
            QWidget: Button bar widget
        """
        bar = QWidget()
        bar.setStyleSheet(
            f"""
            QWidget {{
                background-color: {THEME_BG_SECONDARY};
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }}
            """
        )

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Reset to Defaults button
        reset_btn = QPushButton(f"{Icons.REFRESH}  Reset to Defaults")
        reset_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        reset_btn.setFixedHeight(36)
        reset_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        reset_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(247, 118, 142, 0.1);
                color: #f7768e;
                border: 1px solid rgba(247, 118, 142, 0.3);
                border-radius: 4px;
                padding: 6px 16px;
            }}
            QPushButton:hover {{
                background-color: rgba(247, 118, 142, 0.2);
                border: 1px solid #f7768e;
            }}
            QPushButton:pressed {{
                background-color: rgba(247, 118, 142, 0.3);
            }}
            """
        )
        reset_btn.clicked.connect(self._on_reset_clicked)
        layout.addWidget(reset_btn)

        layout.addStretch()

        # Cancel button
        cancel_btn = QPushButton(f"{Icons.CANCEL}  Cancel")
        cancel_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        cancel_btn.setFixedHeight(36)
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.04);
                color: {THEME_TEXT_PRIMARY};
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                padding: 6px 16px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid {COLOR_ORANGE};
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.12);
            }}
            """
        )
        cancel_btn.clicked.connect(self._on_cancel_clicked)
        layout.addWidget(cancel_btn)

        # Save button
        save_btn = QPushButton(f"{Icons.SAVE}  Save")
        save_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        save_btn.setFixedHeight(36)
        save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(158, 206, 106, 0.2);
                color: #9ece6a;
                border: 1px solid rgba(158, 206, 106, 0.5);
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(158, 206, 106, 0.3);
                border: 1px solid #9ece6a;
            }}
            QPushButton:pressed {{
                background-color: rgba(158, 206, 106, 0.4);
            }}
            """
        )
        save_btn.clicked.connect(self._on_save_clicked)
        layout.addWidget(save_btn)

        return bar

    def _on_nav_item_clicked(self, index: int):
        """Handle navigation item selection.

        Args:
            index: Selected navigation item index
        """
        self.stacked_widget.setCurrentIndex(index)

    def _on_add_custom_path(self, list_widget):
        """Handle adding a custom repository path.

        Args:
            list_widget: QListWidget to add path to
        """
        from PyQt6.QtWidgets import QListWidgetItem

        folder = QFileDialog.getExistingDirectory(
            self, "Select Custom Repository Folder"
        )
        if folder:
            # Validate path
            is_valid, error_msg = self.custom_paths_manager.validate_path(folder)
            if not is_valid:
                QMessageBox.warning(self, "Invalid Path", error_msg)
                return

            # Check if already exists
            existing_items = [
                list_widget.item(i).text() for i in range(list_widget.count())
            ]
            if folder in existing_items:
                QMessageBox.warning(
                    self, "Duplicate Path", "This path is already in the list."
                )
                return

            # Add to list widget
            item = QListWidgetItem(folder)
            list_widget.addItem(item)

    def _on_remove_custom_path(self, list_widget, path: str):
        """Handle removing a custom repository path.

        Args:
            list_widget: QListWidget to remove from
            path: Path to remove
        """
        # Find and remove item
        for i in range(list_widget.count()):
            if list_widget.item(i).text() == path:
                list_widget.takeItem(i)
                break

    def _on_add_exclusion(self, list_widget):
        """Handle adding a repository exclusion.

        Args:
            list_widget: QListWidget to add exclusion to
        """
        from PyQt6.QtWidgets import QInputDialog, QListWidgetItem

        repo_name, ok = QInputDialog.getText(
            self,
            "Add Excluded Repository",
            "Enter repository name (not full path):",
        )

        if ok and repo_name:
            # Check if already exists
            existing_items = [
                list_widget.item(i).text() for i in range(list_widget.count())
            ]
            if repo_name in existing_items:
                QMessageBox.warning(
                    self,
                    "Duplicate Exclusion",
                    "This repository is already excluded.",
                )
                return

            # Add to list widget
            item = QListWidgetItem(repo_name)
            list_widget.addItem(item)

    def _on_remove_exclusion(self, list_widget, repo_name: str):
        """Handle removing a repository exclusion.

        Args:
            list_widget: QListWidget to remove from
            repo_name: Repository name to remove
        """
        # Find and remove item
        for i in range(list_widget.count()):
            if list_widget.item(i).text() == repo_name:
                list_widget.takeItem(i)
                break

    def _on_save_clicked(self):
        """Handle Save button click."""
        # Collect values from UI components
        self.current_settings["general"]["github_path"] = self.ui_components[
            "github_path"
        ].text()
        self.current_settings["general"]["window_always_on_top"] = self.ui_components[
            "always_on_top"
        ].isChecked()
        self.current_settings["general"]["window_width"] = self.ui_components[
            "window_width"
        ].value()
        self.current_settings["general"]["window_height"] = self.ui_components[
            "window_height"
        ].value()
        self.current_settings["general"]["auto_close_delay"] = self.ui_components[
            "auto_close_delay"
        ].value()
        self.current_settings["general"][
            "auto_close_no_repos_delay"
        ] = self.ui_components["auto_close_no_repos_delay"].value()

        self.current_settings["git_operations"][
            "powershell_throttle_limit"
        ] = self.ui_components["throttle_limit"].value()
        self.current_settings["git_operations"]["scan_timeout"] = self.ui_components[
            "scan_timeout"
        ].value()
        self.current_settings["git_operations"][
            "operation_timeout"
        ] = self.ui_components["operation_timeout"].value()
        self.current_settings["git_operations"][
            "power_countdown_seconds"
        ] = self.ui_components["power_countdown"].value()
        self.current_settings["git_operations"][
            "exclude_confirmation_timeout"
        ] = self.ui_components["exclude_timeout"].value()

        self.current_settings["appearance"]["font_family"] = self.ui_components[
            "font_family"
        ].text()
        self.current_settings["appearance"]["font_size_title"] = self.ui_components[
            "font_size_title"
        ].value()
        self.current_settings["appearance"]["font_size_header"] = self.ui_components[
            "font_size_header"
        ].value()
        self.current_settings["appearance"]["font_size_label"] = self.ui_components[
            "font_size_label"
        ].value()
        self.current_settings["appearance"]["font_size_stat"] = self.ui_components[
            "font_size_stat"
        ].value()
        self.current_settings["appearance"][
            "enable_animations"
        ] = self.ui_components["enable_animations"].isChecked()
        self.current_settings["appearance"][
            "animation_duration"
        ] = self.ui_components["animation_duration"].value()

        self.current_settings["advanced"]["test_mode_default"] = self.ui_components[
            "test_mode_default"
        ].isChecked()
        self.current_settings["advanced"]["scan_start_delay"] = self.ui_components[
            "scan_start_delay"
        ].value()
        self.current_settings["advanced"][
            "operations_start_delay"
        ] = self.ui_components["operations_start_delay"].value()

        # Save main settings
        success = self.settings_manager.save_settings(self.current_settings)
        if not success:
            QMessageBox.critical(
                self,
                "Save Failed",
                "Failed to save settings. Please check file permissions.",
            )
            return

        # Save custom paths
        custom_paths_list = self.ui_components["custom_paths_list"]
        custom_paths = [
            custom_paths_list.item(i).text()
            for i in range(custom_paths_list.count())
        ]
        self.custom_paths_manager.save_custom_paths(custom_paths)

        # Save exclusions
        exclude_list = self.ui_components["exclude_list"]
        excluded_repos = [
            exclude_list.item(i).text() for i in range(exclude_list.count())
        ]
        self.exclude_manager.save_exclusions(excluded_repos)

        # Check if restart needed
        self.restart_needed = self._check_restart_needed()

        # Emit signal
        self.settings_saved.emit(self.restart_needed)

        # Show confirmation
        if self.restart_needed:
            QMessageBox.information(
                self,
                "Settings Saved",
                "Settings saved successfully.\n\nSome settings require a restart to take effect.",
            )
        else:
            QMessageBox.information(
                self, "Settings Saved", "Settings saved successfully."
            )

        self.accept()

    def _on_cancel_clicked(self):
        """Handle Cancel button click."""
        self.reject()

    def _on_reset_clicked(self):
        """Handle Reset to Defaults button click."""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Are you sure you want to reset all settings to their default values?\n\n"
            "This will:\n"
            "- Reset all application settings\n"
            "- Clear all custom repository paths\n"
            "- Clear all repository exclusions\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Reset settings
            self.settings_manager.reset_to_defaults()

            # Clear custom paths
            self.custom_paths_manager.save_custom_paths([])

            # Clear exclusions
            self.exclude_manager.save_exclusions([])

            QMessageBox.information(
                self,
                "Reset Complete",
                "All settings have been reset to defaults.\n\nPlease restart the application.",
            )

            self.accept()

    def _check_restart_needed(self) -> bool:
        """Check if any restart-required settings have changed.

        Returns:
            bool: True if restart needed, False otherwise
        """
        restart_keys = [
            ("general", "github_path"),
            ("general", "window_width"),
            ("general", "window_height"),
            ("git_operations", "powershell_throttle_limit"),
            ("appearance", "font_family"),
            ("appearance", "font_size_title"),
            ("appearance", "font_size_header"),
            ("appearance", "font_size_label"),
            ("appearance", "font_size_stat"),
            ("appearance", "animation_duration"),
            ("advanced", "scan_start_delay"),
            ("advanced", "operations_start_delay"),
        ]

        for category, key in restart_keys:
            if (
                self.current_settings.get(category, {}).get(key)
                != self.original_settings.get(category, {}).get(key)
            ):
                return True

        # Check custom paths
        original_custom_paths = [
            str(p) for p in self.custom_paths_manager.get_custom_paths()
        ]
        current_custom_paths = [
            self.ui_components["custom_paths_list"].item(i).text()
            for i in range(self.ui_components["custom_paths_list"].count())
        ]
        if original_custom_paths != current_custom_paths:
            return True

        return False
