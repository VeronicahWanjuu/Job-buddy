# Server Start Guide - Job Buddy App

## ✅ SERVERS ARE NOW RUNNING

### Backend Server:
- **Status:** ✅ Running
- **Port:** 5000
- **URL:** http://localhost:5000
- **Health Check:** http://localhost:5000/health

### Frontend Server:
- **Status:** ✅ Running  
- **Port:** 5173
- **URL:** http://localhost:5173 or http://127.0.0.1:5173

---

## 🌐 HOW TO ACCESS THE APP

### Option 1: Localhost
```
http://localhost:5173
```

### Option 2: 127.0.0.1
```
http://127.0.0.1:5173
```

### Option 3: Network IP (if host: true is set)
```
http://[your-ip]:5173
```

---

## 🔧 IF YOU STILL GET CONNECTION REFUSED

### 1. Check if servers are running:
```powershell
# Check backend
netstat -ano | findstr ":5000"

# Check frontend
netstat -ano | findstr ":5173"
```

### 2. Restart servers manually:

**Backend:**
```powershell
cd backend
python app.py
```

**Frontend (in new terminal):**
```powershell
cd frontend
npm run dev
```

### 3. Check firewall:
- Windows Firewall might be blocking ports
- Allow ports 5000 and 5173 through firewall

### 4. Try different URLs:
- http://127.0.0.1:5173
- http://localhost:5173
- http://[::1]:5173 (IPv6)

---

## 🐛 TROUBLESHOOTING

### Issue: Port already in use
**Solution:**
```powershell
# Find process using port
netstat -ano | findstr ":5173"

# Kill process (replace PID with actual process ID)
taskkill /PID [PID] /F
```

### Issue: Backend not responding
**Solution:**
1. Check if Python is installed: `python --version`
2. Check if dependencies are installed: `pip list`
3. Check backend logs for errors

### Issue: Frontend not compiling
**Solution:**
1. Check if Node.js is installed: `node --version`
2. Check if dependencies are installed: `cd frontend && npm list`
3. Reinstall dependencies: `cd frontend && npm install`

---

## ✅ VERIFICATION

### Test Backend:
```powershell
curl http://localhost:5000/health
```
Should return: `{"status": "healthy"}`

### Test Frontend:
Open browser and navigate to: `http://localhost:5173`

---

## 📝 CURRENT STATUS

- ✅ Backend: Running on port 5000
- ✅ Frontend: Running on port 5173
- ✅ Vite config: Updated to listen on all interfaces
- ✅ CORS: Configured correctly

**Try accessing:** http://localhost:5173 or http://127.0.0.1:5173

