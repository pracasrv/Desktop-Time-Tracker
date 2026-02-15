# Pre-Publication Testing Checklist

Complete this checklist before publishing to GitHub.

## ✅ 1. Git File Check

**Files to be committed: 40**

### Check what will be committed:
```bash
cd "Desktop Time Tracker"
git init
git add -n .
```

### Expected files (should see these):
- [x] .gitignore
- [x] .gitattributes
- [x] LICENSE
- [x] README.md
- [x] main.py
- [x] requirements.txt
- [x] docs/ (3 files)
- [x] src/ (all Python source files)

### Should NOT see (verify these are ignored):
- [ ] data/
- [ ] venv/
- [ ] __pycache__/
- [ ] *.html reports
- [ ] .claude/
- [ ] *.pyc files

**Command to verify:**
```bash
git status --ignored
```

---

## ✅ 2. Application Functionality Test

### Test Clean Installation:
```bash
# Ensure venv is activated
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Manual Testing Steps:

#### Initial Launch
- [ ] Application starts without errors
- [ ] Main window appears
- [ ] No error dialogs on startup
- [ ] `data/` folder is created automatically
- [ ] `data/config.json` is created
- [ ] `data/timetracker.db` is created

#### Client/Project/Task Creation
- [ ] Click **+ next to Client** → Dialog opens
- [ ] Create a client successfully
- [ ] Client appears in dropdown
- [ ] Click **+ next to Project** → Dialog opens
- [ ] Create a project successfully
- [ ] Project appears in dropdown
- [ ] Click **+ Add Task** → Dialog opens
- [ ] Create a task with notes
- [ ] Task appears in task list
- [ ] Notes indicator `[i]` shows tooltip

#### Time Tracking
- [ ] Click ▶ on a task → Timer starts
- [ ] Timer counts up
- [ ] Activity bar shows percentage
- [ ] Click ⏸ PAUSE → Timer pauses
- [ ] Click ▶ START → Timer resumes
- [ ] Click ⏹ STOP → Session saved
- [ ] Daily/Weekly KPI cards update

#### Screenshots (wait 60+ seconds)
- [ ] Screenshot counter appears: "Screenshots: ON (1)"
- [ ] Beep sound plays on capture
- [ ] Screenshot saved in `data/screenshots/YYYY-MM-DD/`
- [ ] Filename includes timestamp and activity

#### Settings
- [ ] Click **Settings** → Dialog opens
- [ ] Change screenshot interval
- [ ] Configure freelancer details
- [ ] Enable KPI earnings
- [ ] Enable KPI targets
- [ ] Set daily/weekly targets
- [ ] Click **Save** → Settings persist

#### Reports
- [ ] Click **Reports** → Dialog opens
- [ ] Select date range
- [ ] Generate report successfully
- [ ] HTML file opens in browser
- [ ] Report shows correct data
- [ ] Screenshots are embedded
- [ ] Freelancer info in header
- [ ] Client name shows with "CLIENT:" prefix
- [ ] "FREELANCER:" label visible

#### System Tray
- [ ] Minimize to tray works
- [ ] Tray icon visible
- [ ] Right-click shows menu
- [ ] "Show Window" works
- [ ] Application continues running

#### Data Persistence
- [ ] Close application
- [ ] Reopen application
- [ ] Last client/project selected
- [ ] Previous time entries visible
- [ ] Settings preserved

---

## ✅ 3. Code Quality Check

### No Debug Code:
```bash
# Search for common debug statements
grep -r "print(" src/
grep -r "console.log" src/
grep -r "debugger" src/
```
**Expected:** No debug statements (or only intentional ones)

### No TODO Comments:
```bash
# Search for TODO/FIXME
grep -r "TODO" src/
grep -r "FIXME" src/
```
**Expected:** No critical TODOs

### No Hardcoded Paths:
```bash
# Check for hardcoded paths
grep -r "C:\\\\" src/
grep -r "/home/" src/
```
**Expected:** All paths use Path or config

---

## ✅ 4. Documentation Verification

### README.md
- [ ] Installation steps are clear
- [ ] Features list is accurate
- [ ] Screenshots/diagrams present
- [ ] Links work (if any)
- [ ] GitHub URL is correct (or placeholder)

### ARCHITECTURE.md
- [ ] Reflects current codebase structure
- [ ] All components documented
- [ ] Database schema matches code
- [ ] Signal flow is accurate

### INSTALLATION.md
- [ ] Steps work on fresh install
- [ ] Dependencies list matches requirements.txt
- [ ] PyInstaller command works
- [ ] Troubleshooting covers common issues

### USER_GUIDE.md
- [ ] All features documented
- [ ] Screenshots match current UI
- [ ] Step-by-step guides are clear
- [ ] Keyboard shortcuts listed

---

## ✅ 5. Dependencies Check

### Verify requirements.txt:
```bash
pip freeze > frozen.txt
diff requirements.txt frozen.txt
```

**Current requirements.txt:**
```
PySide6>=6.5.0
pynput>=1.7.6
mss>=9.0.0
Pillow>=10.0.0
Jinja2>=3.1.0
```

### Test fresh install:
```bash
# Create new venv
python -m venv test_venv
test_venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## ✅ 6. File Size Check

### Check repository size:
```bash
# Get total size
du -sh .

# Get size by folder
du -sh src/ docs/ data/ venv/
```

**Expected:**
- Source: < 500 KB
- Docs: < 100 KB
- Total (without venv/data): < 1 MB

### Check for large files:
```bash
find . -type f -size +1M -not -path "./venv/*" -not -path "./data/*"
```
**Expected:** No large files

---

## ✅ 7. License & Legal

- [ ] LICENSE file present
- [ ] Copyright year is correct (2024)
- [ ] No proprietary code included
- [ ] All dependencies are compatible licenses
- [ ] Attribution to libraries provided

---

## ✅ 8. Final Git Commands

### Reset and recommit:
```bash
# Remove test git folder
rm -rf .git

# Initialize fresh
git init

# Add all files
git add .

# Verify what's staged
git status

# Check file count (should be 40)
git status --short | wc -l

# Create initial commit
git commit -m "Initial commit: Desktop Time Tracker v1.0

Features:
- Multi-level time tracking (Client → Project → Task)
- Automatic screenshot capture with smart skipping
- Activity monitoring and idle detection
- Professional HTML reports with embedded screenshots
- KPI dashboard with earnings and targets
- Task notes for freelancer reference
- System tray integration
- Persistent settings and last selection

Built with Python + PySide6"
```

### Before pushing to GitHub:
```bash
# Create repository on GitHub first, then:
git remote add origin https://github.com/yourusername/desktop-time-tracker.git
git branch -M main
git push -u origin main
```

---

## ✅ 9. Post-Publication Verification

After pushing to GitHub:

- [ ] Repository is public/private as intended
- [ ] README.md displays correctly
- [ ] All files uploaded successfully
- [ ] No sensitive data visible
- [ ] Clone test: `git clone` works
- [ ] Fresh install test: Clone → venv → pip install → run

---

## Issues Found During Testing

Document any issues here:

1. Issue: _______________
   Solution: _______________

2. Issue: _______________
   Solution: _______________

---

## Sign-Off

- [ ] All tests passed
- [ ] Documentation complete
- [ ] No errors or warnings
- [ ] Ready for publication

**Tested by:** _______________
**Date:** _______________
**Version:** 1.0
