"""Asset Management System - run this file (python main.py)."""
from datetime import date, datetime
from getpass import getpass
import mysql.connector

from database import Database
from file_handler import FileManager
from manager import AssetManager

CATEGORIES = ["Electronics", "Furniture", "Vehicle", "Other"]
STATUSES = ["Available", "Assigned", "Under Repair", "Retired"]


def show(rows, headers=None):
    if not rows:
        print("  (nothing to show)")
        return
    headers = headers or list(rows[0].keys())
    widths = [max(len(str(h)), *(len(str(r[h])) for r in rows)) for h in headers]
    line = " | ".join(str(h).ljust(w) for h, w in zip(headers, widths))
    print("\n" + line + "\n" + "-" * len(line))
    for r in rows:
        print(" | ".join(str(r[h]).ljust(w) for h, w in zip(headers, widths)))
    print()


def ask(prompt):
    value = input(prompt).strip()
    if not value:
        raise ValueError("This field cannot be empty.")
    return value


def ask_int(prompt):
    try:
        return int(ask(prompt))
    except ValueError:
        raise ValueError("Please enter a whole number.")


def ask_choice(title, options):
    for i, o in enumerate(options, 1):
        print(f"  {i}. {o}")
    n = ask_int(f"{title}: ")
    if not 1 <= n <= len(options):
        raise ValueError("Choice out of range.")
    return options[n - 1]


def ask_date(prompt):
    text = input(prompt + " (YYYY-MM-DD, Enter = today): ").strip()
    return date.today() if not text else datetime.strptime(text, "%Y-%m-%d").date()


def connect():
    db = Database()
    try:
        db.connect()
    except mysql.connector.Error as err:
        if err.errno == 1045:                      # wrong / missing password
            print("MySQL needs a password for user 'root' (or edit config.py).")
            db = Database(getpass("MySQL password: "))
            db.connect()
        else:
            raise
    return db


def menu(m):
    print("""
===== ASSET MANAGEMENT SYSTEM =====
 1 Add asset            8 Issue asset
 2 View all assets      9 Return asset
 3 Search assets       10 Assignment history
 4 Update status       11 Export assets (CSV)
 5 Delete asset        12 Export assignment report
 6 Add employee        13 Backup data (JSON)
 7 View employees      14 View activity log
 0 Exit""")
    c = input("Choose: ").strip()
    if c == "1":
        name = ask("Asset name: ")
        category = ask_choice("Category", CATEGORIES)
        pdate = ask_date("Purchase date")
        cost = float(ask("Cost: "))
        print("Added asset with ID", m.add_asset(name, category, pdate, cost))
    elif c == "2":
        show([a.to_row() for a in m.list_assets()])
    elif c == "3":
        show([a.to_row() for a in m.list_assets(ask("Search keyword: "))])
    elif c == "4":
        m.update_status(ask_int("Asset ID: "), ask_choice("New status", STATUSES))
        print("Status updated.")
    elif c == "5":
        m.delete_asset(ask_int("Asset ID to delete: "))
        print("Asset deleted.")
    elif c == "6":
        print("Added employee with ID",
              m.add_employee(ask("Name: "), ask("Department: "), ask("Email: ")))
    elif c == "7":
        show(m.list_employees())
    elif c == "8":
        m.issue_asset(ask_int("Asset ID: "), ask_int("Employee ID: "))
        print("Asset issued.")
    elif c == "9":
        m.return_asset(ask_int("Asset ID: "))
        print("Asset returned.")
    elif c == "10":
        raw = input("Asset ID (Enter = all): ").strip()
        show(m.assignment_history(int(raw) if raw else None))
    elif c == "11":
        print("Saved:", m.export_assets())
    elif c == "12":
        print("Saved:", m.export_assignments())
    elif c == "13":
        print("Backup saved:", m.backup())
    elif c == "14":
        print("\n".join(m.files.read_log()) or "(log is empty)")
    elif c == "0":
        return False
    else:
        print("Invalid option.")
    return True


def main():
    try:
        db = connect()
    except mysql.connector.Error as err:
        print(f"\nCould not connect to MySQL: {err}")
        print("Make sure MySQL is running and config.py has the right user/password.")
        return
    manager = AssetManager(db, FileManager())
    print("Connected to MySQL.")
    running = True
    while running:
        try:
            running = menu(manager)
        except (ValueError, mysql.connector.Error) as err:
            print(f"\n  Error: {err}")
    db.close()
    print("Goodbye!")


if __name__ == "__main__":
    main()
