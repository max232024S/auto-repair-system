# Auto Repair & Vehicle Maintenance Tracker

Flask + MySQL app for tracking customers, vehicles, appointments, repair orders, parts, and invoices.

## Local setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
cp .env.example .env           # then fill in your MySQL credentials
```

Create the database in MySQL Workbench (or the CLI):

```sql
CREATE DATABASE auto_repair;
USE auto_repair;
SOURCE sql/schema.sql;
SOURCE sql/seed.sql;
```

Run it:

```bash
python app.py
```

Then open http://localhost:5000 and check http://localhost:5000/health. It should say `"database": "connected"`.

## Deploying to Railway

1. Create a project with a MySQL service and a service from this GitHub repo.
2. On the Flask service, add variables referencing the MySQL service: `DB_HOST=${{MySQL.MYSQLHOST}}`, `DB_PORT=${{MySQL.MYSQLPORT}}`, `DB_USER=${{MySQL.MYSQLUSER}}`, `DB_PASSWORD=${{MySQL.MYSQLPASSWORD}}`, `DB_NAME=${{MySQL.MYSQLDATABASE}}`, plus a real `SECRET_KEY`.
3. Railway picks up the `Procfile` and runs Gunicorn.
4. Load schema.sql into the Railway MySQL instance (connect from Workbench using the public connection details).
5. Hit `/health` on the deployed URL to confirm.

## Project layout

```
app.py              Flask app, routes, error handlers
db.py               Connection pool + query/execute/transaction helpers
templates/          Jinja2 templates (base.html is the layout)
static/css, js      Styles and scripts
sql/                schema.sql and seed.sql
Procfile            Gunicorn start command for Railway
```

## AI use disclosure

- Project skeleton (app.py, db.py, templates, config files, this README) generated with Claude Code, then reviewed by the team.
