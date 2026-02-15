"""Dialog for adding/editing clients with full details."""

from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QDoubleSpinBox, QPushButton, QLabel,
    QTextEdit, QTabWidget, QWidget
)
from PySide6.QtCore import Qt

from ...database.models import Client


class ClientDialog(QDialog):
    """Dialog for adding or editing a client with full details."""

    def __init__(self, client: Optional[Client] = None, parent=None):
        super().__init__(parent)
        self._client = client
        self._setup_ui()

        if client:
            self._populate_fields()

    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Add Client" if not self._client else "Edit Client")
        self.setMinimumWidth(450)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ccc;
                font-size: 13px;
            }
            QLineEdit, QDoubleSpinBox, QTextEdit {
                padding: 8px;
                font-size: 13px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: white;
            }
            QLineEdit:focus, QDoubleSpinBox:focus, QTextEdit:focus {
                border-color: #0078d4;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                border-radius: 4px;
                background-color: #252525;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #aaa;
                padding: 8px 16px;
                border: 1px solid #444;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #252525;
                color: white;
            }
            QTabBar::tab:hover {
                color: white;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Tab widget for organizing fields
        tabs = QTabWidget()

        # Basic Info Tab
        basic_tab = QWidget()
        basic_layout = QFormLayout(basic_tab)
        basic_layout.setSpacing(12)
        basic_layout.setContentsMargins(15, 15, 15, 15)

        # Name field
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Enter client name")
        basic_layout.addRow("Name:", self._name_edit)

        # Hourly rate field
        self._rate_spin = QDoubleSpinBox()
        self._rate_spin.setRange(0, 10000)
        self._rate_spin.setDecimals(2)
        self._rate_spin.setPrefix("$ ")
        self._rate_spin.setValue(0)
        basic_layout.addRow("Hourly Rate:", self._rate_spin)

        # Email field
        self._email_edit = QLineEdit()
        self._email_edit.setPlaceholderText("client@example.com")
        basic_layout.addRow("Email:", self._email_edit)

        # Phone field
        self._phone_edit = QLineEdit()
        self._phone_edit.setPlaceholderText("+1 234 567 8900")
        basic_layout.addRow("Phone:", self._phone_edit)

        tabs.addTab(basic_tab, "Basic Info")

        # Details Tab
        details_tab = QWidget()
        details_layout = QFormLayout(details_tab)
        details_layout.setSpacing(12)
        details_layout.setContentsMargins(15, 15, 15, 15)

        # Address field
        self._address_edit = QTextEdit()
        self._address_edit.setPlaceholderText("Enter client address...")
        self._address_edit.setMaximumHeight(80)
        details_layout.addRow("Address:", self._address_edit)

        # Notes field
        self._notes_edit = QTextEdit()
        self._notes_edit.setPlaceholderText("Additional notes about this client...")
        self._notes_edit.setMaximumHeight(100)
        details_layout.addRow("Notes:", self._notes_edit)

        tabs.addTab(details_tab, "Details")

        layout.addWidget(tabs)

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
        """Populate fields with existing client data."""
        if self._client:
            self._name_edit.setText(self._client.name)
            self._rate_spin.setValue(self._client.hourly_rate)
            self._email_edit.setText(self._client.email)
            self._phone_edit.setText(self._client.phone)
            self._address_edit.setPlainText(self._client.address)
            self._notes_edit.setPlainText(self._client.notes)

    def _on_save(self):
        """Validate and save the client."""
        name = self._name_edit.text().strip()
        if not name:
            self._name_edit.setFocus()
            return

        self.accept()

    def get_client(self) -> Client:
        """Get the client data from the form."""
        return Client(
            id=self._client.id if self._client else None,
            name=self._name_edit.text().strip(),
            hourly_rate=self._rate_spin.value(),
            email=self._email_edit.text().strip(),
            phone=self._phone_edit.text().strip(),
            address=self._address_edit.toPlainText().strip(),
            notes=self._notes_edit.toPlainText().strip(),
            is_active=True
        )
