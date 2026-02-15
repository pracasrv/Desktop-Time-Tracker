"""Idle detection for auto-pause functionality."""

from PySide6.QtCore import QObject, Signal


class IdleDetector(QObject):
    """
    Detects when the user becomes idle and triggers auto-pause.

    Works in conjunction with ActivityMonitor to track continuous idle time.
    """

    # Signals
    idle_threshold_reached = Signal()  # Emitted when idle time exceeds threshold
    activity_resumed = Signal()        # Emitted when user becomes active again

    def __init__(self, threshold_seconds: int = 300, parent=None):
        super().__init__(parent)
        self._threshold_seconds = threshold_seconds
        self._is_enabled = True
        self._is_idle = False
        self._was_notified = False

    @property
    def threshold_seconds(self) -> int:
        """Get idle threshold in seconds."""
        return self._threshold_seconds

    @threshold_seconds.setter
    def threshold_seconds(self, value: int):
        """Set idle threshold in seconds."""
        self._threshold_seconds = max(60, value)  # Minimum 1 minute

    @property
    def is_enabled(self) -> bool:
        """Check if idle detection is enabled."""
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, value: bool):
        """Enable or disable idle detection."""
        self._is_enabled = value
        if not value:
            self._is_idle = False
            self._was_notified = False

    @property
    def is_idle(self) -> bool:
        """Check if currently in idle state."""
        return self._is_idle

    def on_idle_detected(self, idle_seconds: int):
        """
        Called by activity monitor when idle time changes.

        Args:
            idle_seconds: Number of continuous idle seconds
        """
        if not self._is_enabled:
            return

        if idle_seconds >= self._threshold_seconds:
            if not self._was_notified:
                self._is_idle = True
                self._was_notified = True
                self.idle_threshold_reached.emit()
        else:
            if self._was_notified and idle_seconds == 0:
                # User resumed activity
                self._is_idle = False
                self._was_notified = False
                self.activity_resumed.emit()

    def reset(self):
        """Reset idle state."""
        self._is_idle = False
        self._was_notified = False
