# Desktop Time Tracker - User Guide

## Getting Started

Desktop Time Tracker helps freelancers track time spent on client projects, capture screenshots as proof of work, and generate professional HTML reports for billing.

### Main Window Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Desktop Time Tracker                                    [_][□][X]│
├───────────────────────────────┬─────────────────────────────────┤
│                               │                                 │
│  Client:  [▼ Select     ] [+] │         T A S K S               │
│  Project: [▼ Select     ] [+] │  ┌─────────────────────────────┐│
│                               │  │ ▶ Task Name        ☐  0:00 ││
│      ┌─────────────────┐      │  │ ▶ Another Task     ☐  1:30 ││
│      │                 │      │  │ ● Active Task      ☐  2:15 ││
│      │   02:34:15      │      │  │ ▶ Completed Task   ☑  0:45 ││
│      │                 │      │  └─────────────────────────────┘│
│      └─────────────────┘      │                                 │
│                               │                     [+ Add Task] │
│  [▶ START] [⏸ PAUSE] [⏹ STOP] │                                 │
│                               │                                 │
│  ┌─────────┐ ┌─────────┐      │                                 │
│  │ Today   │ │ Week    │      │                                 │
│  │  2:34   │ │ 12:45   │      │                                 │
│  └─────────┘ └─────────┘      │                                 │
│                               │                                 │
│  Activity: ████████░░░░ 67%   │                                 │
│  Status: Tracking             │                                 │
│  Screenshots: ON (5)          │                                 │
│                               │                                 │
│  [Manual Entry] [Reports] [Settings]                            │
└───────────────────────────────┴─────────────────────────────────┘
```

## Setting Up

### 1. Create a Client

1. Click the **+** button next to "Client"
2. Fill in the details:
   - **Name** - Client or company name
   - **Hourly Rate** - Your billing rate (used for reports)
   - **Email/Phone/Address** - Optional contact info
   - **Notes** - Private notes about the client
3. Click **Save**

### 2. Create a Project

1. Select a client from the dropdown
2. Click the **+** button next to "Project"
3. Enter the project name
4. Optionally set a different hourly rate (overrides client rate)
5. Click **Save**

### 3. Create Tasks

1. Select a project
2. Click **+ Add** in the Tasks panel
3. Enter task name
4. Add optional notes (for your reference only, not in reports)
5. Click **Save**

## Tracking Time

### Starting a Session

1. Select a client and project
2. Find the task in the task list
3. Click the **▶** (play) button on the task row
4. The timer starts and the task row highlights

### During Tracking

- Timer counts up showing elapsed time
- Activity bar shows your mouse/keyboard activity percentage
- Screenshots are captured at configured intervals
- A beep sound plays when screenshots are taken
- Screenshot counter shows number of captures

### Pausing

- Click **⏸ PAUSE** to temporarily stop tracking
- Time stops counting but session remains open
- Click **▶ START** to resume

### Stopping

- Click **⏹ STOP** to end the session
- Time entry is saved to the database
- You can now select a different task

## Task Management

### Task States

| State | Appearance | Description |
|-------|------------|-------------|
| Available | Normal with ▶ button | Ready to track |
| Tracking | Blue highlight, ● indicator | Currently being tracked |
| Completed | Strikethrough, ☑ checkmark | Marked as done |

### Completing Tasks

1. Click the checkbox (☐) on any task to mark it complete
2. Completed tasks move to the bottom of the list
3. Click again to unmark

### Task Notes

- Tasks can have private notes (indicated by `[i]`)
- Hover over `[i]` to see the notes in a tooltip
- Notes are for your reference only and don't appear in reports

### Editing Tasks

1. (Currently editing tasks requires database access)
2. You can add new tasks even while tracking another task

## Activity Monitoring

The application monitors your keyboard and mouse activity to calculate an activity percentage:

- **Green (70%+)** - High activity
- **Yellow (40-69%)** - Moderate activity
- **Red (below 40%)** - Low activity

### Idle Detection

If no activity is detected for the configured time (default: 5 minutes):
1. A notification appears
2. Tracking is automatically paused
3. Resume when you're back

## Screenshots

### How It Works

- Screenshots capture your primary monitor
- Captured at configurable intervals (default: 10 minutes)
- Saved as JPEG with configurable quality
- Stored in `data/screenshots/YYYY-MM-DD/`

### Smart Capture

Screenshots are automatically skipped when:
- Within 60 seconds of starting/resuming (avoids capturing the timer)
- The Time Tracker window is the active application

### Sound Notification

A beep plays when a screenshot is captured. The status bar shows the count: `Screenshots: ON (5)`

## KPI Dashboard

The Today/Week cards show your tracked time. Enable additional metrics in Settings:

### Earnings Display

- Shows calculated earnings based on hourly rates
- Appears below the time (e.g., "$125.50")

### Target Progress

- Set daily and weekly hour targets
- Shows percentage complete (e.g., "75% of 8.0h")

## Generating Reports

### Creating a Report

1. Click **Reports** button
2. Select date range (Today, This Week, This Month, or Custom)
3. Optionally filter by client
4. Click **Generate Report**
5. **Choose save location** - You can save anywhere:
   - Desktop (easy to find)
   - Documents/Invoices (organized)
   - Dropbox/Google Drive (cloud backup)
   - Email directly from save location
6. Default filename: `time_report_YYYYMMDD_HHMMSS.html`

### Report Contents

- **Header** - Freelancer info, client name, date range
- **Summary Cards** - Total hours, earnings, activity, entry count
- **Summary by Project** - Hours and earnings per project
- **Detailed Entries** - Each time entry with start/end times
- **Screenshot Sections** - Embedded screenshots for each entry

### Report Features

- Click any entry row to jump to its screenshots
- Screenshots include timestamp and activity level
- "Back to Details" links for easy navigation
- All images embedded as base64 (single-file sharing)

## Manual Time Entry

For adding time worked offline or missed tracking:

1. Click **Manual Entry**
2. Select the task
3. Set date, start time, and end time
4. Add optional notes
5. Click **Save**

Manual entries are marked with a "Manual" badge in reports.

## Data Storage

All application data is stored locally in the `data/` folder within the application directory.

### Storage Locations

| Data Type | Location | Description |
|-----------|----------|-------------|
| **Database** | `data/timetracker.db` | All tracking data (clients, projects, tasks, time entries) |
| **Settings** | `data/config.json` | User preferences and configuration |
| **Screenshots** | `data/screenshots/YYYY-MM-DD/` | Organized by date, named `HH-MM-SS_actXX.jpg` |
| **Reports** | User-chosen location | You select where to save each report |

### Screenshot Organization

```
data/screenshots/
├── 2024-02-15/
│   ├── 09-15-00_act75.jpg    ← 9:15 AM, 75% activity
│   ├── 09-25-00_act82.jpg    ← 9:25 AM, 82% activity
│   └── 09-35-00_act68.jpg    ← 9:35 AM, 68% activity
└── 2024-02-16/
    └── 10-00-00_act90.jpg
```

### Report Files

Reports are **not** stored in the application folder:
- Saved wherever you choose (Desktop, Documents, etc.)
- Default name: `time_report_YYYYMMDD_HHMMSS.html`
- Self-contained HTML files (screenshots embedded)
- Can be shared via email or cloud storage

### Data Privacy

- All data stays on **your local machine**
- Screenshots are **never** uploaded anywhere
- Database is **not** synced to cloud
- Reports are only saved where **you** choose

### Backup Recommendations

To backup your data, copy the entire `data/` folder:
```
Desktop Time Tracker/
└── data/               ← Copy this entire folder
    ├── timetracker.db  ← All your tracking data
    ├── config.json     ← Your settings
    └── screenshots/    ← All screenshots
```

## System Tray

The application minimizes to the system tray:

### Tray Icon

- Shows current tracking status in tooltip
- Right-click for quick actions menu

### Quick Actions

- **Show Window** - Open the main window
- **Start/Stop** - Toggle tracking
- **Pause/Resume** - Pause current session
- **Exit** - Close the application

### Minimize Behavior

- Close button minimizes to tray (configurable in Settings)
- Application continues running and tracking

## Settings

Access via the **Settings** button.

### General Tab

**Screenshots**
- Enable/disable screenshot capture
- Capture interval (1-60 minutes)
- Image quality (10-100%)

**Idle Detection**
- Auto-pause threshold (1-60 minutes)

**Application**
- Minimize to tray on close
- Start with Windows
- Start minimized

### Billing Tab

**Your Details** (for reports)
- Name
- Email
- Address
- Payment information

**KPI Dashboard**
- Show earnings on KPI cards
- Show target progress
- Daily target hours
- Weekly target hours

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Start/Resume | Click ▶ on task row |
| Pause | Click ⏸ PAUSE button |
| Stop | Click ⏹ STOP button |
| Minimize | Close button (if configured) |

## Tips for Freelancers

### Best Practices

1. **Create granular tasks** - Break projects into specific tasks for better tracking
2. **Use task notes** - Document requirements, links, or context
3. **Review activity levels** - Aim for consistent activity percentages
4. **Generate regular reports** - Weekly reports help with invoicing

### Hourly Rate Strategy

- Set default rate on the client
- Override on specific projects if needed
- Reports calculate earnings automatically

### Screenshot Tips

- Screenshots prove work was done
- Higher quality = larger file sizes
- Review and clean up old screenshots periodically

### Time Tracking Tips

- Start tracking before you begin work
- Pause for breaks, don't stop
- Stop only when switching tasks
- Use manual entry for forgotten time

## Troubleshooting

### Timer won't start

- Ensure a task is selected
- Click the ▶ button on the task row, not the main START button
- Check that no other session is active

### Screenshots not appearing in reports

- Verify Screenshots are enabled in Settings
- Check that you tracked for longer than the capture interval
- Look in `data/screenshots/` folder

### Activity percentage always low

- Ensure the application isn't blocked by antivirus
- pynput may need administrator privileges
- Check that you're using keyboard/mouse during tracking

### App not minimizing to tray

- Check Settings > "Minimize to tray on close"
- The tray icon should be visible in the system tray

### Data not persisting

- Check write permissions to the `data/` folder
- Ensure the application closes properly
- Look for `data/timetracker.db` file
