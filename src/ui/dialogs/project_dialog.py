"""Dialog for adding/editing projects."""

from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QDoubleSpinBox, QPushButton, QCheckBox
)

from ...database.models import Project


class ProjectDialog(QDialog):
    """Dialog for adding or editing a project."""

    def __init__(self, client_id: int, project: Optional[Project] = None, parent=None):
        super().__init__(parent)
        self._client_id = client_id
        self._project = project
        self._setup_ui()

        if project:
            self._populate_fields()

    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Add Project" if not self._project else "Edit Project")
        self.setFixedWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ccc;
                font-size: 13px;
            }
            QLineEdit, QDoubleSpinBox {
                padding: 8px;
                font-size: 13px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: white;
            }
            QLineEdit:focus, QDoubleSpinBox:focus {
                border-color: #0078d4;
            }
            QCheckBox {
                color: #ccc;
                font-size: 13px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Name field
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Enter project name")
        form_layout.addRow("Name:", self._name_edit)

        # Custom rate checkbox
        self._custom_rate_check = QCheckBox("Override client hourly rate")
        self._custom_rate_check.stateChanged.connect(self._on_custom_rate_changed)
        form_layout.addRow("", self._custom_rate_check)

        # Hourly rate field
        self._rate_spin = QDoubleSpinBox()
        self._rate_spin.setRange(0, 10000)
        self._rate_spin.setDecimals(2)
        self._rate_spin.setPrefix("$ ")
        self._rate_spin.setValue(0)
        self._rate_spin.setEnabled(False)
        form_layout.addRow("Hourly Rate:", self._rate_spin)

        layout.addLayout(form_layout)

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
        """Populate fields with existing project data."""
        if self._project:
            self._name_edit.setText(self._project.name)
            if self._project.hourly_rate is not None:
                self._custom_rate_check.setChecked(True)
                self._rate_spin.setValue(self._project.hourly_rate)

    def _on_custom_rate_changed(self, state):
        """Handle custom rate checkbox change."""
        self._rate_spin.setEnabled(state == 2)  # Qt.CheckState.Checked

    def _on_save(self):
        """Validate and save the project."""
        name = self._name_edit.text().strip()
        if not name:
            self._name_edit.setFocus()
            return

        self.accept()

    def get_project(self) -> Project:
        """Get the project data from the form."""
        hourly_rate = None
        if self._custom_rate_check.isChecked():
            hourly_rate = self._rate_spin.value()

        return Project(
            id=self._project.id if self._project else None,
            client_id=self._client_id,
            name=self._name_edit.text().strip(),
            hourly_rate=hourly_rate,
            is_active=True
        )
