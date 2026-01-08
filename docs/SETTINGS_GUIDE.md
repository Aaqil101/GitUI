# Settings System Developer Guide

This guide explains how to add new settings to the GitUI settings system.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Adding a New Setting](#adding-a-new-setting)
- [File Locations](#file-locations)
- [Settings Categories](#settings-categories)
- [Restart-Required Settings](#restart-required-settings)
- [Code Examples](#code-examples)
- [Best Practices](#best-practices)

## Architecture Overview

The settings system consists of three main components:

1. **Manager Classes** (Backend)
   - `SettingsManager`: Main application settings
   - `ExcludeManager`: Username-specific repository exclusions
   - `CustomPathsManager`: Username-specific custom repository paths

2. **Settings Dialog** (UI)
   - Side panel navigation (General, Git Operations, Appearance, Advanced)
   - Settings pages with form components
   - Save/Cancel/Reset functionality

3. **Integration** (Application)
   - Settings loaded at startup
   - Used throughout scanners, workers, and UI components
   - Some settings require restart to take effect

## Adding a New Setting

Follow these steps to add a new setting to the application:

### Step 1: Add to Default Settings

Edit `core/settings_manager.py` and add your setting to the appropriate category in `_get_default_settings()`:

```python
def _get_default_settings(self) -> dict:
    return {
        "version": "1.0",
        "general": {
            "github_path": "...",
            "my_new_setting": "default_value",  # Add your setting here
        },
        # ... other categories
    }
```

**Categories:**
- `general`: Paths, window behavior, auto-close delays
- `git_operations`: Performance, timeouts, power options
- `appearance`: Fonts, animations
- `advanced`: Test mode, startup delays

### Step 2: Add UI Component

Edit `ui/settings_dialog.py` in the appropriate page creation method (`_create_general_page`, `_create_git_ops_page`, etc.):

```python
def _create_general_page(self) -> QWidget:
    # ... existing code

    # Add your setting widget
    my_setting_widget, my_setting_control = create_checkbox_row(
        "My New Setting",
        self.current_settings["general"]["my_new_setting"],
        "Description of what this setting does"
    )
    self.ui_components["my_new_setting"] = my_setting_control
    layout.addWidget(my_setting_widget)

    # ... rest of code
```

**Available UI Components:**

- **Checkbox**: `create_checkbox_row(label, checked, tooltip)`
- **Spinbox**: `create_spinbox_row(label, value, min, max, suffix, tooltip, restart_required)`
- **Path Selector**: `create_path_selector(label, value, callback)`
- **List Manager**: `create_list_manager(title, items, add_callback, remove_callback)`

### Step 3: Handle Save

In the same file (`ui/settings_dialog.py`), update `_on_save_clicked()` to collect your setting's value:

```python
def _on_save_clicked(self):
    # ... existing code

    # Add your setting
    self.current_settings["general"]["my_new_setting"] = self.ui_components[
        "my_new_setting"
    ].isChecked()  # For checkbox

    # For spinbox: .value()
    # For line edit: .text()

    # ... rest of save logic
```

### Step 4: Mark as Restart-Required (If Needed)

If your setting requires a restart, add it to `_check_restart_needed()`:

```python
def _check_restart_needed(self) -> bool:
    restart_keys = [
        ("general", "my_new_setting"),  # Add here
        # ... existing keys
    ]
    # ... rest of code
```

**When to mark as restart-required:**
- Setting affects objects created once at startup (fonts, window size)
- Setting is embedded in PowerShell scripts
- Setting affects core initialization logic

### Step 5: Use the Setting

Access the setting in your code via SettingsManager:

```python
from core.settings_manager import SettingsManager

settings = SettingsManager().get_settings()
my_value = settings["general"]["my_new_setting"]
```

Or update `core/config.py` to provide a getter function:

```python
from core.settings_manager import SettingsManager

_settings_manager = SettingsManager()

def get_my_new_setting():
    return _settings_manager.get_settings()["general"]["my_new_setting"]

# Constant for backward compatibility
MY_NEW_SETTING = get_my_new_setting()
```

## File Locations

### Manager Files
- `core/settings_manager.py` - Main settings (920 lines)
- `core/exclude_manager.py` - Repository exclusions (175 lines)
- `core/custom_paths_manager.py` - Custom paths (225 lines)

### UI Files
- `ui/settings_dialog.py` - Main settings dialog (870 lines)
- `ui/settings_components.py` - Reusable UI components (463 lines)
- `ui/exclude_confirmation_dialog.py` - Exclusion confirmation (272 lines)

### Data Storage
- `%appdata%\GitUI\settings.json` - Main settings
- `%appdata%\GitUI\exclude_repositories.json` - Exclusions by username
- `%appdata%\GitUI\custom_repositories.json` - Custom paths by username

## Settings Categories

### General
- Repository paths (GitHub folder, custom paths)
- Repository exclusions (username-specific)
- Window behavior (always on top, dimensions)
- Auto-close delays

### Git Operations
- PowerShell throttle limit (parallelism)
- Scan timeout
- Operation timeout
- Power countdown seconds
- Exclude confirmation timeout

### Appearance
- Font family and sizes (title, header, label, stat)
- Enable animations
- Animation duration

### Advanced
- Test mode default
- Scan start delay
- Operations start delay

## Restart-Required Settings

Settings that require restart:

| Category | Setting | Reason |
|----------|---------|--------|
| general | github_path | Loaded once at startup |
| general | window_width | Set via setFixedSize() at init |
| general | window_height | Set via setFixedSize() at init |
| git_operations | powershell_throttle_limit | Embedded in PowerShell script |
| appearance | font_family | Font objects created once |
| appearance | font_size_* | Font objects created once |
| appearance | animation_duration | Animation objects created once |
| advanced | scan_start_delay | Timer created at startup |
| advanced | operations_start_delay | Timer created at startup |

Settings that take effect immediately:

| Category | Setting | How Applied |
|----------|---------|-------------|
| general | window_always_on_top | Applied via setWindowFlags() |
| general | auto_close_delay | Timer value updated |
| general | auto_close_no_repos_delay | Timer value updated |
| git_operations | scan_timeout | Read when worker starts |
| git_operations | operation_timeout | Read when worker starts |
| git_operations | power_countdown_seconds | Timer value updated |
| git_operations | exclude_confirmation_timeout | Read when dialog shows |
| appearance | enable_animations | Checked before animations |
| advanced | test_mode_default | Read at startup only |

## Code Examples

### Example 1: Add Boolean Setting

```python
# Step 1: Add to defaults (settings_manager.py)
"general": {
    "show_tooltips": True,  # New setting
}

# Step 2: Add UI (settings_dialog.py)
tooltip_widget, tooltip_check = create_checkbox_row(
    "Show Tooltips",
    self.current_settings["general"]["show_tooltips"],
    "Display helpful tooltips throughout the UI"
)
self.ui_components["show_tooltips"] = tooltip_check
layout.addWidget(tooltip_widget)

# Step 3: Handle save (settings_dialog.py in _on_save_clicked)
self.current_settings["general"]["show_tooltips"] = self.ui_components[
    "show_tooltips"
].isChecked()

# Step 4: Use it (anywhere)
from core.settings_manager import SettingsManager
settings = SettingsManager().get_settings()
if settings["general"]["show_tooltips"]:
    widget.setToolTip("Helpful text")
```

### Example 2: Add Numeric Setting with Restart Required

```python
# Step 1: Add to defaults (settings_manager.py)
"appearance": {
    "card_spacing": 8,  # New setting
}

# Step 2: Add UI (settings_dialog.py)
spacing_widget, spacing_spin = create_spinbox_row(
    "Card Spacing",
    self.current_settings["appearance"]["card_spacing"],
    0,  # min
    50,  # max
    "px",  # suffix
    "Spacing between repository cards",
    restart_required=True  # Shows restart indicator
)
self.ui_components["card_spacing"] = spacing_spin
layout.addWidget(spacing_widget)

# Step 3: Handle save
self.current_settings["appearance"]["card_spacing"] = self.ui_components[
    "card_spacing"
].value()

# Step 4: Mark restart required
restart_keys = [
    ("appearance", "card_spacing"),  # Add here
]

# Step 5: Add to config.py
from core.settings_manager import SettingsManager
_settings_manager = SettingsManager()

def get_card_spacing():
    return _settings_manager.get_settings()["appearance"]["card_spacing"]

CARD_SPACING = get_card_spacing()  # For backward compatibility
```

### Example 3: Add Path Setting

```python
# Step 1: Add to defaults
"general": {
    "export_path": str(Path.home() / "Documents" / "GitUI_Exports"),
}

# Step 2: Add UI
export_path_widget, export_path_edit = create_path_selector(
    "Export Path",
    self.current_settings["general"]["export_path"],
    lambda: None  # No real-time callback needed
)
self.ui_components["export_path"] = export_path_edit
layout.addWidget(export_path_widget)

# Step 3: Handle save
self.current_settings["general"]["export_path"] = self.ui_components[
    "export_path"
].text()

# Step 4: Use it
from core.settings_manager import SettingsManager
from pathlib import Path

settings = SettingsManager().get_settings()
export_path = Path(settings["general"]["export_path"])
```

## Best Practices

### 1. Setting Names
- Use lowercase with underscores: `my_setting_name`
- Be descriptive: `exclude_confirmation_timeout` not `timeout`
- Group related settings with common prefixes: `font_size_title`, `font_size_header`

### 2. Default Values
- Choose sensible defaults that work for most users
- Document why you chose the default (in code comments)
- Consider platform differences (Windows vs Unix paths)

### 3. Validation
- Validate in UI before saving (enable/disable Save button)
- Validate in manager when loading (merge with defaults if corrupt)
- Provide helpful error messages to users

### 4. Tooltips
- Always provide tooltips explaining what the setting does
- Include valid ranges for numeric settings
- Mention if restart is required

### 5. Categorization
- Place settings in the most logical category
- If unsure, use "Advanced" for developer-focused settings
- Keep related settings together

### 6. Backward Compatibility
- Never remove settings (users may have old JSON files)
- Use `_merge_with_defaults()` to handle new settings
- Increment version number when changing schema

### 7. Testing
- Test with missing settings file (creates defaults)
- Test with corrupted JSON (backs up and restores defaults)
- Test restart-required indicator appears correctly
- Test setting changes persist after restart

### 8. Documentation
- Update this guide when adding new setting types
- Update CLAUDE.md with user-facing documentation
- Add code comments explaining complex settings

## Common Patterns

### Pattern 1: Timeout Setting
```python
# Numeric value with range validation
create_spinbox_row("Timeout", value, 1, 600, "seconds", "Max wait time")
```

### Pattern 2: Enable/Disable Feature
```python
# Boolean checkbox
create_checkbox_row("Enable Feature", checked, "Turn feature on/off")
```

### Pattern 3: List of Items
```python
# List manager with Add/Remove
create_list_manager("Items", items, on_add, on_remove)
```

### Pattern 4: Font Configuration
```python
# Text field for font name + spinboxes for sizes
# No browse button needed (not a file path)
```

## Troubleshooting

### Setting Not Saving
- Check `_on_save_clicked()` includes your setting
- Verify key name matches exactly
- Check file permissions on `%appdata%\GitUI\`

### Setting Not Taking Effect
- Check if marked as restart-required (may need app restart)
- Verify setting is actually read from SettingsManager
- Check for typos in key path

### UI Component Not Appearing
- Verify component added to layout
- Check if scroll area has enough height
- Verify import statements for component functions

### Restart Indicator Not Showing
- Add setting to `_check_restart_needed()` restart_keys list
- Pass `restart_required=True` to component factory

## Migration Guide

If you need to change a setting's structure (rare):

1. Increment version in `_get_default_settings()`
2. Add migration logic in `load_settings()`
3. Preserve old format for backward compatibility
4. Document migration in CLAUDE.md

Example:
```python
def load_settings(self) -> dict:
    settings = # ... load from file

    # Migrate old format
    if settings.get("version") == "1.0":
        # Convert old setting to new format
        if "old_key" in settings["general"]:
            settings["general"]["new_key"] = convert(settings["general"]["old_key"])
            settings["version"] = "1.1"

    return settings
```

## Additional Resources

- See `ui/settings_components.py` for all available UI component factories
- See `test_managers.py` for examples of testing manager classes
- See existing settings in `settings_manager.py` for reference implementations
- Check `ui/settings_dialog.py` for complex UI layout examples

## Questions?

If you have questions about adding settings:

1. Check existing similar settings for reference
2. Review this guide thoroughly
3. Test your changes with the `--settings` flag
4. Update this documentation if you discover new patterns
