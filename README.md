# PYTHON-project
# Asset Management System (Python + MySQL)

Uses **OOP** (models.py, manager.py), **MySQL** (database.py) and **File Handling** (file_handler.py).

## Run in VS Code
1. Install Python 3.9+ and MySQL Server (make sure it is running).
2. Open this folder in VS Code (File > Open Folder).
3. Open the terminal (Ctrl + `) and run:
   ```
   pip install -r requirements.txt
   python main.py
   ```
   (or press F5 to run with the included launch config)
4. The database `asset_db` and all tables are created automatically.
   If your MySQL root user has a password, either type it when asked
   or set `DB_PASSWORD` in `config.py`.

## Files created while running
- `reports/` CSV asset report and TXT assignment report
- `logs/activity.log` every action with a timestamp
- `backups/` JSON backup of all tables

## Structure
| File | Purpose |
|---|---|
| main.py | Menu and user input |
| manager.py | AssetManager: business logic |
| models.py | Asset, ElectronicAsset, FurnitureAsset, VehicleAsset, Employee |
| database.py | MySQL connection, schema, queries |
| file_handler.py | Logs, reports, backups |
| config.py | DB settings and folder names |
