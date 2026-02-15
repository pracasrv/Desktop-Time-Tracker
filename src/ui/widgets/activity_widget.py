"""Activity display widget."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt


class ActivityWidget(QWidget):
    """Widget displaying current activity percentage."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._activity = 0.0

    def _setup_ui(self):
        """Set up the widget UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        # Activity label
        activity_label = QLabel("Activity:")
        activity_label.setStyleSheet("color: #aaa; font-size: 12px;")
        layout.addWidget(activity_label)

        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(16)
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2d2d2d;
            }
            QProgressBar::chunk {
                background-color: #00ff88;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self._progress_bar, 1)

        # Percentage label
        self._percentage_label = QLabel("0%")
        self._percentage_label.setStyleSheet("color: #00ff88; font-size: 12px; font-weight: bold;")
        self._percentage_label.setFixedWidth(45)
        self._percentage_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self._percentage_label)

    def set_activity(self, percentage: float):
        """Set the activity percentage (0-100)."""
        self._activity = max(0, min(100, percentage))
        self._progress_bar.setValue(int(self._activity))
        self._percentage_label.setText(f"{self._activity:.0f}%")

        # Change color based on activity level
        if self._activity >= 70:
            color = "#00ff88"  # Green - good
        elif self._activity >= 40:
            color = "#ffc107"  # Yellow - moderate
        else:
            color = "#dc3545"  # Red - low

        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2d2d2d;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        self._percentage_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold;")

    def reset(self):
        """Reset the activity display."""
        self.set_activity(0)


class StatusWidget(QWidget):
    """Widget displaying tracking status information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._screenshots_enabled = False
        self._screenshot_count = 0
        self._setup_ui()

    def _setup_ui(self):
        """Set up the widget UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        # Status label
        self._status_label = QLabel("Status: Stopped")
        self._status_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self._status_label)

        layout.addStretch()

        # Screenshots status
        self._screenshots_label = QLabel("Screenshots: OFF")
        self._screenshots_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self._screenshots_label)

    def set_tracking_status(self, is_tracking: bool, is_paused: bool = False):
        """Update the tracking status display."""
        if is_paused:
            self._status_label.setText("Status: Paused")
            self._status_label.setStyleSheet("color: #ffc107; font-size: 12px;")
        elif is_tracking:
            self._status_label.setText("Status: Tracking")
            self._status_label.setStyleSheet("color: #00ff88; font-size: 12px;")
        else:
            self._status_label.setText("Status: Stopped")
            self._status_label.setStyleSheet("color: #888; font-size: 12px;")

    def set_screenshots_status(self, enabled: bool):
        """Update the screenshots status display."""
        self._screenshots_enabled = enabled
        self._update_screenshots_label()

    def increment_screenshot_count(self):
        """Increment the screenshot count and update display."""
        self._screenshot_count += 1
        self._update_screenshots_label()

    def reset_screenshot_count(self):
        """Reset the screenshot count to 0."""
        self._screenshot_count = 0
        self._update_screenshots_label()

    def _update_screenshots_label(self):
        """Update the screenshots label with current status and count."""
        if self._screenshots_enabled:
            if self._screenshot_count > 0:
                self._screenshots_label.setText(f"Screenshots: ON ({self._screenshot_count})")
            else:
                self._screenshots_label.setText("Screenshots: ON")
            self._screenshots_label.setStyleSheet("color: #00ff88; font-size: 12px;")
        else:
            self._screenshots_label.setText("Screenshots: OFF")
            self._screenshots_label.setStyleSheet("color: #888; font-size: 12px;")
