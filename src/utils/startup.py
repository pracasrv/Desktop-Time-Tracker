"""Windows auto-start functionality using registry."""

import sys
import os

try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False

APP_NAME = "DesktopTimeTracker"
REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def get_executable_path() -> str:
    """Get the path to the executable or Python script."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return sys.executable
    else:
        # Running as Python script
        return f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'


def is_auto_start_enabled() -> bool:
    """Check if auto-start is enabled in registry."""
    if not WINREG_AVAILABLE:
        return False

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_PATH,
            0,
            winreg.KEY_READ
        )
        try:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return True
        except WindowsError:
            winreg.CloseKey(key)
            return False
    except WindowsError:
        return False


def set_auto_start(enabled: bool) -> bool:
    """Enable or disable auto-start in registry."""
    if not WINREG_AVAILABLE:
        return False

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_PATH,
            0,
            winreg.KEY_WRITE
        )

        if enabled:
            exe_path = get_executable_path()
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except WindowsError:
                pass  # Key doesn't exist, that's fine

        winreg.CloseKey(key)
        return True

    except WindowsError as e:
        print(f"Error modifying registry: {e}")
        return False


def sync_auto_start_with_config(config) -> None:
    """Sync the auto-start registry with config setting."""
    current = is_auto_start_enabled()
    desired = config.auto_start_enabled

    if current != desired:
        set_auto_start(desired)
