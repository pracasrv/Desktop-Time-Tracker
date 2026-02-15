"""Settings dialog for application configuration."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton, QLabel, QGroupBox,
    QLineEdit, QTextEdit, QTabWidget, QWidget, QScrollArea
)
from PySide6.QtCore import Qt

from ...utils.config import Config


class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 450)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ccc;
                font-size: 13px;
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
            QGroupBox {
                color: #0078d4;
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QSpinBox, QDoubleSpinBox, QLineEdit {
                padding: 8px;
                font-size: 13px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: white;
            }
            QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus, QTextEdit:focus {
                border-color: #0078d4;
            }
            QTextEdit {
                padding: 8px;
                font-size: 13px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: white;
            }
            QCheckBox {
                color: #ccc;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid #555;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border-color: #0078d4;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Tab widget
        tabs = QTabWidget()

        # ===== General Tab =====
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        general_layout.setSpacing(10)

        # Screenshots group
        screenshots_group = QGroupBox("Screenshots")
        screenshots_layout = QFormLayout()
        screenshots_layout.setSpacing(10)

        self._screenshots_enabled_check = QCheckBox("Enable screenshot capture")
        screenshots_layout.addRow(self._screenshots_enabled_check)

        self._screenshot_interval_spin = QSpinBox()
        self._screenshot_interval_spin.setRange(1, 60)
        self._screenshot_interval_spin.setSuffix(" minutes")
        screenshots_layout.addRow("Capture interval:", self._screenshot_interval_spin)

        self._screenshot_quality_spin = QSpinBox()
        self._screenshot_quality_spin.setRange(10, 100)
        self._screenshot_quality_spin.setSuffix(" %")
        screenshots_layout.addRow("Image quality:", self._screenshot_quality_spin)

        screenshots_group.setLayout(screenshots_layout)
        general_layout.addWidget(screenshots_group)

        # Idle detection group
        idle_group = QGroupBox("Idle Detection")
        idle_layout = QFormLayout()
        idle_layout.setSpacing(10)

        self._idle_threshold_spin = QSpinBox()
        self._idle_threshold_spin.setRange(1, 60)
        self._idle_threshold_spin.setSuffix(" minutes")
        idle_layout.addRow("Auto-pause after:", self._idle_threshold_spin)

        idle_group.setLayout(idle_layout)
        general_layout.addWidget(idle_group)

        # Application group
        app_group = QGroupBox("Application")
        app_layout = QFormLayout()
        app_layout.setSpacing(10)

        self._minimize_to_tray_check = QCheckBox("Minimize to system tray on close")
        app_layout.addRow(self._minimize_to_tray_check)

        self._auto_start_check = QCheckBox("Start with Windows")
        app_layout.addRow(self._auto_start_check)

        self._start_minimized_check = QCheckBox("Start minimized")
        app_layout.addRow(self._start_minimized_check)

        app_group.setLayout(app_layout)
        general_layout.addWidget(app_group)
        general_layout.addStretch()

        tabs.addTab(general_tab, "General")

        # ===== Billing Tab =====
        billing_tab = QWidget()
        billing_layout = QVBoxLayout(billing_tab)
        billing_layout.setSpacing(10)

        billing_group = QGroupBox("Your Details (for Reports)")
        billing_form = QFormLayout()
        billing_form.setSpacing(10)

        self._freelancer_name_edit = QLineEdit()
        self._freelancer_name_edit.setPlaceholderText("Your name or business name")
        billing_form.addRow("Name:", self._freelancer_name_edit)

        self._freelancer_email_edit = QLineEdit()
        self._freelancer_email_edit.setPlaceholderText("your@email.com")
        billing_form.addRow("Email:", self._freelancer_email_edit)

        self._freelancer_address_edit = QTextEdit()
        self._freelancer_address_edit.setPlaceholderText("Your business address...")
        self._freelancer_address_edit.setMaximumHeight(60)
        billing_form.addRow("Address:", self._freelancer_address_edit)

        self._payment_details_edit = QTextEdit()
        self._payment_details_edit.setPlaceholderText("Bank account, PayPal, etc...")
        self._payment_details_edit.setMaximumHeight(80)
        billing_form.addRow("Payment Info:", self._payment_details_edit)

        billing_group.setLayout(billing_form)
        billing_layout.addWidget(billing_group)

        # KPI Dashboard group
        kpi_group = QGroupBox("KPI Dashboard")
        kpi_form = QFormLayout()
        kpi_form.setSpacing(10)

        self._show_kpi_earnings_check = QCheckBox("Show earnings ($) on KPI cards")
        kpi_form.addRow(self._show_kpi_earnings_check)

        self._show_kpi_targets_check = QCheckBox("Show target progress on KPI cards")
        kpi_form.addRow(self._show_kpi_targets_check)

        self._daily_target_spin = QDoubleSpinBox()
        self._daily_target_spin.setRange(0.5, 24.0)
        self._daily_target_spin.setSingleStep(0.5)
        self._daily_target_spin.setSuffix(" hours")
        self._daily_target_spin.setDecimals(1)
        kpi_form.addRow("Daily target:", self._daily_target_spin)

        self._weekly_target_spin = QDoubleSpinBox()
        self._weekly_target_spin.setRange(1.0, 168.0)
        self._weekly_target_spin.setSingleStep(1.0)
        self._weekly_target_spin.setSuffix(" hours")
        self._weekly_target_spin.setDecimals(1)
        kpi_form.addRow("Weekly target:", self._weekly_target_spin)

        kpi_group.setLayout(kpi_form)
        billing_layout.addWidget(kpi_group)
        billing_layout.addStretch()

        tabs.addTab(billing_tab, "Billing")

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

    def _load_settings(self):
        """Load current settings into the form."""
        # General settings
        self._screenshots_enabled_check.setChecked(self.config.screenshots_enabled)
        self._screenshot_interval_spin.setValue(self.config.screenshot_interval // 60)
        self._screenshot_quality_spin.setValue(self.config.screenshot_quality)
        self._idle_threshold_spin.setValue(self.config.idle_threshold // 60)
        self._minimize_to_tray_check.setChecked(self.config.minimize_to_tray)
        self._auto_start_check.setChecked(self.config.auto_start_enabled)
        self._start_minimized_check.setChecked(self.config.start_minimized)

        # Billing settings
        self._freelancer_name_edit.setText(self.config.freelancer_name)
        self._freelancer_email_edit.setText(self.config.freelancer_email)
        self._freelancer_address_edit.setPlainText(self.config.freelancer_address)
        self._payment_details_edit.setPlainText(self.config.payment_details)

        # KPI settings
        self._show_kpi_earnings_check.setChecked(self.config.show_kpi_earnings)
        self._show_kpi_targets_check.setChecked(self.config.show_kpi_targets)
        self._daily_target_spin.setValue(self.config.daily_target_hours)
        self._weekly_target_spin.setValue(self.config.weekly_target_hours)

    def _on_save(self):
        """Save settings and close dialog."""
        # General settings
        self.config.screenshots_enabled = self._screenshots_enabled_check.isChecked()
        self.config.screenshot_interval = self._screenshot_interval_spin.value() * 60
        self.config.screenshot_quality = self._screenshot_quality_spin.value()
        self.config.idle_threshold = self._idle_threshold_spin.value() * 60
        self.config.minimize_to_tray = self._minimize_to_tray_check.isChecked()
        self.config.auto_start_enabled = self._auto_start_check.isChecked()
        self.config.start_minimized = self._start_minimized_check.isChecked()

        # Billing settings
        self.config.freelancer_name = self._freelancer_name_edit.text().strip()
        self.config.freelancer_email = self._freelancer_email_edit.text().strip()
        self.config.freelancer_address = self._freelancer_address_edit.toPlainText().strip()
        self.config.payment_details = self._payment_details_edit.toPlainText().strip()

        # KPI settings
        self.config.show_kpi_earnings = self._show_kpi_earnings_check.isChecked()
        self.config.show_kpi_targets = self._show_kpi_targets_check.isChecked()
        self.config.daily_target_hours = self._daily_target_spin.value()
        self.config.weekly_target_hours = self._weekly_target_spin.value()

        self.accept()

    def is_auto_start_changed(self) -> bool:
        """Check if auto-start setting was changed."""
        return self._auto_start_check.isChecked() != self.config.auto_start_enabled
