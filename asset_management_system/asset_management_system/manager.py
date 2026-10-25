"""AssetManager: business logic joining the models, MySQL and files."""
from datetime import date
from models import Asset, Employee, CATEGORY_CLASSES


class AssetManager:
    def __init__(self, db, files):
        self.db, self.files = db, files

    # ---- assets ----
    def add_asset(self, name, category, purchase_date, cost):
        cls = CATEGORY_CLASSES.get(category, Asset)
        asset = cls(name, purchase_date, cost)          # validates cost
        asset_id = self.db.execute(
            "INSERT INTO assets (name, category, purchase_date, cost) VALUES (%s,%s,%s,%s)",
            (asset.name, asset.category, asset.purchase_date, asset.cost))
        self.files.log(f"ADD ASSET id={asset_id} name={name}")
        return asset_id

    def list_assets(self, keyword=None):
        sql, params = "SELECT * FROM assets", ()
        if keyword:
            like = f"%{keyword}%"
            sql += " WHERE name LIKE %s OR category LIKE %s OR status LIKE %s"
            params = (like, like, like)
        rows = self.db.fetch_all(sql + " ORDER BY asset_id", params)
        return [Asset.from_row(r) for r in rows]

    def get_asset(self, asset_id):
        rows = self.db.fetch_all("SELECT * FROM assets WHERE asset_id=%s", (asset_id,))
        return Asset.from_row(rows[0]) if rows else None

    def update_status(self, asset_id, status):
        self.db.execute("UPDATE assets SET status=%s WHERE asset_id=%s", (status, asset_id))
        self.files.log(f"STATUS asset={asset_id} -> {status}")

    def delete_asset(self, asset_id):
        self.db.execute("DELETE FROM assets WHERE asset_id=%s", (asset_id,))
        self.files.log(f"DELETE ASSET id={asset_id}")

    # ---- employees ----
    def add_employee(self, name, department, email):
        emp = Employee(name, department, email)          # validates email
        emp_id = self.db.execute(
            "INSERT INTO employees (name, department, email) VALUES (%s,%s,%s)",
            (emp.name, emp.department, emp.email))
        self.files.log(f"ADD EMPLOYEE id={emp_id} name={name}")
        return emp_id

    def list_employees(self):
        return self.db.fetch_all("SELECT * FROM employees ORDER BY emp_id")

    # ---- issue / return ----
    def issue_asset(self, asset_id, emp_id):
        asset = self.get_asset(asset_id)
        if asset is None:
            raise ValueError("No asset with that ID.")
        if asset.status != "Available":
            raise ValueError(f"Asset is not available (status: {asset.status}).")
        if not self.db.fetch_all("SELECT 1 FROM employees WHERE emp_id=%s", (emp_id,)):
            raise ValueError("No employee with that ID.")
        self.db.transaction([
            ("INSERT INTO assignments (asset_id, emp_id, issue_date) VALUES (%s,%s,%s)",
             (asset_id, emp_id, date.today())),
            ("UPDATE assets SET status='Assigned' WHERE asset_id=%s", (asset_id,)),
        ])
        self.files.log(f"ISSUE asset={asset_id} to emp={emp_id}")

    def return_asset(self, asset_id):
        open_rows = self.db.fetch_all(
            "SELECT assign_id FROM assignments WHERE asset_id=%s AND return_date IS NULL",
            (asset_id,))
        if not open_rows:
            raise ValueError("This asset is not currently issued.")
        self.db.transaction([
            ("UPDATE assignments SET return_date=%s WHERE assign_id=%s",
             (date.today(), open_rows[0]["assign_id"])),
            ("UPDATE assets SET status='Available' WHERE asset_id=%s", (asset_id,)),
        ])
        self.files.log(f"RETURN asset={asset_id}")

    def assignment_history(self, asset_id=None):
        sql = """SELECT a.assign_id, s.name AS asset_name, e.name AS employee_name,
                        e.department, a.issue_date, a.return_date
                 FROM assignments a
                 JOIN assets s ON s.asset_id = a.asset_id
                 JOIN employees e ON e.emp_id = a.emp_id"""
        params = ()
        if asset_id:
            sql += " WHERE a.asset_id=%s"
            params = (asset_id,)
        return self.db.fetch_all(sql + " ORDER BY a.assign_id", params)

    # ---- file features ----
    def export_assets(self):
        rows = [a.to_row() for a in self.list_assets()]
        if not rows:
            raise ValueError("No assets to export.")
        path = self.files.export_assets_csv(rows)
        self.files.log(f"EXPORT CSV {path}")
        return path

    def export_assignments(self):
        rows = self.assignment_history()
        if not rows:
            raise ValueError("No assignments to export.")
        path = self.files.export_assignment_report(rows)
        self.files.log(f"EXPORT REPORT {path}")
        return path

    def backup(self):
        data = {t: self.db.fetch_all(f"SELECT * FROM {t}")
                for t in ("assets", "employees", "assignments")}
        path = self.files.backup(data)
        self.files.log(f"BACKUP {path}")
        return path
