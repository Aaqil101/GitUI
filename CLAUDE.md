# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GitUI is a PyQt6-based desktop application for managing Git repositories in bulk. It provides visual interfaces for:

-   **Git Pull Runner**: Scans repositories, detects those behind upstream, and automatically pulls updates
-   **Git Push Runner**: Scans repositories for uncommitted changes, prompts for power action selection via modal dialog, commits with action-specific messages, pushes to remote, and optionally executes system shutdown/restart

The application features a modern Tokyo Night-themed UI with real-time progress tracking, animated components, and status cards for each repository.

## Running the Application

```bash
# Activate virtual environment (if not already active)
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
source .venv/bin/activate     # Unix/Mac

# Run Git Pull Runner
python __init__.py --git-pull

# Run Git Push Runner
python __init__.py --git-push

# Run in test mode (simulates operations without actual git commands)
python __init__.py --git-pull --test
python __init__.py --git-push --test
```

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt
```

Dependencies:

-   PyQt6==6.9.1
-   PyQt6-Qt6==6.9.1
-   PyQt6_sip==13.10.2

## Architecture

### Core Structure

```
GitUI/
├── __init__.py           # Entry point with CLI argument parsing
├── base/                 # Abstract base classes
│   └── base_worker.py   # Base classes for scanners and workers
├── core/                 # Application logic
│   ├── base_runner.py   # Abstract base class for Pull/Push runners
│   ├── pull_runner.py   # Git Pull Runner implementation
│   ├── push_runner.py   # Git Push Runner implementation
│   └── config.py        # Centralized configuration (colors, fonts, timing)
├── ui/                  # UI components and styles
│   ├── components.py    # Reusable UI component factories
│   ├── styles.py        # PyQt6 stylesheet definitions
│   └── power_options_panel.py  # Power options panel for Git Push
├── utils/               # Utility modules
│   ├── card.py          # Repository card widget with animations
│   ├── check_internet.py     # Internet connectivity checker
│   ├── color.py         # Color constants and helpers
│   ├── icons.py         # Nerd Font icon constants
│   └── center.py        # Window centering utility
├── scanners/            # Repository scanners (discovery)
│   ├── git_pull_scanner.py   # Scans for repos behind upstream
│   └── git_push_scanner.py   # Scans for repos with uncommitted changes
└── workers/             # Operation workers (execution)
    ├── git_pull_worker.py    # Executes git pull operations
    └── git_push_worker.py    # Executes git push operations
```

### Key Design Patterns

Note: Whenever you add a new feature or make any updates, please remember to update this markdown file.

#### 1. Template Method Pattern

`BaseGitRunner` (in [core/base_runner.py](core/base_runner.py)) is an abstract base class that defines the common UI and workflow for both Pull and Push runners. Subclasses implement operation-specific methods:

-   `_get_operation_config()`: Operation-specific labels and icons
-   `_show_scan_summary()`: Display scan results summary
-   `_update_stats()`: Update statistics panel
-   `_run_operations()`: Execute git operations
-   `_populate_test_data()`: Generate test mode data

#### 2. Worker Base Class Hierarchy

All QRunnable workers (scanners and operation workers) inherit from a 3-tier base class hierarchy in [base/base_worker.py](base/base_worker.py):

**BaseWorker (abstract)**: Provides common infrastructure for all workers:

-   Signal safety patterns with RuntimeError handling
-   Graceful shutdown via `stop()` method and `_is_running` flag
-   PowerShell subprocess execution with standard configuration
-   Template method `run()` with comprehensive error handling (TimeoutExpired, JSONDecodeError, Exception)
-   Abstract methods for subclasses to implement operation-specific logic

**BaseScannerWorker (abstract)**: Extends BaseWorker for repository scanning operations:

-   Repository counting before scanning for progress tracking
-   JSON array parsing (handles empty results, single object → array conversion)
-   Progress signal emission (`_safe_emit_progress`)
-   Returns `ScanResult(repos=[], duration=X)` on errors

**BaseOperationWorker (abstract)**: Extends BaseWorker for git operations on individual repos:

-   Repository existence validation
-   CREATE_NO_WINDOW flag for silent execution
-   JSON single-object parsing
-   Returns typed result objects (PullResult/PushResult)

**Benefits of hierarchy:**

-   **37% code reduction**: 342 lines eliminated across 4 worker files
-   **DRY principle**: Common patterns (signal safety, subprocess execution, error handling) defined once
-   **Easier maintenance**: Changes to common patterns automatically affect all workers
-   **Type safety**: Abstract methods enforce implementation contracts

#### 3. Worker Thread Pattern

Uses `QRunnable` workers inheriting from base classes ([base/base_worker.py](base/base_worker.py)) for asynchronous operations:

-   **Scanner Workers** ([scanners/git_pull_scanner.py](scanners/git_pull_scanner.py), [scanners/git_push_scanner.py](scanners/git_push_scanner.py)): Run PowerShell scripts to scan repositories in parallel (30 concurrent operations) - **Discovery phase**
-   **Operation Workers** ([workers/git_pull_worker.py](workers/git_pull_worker.py), [workers/git_push_worker.py](workers/git_push_worker.py)): Execute individual git pull/push operations - **Execution phase**
-   All workers emit PyQt signals for progress updates and completion

#### 4. Configuration Centralization

All UI constants (colors, fonts, sizes, timing) are centralized in [core/config.py](core/config.py):

-   Theme colors (Tokyo Night palette)
-   Font configuration (JetBrainsMono Nerd Font)
-   Layout dimensions
-   Animation timings
-   Default file paths
-   Power options dialog configuration (width, height, countdown seconds)

#### 5. Factory Function Pattern (Power Options)

The Git Push Runner uses a factory function for power option selection ([ui/power_options_panel.py](ui/power_options_panel.py)):

-   **create_power_options_panel()**: Factory function that returns a plain QWidget with PowerOptionsSignals
-   Returns tuple of (widget, signals) for clean separation of UI and event handling
-   Appears in left sidebar between stats panel and bottom stretch
-   Emits `option_selected` signal when user clicks button or timer expires (auto-selects "Shutdown")
-   Integrates with Tokyo Night theme using `PANEL_STYLE` applied to plain QWidget
-   Disables buttons after selection and updates countdown label to show selected option
-   Used to determine commit message prefix and post-push system action
-   Window automatically resizes from 620px to 800px height and re-centers when panel appears
-   Buttons feature modern glass morphism style with subtle transparency and colored bottom border accents

### PowerShell Integration

The application uses PowerShell for high-performance parallel git operations:

1. **Repository Scanning**: PowerShell's `ForEach-Object -Parallel` with `-ThrottleLimit 30` scans up to 30 repositories concurrently
2. **Git Operations**: Executes `git fetch`, `git rev-list`, `git pull`, `git push` via PowerShell
3. **JSON Output**: Results are returned as JSON and parsed in Python
4. **Error Handling**: Subprocess timeouts and error capturing prevent UI freezes

### UI Components

#### Reusable Component Factories ([ui/components.py](ui/components.py))

-   `create_icon_label()`: Nerd Font icons with styling
-   `create_text_label()`: Styled text labels
-   `create_progress_bar()`: Animated segmented progress bar
-   `create_stat_row()`: Icon + label + value statistics row
-   Shadow effect helpers for depth

#### Repository Cards ([utils/card.py](utils/card.py))

-   `RepoCard` widget displays repository name, commits behind/ahead, and status
-   Animated status transitions using `QVariantAnimation`
-   Fade-in animations on creation
-   Hover effects with shadow enhancement

#### Status Colors

Defined in [utils/color.py](utils/color.py):

-   `SUCCESS`: Green (#9ece6a)
-   `FAILED`: Red (#f7768e)
-   `PENDING`: Yellow (#e0af68)
-   `QUEUED`: Blue (#7aa2f7)
-   `MISSING`: Purple (#bb9af7)

### Important Implementation Details

#### Test Mode vs. Real Mode

-   **Test mode** (`--test` flag): Sets `testing=True`, skips internet check, calls `_populate_test_data()` to show simulated data
-   **Real mode**: Checks internet connectivity, runs actual PowerShell scanners and git operations
-   The summary text color differences mentioned in user's original question are intentional: test mode uses purple (#bb9af7), real mode uses theme colors based on results

#### Timing and Auto-Close

Configured in [core/config.py](core/config.py):

-   `SCAN_START_DELAY`: 0ms (starts immediately)
-   `OPERATIONS_START_DELAY`: 100ms delay before starting git operations
-   `AUTO_CLOSE_DELAY`: 1000ms (1s) after all operations complete
-   `AUTO_CLOSE_NO_REPOS_DELAY`: 2000ms (2s) if no repos need updates

#### Animation System

-   Progress bar: 23 segments animated in sweeping pattern at 150ms intervals
-   Cards: Staggered fade-in with 50ms delay per card
-   Status transitions: 200ms color interpolation with InOutQuad easing

#### GitHub Desktop Integration

When merge conflicts are detected during pull ([core/pull_runner.py](core/pull_runner.py):236), the app attempts to open GitHub Desktop to the conflicting repository using PowerShell.

## Power Options Integration (Git Push)

When running Git Push (`--git-push`), the application displays a power options panel in the left sidebar after scanning completes.

### Panel Behavior

-   Appears automatically in the left sidebar after scan if repositories with changes are found
-   Integrated panel (part of the main UI, between stats panel and bottom)
-   **Window resizes** from 620px to 800px height when panel appears and automatically re-centers on screen
-   Presents 4 buttons in a 2x2 grid with modern glass morphism styling:
    1. **Shutdown** (Red #EF4444): Commits with "Shutdown commit by...", pushes, then shuts down system
    2. **Restart** (Blue #3B82F6): Commits with "Restart commit by...", pushes, then restarts system
    3. **Shutdown (Cancel)** (Amber #F59E0B): Commits with "Shutdown (Cancelled) commit by...", pushes, NO system action
    4. **Restart (Cancel)** (Emerald #10B981): Commits with "Restart (Cancelled) commit by...", pushes, NO system action
-   5-second countdown timer auto-selects "Shutdown" if no user interaction
-   Countdown label shows time remaining, turns green when option selected
-   All buttons disabled after selection
-   Buttons feature subtle glass effect (4% white background) with colored bottom border on hover/press

### Implementation Flow

1. Scan completes → `_on_scan_finished()` in [core/push_runner.py](core/push_runner.py)
2. If repos found → `_show_power_options_panel()` creates panel using factory function and resizes window
3. Window resizes to 800px height and re-centers on screen
4. Panel displays with countdown timer
5. User selects option (or waits for auto-select) → Signal emitted via `PowerOptionsSignals`, stored in `self.power_option`
6. Push operations execute with custom commit message prefix
7. All pushes complete → `_handle_completion()` executes system action if applicable

### Commit Message Format

All commits use format:

```
{Prefix} commit by {username} on {timestamp}

Changed files:
- Modified: file1.txt
- Added: file2.py
```

Where `{Prefix}` is:

-   "Shutdown" (for Shutdown option)
-   "Restart" (for Restart option)
-   "Shutdown (Cancelled)" (for Shutdown Cancel option)
-   "Restart (Cancelled)" (for Restart Cancel option)

### System Action Execution

-   Only executes if ALL push operations succeed (`self.failed_count == 0`)
-   **Shutdown** → `os.system("shutdown /s /t 5")` (5 second delay)
-   **Restart** → `os.system("shutdown /r /t 5")` (5 second delay)
-   Cancel variants → No system action, just closes UI
-   If any push fails → No system action, just closes UI after delay

### Test Mode Behavior

When running `python __init__.py --git-push --test`:

-   Panel appears in left sidebar after 1 second
-   After selection, card transitions animate
-   Console prints: `[TEST MODE] Would execute power action: {option}`
-   NO actual system action occurs
-   UI closes after delay

### Customization

**Countdown timing** (in [core/config.py](core/config.py)):

```python
POWER_COUNTDOWN_SECONDS = 5  # Auto-select countdown duration
```

**Button styling** (in [ui/power_options_panel.py](ui/power_options_panel.py)):

-   Glass morphism effect with `rgba(255, 255, 255, 0.04)` background
-   Colored bottom borders on hover/press:
    -   Shutdown: Red (#EF4444)
    -   Restart: Blue (#3B82F6)
    -   Shutdown (Cancel): Amber (#F59E0B)
    -   Restart (Cancel): Emerald (#10B981)
-   Hover state: 8% white background with warm cream text
-   Pressed state: 40% white background with golden text
-   6px border radius for subtle rounded corners

**Panel styling**: Uses `PANEL_STYLE` from [ui/styles.py](ui/styles.py), created via factory function pattern

## Common Modifications

### Adding a New Git Operation Type

1. Create new runner in `core/` inheriting from `BaseGitRunner`
2. Implement abstract methods (`_get_operation_config`, `_run_operations`, etc.)
3. Create scanner in `scanners/` inheriting from `BaseScannerWorker` (implement `_get_powershell_command`, `_create_repo_status`)
4. Create worker in `workers/` inheriting from `BaseOperationWorker` (implement `_get_powershell_command`, `_create_result_from_data`)
5. Add CLI argument in `__init__.py`

### Modifying Colors/Theme

Edit [core/config.py](core/config.py) constants:

-   `THEME_*` for background/text colors
-   `COLOR_*` for accent colors
-   Update [utils/color.py](utils/color.py) status color mappings if needed

### Adjusting Scan Performance

Modify PowerShell `-ThrottleLimit` in scanner files:

-   Higher values (30-50): Faster but more resource-intensive
-   Lower values (10-20): Slower but more stable on limited systems

### Changing Default Repository Path

Edit `get_default_paths()` in [core/config.py](core/config.py):98

### Modifying UI Layout

-   Panel dimensions: Edit `LEFT_PANEL_WIDTH`, `WINDOW_WIDTH`, `WINDOW_HEIGHT` in [core/config.py](core/config.py)
-   Spacing/padding: Edit `PANEL_SPACING`, `*_PADDING` constants
-   Component styles: Edit stylesheet strings in [ui/styles.py](ui/styles.py)

## Platform Notes

-   **Windows-specific**: Uses PowerShell (`pwsh`) for git operations
-   **Nerd Fonts required**: Install JetBrainsMono Nerd Font for icons to display correctly
-   **Git required**: Must be in PATH for PowerShell git commands to work
-   The application is designed for Windows but could be adapted for Unix/Mac by replacing PowerShell scripts with Bash equivalents
