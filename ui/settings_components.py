# ----- PyQt6 Modules -----
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

# ----- Config Imports -----
from core.config import (
    COLOR_DARK_BLUE,
    COLOR_ORANGE,
    FONT_FAMILY,
    FONT_SIZE_LABEL,
    FONT_SIZE_STAT,
    THEME_TEXT_PRIMARY,
    THEME_TEXT_SECONDARY,
)

# ----- Utils Imports -----
from utils.icons import Icons


# ══════════════════════════════════════════════════════════════════
# CUSTOM BUTTON CLASSES
# ══════════════════════════════════════════════════════════════════
class HoverIconButton(QPushButton):
    """QPushButton subclass that changes icon on hover and press states.

    This button displays different icons based on user interaction:
    - Normal state: Shows normal_icon
    - Hover state: Shows hover_icon
    - Pressed state: Shows pressed_icon (if provided, otherwise uses hover_icon)

    Args:
        normal_icon: Icon to display in normal state
        hover_icon: Icon to display on hover
        pressed_icon: Optional icon to display when pressed (defaults to hover_icon)
        text: Button text (default: empty string)
        parent: Parent widget (default: None)
    """

    def __init__(
        self,
        normal_icon: str,
        hover_icon: str,
        pressed_icon: str = "",
        text: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(text, parent)
        self.normal_icon: str = normal_icon
        self.hover_icon: str = hover_icon
        self.pressed_icon: str = pressed_icon if pressed_icon else hover_icon
        self._is_hovered = False
        self._is_pressed = False

        # Set initial text with normal icon
        self._update_text()

        # Connect pressed/released signals for click state tracking
        self.pressed.connect(self._on_pressed)
        self.released.connect(self._on_released)

    def _update_text(self) -> None:
        """Update button text based on current state."""
        # Extract text without icon (text after " " if present)
        text_parts: list[str] = self.text().split(" ", 1)
        label_text: str = text_parts[1] if len(text_parts) > 1 else text_parts[0]

        # Determine which icon to show
        if self._is_pressed:
            icon: str = self.pressed_icon
        elif self._is_hovered:
            icon: str = self.hover_icon
        else:
            icon: str = self.normal_icon

        # Set text with icon (only if we have label text)
        if label_text and not label_text.startswith(
            (self.normal_icon, self.hover_icon, self.pressed_icon)
        ):
            self.setText(f"{icon} {label_text}")
        else:
            self.setText(icon)

    def enterEvent(self, event: QEvent) -> None:
        """Handle mouse enter event."""
        self._is_hovered = True
        self._update_text()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """Handle mouse leave event."""
        self._is_hovered = False
        self._is_pressed = False  # Reset pressed state when leaving
        self._update_text()
        super().leaveEvent(event)

    def _on_pressed(self) -> None:
        """Handle button pressed signal."""
        self._is_pressed = True
        self._update_text()

    def _on_released(self) -> None:
        """Handle button released signal."""
        self._is_pressed = False
        self._update_text()


# ══════════════════════════════════════════════════════════════════
# SECTION HEADERS
# ══════════════════════════════════════════════════════════════════
def create_settings_section(title: str, icon: str = "") -> QWidget:
    """Create a section header with icon.

    Args:
        title: Section title text
        icon: Optional Nerd Font icon

    Returns:
        QWidget: Section header widget
    """
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 8, 0, 4)  # Reduced from 12, 8
    layout.setSpacing(8)

    # Icon (if provided)
    if icon:
        icon_label = QLabel(icon)
        icon_label.setFont(QFont(FONT_FAMILY, 18))  # Larger icon size
        icon_label.setStyleSheet(f"color: {COLOR_ORANGE}; padding: 0;")
        layout.addWidget(icon_label)

    # Title
    title_label = QLabel(title)
    title_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_LABEL + 1, QFont.Weight.Bold))
    title_label.setStyleSheet(f"color: {THEME_TEXT_PRIMARY}; padding: 0;")
    layout.addWidget(title_label)

    layout.addStretch()

    return widget


# ══════════════════════════════════════════════════════════════════
# PATH SELECTOR
# ══════════════════════════════════════════════════════════════════
def create_path_selector(label: str, value: str, callback) -> tuple[QWidget, QLineEdit]:
    """Create a path selector with label, text field, and browse button.

    Args:
        label: Label text
        value: Initial path value
        callback: Function to call when path changes

    Returns:
        tuple: (widget, line_edit) - widget for layout, line_edit for reading value
    """
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 2, 0, 2)  # Reduced from 4, 4
    layout.setSpacing(4)  # Reduced from 6

    # Label
    label_widget = QLabel(label)
    label_widget.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
    label_widget.setStyleSheet(f"color: {THEME_TEXT_SECONDARY}; padding: 0;")
    layout.addWidget(label_widget)

    # Path row (text field + browse button)
    path_row = QWidget()
    path_layout = QHBoxLayout(path_row)
    path_layout.setContentsMargins(0, 0, 0, 0)
    path_layout.setSpacing(8)

    # Text field
    line_edit = QLineEdit(value)
    line_edit.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
    line_edit.setStyleSheet(
        f"""
        QLineEdit {{
            background-color: rgba(255, 255, 255, 0.04);
            color: {THEME_TEXT_PRIMARY};
            border-radius: 4px;
            padding: 6px 10px;
            border: 2px solid transparent;
        }}
        QLineEdit:focus {{
            background-color: #222;
            border-bottom: 2px solid {COLOR_DARK_BLUE};
            border-right: 2px solid {COLOR_DARK_BLUE};
            font-style: unset;
        }}
        """
    )
    line_edit.textChanged.connect(callback)
    path_layout.addWidget(line_edit, 1)

    # Browse button
    browse_btn = HoverIconButton(
        normal_icon=Icons.FOLDER_OUTLINE,
        hover_icon=Icons.FOLDER,
        pressed_icon=Icons.FOLDER_OPEN,
        text="Browse",
    )
    browse_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
    browse_btn.setFixedHeight(32)
    browse_btn.setStyleSheet(
        f"""
        QPushButton {{
            background-color: rgba(255, 255, 255, 0.04);
            color: {THEME_TEXT_PRIMARY};
            border-radius: 4px;
            padding: 4px 12px;
        }}
        QPushButton:hover {{
            background-color: rgba(255, 255, 255, 0.08);
            border-bottom: 2px solid {COLOR_DARK_BLUE};
        }}
        QPushButton:pressed {{
            background-color: rgba(255, 255, 255, 0.12);
        }}
        """
    )

    def on_browse() -> None:
        folder: str = QFileDialog.getExistingDirectory(
            widget, "Select Folder", line_edit.text()
        )
        if folder:
            line_edit.setText(folder)

    browse_btn.clicked.connect(on_browse)
    path_layout.addWidget(browse_btn)

    layout.addWidget(path_row)

    return widget, line_edit


# ══════════════════════════════════════════════════════════════════
# SPINBOX ROW
# ══════════════════════════════════════════════════════════════════
def create_spinbox_row(
    label: str,
    value: int,
    min_val: int,
    max_val: int,
    suffix: str = "",
    tooltip: str = "",
    restart_required: bool = False,
) -> tuple[QWidget, QSpinBox]:
    """Create a labeled spinbox row.

    Args:
        label: Label text
        value: Initial value
        min_val: Minimum value
        max_val: Maximum value
        suffix: Optional suffix text (e.g., "ms", "px")
        tooltip: Optional tooltip text
        restart_required: Show restart indicator

    Returns:
        tuple: (widget, spinbox) - widget for layout, spinbox for reading value
    """
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 4, 0, 4)
    layout.setSpacing(12)

    # Label
    label_widget = QLabel(label)
    label_widget.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
    label_widget.setStyleSheet(f"color: {THEME_TEXT_SECONDARY}; padding: 0;")
    if tooltip:
        label_widget.setToolTip(tooltip)
    layout.addWidget(label_widget, 1)

    # Spinbox
    spinbox = QSpinBox()
    spinbox.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
    spinbox.setRange(min_val, max_val)
    spinbox.setValue(value)
    spinbox.setFixedWidth(150)
    if suffix:
        spinbox.setSuffix(f" {suffix}")
    spinbox.setStyleSheet(
        f"""
        QSpinBox {{
            background-color: rgba(255, 255, 255, 0.04);
            color: {THEME_TEXT_PRIMARY};
            border-radius: 4px;
            padding: 4px 8px;
        }}
        QSpinBox:focus {{
            border: 1px solid {COLOR_ORANGE};
        }}
        QSpinBox::up-button, QSpinBox::down-button {{
            background-color: rgba(255, 255, 255, 0.04);
            border: none;
            width: 16px;
        }}
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
            background-color: rgba(255, 255, 255, 0.08);
        }}
        """
    )
    if tooltip:
        spinbox.setToolTip(tooltip)
    layout.addWidget(spinbox)

    # Restart indicator
    if restart_required:
        restart_label = create_restart_indicator()
        layout.addWidget(restart_label)

    return widget, spinbox


# ══════════════════════════════════════════════════════════════════
# CHECKBOX ROW
# ══════════════════════════════════════════════════════════════════
def create_checkbox_row(
    label: str, checked: bool, tooltip: str = ""
) -> tuple[QWidget, QCheckBox]:
    """Create a labeled checkbox row.

    Args:
        label: Label text
        checked: Initial checked state
        tooltip: Optional tooltip text

    Returns:
        tuple: (widget, checkbox) - widget for layout, checkbox for reading value
    """
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 4, 0, 4)
    layout.setSpacing(12)

    # Checkbox
    checkbox = QCheckBox(label)
    checkbox.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
    checkbox.setChecked(checked)
    checkbox.setStyleSheet(
        f"""
        QCheckBox {{
            color: {THEME_TEXT_SECONDARY};
            spacing: 8px;
            padding: 4px;
            border-radius: 4px;
        }}
        QCheckBox:hover {{
            background-color: rgba(255, 158, 100, 0.08);
            color: {THEME_TEXT_PRIMARY};
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 3px;
            background-color: rgba(255, 255, 255, 0.04);
            border: 1px solid transparent;
        }}
        QCheckBox::indicator:checked {{
            image: url(assets/Check.png);
            background-color: {COLOR_ORANGE};
            border: 1px solid {COLOR_ORANGE};
        }}
        QCheckBox::indicator:hover {{
            border: 1px solid {COLOR_ORANGE};
        }}
        """
    )
    if tooltip:
        checkbox.setToolTip(tooltip)
    layout.addWidget(checkbox)

    layout.addStretch()

    return widget, checkbox


# ══════════════════════════════════════════════════════════════════
# RESTART INDICATOR
# ══════════════════════════════════════════════════════════════════
def create_restart_indicator() -> QLabel:
    """Create a 'Requires restart' indicator badge.

    Returns:
        QLabel: Restart indicator label
    """
    label = QLabel(f"{Icons.REFRESH}  Restart required")
    label.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT - 1))
    label.setStyleSheet(
        f"""
        QLabel {{
            color: {COLOR_ORANGE};
            background-color: rgba(255, 158, 100, 0.1);
            border: 1px solid {COLOR_ORANGE};
            border-radius: 3px;
            padding: 2px 6px;
        }}
        """
    )
    return label


# ══════════════════════════════════════════════════════════════════
# LIST MANAGER
# ══════════════════════════════════════════════════════════════════
def create_list_manager(
    title: str, items: list[str], add_callback, remove_callback
) -> tuple[QWidget, QListWidget]:
    """Create a list manager with Add/Remove buttons.

    Args:
        title: List title
        items: Initial list items
        add_callback: Function to call when Add button clicked
        remove_callback: Function to call when item should be removed

    Returns:
        tuple: (widget, list_widget) - widget for layout, list_widget for access
    """
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 2, 0, 2)  # Reduced from 4, 4
    layout.setSpacing(4)  # Reduced from 6

    # Title
    title_label = QLabel(title)
    title_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
    title_label.setStyleSheet(f"color: {THEME_TEXT_SECONDARY}; padding: 0;")
    layout.addWidget(title_label)

    # List widget
    list_widget = QListWidget()
    list_widget.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
    list_widget.setMinimumHeight(120)
    list_widget.setMaximumHeight(200)
    list_widget.setStyleSheet(
        f"""
        QListWidget {{
            background-color: rgba(255, 255, 255, 0.04);
            color: {THEME_TEXT_PRIMARY};
            border-radius: 4px;
            padding: 4px;
        }}
        QListWidget::item {{
            padding: 6px;
            border-radius: 3px;
        }}
        QListWidget::item:selected {{
            background-color: rgba(122, 162, 247, 0.3);
        }}
        QListWidget::item:hover {{
            background-color: rgba(255, 255, 255, 0.06);
        }}
        """
    )

    # Add initial items
    for item in items:
        list_item = QListWidgetItem(item)
        list_widget.addItem(list_item)

    layout.addWidget(list_widget)

    # Buttons row
    buttons_row = QWidget()
    buttons_layout = QHBoxLayout(buttons_row)
    buttons_layout.setContentsMargins(0, 0, 0, 0)
    buttons_layout.setSpacing(8)

    # Add button
    add_btn = QPushButton(f"{Icons.ADD}  Add")
    add_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
    add_btn.setFixedHeight(28)
    add_btn.setStyleSheet(
        f"""
        QPushButton {{
            background-color: rgba(255, 255, 255, 0.04);
            color: {THEME_TEXT_PRIMARY};
            border-radius: 4px;
            padding: 4px 12px;
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
    add_btn.clicked.connect(lambda: add_callback(list_widget))
    buttons_layout.addWidget(add_btn)

    # Remove button
    remove_btn = QPushButton(f"{Icons.TRASH}  Remove")
    remove_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_STAT))
    remove_btn.setFixedHeight(28)
    remove_btn.setStyleSheet(
        f"""
        QPushButton {{
            background-color: rgba(247, 118, 142, 0.1);
            color: #f7768e;
            border: 1px solid rgba(247, 118, 142, 0.3);
            border-radius: 4px;
            padding: 4px 12px;
        }}
        QPushButton:hover {{
            background-color: rgba(247, 118, 142, 0.2);
            border: 1px solid #f7768e;
        }}
        QPushButton:pressed {{
            background-color: rgba(247, 118, 142, 0.3);
        }}
        QPushButton:disabled {{
            background-color: rgba(255, 255, 255, 0.02);
            color: rgba(255, 255, 255, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        """
    )

    def on_remove() -> None:
        current_item = list_widget.currentItem()
        if current_item:
            remove_callback(list_widget, current_item.text())

    remove_btn.clicked.connect(on_remove)
    buttons_layout.addWidget(remove_btn)

    buttons_layout.addStretch()

    layout.addWidget(buttons_row)

    # Enable/disable remove button based on selection
    def update_remove_button() -> None:
        remove_btn.setEnabled(list_widget.currentItem() is not None)

    list_widget.itemSelectionChanged.connect(update_remove_button)
    update_remove_button()  # Initial state

    return widget, list_widget
