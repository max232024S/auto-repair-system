"""Form validation for each table.

Each validate_* function takes request.form and returns (values, errors):
- values: cleaned data ready to pass to SQL (invalid fields keep the raw input
  so the form can be re-shown with what the user typed)
- errors: {field_name: message}; empty means the input is valid

These mirror the constraints in sql/schema.sql so users get a readable message
instead of a raw MySQL error. The DB constraints are still the final safety net.
"""
import re
from datetime import date
from decimal import Decimal, InvalidOperation

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
# Real VINs are 17 chars and never use I, O, or Q
VIN_RE = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")
REPAIR_STATUSES = ("Pending", "In Progress", "Completed")


def _text(form, name, label, max_len, errors, required=True):
    value = (form.get(name) or "").strip()
    if not value:
        if required:
            errors[name] = f"{label} is required."
            return ""
        return None  # store optional blanks as NULL
    if len(value) > max_len:
        errors[name] = f"{label} must be {max_len} characters or fewer."
    return value


def _int(form, name, label, errors, min_value=None, max_value=None, required=True):
    raw = (form.get(name) or "").strip()
    if not raw:
        if required:
            errors[name] = f"{label} is required."
        return None
    try:
        value = int(raw)
    except ValueError:
        errors[name] = f"{label} must be a whole number."
        return raw
    if min_value is not None and value < min_value:
        errors[name] = f"{label} must be at least {min_value}."
    elif max_value is not None and value > max_value:
        errors[name] = f"{label} must be at most {max_value}."
    return value


def validate_customer(form):
    errors = {}
    values = {
        "first_name": _text(form, "first_name", "First name", 50, errors),
        "last_name": _text(form, "last_name", "Last name", 50, errors),
        "email": _text(form, "email", "Email", 100, errors),
        "phone": _text(form, "phone", "Phone", 20, errors, required=False),
    }
    if values["email"] and "email" not in errors:
        values["email"] = values["email"].lower()
        if not EMAIL_RE.match(values["email"]):
            errors["email"] = "Enter a valid email address."
    return values, errors


def validate_vehicle(form):
    errors = {}
    values = {
        "customer_id": _int(form, "customer_id", "Owner", errors, min_value=1),
        "vin": _text(form, "vin", "VIN", 17, errors),
        "make": _text(form, "make", "Make", 50, errors),
        "model": _text(form, "model", "Model", 50, errors),
        "year": _int(form, "year", "Year", errors, min_value=1886, max_value=date.today().year + 1),
        "mileage": _int(form, "mileage", "Mileage", errors, min_value=0, required=False),
    }
    if values["vin"] and "vin" not in errors:
        values["vin"] = values["vin"].upper()
        if not VIN_RE.match(values["vin"]):
            errors["vin"] = "VIN must be exactly 17 letters/digits (no I, O, or Q)."
    if values["mileage"] is None:
        values["mileage"] = 0
    return values, errors


def validate_repair(form):
    errors = {}
    values = {
        "vehicle_id": _int(form, "vehicle_id", "Vehicle", errors, min_value=1),
        "description": _text(form, "description", "Description", 255, errors),
        "repair_date": (form.get("repair_date") or "").strip(),
        "cost": (form.get("cost") or "").strip(),
        "status": (form.get("status") or "Pending").strip(),
    }

    if not values["repair_date"]:
        errors["repair_date"] = "Repair date is required."
    else:
        try:
            values["repair_date"] = date.fromisoformat(values["repair_date"])
        except ValueError:
            errors["repair_date"] = "Enter a valid date (YYYY-MM-DD)."

    if not values["cost"]:
        errors["cost"] = "Cost is required."
    else:
        try:
            cost = Decimal(values["cost"])
            if not cost.is_finite() or cost < 0:
                errors["cost"] = "Cost must be 0 or more."
            elif cost.as_tuple().exponent < -2:
                errors["cost"] = "Cost can have at most 2 decimal places."
            elif cost >= Decimal("100000000"):  # DECIMAL(10,2) limit
                errors["cost"] = "Cost is too large."
            else:
                values["cost"] = cost
        except InvalidOperation:
            errors["cost"] = "Cost must be a number."

    if values["status"] not in REPAIR_STATUSES:
        errors["status"] = "Pick a valid status."
    return values, errors
