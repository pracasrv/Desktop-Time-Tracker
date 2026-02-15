# Desktop Time Tracker

A professional time tracking application for freelancers built with Python and PySide6 (Qt). Track time spent on client projects, capture screenshots as proof of work, monitor activity levels, and generate beautiful HTML reports for billing.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.5%2B-green)

## Features

### Time Tracking
- ⏱️ **Multi-level Organization** - Organize by Client → Project → Task
- ▶️ **One-Click Start** - Start tracking with a single click on any task
- ⏸️ **Pause & Resume** - Pause tracking for breaks without losing time
- 📊 **Activity Monitoring** - Track keyboard and mouse activity percentage
- 🔕 **Idle Detection** - Auto-pause after configurable idle time
- 📝 **Task Notes** - Add private notes to tasks (not shown in reports)

### Screenshot Capture
- 📸 **Automatic Screenshots** - Periodic screenshot capture (configurable interval)
- 🎯 **Smart Capture** - Skips first 60 seconds and when timer app is active
- 🔊 **Sound Notification** - Beep when screenshot is captured
- 📊 **Capture Counter** - Live count of screenshots taken
- 💾 **Organized Storage** - Screenshots stored by date

### Reporting
- 📄 **Professional HTML Reports** - Beautiful single-file reports with embedded screenshots
- 💰 **Earnings Calculation** - Automatic earnings based on hourly rates
- 📈 **Activity Analytics** - Average activity percentage per entry
- 🖼️ **Screenshot Gallery** - Embedded screenshots with activity levels
- 🔗 **Navigation** - Clickable entries that jump to screenshot sections
- 📧 **Freelancer Info** - Include your contact and payment details

### KPI Dashboard
- 📊 **Today & Week Cards** - Quick view of hours worked
- 💵 **Optional Earnings** - Show calculated earnings on cards
- 🎯 **Target Progress** - Set daily/weekly targets and track progress
- ⚙️ **Fully Configurable** - Enable/disable features in settings

### User Experience
- 🎨 **Dark Theme** - Modern dark UI optimized for long hours
- 🔔 **System Tray** - Minimize to tray and continue tracking
- 💾 **Auto-Save** - Data persists automatically
- 🔁 **Remember Selection** - Last client/project restored on startup
- 🚀 **Windows Startup** - Optional auto-start with Windows
- ✅ **Task Completion** - Mark tasks as complete with checkbox

## Screenshots

### Main Window
```
┌─────────────────────────────────────────────────────────────────┐
│  Client & Project Selection │         Active Tasks               │
│  ─────────────────────────── │  ────────────────────────────────  │
│  Large Timer Display         │  ▶ Task 1            ☐  2:34      │
│  Start/Pause/Stop Controls   │  ● Tracking Task     ☐  1:15      │
│  Daily/Weekly KPI Cards      │  ▶ Completed Task    ☑  0:45      │
│  Activity Progress Bar       │                                    │
│  Screenshot Status Counter   │  [+ Add Task]                      │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites
- Python 3.10 or higher
- Windows 10 or later

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/desktop-time-tracker.git
   cd desktop-time-tracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## Dependencies

- **PySide6** (≥6.5.0) - Qt GUI framework
- **pynput** (≥1.7.6) - Keyboard/mouse monitoring
- **mss** (≥9.0.0) - Fast screenshot capture
- **Pillow** (≥10.0.0) - Image processing
- **Jinja2** (≥3.1.0) - HTML report templates

## Documentation

- 📖 [User Guide](docs/USER_GUIDE.md) - Complete user manual
- 🏗️ [Architecture](docs/ARCHITECTURE.md) - Developer documentation
- 💿 [Installation Guide](docs/INSTALLATION.md) - Detailed setup instructions

## Quick Usage

### 1. Setup
1. Click **Settings** to configure screenshot interval and freelancer details
2. Create a client with **+ button** next to Client dropdown
3. Create a project with **+ button** next to Project dropdown
4. Add tasks to your project

### 2. Track Time
1. Click the **▶** button on any task to start tracking
2. Timer counts up, activity is monitored, screenshots are captured
3. Click **⏸ PAUSE** for breaks
4. Click **⏹ STOP** when done

### 3. Generate Reports
1. Click **Reports** button
2. Select date range and optional client filter
3. Click **Generate Report**
4. Save HTML file and share with client

## Project Structure

```
Desktop Time Tracker/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md         # Developer docs
│   ├── INSTALLATION.md         # Install guide
│   └── USER_GUIDE.md           # User manual
└── src/
    ├── database/               # SQLite models & manager
    ├── core/                   # Tracking, activity, screenshots
    ├── ui/                     # PySide6 interface
    │   ├── dialogs/            # Dialog windows
    │   └── widgets/            # UI components
    ├── reports/                # HTML report generation
    └── utils/                  # Config & utilities
```

## Configuration

Settings are stored in `data/config.json`:

- Screenshot interval and quality
- Idle detection threshold
- Freelancer details for reports
- KPI dashboard preferences
- Daily/weekly hour targets

## Building Executable

Create a standalone `.exe` for distribution:

```bash
pip install pyinstaller
pyinstaller --name "Desktop Time Tracker" ^
    --windowed ^
    --onefile ^
    main.py
```

Executable will be in `dist/` folder.

## Data Storage

All application data is stored locally in the `data/` folder (created automatically on first run):

```
Desktop Time Tracker/
└── data/                                    ← All local data (git ignored)
    ├── timetracker.db                       ← SQLite database
    ├── config.json                          ← User settings
    └── screenshots/                         ← Screenshot storage
        └── YYYY-MM-DD/                      ← Organized by date
            └── HH-MM-SS_actXX.jpg          ← Timestamped files
```

**Reports** are saved wherever you choose via file save dialog:
- Default filename: `time_report_YYYYMMDD_HHMMSS.html`
- Single-file HTML with embedded screenshots
- Can be saved to Desktop, Documents, cloud storage, etc.

**Privacy:** All data stays on your local machine. The `data/` folder is git-ignored and never uploaded to repositories.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [PySide6](https://doc.qt.io/qtforpython-6/) (Qt for Python)
- Screenshot capture using [mss](https://github.com/BoboTiG/python-mss)
- Activity monitoring with [pynput](https://github.com/moses-palmer/pynput)

## Support

For issues, questions, or suggestions:
- 🐛 [Report a Bug](https://github.com/yourusername/desktop-time-tracker/issues)
- 💡 [Request a Feature](https://github.com/yourusername/desktop-time-tracker/issues)
- 📖 [Read the Docs](docs/USER_GUIDE.md)

## Roadmap

- [ ] Cross-platform support (macOS, Linux)
- [ ] Cloud backup integration
- [ ] PDF report export
- [ ] Calendar view of tracked time
- [ ] Project budgets and alerts
- [ ] Client portal for report viewing

---

Made with ❤️ for freelancers who value transparency and professionalism.
