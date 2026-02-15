"""Dialog for adding/editing tasks."""

from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QPushButton, QLabel
)

from ...database.models import Task


class TaskDialog(QDialog):
    """Dialog for adding or editing a task."""

    def __init__(self, project_id: int, task: Optional[Task] = None, parent=None):
        super().__init__(parent)
        self._project_id = project_id
        self._task = task
        self._setup_ui()

        if task:
            self._populate_fields()

    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Add Task" if not self._task else "Edit Task")
        self.setFixedWidth(450)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ccc;
                font-size: 13px;
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                font-size: 13px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: white;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #0078d4;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Name field
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Enter task name")
        form_layout.addRow("Name:", self._name_edit)

        layout.addLayout(form_layout)

        # Notes field (separate from form layout for better sizing)
        notes_label = QLabel("Notes:")
        notes_label.setStyleSheet("color: #ccc; font-size: 13px; margin-top: 5px;")
        layout.addWidget(notes_label)

        self._notes_edit = QTextEdit()
        self._notes_edit.setPlaceholderText("Personal notes (not included in reports)")
        self._notes_edit.setFixedHeight(100)
        layout.addWidget(self._notes_edit)

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

        save_btn = QPushButton("Save")
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

    def _populate_fields(self):
        """Populate fields with existing task data."""
        if self._task:
            self._name_edit.setText(self._task.name)
            self._notes_edit.setPlainText(self._task.notes or "")

    def _on_save(self):
        """Validate and save the task."""
        name = self._name_edit.text().strip()
        if not name:
            self._name_edit.setFocus()
            return

        self.accept()

    def get_task(self) -> Task:
        """Get the task data from the form."""
        return Task(
            id=self._task.id if self._task else None,
            project_id=self._project_id,
            name=self._name_edit.text().strip(),
            notes=self._notes_edit.toPlainText().strip(),
            is_active=True
        )
