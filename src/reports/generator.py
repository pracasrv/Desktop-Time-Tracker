"""HTML report generator with embedded screenshots."""

import base64
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from jinja2 import Template

from ..database.db_manager import DatabaseManager
from ..database.models import TimeEntryWithDetails
from ..utils.config import Config


class ReportGenerator:
    """Generates HTML reports from time entries."""

    def __init__(self, db_manager: DatabaseManager, config: Config):
        self.db_manager = db_manager
        self.config = config

    def generate_html_report(
        self,
        output_path: str,
        start_date: datetime,
        end_date: datetime,
        client_id: Optional[int] = None
    ):
        """Generate an HTML report with embedded images."""
        entries = self.db_manager.get_time_entries_by_date_range(
            start_date, end_date, client_id=client_id
        )

        # Calculate totals
        total_seconds = sum(e.entry.duration_seconds for e in entries)
        total_earnings = sum(e.earnings for e in entries)
        avg_activity = 0.0
        if entries:
            avg_activity = sum(e.entry.activity_percentage for e in entries) / len(entries)

        # Get client name (report is typically at client level)
        client_name = entries[0].client_name if entries else None

        # Group by project (instead of client)
        by_project = {}
        for entry in entries:
            project_name = entry.project_name
            if project_name not in by_project:
                by_project[project_name] = {
                    'entries': [],
                    'total_seconds': 0,
                    'total_earnings': 0.0
                }
            by_project[project_name]['entries'].append(entry)
            by_project[project_name]['total_seconds'] += entry.entry.duration_seconds
            by_project[project_name]['total_earnings'] += entry.earnings

        # Render HTML
        html = self._render_template(
            entries=entries,
            by_project=by_project,
            client_name=client_name,
            start_date=start_date,
            end_date=end_date,
            total_seconds=total_seconds,
            total_earnings=total_earnings,
            avg_activity=avg_activity
        )

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

    def _encode_image(self, filepath: str) -> Optional[str]:
        """Encode an image file as base64 data URI."""
        try:
            path = Path(filepath)
            if not path.exists():
                return None

            with open(path, 'rb') as f:
                data = f.read()

            ext = path.suffix.lower()
            mime = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
            b64 = base64.b64encode(data).decode('utf-8')

            return f"data:{mime};base64,{b64}"
        except Exception:
            return None

    def _format_duration(self, seconds: int) -> str:
        """Format seconds as HH:MM:SS."""
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def _render_template(
        self,
        entries: List[TimeEntryWithDetails],
        by_project: dict,
        client_name: str,
        start_date: datetime,
        end_date: datetime,
        total_seconds: int,
        total_earnings: float,
        avg_activity: float
    ) -> str:
        """Render the HTML report template."""
        template = Template(HTML_TEMPLATE)

        # Process screenshots for each entry
        entries_with_images = []
        for entry in entries:
            screenshots = []
            for screenshot in entry.screenshots:
                img_data = self._encode_image(screenshot.filepath)
                if img_data:
                    screenshots.append({
                        'data': img_data,
                        'time': screenshot.captured_at.strftime('%H:%M:%S') if screenshot.captured_at else '',
                        'activity': screenshot.activity_percentage
                    })
            entries_with_images.append({
                'entry': entry,
                'screenshots': screenshots
            })

        return template.render(
            entries=entries_with_images,
            by_project=by_project,
            client_name=client_name,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            total_hours=total_seconds / 3600,
            total_duration=self._format_duration(total_seconds),
            total_amount=total_earnings,
            avg_activity=avg_activity,
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            format_duration=self._format_duration,
            # Freelancer details from config
            freelancer_name=self.config.freelancer_name,
            freelancer_email=self.config.freelancer_email,
            freelancer_address=self.config.freelancer_address,
            payment_details=self.config.payment_details
        )


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Time Tracking Invoice</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 30px 20px;
            margin-bottom: 30px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        .header-left h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        .header-left p {
            opacity: 0.8;
            font-size: 14px;
        }
        .header-right {
            text-align: right;
        }
        .header-right .from-label {
            font-size: 12px;
            text-transform: uppercase;
            opacity: 0.6;
            margin-bottom: 5px;
        }
        .header-right .name {
            font-size: 16px;
            font-weight: 600;
        }
        .header-right p {
            opacity: 0.8;
            font-size: 13px;
            margin: 2px 0;
        }
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .card h3 {
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        .card .value {
            font-size: 28px;
            font-weight: bold;
            color: #1a1a2e;
        }
        .card .value.green { color: #28a745; }
        .card .value.blue { color: #0078d4; }
        .section {
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .section h2 {
            font-size: 20px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: #555;
            text-transform: uppercase;
            font-size: 12px;
        }
        tr:hover {
            background-color: #f8f9fa;
        }
        tr.clickable {
            cursor: pointer;
            transition: background-color 0.2s;
        }
        tr.clickable:hover {
            background-color: #e3f2fd;
        }
        tr.clickable td:first-child::before {
            content: "";
        }
        .has-screenshots {
            position: relative;
        }
        .has-screenshots::after {
            content: "📷";
            margin-left: 8px;
            font-size: 12px;
        }
        a.back-link {
            display: inline-block;
            color: #0078d4;
            text-decoration: none;
            font-size: 13px;
            margin-top: 10px;
        }
        a.back-link:hover {
            text-decoration: underline;
        }
        .activity-bar {
            display: inline-block;
            width: 60px;
            height: 8px;
            background-color: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin-right: 8px;
            vertical-align: middle;
        }
        .activity-bar-fill {
            height: 100%;
            border-radius: 4px;
        }
        .activity-high { background-color: #28a745; }
        .activity-medium { background-color: #ffc107; }
        .activity-low { background-color: #dc3545; }
        .screenshots {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .screenshot {
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }
        .screenshot img {
            width: 100%;
            height: auto;
            display: block;
        }
        .screenshot .info {
            padding: 8px 10px;
            background: #f8f9fa;
            font-size: 12px;
            color: #666;
        }
        .entry-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        .entry-title {
            font-weight: 600;
        }
        .entry-meta {
            color: #666;
            font-size: 14px;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-manual {
            background: #e9ecef;
            color: #666;
        }
        .payment-info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            border: 1px solid #e0e0e0;
        }
        .payment-info h3 {
            color: #1a1a2e;
            margin-bottom: 10px;
            font-size: 16px;
        }
        .payment-info p {
            color: #666;
            font-size: 13px;
            white-space: pre-line;
        }
        footer {
            text-align: center;
            padding: 20px;
            color: #888;
            font-size: 12px;
        }
        @media print {
            body { background: white; }
            .container { padding: 0; }
            .section { box-shadow: none; border: 1px solid #ddd; }
            .screenshot img { max-height: 180px; object-fit: cover; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-left">
                <h1>Time Tracking Report</h1>
                {% if client_name %}<p style="font-size: 18px; opacity: 1; margin-bottom: 8px;">CLIENT: {{ client_name }}</p>{% endif %}
                <p>Period: {{ start_date }} to {{ end_date }}</p>
                <p>Generated: {{ generated_at }}</p>
            </div>
            {% if freelancer_name or freelancer_email %}
            <div class="header-right">
                <div class="from-label">FREELANCER:</div>
                {% if freelancer_name %}<div class="name">{{ freelancer_name }}</div>{% endif %}
                {% if freelancer_email %}<p>{{ freelancer_email }}</p>{% endif %}
                {% if freelancer_address %}<p>{{ freelancer_address }}</p>{% endif %}
            </div>
            {% endif %}
        </header>

        <div class="summary-cards">
            <div class="card">
                <h3>Total Time</h3>
                <div class="value">{{ "%.1f"|format(total_hours) }} hrs</div>
            </div>
            <div class="card">
                <h3>Total Billed Amount</h3>
                <div class="value green">${{ "%.2f"|format(total_amount) }}</div>
            </div>
            <div class="card">
                <h3>Avg Activity</h3>
                <div class="value blue">{{ "%.0f"|format(avg_activity) }}%</div>
            </div>
            <div class="card">
                <h3>Time Entries</h3>
                <div class="value">{{ entries|length }}</div>
            </div>
        </div>

        <div class="section">
            <h2>Summary by Project</h2>
            <table>
                <thead>
                    <tr>
                        <th>Project</th>
                        <th>Duration</th>
                        <th>Billed Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {% for project_name, data in by_project.items() %}
                    <tr>
                        <td>{{ project_name }}</td>
                        <td>{{ format_duration(data.total_seconds) }}</td>
                        <td>${{ "%.2f"|format(data.total_earnings) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="section" id="detailed-entries">
            <h2>Detailed Entries</h2>
            <table>
                <thead>
                    <tr>
                        <th>Start Time</th>
                        <th>End Time</th>
                        <th>Client</th>
                        <th>Project</th>
                        <th>Task</th>
                        <th>Duration</th>
                        <th>Activity</th>
                        <th>Billed Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in entries %}
                    <tr id="entry-{{ loop.index }}" {% if item.screenshots %}class="clickable" onclick="location.href='#screenshots-{{ loop.index }}'"{% endif %}>
                        <td>{{ item.entry.entry.start_time.strftime('%Y-%m-%d %H:%M') if item.entry.entry.start_time else '' }}</td>
                        <td>{{ item.entry.entry.end_time.strftime('%Y-%m-%d %H:%M') if item.entry.entry.end_time else '' }}</td>
                        <td>{{ item.entry.client_name }}</td>
                        <td>{{ item.entry.project_name }}</td>
                        <td{% if item.screenshots %} class="has-screenshots"{% endif %}>
                            {{ item.entry.task_name }}
                            {% if item.entry.entry.is_manual %}
                            <span class="badge badge-manual">Manual</span>
                            {% endif %}
                        </td>
                        <td>{{ item.entry.entry.duration_formatted }}</td>
                        <td>
                            <span class="activity-bar">
                                <span class="activity-bar-fill {% if item.entry.entry.activity_percentage >= 70 %}activity-high{% elif item.entry.entry.activity_percentage >= 40 %}activity-medium{% else %}activity-low{% endif %}"
                                      style="width: {{ item.entry.entry.activity_percentage }}%"></span>
                            </span>
                            {{ "%.0f"|format(item.entry.entry.activity_percentage) }}%
                        </td>
                        <td>${{ "%.2f"|format(item.entry.earnings) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        {% for item in entries %}
        {% if item.screenshots %}
        <div class="section" id="screenshots-{{ loop.index }}">
            <div class="entry-header">
                <div>
                    <div class="entry-title">{{ item.entry.client_name }} / {{ item.entry.project_name }} / {{ item.entry.task_name }}</div>
                    <div class="entry-meta">{{ item.entry.entry.start_time.strftime('%Y-%m-%d %H:%M') if item.entry.entry.start_time else '' }} - {{ item.entry.entry.end_time.strftime('%H:%M') if item.entry.entry.end_time else '' }} | {{ item.entry.entry.duration_formatted }} | {{ "%.0f"|format(item.entry.entry.activity_percentage) }}% activity</div>
                </div>
                <a href="#entry-{{ loop.index }}" class="back-link">↑ Back to Details</a>
            </div>
            <div class="screenshots">
                {% for screenshot in item.screenshots %}
                <div class="screenshot">
                    <img src="{{ screenshot.data }}" alt="Screenshot">
                    <div class="info">{{ screenshot.time }} | {{ "%.0f"|format(screenshot.activity) }}% activity</div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        {% endfor %}

        {% if payment_details %}
        <div class="payment-info">
            <h3>Payment Information</h3>
            <p>{{ payment_details }}</p>
        </div>
        {% endif %}

        <footer>
            Generated by Desktop Time Tracker
        </footer>
    </div>
</body>
</html>
'''
