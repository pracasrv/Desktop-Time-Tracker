# Desktop Time Tracker - Architecture Documentation

## Overview

Desktop Time Tracker is a Windows desktop application built with Python and PySide6 (Qt for Python). It helps freelancers track time spent on client projects, capture periodic screenshots as proof of work, monitor activity levels, and generate HTML reports.

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| UI Framework | PySide6 (Qt 6) | Cross-platform GUI, system tray, dialogs |
| Database | SQLite3 | Local data storage |
| Screenshots | mss | Fast screen capture |
| Activity Monitoring | pynput | Mouse/keyboard input detection |
| Image Processing | Pillow | JPEG compression for screenshots |
| Report Generation | Jinja2 | HTML template rendering |

## Project Structure

```
Desktop Time Tracker/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md         # This file
│   ├── INSTALLATION.md         # Installation guide
│   └── USER_GUIDE.md           # User guide
├── data/                       # Runtime data (created automatically)
│   ├── timetracker.db          # SQLite database
│   ├── config.json             # User settings
│   └── screenshots/            # Screenshot storage
│       └── YYYY-MM-DD/         # Organized by date
├── src/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py           # Data models (dataclasses)
│   │   └── db_manager.py       # SQLite operations
│   ├── core/
│   │   ├── __init__.py
│   │   ├── tracker.py          # Time tracking state machine
│   │   ├── activity_monitor.py # Mouse/keyboard monitoring
│   │   ├── screenshot.py       # Screenshot capture
│   │   └── idle_detector.py    # Idle detection & auto-pause
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main application window
│   │   ├── system_tray.py      # System tray icon & menu
│   │   ├── dialogs/
│   │   │   ├── __init__.py
│   │   │   ├── client_dialog.py
│   │   │   ├── project_dialog.py
│   │   │   ├── task_dialog.py
│   │   │   ├── manual_entry.py
│   │   │   ├── settings_dialog.py
│   │   │   └── reports_dialog.py
│   │   └── widgets/
│   │       ├── __init__.py
│   │       ├── timer_widget.py     # Timer display & controls
│   │       ├── selector_widget.py  # Client/Project dropdowns
│   │       ├── task_panel.py       # Task list panel
│   │       ├── task_list_widget.py # Task rows with play buttons
│   │       ├── activity_widget.py  # Activity bar & status
│   │       └── stats_widget.py     # Daily/weekly KPI cards
│   ├── reports/
│   │   ├── __init__.py
│   │   └── generator.py        # HTML report generation
│   └── utils/
│       ├── __init__.py
│       ├── config.py           # Configuration management
│       └── startup.py          # Windows auto-start registry
└── venv/                       # Virtual environment
```

## Core Components

### 1. Database Layer (`src/database/`)

#### Models (`models.py`)
Defines dataclasses for all entities:
- `Client` - Client with hourly rate and contact info
- `Project` - Project belonging to a client
- `Task` - Task within a project (with notes)
- `TimeEntry` - Individual tracking session
- `Screenshot` - Screenshot captured during tracking
- `TimeEntryWithDetails` - Joined view for reports

#### Database Manager (`db_manager.py`)
- SQLite connection management
- CRUD operations for all entities
- Automatic schema migrations
- Reporting queries with joins

### 2. Core Tracking (`src/core/`)

#### Time Tracker (`tracker.py`)
State machine with states:
- `STOPPED` - Not tracking
- `RUNNING` - Actively tracking
- `PAUSED` - Tracking paused

Emits Qt signals for UI updates:
- `state_changed(TrackerState)`
- `time_updated(int)` - elapsed seconds
- `entry_saved(TimeEntry)`

#### Activity Monitor (`activity_monitor.py`)
- Uses `pynput` to listen for mouse/keyboard events
- Calculates activity percentage per interval
- Thread-safe with Qt signal integration

#### Screenshot Capture (`screenshot.py`)
- Captures primary monitor using `mss`
- Saves as JPEG with configurable quality
- 60-second delay after start (avoids capturing timer)
- Skips capture if timer app is active window
- Emits signals: `screenshot_taken`, `screenshot_skipped`

#### Idle Detector (`idle_detector.py`)
- Monitors activity monitor output
- Auto-pauses after configurable idle threshold
- Shows notification when pausing

### 3. User Interface (`src/ui/`)

#### Main Window (`main_window.py`)
- Horizontal layout: Controls panel + Task panel
- Coordinates all components
- Handles signal connections
- Persists last selection (client/project)

#### System Tray (`system_tray.py`)
- Shows tracking status in tooltip
- Quick actions: Start/Stop, Pause, Show window
- App continues running when minimized

#### Widgets
- `TimerWidget` - Large timer display with Start/Pause/Stop buttons
- `SelectorWidget` - Client/Project dropdowns with add/edit buttons
- `TaskPanelWidget` - Collapsible task list panel
- `TaskListWidget` - Task rows with play buttons and duration
- `ActivityWidget` - Progress bar showing activity percentage
- `StatsWidget` - Daily/weekly KPI cards with optional $ and targets
- `StatusWidget` - Current status and screenshot count

#### Dialogs
- `ClientDialog` - Add/edit clients
- `ProjectDialog` - Add/edit projects
- `TaskDialog` - Add/edit tasks with notes
- `ManualEntryDialog` - Manual time entry
- `SettingsDialog` - App configuration (General + Billing tabs)
- `ReportsDialog` - Report generation with date range

### 4. Reports (`src/reports/`)

#### Generator (`generator.py`)
- Jinja2 HTML template with embedded CSS
- Screenshots embedded as base64 (single-file reports)
- Grouped by project with clickable navigation
- Summary cards, detailed entries, screenshot sections
- Freelancer info in header

### 5. Configuration (`src/utils/`)

#### Config (`config.py`)
JSON-based configuration with properties:
- Screenshot settings (interval, quality, enabled)
- Idle detection threshold
- Application behavior (minimize to tray, auto-start)
- Freelancer details (name, email, address)
- KPI settings (show earnings, targets, daily/weekly goals)
- Last selection persistence

#### Startup (`startup.py`)
- Windows registry integration for auto-start
- Syncs with config on application launch

## Data Flow

```
User Action
    ↓
Main Window (handles UI events)
    ↓
Time Tracker (state management)
    ↓
Database Manager (persistence)
    ↓
Qt Signals (UI updates)
    ↓
Widgets (display changes)
```

## Signal Architecture

The application uses Qt's signal/slot mechanism extensively:

```
TimeTracker.state_changed → MainWindow._on_tracker_state_changed
TimeTracker.time_updated → TimerWidget.set_time
ActivityMonitor.activity_updated → ActivityWidget.set_activity
ScreenshotCapture.screenshot_taken → MainWindow._on_screenshot_taken
IdleDetector.idle_detected → MainWindow._on_idle_detected
```

## Database Schema

```sql
-- Clients
CREATE TABLE clients (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    hourly_rate REAL,
    email TEXT,
    phone TEXT,
    address TEXT,
    notes TEXT,
    created_at TIMESTAMP,
    is_active BOOLEAN
);

-- Projects
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    name TEXT,
    hourly_rate REAL,  -- Override client rate
    created_at TIMESTAMP,
    is_active BOOLEAN,
    UNIQUE(client_id, name)
);

-- Tasks
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    name TEXT,
    notes TEXT,
    created_at TIMESTAMP,
    is_active BOOLEAN,
    is_completed BOOLEAN,
    completed_at TIMESTAMP,
    UNIQUE(project_id, name)
);

-- Time Entries
CREATE TABLE time_entries (
    id INTEGER PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    activity_percentage REAL,
    notes TEXT,
    is_manual BOOLEAN,
    created_at TIMESTAMP
);

-- Screenshots
CREATE TABLE screenshots (
    id INTEGER PRIMARY KEY,
    time_entry_id INTEGER REFERENCES time_entries(id),
    filepath TEXT,
    captured_at TIMESTAMP,
    activity_percentage REAL
);
```

## Configuration Storage

Settings stored in `data/config.json`:

```json
{
  "screenshot_interval": 600,
  "idle_threshold": 300,
  "screenshot_quality": 70,
  "minimize_to_tray": true,
  "start_minimized": false,
  "auto_start_enabled": false,
  "screenshots_enabled": true,
  "freelancer_name": "",
  "freelancer_email": "",
  "freelancer_address": "",
  "payment_details": "",
  "last_client_id": 1,
  "last_project_id": 2,
  "show_kpi_earnings": false,
  "show_kpi_targets": false,
  "daily_target_hours": 8.0,
  "weekly_target_hours": 40.0
}
```

## Extending the Application

### Adding a New Dialog
1. Create dialog class in `src/ui/dialogs/`
2. Add to `__init__.py` exports
3. Connect from `MainWindow`

### Adding a New Widget
1. Create widget class in `src/ui/widgets/`
2. Add to `__init__.py` exports
3. Integrate into `MainWindow._setup_ui()`

### Adding a New Setting
1. Add default to `Config.DEFAULTS`
2. Add property getter/setter in `Config`
3. Add UI control in `SettingsDialog`
4. Load/save in `_load_settings()` and `_on_save()`

### Adding a New Database Column
1. Add to CREATE TABLE in `db_manager._init_database()`
2. Add migration ALTER TABLE in the migration section
3. Update relevant methods and model dataclass
