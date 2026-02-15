"""Main application window."""

import winsound

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox, QFrame, QSplitter
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent

from ..database.db_manager import DatabaseManager
from ..database.models import Client, Project, Task, Screenshot
from ..core.tracker import TimeTracker, TrackerState
from ..core.activity_monitor import create_activity_monitor
from ..core.screenshot import ScreenshotCapture
from ..core.idle_detector import IdleDetector
from ..utils.config import Config

from .widgets.timer_widget import TimerWidget
from .widgets.selector_widget import SelectorWidget
from .widgets.task_panel import TaskPanelWidget
from .widgets.activity_widget import ActivityWidget, StatusWidget
from .widgets.stats_widget import StatsWidget
from .system_tray import SystemTrayIcon
from .dialogs import (
    ClientDialog, ProjectDialog, TaskDialog,
    ManualEntryDialog, SettingsDialog, ReportsDialog
)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, db_manager: DatabaseManager, config: Config):
        super().__init__()
        self.db_manager = db_manager
        self.config = config

        # Initialize core components
        self._tracker = TimeTracker(db_manager)
        self._activity_monitor = create_activity_monitor(
            sample_interval=60
        )
        self._screenshot_capture = ScreenshotCapture(
            screenshots_dir=config.screenshots_dir,
            interval_seconds=config.screenshot_interval,
            quality=config.screenshot_quality
        )
        self._idle_detector = IdleDetector(
            threshold_seconds=config.idle_threshold
        )

        self._setup_ui()
        self._setup_tray()
        self._connect_signals()

        # Start activity monitoring (always on, but doesn't affect tracking until started)
        self._activity_monitor.start()

    def _setup_ui(self):
        """Set up the main window UI."""
        self.setWindowTitle("Desktop Time Tracker")
        self.setMinimumSize(800, 450)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QSplitter::handle {
                background-color: #3a3a3a;
                width: 1px;
            }
        """)

        # Central widget with horizontal splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left panel (main controls)
        left_panel = QWidget()
        left_panel.setMinimumWidth(300)
        left_panel.setMaximumWidth(380)
        layout = QVBoxLayout(left_panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Selector widget (Client/Project only)
        self._selector = SelectorWidget(self.db_manager, self.config)
        layout.addWidget(self._selector)

        # Timer widget
        self._timer_widget = TimerWidget()
        layout.addWidget(self._timer_widget)

        # Stats widget (daily/weekly totals)
        self._stats_widget = StatsWidget(self.db_manager, self.config)
        layout.addWidget(self._stats_widget)

        # Activity widget
        self._activity_widget = ActivityWidget()
        layout.addWidget(self._activity_widget)

        # Status widget
        self._status_widget = StatusWidget()
        self._status_widget.set_screenshots_status(self.config.screenshots_enabled)
        layout.addWidget(self._status_widget)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #444;")
        layout.addWidget(separator)

        # Bottom buttons
        buttons_layout = QHBoxLayout()

        button_style = """
            QPushButton {
                padding: 10px 15px;
                font-size: 12px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: #ccc;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #666;
            }
        """

        manual_btn = QPushButton("Manual Entry")
        manual_btn.setStyleSheet(button_style)
        manual_btn.clicked.connect(self._on_manual_entry)
        buttons_layout.addWidget(manual_btn)

        reports_btn = QPushButton("Reports")
        reports_btn.setStyleSheet(button_style)
        reports_btn.clicked.connect(self._on_reports)
        buttons_layout.addWidget(reports_btn)

        settings_btn = QPushButton("Settings")
        settings_btn.setStyleSheet(button_style)
        settings_btn.clicked.connect(self._on_settings)
        buttons_layout.addWidget(settings_btn)

        quit_btn = QPushButton("Quit")
        quit_btn.setStyleSheet(button_style + """
            QPushButton {
                color: #dc3545;
            }
            QPushButton:hover {
                border-color: #dc3545;
            }
        """)
        quit_btn.clicked.connect(self._on_quit)
        buttons_layout.addWidget(quit_btn)

        layout.addLayout(buttons_layout)

        # Toggle tasks button
        self._toggle_tasks_btn = QPushButton("Hide Tasks")
        self._toggle_tasks_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                font-size: 11px;
                border: 1px solid #444;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: #888;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                color: #ccc;
            }
        """)
        self._toggle_tasks_btn.clicked.connect(self._toggle_task_panel)
        layout.addWidget(self._toggle_tasks_btn)

        layout.addStretch()

        main_layout.addWidget(left_panel, 1)

        # Right panel (task list)
        self._task_panel = TaskPanelWidget(self.db_manager)
        self._task_panel_visible = True
        main_layout.addWidget(self._task_panel)

    def _setup_tray(self):
        """Set up system tray icon."""
        self._tray_icon = SystemTrayIcon(self)
        self._tray_icon.show_window_requested.connect(self._show_from_tray)
        self._tray_icon.start_requested.connect(self._on_start_from_tray)
        self._tray_icon.pause_requested.connect(self._on_pause)
        self._tray_icon.stop_requested.connect(self._on_stop)
        self._tray_icon.quit_requested.connect(self._on_quit)
        self._tray_icon.show()

    def _connect_signals(self):
        """Connect all signals."""
        # Timer widget signals
        self._timer_widget.start_clicked.connect(self._on_start)
        self._timer_widget.pause_clicked.connect(self._on_pause)
        self._timer_widget.stop_clicked.connect(self._on_stop)

        # Tracker signals
        self._tracker.state_changed.connect(self._on_tracker_state_changed)
        self._tracker.time_updated.connect(self._on_time_updated)

        # Activity monitor signals
        self._activity_monitor.activity_updated.connect(self._on_activity_updated)
        self._activity_monitor.idle_detected.connect(self._idle_detector.on_idle_detected)

        # Idle detector signals
        self._idle_detector.idle_threshold_reached.connect(self._on_idle_threshold)

        # Screenshot capture signals
        self._screenshot_capture.screenshot_taken.connect(self._on_screenshot_taken)
        self._screenshot_capture.screenshot_skipped.connect(self._on_screenshot_skipped)

        # Selector signals
        self._selector.add_client_clicked.connect(self._on_add_client)
        self._selector.add_project_clicked.connect(self._on_add_project)
        self._selector.edit_client_clicked.connect(self._on_edit_client)
        self._selector.edit_project_clicked.connect(self._on_edit_project)
        self._selector.selection_changed.connect(self._on_selection_changed)

        # Task panel signals
        self._task_panel.add_task_clicked.connect(self._on_add_task)
        self._task_panel.task_start_requested.connect(self._on_task_start_from_list)

        # Initialize task panel with restored selection (signal was emitted before connection)
        self._on_selection_changed()

    def _toggle_task_panel(self):
        """Toggle the task panel visibility."""
        self._task_panel_visible = not self._task_panel_visible
        self._task_panel.setVisible(self._task_panel_visible)
        self._toggle_tasks_btn.setText("Hide Tasks" if self._task_panel_visible else "Show Tasks")

    def _on_selection_changed(self):
        """Handle client/project selection change."""
        self._task_panel.set_project(self._selector.selected_project_id)

    def _on_task_start_from_list(self, task_id: int):
        """Handle task start from task list widget."""
        if self._tracker.is_running or self._tracker.is_paused:
            QMessageBox.warning(
                self, "Tracking Active",
                "Please stop the current tracking session first."
            )
            return

        if self._tracker.start(task_id):
            self._selector.set_enabled(False)
            self._task_panel.set_enabled(False)
            self._task_panel.set_tracking_task(task_id)
            # Reset screenshot counter for new session
            self._status_widget.reset_screenshot_count()
            if self.config.screenshots_enabled:
                self._screenshot_capture.start()
            self._activity_monitor.reset_interval()

    def _on_start(self):
        """Handle start/resume button click."""
        if self._tracker.is_paused:
            self._tracker.resume()
            if self.config.screenshots_enabled:
                self._screenshot_capture.start()
            return

        # Start button without task list selection - show message
        QMessageBox.information(
            self, "Select a Task",
            "Click the 'Start' button on a task in the list below to begin tracking."
        )
        return

        # Legacy code path (kept for reference)
        task_id = self._selector.selected_task_id
        if self._tracker.start(task_id):
            self._selector.set_enabled(False)
            if self.config.screenshots_enabled:
                self._screenshot_capture.start()
            self._activity_monitor.reset_interval()

    def _on_start_from_tray(self):
        """Handle start from tray (may need to resume)."""
        if self._tracker.is_paused:
            self._tracker.resume()
            if self.config.screenshots_enabled:
                self._screenshot_capture.start()
        elif self._tracker.is_stopped:
            self._on_start()

    def _on_pause(self):
        """Handle pause button click."""
        if self._tracker.pause():
            self._screenshot_capture.stop()

    def _on_stop(self):
        """Handle stop button click."""
        if self._tracker.is_stopped:
            return

        self._screenshot_capture.stop()
        entry_id = self._tracker.stop()
        self._selector.set_enabled(True)
        self._task_panel.set_enabled(True)
        self._task_panel.set_tracking_task(None)  # Clear tracking indicator
        self._task_panel.refresh()  # Refresh to show updated duration
        self._stats_widget.refresh()  # Refresh daily/weekly totals
        self._activity_widget.reset()

        if entry_id:
            self._tray_icon.show_message(
                "Time Saved",
                f"Time entry saved: {self._selector.get_selection_text()}"
            )

    def _on_tracker_state_changed(self, state: TrackerState):
        """Handle tracker state changes."""
        self._timer_widget.set_state(state)
        self._tray_icon.set_state(state)
        self._status_widget.set_tracking_status(
            state == TrackerState.RUNNING,
            state == TrackerState.PAUSED
        )

    def _on_time_updated(self, seconds: int):
        """Handle time updates."""
        self._timer_widget.update_time(seconds)
        time_str = TimeTracker.format_duration(seconds)
        self._tray_icon.update_time(time_str)

    def _on_activity_updated(self, percentage: float):
        """Handle activity percentage updates."""
        self._activity_widget.set_activity(percentage)
        self._screenshot_capture.set_activity_percentage(percentage)

        if self._tracker.is_running:
            self._tracker.add_activity_sample(percentage)

    def _on_idle_threshold(self):
        """Handle idle threshold being reached."""
        if self._tracker.is_running:
            self._on_pause()
            self._tray_icon.show_message(
                "Auto-Paused",
                f"Tracking paused due to {self.config.idle_threshold // 60} minutes of inactivity."
            )

    def _on_screenshot_taken(self, filepath: str, activity: float):
        """Handle screenshot capture."""
        if self._tracker.current_entry and self._tracker.current_entry.id:
            screenshot = Screenshot(
                time_entry_id=self._tracker.current_entry.id,
                filepath=filepath,
                activity_percentage=activity
            )
            self.db_manager.add_screenshot(screenshot)

            # Increment screenshot counter and update display
            self._status_widget.increment_screenshot_count()

            # Play a short beep sound (frequency 800Hz, duration 100ms)
            try:
                winsound.Beep(800, 100)
            except Exception:
                pass  # Ignore sound errors

    def _on_screenshot_skipped(self, reason: str):
        """Handle screenshot skip."""
        # Update status to show why screenshot was skipped
        self._status_widget.set_status(f"Screenshot skipped: {reason}")

    def _on_add_client(self):
        """Show add client dialog."""
        dialog = ClientDialog(parent=self)
        if dialog.exec():
            client = dialog.get_client()
            try:
                self.db_manager.add_client(client)
                self._selector.refresh_clients()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not add client: {e}")

    def _on_edit_client(self, client_id: int):
        """Show edit client dialog."""
        client = self.db_manager.get_client(client_id)
        if not client:
            return

        dialog = ClientDialog(client, parent=self)
        if dialog.exec():
            updated_client = dialog.get_client()
            try:
                self.db_manager.update_client(updated_client)
                self._selector.refresh_clients()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not update client: {e}")

    def _on_add_project(self):
        """Show add project dialog."""
        client_id = self._selector.selected_client_id
        if not client_id:
            QMessageBox.warning(self, "Selection Required", "Please select a client first.")
            return

        dialog = ProjectDialog(client_id, parent=self)
        if dialog.exec():
            project = dialog.get_project()
            try:
                self.db_manager.add_project(project)
                self._selector.refresh_projects()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not add project: {e}")

    def _on_edit_project(self, project_id: int):
        """Show edit project dialog."""
        project = self.db_manager.get_project(project_id)
        if not project:
            return

        dialog = ProjectDialog(project.client_id, project, parent=self)
        if dialog.exec():
            updated_project = dialog.get_project()
            try:
                self.db_manager.update_project(updated_project)
                self._selector.refresh_projects()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not update project: {e}")

    def _on_add_task(self):
        """Show add task dialog."""
        project_id = self._selector.selected_project_id
        if not project_id:
            QMessageBox.warning(self, "Selection Required", "Please select a project first.")
            return

        dialog = TaskDialog(project_id, parent=self)
        if dialog.exec():
            task = dialog.get_task()
            try:
                self.db_manager.add_task(task)
                self._task_panel.refresh()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not add task: {e}")

    def _on_manual_entry(self):
        """Show manual entry dialog."""
        dialog = ManualEntryDialog(self.db_manager, parent=self)
        if dialog.exec():
            entry = dialog.get_time_entry()
            if entry:
                try:
                    self.db_manager.add_time_entry(entry)
                    QMessageBox.information(
                        self, "Entry Added",
                        f"Manual time entry added: {entry.duration_formatted}"
                    )
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Could not add entry: {e}")

    def _on_reports(self):
        """Show reports dialog."""
        try:
            dialog = ReportsDialog(self.db_manager, self.config, parent=self)
            dialog.exec()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open reports: {e}")

    def _on_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.config, parent=self)
        if dialog.exec():
            # Apply updated settings
            self._screenshot_capture.interval_seconds = self.config.screenshot_interval
            self._screenshot_capture.quality = self.config.screenshot_quality
            self._idle_detector.threshold_seconds = self.config.idle_threshold
            self._status_widget.set_screenshots_status(self.config.screenshots_enabled)

            # Refresh KPI cards to show updated settings (earnings/targets)
            self._stats_widget.refresh()

            # Handle auto-start change
            if dialog.is_auto_start_changed():
                from ..utils.startup import set_auto_start
                set_auto_start(self.config.auto_start_enabled)

    def _show_from_tray(self):
        """Show window from tray."""
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _on_quit(self):
        """Handle quit request."""
        if self._tracker.is_running or self._tracker.is_paused:
            reply = QMessageBox.question(
                self, "Confirm Quit",
                "Tracking is in progress. Stop and save before quitting?",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return
            if reply == QMessageBox.StandardButton.Yes:
                self._on_stop()

        # Stop all background processes
        self._screenshot_capture.stop()
        self._activity_monitor.stop()
        self._tray_icon.hide()

        # Force close and quit
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QCoreApplication
        self.close()
        QCoreApplication.processEvents()
        QApplication.quit()

        # Force exit if threads are still running
        import sys
        sys.exit(0)

    def closeEvent(self, event: QCloseEvent):
        """Handle window close event."""
        if self.config.minimize_to_tray:
            event.ignore()
            self.hide()
            self._tray_icon.show_message(
                "Time Tracker",
                "Application minimized to system tray."
            )
        else:
            self._on_quit()
            event.accept()
