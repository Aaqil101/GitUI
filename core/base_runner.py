# ----- Built-In Modules -----
import getpass
import random
import sys
from abc import ABCMeta, abstractmethod
from pathlib import Path

# ----- PyQt6 Modules -----
from PyQt6.QtCore import Qt, QThreadPool, QTimer
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# ----- Config Imports -----
from core.config import (
    ANIMATION_INTERVAL,
    BUTTON_HEIGHT,
    CARD_AREA_PADDING,
    COLOR_BLUE,
    COLOR_CYAN,
    COLOR_GREEN,
    FONT_FAMILY,
    FONT_SIZE_HEADER,
    FONT_SIZE_ICON,
    FONT_SIZE_ICON_HEADER,
    FONT_SIZE_ICON_LARGE,
    FONT_SIZE_LABEL,
    FONT_SIZE_STAT,
    FONT_SIZE_SUBTITLE,
    FONT_SIZE_TITLE,
    HEADER_HEIGHT,
    LEFT_PANEL_WIDTH,
    PANEL_MARGINS,
    PANEL_SPACING,
    PROGRESS_COLORS,
    SCAN_START_DELAY,
    SCANNER_PANEL_PADDING,
    SECTION_SPACING,
    STATS_PANEL_PADDING,
    TEST_MODE_START_DELAY,
    THEME_TEXT_SECONDARY,
    TIME_UPDATE_INTERVAL,
    WINDOW_ALWAYS_ON_TOP,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
    get_default_paths,
)

# ----- Component Imports -----
from ui.components import (
    apply_icon_shadow,
    apply_subtitle_shadow,
    apply_title_shadow,
    create_icon_label,
    create_panel_widget,
    create_progress_bar,
    create_stat_row,
    create_text_label,
)

# ----- Style Imports -----
from ui.styles import (
    CARD_CONTAINER_STYLE,
    HEADER_PANEL_STYLE,
    PANEL_STYLE,
    PROGRESS_SEGMENT_DEFAULT_STYLE,
    RETRY_BUTTON_STYLE,
    SCROLL_AREA_STYLE,
    WINDOW_STYLE,
    get_progress_segment_style,
    get_separator_style,
)

# ----- Utils Imports -----
from utils.card import RepoCard
from utils.center import position_center
from utils.check_internet import InternetChecker
from utils.color import Color
from utils.icons import Icons


# Create a compatible metaclass that combines ABCMeta with PyQt's metaclass
class CombinedMeta(type(QWidget), ABCMeta):
    """Metaclass that combines Qt's metaclass with ABCMeta."""

    pass


class BaseGitRunner(InternetChecker, QWidget, metaclass=CombinedMeta):
    """Abstract base class for Git Pull/Push Runner applications."""

    def __init__(self, testing: bool = False) -> None:
        super().__init__()

        self.app = QApplication.instance() or QApplication(sys.argv)

        # Get default paths
        paths = get_default_paths()

        # Config
        self.script_dir: Path = paths["script_dir"]
        self.username: str = getpass.getuser()
        self.msg_icon_path: Path = paths["msg_icon"]
        self.app_icon_path: Path = paths["app_icon"]
        self.github_path: Path = paths["github"]
        self.random_colors: list[str] = Color.random_color()
        self.repositories: list = []
        self._scan_started = False
        self.has_internet = False
        self.is_closing = False
        self.worker = None
        self.testing: bool = testing

        # Get operation-specific configuration
        self.config = self._get_operation_config()

        self._init_ui()

        if not testing:
            self._check_internet_status()
        else:
            self.has_internet = True
            self._update_subtitle("Test Mode", "#bb9af7")

    # ══════════════════════════════════════════════════════════════════
    # ABSTRACT METHODS
    # ══════════════════════════════════════════════════════════════════
    @abstractmethod
    def _get_operation_config(self) -> dict:
        """
        Return operation-specific configuration.

        Returns:
            dict with keys:
                - title: str (e.g., "Git Pull Runner")
                - icon: str (e.g., Icons.GIT_PULL)
                - header_text: str (e.g., "Repositories to Update")
                - stat_labels: dict with keys:
                    - repos: str (e.g., "Repos Behind")
                    - items: str (e.g., "Commits to Pull")
                    - operation_success: str (e.g., "Successfully Pulled")
        """
        pass

    @abstractmethod
    def _show_scan_summary(
        self, repos_count: int, items_count: int, total_scanned: int
    ) -> None:
        """Display operation-specific scan summary."""
        pass

    @abstractmethod
    def _update_stats(
        self, repos_count: int, items_count: int, total_scanned: int
    ) -> None:
        """Update stats panel with operation-specific labels."""
        pass

    @abstractmethod
    def _run_operations(self) -> None:
        """Execute git operations (pull/push)."""
        pass

    @abstractmethod
    def _update_operation_stats(self, success: int, failed: int) -> None:
        """Update operation success/failure stats."""
        pass

    @abstractmethod
    def _populate_test_data(self) -> None:
        """Populate test mode data."""
        pass

    # ══════════════════════════════════════════════════════════════════
    # UI INITIALIZATION
    # ══════════════════════════════════════════════════════════════════
    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle(WINDOW_TITLE)
        if WINDOW_ALWAYS_ON_TOP:
            self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(str(self.app_icon_path)))
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(WINDOW_STYLE)

        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(PANEL_SPACING)
        main_layout.setContentsMargins(*PANEL_MARGINS)

        # Left Panel
        left_panel = QVBoxLayout()
        left_panel.setSpacing(SECTION_SPACING)
        left_panel.setContentsMargins(0, 0, 0, 0)

        left_panel.addWidget(self._create_header())
        left_panel.addWidget(self._create_scanner_panel())
        left_panel.addWidget(self._create_stats_panel())
        left_panel.addStretch()

        left_container = QWidget()
        left_container.setLayout(left_panel)
        left_container.setFixedWidth(LEFT_PANEL_WIDTH)

        # Right Panel
        right_panel = QVBoxLayout()
        right_panel.setSpacing(8)
        right_panel.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QLabel(f"{Icons.FILES}  {self.config['header_text']}")
        header.setFont(QFont(FONT_FAMILY, FONT_SIZE_HEADER, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {COLOR_BLUE}; padding: 4px 0;")
        header.setFixedHeight(32)
        right_panel.addWidget(header)

        right_panel.addWidget(self._create_cards_area())

        right_container = QWidget()
        right_container.setLayout(right_panel)

        main_layout.addWidget(left_container)
        main_layout.addWidget(right_container, 1)

        position_center(self)

    # ══════════════════════════════════════════════════════════════════
    # HEADER
    # ══════════════════════════════════════════════════════════════════
    def _create_header(self) -> QWidget:
        """Create a stylized header with icon, title and subtle subtitle."""
        widget = create_panel_widget(min_height=HEADER_HEIGHT)
        widget.setStyleSheet(HEADER_PANEL_STYLE)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        # Top row: icon + title
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Randomize title and icon colors
        title_icon_color: str = random.choice(self.random_colors)

        icon_label = create_icon_label(
            self.config["icon"], FONT_SIZE_ICON_HEADER, title_icon_color
        )
        icon_label.setStyleSheet(f"color: {title_icon_color}; font-weight: bold;")
        apply_icon_shadow(icon_label)
        top_layout.addWidget(icon_label, 0)

        title = create_text_label(
            self.config["title"],
            FONT_SIZE_TITLE,
            title_icon_color,
            bold=True,
            alignment=Qt.AlignmentFlag.AlignHCenter,
        )
        title.setStyleSheet(
            f"color: {title_icon_color}; letter-spacing: 1px; font-weight: bold;"
        )
        apply_title_shadow(title)
        top_layout.addWidget(title, 1)

        layout.addLayout(top_layout)

        # Bottom: subtitle with internet status
        self.subtitle_label = QLabel()
        self.subtitle_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_SUBTITLE))
        self.subtitle_label.setStyleSheet(
            f"color: {THEME_TEXT_SECONDARY}; letter-spacing: 0.2px; font-weight: bold;"
        )
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        apply_subtitle_shadow(self.subtitle_label)

        layout.addWidget(self.subtitle_label)

        return widget

    def _update_subtitle(self, status_text: str, status_color: str) -> None:
        """Update the subtitle with status information."""
        path_str = str(self.github_path)

        home = str(Path.home())

        # Replace home directory with ~
        if path_str.startswith(home):
            path_str: str = "~" + path_str[len(home) :]

        # Optional: shorten if still too long
        if len(path_str) > 35:
            path_str: str = "..." + path_str[-32:]

        self.subtitle_label.setText(
            f"{self.username} • {path_str} • "
            f"<span style='color: {status_color};'>{status_text}</span>"
        )

    # ══════════════════════════════════════════════════════════════════
    # SCANNER PANEL
    # ══════════════════════════════════════════════════════════════════
    def _create_scanner_panel(self) -> QWidget:
        """Create the scanner panel with progress bar."""
        widget = QWidget()
        widget.setStyleSheet(PANEL_STYLE)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(*SCANNER_PANEL_PADDING)
        layout.setSpacing(12)

        # Row 1: Status
        row1 = QHBoxLayout()
        row1.setSpacing(12)
        row1.setContentsMargins(0, 0, 0, 0)

        self.scan_icon = create_icon_label(
            Icons.SEARCH, FONT_SIZE_ICON_LARGE, Color.SCANNING, fixed_size=(24, 24)
        )
        row1.addWidget(self.scan_icon)

        self.scan_status = create_text_label(
            "Scanning repositories...",
            FONT_SIZE_LABEL,
            Color.SCANNING,
            bold=True,
        )
        self.scan_status.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        row1.addWidget(self.scan_status, 1)

        self.time_label = create_text_label(
            "0.0s",
            FONT_SIZE_LABEL,
            Color.COMPLETE,
            bold=True,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            fixed_width=60,
        )
        row1.addWidget(self.time_label)

        layout.addLayout(row1)

        # Row 2: Progress
        row2 = QHBoxLayout()
        row2.setSpacing(12)
        row2.setContentsMargins(0, 0, 0, 0)

        self.folder_icon = create_icon_label(
            Icons.FOLDER_OPEN, FONT_SIZE_ICON, COLOR_BLUE, fixed_size=(28, 28)
        )
        row2.addWidget(self.folder_icon)

        self.progress_label = create_text_label(
            "0/0", FONT_SIZE_LABEL, COLOR_BLUE, bold=True, fixed_width=50
        )
        row2.addWidget(self.progress_label)

        # Progress bar
        bar_container, self.progress_segments = create_progress_bar()
        row2.addWidget(bar_container, 1)

        layout.addLayout(row2)

        # Row 3: Summary (hidden initially)
        self.summary_widget = QWidget()
        self.summary_widget.setVisible(False)

        summary_layout = QHBoxLayout(self.summary_widget)
        summary_layout.setContentsMargins(0, 4, 0, 0)
        summary_layout.setSpacing(20)

        self.summary_repos = create_text_label(
            f"{Icons.GIT_BRANCH} 0 repos", FONT_SIZE_STAT, COLOR_BLUE
        )
        summary_layout.addWidget(self.summary_repos)

        self.summary_commits = create_text_label(
            f"{Icons.GIT_COMMIT} 0 commits", FONT_SIZE_STAT, COLOR_GREEN
        )
        summary_layout.addWidget(self.summary_commits)

        summary_layout.addStretch()

        layout.addWidget(self.summary_widget)

        # Row 4: Retry button (hidden)
        self.retry_button = QPushButton(f"{Icons.REFRESH}  Retry Connection")
        self.retry_button.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT, QFont.Weight.Bold))
        self.retry_button.setFixedHeight(BUTTON_HEIGHT)
        self.retry_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.retry_button.setStyleSheet(RETRY_BUTTON_STYLE)
        self.retry_button.clicked.connect(self._on_retry_clicked)
        self.retry_button.setVisible(False)
        layout.addWidget(self.retry_button)

        # Animation timer
        self.dot_timer = QTimer()
        self.dot_timer.timeout.connect(self._animate_progress)
        self.bar_anim_index = 0

        return widget

    def _animate_progress(self) -> None:
        """Animate the progress bar."""
        sweep: int = self.bar_anim_index % (len(self.progress_segments) + 2)

        for i, seg in enumerate(self.progress_segments):
            if sweep - 1 <= i <= sweep:
                c: str = PROGRESS_COLORS[
                    (self.bar_anim_index + i) % len(PROGRESS_COLORS)
                ]
                seg.setStyleSheet(get_progress_segment_style(c))
            else:
                seg.setStyleSheet(PROGRESS_SEGMENT_DEFAULT_STYLE)

        self.bar_anim_index += 1

    def _set_progress_complete(self, color: str = COLOR_GREEN) -> None:
        """Set progress bar to complete state."""
        for seg in self.progress_segments:
            seg.setStyleSheet(get_progress_segment_style(color))
        self.folder_icon.setStyleSheet(f"color: {color}; padding: 0;")

    def _update_scan_status(
        self, text: str, color: str, icon: str = Icons.SEARCH
    ) -> None:
        """Update the scan status display."""
        self.scan_icon.setText(icon)
        self.scan_icon.setStyleSheet(f"color: {color}; padding: 0;")
        self.scan_status.setText(text)
        self.scan_status.setStyleSheet(
            f"color: {color}; padding: 0; font-weight: bold;"
        )

    # ══════════════════════════════════════════════════════════════════
    # STATS PANEL
    # ══════════════════════════════════════════════════════════════════
    def _create_stats_panel(self) -> QWidget:
        """Create the statistics panel."""
        widget = QWidget()
        widget.setStyleSheet(PANEL_STYLE)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(*STATS_PANEL_PADDING)
        layout.setSpacing(10)

        # Title
        title = create_text_label(
            f"{Icons.INFO}  Repository Statistics",
            FONT_SIZE_ICON,
            COLOR_CYAN,
            bold=True,
        )
        layout.addWidget(title)

        # Stats
        stat_labels = self.config["stat_labels"]
        self.stat_scanned = create_stat_row(
            Icons.FOLDER_OPEN, "Repositories Scanned", "0", COLOR_BLUE
        )
        self.stat_behind = create_stat_row(
            Icons.GIT_BRANCH, stat_labels["repos"], "0", "#e0af68"
        )
        self.stat_commits = create_stat_row(
            Icons.GIT_COMMIT, stat_labels["items"], "0", COLOR_GREEN
        )

        layout.addWidget(self.stat_scanned)
        layout.addWidget(self.stat_behind)
        layout.addWidget(self.stat_commits)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(get_separator_style())
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        self.stat_success = create_stat_row(
            Icons.CHECK, stat_labels["operation_success"], "0", COLOR_GREEN
        )
        self.stat_failed = create_stat_row(Icons.CROSS, "Failed", "0", "#f7768e")

        layout.addWidget(self.stat_success)
        layout.addWidget(self.stat_failed)

        return widget

    # ══════════════════════════════════════════════════════════════════
    # CARDS AREA
    # ══════════════════════════════════════════════════════════════════
    def _create_cards_area(self) -> QScrollArea:
        """Create the scrollable cards area."""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet(SCROLL_AREA_STYLE)

        self.cards_container = QWidget()
        self.cards_container.setStyleSheet(CARD_CONTAINER_STYLE)

        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setContentsMargins(*CARD_AREA_PADDING)
        self.cards_layout.addStretch()

        self.scroll_area.setWidget(self.cards_container)
        self.cards: dict[int, RepoCard] = {}

        return self.scroll_area

    def _update_card(self, row: int, name: str, status: str, behind: int = 0) -> None:
        """Update or create a repository card."""
        if row in self.cards:
            self.cards[row].set_status(status)
        else:
            card = RepoCard(name, behind, self.cards_container)
            card.set_status(status)
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
            self.cards[row] = card
            card.animate_fade_in(delay_ms=row * 50)

    def _clear_cards(self) -> None:
        """Clear all repository cards."""
        for card in self.cards.values():
            card.setParent(None)
            card.deleteLater()
        self.cards.clear()

    # ══════════════════════════════════════════════════════════════════
    # SCANNING
    # ══════════════════════════════════════════════════════════════════
    def _setup_scanner(self) -> None:
        """Setup the scanner thread pool."""
        self.threadpool = QThreadPool()
        self.scan_start_time = None

    def _start_scan(self) -> None:
        """Start the scanning process."""
        if not self.has_internet or self.is_closing:
            return

        import time

        self._setup_scanner()
        self.scan_start_time: float = time.time()

        self.dot_timer.start(ANIMATION_INTERVAL)

        self.time_update_timer = QTimer()
        self.time_update_timer.timeout.connect(self._update_scan_time)
        self.time_update_timer.start(TIME_UPDATE_INTERVAL)

        # Subclasses should override to create their specific scanner
        # This will be handled in the scan completion

    def _update_scan_time(self) -> None:
        """Update the elapsed scan time display."""
        if self.is_closing or not self.scan_start_time:
            return
        import time

        elapsed: float = time.time() - self.scan_start_time
        self.time_label.setText(f"{elapsed:.1f}s")

    def _on_progress_update(self, current: int, total: int) -> None:
        """Handle progress updates from scanner."""
        if not self.is_closing:
            self.progress_label.setText(f"{current}/{total}")

    def _on_scan_error(self, error_msg: str) -> None:
        """Handle scan errors."""
        if self.is_closing:
            return

        self.dot_timer.stop()
        if hasattr(self, "time_update_timer"):
            self.time_update_timer.stop()

        self._update_scan_status("Scan failed", Color.FAILED, Icons.CROSS)
        print(f"Scan error: {error_msg}")

    def _update_card_status(self, row: int, status: str) -> None:
        """Update a card's status."""
        if row in self.cards:
            self.cards[row].set_status(status)

    # ══════════════════════════════════════════════════════════════════
    # TEST MODE
    # ══════════════════════════════════════════════════════════════════
    def _simulate_transitions(self) -> None:
        """Simulate status transitions for test mode."""
        transitions = [
            (500, 0, "QUEUED"),
            (1000, 0, "SUCCESS"),
            (1200, 1, "SUCCESS"),
            (1800, 5, "QUEUED"),
            (2500, 5, "SUCCESS"),
        ]
        for delay, row, status in transitions:
            QTimer.singleShot(
                delay, lambda r=row, s=status: self._update_card_status(r, s)
            )

    # ══════════════════════════════════════════════════════════════════
    # EVENTS
    # ══════════════════════════════════════════════════════════════════
    def showEvent(self, event) -> None:
        """Handle window show event."""
        super().showEvent(event)
        if not self._scan_started:
            self._scan_started = True
            if self.testing:
                QTimer.singleShot(TEST_MODE_START_DELAY, self._populate_test_data)
            elif self.has_internet:
                QTimer.singleShot(SCAN_START_DELAY, self._start_scan)

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        self.is_closing = True

        for timer_name in ["dot_timer", "time_update_timer"]:
            if hasattr(self, timer_name):
                timer = getattr(self, timer_name)
                if timer.isActive():
                    timer.stop()

        if self.worker and hasattr(self.worker, "cancel"):
            self.worker.cancel()

        if hasattr(self, "threadpool"):
            self.threadpool.waitForDone(3000)

        self.worker = None
        event.accept()
