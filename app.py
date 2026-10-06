"""Employee Management System - Flask + SQLite.
Features: login, CRUD (UI + REST API), DB connectivity, error handling.
"""
import os
import sqlite3
import sys
from functools import wraps

from flask import (Flask, flash, g, jsonify, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash


def resource_path(rel):
    """Works both normally and inside a PyInstaller executable."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def create_app(db_path=None):
    app = Flask(__name__,
                template_folder=resource_path("templates"),
                static_folder=resource_path("static"))
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    app.config["DATABASE"] = db_path or os.environ.get(
        "EMS_DB", os.path.join(os.getcwd(), "employees.db"))

    # ---------- database ----------
    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        db = sqlite3.connect(app.config["DATABASE"])
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                department TEXT NOT NULL,
                salary REAL NOT NULL DEFAULT 0);
        """)
        if not db.execute("SELECT 1 FROM users WHERE username='admin'").fetchone():
            db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                       ("admin", generate_password_hash("admin123")))
        db.commit()
        db.close()

    init_db()

    # ---------- helpers ----------
    def login_required(view):
        @wraps(view)
        def wrapped(*a, **kw):
            if "user" not in session:
                if request.path.startswith("/api/"):
                    return jsonify(error="Authentication required"), 401
                return redirect(url_for("login"))
            return view(*a, **kw)
        return wrapped

    def validate(data):
        """Return (clean_data, error_message)."""
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()
        dept = (data.get("department") or "").strip()
        try:
            salary = float(data.get("salary") or 0)
        except (TypeError, ValueError):
            return None, "Salary must be a number"
        if not name or not email or not dept:
            return None, "Name, email and department are required"
        if "@" not in email:
            return None, "Invalid email address"
        if salary < 0:
            return None, "Salary cannot be negative"
        return dict(name=name, email=email, department=dept, salary=salary), None

    # ---------- auth ----------
    @app.route("/", methods=["GET"])
    def index():
        return redirect(url_for("employees" if "user" in session else "login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            u = request.form.get("username", "").strip()
            p = request.form.get("password", "")
            row = get_db().execute(
                "SELECT * FROM users WHERE username=?", (u,)).fetchone()
            if row and check_password_hash(row["password_hash"], p):
                session["user"] = u
                return redirect(url_for("employees"))
            flash("Invalid username or password", "error")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    # ---------- UI: employees ----------
    @app.route("/employees")
    @login_required
    def employees():
        rows = get_db().execute("SELECT * FROM employees ORDER BY id").fetchall()
        return render_template("employees.html", employees=rows, user=session["user"])

    @app.route("/employees/add", methods=["POST"])
    @login_required
    def add_employee_ui():
        clean, err = validate(request.form)
        if err:
            flash(err, "error")
        else:
            try:
                get_db().execute(
                    "INSERT INTO employees (name,email,department,salary) VALUES (?,?,?,?)",
                    (clean["name"], clean["email"], clean["department"], clean["salary"]))
                get_db().commit()
                flash("Employee added", "ok")
            except sqlite3.IntegrityError:
                flash("An employee with that email already exists", "error")
        return redirect(url_for("employees"))

    @app.route("/employees/<int:eid>/update", methods=["POST"])
    @login_required
    def update_employee_ui(eid):
        clean, err = validate(request.form)
        if err:
            flash(err, "error")
        else:
            try:
                cur = get_db().execute(
                    "UPDATE employees SET name=?,email=?,department=?,salary=? WHERE id=?",
                    (clean["name"], clean["email"], clean["department"], clean["salary"], eid))
                get_db().commit()
                flash("Employee updated" if cur.rowcount else "Employee not found",
                      "ok" if cur.rowcount else "error")
            except sqlite3.IntegrityError:
                flash("An employee with that email already exists", "error")
        return redirect(url_for("employees"))

    @app.route("/employees/<int:eid>/delete", methods=["POST"])
    @login_required
    def delete_employee_ui(eid):
        cur = get_db().execute("DELETE FROM employees WHERE id=?", (eid,))
        get_db().commit()
        flash("Employee deleted" if cur.rowcount else "Employee not found",
              "ok" if cur.rowcount else "error")
        return redirect(url_for("employees"))

    # ---------- REST API ----------
    @app.get("/api/employees")
    @login_required
    def api_list():
        rows = get_db().execute("SELECT * FROM employees ORDER BY id").fetchall()
        return jsonify([dict(r) for r in rows])

    @app.get("/api/employees/<int:eid>")
    @login_required
    def api_get(eid):
        row = get_db().execute("SELECT * FROM employees WHERE id=?", (eid,)).fetchone()
        if not row:
            return jsonify(error="Employee not found"), 404
        return jsonify(dict(row))

    @app.post("/api/employees")
    @login_required
    def api_create():
        clean, err = validate(request.get_json(silent=True) or {})
        if err:
            return jsonify(error=err), 400
        try:
            cur = get_db().execute(
                "INSERT INTO employees (name,email,department,salary) VALUES (?,?,?,?)",
                (clean["name"], clean["email"], clean["department"], clean["salary"]))
            get_db().commit()
        except sqlite3.IntegrityError:
            return jsonify(error="Email already exists"), 409
        return jsonify(id=cur.lastrowid, **clean), 201

    @app.put("/api/employees/<int:eid>")
    @login_required
    def api_update(eid):
        clean, err = validate(request.get_json(silent=True) or {})
        if err:
            return jsonify(error=err), 400
        try:
            cur = get_db().execute(
                "UPDATE employees SET name=?,email=?,department=?,salary=? WHERE id=?",
                (clean["name"], clean["email"], clean["department"], clean["salary"], eid))
            get_db().commit()
        except sqlite3.IntegrityError:
            return jsonify(error="Email already exists"), 409
        if not cur.rowcount:
            return jsonify(error="Employee not found"), 404
        return jsonify(id=eid, **clean)

    @app.delete("/api/employees/<int:eid>")
    @login_required
    def api_delete(eid):
        cur = get_db().execute("DELETE FROM employees WHERE id=?", (eid,))
        get_db().commit()
        if not cur.rowcount:
            return jsonify(error="Employee not found"), 404
        return "", 204

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    # ---------- error handling ----------
    @app.errorhandler(404)
    def not_found(_e):
        if request.path.startswith("/api/"):
            return jsonify(error="Not found"), 404
        return render_template("error.html", code=404, message="Page not found"), 404

    @app.errorhandler(500)
    def server_error(_e):
        if request.path.startswith("/api/"):
            return jsonify(error="Internal server error"), 500
        return render_template("error.html", code=500, message="Something went wrong"), 500

    return app


if __name__ == "__main__":
    import webbrowser, threading
    port = int(os.environ.get("PORT", 5000))
    if getattr(sys, "frozen", False):  # running as .exe -> open the browser
        threading.Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    create_app().run(host="0.0.0.0", port=port)
