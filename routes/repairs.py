from datetime import date

import mysql.connector
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

import db
from validation import REPAIR_STATUSES, validate_repair

bp = Blueprint("repairs", __name__, url_prefix="/repairs")


def _get_repair(repair_id):
    repair = db.query("SELECT * FROM Repair WHERE repair_id = %s", (repair_id,), one=True)
    if repair is None:
        abort(404)
    return repair


def _vehicle_options():
    """(value, label) pairs for the vehicle dropdown."""
    rows = db.query(
        """SELECT v.vehicle_id, v.year, v.make, v.model, v.vin, c.first_name, c.last_name
           FROM Vehicle AS v
           JOIN Customer AS c ON c.customer_id = v.customer_id
           ORDER BY c.last_name, c.first_name, v.year DESC"""
    )
    return [
        (r["vehicle_id"], f"{r['year']} {r['make']} {r['model']} ({r['vin']}) - {r['first_name']} {r['last_name']}")
        for r in rows
    ]


def _render_form(title, values, errors, cancel_url):
    return render_template(
        "repairs/form.html", title=title, values=values, errors=errors,
        vehicles=_vehicle_options(), statuses=REPAIR_STATUSES, cancel_url=cancel_url,
    ), (400 if errors else 200)


@bp.route("/")
def index():
    # Optional ?status=Pending filter
    status = request.args.get("status")
    sql = """SELECT r.repair_id, r.description, r.repair_date, r.cost, r.status,
                    v.vehicle_id, v.year, v.make, v.model,
                    c.customer_id, c.first_name, c.last_name
             FROM Repair AS r
             JOIN Vehicle AS v ON v.vehicle_id = r.vehicle_id
             JOIN Customer AS c ON c.customer_id = v.customer_id"""
    params = ()
    if status in REPAIR_STATUSES:
        sql += " WHERE r.status = %s"
        params = (status,)
    sql += " ORDER BY r.repair_date DESC, r.repair_id DESC"
    repairs = db.query(sql, params)
    return render_template(
        "repairs/index.html", repairs=repairs, statuses=REPAIR_STATUSES, current_status=status
    )


@bp.route("/new", methods=["GET", "POST"])
def create():
    values = {
        "vehicle_id": request.args.get("vehicle_id"),
        "repair_date": date.today().isoformat(),
        "status": "Pending",
    }
    errors = {}
    if request.method == "POST":
        values, errors = validate_repair(request.form)
        if not errors:
            try:
                db.execute(
                    """INSERT INTO Repair (vehicle_id, description, repair_date, cost, status)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (values["vehicle_id"], values["description"], values["repair_date"],
                     values["cost"], values["status"]),
                )
            except mysql.connector.Error as err:
                field, msg = db.describe_error(err)
                errors[field or "_form"] = msg
            else:
                flash("Repair added.", "success")
                return redirect(url_for("vehicles.detail", vehicle_id=values["vehicle_id"]))
    return _render_form("New repair", values, errors, url_for(".index"))


@bp.route("/<int:repair_id>/edit", methods=["GET", "POST"])
def edit(repair_id):
    repair = _get_repair(repair_id)
    values, errors = repair, {}
    if request.method == "POST":
        values, errors = validate_repair(request.form)
        if not errors:
            try:
                db.execute(
                    """UPDATE Repair
                       SET vehicle_id = %s, description = %s, repair_date = %s, cost = %s, status = %s
                       WHERE repair_id = %s""",
                    (values["vehicle_id"], values["description"], values["repair_date"],
                     values["cost"], values["status"], repair_id),
                )
            except mysql.connector.Error as err:
                field, msg = db.describe_error(err)
                errors[field or "_form"] = msg
            else:
                flash("Repair updated.", "success")
                return redirect(url_for("vehicles.detail", vehicle_id=values["vehicle_id"]))
    return _render_form("Edit repair", values, errors,
                        url_for("vehicles.detail", vehicle_id=repair["vehicle_id"]))


@bp.route("/<int:repair_id>/delete", methods=["POST"])
def delete(repair_id):
    repair = _get_repair(repair_id)
    db.execute("DELETE FROM Repair WHERE repair_id = %s", (repair_id,))
    flash("Repair deleted.", "success")
    return redirect(url_for("vehicles.detail", vehicle_id=repair["vehicle_id"]))
