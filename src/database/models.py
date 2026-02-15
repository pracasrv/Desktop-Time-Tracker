"""Data models for the Time Tracker application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Client:
    """Represents a client in the time tracker."""
    id: Optional[int] = None
    name: str = ""
    hourly_rate: float = 0.0
    email: str = ""
    phone: str = ""
    address: str = ""
    notes: str = ""
    created_at: Optional[datetime] = None
    is_active: bool = True

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class Project:
    """Represents a project belonging to a client."""
    id: Optional[int] = None
    client_id: int = 0
    name: str = ""
    hourly_rate: Optional[float] = None  # Override client rate if set
    created_at: Optional[datetime] = None
    is_active: bool = True

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class Task:
    """Represents a task belonging to a project."""
    id: Optional[int] = None
    project_id: int = 0
    name: str = ""
    notes: str = ""  # Personal notes for freelancer reference (not in reports)
    created_at: Optional[datetime] = None
    is_active: bool = True
    is_completed: bool = False
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class TimeEntry:
    """Represents a time tracking entry."""
    id: Optional[int] = None
    task_id: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: int = 0
    activity_percentage: float = 0.0
    notes: str = ""
    is_manual: bool = False
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    @property
    def duration_formatted(self) -> str:
        """Return duration as HH:MM:SS string."""
        hours, remainder = divmod(self.duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @property
    def duration_hours(self) -> float:
        """Return duration in decimal hours."""
        return self.duration_seconds / 3600


@dataclass
class Screenshot:
    """Represents a screenshot taken during tracking."""
    id: Optional[int] = None
    time_entry_id: int = 0
    filepath: str = ""
    captured_at: Optional[datetime] = None
    activity_percentage: float = 0.0

    def __post_init__(self):
        if self.captured_at is None:
            self.captured_at = datetime.now()


@dataclass
class TimeEntryWithDetails:
    """Time entry with related client, project, and task info for reporting."""
    entry: TimeEntry
    task_name: str = ""
    project_name: str = ""
    client_name: str = ""
    hourly_rate: float = 0.0
    screenshots: list = field(default_factory=list)

    @property
    def earnings(self) -> float:
        """Calculate earnings for this entry."""
        return self.entry.duration_hours * self.hourly_rate
