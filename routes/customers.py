import mysql.connector
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

import db
from validation import validate_customer

bp = Blueprint("customers", __name__, url_prefix="/customers")


def _get_customer(customer_id):
    customer = db.query("SELECT * FROM Customer WHERE customer_id = %s", (customer_id,), one=True)
    if customer is None:
        abort(404)
    return customer


@bp.route("/")
def index():
    customers = db.query(
        """SELECT c.customer_id, c.first_name, c.last_name, c.email, c.phone,
                  COUNT(v.vehicle_id) AS vehicle_count
           FROM Customer AS c
           LEFT JOIN Vehicle AS v ON v.customer_id = c.customer_id
           GROUP BY c.customer_id, c.first_name, c.last_name, c.email, c.phone
           ORDER BY c.last_name, c.first_name"""
    )
    return render_template("customers/index.html", customers=customers)


@bp.route("/<int:customer_id>")
def detail(customer_id):
    customer = _get_customer(customer_id)
    vehicles = db.query(
        """SELECT vehicle_id, vin, make, model, year, mileage
           FROM Vehicle WHERE customer_id = %s
           ORDER BY year DESC""",
        (customer_id,),
    )
    return render_template("customers/detail.html", customer=customer, vehicles=vehicles)


@bp.route("/new", methods=["GET", "POST"])
def create():
    values, errors = {}, {}
    if request.method == "POST":
        values, errors = validate_customer(request.form)
        if not errors:
            try:
                new_id = db.execute(
                    """INSERT INTO Customer (first_name, last_name, email, phone)
                       VALUES (%s, %s, %s, %s)""",
                    (values["first_name"], values["last_name"], values["email"], values["phone"]),
                )
            except mysql.connector.Error as err:
                field, msg = db.describe_error(err)
                errors[field or "_form"] = msg
            else:
                flash("Customer added.", "success")
                return redirect(url_for(".detail", customer_id=new_id))
    return render_template(
        "customers/form.html", title="New customer", values=values, errors=errors,
        cancel_url=url_for(".index"),
    ), (400 if errors else 200)


@bp.route("/<int:customer_id>/edit", methods=["GET", "POST"])
def edit(customer_id):
    values, errors = _get_customer(customer_id), {}
    if request.method == "POST":
        values, errors = validate_customer(request.form)
        if not errors:
            try:
                db.execute(
                    """UPDATE Customer
                       SET first_name = %s, last_name = %s, email = %s, phone = %s
                       WHERE customer_id = %s""",
                    (values["first_name"], values["last_name"], values["email"], values["phone"], customer_id),
                )
            except mysql.connector.Error as err:
                field, msg = db.describe_error(err)
                errors[field or "_form"] = msg
            else:
                flash("Customer updated.", "success")
                return redirect(url_for(".detail", customer_id=customer_id))
    return render_template(
        "customers/form.html", title="Edit customer", values=values, errors=errors,
        cancel_url=url_for(".detail", customer_id=customer_id),
    ), (400 if errors else 200)


@bp.route("/<int:customer_id>/delete", methods=["POST"])
def delete(customer_id):
    _get_customer(customer_id)
    try:
        db.execute("DELETE FROM Customer WHERE customer_id = %s", (customer_id,))
    except mysql.connector.Error as err:
        _, msg = db.describe_error(err)
        flash(msg, "error")
        return redirect(url_for(".detail", customer_id=customer_id))
    flash("Customer deleted.", "success")
    return redirect(url_for(".index"))
