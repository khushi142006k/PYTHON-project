"""MySQL connection layer. Creates the database and tables automatically."""
import mysql.connector
import config

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS assets (
        asset_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        category VARCHAR(50) NOT NULL,
        purchase_date DATE NOT NULL,
        cost DECIMAL(12,2) NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'Available'
    )""",
    """CREATE TABLE IF NOT EXISTS employees (
        emp_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        department VARCHAR(100) NOT NULL,
        email VARCHAR(120) NOT NULL UNIQUE
    )""",
    """CREATE TABLE IF NOT EXISTS assignments (
        assign_id INT AUTO_INCREMENT PRIMARY KEY,
        asset_id INT NOT NULL,
        emp_id INT NOT NULL,
        issue_date DATE NOT NULL,
        return_date DATE NULL,
        FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
        FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
    )""",
]


class Database:
    def __init__(self, password=None):
        self.password = config.DB_PASSWORD if password is None else password
        self.conn = None

    def connect(self):
        server = mysql.connector.connect(
            host=config.DB_HOST, port=config.DB_PORT,
            user=config.DB_USER, password=self.password)
        cur = server.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}`")
        server.close()
        self.conn = mysql.connector.connect(
            host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER,
            password=self.password, database=config.DB_NAME)
        cur = self.conn.cursor()
        for statement in SCHEMA:
            cur.execute(statement)
        self.conn.commit()

    def fetch_all(self, sql, params=()):
        cur = self.conn.cursor(dictionary=True)
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        return rows

    def execute(self, sql, params=()):
        """Run one INSERT/UPDATE/DELETE. Returns the new row id."""
        return self.transaction([(sql, params)])

    def transaction(self, statements):
        """Run several statements together; all succeed or none do."""
        cur = self.conn.cursor()
        try:
            for sql, params in statements:
                cur.execute(sql, params)
            self.conn.commit()
            return cur.lastrowid
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def close(self):
        if self.conn:
            self.conn.close()
