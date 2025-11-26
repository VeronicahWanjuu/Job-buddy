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

## 📁 Project Structure

```
Job-buddy-1/
├── backend/          # Flask REST API
├── frontend/         # React + Vite frontend
├── docs/            # Documentation
└── tests/           # Test files
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

### 1. Clone the Repository

```bash
git clone https://github.com/VeronicahWanjuu/Job-buddy.git
cd Job-buddy-1
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (Windows)
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional, uses defaults if not present)
# Copy .env.example to .env and modify if needed

# Run the server
python app.py
```

**Backend will run on:** `http://localhost:5000`

### 3. Frontend Setup

```bash
# Open a new terminal window
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend will run on:** `http://localhost:5173`

### 4. Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

## 📚 Detailed Documentation

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

```bash
# Run development server
python app.py

# Run tests
pytest

# Run with coverage
pytest --cov=backend
```

### Frontend

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🗄️ Database

The application uses SQLite database. The database schema is automatically created on first run.

**Database Location:** `backend/jobbuddy.db` (or as specified in `DATABASE_URL`)

**To reset database:**
```bash
# Delete the database file
rm backend/jobbuddy.db  # Linux/Mac
del backend\jobbuddy.db  # Windows

# Restart the backend server (schema will be recreated)
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
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID)
taskkill /PID <PID> /F
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
```bash
# Kill node processes
taskkill /F /IM node.exe
```

**Module not found errors:**
```bash
# Delete node_modules and reinstall
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

### Backend

1. Set `FLASK_ENV=production`
2. Use a production WSGI server (e.g., Gunicorn)
3. Set secure `SECRET_KEY` and `JWT_SECRET_KEY`
4. Use a production database (PostgreSQL recommended)

### Frontend

1. Build the production bundle:
```bash
npm run build
```

2. Serve the `dist/` folder using a web server (Nginx, Apache, etc.)

3. Configure API proxy to point to your backend URL

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

