"""OOP models: Asset (with subclasses), Employee."""
from datetime import date


class Asset:
    """Base class. Subclasses change the yearly depreciation rate."""
    CATEGORY = "Other"
    DEPRECIATION_RATE = 0.15

    def __init__(self, name, purchase_date, cost, asset_id=None, status="Available"):
        self.asset_id = asset_id
        self.name = name
        self.purchase_date = purchase_date
        self.cost = cost            # goes through the property setter
        self.status = status

    @property
    def cost(self):
        return self._cost

    @cost.setter
    def cost(self, value):          # encapsulation: validate before storing
        value = float(value)
        if value < 0:
            raise ValueError("Cost cannot be negative.")
        self._cost = value

    @property
    def category(self):
        return self.CATEGORY

    def current_value(self):
        """Straight-line depreciation, never below 10% of cost."""
        years = (date.today() - self.purchase_date).days / 365
        value = self._cost * (1 - self.DEPRECIATION_RATE * years)
        return round(max(value, self._cost * 0.10), 2)

    def to_row(self):
        return {"ID": self.asset_id, "Name": self.name, "Category": self.category,
                "Purchased": self.purchase_date, "Cost": f"{self._cost:.2f}",
                "Value now": f"{self.current_value():.2f}", "Status": self.status}

    def __str__(self):
        return f"{self.name} ({self.category}, {self.status})"

    @staticmethod
    def from_row(row):
        """Factory: build the right subclass from a database row."""
        cls = CATEGORY_CLASSES.get(row["category"], Asset)
        return cls(row["name"], row["purchase_date"], row["cost"],
                   asset_id=row["asset_id"], status=row["status"])


class ElectronicAsset(Asset):
    CATEGORY = "Electronics"
    DEPRECIATION_RATE = 0.25


class FurnitureAsset(Asset):
    CATEGORY = "Furniture"
    DEPRECIATION_RATE = 0.10


class VehicleAsset(Asset):
    CATEGORY = "Vehicle"
    DEPRECIATION_RATE = 0.15


CATEGORY_CLASSES = {c.CATEGORY: c for c in (ElectronicAsset, FurnitureAsset, VehicleAsset)}
CATEGORY_CLASSES["Other"] = Asset


class Employee:
    def __init__(self, name, department, email, emp_id=None):
        if "@" not in email:
            raise ValueError("Enter a valid email address.")
        self.emp_id, self.name = emp_id, name
        self.department, self.email = department, email
