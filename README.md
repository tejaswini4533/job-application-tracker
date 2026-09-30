# JobTrack

**Track. Apply. Follow Up. Get Hired.**

A full-stack Job Application Tracker built with Python Flask, SQLAlchemy, and Bootstrap 5. Designed as a professional final-year project demonstrating full-stack development, authentication, CRUD, REST APIs, data visualization, and deployment readiness.

---

## Features

- **Authentication** — Register, login, logout with secure password hashing
- **Dashboard** — Real-time stats, charts, upcoming interviews, overdue follow-ups
- **Application Management** — Add, edit, delete, search, filter, sort, paginate
- **Interview Tracking** — Log rounds, types, dates, results per application
- **Follow-up Management** — Overdue, upcoming, and completed follow-ups
- **Resume Manager** — Upload, download, delete PDF/DOC/DOCX resumes
- **Analytics** — Response rate, interview rate, offer rate, charts by source/month
- **Profile** — Update name, change password
- **Dark Mode** — Persisted via localStorage
- **Global Search** — Wired topbar search (press `/` to focus)
- **Live Notifications** — Bell icon shows upcoming interviews and overdue follow-ups
- **Security** — User isolation, CSRF protection, `@login_required` on all private routes
- **Responsive** — Works on desktop, tablet, and mobile

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask |
| ORM | Flask-SQLAlchemy |
| Auth | Flask-Login, Werkzeug |
| Forms/CSRF | Flask-WTF |
| Migrations | Flask-Migrate |
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript |
| Charts | Chart.js |
| Icons | Bootstrap Icons |
| Database (dev) | SQLite |
| Database (prod) | PostgreSQL |
| Deployment | Gunicorn, Render |

---

## Project Structure

```
job_application_tracker/
├── run.py                  # Entry point
├── config.py               # Dev/prod config
├── requirements.txt
├── render.yaml             # Render deployment config
├── seed_demo.py            # Demo data seeder
├── .env.example
├── .gitignore
├── app/
│   ├── __init__.py         # App factory
│   ├── models.py           # User, Application, Interview, Resume
│   ├── routes/
│   │   ├── auth.py         # /auth/register, /auth/login, /auth/logout, /auth/profile
│   │   ├── main.py         # /, /dashboard, /analytics, /search, /api/notifications
│   │   ├── applications.py # /applications CRUD
│   │   ├── interviews.py   # /interviews CRUD
│   │   ├── followups.py    # /followups
│   │   ├── resumes.py      # /resumes upload/download/delete
│   │   └── errors.py       # 404, 403, 500 handlers
│   ├── templates/
│   └── static/
└── instance/
    ├── job_tracker.db
    └── resumes/            # Uploaded resume files
```

---

## Installation (Local)

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/job_application_tracker.git
cd job_application_tracker
```

### 2. Create and activate virtual environment

```bash
# Windows
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# If PowerShell blocks activation:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
```

Edit `.env`:
```
SECRET_KEY=your-random-secret-key
FLASK_ENV=development
```

### 5. Run the application

```bash
python run.py
```

Open: http://127.0.0.1:5000

---

## Demo Data (Optional)

To seed a demo account with sample applications:

```bash
python seed_demo.py
```

Login with: `demo@jobtrack.com` / `demo1234`

---

## Database Migrations

After changing models:

```bash
flask db init       # First time only
flask db migrate -m "description"
flask db upgrade
```

---

## Testing the Full Flow

1. Open http://127.0.0.1:5000 — landing page
2. Register a new account
3. Login → redirects to dashboard
4. Add an application
5. View application detail
6. Add an interview from the detail page
7. Set a follow-up date
8. Go to Follow-ups page — see it listed
9. Mark follow-up as done
10. Upload a resume at /resumes
11. Edit the application and link the resume
12. Open Analytics — see real charts
13. Edit profile — update name or password
14. Logout — dashboard becomes inaccessible
15. Try accessing /dashboard directly — redirects to login

---

## Deployment on Render

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/jobtrack.git
git push -u origin main
```

### 2. Create Render Web Service

- Go to https://render.com
- New → Web Service → Connect GitHub repo
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn run:app`

### 3. Add Environment Variables on Render

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | (generate a random string) |
| `DATABASE_URL` | (from Render PostgreSQL) |

### 4. Add PostgreSQL on Render

- New → PostgreSQL
- Copy the **Internal Database URL**
- Add as `DATABASE_URL` environment variable in your web service

### 5. Database initializes automatically on first request via `db.create_all()`

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session secret | `dev-secret-change-in-production` |
| `FLASK_ENV` | `development` or `production` | `default` (development) |
| `DATABASE_URL` | Database connection string | SQLite local file |

---

## Future Enhancements

- Email reminders for follow-ups and interviews
- Calendar integration (Google Calendar API)
- Automatic job import from LinkedIn/Naukri APIs
- Resume parsing and keyword matching
- Interview preparation notes with rich text editor
- Export applications to CSV/Excel
- Two-factor authentication
- Team/shared workspace mode

---

## License

MIT License — Free to use for educational and personal projects.
