# Placement Portal Application V2 (PPA-V2)

A full-stack web application for managing campus placement activities between Institute Admin, Companies, and Students.

Built as part of the **Modern Application Development II (MAD-2)** course at IIT Madras BS Programme.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Flask 3.0 |
| Frontend SPA | Vue.js 3 |
| Database | SQLite + SQLAlchemy |
| Authentication | Flask-JWT-Extended |
| State Management | Vuex 4 |
| Routing | Vue Router 4 |
| Styling | Bootstrap 5 |
| Caching | Redis |
| Background Jobs | Celery + Redis |
| Email | Flask-Mail + Gmail SMTP |
| Charts | Chart.js 4 |

---

## Features

### Admin
- Dashboard with placement statistics
- Approve or reject company registrations
- Approve or reject placement drives
- Blacklist or deactivate companies and students
- Search companies and students
- View all applications across the system
- View admin action audit logs
- Download monthly placement reports

### Company
- Register and manage company profile
- Create placement drives after admin approval
- View and manage student applications
- Shortlist students and update application status
- Schedule interviews with mode, venue, date and notes
- Export all applications as CSV

### Student
- Register, login and update profile
- Upload resume
- Browse and search approved placement drives
- Apply to eligible drives with automatic eligibility check
- Track application status with progress indicator
- View interview details with join meeting link
- View placement history
- Export application history as CSV
- ATS resume screener

### Background Jobs (Celery)
- Daily interview reminders sent to students via email
- Daily deadline reminders for upcoming drives
- Monthly placement report generated and emailed to admin
- Async CSV export triggered by student or company

### Analytics
- Application funnel chart
- Monthly placement trends chart
- Top skills in demand chart
- Company performance table
- Public landing page with aggregated stats

---

## Project Structure

```
placement-portal/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models (9 tables)
│   │   ├── routes/          # Flask blueprints
│   │   ├── services/        # Business logic layer
│   │   ├── tasks/           # Celery background jobs
│   │   ├── utils/           # Helpers: cache, mail, validators
│   │   └── __init__.py      # Flask app factory
│   ├── static/
│   │   ├── uploads/resumes/ # Student uploaded resumes
│   │   ├── reports/         # Generated HTML reports
│   │   └── exports/         # CSV export files
│   ├── instance/
│   │   └── placement.db     # SQLite database (auto created)
│   ├── .env                 # Environment variables (not committed)
│   ├── .env.example         # Template for environment variables
│   ├── celery_worker.py     # Celery worker entry point
│   ├── create_admin.py      # Admin seeding script
│   ├── run.py               # Flask entry point
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── views/           # Page components (admin, company, student)
    │   ├── components/      # Reusable UI components
    │   ├── services/        # Axios API service layer
    │   ├── store/           # Vuex store modules
    │   └── router/          # Vue Router with role guards
    ├── public/
    └── package.json
```

---

## Database Tables

| Table | Description |
|-------|-------------|
| users | Unified user model with role field |
| students | Student profile linked to user |
| companies | Company profile linked to user |
| placement_drives | Drives created by companies |
| applications | Student applications to drives |
| interviews | Interview details per application |
| notifications | In-app and email notifications |
| admin_logs | Audit trail of all admin actions |
| reports | Monthly placement report records |

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 16+
- Redis Server

### Step 1 — Clone the repository

```bash
git clone https://github.com/yourusername/placement-portal.git
cd placement-portal
```

### Step 2 — Backend setup

```bash
cd backend
pip install -r requirements.txt
```

Create `.env` file from the example:

```bash
copy .env.example .env
```

Edit `.env` with your actual values:

```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
MAIL_USERNAME=yourgmail@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_DEFAULT_SENDER=yourgmail@gmail.com
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

Initialize the database and seed admin:

```bash
python run.py        # creates DB and all tables automatically
python create_admin.py   # seeds the admin user
```

Default admin credentials:
- Email: `admin@ppa.com`
- Password: `Admin@123`

### Step 3 — Frontend setup

```bash
cd frontend
npm install
```

### Step 4 — Run the application

Open 5 separate terminals:

```bash
# Terminal 1 - Redis
redis-server

# Terminal 2 - Flask
cd backend
python run.py

# Terminal 3 - Celery Worker
cd backend
python -m celery -A celery_worker worker --loglevel=info --pool=solo

# Terminal 4 - Celery Beat
cd backend
python -m celery -A celery_worker beat --loglevel=info

# Terminal 5 - Vue Frontend
cd frontend
npm run serve
```

Open browser at `http://localhost:8080`

---

## API Endpoints Summary

| Prefix | Description |
|--------|-------------|
| `/api/auth` | Login, register, get current user |
| `/api/admin` | All admin management endpoints |
| `/api/company` | Company dashboard and drive management |
| `/api/student` | Student dashboard and application management |
| `/api/public` | Public stats and trends (no auth required) |
| `/api/analytics` | Charts and analytics data |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask secret key |
| `JWT_SECRET_KEY` | JWT signing key |
| `MAIL_USERNAME` | Gmail address for sending emails |
| `MAIL_PASSWORD` | Gmail App Password (16 characters) |
| `MAIL_DEFAULT_SENDER` | Sender email address |
| `REDIS_URL` | Redis connection URL |
| `CELERY_BROKER_URL` | Celery broker URL (same as Redis) |
| `CELERY_RESULT_BACKEND` | Celery result backend URL |

---

## Git Commit Milestones

| Commit Message | Description |
|---------------|-------------|
| `Milestone-0 PPA-V2 Setup` | GitHub repository setup |
| `Milestone-PPA-V2 DB-Relationship` | Database models and schema |
| `Milestone-PPA-V2 Auth-RBAC` | Authentication and role-based access |
| `Milestone-PPA-V2 Admin-Dashboard-Management` | Admin dashboard |
| `Milestone-PPA-V2 Company-Dashboard-Management` | Company dashboard |
| `Milestone-PPA-V2 Student-Dashboard-Management` | Student dashboard |
| `Milestone-PPA-V2 Placement-Tracking` | Application tracking |
| `Milestone-PPA-V2 Celery-Jobs` | Background jobs |
| `Milestone-PPA-V2 Redis-Caching` | Redis caching layer |
| `Milestone-PPA-V2 Reports-Charts-ATS` | Analytics and ATS |
| `Milestone-PPA-V2 Final-Submission` | Final submission |

---

## Notes

- Admin account is pre-seeded programmatically. No admin registration is allowed via UI.
- Database is created automatically on first run via SQLAlchemy. No manual DB creation.
- All sensitive credentials are stored in `.env` file which is excluded from version control.
- Celery worker must be running for CSV export and reminder jobs to work.
- Redis must be running before starting Flask or Celery.