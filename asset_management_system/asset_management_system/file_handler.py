"""File handling: activity log, CSV/TXT reports and JSON backups."""
import csv
import json
import os
from datetime import datetime
import config


class FileManager:
    def __init__(self):
        for folder in (config.REPORTS_DIR, config.LOGS_DIR, config.BACKUP_DIR):
            os.makedirs(folder, exist_ok=True)

    @staticmethod
    def _stamp():
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def log(self, message):
        with open(config.LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {message}\n")

    def read_log(self, last=20):
        if not os.path.exists(config.LOG_FILE):
            return []
        with open(config.LOG_FILE, encoding="utf-8") as f:
            return f.read().splitlines()[-last:]

    def export_assets_csv(self, rows):
        path = os.path.join(config.REPORTS_DIR, f"assets_{self._stamp()}.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        return path

    def export_assignment_report(self, rows):
        path = os.path.join(config.REPORTS_DIR, f"assignments_{self._stamp()}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("ASSET ASSIGNMENT REPORT\n" + "=" * 60 + "\n")
            for r in rows:
                returned = r["return_date"] or "still with employee"
                f.write(f"{r['asset_name']} -> {r['employee_name']} "
                        f"({r['department']})\n   issued {r['issue_date']}, "
                        f"returned: {returned}\n")
        return path

    def backup(self, tables):
        """tables: dict of table name -> list of row dicts."""
        path = os.path.join(config.BACKUP_DIR, f"backup_{self._stamp()}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tables, f, indent=2, default=str)
        return path
