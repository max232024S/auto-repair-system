import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template

# override=True so .env wins over stale vars already in the terminal
# (VS Code's python.terminal.useEnvFile injects .env when a terminal opens).
# No-op on Railway since there's no .env file there.
load_dotenv(override=True)

import db  # noqa: E402  (import after env is loaded)
from routes import customers, repairs, vehicles  # noqa: E402

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-change-me")
logging.basicConfig(level=logging.INFO)

app.register_blueprint(customers.bp)
app.register_blueprint(vehicles.bp)
app.register_blueprint(repairs.bp)


@app.template_filter("money")
def money(value):
    return f"${value:,.2f}" if value is not None else ""


@app.route("/")
def index():
    counts = db.query(
        """SELECT (SELECT COUNT(*) FROM Customer) AS customers,
                  (SELECT COUNT(*) FROM Vehicle) AS vehicles,
                  (SELECT COUNT(*) FROM Repair WHERE status <> 'Completed') AS open_repairs""",
        one=True,
    )
    return render_template("index.html", counts=counts)


@app.route("/health")
def health():
    """Quick check that the app is up and can reach MySQL. Handy right after a deploy."""
    try:
        db.query("SELECT 1 AS ok", one=True)
        return jsonify(status="ok", database="connected")
    except Exception as e:
        app.logger.exception("Health check DB failure")
        return jsonify(status="error", database=str(e)), 500


@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("errors/500.html"), 500


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1", port=int(os.getenv("PORT", "5000")))
