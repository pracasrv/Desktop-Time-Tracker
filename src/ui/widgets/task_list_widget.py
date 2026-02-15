"""Task list widget with play buttons and duration display."""

from typing import Optional, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QPushButton, QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Signal, Qt

from ...database.db_manager import DatabaseManager
from ...database.models import Task


class TaskRowWidget(QFrame):
    """Individual task row in the list."""

    start_clicked = Signal(int)  # task_id
    complete_clicked = Signal(int, bool)  # task_id, is_completed

    def __init__(self, task: Task, total_duration: int = 0, parent=None):
        super().__init__(parent)
        self.task = task
        self.total_duration = total_duration
        self._is_tracking = False
        self._setup_ui()

    def _setup_ui(self):
        """Set up the widget UI."""
        self.setFixedHeight(44)
        self._update_style()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(12)

        # Play/Start button
        self._play_btn = QPushButton()
        self._play_btn.setFixedSize(28, 28)
        self._play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._play_btn.clicked.connect(lambda: self.start_clicked.emit(self.task.id))
        self._update_play_button()
        layout.addWidget(self._play_btn)

        # Task name
        self._name_label = QLabel(self.task.name)
        self._name_label.setStyleSheet("font-size: 13px; color: #e0e0e0;")
        if self.task.is_completed:
            self._name_label.setStyleSheet(
                "font-size: 13px; color: #666; text-decoration: line-through;"
            )
        layout.addWidget(self._name_label, 1)

        # Notes indicator (shows when task has notes)
        self._notes_indicator = QLabel()
        self._notes_indicator.setFixedWidth(18)
        if self.task.notes:
            self._notes_indicator.setText("[i]")
            self._notes_indicator.setStyleSheet("font-size: 11px; color: #888;")
            self._notes_indicator.setToolTip(self.task.notes)
        else:
            self._notes_indicator.hide()
        layout.addWidget(self._notes_indicator)

        # Completion checkbox (small, subtle)
        self._complete_btn = QPushButton()
        self._complete_btn.setFixedSize(22, 22)
        self._complete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._complete_btn.setToolTip("Mark as complete" if not self.task.is_completed else "Mark as incomplete")
        self._complete_btn.clicked.connect(self._on_complete_clicked)
        self._update_complete_button()
        layout.addWidget(self._complete_btn)

        # Duration label
        duration_text = self._format_duration(self.total_duration)
        self._duration_label = QLabel(duration_text)
        self._duration_label.setFixedWidth(60)
        self._duration_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._duration_label.setStyleSheet("font-size: 12px; color: #888; font-family: 'Consolas', monospace;")
        layout.addWidget(self._duration_label)

    def _update_style(self):
        """Update row styling based on state."""
        if self._is_tracking:
            self.setStyleSheet("""
                TaskRowWidget {
                    background-color: #1e3a5f;
                    border: none;
                    border-bottom: 1px solid #2a4a6f;
                }
            """)
        elif self.task.is_completed:
            self.setStyleSheet("""
                TaskRowWidget {
                    background-color: #252525;
                    border: none;
                    border-bottom: 1px solid #333;
                }
            """)
        else:
            self.setStyleSheet("""
                TaskRowWidget {
                    background-color: #2d2d2d;
                    border: none;
                    border-bottom: 1px solid #3a3a3a;
                }
                TaskRowWidget:hover {
                    background-color: #353535;
                }
            """)

    def _update_play_button(self):
        """Update play button appearance."""
        if self._is_tracking:
            # Show pause-like indicator when tracking
            self._play_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    border: none;
                    border-radius: 14px;
                    font-size: 14px;
                    color: white;
                }
            """)
            self._play_btn.setText("●")
            self._play_btn.setEnabled(False)
        elif self.task.is_completed:
            self._play_btn.setStyleSheet("""
                QPushButton {
                    background-color: #444;
                    border: none;
                    border-radius: 14px;
                    font-size: 12px;
                    color: #666;
                }
            """)
            self._play_btn.setText("▶")
            self._play_btn.setEnabled(False)
        else:
            self._play_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 2px solid #28a745;
                    border-radius: 14px;
                    font-size: 12px;
                    color: #28a745;
                }
                QPushButton:hover {
                    background-color: #28a745;
                    color: white;
                }
            """)
            self._play_btn.setText("▶")
            self._play_btn.setEnabled(True)

    def _update_complete_button(self):
        """Update completion button appearance."""
        if self.task.is_completed:
            self._complete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            self._complete_btn.setText("✓")
        else:
            self._complete_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid #555;
                    border-radius: 4px;
                    font-size: 10px;
                    color: #555;
                }
                QPushButton:hover {
                    border-color: #888;
                    color: #888;
                }
            """)
            self._complete_btn.setText("")

    def _on_complete_clicked(self):
        """Handle completion button click."""
        new_state = not self.task.is_completed
        self.task.is_completed = new_state
        self._update_complete_button()
        self._update_play_button()
        self._update_style()

        if new_state:
            self._name_label.setStyleSheet(
                "font-size: 13px; color: #666; text-decoration: line-through;"
            )
        else:
            self._name_label.setStyleSheet("font-size: 13px; color: #e0e0e0;")

        self.complete_clicked.emit(self.task.id, new_state)

    def _format_duration(self, seconds: int) -> str:
        """Format seconds as HH:MM."""
        hours, remainder = divmod(seconds, 3600)
        minutes = remainder // 60
        return f"{hours:02d}:{minutes:02d}"

    def set_tracking(self, is_tracking: bool):
        """Update UI when this task is being tracked."""
        self._is_tracking = is_tracking
        self._update_style()
        self._update_play_button()


class TaskListWidget(QWidget):
    """Widget displaying a list of tasks for a project."""

    task_start_requested = Signal(int)  # task_id
    task_completion_changed = Signal(int, bool)  # task_id, is_completed

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self._current_project_id: Optional[int] = None
        self._task_widgets: dict = {}  # task_id -> TaskRowWidget
        self._tracking_task_id: Optional[int] = None
        self._setup_ui()

    def _setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header row
        header = QFrame()
        header.setFixedHeight(32)
        header.setStyleSheet("background-color: #252525; border-bottom: 1px solid #3a3a3a;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 0, 12, 0)
        header_layout.setSpacing(12)

        # Spacer for play button column
        header_layout.addSpacing(28)

        task_header = QLabel("Task")
        task_header.setStyleSheet("font-size: 11px; color: #888; font-weight: bold;")
        header_layout.addWidget(task_header, 1)

        notes_header = QLabel("")  # Notes indicator column (no header text)
        notes_header.setFixedWidth(18)
        header_layout.addWidget(notes_header)

        status_header = QLabel("Done")
        status_header.setFixedWidth(22)
        status_header.setStyleSheet("font-size: 11px; color: #888; font-weight: bold;")
        header_layout.addWidget(status_header)

        duration_header = QLabel("Time")
        duration_header.setFixedWidth(60)
        duration_header.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        duration_header.setStyleSheet("font-size: 11px; color: #888; font-weight: bold;")
        header_layout.addWidget(duration_header)

        layout.addWidget(header)

        # Scroll area for task list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #2d2d2d;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Container for task items
        self._tasks_container = QWidget()
        self._tasks_container.setStyleSheet("background-color: #2d2d2d;")
        self._tasks_layout = QVBoxLayout(self._tasks_container)
        self._tasks_layout.setContentsMargins(0, 0, 0, 0)
        self._tasks_layout.setSpacing(0)
        self._tasks_layout.addStretch()

        scroll_area.setWidget(self._tasks_container)
        layout.addWidget(scroll_area)

        # Empty state label (added to layout but hidden initially)
        self._empty_label = QLabel("No tasks yet")
        self._empty_label.setStyleSheet("color: #666; font-size: 13px; padding: 20px;")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.hide()
        self._tasks_layout.insertWidget(0, self._empty_label)

    def set_project(self, project_id: Optional[int]):
        """Set the current project and load its tasks."""
        self._current_project_id = project_id
        self.refresh()

    def refresh(self):
        """Refresh the task list."""
        # Clear existing task widgets (but keep empty_label and stretch)
        for widget in self._task_widgets.values():
            widget.deleteLater()
        self._task_widgets.clear()

        # Remove task row widgets only (skip empty_label at index 0 and stretch at end)
        # We need to remove from index 1 up to count-1 (excluding stretch)
        while self._tasks_layout.count() > 2:  # Keep empty_label and stretch
            item = self._tasks_layout.takeAt(1)  # Take from index 1 (after empty_label)
            if item.widget():
                item.widget().deleteLater()

        if not self._current_project_id:
            self._show_empty("Select a project")
            return

        tasks = self.db_manager.get_tasks_by_project(
            self._current_project_id,
            active_only=True,
            include_completed=True
        )

        if not tasks:
            self._show_empty("No tasks yet")
            return

        self._empty_label.hide()

        # Get task durations
        task_durations = self._get_task_durations(tasks)

        # Add task widgets (insert after empty_label which is at index 0)
        for i, task in enumerate(tasks):
            duration = task_durations.get(task.id, 0)
            task_widget = TaskRowWidget(task, duration)
            task_widget.start_clicked.connect(self._on_task_start)
            task_widget.complete_clicked.connect(self._on_completion_changed)

            if task.id == self._tracking_task_id:
                task_widget.set_tracking(True)

            self._task_widgets[task.id] = task_widget
            self._tasks_layout.insertWidget(i + 1, task_widget)  # +1 to insert after empty_label

    def _show_empty(self, message: str):
        """Show empty state message."""
        self._empty_label.setText(message)
        self._empty_label.show()

    def _get_task_durations(self, tasks: List[Task]) -> dict:
        """Get total duration for each task."""
        if not tasks:
            return {}

        # Initialize all tasks with 0 duration
        durations = {task.id: 0 for task in tasks}

        # Get all durations in one query for efficiency
        task_ids = [task.id for task in tasks]
        conn = self.db_manager._get_connection()
        cursor = conn.cursor()

        placeholders = ','.join('?' * len(task_ids))
        cursor.execute(
            f'''SELECT task_id, COALESCE(SUM(duration_seconds), 0) as total
                FROM time_entries
                WHERE task_id IN ({placeholders})
                GROUP BY task_id''',
            task_ids
        )

        for row in cursor.fetchall():
            durations[row['task_id']] = row['total']

        conn.close()
        return durations

    def _on_task_start(self, task_id: int):
        """Handle task start button click."""
        self.task_start_requested.emit(task_id)

    def _on_completion_changed(self, task_id: int, is_completed: bool):
        """Handle task completion checkbox change."""
        self.db_manager.mark_task_completed(task_id, is_completed)
        self.task_completion_changed.emit(task_id, is_completed)

    def set_tracking_task(self, task_id: Optional[int]):
        """Update which task is currently being tracked."""
        # Reset previous tracking task
        if self._tracking_task_id and self._tracking_task_id in self._task_widgets:
            self._task_widgets[self._tracking_task_id].set_tracking(False)

        self._tracking_task_id = task_id

        # Highlight new tracking task
        if task_id and task_id in self._task_widgets:
            self._task_widgets[task_id].set_tracking(True)

    def set_enabled(self, enabled: bool):
        """Enable or disable the task list."""
        for widget in self._task_widgets.values():
            widget.setEnabled(enabled)
