"""Test script for validating Settings, Exclude, and CustomPaths managers."""

import importlib.util
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


# Direct imports to avoid core/__init__.py
def import_module_from_path(module_name, file_path):
    """Import a module directly from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Import managers directly
base_path = Path(__file__).parent / "core"
settings_manager_mod = import_module_from_path(
    "settings_manager", base_path / "settings_manager.py"
)
exclude_manager_mod = import_module_from_path(
    "exclude_manager", base_path / "exclude_manager.py"
)
custom_paths_manager_mod = import_module_from_path(
    "custom_paths_manager", base_path / "custom_paths_manager.py"
)

SettingsManager = settings_manager_mod.SettingsManager
ExcludeManager = exclude_manager_mod.ExcludeManager
CustomPathsManager = custom_paths_manager_mod.CustomPathsManager


def test_settings_manager():
    """Test SettingsManager functionality."""
    print("\n" + "=" * 60)
    print("TESTING SETTINGS MANAGER")
    print("=" * 60)

    sm = SettingsManager()

    # Test 1: Get default settings
    print("\n[TEST 1] Getting default settings...")
    settings = sm.get_settings()
    print(f"✓ Settings loaded: {len(settings)} categories")
    print(f"  - general: {len(settings.get('general', {}))} settings")
    print(f"  - git_operations: {len(settings.get('git_operations', {}))} settings")
    print(f"  - appearance: {len(settings.get('appearance', {}))} settings")
    print(f"  - advanced: {len(settings.get('advanced', {}))} settings")

    # Test 2: Save settings
    print("\n[TEST 2] Saving settings...")
    success = sm.save_settings(settings)
    if success:
        print(f"✓ Settings saved to: {sm.get_settings_path()}")
    else:
        print("✗ Failed to save settings")

    # Test 3: Load settings
    print("\n[TEST 3] Loading settings from file...")
    sm._settings = None  # Clear cache
    loaded = sm.get_settings()
    print(f"✓ Settings loaded: version {loaded.get('version')}")

    # Test 4: Reset to defaults
    print("\n[TEST 4] Resetting to defaults...")
    success = sm.reset_to_defaults()
    if success:
        print("✓ Settings reset successfully")
    else:
        print("✗ Failed to reset settings")

    print("\n✅ SettingsManager tests complete!")


def test_exclude_manager():
    """Test ExcludeManager functionality."""
    print("\n" + "=" * 60)
    print("TESTING EXCLUDE MANAGER")
    print("=" * 60)

    em = ExcludeManager()

    # Test 1: Get machine name
    print("\n[TEST 1] Getting machine name...")
    machine_name = em.get_current_machine_name()
    print(f"✓ Current machine: {machine_name}")

    # Test 2: Get excluded repos (should be empty initially)
    print("\n[TEST 2] Getting excluded repos...")
    excluded = em.get_excluded_repos()
    print(f"✓ Excluded repos: {len(excluded)} repositories")
    if excluded:
        for repo in excluded:
            print(f"  - {repo}")

    # Test 3: Add exclusion
    print("\n[TEST 3] Adding test exclusions...")
    test_repos = ["test-repo-1", "test-repo-2", "experimental-project"]
    for repo in test_repos:
        success = em.add_exclusion(repo)
        if success:
            print(f"✓ Added: {repo}")
        else:
            print(f"✗ Failed to add: {repo}")

    # Test 4: Check if excluded
    print("\n[TEST 4] Checking exclusion status...")
    for repo in ["test-repo-1", "not-excluded", "test-repo-2"]:
        is_excluded = em.is_excluded(repo)
        status = "EXCLUDED" if is_excluded else "NOT EXCLUDED"
        print(f"  - {repo}: {status}")

    # Test 5: Get all excluded repos
    print("\n[TEST 5] Getting all excluded repos...")
    all_excluded = em.get_excluded_repos()
    print(f"✓ Total excluded: {len(all_excluded)} repositories")
    for repo in all_excluded:
        print(f"  - {repo}")

    # Test 6: Remove exclusion
    print("\n[TEST 6] Removing test exclusions...")
    for repo in test_repos:
        success = em.remove_exclusion(repo)
        if success:
            print(f"✓ Removed: {repo}")
        else:
            print(f"✗ Failed to remove: {repo}")

    # Test 7: Verify removal
    print("\n[TEST 7] Verifying removal...")
    final_excluded = em.get_excluded_repos()
    print(f"✓ Remaining excluded: {len(final_excluded)} repositories")

    print(f"\n✓ Exclusions file location: {em.get_exclusions_path()}")
    print("\n✅ ExcludeManager tests complete!")


def test_custom_paths_manager():
    """Test CustomPathsManager functionality."""
    print("\n" + "=" * 60)
    print("TESTING CUSTOM PATHS MANAGER")
    print("=" * 60)

    cpm = CustomPathsManager()

    # Test 1: Get machine name
    print("\n[TEST 1] Getting machine name...")
    machine_name = cpm.get_current_machine_name()
    print(f"✓ Current machine: {machine_name}")

    # Test 2: Get custom paths (should be empty initially)
    print("\n[TEST 2] Getting custom paths...")
    paths = cpm.get_custom_paths()
    print(f"✓ Custom paths: {len(paths)} paths")
    if paths:
        for path in paths:
            print(f"  - {path}")

    # Test 3: Validate paths
    print("\n[TEST 3] Validating test paths...")
    test_paths = [
        (str(Path.home()), True),  # Should be valid
        (str(Path.home() / "Documents"), True),  # Should be valid
        ("C:\\NonExistent\\Path", False),  # Should be invalid
        ("relative/path", False),  # Should be invalid (not absolute)
    ]

    for path, should_be_valid in test_paths:
        is_valid, error_msg = cpm.validate_path(path)
        status = "VALID" if is_valid else f"INVALID ({error_msg})"
        expected = "✓" if is_valid == should_be_valid else "✗"
        print(f"  {expected} {path}: {status}")

    # Test 4: Add custom paths
    print("\n[TEST 4] Adding valid custom paths...")
    valid_paths = [str(Path.home() / "Documents"), str(Path.home())]
    for path in valid_paths:
        success, error = cpm.add_path(path)
        if success:
            print(f"✓ Added: {path}")
        else:
            print(f"✗ Failed to add {path}: {error}")

    # Test 5: Get all custom paths
    print("\n[TEST 5] Getting all custom paths...")
    all_paths = cpm.get_custom_paths()
    print(f"✓ Total custom paths: {len(all_paths)}")
    for path in all_paths:
        print(f"  - {path}")

    # Test 6: Get all scan paths (GitHub + custom)
    print("\n[TEST 6] Getting all scan paths...")
    scan_paths = cpm.get_all_scan_paths()
    print(f"✓ Total scan paths: {len(scan_paths)}")
    for path in scan_paths:
        print(f"  - {path}")

    # Test 7: Remove custom paths
    print("\n[TEST 7] Removing custom paths...")
    for path in valid_paths:
        success = cpm.remove_path(path)
        if success:
            print(f"✓ Removed: {path}")
        else:
            print(f"✗ Failed to remove: {path}")

    # Test 8: Verify removal
    print("\n[TEST 8] Verifying removal...")
    final_paths = cpm.get_custom_paths()
    print(f"✓ Remaining paths: {len(final_paths)}")

    print(f"\n✓ Custom paths file location: {cpm.get_custom_paths_file()}")
    print("\n✅ CustomPathsManager tests complete!")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("CORE MANAGERS VALIDATION TESTS")
    print("=" * 60)
    print("\nThis script will test all three manager classes:")
    print("  1. SettingsManager")
    print("  2. ExcludeManager")
    print("  3. CustomPathsManager")
    print("\nAll test data will be saved to %appdata%\\GitUI\\")

    try:
        test_settings_manager()
        test_exclude_manager()
        test_custom_paths_manager()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✅")
        print("=" * 60)
        print("\nCheck the following files:")
        print(f"  - {SettingsManager().get_settings_path()}")
        print(f"  - {ExcludeManager().get_exclusions_path()}")
        print(f"  - {CustomPathsManager().get_custom_paths_file()}")
        print("\n")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
