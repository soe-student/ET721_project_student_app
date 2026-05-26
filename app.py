from flask import Flask, render_template, request, redirect, session, flash, send_from_directory
from datetime import datetime
import sqlite3
import hashlib
import os

# ── App & Config ───────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "et721-lms-secret-key-2024"
UPLOAD_FOLDER   = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}

# ── Password helpers (using built-in hashlib) ──────────────────────────────────
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(stored, entered):
    return stored == hashlib.sha256(entered.encode()).hexdigest()

# ── Safe filename (no werkzeug needed) ────────────────────────────────────────
def safe_filename(filename):
    keep = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    return "".join(c for c in filename.replace(" ", "_") if c in keep)

# ── Database helper ────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect("lms.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            email    TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER NOT NULL,
            title    TEXT    NOT NULL,
            category TEXT    DEFAULT 'General',
            due_date TEXT,
            done     INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS posts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            title      TEXT    NOT NULL,
            content    TEXT    NOT NULL,
            category   TEXT    DEFAULT 'General',
            created_at TEXT    NOT NULL
        );
        CREATE TABLE IF NOT EXISTS comments (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id    INTEGER NOT NULL,
            user_id    INTEGER NOT NULL,
            content    TEXT    NOT NULL,
            created_at TEXT    NOT NULL
        );
        CREATE TABLE IF NOT EXISTS notes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            filename    TEXT    NOT NULL,
            subject     TEXT    DEFAULT 'General',
            uploaded_at TEXT    NOT NULL
        );
    """)
    conn.commit()
    conn.close()

# ── Helper: check if logged in ─────────────────────────────────────────────────
def logged_in():
    return "user_id" in session

# ── Auth Routes ────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    if logged_in():
        return redirect("/dashboard")
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    email    = request.form["email"]
    password = request.form["password"]

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()

    if user and check_password(user["password"], password):
        session["user_id"]  = user["id"]
        session["username"] = user["username"]
        return redirect("/dashboard")
    else:
        flash("Wrong email or password.")
        return redirect("/")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    username = request.form["username"]
    email    = request.form["email"]
    password = hash_password(request.form["password"])

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )
        conn.commit()
        flash("Account created! Please log in.")
        return redirect("/")
    except sqlite3.IntegrityError:
        flash("Username or email already taken.")
        return redirect("/signup")
    finally:
        conn.close()

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ── Dashboard ──────────────────────────────────────────────────────────────────
@app.route("/dashboard")
def dashboard():
    if not logged_in():
        return redirect("/")
    conn = get_db()
    uid = session["user_id"]
    tasks_pending = conn.execute("SELECT COUNT(*) FROM tasks WHERE user_id=? AND done=0", (uid,)).fetchone()[0]
    tasks_done    = conn.execute("SELECT COUNT(*) FROM tasks WHERE user_id=? AND done=1", (uid,)).fetchone()[0]
    total_posts   = conn.execute("SELECT COUNT(*) FROM posts WHERE user_id=?", (uid,)).fetchone()[0]
    total_notes   = conn.execute("SELECT COUNT(*) FROM notes WHERE user_id=?", (uid,)).fetchone()[0]
    recent_tasks  = conn.execute("SELECT * FROM tasks WHERE user_id=? ORDER BY id DESC LIMIT 3", (uid,)).fetchall()
    recent_posts  = conn.execute("SELECT * FROM posts WHERE user_id=? ORDER BY id DESC LIMIT 3", (uid,)).fetchall()
    conn.close()
    return render_template("dashboard.html",
        username=session["username"],
        tasks_pending=tasks_pending,
        tasks_done=tasks_done,
        total_posts=total_posts,
        total_notes=total_notes,
        recent_tasks=recent_tasks,
        recent_posts=recent_posts
    )

# ── Tasks ──────────────────────────────────────────────────────────────────────
@app.route("/tasks")
def tasks():
    if not logged_in():
        return redirect("/")
    conn = get_db()
    all_tasks = conn.execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY done, due_date",
        (session["user_id"],)
    ).fetchall()
    conn.close()
    return render_template("tasks.html", tasks=all_tasks)

@app.route("/tasks/add", methods=["POST"])
def add_task():
    if not logged_in():
        return redirect("/")
    title    = request.form["title"]
    category = request.form.get("category", "General")
    due_date = request.form.get("due_date", "")

    conn = get_db()
    conn.execute(
        "INSERT INTO tasks (user_id, title, category, due_date) VALUES (?, ?, ?, ?)",
        (session["user_id"], title, category, due_date)
    )
    conn.commit()
    conn.close()
    return redirect("/tasks")

@app.route("/tasks/done/<int:task_id>")
def complete_task(task_id):
    if not logged_in():
        return redirect("/")
    conn = get_db()
    conn.execute(
        "UPDATE tasks SET done = 1 WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"])
    )
    conn.commit()
    conn.close()
    return redirect("/tasks")

@app.route("/tasks/delete/<int:task_id>")
def delete_task(task_id):
    if not logged_in():
        return redirect("/")
    conn = get_db()
    conn.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"])
    )
    conn.commit()
    conn.close()
    return redirect("/tasks")

# ── Blog ───────────────────────────────────────────────────────────────────────
@app.route("/blog")
def blog():
    if not logged_in():
        return redirect("/")
    conn = get_db()
    posts = conn.execute("""
        SELECT posts.*, users.username
        FROM posts JOIN users ON posts.user_id = users.id
        ORDER BY posts.id DESC
    """).fetchall()
    conn.close()
    return render_template("blog.html", posts=posts)

@app.route("/blog/add", methods=["POST"])
def add_post():
    if not logged_in():
        return redirect("/")
    title    = request.form["title"]
    content  = request.form["content"]
    category = request.form.get("category", "General")
    now      = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = get_db()
    conn.execute(
        "INSERT INTO posts (user_id, title, content, category, created_at) VALUES (?, ?, ?, ?, ?)",
        (session["user_id"], title, content, category, now)
    )
    conn.commit()
    conn.close()
    return redirect("/blog")

@app.route("/blog/delete/<int:post_id>")
def delete_post(post_id):
    if not logged_in():
        return redirect("/")
    conn = get_db()
    conn.execute(
        "DELETE FROM posts WHERE id = ? AND user_id = ?",
        (post_id, session["user_id"])
    )
    conn.commit()
    conn.close()
    return redirect("/blog")

@app.route("/blog/comment/<int:post_id>", methods=["POST"])
def add_comment(post_id):
    if not logged_in():
        return redirect("/")
    content = request.form["content"]
    now     = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = get_db()
    conn.execute(
        "INSERT INTO comments (post_id, user_id, content, created_at) VALUES (?, ?, ?, ?)",
        (post_id, session["user_id"], content, now)
    )
    conn.commit()
    conn.close()
    return redirect("/blog")

# ── Notes (File Upload) ────────────────────────────────────────────────────────
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/notes")
def notes():
    if not logged_in():
        return redirect("/")
    conn = get_db()
    all_notes = conn.execute(
        "SELECT * FROM notes WHERE user_id = ? ORDER BY id DESC",
        (session["user_id"],)
    ).fetchall()
    conn.close()
    return render_template("notes.html", notes=all_notes)

@app.route("/notes/upload", methods=["POST"])
def upload_note():
    if not logged_in():
        return redirect("/")
    file    = request.files.get("file")
    subject = request.form.get("subject", "General")

    if file and allowed_file(file.filename):
        filename = safe_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(os.path.join(UPLOAD_FOLDER, filename))

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = get_db()
        conn.execute(
            "INSERT INTO notes (user_id, filename, subject, uploaded_at) VALUES (?, ?, ?, ?)",
            (session["user_id"], filename, subject, now)
        )
        conn.commit()
        conn.close()
        flash("File uploaded!")
    else:
        flash("Invalid file type. Allowed: png, jpg, jpeg, gif, pdf")

    return redirect("/notes")

@app.route("/notes/delete/<int:note_id>")
def delete_note(note_id):
    if not logged_in():
        return redirect("/")
    conn = get_db()
    note = conn.execute(
        "SELECT * FROM notes WHERE id = ? AND user_id = ?",
        (note_id, session["user_id"])
    ).fetchone()
    if note:
        filepath = os.path.join(UPLOAD_FOLDER, note["filename"])
        if os.path.exists(filepath):
            os.remove(filepath)
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
    conn.close()
    return redirect("/notes")

@app.route("/notes/download/<filename>")
def download_note(filename):
    if not logged_in():
        return redirect("/")
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)