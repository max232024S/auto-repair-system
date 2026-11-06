# Auto Repair & Vehicle Maintenance Tracker

Flask + MySQL app for tracking customers, vehicles, appointments, repair orders, parts, and invoices.

## Local setup

MySQL 8.0.16+ is recommended. The initial Sprint 1 SQL files implement the
**Customer**, **Vehicle**, and **Repair** tables. Confirm these definitions match
your team's finalized relational schema before treating them as final.

1. Create a Python virtual environment and install dependencies:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

On Mac/Linux, use `source venv/bin/activate` and `cp .env.example .env`.

2. Start MySQL and **for a NEW database only**, from the MySQL command-line
client while located in the repository root, run:

```sql
SOURCE sql/schema.sql;
SOURCE sql/seed.sql;
```

`schema.sql` creates `auto_repair_db` if needed. `seed.sql` is only for an
**empty** database; it has fixed identifiers and intentionally fails on
existing duplicate test data. If you've already built/populated your database,
**do not rerun `seed.sql`**. `CREATE TABLE IF NOT EXISTS` does not verify or
update a table that already exists: compare `SHOW CREATE TABLE` output with
the committed definitions.

3. Create the application's MySQL account (as a privileged MySQL user):

```sql
CREATE USER IF NOT EXISTS 'auto_repair_app'@'localhost'
    IDENTIFIED BY 'SET_A_STRONG_LOCAL_PASSWORD';
GRANT SELECT, INSERT, UPDATE, DELETE
    ON auto_repair_db.* TO 'auto_repair_app'@'localhost';
```

Replace the password before running. If this account already exists, use your
existing password rather than assuming the command changed it. Set `.env` with
`DB_NAME=auto_repair_db`, `DB_USER=auto_repair_app`, and that password. `.env`
is ignored by Git and must never be committed.

4. To run read-only reports and rollback-protected CRUD tests, sign in with an
account that has SELECT/INSERT/UPDATE/DELETE privileges and run:

```sql
SOURCE sql/queries.sql;
```

The test transaction rolls back its writes, although MySQL AUTO_INCREMENT
counters may still advance. Do not run these scripts on production data.

5. Launch Flask:

```powershell
python app.py
```

Open http://localhost:5000 and check http://localhost:5000/health. It should
return `"database": "connected"` if your configuration works.

**Important:** `localhost` means the same machine as Flask. Your teammate can
run the schema and seed scripts on their own local MySQL installation; they
do not automatically connect to your local database.

## Deploying to Railway

1. Create a project with a MySQL service and a service from this GitHub repo.
2. On the Flask service, add variables referencing the MySQL service: `DB_HOST=${{MySQL.MYSQLHOST}}`, `DB_PORT=${{MySQL.MYSQLPORT}}`, `DB_USER=${{MySQL.MYSQLUSER}}`, `DB_PASSWORD=${{MySQL.MYSQLPASSWORD}}`, `DB_NAME=${{MySQL.MYSQLDATABASE}}`, plus a real `SECRET_KEY`.
3. Railway picks up the `Procfile` and runs Gunicorn.
4. Load the tables into the Railway MySQL database using its assigned database name. The included schema.sql selects `auto_repair_db`, so adapt the CREATE DATABASE/USE statements for Railway before executing it there. Load seed.sql only if sample data is appropriate and the database is empty.
5. Hit `/health` on the deployed URL to confirm.

## Project layout

```
app.py              Flask app, routes, error handlers
db.py               Connection pool + query/execute/transaction helpers
templates/          Jinja2 templates (base.html is the layout)
static/css, js      Styles and scripts
sql/                schema.sql, seed.sql and queries.sql
Procfile            Gunicorn start command for Railway
```

## AI use disclosure

- Original project skeleton (app.py, db.py, templates, config files, README) generated with Claude Code, then reviewed by the team.
- Sprint 1 example SQL scripts and local-configuration/README edits drafted with ChatGPT; verify against finalized relational schema and review before committing.
