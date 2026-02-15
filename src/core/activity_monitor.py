"""Activity monitor for tracking mouse and keyboard input."""

import threading
import time
from datetime import datetime
from typing import Optional

from PySide6.QtCore import QObject, QTimer, Signal

try:
    from pynput import mouse, keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class ActivityMonitor(QObject):
    """
    Monitors mouse and keyboard activity to calculate activity percentage.

    Activity is measured in intervals (default 60 seconds).
    If any input occurs within a second, that second counts as "active".
    Activity percentage = (active seconds / interval seconds) * 100
    """

    # Signals
    activity_updated = Signal(float)  # Emits activity percentage (0-100)
    idle_detected = Signal(int)       # Emits seconds of continuous idle

    def __init__(self, sample_interval: int = 60, parent=None):
        super().__init__(parent)
        self._sample_interval = sample_interval  # Interval for calculating percentage
        self._is_running = False
        self._last_activity_time: Optional[datetime] = None
        self._active_seconds_in_interval = 0
        self._interval_start_time: Optional[datetime] = None
        self._continuous_idle_seconds = 0

        # For tracking activity within each second
        self._current_second_active = False
        self._last_second_check = 0

        # Listeners (will be created when starting)
        self._mouse_listener: Optional[mouse.Listener] = None
        self._keyboard_listener: Optional[keyboard.Listener] = None

        # Timer for periodic checks
        self._check_timer = QTimer(self)
        self._check_timer.setInterval(1000)  # Check every second
        self._check_timer.timeout.connect(self._on_check_timer)

    @property
    def is_running(self) -> bool:
        """Check if monitoring is active."""
        return self._is_running

    @property
    def last_activity_time(self) -> Optional[datetime]:
        """Get the time of last detected activity."""
        return self._last_activity_time

    @property
    def continuous_idle_seconds(self) -> int:
        """Get seconds since last activity."""
        return self._continuous_idle_seconds

    def start(self):
        """Start monitoring activity."""
        if self._is_running or not PYNPUT_AVAILABLE:
            return

        self._is_running = True
        self._last_activity_time = datetime.now()
        self._interval_start_time = datetime.now()
        self._active_seconds_in_interval = 0
        self._continuous_idle_seconds = 0
        self._current_second_active = False
        self._last_second_check = int(time.time())

        # Start mouse listener
        self._mouse_listener = mouse.Listener(
            on_move=self._on_mouse_activity,
            on_click=self._on_mouse_activity,
            on_scroll=self._on_mouse_activity
        )
        self._mouse_listener.start()

        # Start keyboard listener
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_keyboard_activity,
            on_release=self._on_keyboard_activity
        )
        self._keyboard_listener.start()

        # Start check timer
        self._check_timer.start()

    def stop(self):
        """Stop monitoring activity."""
        if not self._is_running:
            return

        self._is_running = False
        self._check_timer.stop()

        # Stop listeners with timeout to prevent hanging
        if self._mouse_listener:
            try:
                self._mouse_listener.stop()
                # Give it a moment to stop
                if self._mouse_listener.is_alive():
                    self._mouse_listener.join(timeout=0.5)
            except Exception:
                pass
            self._mouse_listener = None

        if self._keyboard_listener:
            try:
                self._keyboard_listener.stop()
                if self._keyboard_listener.is_alive():
                    self._keyboard_listener.join(timeout=0.5)
            except Exception:
                pass
            self._keyboard_listener = None

    def reset_interval(self):
        """Reset the current measurement interval."""
        self._interval_start_time = datetime.now()
        self._active_seconds_in_interval = 0
        self._current_second_active = False
        self._last_second_check = int(time.time())

    def _on_mouse_activity(self, *args):
        """Called on any mouse activity."""
        self._register_activity()

    def _on_keyboard_activity(self, *args):
        """Called on any keyboard activity."""
        self._register_activity()

    def _register_activity(self):
        """Register that activity occurred."""
        self._last_activity_time = datetime.now()
        self._current_second_active = True
        self._continuous_idle_seconds = 0

    def _on_check_timer(self):
        """Called every second to update activity tracking."""
        current_second = int(time.time())

        # Check if we've moved to a new second
        if current_second > self._last_second_check:
            # Count active seconds
            if self._current_second_active:
                self._active_seconds_in_interval += 1
            else:
                self._continuous_idle_seconds += 1

            # Reset for next second
            self._current_second_active = False
            self._last_second_check = current_second

        # Check if interval is complete
        if self._interval_start_time:
            elapsed = (datetime.now() - self._interval_start_time).total_seconds()
            if elapsed >= self._sample_interval:
                # Calculate and emit activity percentage
                percentage = (self._active_seconds_in_interval / self._sample_interval) * 100
                self.activity_updated.emit(min(100.0, percentage))

                # Reset interval
                self.reset_interval()

        # Emit idle signal if continuously idle
        if self._continuous_idle_seconds > 0:
            self.idle_detected.emit(self._continuous_idle_seconds)

    def get_current_activity_percentage(self) -> float:
        """Get the current activity percentage for the ongoing interval."""
        if not self._interval_start_time:
            return 0.0

        elapsed = (datetime.now() - self._interval_start_time).total_seconds()
        if elapsed <= 0:
            return 0.0

        return min(100.0, (self._active_seconds_in_interval / elapsed) * 100)


class DummyActivityMonitor(QObject):
    """Fallback activity monitor when pynput is not available."""

    activity_updated = Signal(float)
    idle_detected = Signal(int)

    def __init__(self, sample_interval: int = 60, parent=None):
        super().__init__(parent)
        self._is_running = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def last_activity_time(self) -> Optional[datetime]:
        return datetime.now()

    @property
    def continuous_idle_seconds(self) -> int:
        return 0

    def start(self):
        self._is_running = True

    def stop(self):
        self._is_running = False

    def reset_interval(self):
        pass

    def get_current_activity_percentage(self) -> float:
        return 100.0  # Assume always active


def create_activity_monitor(sample_interval: int = 60, parent=None):
    """Factory function to create the appropriate activity monitor."""
    if PYNPUT_AVAILABLE:
        return ActivityMonitor(sample_interval, parent)
    else:
        return DummyActivityMonitor(sample_interval, parent)
