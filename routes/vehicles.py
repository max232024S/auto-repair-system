import mysql.connector
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

import db
from validation import validate_vehicle

bp = Blueprint("vehicles", __name__, url_prefix="/vehicles")


def _get_vehicle(vehicle_id):
    vehicle = db.query(
        """SELECT v.*, c.first_name, c.last_name
           FROM Vehicle AS v
           JOIN Customer AS c ON c.customer_id = v.customer_id
           WHERE v.vehicle_id = %s""",
        (vehicle_id,),
        one=True,
    )
    if vehicle is None:
        abort(404)
    return vehicle


def _customer_options():
    """(value, label) pairs for the owner dropdown."""
    rows = db.query(
        "SELECT customer_id, first_name, last_name, email FROM Customer ORDER BY last_name, first_name"
    )
    return [(r["customer_id"], f"{r['last_name']}, {r['first_name']} ({r['email']})") for r in rows]


@bp.route("/")
def index():
    vehicles = db.query(
        """SELECT v.vehicle_id, v.vin, v.make, v.model, v.year, v.mileage,
                  c.customer_id, c.first_name, c.last_name
           FROM Vehicle AS v
           JOIN Customer AS c ON c.customer_id = v.customer_id
           ORDER BY c.last_name, c.first_name, v.year DESC"""
    )
    return render_template("vehicles/index.html", vehicles=vehicles)


@bp.route("/<int:vehicle_id>")
def detail(vehicle_id):
    vehicle = _get_vehicle(vehicle_id)
    repairs = db.query(
        """SELECT repair_id, description, repair_date, cost, status
           FROM Repair WHERE vehicle_id = %s
           ORDER BY repair_date DESC, repair_id DESC""",
        (vehicle_id,),
    )
    completed_total = sum(r["cost"] for r in repairs if r["status"] == "Completed")
    return render_template(
        "vehicles/detail.html", vehicle=vehicle, repairs=repairs, completed_total=completed_total
    )


@bp.route("/new", methods=["GET", "POST"])
def create():
    # ?customer_id=3 pre-selects the owner when coming from a customer's page
    values, errors = {"customer_id": request.args.get("customer_id")}, {}
    if request.method == "POST":
        values, errors = validate_vehicle(request.form)
        if not errors:
            try:
                new_id = db.execute(
                    """INSERT INTO Vehicle (customer_id, vin, make, model, year, mileage)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (values["customer_id"], values["vin"], values["make"], values["model"],
                     values["year"], values["mileage"]),
                )
            except mysql.connector.Error as err:
                field, msg = db.describe_error(err)
                errors[field or "_form"] = msg
            else:
                flash("Vehicle added.", "success")
                return redirect(url_for(".detail", vehicle_id=new_id))
    return render_template(
        "vehicles/form.html", title="New vehicle", values=values, errors=errors,
        customers=_customer_options(), cancel_url=url_for(".index"),
    ), (400 if errors else 200)


@bp.route("/<int:vehicle_id>/edit", methods=["GET", "POST"])
def edit(vehicle_id):
    values, errors = _get_vehicle(vehicle_id), {}
    if request.method == "POST":
        values, errors = validate_vehicle(request.form)
        if not errors:
            try:
                db.execute(
                    """UPDATE Vehicle
                       SET customer_id = %s, vin = %s, make = %s, model = %s, year = %s, mileage = %s
                       WHERE vehicle_id = %s""",
                    (values["customer_id"], values["vin"], values["make"], values["model"],
                     values["year"], values["mileage"], vehicle_id),
                )
            except mysql.connector.Error as err:
                field, msg = db.describe_error(err)
                errors[field or "_form"] = msg
            else:
                flash("Vehicle updated.", "success")
                return redirect(url_for(".detail", vehicle_id=vehicle_id))
    return render_template(
        "vehicles/form.html", title="Edit vehicle", values=values, errors=errors,
        customers=_customer_options(), cancel_url=url_for(".detail", vehicle_id=vehicle_id),
    ), (400 if errors else 200)


@bp.route("/<int:vehicle_id>/delete", methods=["POST"])
def delete(vehicle_id):
    vehicle = _get_vehicle(vehicle_id)
    try:
        db.execute("DELETE FROM Vehicle WHERE vehicle_id = %s", (vehicle_id,))
    except mysql.connector.Error as err:
        _, msg = db.describe_error(err)
        flash(msg, "error")
        return redirect(url_for(".detail", vehicle_id=vehicle_id))
    flash("Vehicle deleted.", "success")
    return redirect(url_for("customers.detail", customer_id=vehicle["customer_id"]))
