"""Configuration management for the Time Tracker application."""

import json
from pathlib import Path
from typing import Any, Dict


class Config:
    """Application configuration manager."""

    # Default settings
    DEFAULTS = {
        'screenshot_interval': 600,      # Seconds between screenshots (10 minutes)
        'idle_threshold': 300,           # Seconds before auto-pause (5 minutes)
        'screenshot_quality': 70,        # JPEG quality (1-100)
        'minimize_to_tray': True,        # Close button minimizes to tray
        'start_minimized': False,        # Start minimized on auto-start
        'activity_sample_rate': 1,       # Seconds between activity checks
        'auto_start_enabled': False,     # Start app on Windows boot
        'screenshots_enabled': True,     # Enable screenshot capture
        # Freelancer/billing info
        'freelancer_name': '',           # Freelancer name for reports
        'freelancer_email': '',          # Freelancer email for reports
        'freelancer_address': '',        # Business address
        'payment_details': '',           # Bank/payment details
        # Last selection (remembered between sessions)
        'last_client_id': None,          # Last selected client ID
        'last_project_id': None,         # Last selected project ID
        # KPI display settings
        'show_kpi_earnings': False,      # Show $ earnings on KPI cards
        'show_kpi_targets': False,       # Show target progress on KPI cards
        'daily_target_hours': 8.0,       # Daily target hours
        'weekly_target_hours': 40.0,     # Weekly target hours
    }

    def __init__(self, app_data_dir: Path):
        self.app_data_dir = app_data_dir
        self.config_file = app_data_dir / 'config.json'
        self.db_path = app_data_dir / 'timetracker.db'
        self.screenshots_dir = app_data_dir / 'screenshots'
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from file or create with defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._config = {}

        # Merge with defaults (add any missing keys)
        for key, value in self.DEFAULTS.items():
            if key not in self._config:
                self._config[key] = value

        self._save_config()

    def _save_config(self):
        """Save configuration to file."""
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default if default is not None else self.DEFAULTS.get(key))

    def set(self, key: str, value: Any):
        """Set a configuration value and save."""
        self._config[key] = value
        self._save_config()

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()

    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self._config = self.DEFAULTS.copy()
        self._save_config()

    @property
    def screenshot_interval(self) -> int:
        return self.get('screenshot_interval')

    @screenshot_interval.setter
    def screenshot_interval(self, value: int):
        self.set('screenshot_interval', value)

    @property
    def idle_threshold(self) -> int:
        return self.get('idle_threshold')

    @idle_threshold.setter
    def idle_threshold(self, value: int):
        self.set('idle_threshold', value)

    @property
    def screenshot_quality(self) -> int:
        return self.get('screenshot_quality')

    @screenshot_quality.setter
    def screenshot_quality(self, value: int):
        self.set('screenshot_quality', max(1, min(100, value)))

    @property
    def minimize_to_tray(self) -> bool:
        return self.get('minimize_to_tray')

    @minimize_to_tray.setter
    def minimize_to_tray(self, value: bool):
        self.set('minimize_to_tray', value)

    @property
    def start_minimized(self) -> bool:
        return self.get('start_minimized')

    @start_minimized.setter
    def start_minimized(self, value: bool):
        self.set('start_minimized', value)

    @property
    def activity_sample_rate(self) -> int:
        return self.get('activity_sample_rate')

    @activity_sample_rate.setter
    def activity_sample_rate(self, value: int):
        self.set('activity_sample_rate', max(1, value))

    @property
    def auto_start_enabled(self) -> bool:
        return self.get('auto_start_enabled')

    @auto_start_enabled.setter
    def auto_start_enabled(self, value: bool):
        self.set('auto_start_enabled', value)

    @property
    def screenshots_enabled(self) -> bool:
        return self.get('screenshots_enabled')

    @screenshots_enabled.setter
    def screenshots_enabled(self, value: bool):
        self.set('screenshots_enabled', value)

    @property
    def freelancer_name(self) -> str:
        return self.get('freelancer_name', '')

    @freelancer_name.setter
    def freelancer_name(self, value: str):
        self.set('freelancer_name', value)

    @property
    def freelancer_email(self) -> str:
        return self.get('freelancer_email', '')

    @freelancer_email.setter
    def freelancer_email(self, value: str):
        self.set('freelancer_email', value)

    @property
    def freelancer_address(self) -> str:
        return self.get('freelancer_address', '')

    @freelancer_address.setter
    def freelancer_address(self, value: str):
        self.set('freelancer_address', value)

    @property
    def payment_details(self) -> str:
        return self.get('payment_details', '')

    @payment_details.setter
    def payment_details(self, value: str):
        self.set('payment_details', value)

    @property
    def last_client_id(self) -> int:
        return self.get('last_client_id')

    @last_client_id.setter
    def last_client_id(self, value: int):
        self.set('last_client_id', value)

    @property
    def last_project_id(self) -> int:
        return self.get('last_project_id')

    @last_project_id.setter
    def last_project_id(self, value: int):
        self.set('last_project_id', value)

    @property
    def show_kpi_earnings(self) -> bool:
        return self.get('show_kpi_earnings', False)

    @show_kpi_earnings.setter
    def show_kpi_earnings(self, value: bool):
        self.set('show_kpi_earnings', value)

    @property
    def show_kpi_targets(self) -> bool:
        return self.get('show_kpi_targets', False)

    @show_kpi_targets.setter
    def show_kpi_targets(self, value: bool):
        self.set('show_kpi_targets', value)

    @property
    def daily_target_hours(self) -> float:
        return self.get('daily_target_hours', 8.0)

    @daily_target_hours.setter
    def daily_target_hours(self, value: float):
        self.set('daily_target_hours', max(0.5, value))

    @property
    def weekly_target_hours(self) -> float:
        return self.get('weekly_target_hours', 40.0)

    @weekly_target_hours.setter
    def weekly_target_hours(self, value: float):
        self.set('weekly_target_hours', max(1.0, value))


def get_app_data_dir() -> Path:
    """Get the application data directory."""
    # Use a folder in the project directory for development
    # In production, this could be moved to %APPDATA%
    return Path(__file__).parent.parent.parent / 'data'


def get_config() -> Config:
    """Get the global configuration instance."""
    return Config(get_app_data_dir())
