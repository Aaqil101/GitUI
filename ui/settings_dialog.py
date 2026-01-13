# ----- Built-In Modules-----
from pathlib import Path

# ----- PyQt6 Modules -----
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCursor, QFont, QIcon
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListView,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

# ----- Config Imports -----
from core.config import (
    COLOR_DARK_BLUE,
    COLOR_ORANGE,
    FONT_FAMILY,
    FONT_SIZE_STAT,
    THEME_BG_PRIMARY,
    THEME_BG_SECONDARY,
    THEME_TEXT_PRIMARY,
    THEME_TEXT_SECONDARY,
    PowerOption,
    get_default_paths,
)

# ----- Manager Imports -----
from core.custom_paths_manager import CustomPathsManager
from core.exclude_manager import ExcludeManager
from core.github_path_manager import GitHubPathManager
from core.log_manager import LogManager
from core.settings_manager import SettingsManager

# ----- UI Component Imports -----
from ui.settings_components import (
    HoverIconButton,
    create_checkbox_row,
    create_combobox_row,
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

    def __init__(self, parent=None) -> None:
        """Initialize the settings dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.settings_manager = SettingsManager()
        self.exclude_manager = ExcludeManager()
        self.custom_paths_manager = CustomPathsManager()
        self.github_path_manager = GitHubPathManager()
        self.log_manager = LogManager()

        # Deep copy current settings to allow cancellation
        self.current_settings = self._deep_copy_dict(
            self.settings_manager.get_settings()
        )
        self.original_settings = self._deep_copy_dict(self.current_settings)

        # Store original GitHub path for restart detection
        self.original_github_path = str(self.github_path_manager.get_github_path())

        # Store original custom paths for restart detection
        self.original_custom_paths = [
            str(p) for p in self.custom_paths_manager.get_custom_paths()
        ]

        self.restart_needed = False

        # UI component references (populated in page creation methods)
        self.ui_components = {}

        # Side panel collapse state
        self.is_collapsed = False

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

    def _get_modern_scrollbar_style(self) -> str:
        """Get modern scrollbar stylesheet with Tokyo Night theme.

        Returns:
            str: Modern scrollbar stylesheet
        """
        return f"""
            QScrollArea {{
                border: none;
                background-color: {THEME_BG_PRIMARY};
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {THEME_BG_PRIMARY};
            }}

            /* Vertical Scrollbar */
            QScrollBar:vertical {{
                background-color: transparent;
                width: 12px;
                margin: 4px 2px 4px 2px;
                border-radius: 6px;
            }}

            /* Scrollbar Handle (Thumb) */
            QScrollBar::handle:vertical {{
                background-color: rgba(122, 162, 247, 0.3);
                border-radius: 6px;
                min-height: 30px;
                margin: 0px 2px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: rgba(122, 162, 247, 0.5);
            }}

            QScrollBar::handle:vertical:pressed {{
                background-color: rgba(122, 162, 247, 0.7);
            }}

            /* Remove arrow buttons */
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
                border: none;
            }}

            /* Scrollbar background track */
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: rgba(255, 255, 255, 0.02);
                border-radius: 6px;
            }}

            /* Horizontal Scrollbar (if needed) */
            QScrollBar:horizontal {{
                background-color: transparent;
                height: 12px;
                margin: 2px 4px 2px 4px;
                border-radius: 6px;
            }}

            QScrollBar::handle:horizontal {{
                background-color: rgba(122, 162, 247, 0.3);
                border-radius: 6px;
                min-width: 30px;
                margin: 2px 0px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background-color: rgba(122, 162, 247, 0.5);
            }}

            QScrollBar::handle:horizontal:pressed {{
                background-color: rgba(122, 162, 247, 0.7);
            }}

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
                background: none;
                border: none;
            }}

            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {{
                background: rgba(255, 255, 255, 0.02);
                border-radius: 6px;
            }}
        """

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("Settings")
        self.setFixedSize(900, 600)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setModal(True)

        # Set window icon
        paths: dict[str, Path] = get_default_paths()
        self.setWindowIcon(QIcon(str(paths["app_icon"])))

        # Main layout
        main_layout = QVBoxLayout(self)
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

        # Tab widget
        self.tab_widget = self._create_tab_widget()
        main_layout.addWidget(self.tab_widget, 1)

        # Bottom button bar
        button_bar = self._create_button_bar()
        main_layout.addWidget(button_bar)

        # Center dialog on screen
        position_center(self)

    def _create_tab_label_widget(self, icon: str, text: str) -> QWidget:
        """Create a custom tab label widget with larger icon.

        Args:
            icon: Icon character
            text: Tab text

        Returns:
            QWidget: Tab label widget with separate icon and text
        """
        widget = QWidget()
        widget.setFixedWidth(187)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Add left stretch to center content
        layout.addStretch()

        # Icon label with larger font
        icon_label = QLabel(icon)
        icon_label.setFont(QFont(FONT_FAMILY, 16))
        layout.addWidget(icon_label)

        # Text label with normal font
        text_label = QLabel(text)
        text_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        layout.addWidget(text_label)

        # Add right stretch to center content
        layout.addStretch()

        return widget

    def _create_tab_widget(self) -> QTabWidget:
        """Create the tab widget with settings pages.

        Returns:
            QTabWidget: Tab widget with all settings pages
        """
        tab_widget = QTabWidget()
        tab_widget.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))

        # Modern tab bar styling
        tab_widget.setStyleSheet(
            f"""
            QTabWidget::pane {{
                background-color: {THEME_BG_PRIMARY};
            }}
            QTabBar::tab {{
                background-color: {THEME_BG_SECONDARY};
                color: {THEME_TEXT_SECONDARY};
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: normal;
            }}
            QTabBar::tab:hover {{
                background-color: rgba(122, 162, 247, 0.1);
                color: {THEME_TEXT_PRIMARY};
            }}
            QTabBar::tab:selected {{
                background-color: rgba(122, 162, 247, 0.2);
                color: {THEME_TEXT_PRIMARY};
                font-weight: bold;
            }}
            QTabBar:focus {{
                background-color: rgba(122, 162, 247, 0.1);
                color: {THEME_TEXT_PRIMARY};
                outline: none;
            }}
            """
        )

        # Add tabs with custom widgets for larger icons
        idx: int = tab_widget.addTab(self._create_general_page(), "")
        tab_widget.tabBar().setTabButton(
            idx,
            tab_widget.tabBar().ButtonPosition.LeftSide,
            self._create_tab_label_widget(Icons.FOLDER, "General"),
        )

        idx = tab_widget.addTab(self._create_git_ops_page(), "")
        tab_widget.tabBar().setTabButton(
            idx,
            tab_widget.tabBar().ButtonPosition.LeftSide,
            self._create_tab_label_widget(Icons.GIT, "Git Operations"),
        )

        idx = tab_widget.addTab(self._create_appearance_page(), "")
        tab_widget.tabBar().setTabButton(
            idx,
            tab_widget.tabBar().ButtonPosition.LeftSide,
            self._create_tab_label_widget(Icons.PALETTE, "Appearance"),
        )

        idx = tab_widget.addTab(self._create_advanced_page(), "")
        tab_widget.tabBar().setTabButton(
            idx,
            tab_widget.tabBar().ButtonPosition.LeftSide,
            self._create_tab_label_widget(Icons.ADVANCED, "Advanced"),
        )

        return tab_widget

    def _create_general_page(self) -> QWidget:
        """Create the General settings page.

        Returns:
            QWidget: General settings page
        """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet(self._get_modern_scrollbar_style())

        content = QWidget()
        content.setStyleSheet(f"background-color: {THEME_BG_PRIMARY};")
        layout = QVBoxLayout(content)
        layout.setSpacing(12)  # Reduced from 20
        layout.setContentsMargins(20, 16, 20, 16)  # Reduced from 24, 20, 24, 20

        # Repository Paths Section
        layout.addWidget(create_settings_section("Repository Paths", Icons.FOLDER))

        # Add current username display
        username_label = QLabel(
            f"{Icons.USER}  Current User: {self.github_path_manager.get_current_user_name()}"
        )
        username_label.setStyleSheet(
            f"color: {COLOR_ORANGE}; font-size: {FONT_SIZE_STAT}pt; font-family: '{FONT_FAMILY}'; padding: 4px 8px;"
        )
        layout.addWidget(username_label)

        github_path_widget, github_path_edit = create_path_selector(
            "GitHub Repositories Folder (username-specific)",
            str(self.github_path_manager.get_github_path()),
            lambda: None,  # No real-time callback needed
        )
        self.ui_components["github_path"] = github_path_edit
        layout.addWidget(github_path_widget)

        # Custom Repository Paths - Button to open manager window
        custom_paths_count: int = len(self.custom_paths_manager.get_custom_paths())
        custom_paths_btn = self._create_manager_button(
            "Custom Repository Paths",
            Icons.REPOSITORY,
            f"{custom_paths_count} path{'s' if custom_paths_count != 1 else ''} configured",
            self._open_custom_paths_manager,
        )
        layout.addWidget(custom_paths_btn)

        # Repository Exclusions Section
        layout.addWidget(
            create_settings_section("Repository Exclusions", Icons.EXCLUDE)
        )

        # Username display
        username_label = QLabel(
            f"Current User: {self.exclude_manager.get_current_user_name()}"
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

        # Excluded repositories - Button to open manager window
        excluded_count: int = len(self.exclude_manager.get_excluded_repos())
        exclusions_btn = self._create_manager_button(
            "Excluded Repositories",
            Icons.REPOSITORY,
            f"{excluded_count} repositor{'ies' if excluded_count != 1 else 'y'} excluded",
            self._open_exclusions_manager,
        )
        layout.addWidget(exclusions_btn)

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
        scroll.setStyleSheet(self._get_modern_scrollbar_style())

        content = QWidget()
        content.setStyleSheet(f"background-color: {THEME_BG_PRIMARY};")
        layout = QVBoxLayout(content)
        layout.setSpacing(12)  # Reduced from 20
        layout.setContentsMargins(20, 16, 20, 16)  # Reduced from 24, 20, 24, 20

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

        # Default Power Option dropdown
        power_options = [
            (
                PowerOption.SHUTDOWN.value,
                PowerOption.get_display_name(PowerOption.SHUTDOWN),
            ),
            (
                PowerOption.RESTART.value,
                PowerOption.get_display_name(PowerOption.RESTART),
            ),
            (
                PowerOption.SHUTDOWN_CANCEL.value,
                PowerOption.get_display_name(PowerOption.SHUTDOWN_CANCEL),
            ),
            (
                PowerOption.RESTART_CANCEL.value,
                PowerOption.get_display_name(PowerOption.RESTART_CANCEL),
            ),
        ]
        default_power_widget, default_power_combo = create_combobox_row(
            "Default Power Option",
            power_options,
            self.current_settings["git_operations"].get(
                "default_power_option", "shutdown"
            ),
            "Power option auto-selected when countdown expires (Git Push only)",
        )
        self.ui_components["default_power_option"] = default_power_combo
        layout.addWidget(default_power_widget)

        # Repository Exclusions Section
        layout.addWidget(
            create_settings_section("Repository Exclusions", Icons.EXCLUDE)
        )

        exclude_pull_widget, exclude_pull_check = create_checkbox_row(
            "Apply Exclusions to Git Pull",
            self.current_settings["git_operations"]["exclude_repos_affect_pull"],
            "If enabled, excluded repositories will be skipped during Git Pull operations",
        )
        self.ui_components["exclude_repos_affect_pull"] = exclude_pull_check
        layout.addWidget(exclude_pull_widget)

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
        scroll.setStyleSheet(self._get_modern_scrollbar_style())

        content = QWidget()
        content.setStyleSheet(f"background-color: {THEME_BG_PRIMARY};")
        layout = QVBoxLayout(content)
        layout.setSpacing(12)  # Reduced from 20
        layout.setContentsMargins(20, 16, 20, 16)  # Reduced from 24, 20, 24, 20

        # Font Configuration Section
        layout.addWidget(create_settings_section("Font Configuration", Icons.FONT))

        font_family_widget, font_family_edit = create_path_selector(
            "Font Family (<span style='color:red; font-weight: bold'>requires Nerd Font for icons</span>)",
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

        # Power Options Section
        layout.addWidget(create_settings_section("Power Options", Icons.POWER))

        icon_only_widget, icon_only_check = create_checkbox_row(
            "Icon-Only Power Buttons",
            self.current_settings["appearance"]["power_buttons_icon_only"],
            "Show only icons in power buttons (Git Push). Uncheck to show only text.",
        )
        self.ui_components["power_buttons_icon_only"] = icon_only_check
        layout.addWidget(icon_only_widget)

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
        scroll.setStyleSheet(self._get_modern_scrollbar_style())

        content = QWidget()
        content.setStyleSheet(f"background-color: {THEME_BG_PRIMARY};")
        layout = QVBoxLayout(content)
        layout.setSpacing(12)  # Reduced from 20
        layout.setContentsMargins(20, 16, 20, 16)  # Reduced from 24, 20, 24, 20

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

        # Log Management Section
        layout.addWidget(create_settings_section("Log Management", Icons.FILE))

        # Log stats display
        log_stats = self.log_manager.get_log_stats()
        size_kb = log_stats["total_size_bytes"] / 1024
        size_display = (
            f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
        )

        self.log_stats_label = QLabel(
            f"{Icons.INFO}  {log_stats['total_files']} log files across "
            f"{log_stats['repo_count']} repositories ({size_display})"
        )
        self.log_stats_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        self.log_stats_label.setStyleSheet(
            f"color: {THEME_TEXT_SECONDARY}; padding: 4px 0;"
        )
        layout.addWidget(self.log_stats_label)

        # Auto-delete dropdown
        from core.config import LogAutoDelete

        auto_delete_options = [
            (
                LogAutoDelete.DISABLED.value,
                LogAutoDelete.get_display_name(LogAutoDelete.DISABLED),
            ),
            (
                LogAutoDelete.DAYS_7.value,
                LogAutoDelete.get_display_name(LogAutoDelete.DAYS_7),
            ),
            (
                LogAutoDelete.DAYS_30.value,
                LogAutoDelete.get_display_name(LogAutoDelete.DAYS_30),
            ),
            (
                LogAutoDelete.DAYS_60.value,
                LogAutoDelete.get_display_name(LogAutoDelete.DAYS_60),
            ),
            (
                LogAutoDelete.DAYS_90.value,
                LogAutoDelete.get_display_name(LogAutoDelete.DAYS_90),
            ),
        ]
        auto_delete_widget, auto_delete_combo = create_combobox_row(
            "Auto-Delete Logs",
            auto_delete_options,
            self.current_settings["advanced"].get("log_auto_delete", "disabled"),
            "Automatically delete logs older than selected age on startup",
        )
        self.ui_components["log_auto_delete"] = auto_delete_combo
        layout.addWidget(auto_delete_widget)

        # Clear logs buttons row
        clear_logs_widget = QWidget()
        clear_logs_layout = QHBoxLayout(clear_logs_widget)
        clear_logs_layout.setContentsMargins(0, 4, 0, 4)
        clear_logs_layout.setSpacing(8)

        # Common button style for clear buttons
        clear_btn_style = f"""
            QPushButton {{
                background-color: rgba(247, 118, 142, 0.1);
                color: #f7768e;
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: rgba(247, 118, 142, 0.2);
                border-bottom: 2px solid #f7768e;
            }}
            QPushButton:pressed {{
                background-color: rgba(247, 118, 142, 0.3);
            }}
            QPushButton:focus {{
                background-color: rgba(247, 118, 142, 0.2);
                border-bottom: 2px solid #f7768e;
                outline: none;
            }}
        """

        # Clear logs older than 7 days
        clear_7_days_btn = HoverIconButton(
            normal_icon=Icons.TRASH_OUTLINE,
            hover_icon=Icons.TRASH,
            pressed_icon=Icons.TRASH_OCT,
            text="Older than 7 days",
        )
        clear_7_days_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        clear_7_days_btn.setFixedHeight(32)
        clear_7_days_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        clear_7_days_btn.setStyleSheet(clear_btn_style)
        clear_7_days_btn.clicked.connect(lambda: self._on_clear_logs_clicked(days=7))
        clear_logs_layout.addWidget(clear_7_days_btn)

        # Clear logs older than 30 days
        clear_30_days_btn = HoverIconButton(
            normal_icon=Icons.TRASH_OUTLINE,
            hover_icon=Icons.TRASH,
            pressed_icon=Icons.TRASH_OCT,
            text="Older than 30 days",
        )
        clear_30_days_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        clear_30_days_btn.setFixedHeight(32)
        clear_30_days_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        clear_30_days_btn.setStyleSheet(clear_btn_style)
        clear_30_days_btn.clicked.connect(lambda: self._on_clear_logs_clicked(days=30))
        clear_logs_layout.addWidget(clear_30_days_btn)

        # Clear all logs
        clear_all_btn = HoverIconButton(
            normal_icon=Icons.TRASH_OUTLINE,
            hover_icon=Icons.TRASH,
            pressed_icon=Icons.TRASH_OCT,
            text="Clear All",
        )
        clear_all_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
        clear_all_btn.setFixedHeight(32)
        clear_all_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        clear_all_btn.setStyleSheet(clear_btn_style)
        clear_all_btn.clicked.connect(lambda: self._on_clear_logs_clicked(days=None))
        clear_logs_layout.addWidget(clear_all_btn)

        clear_logs_layout.addStretch()
        layout.addWidget(clear_logs_widget)

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
                border-radius: 4px;
                padding: 6px 16px;
            }}
            QPushButton:hover {{
                background-color: rgba(247, 118, 142, 0.2);
                border-bottom: 2px solid #f7768e;
            }}
            QPushButton:pressed {{
                background-color: rgba(247, 118, 142, 0.3);
            }}
            QPushButton:focus {{
                background-color: rgba(247, 118, 142, 0.2);
                border-bottom: 2px solid #f7768e;
                outline: none;
            }}
            """
        )
        reset_btn.clicked.connect(self._on_reset_clicked)
        layout.addWidget(reset_btn)

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
                border-radius: 4px;
                padding: 6px 16px;
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
                border-radius: 4px;
                padding: 6px 16px;
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

        return bar

    def _create_manager_button(
        self, title: str, icon: str, subtitle: str, callback
    ) -> QWidget:
        """Create a button that opens a manager window.

        Args:
            title: Button title text
            icon: Icon to display
            subtitle: Subtitle/count text
            callback: Function to call when clicked

        Returns:
            QWidget: Button widget
        """
        button = QPushButton()
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        button.setFixedHeight(60)
        button.clicked.connect(callback)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(16, 8, 16, 8)
        button_layout.setSpacing(12)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont(FONT_FAMILY, 16))
        icon_label.setStyleSheet(f"color: {COLOR_ORANGE};")
        button_layout.addWidget(icon_label)

        # Text container
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {THEME_TEXT_PRIMARY};")
        text_layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT - 1))
        subtitle_label.setStyleSheet(f"color: {THEME_TEXT_SECONDARY};")
        text_layout.addWidget(subtitle_label)

        button_layout.addWidget(text_container, 1)

        # Arrow icon
        arrow_label = QLabel(Icons.CHEVRON_RIGHT)
        arrow_label.setFont(QFont(FONT_FAMILY, 14))
        arrow_label.setStyleSheet(f"color: {THEME_TEXT_SECONDARY};")
        button_layout.addWidget(arrow_label)

        # Apply layout to button using a container widget
        container = QWidget()
        container.setLayout(button_layout)
        main_layout = QHBoxLayout(button)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)

        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.04);
                border-radius: 6px;
                border: 1px solid transparent;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 158, 100, 0.3);
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.08);
            }}
            QPushButton:focus {{
                background-color: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 158, 100, 0.3);
                outline: none;
            }}
            """
        )

        return button

    def _open_custom_paths_manager(self) -> None:
        """Open the custom paths manager window."""
        from ui.custom_paths_manager_window import CustomPathsManagerWindow

        dialog = CustomPathsManagerWindow(self)
        dialog.exec()

    def _open_exclusions_manager(self) -> None:
        """Open the exclusions manager window."""
        from ui.exclusions_manager_window import ExclusionsManagerWindow

        dialog = ExclusionsManagerWindow(self)
        dialog.exec()

    def _on_add_custom_path(self, list_widget) -> None:
        """Handle adding custom repository paths (supports multiple selection).

        Args:
            list_widget: QListWidget to add paths to
        """
        from PyQt6.QtWidgets import QListWidgetItem

        # Create file dialog with multi-selection enabled
        dialog = QFileDialog(self)
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
            existing_items = [
                list_widget.item(i).text() for i in range(list_widget.count())
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
                list_widget.addItem(item)
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

    def _on_remove_custom_path(self, list_widget, paths: list[str]) -> None:
        """Handle removing custom repository paths (supports multiple selection).

        Args:
            list_widget: QListWidget to remove from
            paths: List of paths to remove
        """
        # Remove items in reverse order to avoid index issues
        for path in paths:
            for i in range(list_widget.count() - 1, -1, -1):
                if list_widget.item(i).text() == path:
                    list_widget.takeItem(i)
                    break

    def _on_add_exclusion(self, list_widget) -> None:
        """Handle adding repository exclusions (supports multiple, comma-separated).

        Args:
            list_widget: QListWidget to add exclusions to
        """
        from PyQt6.QtWidgets import QListWidgetItem

        from ui.add_exclusion_dialog import AddExclusionDialog

        # Show custom dialog
        dialog = AddExclusionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            repo_names_input = dialog.get_input_text()
        else:
            return

        if repo_names_input:
            # Split by comma and clean up whitespace
            repo_names = [
                name.strip() for name in repo_names_input.split(",") if name.strip()
            ]

            if not repo_names:
                return

            # Get existing items
            existing_items = [
                list_widget.item(i).text() for i in range(list_widget.count())
            ]

            # Track results
            added_count = 0
            duplicate_repos = []

            for repo_name in repo_names:
                # Check if already exists
                if repo_name in existing_items:
                    duplicate_repos.append(repo_name)
                    continue

                # Add to list widget
                item = QListWidgetItem(repo_name)
                list_widget.addItem(item)
                existing_items.append(repo_name)  # Track for duplicate checking
                added_count += 1

            # Show summary if there were any issues
            messages = []
            if added_count > 0:
                messages.append(f"Successfully added {added_count} exclusion(s).")
            if duplicate_repos:
                messages.append(f"\nSkipped {len(duplicate_repos)} duplicate(s):")
                for dup in duplicate_repos[:5]:  # Show max 5
                    messages.append(f"  • {dup}")
                if len(duplicate_repos) > 5:
                    messages.append(f"  ... and {len(duplicate_repos) - 5} more")

            if messages:
                if duplicate_repos and added_count == 0:
                    QMessageBox.warning(self, "Add Exclusions", "\n".join(messages))
                else:
                    QMessageBox.information(self, "Add Exclusions", "\n".join(messages))

    def _on_remove_exclusion(self, list_widget, repo_names: list[str]) -> None:
        """Handle removing repository exclusions (supports multiple selection).

        Args:
            list_widget: QListWidget to remove from
            repo_names: List of repository names to remove
        """
        # Remove items in reverse order to avoid index issues
        for repo_name in repo_names:
            for i in range(list_widget.count() - 1, -1, -1):
                if list_widget.item(i).text() == repo_name:
                    list_widget.takeItem(i)
                    break

    def _on_save_clicked(self) -> None:
        """Handle Save button click."""
        # Collect values from UI components
        new_github_path = self.ui_components["github_path"].text()

        # Validate GitHub path
        is_valid, error_msg = self.github_path_manager.validate_path(new_github_path)
        if not is_valid:
            QMessageBox.warning(
                self,
                "Invalid Path",
                f"GitHub path is invalid:\n{error_msg}",
            )
            return

        # Save GitHub path (username-specific)
        if not self.github_path_manager.save_github_path(new_github_path):
            QMessageBox.critical(
                self,
                "Save Failed",
                "Failed to save GitHub path. Please try again.",
            )
            return

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
        self.current_settings["general"]["auto_close_no_repos_delay"] = (
            self.ui_components["auto_close_no_repos_delay"].value()
        )

        self.current_settings["git_operations"]["powershell_throttle_limit"] = (
            self.ui_components["throttle_limit"].value()
        )
        self.current_settings["git_operations"]["scan_timeout"] = self.ui_components[
            "scan_timeout"
        ].value()
        self.current_settings["git_operations"]["operation_timeout"] = (
            self.ui_components["operation_timeout"].value()
        )
        self.current_settings["git_operations"]["power_countdown_seconds"] = (
            self.ui_components["power_countdown"].value()
        )
        self.current_settings["git_operations"]["default_power_option"] = (
            self.ui_components["default_power_option"].currentData()
        )
        self.current_settings["git_operations"]["exclude_confirmation_timeout"] = (
            self.ui_components["exclude_timeout"].value()
        )
        self.current_settings["git_operations"]["exclude_repos_affect_pull"] = (
            self.ui_components["exclude_repos_affect_pull"].isChecked()
        )

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
        self.current_settings["appearance"]["enable_animations"] = self.ui_components[
            "enable_animations"
        ].isChecked()
        self.current_settings["appearance"]["animation_duration"] = self.ui_components[
            "animation_duration"
        ].value()
        self.current_settings["appearance"]["power_buttons_icon_only"] = (
            self.ui_components["power_buttons_icon_only"].isChecked()
        )

        self.current_settings["advanced"]["test_mode_default"] = self.ui_components[
            "test_mode_default"
        ].isChecked()
        self.current_settings["advanced"]["scan_start_delay"] = self.ui_components[
            "scan_start_delay"
        ].value()
        self.current_settings["advanced"]["operations_start_delay"] = (
            self.ui_components["operations_start_delay"].value()
        )
        self.current_settings["advanced"]["log_auto_delete"] = self.ui_components[
            "log_auto_delete"
        ].currentData()

        # Save main settings
        success: bool = self.settings_manager.save_settings(self.current_settings)
        if not success:
            QMessageBox.critical(
                self,
                "Save Failed",
                "Failed to save settings. Please check file permissions.",
            )
            return

        # Custom paths and exclusions are managed by their dedicated windows
        # No need to save them here as they're saved when user clicks Save in those windows

        # Check if restart needed
        self.restart_needed: bool = self._check_restart_needed()

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

    def _on_cancel_clicked(self) -> None:
        """Handle Cancel button click."""
        self.reject()

    def _on_clear_logs_clicked(self, days: int | None = None) -> None:
        """Handle Clear Logs button click.

        Args:
            days: If provided, only clear logs older than this many days.
                  If None, clear all logs.
        """
        # Get stats based on whether we're clearing by age or all
        if days is not None:
            log_stats = self.log_manager.get_log_stats_by_age(days)
            title = f"Clear Logs Older Than {days} Days"
            description = f"older than {days} days"
        else:
            log_stats = self.log_manager.get_log_stats()
            title = "Clear All Logs"
            description = "all"

        if log_stats["total_files"] == 0:
            if days is not None:
                QMessageBox.information(
                    self,
                    "No Logs",
                    f"There are no log files older than {days} days.",
                )
            else:
                QMessageBox.information(
                    self,
                    "No Logs",
                    "There are no log files to clear.",
                )
            return

        size_kb = log_stats["total_size_bytes"] / 1024
        size_display = (
            f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
        )

        reply = QMessageBox.question(
            self,
            title,
            f"Are you sure you want to delete {description} log files?\n\n"
            f"This will remove:\n"
            f"- {log_stats['total_files']} log files\n"
            f"- From {log_stats['repo_count']} repositories\n"
            f"- Total size: {size_display}\n\n"
            f"This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, files_deleted, error_msg = self.log_manager.clear_logs(days=days)

            if success:
                # Update the stats label with current total stats
                new_stats = self.log_manager.get_log_stats()
                new_size_kb = new_stats["total_size_bytes"] / 1024
                new_size_display = (
                    f"{new_size_kb:.1f} KB"
                    if new_size_kb < 1024
                    else f"{new_size_kb/1024:.2f} MB"
                )
                self.log_stats_label.setText(
                    f"{Icons.INFO}  {new_stats['total_files']} log files across "
                    f"{new_stats['repo_count']} repositories ({new_size_display})"
                )
                QMessageBox.information(
                    self,
                    "Logs Cleared",
                    f"Successfully deleted {files_deleted} log files.",
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to clear logs:\n{error_msg}",
                )

    def _on_reset_clicked(self) -> None:
        """Handle Reset to Defaults button click."""
        from ui.reset_confirmation_dialog import ResetConfirmationDialog

        # Show custom reset confirmation dialog
        dialog = ResetConfirmationDialog(self)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            # Get user's choices
            reset_custom_paths, reset_exclusions = dialog.get_reset_options()

            # Reset settings (always)
            self.settings_manager.reset_to_defaults()

            # Conditionally clear custom paths
            if reset_custom_paths:
                self.custom_paths_manager.save_custom_paths([])

            # Conditionally clear exclusions
            if reset_exclusions:
                self.exclude_manager.save_exclusions([])

            # Build completion message
            reset_items = ["Application settings"]
            if reset_custom_paths:
                reset_items.append("Custom repository paths")
            if reset_exclusions:
                reset_items.append("Repository exclusions")

            items_text = "\n- ".join(reset_items)

            QMessageBox.information(
                self,
                "Reset Complete",
                f"The following have been reset:\n- {items_text}\n\nPlease restart the application.",
            )

            self.accept()

    def _check_restart_needed(self) -> bool:
        """Check if any restart-required settings have changed.

        Returns:
            bool: True if restart needed, False otherwise
        """
        # Check if GitHub path changed (username-specific setting)
        if self.original_github_path != str(self.github_path_manager.get_github_path()):
            return True

        restart_keys: list[tuple[str, str]] = [
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
            if self.current_settings.get(category, {}).get(
                key
            ) != self.original_settings.get(category, {}).get(key):
                return True

        # Check custom paths (compare original with current state from manager)
        current_custom_paths = [
            str(p) for p in self.custom_paths_manager.get_custom_paths()
        ]
        if set(self.original_custom_paths) != set(current_custom_paths):
            return True

        return False
