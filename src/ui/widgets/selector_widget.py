"""Selector widget for Client/Project selection."""

from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel
)
from PySide6.QtCore import Signal

from ...database.db_manager import DatabaseManager
from ...database.models import Client, Project, Task
from ...utils.config import Config


class SelectorWidget(QWidget):
    """Widget for selecting Client/Project."""

    # Signals
    selection_changed = Signal()
    add_client_clicked = Signal()
    add_project_clicked = Signal()
    edit_client_clicked = Signal(int)  # client_id
    edit_project_clicked = Signal(int)  # project_id

    def __init__(self, db_manager: DatabaseManager, config: Config = None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.config = config
        self._setup_ui()
        self._restore_last_selection()

    def _setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        combo_style = """
            QComboBox {
                padding: 8px 12px;
                font-size: 13px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: white;
                min-width: 200px;
            }
            QComboBox:hover {
                border-color: #888;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #888;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: white;
                selection-background-color: #0078d4;
            }
        """

        btn_style = """
            QPushButton {
                padding: 8px 12px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: #00ff88;
                min-width: 35px;
                max-width: 35px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #00ff88;
            }
            QPushButton:disabled {
                color: #555;
                border-color: #444;
            }
        """

        edit_btn_style = """
            QPushButton {
                padding: 8px 10px;
                font-size: 12px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: #888;
                min-width: 30px;
                max-width: 30px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #888;
                color: #ccc;
            }
            QPushButton:disabled {
                color: #444;
            }
        """

        label_style = "color: #aaa; font-size: 12px; font-weight: bold;"

        # Client selector
        client_layout = QHBoxLayout()
        client_label = QLabel("Client:")
        client_label.setStyleSheet(label_style)
        client_label.setFixedWidth(60)
        client_layout.addWidget(client_label)

        self._client_combo = QComboBox()
        self._client_combo.setStyleSheet(combo_style)
        self._client_combo.currentIndexChanged.connect(self._on_client_changed)
        client_layout.addWidget(self._client_combo, 1)

        self._edit_client_btn = QPushButton("...")
        self._edit_client_btn.setStyleSheet(edit_btn_style)
        self._edit_client_btn.setToolTip("Edit client")
        self._edit_client_btn.clicked.connect(self._on_edit_client)
        self._edit_client_btn.setEnabled(False)
        client_layout.addWidget(self._edit_client_btn)

        self._add_client_btn = QPushButton("+")
        self._add_client_btn.setStyleSheet(btn_style)
        self._add_client_btn.setToolTip("Add new client")
        self._add_client_btn.clicked.connect(self.add_client_clicked.emit)
        client_layout.addWidget(self._add_client_btn)

        layout.addLayout(client_layout)

        # Project selector
        project_layout = QHBoxLayout()
        project_label = QLabel("Project:")
        project_label.setStyleSheet(label_style)
        project_label.setFixedWidth(60)
        project_layout.addWidget(project_label)

        self._project_combo = QComboBox()
        self._project_combo.setStyleSheet(combo_style)
        self._project_combo.currentIndexChanged.connect(self._on_project_changed)
        project_layout.addWidget(self._project_combo, 1)

        self._edit_project_btn = QPushButton("...")
        self._edit_project_btn.setStyleSheet(edit_btn_style)
        self._edit_project_btn.setToolTip("Edit project")
        self._edit_project_btn.clicked.connect(self._on_edit_project)
        self._edit_project_btn.setEnabled(False)
        project_layout.addWidget(self._edit_project_btn)

        self._add_project_btn = QPushButton("+")
        self._add_project_btn.setStyleSheet(btn_style)
        self._add_project_btn.setToolTip("Add new project")
        self._add_project_btn.clicked.connect(self.add_project_clicked.emit)
        project_layout.addWidget(self._add_project_btn)

        layout.addLayout(project_layout)

    def refresh_clients(self):
        """Refresh the client list."""
        self._client_combo.blockSignals(True)
        current_id = self.selected_client_id

        self._client_combo.clear()
        self._client_combo.addItem("-- Select Client --", None)

        clients = self.db_manager.get_all_clients()
        for client in clients:
            self._client_combo.addItem(client.name, client.id)

        # Try to restore selection
        if current_id:
            index = self._client_combo.findData(current_id)
            if index >= 0:
                self._client_combo.setCurrentIndex(index)

        self._client_combo.blockSignals(False)
        self._on_client_changed()

    def refresh_projects(self):
        """Refresh the project list for current client."""
        self._project_combo.blockSignals(True)
        current_id = self.selected_project_id

        self._project_combo.clear()
        self._project_combo.addItem("-- Select Project --", None)

        client_id = self.selected_client_id
        if client_id:
            projects = self.db_manager.get_projects_by_client(client_id)
            for project in projects:
                self._project_combo.addItem(project.name, project.id)

        # Try to restore selection
        if current_id:
            index = self._project_combo.findData(current_id)
            if index >= 0:
                self._project_combo.setCurrentIndex(index)

        self._project_combo.blockSignals(False)
        self._on_project_changed()

    def _on_client_changed(self):
        """Handle client selection change."""
        self._edit_client_btn.setEnabled(self.selected_client_id is not None)
        # Save last selection
        if self.config and self.selected_client_id is not None:
            self.config.last_client_id = self.selected_client_id
        self.refresh_projects()

    def _on_project_changed(self):
        """Handle project selection change."""
        self._edit_project_btn.setEnabled(self.selected_project_id is not None)
        # Save last selection
        if self.config and self.selected_project_id is not None:
            self.config.last_project_id = self.selected_project_id
        self.selection_changed.emit()

    def _restore_last_selection(self):
        """Restore the last selected client and project from config."""
        # First load all clients
        self._client_combo.blockSignals(True)
        self._client_combo.clear()
        self._client_combo.addItem("-- Select Client --", None)

        clients = self.db_manager.get_all_clients()
        for client in clients:
            self._client_combo.addItem(client.name, client.id)

        # Restore last client if available
        if self.config and self.config.last_client_id:
            index = self._client_combo.findData(self.config.last_client_id)
            if index >= 0:
                self._client_combo.setCurrentIndex(index)

        self._client_combo.blockSignals(False)
        self._edit_client_btn.setEnabled(self.selected_client_id is not None)

        # Now load projects for selected client
        self._project_combo.blockSignals(True)
        self._project_combo.clear()
        self._project_combo.addItem("-- Select Project --", None)

        if self.selected_client_id:
            projects = self.db_manager.get_projects_by_client(self.selected_client_id)
            for project in projects:
                self._project_combo.addItem(project.name, project.id)

            # Restore last project if available
            if self.config and self.config.last_project_id:
                index = self._project_combo.findData(self.config.last_project_id)
                if index >= 0:
                    self._project_combo.setCurrentIndex(index)

        self._project_combo.blockSignals(False)
        self._edit_project_btn.setEnabled(self.selected_project_id is not None)

        # Emit selection changed to update task panel
        self.selection_changed.emit()

    def _on_edit_client(self):
        """Handle edit client button click."""
        if self.selected_client_id:
            self.edit_client_clicked.emit(self.selected_client_id)

    def _on_edit_project(self):
        """Handle edit project button click."""
        if self.selected_project_id:
            self.edit_project_clicked.emit(self.selected_project_id)

    @property
    def selected_client_id(self) -> Optional[int]:
        """Get the selected client ID."""
        return self._client_combo.currentData()

    @property
    def selected_project_id(self) -> Optional[int]:
        """Get the selected project ID."""
        return self._project_combo.currentData()

    @property
    def is_valid_selection(self) -> bool:
        """Check if a valid project is selected."""
        return self.selected_project_id is not None

    def set_enabled(self, enabled: bool):
        """Enable or disable the selectors."""
        self._client_combo.setEnabled(enabled)
        self._project_combo.setEnabled(enabled)
        self._add_client_btn.setEnabled(enabled)
        self._add_project_btn.setEnabled(enabled)
        self._edit_client_btn.setEnabled(enabled and self.selected_client_id is not None)
        self._edit_project_btn.setEnabled(enabled and self.selected_project_id is not None)

    def get_selection_text(self) -> str:
        """Get a text representation of current selection."""
        parts = []
        if self._client_combo.currentIndex() > 0:
            parts.append(self._client_combo.currentText())
        if self._project_combo.currentIndex() > 0:
            parts.append(self._project_combo.currentText())
        return " > ".join(parts) if parts else "No selection"

    def get_task_name(self, task_id: int) -> str:
        """Get task name by ID."""
        task = self.db_manager.get_task(task_id)
        return task.name if task else ""
