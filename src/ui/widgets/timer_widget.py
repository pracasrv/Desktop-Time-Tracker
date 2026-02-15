"""Timer widget with start/stop/pause controls."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ...core.tracker import TrackerState


class TimerWidget(QWidget):
    """Widget displaying timer and control buttons."""

    # Signals
    start_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._state = TrackerState.STOPPED

    def _setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # Timer display frame
        timer_frame = QFrame()
        timer_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        timer_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        timer_layout = QVBoxLayout(timer_frame)
        timer_layout.setContentsMargins(5, 5, 5, 5)
        timer_layout.setSpacing(2)

        # Timer display
        self._time_label = QLabel("00:00:00")
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._time_label.setStyleSheet("""
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 36px;
            font-weight: bold;
            color: #00ff88;
        """)
        timer_layout.addWidget(self._time_label)

        # Status label
        self._status_label = QLabel("Ready")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet("color: #888; font-size: 12px;")
        timer_layout.addWidget(self._status_label)

        layout.addWidget(timer_frame)

        # Control buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(6)

        button_style = """
            QPushButton {
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 70px;
            }
            QPushButton:disabled {
                background-color: #444;
                color: #888;
            }
        """

        # Start button
        self._start_btn = QPushButton("START")
        self._start_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #28a745;
                color: white;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self._start_btn.clicked.connect(self.start_clicked.emit)
        buttons_layout.addWidget(self._start_btn)

        # Pause button
        self._pause_btn = QPushButton("PAUSE")
        self._pause_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #ffc107;
                color: black;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        self._pause_btn.clicked.connect(self.pause_clicked.emit)
        self._pause_btn.setEnabled(False)
        buttons_layout.addWidget(self._pause_btn)

        # Stop button
        self._stop_btn = QPushButton("STOP")
        self._stop_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #dc3545;
                color: white;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self._stop_btn.clicked.connect(self.stop_clicked.emit)
        self._stop_btn.setEnabled(False)
        buttons_layout.addWidget(self._stop_btn)

        layout.addLayout(buttons_layout)

    def update_time(self, seconds: int):
        """Update the displayed time."""
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        self._time_label.setText(f"{hours:02d}:{minutes:02d}:{secs:02d}")

    def set_state(self, state: TrackerState):
        """Update button states based on tracker state."""
        self._state = state

        timer_font_style = "font-family: 'Segoe UI', 'Arial', sans-serif; font-size: 36px; font-weight: bold;"

        if state == TrackerState.STOPPED:
            self._start_btn.setEnabled(True)
            self._start_btn.setText("START")
            self._pause_btn.setEnabled(False)
            self._stop_btn.setEnabled(False)
            self._status_label.setText("Ready")
            self._status_label.setStyleSheet("color: #888; font-size: 12px;")
            self._time_label.setStyleSheet(timer_font_style + "color: #888;")

        elif state == TrackerState.RUNNING:
            self._start_btn.setEnabled(False)
            self._start_btn.setText("START")
            self._pause_btn.setEnabled(True)
            self._pause_btn.setText("PAUSE")
            self._stop_btn.setEnabled(True)
            self._status_label.setText("Tracking...")
            self._status_label.setStyleSheet("color: #00ff88; font-size: 12px;")
            self._time_label.setStyleSheet(timer_font_style + "color: #00ff88;")

        elif state == TrackerState.PAUSED:
            self._start_btn.setEnabled(True)
            self._start_btn.setText("RESUME")
            self._pause_btn.setEnabled(False)
            self._stop_btn.setEnabled(True)
            self._status_label.setText("Paused")
            self._status_label.setStyleSheet("color: #ffc107; font-size: 12px;")
            self._time_label.setStyleSheet(timer_font_style + "color: #ffc107;")

    def reset(self):
        """Reset the timer display."""
        self._time_label.setText("00:00:00")
        self.set_state(TrackerState.STOPPED)
