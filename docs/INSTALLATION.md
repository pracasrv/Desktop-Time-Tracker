# Desktop Time Tracker - Installation Guide

## System Requirements

- **Operating System:** Windows 10 or later
- **Python:** 3.10 or later
- **RAM:** 4GB minimum (8GB recommended)
- **Disk Space:** 100MB for application + space for screenshots

## Installation Methods

### Method 1: Development Setup (Recommended for developers)

#### Step 1: Clone or Download the Project

```bash
# Clone repository (if using git)
git clone <repository-url>
cd "Desktop Time Tracker"

# Or download and extract the ZIP file
```

#### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `PySide6>=6.5.0` - Qt GUI framework
- `pynput>=1.7.6` - Keyboard/mouse monitoring
- `mss>=9.0.0` - Screenshot capture
- `Pillow>=10.0.0` - Image processing
- `Jinja2>=3.1.0` - Report templates

#### Step 4: Run the Application

```bash
python main.py
```

### Method 2: Create Standalone Executable

For distribution without requiring Python installation.

#### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

#### Step 2: Create Executable

```bash
pyinstaller --name "Desktop Time Tracker" ^
    --windowed ^
    --onefile ^
    --icon=assets/icon.ico ^
    --add-data "src;src" ^
    main.py
```

Options explained:
- `--name` - Executable name
- `--windowed` - No console window
- `--onefile` - Single executable file
- `--icon` - Application icon
- `--add-data` - Include source files

#### Step 3: Locate Executable

Find the executable in `dist/Desktop Time Tracker.exe`

### Method 3: Create Installer (Advanced)

For professional distribution with Windows installer.

#### Step 1: Install NSIS

Download and install [NSIS](https://nsis.sourceforge.io/Download)

#### Step 2: Create Executable First

Follow Method 2 to create the standalone executable.

#### Step 3: Create NSIS Script

Create `installer.nsi`:

```nsis
!include "MUI2.nsh"

Name "Desktop Time Tracker"
OutFile "DesktopTimeTrackerSetup.exe"
InstallDir "$PROGRAMFILES\Desktop Time Tracker"

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

Section "Install"
    SetOutPath $INSTDIR
    File "dist\Desktop Time Tracker.exe"

    CreateShortcut "$DESKTOP\Desktop Time Tracker.lnk" "$INSTDIR\Desktop Time Tracker.exe"
    CreateShortcut "$SMPROGRAMS\Desktop Time Tracker.lnk" "$INSTDIR\Desktop Time Tracker.exe"
SectionEnd
```

#### Step 4: Compile Installer

```bash
makensis installer.nsi
```

## Post-Installation Setup

### First Launch

1. Run the application
2. The following directories are created automatically:
   - `data/` - Application data folder
   - `data/screenshots/` - Screenshot storage
   - `data/timetracker.db` - SQLite database
   - `data/config.json` - Configuration file

### Configure Settings

1. Click **Settings** button in the application
2. Configure screenshot interval (default: 10 minutes)
3. Set idle detection threshold (default: 5 minutes)
4. Enter your freelancer details for reports

### Create Your First Client

1. Click the **+** button next to "Client"
2. Enter client name and hourly rate
3. Click **Save**

### Create Your First Project

1. Select a client
2. Click the **+** button next to "Project"
3. Enter project name
4. Click **Save**

## Data Storage Locations

| Data | Location |
|------|----------|
| Database | `data/timetracker.db` |
| Configuration | `data/config.json` |
| Screenshots | `data/screenshots/YYYY-MM-DD/` |

## Troubleshooting

### "Python not found"

Ensure Python is installed and added to PATH:
```bash
python --version
```

If not working, download Python from [python.org](https://www.python.org/downloads/)

### "Module not found" errors

Ensure virtual environment is activated:
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Screenshots not capturing

1. Ensure `mss` is installed: `pip install mss`
2. Check Settings > Screenshots is enabled
3. Note: Screenshots skip the first 60 seconds after starting

### Activity monitoring not working

1. Run the application as Administrator (may be required for `pynput`)
2. Ensure antivirus isn't blocking keyboard/mouse monitoring

### Application won't start

1. Check for error messages in console
2. Delete `data/config.json` to reset settings
3. Ensure no other instance is running

## Updating

### Development Setup

```bash
# Pull latest changes
git pull

# Update dependencies
pip install -r requirements.txt --upgrade
```

### Standalone Executable

Replace the old `.exe` file with the new version.

## Backup and Migration

### Backup Your Data

Copy the entire `data/` folder:
- `timetracker.db` - All tracking data
- `config.json` - Your settings
- `screenshots/` - All captured screenshots

### Migrate to New Computer

1. Install the application on the new computer
2. Copy your `data/` folder to the new installation
3. Launch the application

## Uninstallation

### Development Setup

1. Close the application
2. Delete the project folder
3. Data is stored in `data/` subfolder (delete if not needed)

### Standalone Executable

1. Close the application
2. Delete the executable
3. Delete `%LOCALAPPDATA%\Desktop Time Tracker\` (if exists)
4. Delete application data folder

### Remove Auto-Start

If auto-start was enabled:
1. Open Settings > General
2. Uncheck "Start with Windows"
3. Or manually remove from Windows Registry:
   - `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
