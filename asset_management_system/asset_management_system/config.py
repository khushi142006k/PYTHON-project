"""Settings for the Asset Management System.
Edit the values below, or set them as environment variables."""
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")      # put your MySQL password here
DB_NAME = os.getenv("DB_NAME", "asset_db")      # created automatically

# Folders for file handling (created automatically)
REPORTS_DIR = "reports"
LOGS_DIR = "logs"
BACKUP_DIR = "backups"
LOG_FILE = os.path.join(LOGS_DIR, "activity.log")
