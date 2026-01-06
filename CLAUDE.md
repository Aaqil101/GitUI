# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GitUI is a PyQt6-based desktop application for managing Git repositories in bulk. It provides visual interfaces for:

-   **Git Pull Runner**: Scans repositories, detects those behind upstream, and automatically pulls updates
-   **Git Push Runner**: Scans repositories for unpushed commits and pushes them to remote

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
│   └── styles.py        # PyQt6 stylesheet definitions
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
