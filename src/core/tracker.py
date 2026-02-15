"""Time tracking engine with state management."""

from datetime import datetime
from enum import Enum, auto
from typing import Optional

from PySide6.QtCore import QObject, QTimer, Signal

from ..database.models import TimeEntry
from ..database.db_manager import DatabaseManager


class TrackerState(Enum):
    """Possible states for the time tracker."""
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()


class TimeTracker(QObject):
    """Manages time tracking state and duration calculation."""

    # Signals
    state_changed = Signal(TrackerState)
    time_updated = Signal(int)  # Emits duration in seconds
    entry_saved = Signal(int)   # Emits entry ID when saved

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self._state = TrackerState.STOPPED
        self._current_entry: Optional[TimeEntry] = None
        self._start_time: Optional[datetime] = None
        self._pause_time: Optional[datetime] = None
        self._paused_duration: int = 0  # Accumulated paused time in seconds
        self._elapsed_seconds: int = 0
        self._activity_samples: list = []

        # Timer for updating elapsed time display
        self._timer = QTimer(self)
        self._timer.setInterval(1000)  # Update every second
        self._timer.timeout.connect(self._on_timer_tick)

        # Check for active entry on startup (crash recovery)
        self._recover_active_entry()

    def _recover_active_entry(self):
        """Recover any active time entry from previous session."""
        active_entry = self.db_manager.get_active_time_entry()
        if active_entry:
            self._current_entry = active_entry
            self._start_time = active_entry.start_time
            self._elapsed_seconds = int((datetime.now() - self._start_time).total_seconds())
            self._state = TrackerState.RUNNING
            self._timer.start()
            self.state_changed.emit(self._state)
            self.time_updated.emit(self._elapsed_seconds)

    @property
    def state(self) -> TrackerState:
        """Get current tracker state."""
        return self._state

    @property
    def is_running(self) -> bool:
        """Check if tracker is running."""
        return self._state == TrackerState.RUNNING

    @property
    def is_paused(self) -> bool:
        """Check if tracker is paused."""
        return self._state == TrackerState.PAUSED

    @property
    def is_stopped(self) -> bool:
        """Check if tracker is stopped."""
        return self._state == TrackerState.STOPPED

    @property
    def elapsed_seconds(self) -> int:
        """Get elapsed time in seconds."""
        return self._elapsed_seconds

    @property
    def current_entry(self) -> Optional[TimeEntry]:
        """Get the current time entry."""
        return self._current_entry

    @property
    def current_task_id(self) -> Optional[int]:
        """Get the task ID of current entry."""
        return self._current_entry.task_id if self._current_entry else None

    def start(self, task_id: int) -> bool:
        """Start tracking time for a task."""
        if self._state == TrackerState.RUNNING:
            return False

        if self._state == TrackerState.PAUSED:
            # Resume from pause
            self._paused_duration += int((datetime.now() - self._pause_time).total_seconds())
            self._pause_time = None
            self._state = TrackerState.RUNNING
            self._timer.start()
            self.state_changed.emit(self._state)
            return True

        # Start fresh
        self._start_time = datetime.now()
        self._pause_time = None
        self._paused_duration = 0
        self._elapsed_seconds = 0
        self._activity_samples = []

        # Create new time entry
        self._current_entry = TimeEntry(
            task_id=task_id,
            start_time=self._start_time
        )
        entry_id = self.db_manager.add_time_entry(self._current_entry)
        self._current_entry.id = entry_id

        self._state = TrackerState.RUNNING
        self._timer.start()
        self.state_changed.emit(self._state)
        self.time_updated.emit(self._elapsed_seconds)

        return True

    def pause(self) -> bool:
        """Pause the tracker."""
        if self._state != TrackerState.RUNNING:
            return False

        self._pause_time = datetime.now()
        self._state = TrackerState.PAUSED
        self._timer.stop()
        self.state_changed.emit(self._state)

        return True

    def resume(self) -> bool:
        """Resume from paused state."""
        if self._state != TrackerState.PAUSED:
            return False

        self._paused_duration += int((datetime.now() - self._pause_time).total_seconds())
        self._pause_time = None
        self._state = TrackerState.RUNNING
        self._timer.start()
        self.state_changed.emit(self._state)

        return True

    def stop(self, notes: str = "") -> Optional[int]:
        """Stop tracking and save the entry."""
        if self._state == TrackerState.STOPPED:
            return None

        self._timer.stop()
        end_time = datetime.now()

        # Calculate final duration (excluding paused time)
        if self._pause_time:
            self._paused_duration += int((end_time - self._pause_time).total_seconds())

        total_seconds = int((end_time - self._start_time).total_seconds())
        active_seconds = total_seconds - self._paused_duration

        # Calculate average activity
        avg_activity = 0.0
        if self._activity_samples:
            avg_activity = sum(self._activity_samples) / len(self._activity_samples)

        # Update the entry
        self._current_entry.end_time = end_time
        self._current_entry.duration_seconds = max(0, active_seconds)
        self._current_entry.activity_percentage = avg_activity
        self._current_entry.notes = notes

        self.db_manager.update_time_entry(self._current_entry)
        entry_id = self._current_entry.id

        # Reset state
        self._state = TrackerState.STOPPED
        self._start_time = None
        self._pause_time = None
        self._paused_duration = 0
        self._elapsed_seconds = 0
        self._activity_samples = []

        old_entry = self._current_entry
        self._current_entry = None

        self.state_changed.emit(self._state)
        self.entry_saved.emit(entry_id)

        return entry_id

    def discard(self):
        """Discard the current entry without saving."""
        if self._state == TrackerState.STOPPED:
            return

        self._timer.stop()

        # Delete the entry from database
        if self._current_entry and self._current_entry.id:
            self.db_manager.delete_time_entry(self._current_entry.id)

        # Reset state
        self._state = TrackerState.STOPPED
        self._current_entry = None
        self._start_time = None
        self._pause_time = None
        self._paused_duration = 0
        self._elapsed_seconds = 0
        self._activity_samples = []

        self.state_changed.emit(self._state)

    def add_activity_sample(self, percentage: float):
        """Add an activity percentage sample."""
        self._activity_samples.append(percentage)

    def _on_timer_tick(self):
        """Called every second to update elapsed time."""
        if self._start_time:
            total_seconds = int((datetime.now() - self._start_time).total_seconds())
            self._elapsed_seconds = total_seconds - self._paused_duration
            self.time_updated.emit(self._elapsed_seconds)

    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format seconds as HH:MM:SS."""
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
