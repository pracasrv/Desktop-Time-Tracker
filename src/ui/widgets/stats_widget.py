"""KPI stats widget showing daily and weekly time totals."""

from datetime import datetime, timedelta
from typing import Optional

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

from ...database.db_manager import DatabaseManager
from ...utils.config import Config


class StatsWidget(QWidget):
    """Widget displaying daily and weekly time totals."""

    def __init__(self, db_manager: DatabaseManager, config: Optional[Config] = None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.config = config
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Set up the widget UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        card_style = """
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px;
            }
        """

        # Today's total
        today_card = QFrame()
        today_card.setStyleSheet(card_style)
        today_card.setMinimumHeight(80)  # Ensure enough height for all labels
        today_layout = QVBoxLayout(today_card)
        today_layout.setContentsMargins(10, 6, 10, 6)
        today_layout.setSpacing(2)

        today_title = QLabel("Today")
        today_title.setStyleSheet("color: #888; font-size: 10px; font-weight: bold;")
        today_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        today_layout.addWidget(today_title)

        self._today_value = QLabel("0:00")
        self._today_value.setStyleSheet("color: #00ff88; font-size: 16px; font-weight: bold;")
        self._today_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        today_layout.addWidget(self._today_value)

        # Today's earnings (hidden by default)
        self._today_earnings = QLabel("")
        self._today_earnings.setStyleSheet("color: #28a745; font-size: 11px;")
        self._today_earnings.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._today_earnings.hide()
        today_layout.addWidget(self._today_earnings)

        # Today's target progress (hidden by default)
        self._today_target = QLabel("")
        self._today_target.setStyleSheet("color: #888; font-size: 10px;")
        self._today_target.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._today_target.hide()
        today_layout.addWidget(self._today_target)

        layout.addWidget(today_card)

        # This week's total
        week_card = QFrame()
        week_card.setStyleSheet(card_style)
        week_card.setMinimumHeight(80)  # Ensure enough height for all labels
        week_layout = QVBoxLayout(week_card)
        week_layout.setContentsMargins(10, 6, 10, 6)
        week_layout.setSpacing(2)

        week_title = QLabel("This Week")
        week_title.setStyleSheet("color: #888; font-size: 10px; font-weight: bold;")
        week_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        week_layout.addWidget(week_title)

        self._week_value = QLabel("0:00")
        self._week_value.setStyleSheet("color: #0078d4; font-size: 16px; font-weight: bold;")
        self._week_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        week_layout.addWidget(self._week_value)

        # Week's earnings (hidden by default)
        self._week_earnings = QLabel("")
        self._week_earnings.setStyleSheet("color: #28a745; font-size: 11px;")
        self._week_earnings.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._week_earnings.hide()
        week_layout.addWidget(self._week_earnings)

        # Week's target progress (hidden by default)
        self._week_target = QLabel("")
        self._week_target.setStyleSheet("color: #888; font-size: 10px;")
        self._week_target.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._week_target.hide()
        week_layout.addWidget(self._week_target)

        layout.addWidget(week_card)

    def refresh(self):
        """Refresh the stats from the database."""
        today = datetime.now().date()

        # Get start of week (Monday)
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)

        # Query today's total
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        # Query week's total
        week_start_dt = datetime.combine(week_start, datetime.min.time())
        week_end_dt = datetime.combine(today, datetime.max.time())

        conn = self.db_manager._get_connection()
        cursor = conn.cursor()

        # Today's total with earnings
        cursor.execute(
            '''SELECT COALESCE(SUM(te.duration_seconds), 0),
                      COALESCE(SUM(te.duration_seconds * COALESCE(p.hourly_rate, c.hourly_rate, 0) / 3600.0), 0)
               FROM time_entries te
               JOIN tasks t ON te.task_id = t.id
               JOIN projects p ON t.project_id = p.id
               JOIN clients c ON p.client_id = c.id
               WHERE te.start_time >= ? AND te.start_time <= ?''',
            (today_start.isoformat(), today_end.isoformat())
        )
        row = cursor.fetchone()
        today_seconds = row[0] if row else 0
        today_earnings = row[1] if row else 0.0

        # Week's total with earnings
        cursor.execute(
            '''SELECT COALESCE(SUM(te.duration_seconds), 0),
                      COALESCE(SUM(te.duration_seconds * COALESCE(p.hourly_rate, c.hourly_rate, 0) / 3600.0), 0)
               FROM time_entries te
               JOIN tasks t ON te.task_id = t.id
               JOIN projects p ON t.project_id = p.id
               JOIN clients c ON p.client_id = c.id
               WHERE te.start_time >= ? AND te.start_time <= ?''',
            (week_start_dt.isoformat(), week_end_dt.isoformat())
        )
        row = cursor.fetchone()
        week_seconds = row[0] if row else 0
        week_earnings = row[1] if row else 0.0

        conn.close()

        # Update time labels
        self._today_value.setText(self._format_hours(today_seconds))
        self._week_value.setText(self._format_hours(week_seconds))

        # Update earnings labels (if enabled)
        show_earnings = self.config.show_kpi_earnings if self.config else False
        if show_earnings:
            self._today_earnings.setText(f"${today_earnings:.2f}")
            self._today_earnings.show()
            self._week_earnings.setText(f"${week_earnings:.2f}")
            self._week_earnings.show()
        else:
            self._today_earnings.hide()
            self._week_earnings.hide()

        # Update target labels (if enabled)
        show_targets = self.config.show_kpi_targets if self.config else False
        if show_targets:
            daily_target = self.config.daily_target_hours if self.config else 8.0
            weekly_target = self.config.weekly_target_hours if self.config else 40.0

            today_hours = today_seconds / 3600.0
            week_hours = week_seconds / 3600.0

            today_pct = min(100, (today_hours / daily_target) * 100) if daily_target > 0 else 0
            week_pct = min(100, (week_hours / weekly_target) * 100) if weekly_target > 0 else 0

            self._today_target.setText(f"{today_pct:.0f}% of {daily_target:.1f}h")
            self._today_target.show()
            self._week_target.setText(f"{week_pct:.0f}% of {weekly_target:.1f}h")
            self._week_target.show()
        else:
            self._today_target.hide()
            self._week_target.hide()

    def _format_hours(self, seconds: int) -> str:
        """Format seconds as H:MM."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}:{minutes:02d}"
