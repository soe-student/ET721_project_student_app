# EduHub — ET721 Student Learning Management App

EduHub is a simple web-based Student Learning Management System (LMS) built with Python and Flask. It was developed as a student project for ET721, allowing students to manage their academic life in one place — tracking tasks, writing blog posts, and uploading notes.

---

## Features

- **User Authentication** — Register and log in securely using hashed passwords
- **Task Manager** — Add, complete, and delete tasks with categories and due dates
- **Student Blog** — Write and share blog posts with the community, and leave comments
- **Notes Upload** — Upload images and PDF files organised by subject

---

## Repository Structure

```
ET721_project_student_app/
│
├── app.py                  # Main Flask application — all routes and logic
├── lms.db                  # SQLite database (auto-created on first run)
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
│
├── static/
│   ├── css/
│   │   └── style.css       # All styles for the application
│   ├── js/
│   │   └── main.js         # Optional frontend JavaScript
│   └── uploads/            # Uploaded note files (auto-created)
│
└── templates/
    ├── base.html           # Base layout with sidebar navigation
    ├── login.html          # Login page
    ├── signup.html         # Registration page
    ├── dashboard.html      # User dashboard with stats
    ├── tasks.html          # Task manager page
    ├── blog.html           # Blog listing and post creation
    └── notes.html          # Notes upload and gallery
```

---

## Static Folder

| File | Description |
|------|-------------|
| `css/style.css` | Main stylesheet. Controls layout, colours, buttons, forms, cards, sidebar, and all page components. Uses CSS variables for easy theming. |
| `js/main.js` | Optional JavaScript file. Currently a placeholder for any future frontend interactions. |
| `uploads/` | Folder where uploaded note files (images and PDFs) are saved. Created automatically on first run. |

---

## Templates Folder

| File | Description |
|------|-------------|
| `base.html` | The parent template that all other templates extend. Contains the sidebar navigation (shown when logged in), the top navigation bar (shown on login/signup pages), and flash message display. |
| `login.html` | The login page. Contains a form with email and password fields that submits to the `/login` route. |
| `signup.html` | The registration page. Contains a form with username, email, and password fields that submits to the `/signup` route. |
| `dashboard.html` | The main dashboard shown after login. Displays four stat cards (tasks pending, tasks done, blog posts, notes), a list of recent tasks, and a list of recent blog posts. |
| `tasks.html` | The task manager page. Contains a form to add new tasks with title, category, and due date, followed by a list of all tasks with options to mark complete or delete. |
| `blog.html` | The blog page. Shows a form to write and publish new posts, followed by all community posts with the author name, category, excerpt, delete option (own posts), and a comment form. |
| `notes.html` | The notes page. Contains a file upload form with subject input, and displays uploaded notes as a grid with image preview or PDF icon, download button, and delete option. |

---

## Routes in app.py

### Authentication

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Shows the login page. Redirects to dashboard if already logged in. |
| POST | `/login` | Processes login form. Checks email and hashed password. Creates session on success. |
| GET | `/signup` | Shows the registration page. |
| POST | `/signup` | Processes signup form. Saves new user with hashed password to the database. |
| GET | `/logout` | Clears the session and redirects to the login page. |

### Dashboard

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/dashboard` | Shows the dashboard with task counts, post counts, note counts, and recent activity. |

### Tasks

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/tasks` | Lists all tasks for the logged-in user. |
| POST | `/tasks/add` | Adds a new task with title, category, and optional due date. |
| GET | `/tasks/done/<task_id>` | Marks a task as completed. |
| GET | `/tasks/delete/<task_id>` | Deletes a task. |

### Blog

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/blog` | Lists all blog posts from all users, newest first. |
| POST | `/blog/add` | Creates a new blog post with title, content, and category. |
| GET | `/blog/delete/<post_id>` | Deletes a blog post (only if it belongs to the logged-in user). |
| POST | `/blog/comment/<post_id>` | Adds a comment to a specific blog post. |

### Notes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/notes` | Lists all uploaded notes for the logged-in user. |
| POST | `/notes/upload` | Uploads a file (image or PDF) with a subject label. |
| GET | `/notes/delete/<note_id>` | Deletes a note and removes the file from disk. |
| GET | `/notes/download/<filename>` | Downloads a note file. |

---

## How to Run

1. Install Flask:
   ```bash
   pip install flask
   ```

2. Run the app:
   ```bash
   python app.py
   ```

3. Open in browser:
   ```
   http://127.0.0.1:5000
   ```

The database and upload folder are created automatically on first launch.

---

## Technologies Used

- **Python** — Backend logic
- **Flask** — Web framework
- **SQLite** — Database (via Python's built-in `sqlite3`)
- **HTML / CSS** — Frontend templates and styling
- **Jinja2** — HTML templating (included with Flask)
- **hashlib** — Password hashing (Python built-in)
