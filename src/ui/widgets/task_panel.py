"""Collapsible task panel widget for the side bar."""

from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Signal, Qt

from ...database.db_manager import DatabaseManager
from .task_list_widget import TaskListWidget


class TaskPanelWidget(QWidget):
    """Collapsible panel showing tasks for the selected project."""

    # Signals
    add_task_clicked = Signal()
    task_start_requested = Signal(int)  # task_id
    task_completion_changed = Signal(int, bool)  # task_id, is_completed

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self._current_project_id: Optional[int] = None
        self._setup_ui()

    def _setup_ui(self):
        """Set up the panel UI."""
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            TaskPanelWidget {
                background-color: #252525;
                border-left: 1px solid #3a3a3a;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(48)
        header.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-bottom: 1px solid #3a3a3a;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 10, 0)

        title = QLabel("Tasks")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #e0e0e0;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self._add_task_btn = QPushButton("+ Add")
        self._add_task_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                font-size: 12px;
                border: 1px solid #28a745;
                border-radius: 4px;
                background-color: transparent;
                color: #28a745;
            }
            QPushButton:hover {
                background-color: #28a745;
                color: white;
            }
            QPushButton:disabled {
                border-color: #555;
                color: #555;
            }
        """)
        self._add_task_btn.clicked.connect(self.add_task_clicked.emit)
        header_layout.addWidget(self._add_task_btn)

        layout.addWidget(header)

        # Task list
        self._task_list = TaskListWidget(self.db_manager)
        self._task_list.task_start_requested.connect(self.task_start_requested.emit)
        self._task_list.task_completion_changed.connect(self.task_completion_changed.emit)
        layout.addWidget(self._task_list, 1)

    def set_project(self, project_id: Optional[int]):
        """Set the current project and load its tasks."""
        self._current_project_id = project_id
        self._add_task_btn.setEnabled(project_id is not None)
        # TaskListWidget handles its own empty state display
        self._task_list.set_project(project_id)

    def refresh(self):
        """Refresh the task list."""
        self._task_list.refresh()

    def set_tracking_task(self, task_id: Optional[int]):
        """Set which task is currently being tracked."""
        self._task_list.set_tracking_task(task_id)

    def set_enabled(self, enabled: bool):
        """Enable or disable the panel (for tracking state).

        Note: Add task button stays enabled as long as a project is selected,
        allowing users to add new tasks even while tracking.
        """
        # Add task button should always be enabled when a project is selected
        # (not affected by tracking state)
        self._task_list.setEnabled(enabled)
