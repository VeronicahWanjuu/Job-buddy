# JobBuddy - Job Search Tracker Application

A comprehensive full-stack application to help job seekers track applications, manage companies, analyze CVs, and stay motivated throughout their job search journey.

## 🚀 Features

- **Application Tracking**: Kanban board to track job applications through different stages
- **Company Management**: Organize target companies and contacts
- **CV Analysis**: ATS score checker to optimize your resume
- **Goal Setting**: Weekly goals and streak tracking
- **Micro-Quests**: Gamified tasks to boost productivity
- **Resources & Coaches**: Curated resources and career coach recommendations
- **Notifications**: Stay on top of follow-ups and reminders
- **Dashboard**: Overview of your job search progress

## 🌐 Access the Application

### Option 1: Use the Live Application (Recommended)

**Live Application URL:** [https://jobbuddy-frontend.onrender.com](https://jobbuddy-frontend.onrender.com)

**Important Notes:**
- The application is deployed on Render's free tier
- The first request may take 30-60 seconds to load as the service spins up from sleep
- Subsequent requests will be faster
- This is normal behavior for free tier hosting
- No installation required - just open the link and start using!

### Option 2: Run Locally

If you want to run the application on your computer, follow the setup instructions below. You'll need to clone the repository and set up both backend and frontend servers.

**Clone the Repository:**
```bash
git clone https://github.com/VeronicahWanjuu/Job-buddy.git
cd Job-buddy-1
```

Then follow the setup instructions in the [Quick Start](#-quick-start) section below.

## 📁 Project Structure

```
Job-buddy-1/
├── backend/                    # Flask REST API backend
│   ├── app.py                 # Main Flask application entry point
│   ├── config.py              # Configuration classes (dev/prod/test)
│   ├── requirements.txt       # Python dependencies
│   ├── database/              # Database management
│   │   ├── db.py             # Database manager class
│   │   ├── init_db.py        # Database initialization script
│   │   └── schema.sql        # SQL schema definitions
│   ├── models/                # Data models (User, Application, Company, etc.)
│   │   ├── user.py           # User model
│   │   ├── application.py    # Job application model
│   │   ├── company.py        # Company model
│   │   ├── contact.py        # Contact model
│   │   ├── cv_analysis.py    # CV analysis model
│   │   ├── goal.py           # Goals model
│   │   ├── notification.py   # Notification model
│   │   ├── onboardingData.py # Onboarding data model
│   │   ├── outreach.py       # Outreach activity model
│   │   ├── streak.py          # Streak tracking model
│   │   └── user_quest.py      # Micro-quest model
│   ├── routes/                # API route handlers
│   │   ├── auth.py           # Authentication routes (login, register)
│   │   ├── applications.py   # Application CRUD routes
│   │   ├── companies.py      # Company CRUD routes
│   │   ├── contacts.py       # Contact CRUD routes
│   │   ├── coaches.py        # Career coaches routes
│   │   ├── cv_matcher.py     # CV analysis routes
│   │   ├── goals.py          # Goals and streaks routes
│   │   ├── notifications.py  # Notification routes
│   │   ├── onboarding.py     # Onboarding routes
│   │   ├── outreach.py       # Outreach routes
│   │   ├── resources.py       # Resources routes
│   │   └── postman/          # Postman API collection files
│   ├── services/              # Business logic services
│   │   ├── notification_service.py  # Notification service
│   │   └── streak_service.py         # Streak calculation service
│   ├── utils/                 # Utility functions
│   │   ├── decorators.py     # Auth decorators
│   │   ├── errors.py         # Error handlers
│   │   ├── helpers.py        # Helper functions
│   │   ├── notifications.py  # Notification utilities
│   │   └── validators.py     # Input validators
│   ├── data/                  # Static data files
│   │   ├── coaches.json      # Career coaches data
│   │   ├── micro_quests.json # Micro-quest definitions
│   │   ├── rejection_messages.json  # Rejection message templates
│   │   ├── resources.json    # Learning resources
│   │   └── templates.json    # Outreach templates
│   └── uploads/               # Uploaded files (CVs)
│       └── cvs/               # User-uploaded CV files
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx           # Main app component with routing
│   │   ├── main.jsx          # React entry point
│   │   ├── index.css         # Global styles
│   │   ├── App.css           # App-specific styles
│   │   ├── components/       # React components
│   │   │   ├── common/       # Shared components (Navbar, Sidebar, etc.)
│   │   │   ├── dashboard/    # Dashboard widgets
│   │   │   ├── applications/ # Application components
│   │   │   ├── companies/    # Company components
│   │   │   ├── contacts/     # Contact components
│   │   │   ├── cv/           # CV analysis components
│   │   │   ├── onboarding/   # Onboarding wizard
│   │   │   ├── outreach/     # Outreach components
│   │   │   ├── resources/    # Resource components
│   │   │   └── coaches/      # Coach components
│   │   ├── pages/            # Page components
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── ApplicationsPage.jsx
│   │   │   ├── CompaniesPage.jsx
│   │   │   ├── CoachesPage.jsx
│   │   │   ├── NotificationsPage.jsx
│   │   │   └── ...
│   │   ├── contexts/         # React contexts
│   │   │   └── AuthContext.jsx  # Authentication context
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API services
│   │   │   └── api.js        # Axios configuration
│   │   ├── utils/            # Utility functions
│   │   └── layouts/          # Layout components
│   ├── package.json          # Frontend dependencies
│   ├── vite.config.js        # Vite configuration
│   └── dist/                 # Production build output
├── docs/                      # Documentation
│   ├── API.md                # API endpoint documentation
│   ├── DATABASE.md           # Database schema documentation
│   └── SETUP.md              # Detailed setup guide
├── tests/                     # Test files
│   ├── backend/              # Backend tests
│   └── test_*.py             # Integration tests
├── render.yaml               # Render deployment configuration
├── pytest.ini                # Pytest configuration
└── README.md                 # This file
```

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite
- **Authentication**: JWT (PyJWT)
- **Security**: bcrypt
- **CV Processing**: PyPDF2, python-docx

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI)
- **Routing**: React Router v7
- **HTTP Client**: Axios
- **Drag & Drop**: @hello-pangea/dnd

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **npm** (comes with Node.js)
- **Git** - [Download Git](https://git-scm.com/downloads)

## 🚀 Quick Start

### Step 1: Clone the Repository

**To run locally, first clone the repository:**

**Windows (PowerShell):**
```powershell
git clone https://github.com/VeronicahWanjuu/Job-buddy.git
cd Job-buddy-1
```

**Linux/Mac:**
```bash
git clone https://github.com/VeronicahWanjuu/Job-buddy.git
cd Job-buddy-1
```

**Or simply use the live application:** [https://jobbuddy-frontend.onrender.com](https://jobbuddy-frontend.onrender.com) (no installation needed!)

### Step 2: Backend Setup

**Windows (PowerShell):**
```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt

# (Optional) Create .env file
# New-Item -Path .env -ItemType File
# Then edit .env with your configuration

# Run the server
python app.py
```

**Windows (Command Prompt):**
```cmd
cd backend
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python app.py
```

**Linux/Mac:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Backend will run on:** `http://localhost:5000`

**Verify backend is running:**
```powershell
# PowerShell
Invoke-WebRequest -Uri http://localhost:5000/health

# Or use curl
curl http://localhost:5000/health
```

**Expected response:** `{"status": "healthy"}`

### Step 3: Frontend Setup

**Open a NEW terminal window** (keep backend running in the first terminal)

**Windows (PowerShell):**
```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Linux/Mac:**
```bash
cd frontend
npm install
npm run dev
```

**Frontend will run on:** `http://localhost:5173`

**Expected output:**
```
  VITE v7.2.4  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

### Step 4: Access the Application

1. Open your web browser
2. Navigate to: `http://localhost:5173`
3. You should see the JobBuddy login/register page

**Important:** Make sure both backend and frontend servers are running!

## 📚 Detailed Documentation

- **[User Manual](docs/USER_MANUAL.md)** - Complete user guide with step-by-step instructions, FAQ, and troubleshooting
- [Backend README](backend/README.md) - Complete backend documentation
- [Frontend README](frontend/README.md) - Complete frontend documentation
- [API Documentation](docs/API.md) - API endpoints and usage
- [Database Schema](docs/DATABASE.md) - Database structure
- [Setup Guide](docs/SETUP.md) - Detailed setup instructions

## 🔧 Environment Variables

### Backend (.env)

Create a `.env` file in the `backend/` directory:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

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

### Frontend (.env)

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_URL=http://localhost:5000/api/v1
VITE_APP_NAME=JobBuddy
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 📝 Available Scripts

### Backend

**Windows (PowerShell):**
```powershell
# Navigate to backend directory
cd backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run development server
python app.py

# Run tests
pytest

# Run tests with coverage
pytest --cov=backend

# Run specific test file
pytest tests/test_auth.py
```

**Linux/Mac:**
```bash
cd backend
source venv/bin/activate
python app.py
pytest
pytest --cov=backend
```

### Frontend

**Windows (PowerShell):**
```powershell
# Navigate to frontend directory
cd frontend

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

**Linux/Mac:**
```bash
cd frontend
npm run dev
npm run build
npm run preview
npm run lint
```

## 🗄️ Database

The application uses SQLite database. The database schema is automatically created on first run.

**Database Location:** `backend/jobbuddy.db` (or as specified in `DATABASE_URL`)

**To reset database:**

**Windows (PowerShell):**
```powershell
# Delete the database file
Remove-Item backend\jobbuddy.db

# Restart the backend server (schema will be recreated)
cd backend
.\venv\Scripts\Activate.ps1
python app.py
```

**Windows (Command Prompt):**
```cmd
del backend\jobbuddy.db
cd backend
venv\Scripts\activate.bat
python app.py
```

**Linux/Mac:**
```bash
rm backend/jobbuddy.db
cd backend
source venv/bin/activate
python app.py
```

## 🔐 Authentication

The app uses JWT (JSON Web Tokens) for authentication:

1. **Register** a new account
2. **Login** to get a JWT token
3. Token is stored in `localStorage`
4. Token is sent in `Authorization: Bearer <token>` header

## 📡 API Base URL

All API endpoints are prefixed with:
```
http://localhost:5000/api/v1
```

## 🐛 Troubleshooting

### Backend Issues

**Port 5000 already in use:**

**Windows (PowerShell):**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace <PID> with actual process ID from above)
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -ti:5000 | xargs kill -9
```

**Database errors:**
- Ensure SQLite is working
- Check file permissions
- Verify DATABASE_URL path

**Module not found errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Port 5173 already in use:**

**Windows (PowerShell):**
```powershell
# Find process using port 5173
netstat -ano | findstr :5173

# Kill the process (replace <PID> with actual process ID)
taskkill /PID <PID> /F

# Or kill all node processes
taskkill /F /IM node.exe
```

**Linux/Mac:**
```bash
lsof -ti:5173 | xargs kill -9
```

**Module not found errors:**

**Windows (PowerShell):**
```powershell
cd frontend
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

**Linux/Mac:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**White screen:**
- Check browser console (F12) for errors
- Verify backend is running
- Check API_URL in .env file

### Common Issues

**CORS Errors:**
- Verify `FRONTEND_URL` in backend .env matches your frontend URL
- Check backend CORS configuration in `app.py`

**Authentication Issues:**
- Clear browser localStorage
- Check token expiration (default: 7 days)
- Verify JWT_SECRET_KEY matches in backend

## 📦 Production Deployment

### Current Deployment

The application is currently deployed on **Render**:
- **Frontend**: [https://jobbuddy-frontend.onrender.com](https://jobbuddy-frontend.onrender.com)
- **Backend**: Deployed separately on Render (configured via `render.yaml`)

**Important Notes:**
- The application uses Render's free tier, which means:
  - Services spin down after 15 minutes of inactivity
  - First request after spin-down takes 30-60 seconds to load
  - This is normal behavior for free tier hosting
  - Subsequent requests are much faster

### Deployment Configuration

The `render.yaml` file contains the deployment configuration for Render. It defines:
- Backend service configuration
- Environment variables
- Build commands
- Health check endpoints

### Manual Deployment Steps

#### Backend

1. Set `FLASK_ENV=production` in environment variables
2. Use a production WSGI server (e.g., Gunicorn)
3. Set secure `SECRET_KEY` and `JWT_SECRET_KEY`
4. Use a production database (PostgreSQL recommended for production)
5. Configure CORS to allow your frontend domain

#### Frontend

1. Build the production bundle:
```bash
cd frontend
npm run build
```

2. Serve the `dist/` folder using a web server (Nginx, Apache, etc.)

3. Configure API proxy to point to your backend URL

4. Set environment variables:
   - `VITE_API_URL` - Your backend API URL

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Veronicah Wanjuu**
- GitHub: [@VeronicahWanjuu](https://github.com/VeronicahWanjuu)

## 🙏 Acknowledgments

- Material-UI for the amazing component library
- Flask community for excellent documentation
- React team for the fantastic framework

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Documentation](docs/)
2. Review [Troubleshooting](#-troubleshooting) section
3. Open an issue on GitHub

---

**Happy Job Hunting! 🎯**

