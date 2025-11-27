# JobBuddy Backend - Flask REST API

Complete backend documentation for the JobBuddy application.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [Database Setup](#database-setup)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

The JobBuddy backend is a Flask-based REST API that provides:
- User authentication (JWT)
- Application tracking
- Company and contact management
- CV analysis and ATS scoring
- Goal and streak tracking
- Notifications
- Outreach templates
- Resources and coaches data

**Tech Stack:**
- **Framework**: Flask 3.0.0
- **Database**: SQLite (with custom DatabaseManager)
- **Authentication**: JWT (PyJWT)
- **Security**: bcrypt for password hashing
- **CV Processing**: PyPDF2, python-docx
- **CORS**: Flask-CORS

## 📦 Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed
  - Check version: `python --version`
  - Download: [python.org/downloads](https://www.python.org/downloads/)
- **pip** (usually comes with Python)
  - Check version: `pip --version`
- **Git** (for cloning the repository)

## 🚀 Installation

### Step 1: Navigate to Backend Directory

```powershell
cd backend
```

### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
```

**Linux/Mac:**
```bash
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 4: Install Dependencies

```powershell
pip install -r requirements.txt
```

**Expected output:**
```
Collecting Flask==3.0.0
Collecting Flask-CORS==4.0.0
...
Successfully installed Flask-3.0.0 ...
```

### Step 5: Verify Installation

```powershell
python -c "import flask; print(flask.__version__)"
```

Should output: `3.0.0`

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```powershell
# Create .env file (PowerShell)
New-Item -Path .env -ItemType File
```

**Or manually create `.env` with the following content:**

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# Database
DATABASE_URL=backend/jobbuddy.db

# File Uploads
UPLOAD_FOLDER=backend/uploads/cvs
MAX_FILE_SIZE_MB=5

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:5173

# ATS Scoring
ATS_SCORE_THRESHOLD=60
```

**Note:** The `.env` file is optional. If not present, the app uses default values from `config.py`.

### Default Configuration Values

If no `.env` file exists, defaults are:
- `FLASK_ENV`: `development`
- `SECRET_KEY`: `dev-secret`
- `JWT_SECRET_KEY`: `dev-jwt-secret`
- `DATABASE_URL`: `backend/test_models.db`
- `UPLOAD_FOLDER`: `backend/uploads/cvs`
- `MAX_FILE_SIZE_MB`: `5`
- `FRONTEND_URL`: `http://localhost:5173`
- `ATS_SCORE_THRESHOLD`: `60`

## 🗄️ Database Setup

The database is automatically initialized on first run. The schema is created from `backend/database/schema.sql`.

### Manual Database Initialization

If you need to manually initialize or reset the database:

```powershell
python backend/database/init_db.py
```

**Database Location:**
- Default: `backend/jobbuddy.db` (or as specified in `DATABASE_URL`)

### Database Schema

The database includes the following tables:
- `users` - User accounts
- `onboarding_data` - User onboarding information
- `applications` - Job applications
- `companies` - Target companies
- `contacts` - Company contacts
- `outreach` - Outreach activities
- `goals` - Weekly goals
- `streaks` - User streaks
- `cv_analyses` - CV analysis results
- `notifications` - User notifications
- `user_quests` - Micro-quests tracking

See `backend/database/schema.sql` for complete schema.

## 🏃 Running the Server

### Development Mode

**From the backend directory:**

```powershell
# Make sure virtual environment is activated
python app.py
```

**Or from the project root:**

```powershell
cd backend
python app.py
```

**Expected output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://0.0.0.0:5000
Press CTRL+C to quit
```

**Server will be available at:**
- `http://localhost:5000`
- `http://127.0.0.1:5000`

### Health Check

Test if the server is running:

```powershell
# PowerShell
Invoke-WebRequest -Uri http://localhost:5000/health

# Or use curl (if installed)
curl http://localhost:5000/health
```

**Expected response:**
```json
{"status": "healthy"}
```

### Production Mode

For production, use a WSGI server like Gunicorn:

```powershell
# Install gunicorn (if not already installed)
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:app"
```

**Set environment:**
```powershell
$env:FLASK_ENV="production"
python app.py
```

## 📡 API Endpoints

All API endpoints are prefixed with `/api/v1`.

### Base URL
```
http://localhost:5000/api/v1
```

### Available Routes

#### Authentication (`/api/v1/auth`)
- `POST /register` - Register new user
- `POST /login` - User login
- `GET /profile` - Get user profile (protected)
- `PUT /profile` - Update user profile (protected)

#### Onboarding (`/api/v1/onboarding`)
- `GET /status` - Get onboarding status
- `POST /submit` - Submit onboarding data
- `GET /data` - Get onboarding data (protected)

#### Applications (`/api/v1/applications`)
- `GET /` - List all applications (protected)
- `POST /` - Create new application (protected)
- `GET /<id>` - Get application details (protected)
- `PUT /<id>` - Update application (protected)
- `DELETE /<id>` - Delete application (protected)
- `PUT /<id>/status` - Update application status (protected)

#### Companies (`/api/v1/companies`)
- `GET /` - List all companies (protected)
- `POST /` - Create new company (protected)
- `GET /<id>` - Get company details (protected)
- `PUT /<id>` - Update company (protected)
- `DELETE /<id>` - Delete company (protected)

#### Contacts (`/api/v1/contacts`)
- `GET /` - List all contacts (protected)
- `POST /` - Create new contact (protected)
- `GET /<id>` - Get contact details (protected)
- `PUT /<id>` - Update contact (protected)
- `DELETE /<id>` - Delete contact (protected)

#### CV Analysis (`/api/v1/cv`)
- `POST /analyze` - Analyze CV file (protected)
- `GET /history` - Get CV analysis history (protected)
- `GET /<id>` - Get specific analysis (protected)

#### Goals (`/api/v1/goals`)
- `GET /` - Get current goals (protected)
- `POST /` - Create/update goals (protected)

#### Notifications (`/api/v1/notifications`)
- `GET /` - List notifications (protected)
- `GET /unread-count` - Get unread count (protected)
- `PUT /<id>/read` - Mark as read (protected)
- `PUT /read-all` - Mark all as read (protected)
- `DELETE /<id>` - Delete notification (protected)

#### Outreach (`/api/v1/outreach`)
- `GET /` - List outreach activities (protected)
- `POST /` - Create outreach (protected)
- `POST /generate` - Generate outreach template (protected)

#### Resources (`/api/v1/resources`)
- `GET /` - List all resources

#### Coaches (`/api/v1/coaches`)
- `GET /` - List all coaches

### Authentication

Most endpoints require authentication. Include the JWT token in the request header:

```
Authorization: Bearer <your-jwt-token>
```

**Example:**
```powershell
$token = "your-jwt-token-here"
$headers = @{
    "Authorization" = "Bearer $token"
}
Invoke-WebRequest -Uri http://localhost:5000/api/v1/applications -Headers $headers
```

## 🧪 Testing

### Run Tests

```powershell
# Install pytest if not already installed
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=backend

# Run specific test file
pytest tests/test_auth.py
```

### Test Database

Tests use an in-memory SQLite database (configured in `TestingConfig`).

## 🐛 Troubleshooting

### Port 5000 Already in Use

**Windows:**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace <PID> with actual process ID)
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -ti:5000 | xargs kill -9
```

### Module Not Found Errors

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Errors

**Database file not found:**
- The database is created automatically on first run
- Check `DATABASE_URL` in `.env` or `config.py`
- Ensure write permissions in the database directory

**Reset database:**
```powershell
# Delete database file
Remove-Item backend\jobbuddy.db

# Restart server (database will be recreated)
python app.py
```

### CORS Errors

If you see CORS errors in the frontend:

1. Check `FRONTEND_URL` in `.env` matches your frontend URL
2. Default allowed origins:
   - `http://localhost:5173`
   - `http://127.0.0.1:5173`
   - `http://localhost:3000`

### Import Errors

If you see import errors like `ModuleNotFoundError: No module named 'backend'`:

**Run from project root:**
```powershell
# From project root (not backend directory)
cd ..
python backend/app.py
```

### File Upload Errors

**Check upload folder exists:**
```powershell
# Create upload folder if missing
New-Item -ItemType Directory -Force -Path backend\uploads\cvs
```

**Check file size limit:**
- Default: 5MB (configurable via `MAX_FILE_SIZE_MB`)

## 📁 Project Structure

```
backend/
├── app.py                 # Main application entry point
├── config.py              # Configuration classes
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── database/
│   ├── db.py             # Database manager
│   ├── init_db.py        # Database initialization
│   └── schema.sql        # Database schema
├── models/               # Data models
│   ├── user.py
│   ├── application.py
│   ├── company.py
│   └── ...
├── routes/               # API route handlers
│   ├── auth.py
│   ├── applications.py
│   ├── companies.py
│   └── ...
├── services/             # Business logic services
│   ├── notification_service.py
│   └── streak_service.py
├── utils/                # Utility functions
│   ├── decorators.py
│   ├── validators.py
│   └── helpers.py
└── uploads/              # Uploaded files (CVs)
    └── cvs/
```

## 🔐 Security Notes

**For Production:**
1. Change `SECRET_KEY` and `JWT_SECRET_KEY` to strong random values
2. Set `FLASK_ENV=production`
3. Use a production database (PostgreSQL recommended)
4. Enable HTTPS
5. Use environment variables for sensitive data
6. Never commit `.env` file to version control

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [JWT Authentication](https://jwt.io/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

## 🤝 Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review error logs in the terminal
3. Check browser console (for frontend-related errors)
4. Verify all dependencies are installed correctly

---

**Happy Coding! 🚀**

