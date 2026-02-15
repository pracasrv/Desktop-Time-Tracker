"""Database manager for SQLite operations."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from .models import Client, Project, Task, TimeEntry, Screenshot, TimeEntryWithDetails


class DatabaseManager:
    """Manages all database operations for the time tracker."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()

    def _ensure_db_directory(self):
        """Create database directory if it doesn't exist."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self):
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                hourly_rate REAL DEFAULT 0.0,
                email TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                address TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                hourly_rate REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (client_id) REFERENCES clients(id),
                UNIQUE(client_id, name)
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                is_completed BOOLEAN DEFAULT 0,
                completed_at TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id),
                UNIQUE(project_id, name)
            );

            CREATE TABLE IF NOT EXISTS time_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                duration_seconds INTEGER DEFAULT 0,
                activity_percentage REAL DEFAULT 0.0,
                notes TEXT,
                is_manual BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            );

            CREATE TABLE IF NOT EXISTS screenshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time_entry_id INTEGER NOT NULL,
                filepath TEXT NOT NULL,
                captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activity_percentage REAL DEFAULT 0.0,
                FOREIGN KEY (time_entry_id) REFERENCES time_entries(id)
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_time_entries_task ON time_entries(task_id);
            CREATE INDEX IF NOT EXISTS idx_time_entries_start ON time_entries(start_time);
            CREATE INDEX IF NOT EXISTS idx_screenshots_entry ON screenshots(time_entry_id);
        ''')

        # Migration: Add is_completed and completed_at columns if they don't exist
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN is_completed BOOLEAN DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN completed_at TIMESTAMP")
        except sqlite3.OperationalError:
            pass  # Column already exists

        # Migration: Add client detail columns
        for col in ['email', 'phone', 'address', 'notes']:
            try:
                cursor.execute(f"ALTER TABLE clients ADD COLUMN {col} TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass  # Column already exists

        # Migration: Add notes column to tasks
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN notes TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass  # Column already exists

        conn.commit()
        conn.close()

    # ==================== CLIENT OPERATIONS ====================

    def add_client(self, client: Client) -> int:
        """Add a new client and return its ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO clients (name, hourly_rate, email, phone, address, notes, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (client.name, client.hourly_rate, client.email, client.phone,
             client.address, client.notes, client.is_active)
        )
        client_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return client_id

    def update_client(self, client: Client):
        """Update an existing client."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE clients SET name = ?, hourly_rate = ?, email = ?, phone = ?,
               address = ?, notes = ?, is_active = ? WHERE id = ?''',
            (client.name, client.hourly_rate, client.email, client.phone,
             client.address, client.notes, client.is_active, client.id)
        )
        conn.commit()
        conn.close()

    def _row_to_client(self, row) -> Client:
        """Convert a database row to a Client object."""
        return Client(
            id=row['id'],
            name=row['name'],
            hourly_rate=row['hourly_rate'] or 0.0,
            email=row['email'] or '',
            phone=row['phone'] or '',
            address=row['address'] or '',
            notes=row['notes'] or '',
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            is_active=bool(row['is_active'])
        )

    def get_client(self, client_id: int) -> Optional[Client]:
        """Get a client by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return self._row_to_client(row)
        return None

    def get_all_clients(self, active_only: bool = True) -> List[Client]:
        """Get all clients."""
        conn = self._get_connection()
        cursor = conn.cursor()
        if active_only:
            cursor.execute('SELECT * FROM clients WHERE is_active = 1 ORDER BY name')
        else:
            cursor.execute('SELECT * FROM clients ORDER BY name')
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_client(row) for row in rows]

    def delete_client(self, client_id: int):
        """Soft delete a client by setting is_active to False."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE clients SET is_active = 0 WHERE id = ?', (client_id,))
        conn.commit()
        conn.close()

    # ==================== PROJECT OPERATIONS ====================

    def add_project(self, project: Project) -> int:
        """Add a new project and return its ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO projects (client_id, name, hourly_rate, is_active) VALUES (?, ?, ?, ?)',
            (project.client_id, project.name, project.hourly_rate, project.is_active)
        )
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return project_id

    def update_project(self, project: Project):
        """Update an existing project."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE projects SET client_id = ?, name = ?, hourly_rate = ?, is_active = ? WHERE id = ?',
            (project.client_id, project.name, project.hourly_rate, project.is_active, project.id)
        )
        conn.commit()
        conn.close()

    def get_project(self, project_id: int) -> Optional[Project]:
        """Get a project by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Project(
                id=row['id'],
                client_id=row['client_id'],
                name=row['name'],
                hourly_rate=row['hourly_rate'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                is_active=bool(row['is_active'])
            )
        return None

    def get_projects_by_client(self, client_id: int, active_only: bool = True) -> List[Project]:
        """Get all projects for a client."""
        conn = self._get_connection()
        cursor = conn.cursor()
        if active_only:
            cursor.execute(
                'SELECT * FROM projects WHERE client_id = ? AND is_active = 1 ORDER BY name',
                (client_id,)
            )
        else:
            cursor.execute(
                'SELECT * FROM projects WHERE client_id = ? ORDER BY name',
                (client_id,)
            )
        rows = cursor.fetchall()
        conn.close()
        return [
            Project(
                id=row['id'],
                client_id=row['client_id'],
                name=row['name'],
                hourly_rate=row['hourly_rate'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                is_active=bool(row['is_active'])
            )
            for row in rows
        ]

    def delete_project(self, project_id: int):
        """Soft delete a project."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE projects SET is_active = 0 WHERE id = ?', (project_id,))
        conn.commit()
        conn.close()

    # ==================== TASK OPERATIONS ====================

    def add_task(self, task: Task) -> int:
        """Add a new task and return its ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO tasks (project_id, name, notes, is_active, is_completed) VALUES (?, ?, ?, ?, ?)',
            (task.project_id, task.name, task.notes, task.is_active, task.is_completed)
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def update_task(self, task: Task):
        """Update an existing task."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE tasks SET project_id = ?, name = ?, notes = ?, is_active = ?,
               is_completed = ?, completed_at = ? WHERE id = ?''',
            (task.project_id, task.name, task.notes, task.is_active, task.is_completed,
             task.completed_at.isoformat() if task.completed_at else None, task.id)
        )
        conn.commit()
        conn.close()

    def mark_task_completed(self, task_id: int, completed: bool = True):
        """Mark a task as completed or uncompleted."""
        conn = self._get_connection()
        cursor = conn.cursor()
        completed_at = datetime.now().isoformat() if completed else None
        cursor.execute(
            'UPDATE tasks SET is_completed = ?, completed_at = ? WHERE id = ?',
            (completed, completed_at, task_id)
        )
        conn.commit()
        conn.close()

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return self._row_to_task(row)
        return None

    def _row_to_task(self, row) -> Task:
        """Convert a database row to a Task object."""
        completed_at = None
        if row['completed_at']:
            try:
                completed_at = datetime.fromisoformat(row['completed_at'])
            except (ValueError, TypeError):
                pass
        return Task(
            id=row['id'],
            project_id=row['project_id'],
            name=row['name'],
            notes=row['notes'] or '',
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            is_active=bool(row['is_active']),
            is_completed=bool(row['is_completed']) if row['is_completed'] is not None else False,
            completed_at=completed_at
        )

    def get_tasks_by_project(self, project_id: int, active_only: bool = True,
                              include_completed: bool = True) -> List[Task]:
        """Get all tasks for a project, ordered by completion status then name."""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM tasks WHERE project_id = ?'
        params = [project_id]

        if active_only:
            query += ' AND is_active = 1'
        if not include_completed:
            query += ' AND is_completed = 0'

        # Order: uncompleted first, then by name
        query += ' ORDER BY is_completed ASC, name ASC'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_task(row) for row in rows]

    def delete_task(self, task_id: int):
        """Soft delete a task."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET is_active = 0 WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()

    # ==================== TIME ENTRY OPERATIONS ====================

    def add_time_entry(self, entry: TimeEntry) -> int:
        """Add a new time entry and return its ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO time_entries
               (task_id, start_time, end_time, duration_seconds, activity_percentage, notes, is_manual)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (
                entry.task_id,
                entry.start_time.isoformat() if entry.start_time else None,
                entry.end_time.isoformat() if entry.end_time else None,
                entry.duration_seconds,
                entry.activity_percentage,
                entry.notes,
                entry.is_manual
            )
        )
        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return entry_id

    def update_time_entry(self, entry: TimeEntry):
        """Update an existing time entry."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE time_entries
               SET task_id = ?, start_time = ?, end_time = ?, duration_seconds = ?,
                   activity_percentage = ?, notes = ?, is_manual = ?
               WHERE id = ?''',
            (
                entry.task_id,
                entry.start_time.isoformat() if entry.start_time else None,
                entry.end_time.isoformat() if entry.end_time else None,
                entry.duration_seconds,
                entry.activity_percentage,
                entry.notes,
                entry.is_manual,
                entry.id
            )
        )
        conn.commit()
        conn.close()

    def get_time_entry(self, entry_id: int) -> Optional[TimeEntry]:
        """Get a time entry by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM time_entries WHERE id = ?', (entry_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return self._row_to_time_entry(row)
        return None

    def _row_to_time_entry(self, row) -> TimeEntry:
        """Convert a database row to a TimeEntry object."""
        return TimeEntry(
            id=row['id'],
            task_id=row['task_id'],
            start_time=datetime.fromisoformat(row['start_time']) if row['start_time'] else None,
            end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
            duration_seconds=row['duration_seconds'],
            activity_percentage=row['activity_percentage'],
            notes=row['notes'] or "",
            is_manual=bool(row['is_manual']),
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )

    def get_time_entries_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        client_id: Optional[int] = None,
        project_id: Optional[int] = None,
        task_id: Optional[int] = None
    ) -> List[TimeEntryWithDetails]:
        """Get time entries within a date range with full details."""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT
                te.*,
                t.name as task_name,
                p.name as project_name,
                p.hourly_rate as project_rate,
                c.name as client_name,
                c.hourly_rate as client_rate
            FROM time_entries te
            JOIN tasks t ON te.task_id = t.id
            JOIN projects p ON t.project_id = p.id
            JOIN clients c ON p.client_id = c.id
            WHERE te.start_time >= ? AND te.start_time <= ?
        '''
        params = [start_date.isoformat(), end_date.isoformat()]

        if client_id:
            query += ' AND c.id = ?'
            params.append(client_id)
        if project_id:
            query += ' AND p.id = ?'
            params.append(project_id)
        if task_id:
            query += ' AND t.id = ?'
            params.append(task_id)

        query += ' ORDER BY te.start_time DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()

        entries = []
        for row in rows:
            entry = self._row_to_time_entry(row)
            hourly_rate = row['project_rate'] if row['project_rate'] else row['client_rate']

            # Get screenshots for this entry
            cursor.execute(
                'SELECT * FROM screenshots WHERE time_entry_id = ? ORDER BY captured_at',
                (entry.id,)
            )
            screenshot_rows = cursor.fetchall()
            screenshots = [
                Screenshot(
                    id=s['id'],
                    time_entry_id=s['time_entry_id'],
                    filepath=s['filepath'],
                    captured_at=datetime.fromisoformat(s['captured_at']) if s['captured_at'] else None,
                    activity_percentage=s['activity_percentage']
                )
                for s in screenshot_rows
            ]

            entries.append(TimeEntryWithDetails(
                entry=entry,
                task_name=row['task_name'],
                project_name=row['project_name'],
                client_name=row['client_name'],
                hourly_rate=hourly_rate or 0.0,
                screenshots=screenshots
            ))

        conn.close()
        return entries

    def get_active_time_entry(self) -> Optional[TimeEntry]:
        """Get the currently active (running) time entry if any."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM time_entries WHERE end_time IS NULL ORDER BY start_time DESC LIMIT 1'
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return self._row_to_time_entry(row)
        return None

    def delete_time_entry(self, entry_id: int):
        """Delete a time entry and its screenshots."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM screenshots WHERE time_entry_id = ?', (entry_id,))
        cursor.execute('DELETE FROM time_entries WHERE id = ?', (entry_id,))
        conn.commit()
        conn.close()

    # ==================== SCREENSHOT OPERATIONS ====================

    def add_screenshot(self, screenshot: Screenshot) -> int:
        """Add a new screenshot and return its ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO screenshots (time_entry_id, filepath, captured_at, activity_percentage)
               VALUES (?, ?, ?, ?)''',
            (
                screenshot.time_entry_id,
                screenshot.filepath,
                screenshot.captured_at.isoformat() if screenshot.captured_at else None,
                screenshot.activity_percentage
            )
        )
        screenshot_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return screenshot_id

    def get_screenshots_by_entry(self, entry_id: int) -> List[Screenshot]:
        """Get all screenshots for a time entry."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM screenshots WHERE time_entry_id = ? ORDER BY captured_at',
            (entry_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            Screenshot(
                id=row['id'],
                time_entry_id=row['time_entry_id'],
                filepath=row['filepath'],
                captured_at=datetime.fromisoformat(row['captured_at']) if row['captured_at'] else None,
                activity_percentage=row['activity_percentage']
            )
            for row in rows
        ]

    # ==================== SETTINGS OPERATIONS ====================

    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        """Get a setting value by key."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        return row['value'] if row else default

    def set_setting(self, key: str, value: str):
        """Set a setting value."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
            (key, value)
        )
        conn.commit()
        conn.close()

    def get_all_settings(self) -> dict:
        """Get all settings as a dictionary."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM settings')
        rows = cursor.fetchall()
        conn.close()
        return {row['key']: row['value'] for row in rows}

    # ==================== REPORTING HELPERS ====================

    def get_summary_by_client(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[dict]:
        """Get time summary grouped by client."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                c.id as client_id,
                c.name as client_name,
                c.hourly_rate as client_rate,
                SUM(te.duration_seconds) as total_seconds,
                AVG(te.activity_percentage) as avg_activity
            FROM time_entries te
            JOIN tasks t ON te.task_id = t.id
            JOIN projects p ON t.project_id = p.id
            JOIN clients c ON p.client_id = c.id
            WHERE te.start_time >= ? AND te.start_time <= ?
            GROUP BY c.id
            ORDER BY total_seconds DESC
        ''', (start_date.isoformat(), end_date.isoformat()))

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                'client_id': row['client_id'],
                'client_name': row['client_name'],
                'hourly_rate': row['client_rate'],
                'total_seconds': row['total_seconds'],
                'avg_activity': row['avg_activity']
            }
            for row in rows
        ]
