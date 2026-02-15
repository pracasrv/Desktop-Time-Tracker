"""Screenshot capture functionality."""

import ctypes
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QTimer, Signal

try:
    import mss
    import mss.tools
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ScreenshotCapture(QObject):
    """Captures screenshots at regular intervals."""

    # Signals
    screenshot_taken = Signal(str, float)  # filepath, activity_percentage
    capture_error = Signal(str)            # error message
    screenshot_skipped = Signal(str)       # reason for skipping

    # App window title to skip capturing
    APP_WINDOW_TITLE = "Desktop Time Tracker"
    # Delay before first screenshot (seconds)
    STARTUP_DELAY = 60
    # Retry delay when screenshot is skipped (seconds)
    RETRY_DELAY = 120  # 2 minutes

    def __init__(
        self,
        screenshots_dir: Path,
        interval_seconds: int = 600,
        quality: int = 70,
        parent=None
    ):
        super().__init__(parent)
        self._screenshots_dir = screenshots_dir
        self._interval_seconds = interval_seconds
        self._quality = quality
        self._is_running = False
        self._current_activity = 0.0
        self._start_time: Optional[datetime] = None

        # Timer for capturing screenshots
        self._capture_timer = QTimer(self)
        self._capture_timer.timeout.connect(self._on_capture_timer)

    @property
    def is_running(self) -> bool:
        """Check if capture is active."""
        return self._is_running

    @property
    def interval_seconds(self) -> int:
        """Get capture interval in seconds."""
        return self._interval_seconds

    @interval_seconds.setter
    def interval_seconds(self, value: int):
        """Set capture interval."""
        self._interval_seconds = max(60, value)  # Minimum 1 minute
        if self._is_running:
            self._capture_timer.setInterval(self._interval_seconds * 1000)

    @property
    def quality(self) -> int:
        """Get JPEG quality."""
        return self._quality

    @quality.setter
    def quality(self, value: int):
        """Set JPEG quality (1-100)."""
        self._quality = max(1, min(100, value))

    def set_activity_percentage(self, percentage: float):
        """Update current activity percentage for screenshot metadata."""
        self._current_activity = percentage

    def start(self):
        """Start capturing screenshots."""
        if self._is_running:
            return

        self._is_running = True
        self._start_time = datetime.now()
        self._capture_timer.setInterval(self._interval_seconds * 1000)
        self._capture_timer.start()
        # Don't take initial screenshot - wait for startup delay

    def stop(self):
        """Stop capturing screenshots."""
        if not self._is_running:
            return

        self._is_running = False
        self._capture_timer.stop()

    def _get_active_window_title(self) -> str:
        """Get the title of the currently active window."""
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            length = user32.GetWindowTextLengthW(hwnd) + 1
            buffer = ctypes.create_unicode_buffer(length)
            user32.GetWindowTextW(hwnd, buffer, length)
            return buffer.value
        except Exception:
            return ""

    def _should_skip_capture(self) -> Optional[str]:
        """Check if screenshot should be skipped. Returns reason or None."""
        # Check startup delay
        if self._start_time:
            elapsed = (datetime.now() - self._start_time).total_seconds()
            if elapsed < self.STARTUP_DELAY:
                return f"startup delay ({int(self.STARTUP_DELAY - elapsed)}s remaining)"

        # Check if our app is the active window
        active_title = self._get_active_window_title()
        if self.APP_WINDOW_TITLE in active_title:
            return "timer app is active window"

        return None

    def capture_now(self) -> Optional[str]:
        """Capture a screenshot immediately and return the filepath."""
        if not MSS_AVAILABLE:
            self.capture_error.emit("mss library not available")
            return None

        # Check if we should skip this capture
        skip_reason = self._should_skip_capture()
        if skip_reason:
            self.screenshot_skipped.emit(skip_reason)
            return None

        try:
            # Create date-based subdirectory
            today = datetime.now().strftime('%Y-%m-%d')
            save_dir = self._screenshots_dir / today
            save_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename with timestamp and activity
            timestamp = datetime.now().strftime('%H-%M-%S')
            activity_str = f"{self._current_activity:.0f}"
            filename = f"{timestamp}_act{activity_str}.jpg"
            filepath = save_dir / filename

            # Capture the active monitor
            with mss.mss() as sct:
                # Get primary monitor (index 1, as 0 is "all monitors combined")
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)

                # Convert to PIL Image for JPEG compression
                if PIL_AVAILABLE:
                    img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
                    img.save(str(filepath), 'JPEG', quality=self._quality)
                else:
                    # Fallback to PNG if PIL not available
                    filepath = filepath.with_suffix('.png')
                    mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(filepath))

            self.screenshot_taken.emit(str(filepath), self._current_activity)
            return str(filepath)

        except Exception as e:
            self.capture_error.emit(str(e))
            return None

    def _on_capture_timer(self):
        """Called when capture interval elapses."""
        result = self.capture_now()

        # If screenshot was skipped, retry after a shorter delay
        if result is None and self._is_running:
            # Stop the regular timer temporarily
            self._capture_timer.stop()
            # Schedule a single-shot retry after RETRY_DELAY
            QTimer.singleShot(self.RETRY_DELAY * 1000, self._on_retry_after_skip)

    def _on_retry_after_skip(self):
        """Retry screenshot capture after it was skipped."""
        if self._is_running:
            self.capture_now()
            # Restart the regular interval timer
            self._capture_timer.start()

    def get_screenshots_size(self) -> int:
        """Get total size of all screenshots in bytes."""
        total_size = 0
        if self._screenshots_dir.exists():
            for file in self._screenshots_dir.rglob('*'):
                if file.is_file():
                    total_size += file.stat().st_size
        return total_size

    def get_screenshots_size_formatted(self) -> str:
        """Get formatted size of all screenshots."""
        size = self.get_screenshots_size()
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
