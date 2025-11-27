# JobBuddy Frontend - React Application

Complete frontend documentation for the JobBuddy application.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Building for Production](#building-for-production)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

The JobBuddy frontend is a modern React application built with:
- **React 19** - UI framework
- **Vite 7** - Build tool and dev server
- **Material-UI (MUI) 7** - Component library
- **React Router 7** - Client-side routing
- **Axios** - HTTP client
- **React Toastify** - Notifications

**Key Features:**
- Responsive design with Material-UI
- JWT-based authentication
- Real-time notifications
- Drag-and-drop Kanban board for applications
- CV analysis and ATS scoring
- Goal tracking and streaks
- Company and contact management

## 📦 Prerequisites

Before you begin, ensure you have:

- **Node.js 18+** installed
  - Check version: `node --version`
  - Download: [nodejs.org](https://nodejs.org/)
- **npm** (comes with Node.js)
  - Check version: `npm --version`
- **Git** (for cloning the repository)

## 🚀 Installation

### Step 1: Navigate to Frontend Directory

```powershell
cd frontend
```

### Step 2: Install Dependencies

```powershell
npm install
```

**Expected output:**
```
added 250 packages, and audited 251 packages in 15s
```

**If you encounter errors:**
```powershell
# Clear cache and reinstall
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

### Step 3: Verify Installation

```powershell
npm list --depth=0
```

Should show all dependencies without "UNMET DEPENDENCY" errors.

## 🏃 Running the Application

### Development Mode

**Start the development server:**

```powershell
npm run dev
```

**Expected output:**
```
  VITE v7.2.4  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
  ➜  press h + enter to show help
```

**Application will be available at:**
- `http://localhost:5173`
- `http://127.0.0.1:5173`

### Important: Backend Must Be Running

**Before starting the frontend, make sure the backend is running:**

1. Open a separate terminal
2. Navigate to backend directory:
   ```powershell
   cd backend
   ```
3. Activate virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
4. Start backend server:
   ```powershell
   python app.py
   ```

The backend should be running on `http://localhost:5000`.

### Access the Application

1. Open your browser
2. Navigate to: `http://localhost:5173`
3. You should see the JobBuddy login page

## 🏗️ Building for Production

### Build the Application

```powershell
npm run build
```

**Expected output:**
```
vite v7.2.4 building for production...
✓ 150 modules transformed.
dist/index.html                   0.45 kB
dist/assets/index-abc123.js       245.67 kB
...
```

**Build output location:** `frontend/dist/`

### Preview Production Build

```powershell
npm run preview
```

This serves the production build locally for testing.

### Deploy Production Build

The `dist/` folder contains static files that can be served by:
- Nginx
- Apache
- Netlify
- Vercel
- Any static file server

**Example with Python:**
```powershell
cd dist
python -m http.server 8000
```

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # React components
│   │   ├── common/        # Shared components (Navbar, Sidebar, etc.)
│   │   ├── dashboard/     # Dashboard widgets
│   │   ├── applications/  # Application-related components
│   │   ├── companies/     # Company components
│   │   ├── contacts/      # Contact components
│   │   ├── cv/            # CV analysis components
│   │   ├── onboarding/    # Onboarding wizard
│   │   ├── outreach/      # Outreach components
│   │   ├── resources/     # Resource components
│   │   └── coaches/       # Coach components
│   ├── contexts/          # React contexts (AuthContext)
│   ├── hooks/             # Custom React hooks
│   ├── pages/             # Page components
│   │   ├── DashboardPage.jsx
│   │   ├── ApplicationsPage.jsx
│   │   ├── CompaniesPage.jsx
│   │   └── ...
│   ├── services/          # API services
│   │   └── api.js         # Axios configuration
│   ├── utils/             # Utility functions
│   ├── App.jsx            # Main app component
│   ├── main.jsx           # Entry point
│   ├── index.css          # Global styles
│   └── App.css            # App-specific styles
├── package.json           # Dependencies and scripts
├── vite.config.js         # Vite configuration
└── .eslintrc.cjs          # ESLint configuration
```

## ⚙️ Configuration

### Vite Configuration

The Vite config (`vite.config.js`) includes:
- Development server on port `5173`
- Proxy for `/api` requests to `http://localhost:5000`
- Path aliases (`@` maps to `/src`)

**To change the port:**
```javascript
// vite.config.js
server: {
  port: 3000, // Change to your preferred port
}
```

### API Configuration

API base URL is configured in `src/services/api.js`:

```javascript
const api = axios.create({
  baseURL: '/api/v1', // Proxied to http://localhost:5000/api/v1
});
```

**For production, update the base URL:**
```javascript
baseURL: process.env.VITE_API_URL || '/api/v1',
```

### Environment Variables

Create a `.env` file in the `frontend/` directory (optional):

```env
VITE_API_URL=http://localhost:5000/api/v1
VITE_APP_NAME=JobBuddy
```

**Note:** Vite requires the `VITE_` prefix for environment variables.

## 🧪 Available Scripts

### Development

```powershell
npm run dev
```
Starts the development server with hot module replacement.

### Build

```powershell
npm run build
```
Creates an optimized production build in the `dist/` folder.

### Preview

```powershell
npm run preview
```
Serves the production build locally for testing.

### Lint

```powershell
npm run lint
```
Runs ESLint to check for code issues.

## 🐛 Troubleshooting

### Port 5173 Already in Use

**Windows:**
```powershell
# Find process using port 5173
netstat -ano | findstr :5173

# Kill the process (replace <PID> with actual process ID)
taskkill /PID <PID> /F
```

**Or change the port in `vite.config.js`:**
```javascript
server: {
  port: 3000, // Use a different port
}
```

### Module Not Found Errors

```powershell
# Delete node_modules and reinstall
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

### White Screen / Blank Page

1. **Check browser console (F12)** for errors
2. **Verify backend is running** on `http://localhost:5000`
3. **Check network tab** for failed API requests
4. **Clear browser cache** and hard refresh (Ctrl+Shift+R)
5. **Check `src/main.jsx`** - ensure `ErrorBoundary` is wrapping the app

### ERR_CONNECTION_REFUSED

**If you see connection refused errors:**

1. **Verify backend is running:**
   ```powershell
   # In backend directory
   python app.py
   ```

2. **Check Vite proxy configuration** in `vite.config.js`

3. **Verify backend CORS settings** allow `http://localhost:5173`

### Build Errors

**If build fails:**

1. **Check for syntax errors:**
   ```powershell
   npm run lint
   ```

2. **Clear Vite cache:**
   ```powershell
   Remove-Item -Recurse -Force node_modules\.vite
   ```

3. **Update dependencies:**
   ```powershell
   npm update
   ```

### Material-UI Icon Errors

If you see errors like `"IconName" is not exported`:

- Check that the icon exists in `@mui/icons-material`
- Use valid Material-UI icon names
- Common icons: `Add`, `Delete`, `Edit`, `Search`, `Menu`, etc.

### Authentication Issues

**Token not persisting:**
- Check browser localStorage (F12 → Application → Local Storage)
- Verify token is being saved after login

**Redirect loops:**
- Clear localStorage:
  ```javascript
  // In browser console
  localStorage.clear()
  ```

### CORS Errors

If you see CORS errors in the browser console:

1. **Verify backend CORS configuration** allows your frontend URL
2. **Check `FRONTEND_URL` in backend `.env`**
3. **Ensure backend is running** and accessible

## 🎨 Styling

### Material-UI Theme

The app uses a custom Material-UI theme defined in `src/App.jsx`.

### Global Styles

- `src/index.css` - Global CSS reset and base styles
- `src/App.css` - App-specific styles

### Component Styles

Components use Material-UI's `sx` prop for styling:
```jsx
<Box sx={{ p: 2, backgroundColor: 'primary.main' }}>
  Content
</Box>
```

## 📱 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 🔐 Authentication Flow

1. User registers/logs in
2. Backend returns JWT token
3. Token stored in `localStorage`
4. Token included in API requests via Axios interceptor
5. Protected routes check authentication status
6. On logout, token is removed from `localStorage`

## 📚 Additional Resources

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Material-UI Documentation](https://mui.com/)
- [React Router Documentation](https://reactrouter.com/)

## 🤝 Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review browser console (F12) for errors
3. Check network tab for API request failures
4. Verify all dependencies are installed correctly

---

**Happy Coding! 🚀**
