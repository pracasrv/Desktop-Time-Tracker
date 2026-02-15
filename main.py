#!/usr/bin/env python3
"""Desktop Time Tracker - Main Entry Point."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.database.db_manager import DatabaseManager
from src.utils.config import get_app_data_dir, Config
from src.utils.startup import sync_auto_start_with_config
from src.ui.main_window import MainWindow


def main():
    """Main application entry point."""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Desktop Time Tracker")
    app.setOrganizationName("TimeTracker")
    app.setQuitOnLastWindowClosed(False)  # Allow running in system tray

    # Set application-wide dark theme
    app.setStyleSheet("""
        QToolTip {
            background-color: #2d2d2d;
            color: white;
            border: 1px solid #555;
            padding: 5px;
        }
    """)

    # Initialize configuration
    app_data_dir = get_app_data_dir()
    config = Config(app_data_dir)

    # Initialize database
    db_manager = DatabaseManager(str(config.db_path))

    # Sync auto-start setting with registry
    sync_auto_start_with_config(config)

    # Create and show main window
    window = MainWindow(db_manager, config)

    if config.start_minimized:
        window.hide()
    else:
        window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
