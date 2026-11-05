import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template

load_dotenv()  # no-op on Railway if there's no .env file

import db  # noqa: E402  (import after env is loaded)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-change-me")
logging.basicConfig(level=logging.INFO)


@app.route("/")
def index():
    return render_template("index.html")


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
