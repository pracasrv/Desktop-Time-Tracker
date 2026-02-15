"""Dialog for manual time entry."""

from datetime import datetime, timedelta
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QDateTimeEdit, QSpinBox, QTextEdit, QPushButton, QLabel
)
from PySide6.QtCore import QDateTime

from ...database.models import TimeEntry
from ...database.db_manager import DatabaseManager


class ManualEntryDialog(QDialog):
    """Dialog for adding manual time entries."""

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self._setup_ui()

    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Manual Time Entry")
        self.setFixedWidth(450)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ccc;
                font-size: 13px;
            }
            QComboBox, QDateTimeEdit, QSpinBox, QTextEdit {
                padding: 8px;
                font-size: 13px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: white;
            }
            QComboBox:focus, QDateTimeEdit:focus, QSpinBox:focus, QTextEdit:focus {
                border-color: #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: white;
                selection-background-color: #0078d4;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Client selector
        self._client_combo = QComboBox()
        self._client_combo.addItem("-- Select Client --", None)
        for client in self.db_manager.get_all_clients():
            self._client_combo.addItem(client.name, client.id)
        self._client_combo.currentIndexChanged.connect(self._on_client_changed)
        form_layout.addRow("Client:", self._client_combo)

        # Project selector
        self._project_combo = QComboBox()
        self._project_combo.addItem("-- Select Project --", None)
        self._project_combo.currentIndexChanged.connect(self._on_project_changed)
        form_layout.addRow("Project:", self._project_combo)

        # Task selector
        self._task_combo = QComboBox()
        self._task_combo.addItem("-- Select Task --", None)
        form_layout.addRow("Task:", self._task_combo)

        # Start date/time
        self._start_datetime = QDateTimeEdit()
        self._start_datetime.setDateTime(QDateTime.currentDateTime().addSecs(-3600))
        self._start_datetime.setCalendarPopup(True)
        self._start_datetime.setDisplayFormat("yyyy-MM-dd HH:mm")
        form_layout.addRow("Start Time:", self._start_datetime)

        # Duration (in minutes for easy entry)
        duration_layout = QHBoxLayout()
        self._hours_spin = QSpinBox()
        self._hours_spin.setRange(0, 23)
        self._hours_spin.setSuffix(" hrs")
        duration_layout.addWidget(self._hours_spin)

        self._minutes_spin = QSpinBox()
        self._minutes_spin.setRange(0, 59)
        self._minutes_spin.setValue(30)
        self._minutes_spin.setSuffix(" min")
        duration_layout.addWidget(self._minutes_spin)

        form_layout.addRow("Duration:", duration_layout)

        # Notes
        self._notes_edit = QTextEdit()
        self._notes_edit.setPlaceholderText("Optional notes about this time entry...")
        self._notes_edit.setMaximumHeight(80)
        form_layout.addRow("Notes:", self._notes_edit)

        layout.addLayout(form_layout)

        # Info label
        info_label = QLabel("Manual entries are marked and won't have activity tracking or screenshots.")
        info_label.setStyleSheet("color: #888; font-size: 11px; font-style: italic;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #555;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Add Entry")
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
        """)
        save_btn.clicked.connect(self._on_save)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

    def _on_client_changed(self):
        """Handle client selection change."""
        self._project_combo.clear()
        self._project_combo.addItem("-- Select Project --", None)

        client_id = self._client_combo.currentData()
        if client_id:
            for project in self.db_manager.get_projects_by_client(client_id):
                self._project_combo.addItem(project.name, project.id)

        self._on_project_changed()

    def _on_project_changed(self):
        """Handle project selection change."""
        self._task_combo.clear()
        self._task_combo.addItem("-- Select Task --", None)

        project_id = self._project_combo.currentData()
        if project_id:
            for task in self.db_manager.get_tasks_by_project(project_id):
                self._task_combo.addItem(task.name, task.id)

    def _on_save(self):
        """Validate and save the entry."""
        task_id = self._task_combo.currentData()
        if not task_id:
            return

        hours = self._hours_spin.value()
        minutes = self._minutes_spin.value()
        if hours == 0 and minutes == 0:
            return

        self.accept()

    def get_time_entry(self) -> Optional[TimeEntry]:
        """Get the time entry data from the form."""
        task_id = self._task_combo.currentData()
        if not task_id:
            return None

        hours = self._hours_spin.value()
        minutes = self._minutes_spin.value()
        duration_seconds = (hours * 3600) + (minutes * 60)

        if duration_seconds == 0:
            return None

        start_time = self._start_datetime.dateTime().toPyDateTime()
        end_time = start_time + timedelta(seconds=duration_seconds)

        return TimeEntry(
            task_id=task_id,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            activity_percentage=100.0,  # Manual entries assumed 100% productive
            notes=self._notes_edit.toPlainText().strip(),
            is_manual=True
        )
