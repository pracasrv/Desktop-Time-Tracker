"""System tray integration."""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import Signal, QObject

from ..core.tracker import TrackerState


class SystemTrayIcon(QObject):
    """System tray icon with menu and status updates."""

    # Signals
    show_window_requested = Signal()
    start_requested = Signal()
    pause_requested = Signal()
    stop_requested = Signal()
    quit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tray_icon = QSystemTrayIcon(parent)
        self._current_time = "00:00:00"
        self._state = TrackerState.STOPPED

        self._setup_icon()
        self._setup_menu()

        self._tray_icon.activated.connect(self._on_activated)

    def _setup_icon(self):
        """Create and set the tray icon."""
        self._update_icon()

    def _create_icon(self, color: str = "#888888") -> QIcon:
        """Create a simple clock icon with the given color."""
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw circle
        painter.setPen(QColor(color))
        painter.setBrush(QColor(color))
        painter.drawEllipse(4, 4, 56, 56)

        # Draw "T" for Time Tracker
        painter.setPen(QColor("#ffffff"))
        font = QFont("Arial", 28, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), 0x84, "T")  # AlignCenter

        painter.end()

        return QIcon(pixmap)

    def _update_icon(self):
        """Update the tray icon based on state."""
        if self._state == TrackerState.RUNNING:
            color = "#00ff88"  # Green
        elif self._state == TrackerState.PAUSED:
            color = "#ffc107"  # Yellow
        else:
            color = "#888888"  # Gray

        icon = self._create_icon(color)
        self._tray_icon.setIcon(icon)

    def _setup_menu(self):
        """Set up the tray icon context menu."""
        menu = QMenu()

        # Show window action
        self._show_action = menu.addAction("Show Window")
        self._show_action.triggered.connect(self.show_window_requested.emit)

        menu.addSeparator()

        # Start/Resume action
        self._start_action = menu.addAction("Start")
        self._start_action.triggered.connect(self.start_requested.emit)

        # Pause action
        self._pause_action = menu.addAction("Pause")
        self._pause_action.triggered.connect(self.pause_requested.emit)
        self._pause_action.setEnabled(False)

        # Stop action
        self._stop_action = menu.addAction("Stop")
        self._stop_action.triggered.connect(self.stop_requested.emit)
        self._stop_action.setEnabled(False)

        menu.addSeparator()

        # Quit action
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_requested.emit)

        self._tray_icon.setContextMenu(menu)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window_requested.emit()

    def show(self):
        """Show the tray icon."""
        self._tray_icon.show()

    def hide(self):
        """Hide the tray icon."""
        self._tray_icon.hide()

    def set_state(self, state: TrackerState):
        """Update menu items based on tracker state."""
        self._state = state
        self._update_icon()

        if state == TrackerState.STOPPED:
            self._start_action.setText("Start")
            self._start_action.setEnabled(True)
            self._pause_action.setEnabled(False)
            self._stop_action.setEnabled(False)
        elif state == TrackerState.RUNNING:
            self._start_action.setText("Start")
            self._start_action.setEnabled(False)
            self._pause_action.setEnabled(True)
            self._stop_action.setEnabled(True)
        elif state == TrackerState.PAUSED:
            self._start_action.setText("Resume")
            self._start_action.setEnabled(True)
            self._pause_action.setEnabled(False)
            self._stop_action.setEnabled(True)

    def update_time(self, time_str: str):
        """Update the tooltip with current time."""
        self._current_time = time_str
        self._update_tooltip()

    def _update_tooltip(self):
        """Update the tray icon tooltip."""
        status = "Stopped"
        if self._state == TrackerState.RUNNING:
            status = "Tracking"
        elif self._state == TrackerState.PAUSED:
            status = "Paused"

        tooltip = f"Time Tracker - {status}\n{self._current_time}"
        self._tray_icon.setToolTip(tooltip)

    def show_message(self, title: str, message: str, icon_type=QSystemTrayIcon.MessageIcon.Information):
        """Show a notification message."""
        self._tray_icon.showMessage(title, message, icon_type, 3000)
