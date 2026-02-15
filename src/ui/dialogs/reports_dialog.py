"""Reports dialog for viewing and exporting time entries."""

from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QDateEdit, QComboBox, QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox
)
from PySide6.QtCore import QDate, Qt

from ...database.db_manager import DatabaseManager
from ...utils.config import Config
from ...reports.generator import ReportGenerator


class ReportsDialog(QDialog):
    """Dialog for viewing and exporting reports."""

    def __init__(self, db_manager: DatabaseManager, config: Config, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.config = config
        self._report_generator = ReportGenerator(db_manager, config)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Reports")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ccc;
                font-size: 13px;
            }
            QDateEdit, QComboBox {
                padding: 8px;
                font-size: 13px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: white;
            }
            QTableWidget {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                gridline-color: #444;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
            }
            QHeaderView::section {
                background-color: #383838;
                color: #ccc;
                padding: 8px;
                border: none;
                border-right: 1px solid #444;
                border-bottom: 1px solid #444;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Filters row
        filters_layout = QHBoxLayout()

        # Date range
        filters_layout.addWidget(QLabel("From:"))
        self._from_date = QDateEdit()
        self._from_date.setCalendarPopup(True)
        self._from_date.setDate(QDate.currentDate().addDays(-30))
        filters_layout.addWidget(self._from_date)

        filters_layout.addWidget(QLabel("To:"))
        self._to_date = QDateEdit()
        self._to_date.setCalendarPopup(True)
        self._to_date.setDate(QDate.currentDate())
        filters_layout.addWidget(self._to_date)

        # Client filter
        filters_layout.addWidget(QLabel("Client:"))
        self._client_combo = QComboBox()
        self._client_combo.addItem("All Clients", None)
        for client in self.db_manager.get_all_clients():
            self._client_combo.addItem(client.name, client.id)
        filters_layout.addWidget(self._client_combo)

        filters_layout.addStretch()

        # Filter button
        filter_btn = QPushButton("Apply Filter")
        filter_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
        """)
        filter_btn.clicked.connect(self._load_data)
        filters_layout.addWidget(filter_btn)

        layout.addLayout(filters_layout)

        # Summary row
        self._summary_label = QLabel()
        self._summary_label.setStyleSheet("font-size: 14px; color: #00ff88;")
        layout.addWidget(self._summary_label)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels([
            "Date", "Client", "Project", "Task", "Duration", "Activity", "Amount"
        ])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self._table)

        # Buttons row
        buttons_layout = QHBoxLayout()

        export_btn = QPushButton("Export HTML Report")
        export_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        export_btn.clicked.connect(self._export_report)
        buttons_layout.addWidget(export_btn)

        buttons_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #555;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

    def _load_data(self):
        """Load time entries based on current filters."""
        start_date = datetime.combine(
            self._from_date.date().toPython(),
            datetime.min.time()
        )
        end_date = datetime.combine(
            self._to_date.date().toPython(),
            datetime.max.time()
        )
        client_id = self._client_combo.currentData()

        entries = self.db_manager.get_time_entries_by_date_range(
            start_date, end_date, client_id=client_id
        )

        # Clear and populate table
        self._table.setRowCount(0)
        total_seconds = 0
        total_earnings = 0.0

        for entry_detail in entries:
            row = self._table.rowCount()
            self._table.insertRow(row)

            entry = entry_detail.entry

            # Date
            date_str = entry.start_time.strftime("%Y-%m-%d %H:%M") if entry.start_time else ""
            self._table.setItem(row, 0, QTableWidgetItem(date_str))

            # Client
            self._table.setItem(row, 1, QTableWidgetItem(entry_detail.client_name))

            # Project
            self._table.setItem(row, 2, QTableWidgetItem(entry_detail.project_name))

            # Task
            task_text = entry_detail.task_name
            if entry.is_manual:
                task_text += " (manual)"
            self._table.setItem(row, 3, QTableWidgetItem(task_text))

            # Duration
            self._table.setItem(row, 4, QTableWidgetItem(entry.duration_formatted))

            # Activity
            activity_item = QTableWidgetItem(f"{entry.activity_percentage:.0f}%")
            self._table.setItem(row, 5, activity_item)

            # Earnings
            earnings = entry_detail.earnings
            self._table.setItem(row, 6, QTableWidgetItem(f"${earnings:.2f}"))

            total_seconds += entry.duration_seconds
            total_earnings += earnings

        # Update summary
        hours = total_seconds / 3600
        self._summary_label.setText(
            f"Total: {hours:.1f} hours | Earnings: ${total_earnings:.2f} | "
            f"Entries: {len(entries)}"
        )

    def _export_report(self):
        """Export report as HTML file."""
        start_date = datetime.combine(
            self._from_date.date().toPython(),
            datetime.min.time()
        )
        end_date = datetime.combine(
            self._to_date.date().toPython(),
            datetime.max.time()
        )
        client_id = self._client_combo.currentData()

        # Get default filename
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"time_report_{date_str}.html"

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Report",
            default_name,
            "HTML Files (*.html)"
        )

        if filepath:
            try:
                self._report_generator.generate_html_report(
                    filepath, start_date, end_date, client_id
                )
                QMessageBox.information(
                    self, "Report Exported",
                    f"Report saved to:\n{filepath}"
                )
            except Exception as e:
                QMessageBox.warning(
                    self, "Export Error",
                    f"Could not export report: {e}"
                )
